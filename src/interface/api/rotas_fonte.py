from flask import Blueprint, request, jsonify, current_app
from ...dominio.entidades.fonte_autorizada import FonteAutorizada

bp_fonte = Blueprint('fontes', __name__, url_prefix='/fontes')

@bp_fonte.route('', methods=['GET'])
def listar_fontes():
    """
    Lista todas as fontes autorizadas
    ---
    tags:
      - Fontes
    responses:
      200:
        description: Lista de fontes autorizadas
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              nome:
                type: string
              email_remetente:
                type: string
              palavras_assunto:
                type: array
                items:
                  type: string
              palavras_corpo:
                type: array
                items:
                  type: string
              ativo:
                type: boolean
              criado_em:
                type: string
                format: date-time
              atualizado_em:
                type: string
                format: date-time
    """
    repositorio = current_app.config['repositorio_fonte']
    fontes = repositorio.listar_todas()
    return jsonify([_serializar_fonte(f) for f in fontes])

@bp_fonte.route('/<int:id>', methods=['GET'])
def obter_fonte(id):
    """
    Obtém detalhes de uma fonte autorizada
    ---
    tags:
      - Fontes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da fonte
    responses:
      200:
        description: Detalhes da fonte
        schema:
          type: object
          properties:
            id:
              type: integer
            nome:
              type: string
            email_remetente:
              type: string
            palavras_assunto:
              type: array
              items:
                type: string
            palavras_corpo:
              type: array
              items:
                type: string
            ativo:
              type: boolean
      404:
        description: Fonte não encontrada
    """
    repositorio = current_app.config['repositorio_fonte']
    fonte = repositorio.buscar_por_id(id)

    if not fonte:
        return jsonify({'erro': 'Fonte não encontrada'}), 404

    return jsonify(_serializar_fonte(fonte))

@bp_fonte.route('', methods=['POST'])
def criar_fonte():
    """
    Cria uma nova fonte autorizada
    ---
    tags:
      - Fontes
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nome
            - email_remetente
          properties:
            nome:
              type: string
              description: Nome da fonte
              example: "Fornecedor ABC"
            email_remetente:
              type: string
              description: E-mail do remetente autorizado
              example: "cobrancas@fornecedor.com"
            palavras_assunto:
              type: array
              items:
                type: string
              description: Palavras-chave para identificar no assunto
              example: ["fatura", "boleto", "cobrança"]
            palavras_corpo:
              type: array
              items:
                type: string
              description: Palavras-chave para identificar no corpo do e-mail
              example: ["vencimento", "pagamento"]
            ativo:
              type: boolean
              description: Se a fonte está ativa
              default: true
    responses:
      201:
        description: Fonte criada com sucesso
        schema:
          type: object
          properties:
            id:
              type: integer
            nome:
              type: string
            email_remetente:
              type: string
            palavras_assunto:
              type: array
            palavras_corpo:
              type: array
            ativo:
              type: boolean
      400:
        description: Dados inválidos ou campo obrigatório ausente
      500:
        description: Erro interno do servidor
    """
    repositorio = current_app.config['repositorio_fonte']
    dados = request.get_json()

    if not dados:
        return jsonify({'erro': 'Dados inválidos'}), 400

    try:
        fonte = FonteAutorizada(
            nome=dados['nome'],
            email_remetente=dados['email_remetente'],
            palavras_assunto=dados.get('palavras_assunto', []),
            palavras_corpo=dados.get('palavras_corpo', []),
            ativo=dados.get('ativo', True)
        )

        fonte_salva = repositorio.salvar(fonte)
        return jsonify(_serializar_fonte(fonte_salva)), 201

    except KeyError as e:
        return jsonify({'erro': f'Campo obrigatório ausente: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@bp_fonte.route('/<int:id>', methods=['PUT'])
def atualizar_fonte(id):
    """
    Atualiza uma fonte autorizada
    ---
    tags:
      - Fontes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da fonte
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
            email_remetente:
              type: string
            palavras_assunto:
              type: array
              items:
                type: string
            palavras_corpo:
              type: array
              items:
                type: string
            ativo:
              type: boolean
    responses:
      200:
        description: Fonte atualizada com sucesso
      404:
        description: Fonte não encontrada
      500:
        description: Erro interno do servidor
    """
    repositorio = current_app.config['repositorio_fonte']
    dados = request.get_json()

    fonte = repositorio.buscar_por_id(id)
    if not fonte:
        return jsonify({'erro': 'Fonte não encontrada'}), 404

    try:
        fonte.nome = dados.get('nome', fonte.nome)
        fonte.email_remetente = dados.get('email_remetente', fonte.email_remetente)
        fonte.palavras_assunto = dados.get('palavras_assunto', fonte.palavras_assunto)
        fonte.palavras_corpo = dados.get('palavras_corpo', fonte.palavras_corpo)
        fonte.ativo = dados.get('ativo', fonte.ativo)

        fonte_atualizada = repositorio.atualizar(fonte)
        return jsonify(_serializar_fonte(fonte_atualizada))

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@bp_fonte.route('/<int:id>', methods=['DELETE'])
def desativar_fonte(id):
    """
    Desativa uma fonte autorizada
    ---
    tags:
      - Fontes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da fonte a ser desativada
    responses:
      200:
        description: Fonte desativada com sucesso
        schema:
          type: object
          properties:
            mensagem:
              type: string
              example: "Fonte desativada com sucesso"
      404:
        description: Fonte não encontrada
      500:
        description: Erro interno do servidor
    """
    repositorio = current_app.config['repositorio_fonte']

    try:
        repositorio.desativar(id)
        return jsonify({'mensagem': 'Fonte desativada com sucesso'})
    except ValueError as e:
        return jsonify({'erro': str(e)}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

def _serializar_fonte(fonte):
    return {
        'id': fonte.id,
        'nome': fonte.nome,
        'email_remetente': fonte.email_remetente,
        'palavras_assunto': fonte.palavras_assunto,
        'palavras_corpo': fonte.palavras_corpo,
        'ativo': fonte.ativo,
        'criado_em': fonte.criado_em.isoformat() if fonte.criado_em else None,
        'atualizado_em': fonte.atualizado_em.isoformat() if fonte.atualizado_em else None
    }
