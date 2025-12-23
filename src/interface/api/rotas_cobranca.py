from flask import Blueprint, request, jsonify, current_app
from datetime import date

bp_cobranca = Blueprint('cobrancas', __name__, url_prefix='/cobrancas')

@bp_cobranca.route('', methods=['GET'])
def listar_cobrancas():
    """
    Lista todas as cobranças
    ---
    tags:
      - Cobranças
    parameters:
      - name: status
        in: query
        type: string
        enum: [PENDENTE, AUTORIZADA, AGENDADA, PAGA, IGNORADA, ERRO]
        description: Filtrar cobranças por status
      - name: limite
        in: query
        type: integer
        description: Limite de resultados a retornar
    responses:
      200:
        description: Lista de cobranças
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              fonte_id:
                type: integer
              email_id:
                type: string
              hash_unico:
                type: string
              valor:
                type: string
              data_vencimento:
                type: string
                format: date
              tipo_pagamento:
                type: string
              codigo_pix:
                type: string
              codigo_barras:
                type: string
              link_boleto:
                type: string
              descricao:
                type: string
              status:
                type: string
              erro_mensagem:
                type: string
              criado_em:
                type: string
                format: date-time
              atualizado_em:
                type: string
                format: date-time
      400:
        description: Status inválido
    """
    repositorio = current_app.config['repositorio_cobranca']

    status_filtro = request.args.get('status')
    limite = request.args.get('limite', type=int)

    if status_filtro:
        from ...dominio.enums.status_cobranca import StatusCobranca
        try:
            status_enum = StatusCobranca(status_filtro)
            cobrancas = repositorio.listar_por_status(status_enum)
        except ValueError:
            return jsonify({'erro': 'Status inválido'}), 400
    else:
        cobrancas = repositorio.listar_todas(limite)

    return jsonify([_serializar_cobranca(c) for c in cobrancas])

@bp_cobranca.route('/<int:id>', methods=['GET'])
def obter_cobranca(id):
    """
    Obtém detalhes de uma cobrança específica
    ---
    tags:
      - Cobranças
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da cobrança
    responses:
      200:
        description: Detalhes da cobrança com tentativas de pagamento
        schema:
          type: object
          properties:
            id:
              type: integer
            fonte_id:
              type: integer
            email_id:
              type: string
            hash_unico:
              type: string
            valor:
              type: string
            data_vencimento:
              type: string
              format: date
            tipo_pagamento:
              type: string
            codigo_pix:
              type: string
            codigo_barras:
              type: string
            link_boleto:
              type: string
            descricao:
              type: string
            status:
              type: string
            erro_mensagem:
              type: string
            tentativas:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  cobranca_id:
                    type: integer
                  tentativa_em:
                    type: string
                    format: date-time
                  sucesso:
                    type: boolean
                  mensagem_retorno:
                    type: string
                  codigo_transacao:
                    type: string
      404:
        description: Cobrança não encontrada
    """
    repositorio_cobranca = current_app.config['repositorio_cobranca']
    repositorio_tentativa = current_app.config['repositorio_tentativa']

    cobranca = repositorio_cobranca.buscar_por_id(id)
    if not cobranca:
        return jsonify({'erro': 'Cobrança não encontrada'}), 404

    tentativas = repositorio_tentativa.buscar_por_cobranca(id)

    resultado = _serializar_cobranca(cobranca)
    resultado['tentativas'] = [_serializar_tentativa(t) for t in tentativas]

    return jsonify(resultado)

@bp_cobranca.route('/<int:id>/ignorar', methods=['POST'])
def ignorar_cobranca(id):
    """
    Marca uma cobrança como ignorada
    ---
    tags:
      - Cobranças
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da cobrança a ser ignorada
    responses:
      200:
        description: Cobrança marcada como ignorada com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
            status:
              type: string
              example: IGNORADA
      400:
        description: Erro ao processar requisição
      404:
        description: Cobrança não encontrada
    """
    repositorio = current_app.config['repositorio_cobranca']

    cobranca = repositorio.buscar_por_id(id)
    if not cobranca:
        return jsonify({'erro': 'Cobrança não encontrada'}), 404

    try:
        cobranca.marcar_como_ignorada()
        repositorio.atualizar(cobranca)
        return jsonify(_serializar_cobranca(cobranca))
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400

def _serializar_cobranca(cobranca):
    return {
        'id': cobranca.id,
        'fonte_id': cobranca.fonte_id,
        'email_id': cobranca.email_id,
        'hash_unico': cobranca.hash_unico,
        'valor': str(cobranca.valor),
        'data_vencimento': cobranca.data_vencimento.isoformat(),
        'tipo_pagamento': cobranca.tipo_pagamento,
        'codigo_pix': cobranca.codigo_pix,
        'codigo_barras': cobranca.codigo_barras,
        'link_boleto': cobranca.link_boleto,
        'descricao': cobranca.descricao,
        'status': cobranca.status.value,
        'erro_mensagem': cobranca.erro_mensagem,
        'criado_em': cobranca.criado_em.isoformat() if cobranca.criado_em else None,
        'atualizado_em': cobranca.atualizado_em.isoformat() if cobranca.atualizado_em else None
    }

def _serializar_tentativa(tentativa):
    return {
        'id': tentativa.id,
        'cobranca_id': tentativa.cobranca_id,
        'tentativa_em': tentativa.tentativa_em.isoformat(),
        'sucesso': tentativa.sucesso,
        'mensagem_retorno': tentativa.mensagem_retorno,
        'codigo_transacao': tentativa.codigo_transacao
    }
