from typing import Optional
from decimal import Decimal
from datetime import date

def extrair_texto_de_pdf(caminho_arquivo: str) -> str:
    try:
        import pdfplumber

        texto_completo = ""
        with pdfplumber.open(caminho_arquivo) as pdf:
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"

        return texto_completo
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

def extrair_dados_cobranca_de_pdf(caminho_arquivo: str) -> dict:
    from .extrator_pix import extrair_codigo_pix_do_texto
    from .extrator_boleto import extrair_codigo_barras
    from .extrator_dados import extrair_valor, extrair_data_vencimento

    texto = extrair_texto_de_pdf(caminho_arquivo)

    dados = {
        'valor': extrair_valor(texto),
        'data_vencimento': extrair_data_vencimento(texto),
        'codigo_pix': extrair_codigo_pix_do_texto(texto),
        'codigo_barras': extrair_codigo_barras(texto)
    }

    return dados
