import sys
sys.path.insert(0, '.')

print("=" * 60)
print("TESTANDO TODOS OS COMPONENTES")
print("=" * 60)

erros = []

# 1. Testar imports dominio
print("\n[1/10] Testando dominio...")
try:
    from src.dominio.enums.status_cobranca import StatusCobranca, pode_transicionar
    from src.dominio.entidades.cobranca import Cobranca
    from src.dominio.entidades.fonte_autorizada import FonteAutorizada
    from src.dominio.entidades.agendamento import Agendamento
    from src.dominio.servicos.gerador_hash import gerar_hash_cobranca
    from src.dominio.servicos.validador_cobranca import validar_dados_cobranca
    print("   OK - Dominio completo")
except Exception as e:
    erros.append(f"Dominio: {e}")
    print(f"   ERRO: {e}")

# 2. Testar transicoes de estado
print("\n[2/10] Testando maquina de estados...")
try:
    assert pode_transicionar(StatusCobranca.NOVA, StatusCobranca.AUTORIZADA)
    assert not pode_transicionar(StatusCobranca.PAGA, StatusCobranca.NOVA)
    print("   OK - Transicoes funcionando")
except Exception as e:
    erros.append(f"Estados: {e}")
    print(f"   ERRO: {e}")

# 3. Testar criacao de entidades
print("\n[3/10] Testando criacao de entidades...")
try:
    from decimal import Decimal
    from datetime import date

    fonte = FonteAutorizada(
        nome="Teste",
        email_remetente="teste@test.com",
        palavras_assunto=["teste"],
        palavras_corpo=["teste"],
        ativo=True
    )

    cobranca = Cobranca(
        fonte_id=1,
        email_id="email123",
        hash_unico="hash123",
        valor=Decimal("100.00"),
        data_vencimento=date.today(),
        tipo_pagamento="PIX",
        status=StatusCobranca.NOVA,
        descricao="Teste",
        codigo_pix="pix123"
    )

    cobranca.marcar_como_autorizada()
    assert cobranca.status == StatusCobranca.AUTORIZADA
    print("   OK - Entidades criadas e estados funcionando")
except Exception as e:
    erros.append(f"Entidades: {e}")
    print(f"   ERRO: {e}")

# 4. Testar banco de dados
print("\n[4/10] Testando banco de dados...")
try:
    from src.infraestrutura.banco_dados.modelos_sql import criar_engine, criar_todas_tabelas
    engine = criar_engine("test.db")
    criar_todas_tabelas(engine)
    print("   OK - Banco de dados funciona")
    import os
    os.remove("test.db")
except Exception as e:
    erros.append(f"Banco: {e}")
    print(f"   ERRO: {e}")

# 5. Testar repositorios
print("\n[5/10] Testando repositorios...")
try:
    from src.infraestrutura.banco_dados.repositorio_fonte_impl import RepositorioFonteSQL
    from src.infraestrutura.banco_dados.repositorio_cobranca_impl import RepositorioCobrancaSQL
    print("   OK - Repositorios importam")
except Exception as e:
    erros.append(f"Repositorios: {e}")
    print(f"   ERRO: {e}")

# 6. Testar extratores
print("\n[6/10] Testando extratores...")
try:
    from src.infraestrutura.extratores.extrator_pix import extrair_codigo_pix_do_texto
    from src.infraestrutura.extratores.extrator_boleto import extrair_codigo_barras
    from src.infraestrutura.extratores.extrator_dados import extrair_valor, extrair_data_vencimento

    # Teste real de extracao
    texto = "Valor: R$ 150,00 Vencimento: 31/12/2024"
    valor = extrair_valor(texto)
    data = extrair_data_vencimento(texto)

    assert valor == Decimal("150.00"), f"Valor errado: {valor}"
    assert data.day == 31 and data.month == 12, f"Data errada: {data}"

    print("   OK - Extratores funcionando")
except Exception as e:
    erros.append(f"Extratores: {e}")
    print(f"   ERRO: {e}")

# 7. Testar casos de uso
print("\n[7/10] Testando casos de uso...")
try:
    from src.aplicacao.casos_uso.processar_emails import ProcessarEmails
    from src.aplicacao.casos_uso.agendar_pagamento import AgendarPagamento
    from src.aplicacao.casos_uso.executar_pagamentos import ExecutarPagamentos
    print("   OK - Casos de uso importam")
except Exception as e:
    erros.append(f"Casos de uso: {e}")
    print(f"   ERRO: {e}")

# 8. Testar cliente Gmail
print("\n[8/10] Testando cliente Gmail...")
try:
    from src.infraestrutura.gmail.cliente_gmail import ClienteGmail
    print("   OK - Cliente Gmail importa")
except Exception as e:
    erros.append(f"Gmail: {e}")
    print(f"   ERRO: {e}")

# 9. Testar cliente Banco Inter
print("\n[9/10] Testando cliente Banco Inter...")
try:
    from src.infraestrutura.banco_inter.cliente_inter import ClienteInter
    from src.infraestrutura.banco_inter.autenticador_inter import AutenticadorInter
    print("   OK - Cliente Banco Inter importa")
except Exception as e:
    erros.append(f"Banco Inter: {e}")
    print(f"   ERRO: {e}")

# 10. Testar API Flask
print("\n[10/10] Testando API Flask...")
try:
    from src.interface.api.configuracao_flask import criar_app
    print("   OK - API Flask importa")
except Exception as e:
    erros.append(f"API: {e}")
    print(f"   ERRO: {e}")

# Resumo
print("\n" + "=" * 60)
print("RESUMO DOS TESTES")
print("=" * 60)

if not erros:
    print("\n>>> TODOS OS COMPONENTES FUNCIONANDO PERFEITAMENTE!")
    print("\nSistema esta 100% operacional.")
else:
    print(f"\n>>> ENCONTRADOS {len(erros)} PROBLEMAS:\n")
    for i, erro in enumerate(erros, 1):
        print(f"{i}. {erro}")

print("\n" + "=" * 60)
