from typing import Optional
from datetime import date, datetime
from .modelos_sql import AgendamentoSQL
from ...dominio.entidades.agendamento import Agendamento

class RepositorioAgendamentoSQL:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def criar_agendamento(self, cobranca_id: int, data_execucao: date) -> Agendamento:
        session = self.session_factory()
        try:
            agendamento_existente = session.query(AgendamentoSQL).filter_by(cobranca_id=cobranca_id).first()
            if agendamento_existente:
                raise ValueError(f"Já existe agendamento para cobrança {cobranca_id}")

            agendamento_sql = AgendamentoSQL(
                cobranca_id=cobranca_id,
                data_execucao=data_execucao,
                executado=False
            )
            session.add(agendamento_sql)
            session.commit()
            session.refresh(agendamento_sql)
            return self._converter_para_entidade(agendamento_sql)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def buscar_agendamentos_vencidos(self) -> list[Agendamento]:
        session = self.session_factory()
        try:
            agendamentos_sql = session.query(AgendamentoSQL).filter(
                AgendamentoSQL.executado == False,
                AgendamentoSQL.data_execucao <= date.today()
            ).all()
            return [self._converter_para_entidade(a) for a in agendamentos_sql]
        finally:
            session.close()

    def buscar_por_cobranca_id(self, cobranca_id: int) -> Optional[Agendamento]:
        session = self.session_factory()
        try:
            agendamento_sql = session.query(AgendamentoSQL).filter_by(cobranca_id=cobranca_id).first()
            return self._converter_para_entidade(agendamento_sql) if agendamento_sql else None
        finally:
            session.close()

    def marcar_como_executado(self, id: int) -> None:
        session = self.session_factory()
        try:
            agendamento_sql = session.query(AgendamentoSQL).filter_by(id=id).first()
            if not agendamento_sql:
                raise ValueError(f"Agendamento {id} não encontrado")

            agendamento_sql.executado = True
            agendamento_sql.data_execucao_real = datetime.now()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def atualizar(self, agendamento: Agendamento) -> Agendamento:
        session = self.session_factory()
        try:
            agendamento_sql = session.query(AgendamentoSQL).filter_by(id=agendamento.id).first()
            if not agendamento_sql:
                raise ValueError(f"Agendamento {agendamento.id} não encontrado")

            agendamento_sql.data_execucao = agendamento.data_execucao
            agendamento_sql.executado = agendamento.executado
            agendamento_sql.data_execucao_real = agendamento.data_execucao_real

            session.commit()
            session.refresh(agendamento_sql)
            return self._converter_para_entidade(agendamento_sql)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _converter_para_entidade(self, agendamento_sql: AgendamentoSQL) -> Agendamento:
        return Agendamento(
            id=agendamento_sql.id,
            cobranca_id=agendamento_sql.cobranca_id,
            data_execucao=agendamento_sql.data_execucao,
            executado=agendamento_sql.executado,
            data_execucao_real=agendamento_sql.data_execucao_real,
            criado_em=agendamento_sql.criado_em
        )
