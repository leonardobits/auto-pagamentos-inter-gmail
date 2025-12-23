from apscheduler.schedulers.background import BackgroundScheduler

class Agendador:
    def __init__(
        self,
        caso_uso_processar_emails,
        caso_uso_executar_pagamentos,
        caso_uso_agendar_pagamento,
        repositorio_controle
    ):
        self.caso_uso_processar_emails = caso_uso_processar_emails
        self.caso_uso_executar_pagamentos = caso_uso_executar_pagamentos
        self.caso_uso_agendar_pagamento = caso_uso_agendar_pagamento
        self.repositorio_controle = repositorio_controle
        self.scheduler = BackgroundScheduler()

    def iniciar(self):
        self._registrar_rotina_processar_emails()
        self._registrar_rotina_executar_pagamentos()
        self._registrar_rotina_agendar_pagamentos()

        self.scheduler.start()

    def _registrar_rotina_processar_emails(self):
        self.scheduler.add_job(
            func=self._executar_processar_emails,
            trigger='interval',
            minutes=60,
            id='processar_emails',
            name='Processar Emails',
            replace_existing=True
        )

    def _registrar_rotina_executar_pagamentos(self):
        self.scheduler.add_job(
            func=self._executar_pagamentos,
            trigger='interval',
            minutes=30,
            id='executar_pagamentos',
            name='Executar Pagamentos',
            replace_existing=True
        )

    def _registrar_rotina_agendar_pagamentos(self):
        self.scheduler.add_job(
            func=self._executar_agendar_pagamentos,
            trigger='interval',
            minutes=60,
            id='agendar_pagamentos',
            name='Agendar Pagamentos',
            replace_existing=True
        )

    def _executar_processar_emails(self):
        try:
            print("[SCHEDULER] Iniciando processamento de emails...")
            resultado = self.caso_uso_processar_emails.executar()
            self.repositorio_controle.registrar_execucao(
                'processar_emails',
                'SUCESSO',
                f"Processados {resultado['emails_processados']} emails"
            )
            print(f"[SCHEDULER] Emails processados: {resultado}")
        except Exception as e:
            print(f"[SCHEDULER] Erro ao processar emails: {str(e)}")
            self.repositorio_controle.registrar_execucao(
                'processar_emails',
                'FALHA',
                str(e)
            )

    def _executar_pagamentos(self):
        try:
            print("[SCHEDULER] Iniciando execução de pagamentos...")
            resultado = self.caso_uso_executar_pagamentos.executar()
            self.repositorio_controle.registrar_execucao(
                'executar_pagamentos',
                'SUCESSO',
                f"Processadas {resultado['total_processadas']} cobranças"
            )
            print(f"[SCHEDULER] Pagamentos executados: {resultado}")
        except Exception as e:
            print(f"[SCHEDULER] Erro ao executar pagamentos: {str(e)}")
            self.repositorio_controle.registrar_execucao(
                'executar_pagamentos',
                'FALHA',
                str(e)
            )

    def _executar_agendar_pagamentos(self):
        try:
            print("[SCHEDULER] Iniciando agendamento de pagamentos...")
            resultado = self.caso_uso_agendar_pagamento.agendar_cobrancas_autorizadas()
            self.repositorio_controle.registrar_execucao(
                'agendar_pagamentos',
                'SUCESSO',
                f"Agendadas {resultado['total_agendadas']} cobranças"
            )
            print(f"[SCHEDULER] Pagamentos agendados: {resultado}")
        except Exception as e:
            print(f"[SCHEDULER] Erro ao agendar pagamentos: {str(e)}")
            self.repositorio_controle.registrar_execucao(
                'agendar_pagamentos',
                'FALHA',
                str(e)
            )

    def parar(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
