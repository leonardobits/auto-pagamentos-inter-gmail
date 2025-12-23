from typing import Protocol, Optional
from datetime import date
from ...dominio.entidades.agendamento import Agendamento

class RepositorioAgendamento(Protocol):
    def criar_agendamento(self, cobranca_id: int, data_execucao: date) -> Agendamento:
        ...

    def buscar_agendamentos_vencidos(self) -> list[Agendamento]:
        ...

    def buscar_por_cobranca_id(self, cobranca_id: int) -> Optional[Agendamento]:
        ...

    def marcar_como_executado(self, id: int) -> None:
        ...

    def atualizar(self, agendamento: Agendamento) -> Agendamento:
        ...
