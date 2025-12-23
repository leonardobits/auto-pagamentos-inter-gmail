from ..portas.repositorio_cobranca import RepositorioCobranca
from ..portas.repositorio_agendamento import RepositorioAgendamento
from ..portas.repositorio_tentativa_pagamento import RepositorioTentativaPagamento
from ..portas.cliente_bancario import ClienteBancario
from ...dominio.enums.status_cobranca import StatusCobranca

class ExecutarPagamentos:
    def __init__(
        self,
        repositorio_cobranca: RepositorioCobranca,
        repositorio_agendamento: RepositorioAgendamento,
        repositorio_tentativa: RepositorioTentativaPagamento,
        cliente_bancario: ClienteBancario
    ):
        self.repositorio_cobranca = repositorio_cobranca
        self.repositorio_agendamento = repositorio_agendamento
        self.repositorio_tentativa = repositorio_tentativa
        self.cliente_bancario = cliente_bancario

    def executar(self) -> dict:
        cobrancas_elegiveis = self.repositorio_cobranca.buscar_elegiveis_para_pagamento()

        total_processadas = 0
        total_pagas = 0
        total_falhas = 0
        total_revisao = 0

        for cobranca in cobrancas_elegiveis:
            resultado = self._processar_pagamento(cobranca)

            if resultado == 'paga':
                total_pagas += 1
            elif resultado == 'falha':
                total_falhas += 1
            elif resultado == 'revisao':
                total_revisao += 1

            total_processadas += 1

        return {
            'total_processadas': total_processadas,
            'total_pagas': total_pagas,
            'total_falhas': total_falhas,
            'total_revisao': total_revisao
        }

    def _processar_pagamento(self, cobranca) -> str:
        try:
            cobranca.marcar_como_processando()
            self.repositorio_cobranca.atualizar(cobranca)

            if cobranca.tipo_pagamento == "PIX":
                resultado = self.cliente_bancario.realizar_pagamento_pix(
                    cobranca.codigo_pix,
                    cobranca.valor,
                    cobranca.descricao
                )
            else:
                resultado = None
                cobranca.marcar_como_revisao_manual("Tipo de pagamento não suportado ainda")
                self.repositorio_cobranca.atualizar(cobranca)
                return 'revisao'

            if resultado.sucesso:
                cobranca.marcar_como_paga(resultado.codigo_transacao)
                self.repositorio_cobranca.atualizar(cobranca)

                agendamento = self.repositorio_agendamento.buscar_por_cobranca_id(cobranca.id)
                if agendamento:
                    self.repositorio_agendamento.marcar_como_executado(agendamento.id)

                self.repositorio_tentativa.registrar_tentativa(
                    cobranca.id,
                    True,
                    resultado.mensagem,
                    resultado.codigo_transacao
                )

                return 'paga'
            else:
                if resultado.erro_critico:
                    cobranca.marcar_como_revisao_manual(resultado.mensagem)
                    self.repositorio_cobranca.atualizar(cobranca)
                    self.repositorio_tentativa.registrar_tentativa(
                        cobranca.id,
                        False,
                        resultado.mensagem
                    )
                    return 'revisao'
                else:
                    cobranca.marcar_como_falha(resultado.mensagem)
                    self.repositorio_cobranca.atualizar(cobranca)
                    self.repositorio_tentativa.registrar_tentativa(
                        cobranca.id,
                        False,
                        resultado.mensagem
                    )
                    return 'falha'

        except Exception as e:
            try:
                cobranca.marcar_como_falha(str(e))
                self.repositorio_cobranca.atualizar(cobranca)
                self.repositorio_tentativa.registrar_tentativa(
                    cobranca.id,
                    False,
                    str(e)
                )
            except Exception:
                pass

            return 'falha'
