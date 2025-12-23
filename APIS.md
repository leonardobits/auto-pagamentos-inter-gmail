# Documentação das APIs Necessárias

## 🏦 Banco Inter - APIs Banking

### Portal Oficial
- **URL**: https://developers.inter.co/
- **Tipo de Conta**: Apenas PJ (Pessoa Jurídica)
- **Custo**: APIs gratuitas, taxas baixas para recebimentos

### APIs Disponíveis para o Projeto

#### 1. API Pix Pagamento
**Funcionalidade**: Realizar pagamentos Pix (incluindo Pix Copia e Cola)

**Endpoint Principal**: Método de inclusão de pagamento Pix
- Permite pagamentos imediatos
- Permite pagamentos agendados
- Suporta Pix Copia e Cola (código Pix)

**Documentação**: https://developers.inter.co/references/pix-automatico

#### 2. API de Pagamentos (Banking)
**Funcionalidade**: Realizar pagamentos diversos (boletos, transferências)

**Recursos disponíveis**:
- Pagamentos imediatos
- Pagamentos agendados
- Consulta de extrato
- Consulta de saldo

#### 3. API Cobrança (Boleto com Pix)
**Funcionalidade**: Emitir cobranças (útil se quiser gerar boletos futuramente)

**Documentação**: https://developers.inter.co/references/cobranca-bolepix

### Autenticação Inter

**Requisitos**:
1. Acessar Internet Banking
2. Login via QR Code
3. Ir em "Soluções para sua empresa"
4. Clicar em "Nova Integração"
5. Preencher informações e aceitar permissões
6. Baixar chaves e certificados

**Credenciais necessárias**:
- Client ID
- Client Secret
- Certificados (.crt e .key)

**Método de autenticação**: OAuth 2.0 com certificados

### SDKs Oficiais
- Java
- C#

**Observação**: Para Node.js ou Python, será necessário usar bibliotecas da comunidade ou implementar chamadas HTTP diretamente.

### Bibliotecas da Comunidade

**PHP**:
- `divulgueregional/api-inter-v2` (GitHub)
- `allgood/APInter-PHP` (GitHub)

**Python**:
- `bancointer-python` (GitHub - renatojdev/bancointer-python)

**Para Node.js**: Não há SDK oficial, precisará implementar HTTP client com certificados

---

## 📧 Gmail API

### Portal Oficial
- **URL**: https://developers.google.com/gmail/api
- **Tipo**: API RESTful
- **Custo**: Gratuito (dentro dos limites do Google Cloud)

### Funcionalidades Necessárias

#### 1. Ler E-mails (Messages.list e Messages.get)

**Recursos**:
- Buscar mensagens com filtros
- Filtrar por remetente (`from:email@example.com`)
- Filtrar por assunto (`subject:"texto"`)
- Filtrar por data (`after:2024/01/01`)
- Buscar apenas não lidas (`is:unread`)
- Filtrar por anexos (`has:attachment`, `filename:pdf`)

**Exemplo de query**:
```
from:contato@empresa.com subject:fatura has:attachment newer_than:7d
```

#### 2. Baixar Anexos (Messages.attachments.get)

**Recursos**:
- Obter anexos em base64
- Suporta PDFs, imagens, etc
- Salvar localmente para análise

#### 3. Modificar Labels (Messages.modify)

**Útil para**:
- Marcar e-mails como processados
- Criar label "Processado" ou "Cobrança Registrada"
- Evitar processar o mesmo e-mail duas vezes

### Autenticação Gmail

**Método**: OAuth 2.0

**Passo a passo**:
1. Criar projeto no Google Cloud Console
2. Ativar Gmail API
3. Configurar tela de consentimento OAuth
4. Criar credenciais OAuth 2.0 (tipo "Aplicativo Desktop" ou "Aplicativo Web")
5. Baixar arquivo `credentials.json` ou `client_secret.json`
6. Implementar fluxo OAuth (gera `token.json` após primeiro login)

**Scopes necessários**:
- `https://www.googleapis.com/auth/gmail.readonly` - Para ler e-mails
- `https://www.googleapis.com/auth/gmail.modify` - Para modificar labels
- `https://mail.google.com/` - Acesso completo (se necessário)

**Recomendação**: Use scope mínimo necessário (readonly + modify)

### Bibliotecas Recomendadas

#### Node.js
**googleapis** (oficial do Google)
```bash
npm install googleapis
```

**gmail-tester** (comunidade - simplificado)
```bash
npm install gmail-tester
```

**Recursos**:
- Filtrar por remetente (`from`)
- Filtrar por assunto (`subject`)
- Incluir anexos automaticamente
- Simples de usar

#### Python
**google-api-python-client** (oficial)
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**simplegmail** (comunidade - mais fácil)
```bash
pip install simplegmail
```

**Recursos**:
- API simplificada
- Filtros nativos (newer_than, labels, unread)
- Anexos automáticos
- Muito mais legível que a API oficial

### Exemplo de Filtros Gmail API

**Buscar cobranças de um remetente específico**:
```
from:financeiro@empresa.com.br has:attachment
```

**Buscar apenas não processadas** (usando label):
```
from:cobrancas@fornecedor.com -label:processado
```

**Buscar por palavra-chave no assunto**:
```
subject:fatura OR subject:cobrança OR subject:boleto
```

---

## 🔧 Recomendações de Stack Técnica

### Opção 1: Node.js
**Vantagens**:
- Bibliotecas Gmail bem mantidas (googleapis)
- Boa para processar JSON
- Muitos exemplos na comunidade

**Desafios**:
- Sem SDK oficial do Inter (precisa implementar HTTP + certificados)

**Bibliotecas Inter**: Implementação manual com `axios` ou `node-fetch` + certificados

### Opção 2: Python
**Vantagens**:
- Biblioteca simplegmail muito fácil de usar
- Biblioteca bancointer-python disponível
- Excelente para parsing de PDFs e textos

**Recomendação**: ⭐ **Python é a melhor escolha para este projeto**

**Stack sugerida**:
- `simplegmail` - Para Gmail
- `bancointer-python` ou HTTP requests com `requests` - Para Inter
- `pdfplumber` ou `PyPDF2` - Para ler PDFs
- `sqlite3` (built-in) ou `PostgreSQL` - Para banco de dados
- `schedule` ou `APScheduler` - Para agendamentos

---

## 📚 Fontes e Documentação

### Banco Inter
- [Portal do Desenvolvedor Inter](https://developers.inter.co/)
- [API Pix Automático](https://developers.inter.co/references/pix-automatico)
- [API Cobrança (Boleto com Pix)](https://developers.inter.co/references/cobranca-bolepix)
- [Inter Banking APIs](https://inter.co/empresas/api-banking/)
- [API Pix Inter](https://inter.co/empresas/api-pix/)

### Gmail API
- [Gmail API Overview](https://developers.google.com/workspace/gmail/api/guides)
- [Node.js Quickstart](https://developers.google.com/workspace/gmail/api/quickstart/nodejs)
- [Gmail API REST Reference](https://developers.google.com/workspace/gmail/api/reference/rest)
- [OAuth 2.0 Mechanism](https://developers.google.com/gmail/imap/xoauth2-protocol)

### Bibliotecas
- [simplegmail (Python)](https://pypi.org/project/simplegmail/)
- [bancointer-python](https://github.com/renatojdev/bancointer-python)
- [gmail-tester (Node.js)](https://www.npmjs.com/package/gmail-tester)
- [googleapis (Node.js)](https://googleapis.dev/nodejs/googleapis/latest/gmail/classes/Gmail.html)

### Tutoriais
- [How to Use Gmail API in Python](https://thepythoncode.com/article/use-gmail-api-in-python)
- [GeeksforGeeks - Reading Gmail with Python](https://www.geeksforgeeks.org/python/how-to-read-emails-from-gmail-using-gmail-api-in-python/)
- [Como Enviar Emails em Python (PT-BR)](https://mailtrap.io/blog/python-send-email-gmail/)
- [How to Send and Read Emails with Gmail API](https://mailtrap.io/blog/send-emails-with-gmail-api/)

---

## ⚠️ Pontos de Atenção

### Banco Inter
1. **Conta PJ obrigatória** - APIs não funcionam com conta pessoa física
2. **Certificados digitais** - Autenticação requer certificados além de Client ID/Secret
3. **Ambiente sandbox** - Inter oferece ambiente de testes
4. **Webhooks disponíveis** - Para receber notificações de pagamentos em tempo real

### Gmail API
1. **Quotas do Google** - 1 bilhão de unidades/dia (suficiente para uso pessoal)
2. **Token expira** - Refresh token mantém acesso contínuo
3. **Primeiro acesso manual** - Precisa autorizar via navegador uma vez
4. **Labels customizadas** - Criar label "Processado" para evitar duplicação

### Segurança
1. **Nunca commitar credenciais** - Arquivos JSON de credenciais no .gitignore
2. **Certificados Inter sensíveis** - Armazenar de forma segura
3. **Tokens Gmail sensíveis** - token.json dá acesso ao e-mail
4. **Validação de remetentes** - SEMPRE validar fonte antes de processar
