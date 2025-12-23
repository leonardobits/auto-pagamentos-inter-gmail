from typing import Protocol, Optional
from ...dominio.entidades.fonte_autorizada import FonteAutorizada

class RepositorioFonte(Protocol):
    def listar_ativas(self) -> list[FonteAutorizada]:
        ...

    def buscar_por_id(self, id: int) -> Optional[FonteAutorizada]:
        ...

    def salvar(self, fonte: FonteAutorizada) -> FonteAutorizada:
        ...

    def listar_todas(self) -> list[FonteAutorizada]:
        ...

    def atualizar(self, fonte: FonteAutorizada) -> FonteAutorizada:
        ...

    def desativar(self, id: int) -> None:
        ...
