from typing import Protocol
from dataclasses import dataclass
from ...dominio.entidades.fonte_autorizada import FonteAutorizada

@dataclass
class Email:
    id: str
    remetente: str
    assunto: str
    corpo: str
    corpo_html: str
    anexos: list[dict]

class ClienteEmail(Protocol):
    def buscar_emails_nao_processados(self, fonte: FonteAutorizada, dias: int = 30) -> list[Email]:
        ...

    def marcar_como_processado(self, email_id: str) -> None:
        ...

    def baixar_anexo(self, email_id: str, attachment_id: str, destino: str) -> str:
        ...
