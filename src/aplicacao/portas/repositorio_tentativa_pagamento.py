from typing import Protocol
from datetime import datetime

class TentativaPagamento:
    def __init__(
        self,
        cobranca_id: int,
        sucesso: bool,
        mensagem_retorno: str,
        codigo_transacao: str = "",
        tentativa_em: datetime = None,
        id: int = None
    ):
        self.id = id
        self.cobranca_id = cobranca_id
        self.tentativa_em = tentativa_em or datetime.now()
        self.sucesso = sucesso
        self.mensagem_retorno = mensagem_retorno
        self.codigo_transacao = codigo_transacao

class RepositorioTentativaPagamento(Protocol):
    def registrar_tentativa(
        self,
        cobranca_id: int,
        sucesso: bool,
        mensagem_retorno: str,
        codigo_transacao: str = ""
    ) -> TentativaPagamento:
        ...

    def buscar_por_cobranca(self, cobranca_id: int) -> list[TentativaPagamento]:
        ...
