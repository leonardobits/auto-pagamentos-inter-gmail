from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class FonteAutorizada:
    nome: str
    email_remetente: str
    palavras_assunto: list[str]
    palavras_corpo: list[str]
    ativo: bool
    id: Optional[int] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    def validar_email(self, remetente: str, assunto: str, corpo: str) -> bool:
        if not self.ativo:
            return False

        if not self._validar_remetente(remetente):
            return False

        if not self._validar_palavras(assunto, self.palavras_assunto):
            return False

        if not self._validar_palavras(corpo, self.palavras_corpo):
            return False

        return True

    def _validar_remetente(self, remetente: str) -> bool:
        return self.email_remetente.lower() in remetente.lower()

    def _validar_palavras(self, texto: str, palavras: list[str]) -> bool:
        if not palavras:
            return True

        texto_lower = texto.lower()
        return any(palavra.lower() in texto_lower for palavra in palavras)
