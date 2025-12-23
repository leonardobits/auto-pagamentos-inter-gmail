from ..portas.repositorio_controle_execucao import RepositorioControleExecucao

class RecuperarExecucoes:
    def __init__(self, repositorio_controle: RepositorioControleExecucao):
        self.repositorio_controle = repositorio_controle

    def executar(self) -> list[str]:
        rotinas_atrasadas = self.repositorio_controle.verificar_rotinas_atrasadas()
        nomes_rotinas_atrasadas = [rotina.nome_rotina for rotina in rotinas_atrasadas]
        return nomes_rotinas_atrasadas

    def inicializar_rotinas_padrao(self) -> None:
        self.repositorio_controle.inicializar_rotina("processar_emails", 60)
        self.repositorio_controle.inicializar_rotina("executar_pagamentos", 30)
        self.repositorio_controle.inicializar_rotina("agendar_pagamentos", 60)
