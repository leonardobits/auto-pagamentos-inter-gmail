import requests
from decimal import Decimal
from .autenticador_inter import AutenticadorInter
from ...aplicacao.portas.cliente_bancario import ResultadoPagamento

class ClienteInter:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        caminho_certificado: str,
        caminho_chave: str,
        ambiente: str = "producao"
    ):
        self.autenticador = AutenticadorInter(
            client_id,
            client_secret,
            caminho_certificado,
            caminho_chave
        )
        self.caminho_certificado = caminho_certificado
        self.caminho_chave = caminho_chave

        if ambiente == "sandbox":
            self.url_base = "https://cdpj-sandbox.partners.bancointer.com.br"
        else:
            self.url_base = "https://cdpj.partners.bancointer.com.br"

    def realizar_pagamento_pix(self, codigo: str, valor: Decimal, descricao: str) -> ResultadoPagamento:
        try:
            token = self.autenticador.obter_token()

            url = f"{self.url_base}/banking/v2/pix"

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'valor': str(valor),
                'pixCopiaECola': codigo,
                'descricao': descricao[:140]
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                cert=(self.caminho_certificado, self.caminho_chave)
            )

            if response.status_code in [200, 201]:
                dados = response.json()
                codigo_transacao = dados.get('endToEndId', dados.get('txid', 'sem_codigo'))

                return ResultadoPagamento(
                    sucesso=True,
                    codigo_transacao=codigo_transacao,
                    mensagem="Pagamento realizado com sucesso"
                )

            elif response.status_code in [400, 422]:
                mensagem_erro = self._extrair_mensagem_erro(response)

                erro_critico = self._eh_erro_critico(mensagem_erro)

                return ResultadoPagamento(
                    sucesso=False,
                    codigo_transacao="",
                    mensagem=mensagem_erro,
                    erro_critico=erro_critico
                )

            else:
                return ResultadoPagamento(
                    sucesso=False,
                    codigo_transacao="",
                    mensagem=f"Erro HTTP {response.status_code}: {response.text}",
                    erro_critico=False
                )

        except Exception as e:
            return ResultadoPagamento(
                sucesso=False,
                codigo_transacao="",
                mensagem=f"Erro ao realizar pagamento: {str(e)}",
                erro_critico=False
            )

    def _extrair_mensagem_erro(self, response) -> str:
        try:
            dados = response.json()
            if 'message' in dados:
                return dados['message']
            elif 'error' in dados:
                return dados['error']
            elif 'title' in dados:
                return dados['title']
            else:
                return response.text
        except Exception:
            return response.text

    def _eh_erro_critico(self, mensagem: str) -> bool:
        erros_criticos = [
            'saldo insuficiente',
            'conta bloqueada',
            'conta inativa',
            'limite excedido',
            'código pix inválido',
            'pix expirado'
        ]

        mensagem_lower = mensagem.lower()
        return any(erro in mensagem_lower for erro in erros_criticos)

    def consultar_saldo(self) -> Decimal:
        try:
            token = self.autenticador.obter_token()

            url = f"{self.url_base}/banking/v2/extrato"

            headers = {
                'Authorization': f'Bearer {token}'
            }

            response = requests.get(
                url,
                headers=headers,
                cert=(self.caminho_certificado, self.caminho_chave)
            )

            if response.status_code == 200:
                dados = response.json()
                saldo = dados.get('saldo', 0)
                return Decimal(str(saldo))
            else:
                raise Exception(f"Erro ao consultar saldo: {response.status_code}")

        except Exception as e:
            raise Exception(f"Erro ao consultar saldo: {str(e)}")
