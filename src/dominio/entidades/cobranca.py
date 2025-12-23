from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from ..enums.status_cobranca import StatusCobranca, pode_transicionar, eh_status_final

@dataclass
class Cobranca:
    fonte_id: int
    email_id: str
    hash_unico: str
    valor: Decimal
    data_vencimento: date
    tipo_pagamento: str
    status: StatusCobranca
    descricao: str = ""
    codigo_pix: Optional[str] = None
    codigo_barras: Optional[str] = None
    link_boleto: Optional[str] = None
    erro_mensagem: Optional[str] = None
    id: Optional[int] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    def pode_ser_paga(self) -> bool:
        return self.status == StatusCobranca.AGUARDANDO_VENCIMENTO

    def pode_transicionar_para(self, novo_status: StatusCobranca) -> bool:
        return pode_transicionar(self.status, novo_status)

    def esta_em_estado_final(self) -> bool:
        return eh_status_final(self.status)

    def marcar_como_processando(self) -> None:
        if not self.pode_transicionar_para(StatusCobranca.PROCESSANDO):
            raise ValueError(f"Não é possível transicionar de {self.status.value} para PROCESSANDO")
        self.status = StatusCobranca.PROCESSANDO
        self.erro_mensagem = None

    def marcar_como_paga(self, codigo_transacao: str) -> None:
        if not self.pode_transicionar_para(StatusCobranca.PAGA):
            raise ValueError(f"Não é possível transicionar de {self.status.value} para PAGA")
        self.status = StatusCobranca.PAGA
        self.descricao = f"{self.descricao} - Transação: {codigo_transacao}"
        self.erro_mensagem = None

    def marcar_como_falha(self, mensagem_erro: str) -> None:
        if not self.pode_transicionar_para(StatusCobranca.FALHA):
            raise ValueError(f"Não é possível transicionar de {self.status.value} para FALHA")
        self.status = StatusCobranca.FALHA
        self.erro_mensagem = mensagem_erro

    def marcar_como_revisao_manual(self, mensagem_erro: str) -> None:
        if not self.pode_transicionar_para(StatusCobranca.REVISAO_MANUAL):
            raise ValueError(f"Não é possível transicionar de {self.status.value} para REVISAO_MANUAL")
        self.status = StatusCobranca.REVISAO_MANUAL
        self.erro_mensagem = mensagem_erro

    def marcar_como_autorizada(self) -> None:
        if not self.pode_transicionar_para(StatusCobranca.AUTORIZADA):
            raise ValueError(f"Não é possível transicionar de {self.status.value} para AUTORIZADA")
        self.status = StatusCobranca.AUTORIZADA

    def marcar_como_agendada(self) -> None:
        if not self.pode_transicionar_para(StatusCobranca.AGENDADA):
            raise ValueError(f"Não é possível transicionar de {self.status.value} para AGENDADA")
        self.status = StatusCobranca.AGENDADA

    def marcar_como_aguardando_vencimento(self) -> None:
        if not self.pode_transicionar_para(StatusCobranca.AGUARDANDO_VENCIMENTO):
            raise ValueError(f"Não é possível transicionar de {self.status.value} para AGUARDANDO_VENCIMENTO")
        self.status = StatusCobranca.AGUARDANDO_VENCIMENTO

    def marcar_como_ignorada(self) -> None:
        if not self.pode_transicionar_para(StatusCobranca.IGNORADA):
            raise ValueError(f"Não é possível transicionar de {self.status.value} para IGNORADA")
        self.status = StatusCobranca.IGNORADA
