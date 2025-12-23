from enum import Enum

class StatusCobranca(Enum):
    NOVA = "NOVA"
    AUTORIZADA = "AUTORIZADA"
    AGENDADA = "AGENDADA"
    AGUARDANDO_VENCIMENTO = "AGUARDANDO_VENCIMENTO"
    PROCESSANDO = "PROCESSANDO"
    PAGA = "PAGA"
    FALHA = "FALHA"
    REVISAO_MANUAL = "REVISAO_MANUAL"
    IGNORADA = "IGNORADA"

TRANSICOES_VALIDAS = {
    StatusCobranca.NOVA: [StatusCobranca.AUTORIZADA, StatusCobranca.IGNORADA],
    StatusCobranca.AUTORIZADA: [StatusCobranca.AGENDADA, StatusCobranca.IGNORADA],
    StatusCobranca.AGENDADA: [StatusCobranca.AGUARDANDO_VENCIMENTO, StatusCobranca.IGNORADA],
    StatusCobranca.AGUARDANDO_VENCIMENTO: [StatusCobranca.PROCESSANDO, StatusCobranca.IGNORADA],
    StatusCobranca.PROCESSANDO: [StatusCobranca.PAGA, StatusCobranca.FALHA, StatusCobranca.REVISAO_MANUAL],
    StatusCobranca.FALHA: [StatusCobranca.PROCESSANDO, StatusCobranca.REVISAO_MANUAL, StatusCobranca.IGNORADA],
    StatusCobranca.PAGA: [],
    StatusCobranca.REVISAO_MANUAL: [StatusCobranca.PROCESSANDO, StatusCobranca.IGNORADA],
    StatusCobranca.IGNORADA: []
}

def pode_transicionar(status_atual: StatusCobranca, status_novo: StatusCobranca) -> bool:
    return status_novo in TRANSICOES_VALIDAS.get(status_atual, [])

def eh_status_final(status: StatusCobranca) -> bool:
    return len(TRANSICOES_VALIDAS.get(status, [])) == 0
