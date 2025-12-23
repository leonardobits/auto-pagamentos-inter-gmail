import os
import base64
from typing import Optional
from simplegmail import Gmail
from simplegmail.query import construct_query
from ...aplicacao.portas.cliente_email import Email, ClienteEmail
from ...dominio.entidades.fonte_autorizada import FonteAutorizada

class ClienteGmail:
    def __init__(self, caminho_credenciais: str):
        self.caminho_credenciais = caminho_credenciais
        self.gmail: Optional[Gmail] = None
        self.label_processado = "Processado"

    def autenticar(self) -> None:
        if not os.path.exists(self.caminho_credenciais):
            raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {self.caminho_credenciais}")

        self.gmail = Gmail(client_secret_file=self.caminho_credenciais)
        self._criar_label_se_necessario()

    def _criar_label_se_necessario(self) -> None:
        try:
            labels_existentes = self.gmail.list_labels()
            if self.label_processado not in [label.name for label in labels_existentes]:
                self.gmail.create_label(self.label_processado)
        except Exception:
            pass

    def buscar_emails_nao_processados(self, fonte: FonteAutorizada, dias: int = 30) -> list[Email]:
        if not self.gmail:
            self.autenticar()

        query_params = {
            'sender': fonte.email_remetente,
            'newer_than': (dias, 'day'),
            'exclude_labels': [self.label_processado]
        }

        query = construct_query(query_params)
        mensagens = self.gmail.get_messages(query=query)

        emails = []
        for mensagem in mensagens:
            email = self._converter_mensagem_para_email(mensagem)
            if email:
                emails.append(email)

        return emails

    def _converter_mensagem_para_email(self, mensagem) -> Optional[Email]:
        try:
            remetente = mensagem.sender
            assunto = mensagem.subject or ""
            corpo = mensagem.plain or ""
            corpo_html = mensagem.html or ""

            anexos = []
            if mensagem.attachments:
                for anexo in mensagem.attachments:
                    anexos.append({
                        'filename': anexo.filename,
                        'attachment_id': anexo.attachment_id if hasattr(anexo, 'attachment_id') else None,
                        'data': anexo.data if hasattr(anexo, 'data') else None
                    })

            return Email(
                id=mensagem.id,
                remetente=remetente,
                assunto=assunto,
                corpo=corpo,
                corpo_html=corpo_html,
                anexos=anexos
            )
        except Exception as e:
            print(f"Erro ao converter mensagem {mensagem.id}: {str(e)}")
            return None

    def marcar_como_processado(self, email_id: str) -> None:
        if not self.gmail:
            self.autenticar()

        try:
            mensagem = self.gmail.get_message_by_id(email_id)
            mensagem.add_label(self.label_processado)
        except Exception as e:
            print(f"Erro ao marcar email {email_id} como processado: {str(e)}")

    def baixar_anexo(self, email_id: str, attachment_id: str, destino: str) -> str:
        if not self.gmail:
            self.autenticar()

        try:
            mensagem = self.gmail.get_message_by_id(email_id)

            for anexo in mensagem.attachments:
                if hasattr(anexo, 'attachment_id') and anexo.attachment_id == attachment_id:
                    anexo.save(filepath=destino)
                    return destino

            raise ValueError(f"Anexo {attachment_id} não encontrado no email {email_id}")
        except Exception as e:
            raise Exception(f"Erro ao baixar anexo: {str(e)}")
