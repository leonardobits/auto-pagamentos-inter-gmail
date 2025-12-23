import os
import tempfile
from typing import Optional
from ...aplicacao.portas.cliente_email import Email

def extrair_anexos_de_email(email: Email) -> list[dict]:
    return email.anexos

def eh_pdf(filename: str) -> bool:
    if not filename:
        return False
    return filename.lower().endswith('.pdf')

def salvar_anexo_temporario(anexo_data: bytes, filename: str) -> str:
    temp_dir = tempfile.gettempdir()
    caminho_temp = os.path.join(temp_dir, filename)

    with open(caminho_temp, 'wb') as f:
        f.write(anexo_data)

    return caminho_temp

def filtrar_anexos_pdf(anexos: list[dict]) -> list[dict]:
    return [anexo for anexo in anexos if eh_pdf(anexo.get('filename', ''))]
