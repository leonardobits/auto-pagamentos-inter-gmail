import os
import tempfile
from typing import Optional
from decimal import Decimal
from datetime import date
from ..portas.repositorio_fonte import RepositorioFonte
from ..portas.repositorio_cobranca import RepositorioCobranca
from ..portas.cliente_email import ClienteEmail, Email
from ...dominio.entidades.cobranca import Cobranca
from ...dominio.enums.status_cobranca import StatusCobranca
from ...dominio.servicos.gerador_hash import gerar_hash_cobranca
from ...dominio.servicos.validador_cobranca import validar_dados_cobranca
from ...infraestrutura.extratores.extrator_pix import extrair_codigo_pix_do_texto
from ...infraestrutura.extratores.extrator_boleto import extrair_codigo_barras, extrair_link_boleto
from ...infraestrutura.extratores.extrator_dados import extrair_valor, extrair_data_vencimento
from ...infraestrutura.extratores.extrator_pdf import extrair_dados_cobranca_de_pdf
from ...infraestrutura.gmail.extrator_anexos import eh_pdf, salvar_anexo_temporario

class ProcessarEmails:
    def __init__(
        self,
        repositorio_fonte: RepositorioFonte,
        repositorio_cobranca: RepositorioCobranca,
        cliente_email: ClienteEmail
    ):
        self.repositorio_fonte = repositorio_fonte
        self.repositorio_cobranca = repositorio_cobranca
        self.cliente_email = cliente_email

    def executar(self) -> dict:
        fontes_ativas = self.repositorio_fonte.listar_ativas()

        total_emails_processados = 0
        total_cobrancas_criadas = 0
        total_duplicados = 0
        total_invalidos = 0

        for fonte in fontes_ativas:
            emails = self.cliente_email.buscar_emails_nao_processados(fonte)

            for email in emails:
                resultado = self._processar_email(email, fonte)

                if resultado == 'criada':
                    total_cobrancas_criadas += 1
                elif resultado == 'duplicada':
                    total_duplicados += 1
                elif resultado == 'invalida':
                    total_invalidos += 1

                total_emails_processados += 1

        return {
            'emails_processados': total_emails_processados,
            'cobrancas_criadas': total_cobrancas_criadas,
            'duplicados': total_duplicados,
            'invalidos': total_invalidos
        }

    def _processar_email(self, email: Email, fonte) -> str:
        if not fonte.validar_email(email.remetente, email.assunto, email.corpo):
            self.cliente_email.marcar_como_processado(email.id)
            return 'invalida'

        cobranca_existente = self.repositorio_cobranca.buscar_por_email_id(email.id)
        if cobranca_existente:
            return 'duplicada'

        dados_extraidos = self._extrair_dados_de_email(email)

        if not dados_extraidos:
            self.cliente_email.marcar_como_processado(email.id)
            return 'invalida'

        cobranca = self._criar_cobranca_de_dados(email, fonte.id, dados_extraidos)

        if not cobranca:
            self.cliente_email.marcar_como_processado(email.id)
            return 'invalida'

        hash_existente = self.repositorio_cobranca.buscar_por_hash(cobranca.hash_unico)
        if hash_existente:
            self.cliente_email.marcar_como_processado(email.id)
            return 'duplicada'

        self.repositorio_cobranca.salvar(cobranca)
        self.cliente_email.marcar_como_processado(email.id)

        return 'criada'

    def _extrair_dados_de_email(self, email: Email) -> Optional[dict]:
        dados = {
            'valor': extrair_valor(email.corpo),
            'data_vencimento': extrair_data_vencimento(email.corpo),
            'codigo_pix': extrair_codigo_pix_do_texto(email.corpo),
            'codigo_barras': extrair_codigo_barras(email.corpo),
            'link_boleto': extrair_link_boleto(email.corpo_html)
        }

        if email.anexos:
            dados_pdf = self._extrair_dados_de_anexos(email.anexos)
            dados = self._mesclar_dados(dados, dados_pdf)

        return dados if self._tem_dados_minimos(dados) else None

    def _extrair_dados_de_anexos(self, anexos: list[dict]) -> dict:
        dados_combinados = {}

        for anexo in anexos:
            if not eh_pdf(anexo.get('filename', '')):
                continue

            try:
                anexo_data = anexo.get('data')
                if not anexo_data:
                    continue

                caminho_temp = salvar_anexo_temporario(anexo_data, anexo['filename'])
                dados_pdf = extrair_dados_cobranca_de_pdf(caminho_temp)
                dados_combinados = self._mesclar_dados(dados_combinados, dados_pdf)

                os.remove(caminho_temp)
            except Exception:
                continue

        return dados_combinados

    def _mesclar_dados(self, dados1: dict, dados2: dict) -> dict:
        resultado = dados1.copy()

        for chave, valor in dados2.items():
            if not resultado.get(chave) and valor:
                resultado[chave] = valor

        return resultado

    def _tem_dados_minimos(self, dados: dict) -> bool:
        tem_valor = dados.get('valor') is not None
        tem_vencimento = dados.get('data_vencimento') is not None
        tem_metodo_pagamento = any([
            dados.get('codigo_pix'),
            dados.get('codigo_barras'),
            dados.get('link_boleto')
        ])

        return tem_valor and tem_vencimento and tem_metodo_pagamento

    def _criar_cobranca_de_dados(self, email: Email, fonte_id: int, dados: dict) -> Optional[Cobranca]:
        valor = dados.get('valor')
        data_vencimento = dados.get('data_vencimento')
        codigo_pix = dados.get('codigo_pix')
        codigo_barras = dados.get('codigo_barras')
        link_boleto = dados.get('link_boleto')

        valido, mensagem = validar_dados_cobranca(
            valor, data_vencimento, codigo_pix, codigo_barras, link_boleto
        )

        if not valido:
            return None

        codigo_pagamento = codigo_pix or codigo_barras or link_boleto
        hash_unico = gerar_hash_cobranca(email.id, valor, data_vencimento, codigo_pagamento)

        tipo_pagamento = "PIX" if codigo_pix else "BOLETO"
        descricao = f"Cobrança de {email.assunto}"

        cobranca = Cobranca(
            fonte_id=fonte_id,
            email_id=email.id,
            hash_unico=hash_unico,
            valor=valor,
            data_vencimento=data_vencimento,
            tipo_pagamento=tipo_pagamento,
            codigo_pix=codigo_pix,
            codigo_barras=codigo_barras,
            link_boleto=link_boleto,
            descricao=descricao,
            status=StatusCobranca.AUTORIZADA
        )

        return cobranca
