import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')
GMAIL_CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'src/configuracao/credenciais/gmail_credentials.json')
INTER_CLIENT_ID = os.getenv('INTER_CLIENT_ID', '')
INTER_CLIENT_SECRET = os.getenv('INTER_CLIENT_SECRET', '')
INTER_CERT_PATH = os.getenv('INTER_CERT_PATH', 'src/configuracao/credenciais/inter.crt')
INTER_KEY_PATH = os.getenv('INTER_KEY_PATH', 'src/configuracao/credenciais/inter.key')
INTER_AMBIENTE = os.getenv('INTER_AMBIENTE', 'sandbox')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
INTERVALO_PROCESSAR_EMAILS = int(os.getenv('INTERVALO_PROCESSAR_EMAILS', 60))
INTERVALO_EXECUTAR_PAGAMENTOS = int(os.getenv('INTERVALO_EXECUTAR_PAGAMENTOS', 30))
INTERVALO_AGENDAR_PAGAMENTOS = int(os.getenv('INTERVALO_AGENDAR_PAGAMENTOS', 60))

def validar_configuracoes():
    erros = []

    if not os.path.exists(GMAIL_CREDENTIALS_PATH):
        erros.append(f"Arquivo de credenciais Gmail não encontrado: {GMAIL_CREDENTIALS_PATH}")

    if INTER_AMBIENTE == 'producao':
        if not INTER_CLIENT_ID:
            erros.append("INTER_CLIENT_ID não configurado")
        if not INTER_CLIENT_SECRET:
            erros.append("INTER_CLIENT_SECRET não configurado")
        if not os.path.exists(INTER_CERT_PATH):
            erros.append(f"Certificado Inter não encontrado: {INTER_CERT_PATH}")
        if not os.path.exists(INTER_KEY_PATH):
            erros.append(f"Chave Inter não encontrada: {INTER_KEY_PATH}")

    if erros:
        raise ValueError(f"Erros de configuração:\n" + "\n".join(f"- {erro}" for erro in erros))

    return True
