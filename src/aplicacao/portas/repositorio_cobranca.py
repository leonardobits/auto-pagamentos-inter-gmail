from typing import Protocol, Optional
from ...dominio.entidades.cobranca import Cobranca
from ...dominio.enums.status_cobranca import StatusCobranca

class RepositorioCobranca(Protocol):
    def salvar(self, cobranca: Cobranca) -> Cobranca:
        ...

    def buscar_por_id(self, id: int) -> Optional[Cobranca]:
        ...

    def buscar_por_hash(self, hash_unico: str) -> Optional[Cobranca]:
        ...

    def buscar_por_email_id(self, email_id: str) -> Optional[Cobranca]:
        ...

    def buscar_elegiveis_para_pagamento(self) -> list[Cobranca]:
        ...

    def atualizar_status(self, id: int, novo_status: StatusCobranca, erro_mensagem: Optional[str] = None) -> None:
        ...

    def listar_por_status(self, status: StatusCobranca) -> list[Cobranca]:
        ...

    def listar_todas(self, limite: Optional[int] = None) -> list[Cobranca]:
        ...

    def atualizar(self, cobranca: Cobranca) -> Cobranca:
        ...
