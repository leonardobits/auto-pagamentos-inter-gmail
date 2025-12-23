import requests
from datetime import datetime, timedelta
from typing import Optional

class AutenticadorInter:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        caminho_certificado: str,
        caminho_chave: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.caminho_certificado = caminho_certificado
        self.caminho_chave = caminho_chave
        self.token_atual: Optional[str] = None
        self.expiracao_token: Optional[datetime] = None
        self.url_autenticacao = "https://cdpj.partners.bancointer.com.br/oauth/v2/token"

    def obter_token(self) -> str:
        if self._token_valido():
            return self.token_atual

        return self._renovar_token()

    def _token_valido(self) -> bool:
        if not self.token_atual or not self.expiracao_token:
            return False

        return datetime.now() < self.expiracao_token

    def _renovar_token(self) -> str:
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'pagamento-pix.write',
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(
                self.url_autenticacao,
                data=payload,
                cert=(self.caminho_certificado, self.caminho_chave),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code == 200:
                dados = response.json()
                self.token_atual = dados['access_token']
                expires_in = dados.get('expires_in', 3600)
                self.expiracao_token = datetime.now() + timedelta(seconds=expires_in - 60)
                return self.token_atual
            else:
                raise Exception(f"Erro ao autenticar: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Erro na autenticação com Banco Inter: {str(e)}")
