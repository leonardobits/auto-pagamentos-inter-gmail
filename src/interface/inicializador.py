import os
import sys
from dotenv import load_dotenv

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
from src.aplicacao.casos_uso.recuperar_execucoes import RecuperarExecucoes
from src.interface.api.configuracao_flask import criar_app
from src.interface.scheduler.agendador import Agendador

def carregar_configuracoes():
    load_dotenv()

    config = {
        'DATABASE_PATH': os.getenv('DATABASE_PATH', 'database.db'),
        'GMAIL_CREDENTIALS_PATH': os.getenv('GMAIL_CREDENTIALS_PATH', 'src/configuracao/credenciais/gmail_credentials.json'),
        'INTER_CLIENT_ID': os.getenv('INTER_CLIENT_ID', ''),
        'INTER_CLIENT_SECRET': os.getenv('INTER_CLIENT_SECRET', ''),
        'INTER_CERT_PATH': os.getenv('INTER_CERT_PATH', 'src/configuracao/credenciais/inter.crt'),
        'INTER_KEY_PATH': os.getenv('INTER_KEY_PATH', 'src/configuracao/credenciais/inter.key'),
        'INTER_AMBIENTE': os.getenv('INTER_AMBIENTE', 'sandbox'),
        'FLASK_PORT': int(os.getenv('FLASK_PORT', 5000)),
        'FLASK_DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    }

    return config

def inicializar_banco_dados(database_path: str):
    print(f"[BOOT] Inicializando banco de dados: {database_path}")

    engine = criar_engine(database_path)
    criar_todas_tabelas(engine)
    session_factory = criar_session_factory(engine)

    print("[BOOT] Banco de dados inicializado com sucesso")

    return session_factory

def criar_repositorios(session_factory):
    return {
        'fonte': RepositorioFonteSQL(session_factory),
        'cobranca': RepositorioCobrancaSQL(session_factory),
        'agendamento': RepositorioAgendamentoSQL(session_factory),
        'controle': RepositorioControleExecucaoSQL(session_factory),
        'tentativa': RepositorioTentativaPagamentoSQL(session_factory)
    }

def criar_clientes(config):
    cliente_gmail = ClienteGmail(config['GMAIL_CREDENTIALS_PATH'])

    cliente_inter = ClienteInter(
        client_id=config['INTER_CLIENT_ID'],
        client_secret=config['INTER_CLIENT_SECRET'],
        caminho_certificado=config['INTER_CERT_PATH'],
        caminho_chave=config['INTER_KEY_PATH'],
        ambiente=config['INTER_AMBIENTE']
    )

    return {
        'gmail': cliente_gmail,
        'banco_inter': cliente_inter
    }

def criar_casos_uso(repositorios, clientes):
    caso_uso_processar_emails = ProcessarEmails(
        repositorio_fonte=repositorios['fonte'],
        repositorio_cobranca=repositorios['cobranca'],
        cliente_email=clientes['gmail']
    )

    caso_uso_agendar_pagamento = AgendarPagamento(
        repositorio_cobranca=repositorios['cobranca'],
        repositorio_agendamento=repositorios['agendamento']
    )

    caso_uso_executar_pagamentos = ExecutarPagamentos(
        repositorio_cobranca=repositorios['cobranca'],
        repositorio_agendamento=repositorios['agendamento'],
        repositorio_tentativa=repositorios['tentativa'],
        cliente_bancario=clientes['banco_inter']
    )

    caso_uso_recuperar_execucoes = RecuperarExecucoes(
        repositorio_controle=repositorios['controle']
    )

    return {
        'processar_emails': caso_uso_processar_emails,
        'agendar_pagamento': caso_uso_agendar_pagamento,
        'executar_pagamentos': caso_uso_executar_pagamentos,
        'recuperar_execucoes': caso_uso_recuperar_execucoes
    }

def recuperar_execucoes_perdidas(casos_uso, repositorios):
    print("[BOOT] Verificando execuções perdidas...")

    casos_uso['recuperar_execucoes'].inicializar_rotinas_padrao()

    rotinas_atrasadas = casos_uso['recuperar_execucoes'].executar()

    if rotinas_atrasadas:
        print(f"[BOOT] Rotinas atrasadas encontradas: {rotinas_atrasadas}")

        for rotina in rotinas_atrasadas:
            print(f"[BOOT] Executando rotina atrasada: {rotina}")

            if rotina == 'processar_emails':
                try:
                    casos_uso['processar_emails'].executar()
                except Exception as e:
                    print(f"[BOOT] Erro ao executar {rotina}: {str(e)}")

            elif rotina == 'executar_pagamentos':
                try:
                    casos_uso['executar_pagamentos'].executar()
                except Exception as e:
                    print(f"[BOOT] Erro ao executar {rotina}: {str(e)}")

            elif rotina == 'agendar_pagamentos':
                try:
                    casos_uso['agendar_pagamento'].agendar_cobrancas_autorizadas()
                except Exception as e:
                    print(f"[BOOT] Erro ao executar {rotina}: {str(e)}")
    else:
        print("[BOOT] Nenhuma execução perdida encontrada")

def main():
    print("=" * 60)
    print("Sistema de Automação de Cobranças e Pagamentos")
    print("=" * 60)

    config = carregar_configuracoes()

    session_factory = inicializar_banco_dados(config['DATABASE_PATH'])

    repositorios = criar_repositorios(session_factory)

    clientes = criar_clientes(config)

    casos_uso = criar_casos_uso(repositorios, clientes)

    recuperar_execucoes_perdidas(casos_uso, repositorios)

    print("[BOOT] Inicializando scheduler...")
    agendador = Agendador(
        caso_uso_processar_emails=casos_uso['processar_emails'],
        caso_uso_executar_pagamentos=casos_uso['executar_pagamentos'],
        caso_uso_agendar_pagamento=casos_uso['agendar_pagamento'],
        repositorio_controle=repositorios['controle']
    )
    agendador.iniciar()
    print("[BOOT] Scheduler iniciado com sucesso")

    print("[BOOT] Inicializando API Flask...")
    app = criar_app(
        repositorio_cobranca=repositorios['cobranca'],
        repositorio_fonte=repositorios['fonte'],
        repositorio_tentativa=repositorios['tentativa'],
        repositorio_controle=repositorios['controle'],
        caso_uso_processar_emails=casos_uso['processar_emails'],
        caso_uso_executar_pagamentos=casos_uso['executar_pagamentos'],
        caso_uso_agendar_pagamento=casos_uso['agendar_pagamento']
    )

    print("=" * 60)
    print(f"Sistema iniciado com sucesso!")
    print(f"API disponível em: http://localhost:{config['FLASK_PORT']}")
    print("=" * 60)

    try:
        app.run(
            host='0.0.0.0',
            port=config['FLASK_PORT'],
            debug=config['FLASK_DEBUG']
        )
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Parando sistema...")
        agendador.parar()
        print("[SHUTDOWN] Sistema parado com sucesso")

if __name__ == '__main__':
    main()
