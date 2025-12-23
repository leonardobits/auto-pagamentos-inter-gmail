from typing import Optional
import json
from .modelos_sql import FonteAutorizadaSQL
from ...dominio.entidades.fonte_autorizada import FonteAutorizada

class RepositorioFonteSQL:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def listar_ativas(self) -> list[FonteAutorizada]:
        session = self.session_factory()
        try:
            fontes_sql = session.query(FonteAutorizadaSQL).filter_by(ativo=True).all()
            return [self._converter_para_entidade(f) for f in fontes_sql]
        finally:
            session.close()

    def buscar_por_id(self, id: int) -> Optional[FonteAutorizada]:
        session = self.session_factory()
        try:
            fonte_sql = session.query(FonteAutorizadaSQL).filter_by(id=id).first()
            return self._converter_para_entidade(fonte_sql) if fonte_sql else None
        finally:
            session.close()

    def salvar(self, fonte: FonteAutorizada) -> FonteAutorizada:
        session = self.session_factory()
        try:
            fonte_sql = FonteAutorizadaSQL(
                nome=fonte.nome,
                email_remetente=fonte.email_remetente,
                palavras_assunto=json.dumps(fonte.palavras_assunto),
                palavras_corpo=json.dumps(fonte.palavras_corpo),
                ativo=fonte.ativo
            )
            session.add(fonte_sql)
            session.commit()
            session.refresh(fonte_sql)
            return self._converter_para_entidade(fonte_sql)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def listar_todas(self) -> list[FonteAutorizada]:
        session = self.session_factory()
        try:
            fontes_sql = session.query(FonteAutorizadaSQL).all()
            return [self._converter_para_entidade(f) for f in fontes_sql]
        finally:
            session.close()

    def atualizar(self, fonte: FonteAutorizada) -> FonteAutorizada:
        session = self.session_factory()
        try:
            fonte_sql = session.query(FonteAutorizadaSQL).filter_by(id=fonte.id).first()
            if not fonte_sql:
                raise ValueError(f"Fonte {fonte.id} não encontrada")

            fonte_sql.nome = fonte.nome
            fonte_sql.email_remetente = fonte.email_remetente
            fonte_sql.palavras_assunto = json.dumps(fonte.palavras_assunto)
            fonte_sql.palavras_corpo = json.dumps(fonte.palavras_corpo)
            fonte_sql.ativo = fonte.ativo

            session.commit()
            session.refresh(fonte_sql)
            return self._converter_para_entidade(fonte_sql)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def desativar(self, id: int) -> None:
        session = self.session_factory()
        try:
            fonte_sql = session.query(FonteAutorizadaSQL).filter_by(id=id).first()
            if not fonte_sql:
                raise ValueError(f"Fonte {id} não encontrada")

            fonte_sql.ativo = False
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _converter_para_entidade(self, fonte_sql: FonteAutorizadaSQL) -> FonteAutorizada:
        palavras_assunto = json.loads(fonte_sql.palavras_assunto) if isinstance(fonte_sql.palavras_assunto, str) else fonte_sql.palavras_assunto
        palavras_corpo = json.loads(fonte_sql.palavras_corpo) if isinstance(fonte_sql.palavras_corpo, str) else fonte_sql.palavras_corpo

        return FonteAutorizada(
            id=fonte_sql.id,
            nome=fonte_sql.nome,
            email_remetente=fonte_sql.email_remetente,
            palavras_assunto=palavras_assunto,
            palavras_corpo=palavras_corpo,
            ativo=fonte_sql.ativo,
            criado_em=fonte_sql.criado_em,
            atualizado_em=fonte_sql.atualizado_em
        )
