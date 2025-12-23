from flask import Blueprint, jsonify, current_app

bp_controle = Blueprint('controle', __name__, url_prefix='/executar')

@bp_controle.route('/processar-emails', methods=['POST'])
def executar_processar_emails():
    """
    Executa a rotina de processamento de e-mails
    ---
    tags:
      - Controle
    responses:
      200:
        description: Processamento executado com sucesso
        schema:
          type: object
          properties:
            emails_processados:
              type: integer
            cobrancas_criadas:
              type: integer
            cobrancas_duplicadas:
              type: integer
      500:
        description: Erro ao processar e-mails
    """
    caso_uso = current_app.config['caso_uso_processar_emails']
    repositorio_controle = current_app.config['repositorio_controle']

    try:
        resultado = caso_uso.executar()

        repositorio_controle.registrar_execucao(
            'processar_emails',
            'SUCESSO',
            f"Processados {resultado['emails_processados']} emails, {resultado['cobrancas_criadas']} cobranças criadas"
        )

        return jsonify(resultado)

    except Exception as e:
        repositorio_controle.registrar_execucao(
            'processar_emails',
            'FALHA',
            str(e)
        )
        return jsonify({'erro': str(e)}), 500

@bp_controle.route('/executar-pagamentos', methods=['POST'])
def executar_executar_pagamentos():
    """
    Executa a rotina de pagamentos agendados
    ---
    tags:
      - Controle
    responses:
      200:
        description: Pagamentos executados com sucesso
        schema:
          type: object
          properties:
            total_processadas:
              type: integer
            total_pagas:
              type: integer
            total_erros:
              type: integer
            detalhes:
              type: array
              items:
                type: object
      500:
        description: Erro ao executar pagamentos
    """
    caso_uso = current_app.config['caso_uso_executar_pagamentos']
    repositorio_controle = current_app.config['repositorio_controle']

    try:
        resultado = caso_uso.executar()

        repositorio_controle.registrar_execucao(
            'executar_pagamentos',
            'SUCESSO',
            f"Processadas {resultado['total_processadas']} cobranças, {resultado['total_pagas']} pagas"
        )

        return jsonify(resultado)

    except Exception as e:
        repositorio_controle.registrar_execucao(
            'executar_pagamentos',
            'FALHA',
            str(e)
        )
        return jsonify({'erro': str(e)}), 500

@bp_controle.route('/agendar-pagamentos', methods=['POST'])
def executar_agendar_pagamentos():
    """
    Executa a rotina de agendamento de pagamentos
    ---
    tags:
      - Controle
    responses:
      200:
        description: Agendamento executado com sucesso
        schema:
          type: object
          properties:
            total_agendadas:
              type: integer
            detalhes:
              type: array
              items:
                type: object
      500:
        description: Erro ao agendar pagamentos
    """
    caso_uso = current_app.config['caso_uso_agendar_pagamento']
    repositorio_controle = current_app.config['repositorio_controle']

    try:
        resultado = caso_uso.agendar_cobrancas_autorizadas()

        repositorio_controle.registrar_execucao(
            'agendar_pagamentos',
            'SUCESSO',
            f"Agendadas {resultado['total_agendadas']} cobranças"
        )

        return jsonify(resultado)

    except Exception as e:
        repositorio_controle.registrar_execucao(
            'agendar_pagamentos',
            'FALHA',
            str(e)
        )
        return jsonify({'erro': str(e)}), 500
