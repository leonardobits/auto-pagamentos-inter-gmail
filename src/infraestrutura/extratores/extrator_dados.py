import re
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import Optional

def extrair_valor(texto: str) -> Optional[Decimal]:
    if not texto:
        return None

    padroes = [
        r'R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        r'R\$\s*(\d+,\d{2})',
        r'(?:valor|total|pagar)[:=\s]+R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
        r'(?:valor|total|pagar)[:=\s]+R?\$?\s*(\d+,\d{2})'
    ]

    for padrao in padroes:
        correspondencias = re.findall(padrao, texto, re.IGNORECASE)
        if correspondencias:
            valor_texto = correspondencias[0]
            try:
                return _converter_valor_brasileiro_para_decimal(valor_texto)
            except (ValueError, InvalidOperation):
                continue

    return None

def _converter_valor_brasileiro_para_decimal(valor_texto: str) -> Decimal:
    valor_limpo = valor_texto.replace('.', '').replace(',', '.')
    return Decimal(valor_limpo)

def extrair_data_vencimento(texto: str) -> Optional[date]:
    if not texto:
        return None

    palavras_chave = ['vencimento', 'vence', 'pagar até', 'válido até', 'validade']

    for palavra in palavras_chave:
        padrao = rf'{palavra}[:\s]+(\d{{2}}[/-]\d{{2}}[/-]\d{{4}})'
        correspondencias = re.findall(padrao, texto, re.IGNORECASE)
        if correspondencias:
            data_texto = correspondencias[0]
            data = _converter_texto_para_data(data_texto)
            if data:
                return data

    padrao_generico = r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b'
    correspondencias = re.findall(padrao_generico, texto)

    for data_texto in correspondencias:
        data = _converter_texto_para_data(data_texto)
        if data and _validar_data_razoavel(data):
            return data

    return None

def _converter_texto_para_data(data_texto: str) -> Optional[date]:
    formatos = ['%d/%m/%Y', '%d-%m-%Y']

    for formato in formatos:
        try:
            return datetime.strptime(data_texto, formato).date()
        except ValueError:
            continue

    return None

def _validar_data_razoavel(data: date) -> bool:
    from datetime import timedelta

    hoje = date.today()
    limite_passado = hoje - timedelta(days=90)
    limite_futuro = hoje + timedelta(days=365)

    return limite_passado <= data <= limite_futuro
