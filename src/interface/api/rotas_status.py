from flask import Blueprint, jsonify, current_app
from ...dominio.enums.status_cobranca import StatusCobranca

bp_status = Blueprint('status', __name__)

@bp_status.route('/status', methods=['GET'])
def obter_status_sistema():
    """
    Obtém o status geral do sistema
    ---
    tags:
      - Status
    responses:
      200:
        description: Status do sistema incluindo contagem de cobranças e rotinas
        schema:
          type: object
          properties:
            contagem_cobrancas:
              type: object
              properties:
                PENDENTE:
                  type: integer
                AUTORIZADA:
                  type: integer
                AGENDADA:
                  type: integer
                PAGA:
                  type: integer
                IGNORADA:
                  type: integer
                ERRO:
                  type: integer
            rotinas:
              type: array
              items:
                type: object
                properties:
                  nome:
                    type: string
                  ultima_execucao:
                    type: string
                    format: date-time
                  intervalo_minutos:
                    type: integer
                  ultimo_status:
                    type: string
                  atrasada:
                    type: boolean
    """
    repositorio_cobranca = current_app.config['repositorio_cobranca']
    repositorio_controle = current_app.config['repositorio_controle']

    contagem_por_status = {}
    for status in StatusCobranca:
        cobrancas = repositorio_cobranca.listar_por_status(status)
        contagem_por_status[status.value] = len(cobrancas)

    rotinas = []
    for nome_rotina in ['processar_emails', 'executar_pagamentos', 'agendar_pagamentos']:
        controle = repositorio_controle.obter_ultima_execucao(nome_rotina)
        if controle:
            rotinas.append({
                'nome': controle.nome_rotina,
                'ultima_execucao': controle.ultima_execucao.isoformat() if controle.ultima_execucao else None,
                'intervalo_minutos': controle.intervalo_minutos,
                'ultimo_status': controle.ultimo_status,
                'atrasada': controle.esta_atrasada()
            })

    return jsonify({
        'contagem_cobrancas': contagem_por_status,
        'rotinas': rotinas
    })

@bp_status.route('/logs', methods=['GET'])
def obter_logs():
    """
    Obtém logs do sistema
    ---
    tags:
      - Status
    responses:
      200:
        description: Lista de logs do sistema
        schema:
          type: object
          properties:
            mensagem:
              type: string
            logs:
              type: array
              items:
                type: object
    """
    return jsonify({
        'mensagem': 'Logs não implementados ainda',
        'logs': []
    })
