from typing import Protocol
from decimal import Decimal
from dataclasses import dataclass

@dataclass
class ResultadoPagamento:
    sucesso: bool
    codigo_transacao: str
    mensagem: str
    erro_critico: bool = False

class ClienteBancario(Protocol):
    def realizar_pagamento_pix(self, codigo: str, valor: Decimal, descricao: str) -> ResultadoPagamento:
        ...

    def consultar_saldo(self) -> Decimal:
        ...
