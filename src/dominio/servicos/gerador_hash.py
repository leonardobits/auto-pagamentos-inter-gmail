import hashlib
from datetime import date
from decimal import Decimal

def gerar_hash_cobranca(
    email_id: str,
    valor: Decimal,
    data_vencimento: date,
    codigo_pagamento: str
) -> str:
    conteudo = f"{email_id}|{valor}|{data_vencimento.isoformat()}|{codigo_pagamento}"
    return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()
