from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

def criar_app(
    repositorio_cobranca,
    repositorio_fonte,
    repositorio_tentativa,
    repositorio_controle,
    caso_uso_processar_emails,
    caso_uso_executar_pagamentos,
    caso_uso_agendar_pagamento
):
    app = Flask(__name__)
    CORS(app)

    # Configuração do Swagger para documentação da API
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api-docs"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API de Automação de Cobranças e Pagamentos",
            "description": "API para gerenciar cobranças, fontes autorizadas, agendamentos e execução de pagamentos automáticos via Banco Inter e Gmail",
            "version": "1.0.0",
            "contact": {
                "name": "Sistema de Automação",
            }
        },
        "basePath": "/",
        "schemes": ["http", "https"],
        "tags": [
            {
                "name": "Cobranças",
                "description": "Endpoints para gerenciar cobranças"
            },
            {
                "name": "Fontes",
                "description": "Endpoints para gerenciar fontes autorizadas de e-mail"
            },
            {
                "name": "Status",
                "description": "Endpoints para consultar status do sistema"
            },
            {
                "name": "Controle",
                "description": "Endpoints para executar rotinas do sistema"
            }
        ]
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    app.config['repositorio_cobranca'] = repositorio_cobranca
    app.config['repositorio_fonte'] = repositorio_fonte
    app.config['repositorio_tentativa'] = repositorio_tentativa
    app.config['repositorio_controle'] = repositorio_controle
    app.config['caso_uso_processar_emails'] = caso_uso_processar_emails
    app.config['caso_uso_executar_pagamentos'] = caso_uso_executar_pagamentos
    app.config['caso_uso_agendar_pagamento'] = caso_uso_agendar_pagamento

    from .rotas_cobranca import bp_cobranca
    from .rotas_fonte import bp_fonte
    from .rotas_status import bp_status
    from .rotas_controle import bp_controle

    app.register_blueprint(bp_cobranca)
    app.register_blueprint(bp_fonte)
    app.register_blueprint(bp_status)
    app.register_blueprint(bp_controle)

    @app.errorhandler(404)
    def nao_encontrado(e):
        return {'erro': 'Rota não encontrada'}, 404

    @app.errorhandler(500)
    def erro_interno(e):
        return {'erro': 'Erro interno do servidor'}, 500

    return app
