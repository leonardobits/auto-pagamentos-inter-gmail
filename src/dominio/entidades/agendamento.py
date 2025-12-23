from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class Agendamento:
    cobranca_id: int
    data_execucao: date
    executado: bool = False
    data_execucao_real: Optional[datetime] = None
    id: Optional[int] = None
    criado_em: Optional[datetime] = None

    def esta_vencido(self) -> bool:
        if self.executado:
            return False
        return date.today() >= self.data_execucao

    def marcar_como_executado(self) -> None:
        self.executado = True
        self.data_execucao_real = datetime.now()
