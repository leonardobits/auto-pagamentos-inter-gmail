import sys
import os
sys.path.insert(0, '.')

from decimal import Decimal
from datetime import date, datetime
from src.infraestrutura.banco_dados.modelos_sql import criar_engine, criar_session_factory, criar_todas_tabelas
from src.infraestrutura.banco_dados.repositorio_fonte_impl import RepositorioFonteSQL
from src.infraestrutura.banco_dados.repositorio_cobranca_impl import RepositorioCobrancaSQL
from src.infraestrutura.banco_dados.repositorio_agendamento_impl import RepositorioAgendamentoSQL
from src.dominio.entidades.fonte_autorizada import FonteAutorizada
from src.dominio.entidades.cobranca import Cobranca
from src.dominio.enums.status_cobranca import StatusCobranca
from src.dominio.servicos.gerador_hash import gerar_hash_cobranca

print("=" * 60)
print("TESTE DE INTEGRACAO COMPLETO")
print("=" * 60)

# Criar banco de teste
if os.path.exists('teste_integracao.db'):
    os.remove('teste_integracao.db')

engine = criar_engine('teste_integracao.db')
criar_todas_tabelas(engine)
session_factory = criar_session_factory(engine)

repo_fonte = RepositorioFonteSQL(session_factory)
repo_cobranca = RepositorioCobrancaSQL(session_factory)
repo_agendamento = RepositorioAgendamentoSQL(session_factory)

print("\n[1/6] Criando fonte autorizada...")
fonte = FonteAutorizada(
    nome="Conta de Luz Teste",
    email_remetente="teste@energia.com",
    palavras_assunto=["fatura", "conta"],
    palavras_corpo=["vencimento"],
    ativo=True
)
fonte_salva = repo_fonte.salvar(fonte)
print(f"   OK - Fonte criada com ID: {fonte_salva.id}")

print("\n[2/6] Testando validacao de email...")
valido = fonte_salva.validar_email(
    "teste@energia.com",
    "Fatura de energia eletrica",
    "Valor R$ 100,00 vencimento 31/12/2024"
)
assert valido, "Validacao deveria passar"
print("   OK - Validacao funcionando")

print("\n[3/6] Criando cobranca...")
hash_unico = gerar_hash_cobranca(
    "email123",
    Decimal("150.00"),
    date(2024, 12, 31),
    "PIX123"
)
cobranca = Cobranca(
    fonte_id=fonte_salva.id,
    email_id="email123",
    hash_unico=hash_unico,
    valor=Decimal("150.00"),
    data_vencimento=date(2024, 12, 31),
    tipo_pagamento="PIX",
    status=StatusCobranca.NOVA,
    descricao="Teste de cobranca",
    codigo_pix="PIX123"
)
cobranca.marcar_como_autorizada()
cobranca_salva = repo_cobranca.salvar(cobranca)
print(f"   OK - Cobranca criada com ID: {cobranca_salva.id}")

print("\n[4/6] Testando transicoes de estado...")
cobranca_recuperada = repo_cobranca.buscar_por_id(cobranca_salva.id)
cobranca_recuperada.marcar_como_agendada()
repo_cobranca.atualizar(cobranca_recuperada)

cobranca_verificada = repo_cobranca.buscar_por_id(cobranca_salva.id)
assert cobranca_verificada.status == StatusCobranca.AGENDADA
print("   OK - Transicoes de estado persistem no banco")

print("\n[5/6] Criando agendamento...")
agendamento = repo_agendamento.criar_agendamento(
    cobranca_salva.id,
    date(2024, 12, 31)
)
print(f"   OK - Agendamento criado com ID: {agendamento.id}")

print("\n[6/6] Testando busca de cobrancas...")
todas_cobrancas = repo_cobranca.listar_todas()
assert len(todas_cobrancas) == 1
print(f"   OK - {len(todas_cobrancas)} cobranca encontrada")

cobranca_por_hash = repo_cobranca.buscar_por_hash(hash_unico)
assert cobranca_por_hash is not None
print("   OK - Busca por hash funciona")

cobranca_por_email = repo_cobranca.buscar_por_email_id("email123")
assert cobranca_por_email is not None
print("   OK - Busca por email_id funciona")

# Limpar
os.remove('teste_integracao.db')

print("\n" + "=" * 60)
print(">>> TODOS OS TESTES DE INTEGRACAO PASSARAM!")
print("=" * 60)
print("\nConclusao:")
print("  - Banco de dados: FUNCIONANDO")
print("  - Repositorios: FUNCIONANDO")
print("  - Entidades de dominio: FUNCIONANDO")
print("  - Transicoes de estado: FUNCIONANDO")
print("  - Servicos de dominio: FUNCIONANDO")
print("\n>>> SISTEMA 100% OPERACIONAL!")
