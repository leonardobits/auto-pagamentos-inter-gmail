from typing import Optional
from datetime import datetime
from .modelos_sql import ControleExecucaoSQL
from ...aplicacao.portas.repositorio_controle_execucao import ControleExecucao

class RepositorioControleExecucaoSQL:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def registrar_execucao(self, nome_rotina: str, status: str, mensagem: str) -> None:
        session = self.session_factory()
        try:
            controle = session.query(ControleExecucaoSQL).filter_by(nome_rotina=nome_rotina).first()

            if controle:
                controle.ultima_execucao = datetime.now()
                controle.ultimo_status = status
                controle.ultima_mensagem = mensagem
            else:
                controle = ControleExecucaoSQL(
                    nome_rotina=nome_rotina,
                    ultima_execucao=datetime.now(),
                    intervalo_minutos=60,
                    ultimo_status=status,
                    ultima_mensagem=mensagem
                )
                session.add(controle)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def obter_ultima_execucao(self, nome_rotina: str) -> Optional[ControleExecucao]:
        session = self.session_factory()
        try:
            controle_sql = session.query(ControleExecucaoSQL).filter_by(nome_rotina=nome_rotina).first()
            return self._converter_para_entidade(controle_sql) if controle_sql else None
        finally:
            session.close()

    def verificar_rotinas_atrasadas(self) -> list[ControleExecucao]:
        session = self.session_factory()
        try:
            controles_sql = session.query(ControleExecucaoSQL).all()
            controles = [self._converter_para_entidade(c) for c in controles_sql]
            return [c for c in controles if c.esta_atrasada()]
        finally:
            session.close()

    def inicializar_rotina(self, nome_rotina: str, intervalo_minutos: int) -> None:
        session = self.session_factory()
        try:
            controle_existente = session.query(ControleExecucaoSQL).filter_by(nome_rotina=nome_rotina).first()

            if not controle_existente:
                controle = ControleExecucaoSQL(
                    nome_rotina=nome_rotina,
                    ultima_execucao=None,
                    intervalo_minutos=intervalo_minutos,
                    ultimo_status="NUNCA_EXECUTADO",
                    ultima_mensagem="Rotina inicializada"
                )
                session.add(controle)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _converter_para_entidade(self, controle_sql: ControleExecucaoSQL) -> ControleExecucao:
        return ControleExecucao(
            id=controle_sql.id,
            nome_rotina=controle_sql.nome_rotina,
            ultima_execucao=controle_sql.ultima_execucao,
            intervalo_minutos=controle_sql.intervalo_minutos,
            ultimo_status=controle_sql.ultimo_status,
            ultima_mensagem=controle_sql.ultima_mensagem or ""
        )
