from typing import Protocol, Optional
from datetime import datetime

class ControleExecucao:
    def __init__(
        self,
        nome_rotina: str,
        ultima_execucao: Optional[datetime],
        intervalo_minutos: int,
        ultimo_status: str,
        ultima_mensagem: str,
        id: Optional[int] = None
    ):
        self.id = id
        self.nome_rotina = nome_rotina
        self.ultima_execucao = ultima_execucao
        self.intervalo_minutos = intervalo_minutos
        self.ultimo_status = ultimo_status
        self.ultima_mensagem = ultima_mensagem

    def esta_atrasada(self) -> bool:
        if not self.ultima_execucao:
            return True

        tempo_decorrido = datetime.now() - self.ultima_execucao
        minutos_decorridos = tempo_decorrido.total_seconds() / 60
        return minutos_decorridos > self.intervalo_minutos

class RepositorioControleExecucao(Protocol):
    def registrar_execucao(self, nome_rotina: str, status: str, mensagem: str) -> None:
        ...

    def obter_ultima_execucao(self, nome_rotina: str) -> Optional[ControleExecucao]:
        ...

    def verificar_rotinas_atrasadas(self) -> list[ControleExecucao]:
        ...

    def inicializar_rotina(self, nome_rotina: str, intervalo_minutos: int) -> None:
        ...
