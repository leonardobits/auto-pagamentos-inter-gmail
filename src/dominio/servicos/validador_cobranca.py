from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

def validar_dados_cobranca(
    valor: Decimal,
    data_vencimento: date,
    codigo_pix: Optional[str] = None,
    codigo_barras: Optional[str] = None,
    link_boleto: Optional[str] = None
) -> tuple[bool, str]:

    if valor <= 0:
        return False, "Valor deve ser maior que zero"

    if data_vencimento < date.today() - timedelta(days=90):
        return False, "Data de vencimento muito antiga (mais de 90 dias no passado)"

    tem_metodo_pagamento = any([codigo_pix, codigo_barras, link_boleto])
    if not tem_metodo_pagamento:
        return False, "Necessário pelo menos um método de pagamento (Pix, código de barras ou link)"

    return True, "Dados válidos"

def validar_valor(valor: Decimal) -> bool:
    return valor > 0

def validar_data_vencimento(data_vencimento: date) -> bool:
    limite_passado = date.today() - timedelta(days=90)
    return data_vencimento >= limite_passado
