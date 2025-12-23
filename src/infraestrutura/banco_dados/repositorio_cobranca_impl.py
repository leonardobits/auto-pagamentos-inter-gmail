from typing import Optional
from datetime import date
from decimal import Decimal
from .modelos_sql import CobrancaSQL
from ...dominio.entidades.cobranca import Cobranca
from ...dominio.enums.status_cobranca import StatusCobranca

class RepositorioCobrancaSQL:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def salvar(self, cobranca: Cobranca) -> Cobranca:
        session = self.session_factory()
        try:
            cobranca_sql = CobrancaSQL(
                fonte_id=cobranca.fonte_id,
                email_id=cobranca.email_id,
                hash_unico=cobranca.hash_unico,
                valor=cobranca.valor,
                data_vencimento=cobranca.data_vencimento,
                tipo_pagamento=cobranca.tipo_pagamento,
                codigo_pix=cobranca.codigo_pix,
                codigo_barras=cobranca.codigo_barras,
                link_boleto=cobranca.link_boleto,
                descricao=cobranca.descricao,
                status=cobranca.status.value,
                erro_mensagem=cobranca.erro_mensagem
            )
            session.add(cobranca_sql)
            session.commit()
            session.refresh(cobranca_sql)
            return self._converter_para_entidade(cobranca_sql)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def buscar_por_id(self, id: int) -> Optional[Cobranca]:
        session = self.session_factory()
        try:
            cobranca_sql = session.query(CobrancaSQL).filter_by(id=id).first()
            return self._converter_para_entidade(cobranca_sql) if cobranca_sql else None
        finally:
            session.close()

    def buscar_por_hash(self, hash_unico: str) -> Optional[Cobranca]:
        session = self.session_factory()
        try:
            cobranca_sql = session.query(CobrancaSQL).filter_by(hash_unico=hash_unico).first()
            return self._converter_para_entidade(cobranca_sql) if cobranca_sql else None
        finally:
            session.close()

    def buscar_por_email_id(self, email_id: str) -> Optional[Cobranca]:
        session = self.session_factory()
        try:
            cobranca_sql = session.query(CobrancaSQL).filter_by(email_id=email_id).first()
            return self._converter_para_entidade(cobranca_sql) if cobranca_sql else None
        finally:
            session.close()

    def buscar_elegiveis_para_pagamento(self) -> list[Cobranca]:
        session = self.session_factory()
        try:
            from .modelos_sql import AgendamentoSQL

            cobrancas_sql = session.query(CobrancaSQL).join(AgendamentoSQL).filter(
                CobrancaSQL.status == StatusCobranca.AGUARDANDO_VENCIMENTO.value,
                AgendamentoSQL.executado == False,
                AgendamentoSQL.data_execucao <= date.today()
            ).all()

            return [self._converter_para_entidade(c) for c in cobrancas_sql]
        finally:
            session.close()

    def atualizar_status(self, id: int, novo_status: StatusCobranca, erro_mensagem: Optional[str] = None) -> None:
        session = self.session_factory()
        try:
            cobranca_sql = session.query(CobrancaSQL).filter_by(id=id).first()
            if not cobranca_sql:
                raise ValueError(f"Cobrança {id} não encontrada")

            cobranca_sql.status = novo_status.value
            cobranca_sql.erro_mensagem = erro_mensagem
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def listar_por_status(self, status: StatusCobranca) -> list[Cobranca]:
        session = self.session_factory()
        try:
            cobrancas_sql = session.query(CobrancaSQL).filter_by(status=status.value).all()
            return [self._converter_para_entidade(c) for c in cobrancas_sql]
        finally:
            session.close()

    def listar_todas(self, limite: Optional[int] = None) -> list[Cobranca]:
        session = self.session_factory()
        try:
            query = session.query(CobrancaSQL).order_by(CobrancaSQL.criado_em.desc())
            if limite:
                query = query.limit(limite)
            cobrancas_sql = query.all()
            return [self._converter_para_entidade(c) for c in cobrancas_sql]
        finally:
            session.close()

    def atualizar(self, cobranca: Cobranca) -> Cobranca:
        session = self.session_factory()
        try:
            cobranca_sql = session.query(CobrancaSQL).filter_by(id=cobranca.id).first()
            if not cobranca_sql:
                raise ValueError(f"Cobrança {cobranca.id} não encontrada")

            cobranca_sql.fonte_id = cobranca.fonte_id
            cobranca_sql.email_id = cobranca.email_id
            cobranca_sql.hash_unico = cobranca.hash_unico
            cobranca_sql.valor = cobranca.valor
            cobranca_sql.data_vencimento = cobranca.data_vencimento
            cobranca_sql.tipo_pagamento = cobranca.tipo_pagamento
            cobranca_sql.codigo_pix = cobranca.codigo_pix
            cobranca_sql.codigo_barras = cobranca.codigo_barras
            cobranca_sql.link_boleto = cobranca.link_boleto
            cobranca_sql.descricao = cobranca.descricao
            cobranca_sql.status = cobranca.status.value
            cobranca_sql.erro_mensagem = cobranca.erro_mensagem

            session.commit()
            session.refresh(cobranca_sql)
            return self._converter_para_entidade(cobranca_sql)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _converter_para_entidade(self, cobranca_sql: CobrancaSQL) -> Cobranca:
        return Cobranca(
            id=cobranca_sql.id,
            fonte_id=cobranca_sql.fonte_id,
            email_id=cobranca_sql.email_id,
            hash_unico=cobranca_sql.hash_unico,
            valor=Decimal(str(cobranca_sql.valor)),
            data_vencimento=cobranca_sql.data_vencimento,
            tipo_pagamento=cobranca_sql.tipo_pagamento,
            codigo_pix=cobranca_sql.codigo_pix,
            codigo_barras=cobranca_sql.codigo_barras,
            link_boleto=cobranca_sql.link_boleto,
            descricao=cobranca_sql.descricao,
            status=StatusCobranca(cobranca_sql.status),
            erro_mensagem=cobranca_sql.erro_mensagem,
            criado_em=cobranca_sql.criado_em,
            atualizado_em=cobranca_sql.atualizado_em
        )
