import re
from typing import Optional

def extrair_codigo_pix_do_texto(texto: str) -> Optional[str]:
    if not texto:
        return None

    padrao_pix = r'[0-9a-zA-Z]{32,}'

    correspondencias = re.findall(padrao_pix, texto)

    for codigo in correspondencias:
        if _validar_formato_pix(codigo):
            return codigo

    return None

def _validar_formato_pix(codigo: str) -> bool:
    if len(codigo) < 32:
        return False

    if not any(char.isdigit() for char in codigo):
        return False

    if not any(char.isalpha() for char in codigo):
        return False

    return True

def extrair_codigo_pix_de_pdf(caminho_pdf: str) -> Optional[str]:
    from .extrator_pdf import extrair_texto_de_pdf

    texto = extrair_texto_de_pdf(caminho_pdf)
    return extrair_codigo_pix_do_texto(texto)
