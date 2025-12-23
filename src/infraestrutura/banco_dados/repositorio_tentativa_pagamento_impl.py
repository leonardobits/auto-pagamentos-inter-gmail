from datetime import datetime
from .modelos_sql import TentativaPagamentoSQL
from ...aplicacao.portas.repositorio_tentativa_pagamento import TentativaPagamento

class RepositorioTentativaPagamentoSQL:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def registrar_tentativa(
        self,
        cobranca_id: int,
        sucesso: bool,
        mensagem_retorno: str,
        codigo_transacao: str = ""
    ) -> TentativaPagamento:
        session = self.session_factory()
        try:
            tentativa_sql = TentativaPagamentoSQL(
                cobranca_id=cobranca_id,
                tentativa_em=datetime.now(),
                sucesso=sucesso,
                mensagem_retorno=mensagem_retorno,
                codigo_transacao=codigo_transacao
            )
            session.add(tentativa_sql)
            session.commit()
            session.refresh(tentativa_sql)
            return self._converter_para_entidade(tentativa_sql)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def buscar_por_cobranca(self, cobranca_id: int) -> list[TentativaPagamento]:
        session = self.session_factory()
        try:
            tentativas_sql = session.query(TentativaPagamentoSQL).filter_by(
                cobranca_id=cobranca_id
            ).order_by(TentativaPagamentoSQL.tentativa_em.desc()).all()
            return [self._converter_para_entidade(t) for t in tentativas_sql]
        finally:
            session.close()

    def _converter_para_entidade(self, tentativa_sql: TentativaPagamentoSQL) -> TentativaPagamento:
        return TentativaPagamento(
            id=tentativa_sql.id,
            cobranca_id=tentativa_sql.cobranca_id,
            tentativa_em=tentativa_sql.tentativa_em,
            sucesso=tentativa_sql.sucesso,
            mensagem_retorno=tentativa_sql.mensagem_retorno,
            codigo_transacao=tentativa_sql.codigo_transacao or ""
        )
