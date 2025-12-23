from datetime import date

def calcular_data_execucao(data_vencimento: date) -> date:
    return data_vencimento

def esta_no_prazo_de_pagamento(data_vencimento: date) -> bool:
    return date.today() <= data_vencimento

def ja_venceu(data_vencimento: date) -> bool:
    return date.today() > data_vencimento
