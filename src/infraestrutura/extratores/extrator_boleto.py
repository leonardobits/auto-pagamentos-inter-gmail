import re
from typing import Optional

def extrair_codigo_barras(texto: str) -> Optional[str]:
    if not texto:
        return None

    texto_limpo = re.sub(r'[^\d]', '', texto)

    padrao_47_digitos = r'(\d{47,48})'
    correspondencias = re.findall(padrao_47_digitos, texto_limpo)

    if correspondencias:
        return correspondencias[0]

    padrao_com_separadores = r'(\d{5}[.\s]?\d{5}\s?\d{5}[.\s]?\d{6}\s?\d{5}[.\s]?\d{6}\s?\d\s?\d{14})'
    correspondencias = re.findall(padrao_com_separadores, texto)

    if correspondencias:
        codigo = re.sub(r'[^\d]', '', correspondencias[0])
        if len(codigo) >= 47:
            return codigo

    return None

def extrair_link_boleto(texto_html: str) -> Optional[str]:
    if not texto_html:
        return None

    padrao_links = r'https?://[^\s<>"]+(?:boleto|fatura|pagamento)[^\s<>"]*'
    correspondencias = re.findall(padrao_links, texto_html, re.IGNORECASE)

    if correspondencias:
        return correspondencias[0]

    padrao_links_generico = r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>'
    correspondencias = re.findall(padrao_links_generico, texto_html, re.IGNORECASE)

    for link, texto_link in correspondencias:
        if any(palavra in texto_link.lower() for palavra in ['boleto', 'fatura', 'pagar', 'pagamento']):
            return link

    return None

def validar_codigo_barras(codigo: str) -> bool:
    if not codigo:
        return False

    codigo_limpo = re.sub(r'[^\d]', '', codigo)

    return len(codigo_limpo) in [47, 48]
