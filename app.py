"""
Arquivo de entrada para o Flask CLI.
Este arquivo expõe a aplicação Flask para que o comando 'flask run' funcione.
"""
import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.infraestrutura.banco_dados.modelos_sql import criar_engine, criar_session_factory, criar_todas_tabelas
from src.infraestrutura.banco_dados.repositorio_fonte_impl import RepositorioFonteSQL
from src.infraestrutura.banco_dados.repositorio_cobranca_impl import RepositorioCobrancaSQL
from src.infraestrutura.banco_dados.repositorio_agendamento_impl import RepositorioAgendamentoSQL
from src.infraestrutura.banco_dados.repositorio_controle_execucao_impl import RepositorioControleExecucaoSQL
from src.infraestrutura.banco_dados.repositorio_tentativa_pagamento_impl import RepositorioTentativaPagamentoSQL
from src.infraestrutura.gmail.cliente_gmail import ClienteGmail
from src.infraestrutura.banco_inter.cliente_inter import ClienteInter
from src.aplicacao.casos_uso.processar_emails import ProcessarEmails
from src.aplicacao.casos_uso.agendar_pagamento import AgendarPagamento
from src.aplicacao.casos_uso.executar_pagamentos import ExecutarPagamentos
from src.interface.api.configuracao_flask import criar_app

# Carrega variáveis de ambiente
load_dotenv()

def criar_aplicacao():
    """Cria e retorna a aplicação Flask configurada."""
    config = {
        'DATABASE_PATH': os.getenv('DATABASE_PATH', 'database.db'),
        'GMAIL_CREDENTIALS_PATH': os.getenv('GMAIL_CREDENTIALS_PATH', 'src/configuracao/credenciais/gmail_credentials.json'),
        'INTER_CLIENT_ID': os.getenv('INTER_CLIENT_ID', ''),
        'INTER_CLIENT_SECRET': os.getenv('INTER_CLIENT_SECRET', ''),
        'INTER_CERT_PATH': os.getenv('INTER_CERT_PATH', 'src/configuracao/credenciais/inter.crt'),
        'INTER_KEY_PATH': os.getenv('INTER_KEY_PATH', 'src/configuracao/credenciais/inter.key'),
        'INTER_AMBIENTE': os.getenv('INTER_AMBIENTE', 'sandbox'),
    }

    # Inicializa banco de dados
    engine = criar_engine(config['DATABASE_PATH'])
    criar_todas_tabelas(engine)
    session_factory = criar_session_factory(engine)

    # Cria repositórios
    repositorios = {
        'fonte': RepositorioFonteSQL(session_factory),
        'cobranca': RepositorioCobrancaSQL(session_factory),
        'agendamento': RepositorioAgendamentoSQL(session_factory),
        'controle': RepositorioControleExecucaoSQL(session_factory),
        'tentativa': RepositorioTentativaPagamentoSQL(session_factory)
    }

    # Cria clientes
    cliente_gmail = ClienteGmail(config['GMAIL_CREDENTIALS_PATH'])
    cliente_inter = ClienteInter(
        client_id=config['INTER_CLIENT_ID'],
        client_secret=config['INTER_CLIENT_SECRET'],
        caminho_certificado=config['INTER_CERT_PATH'],
        caminho_chave=config['INTER_KEY_PATH'],
        ambiente=config['INTER_AMBIENTE']
    )

    # Cria casos de uso
    caso_uso_processar_emails = ProcessarEmails(
        repositorio_fonte=repositorios['fonte'],
        repositorio_cobranca=repositorios['cobranca'],
        cliente_email=cliente_gmail
    )

    caso_uso_agendar_pagamento = AgendarPagamento(
        repositorio_cobranca=repositorios['cobranca'],
        repositorio_agendamento=repositorios['agendamento']
    )

    caso_uso_executar_pagamentos = ExecutarPagamentos(
        repositorio_cobranca=repositorios['cobranca'],
        repositorio_agendamento=repositorios['agendamento'],
        repositorio_tentativa=repositorios['tentativa'],
        cliente_bancario=cliente_inter
    )

    # Cria e retorna a aplicação Flask
    app = criar_app(
        repositorio_cobranca=repositorios['cobranca'],
        repositorio_fonte=repositorios['fonte'],
        repositorio_tentativa=repositorios['tentativa'],
        repositorio_controle=repositorios['controle'],
        caso_uso_processar_emails=caso_uso_processar_emails,
        caso_uso_executar_pagamentos=caso_uso_executar_pagamentos,
        caso_uso_agendar_pagamento=caso_uso_agendar_pagamento
    )

    return app

# Cria a aplicação Flask - o Flask CLI procura por uma variável chamada 'app'
app = criar_aplicacao()

