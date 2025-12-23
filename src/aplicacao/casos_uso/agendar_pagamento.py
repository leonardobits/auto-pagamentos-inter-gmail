from ..portas.repositorio_cobranca import RepositorioCobranca
from ..portas.repositorio_agendamento import RepositorioAgendamento
from ...dominio.entidades.agendamento import Agendamento
from ...dominio.servicos.calculador_vencimento import calcular_data_execucao

class AgendarPagamento:
    def __init__(
        self,
        repositorio_cobranca: RepositorioCobranca,
        repositorio_agendamento: RepositorioAgendamento
    ):
        self.repositorio_cobranca = repositorio_cobranca
        self.repositorio_agendamento = repositorio_agendamento

    def executar(self, cobranca_id: int) -> Agendamento:
        cobranca = self.repositorio_cobranca.buscar_por_id(cobranca_id)
        if not cobranca:
            raise ValueError(f"Cobrança {cobranca_id} não encontrada")

        agendamento_existente = self.repositorio_agendamento.buscar_por_cobranca_id(cobranca_id)
        if agendamento_existente:
            raise ValueError(f"Já existe agendamento para cobrança {cobranca_id}")

        data_execucao = calcular_data_execucao(cobranca.data_vencimento)

        agendamento = self.repositorio_agendamento.criar_agendamento(cobranca_id, data_execucao)

        cobranca.marcar_como_agendada()
        self.repositorio_cobranca.atualizar(cobranca)

        cobranca.marcar_como_aguardando_vencimento()
        self.repositorio_cobranca.atualizar(cobranca)

        return agendamento

    def agendar_cobrancas_autorizadas(self) -> dict:
        from ...dominio.enums.status_cobranca import StatusCobranca

        cobrancas_autorizadas = self.repositorio_cobranca.listar_por_status(StatusCobranca.AUTORIZADA)

        total_agendadas = 0
        total_erros = 0

        for cobranca in cobrancas_autorizadas:
            try:
                self.executar(cobranca.id)
                total_agendadas += 1
            except Exception:
                total_erros += 1

        return {
            'total_agendadas': total_agendadas,
            'total_erros': total_erros
        }
