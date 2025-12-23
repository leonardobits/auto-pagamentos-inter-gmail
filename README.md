# Sistema de Automação de Cobranças e Pagamentos por E-mail

Sistema local que automatiza o processamento de cobranças recebidas por e-mail e executa pagamentos via API do Banco Inter.

## Funcionalidades

- Lê emails de fontes autorizadas automaticamente
- Extrai informações de cobrança (Pix, boleto, valor, vencimento)
- Registra cobranças em banco de dados local
- Agenda pagamentos automaticamente
- Executa pagamentos via API Banco Inter
- Previne pagamentos duplicados
- Resiliente a desligamentos (recupera execuções perdidas)

## Requisitos

- Python 3.10+
- Conta Gmail
- Conta PJ no Banco Inter
- Acesso às APIs do Google Cloud e Banco Inter

## Instalação

1. Clone o repositório
2. Crie ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale dependências:
```bash
pip install -r requirements.txt
```

## Configuração

### 1. Gmail API

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie novo projeto
3. Ative Gmail API
4. Crie credenciais OAuth 2.0 (tipo Desktop)
5. Baixe `credentials.json`
6. Coloque em `src/configuracao/credenciais/gmail_credentials.json`

### 2. Banco Inter API

1. Acesse Internet Banking do Inter (conta PJ)
2. Vá em "Soluções para sua empresa"
3. Crie "Nova Integração"
4. Escolha API: Pix Pagamento
5. Baixe Client ID, Client Secret e Certificados
6. Coloque arquivos em `src/configuracao/credenciais/`

### 3. Variáveis de Ambiente

Copie `.env.example` para `.env` e preencha com suas credenciais.

### 4. Primeira Fonte Autorizada

Execute o sistema e use a API para criar sua primeira fonte:

```bash
curl -X POST http://localhost:5000/fontes \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Conta de Luz",
    "email_remetente": "noreply@eletrobras.com",
    "palavras_assunto": ["fatura", "conta"],
    "palavras_corpo": ["vencimento"],
    "ativo": true
  }'
```

## Como Executar

```bash
python src/interface/inicializador.py
```

O sistema irá:
- Criar banco de dados SQLite
- Iniciar servidor Flask na porta 5000
- Iniciar scheduler automático
- Processar emails a cada 60 minutos
- Executar pagamentos a cada 30 minutos

## API de Controle

### Listar cobranças
```bash
curl http://localhost:5000/cobrancas
```

### Ver status do sistema
```bash
curl http://localhost:5000/status
```

### Processar emails manualmente
```bash
curl -X POST http://localhost:5000/executar/processar-emails
```

### Executar pagamentos manualmente
```bash
curl -X POST http://localhost:5000/executar/processar-pagamentos
```

## Arquitetura

O sistema segue Clean Architecture com 4 camadas:

```
Interface (API / Scheduler)
    ↓
Aplicação (Casos de Uso)
    ↓
Domínio (Regras de Negócio)
    ↓
Infraestrutura (Gmail, Banco Inter, Banco de Dados)
```


## Segurança

- Todas as credenciais são armazenadas localmente
- Apenas emails de fontes autorizadas são processados
- Sistema usa OAuth2 para Gmail e Banco Inter
- Prevenção de pagamentos duplicados em múltiplas camadas
- Todas as tentativas de pagamento são auditadas

## Licença

Uso pessoal.
