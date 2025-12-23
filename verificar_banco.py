import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("=" * 60)
print("TABELAS CRIADAS:")
print("=" * 60)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tabelas = cursor.fetchall()
for tabela in tabelas:
    print(f"  > {tabela[0]}")

print("\n" + "=" * 60)
print("ROTINAS INICIALIZADAS:")
print("=" * 60)
cursor.execute("SELECT nome_rotina, ultimo_status, intervalo_minutos FROM controle_execucoes;")
rotinas = cursor.fetchall()
for rotina in rotinas:
    print(f"  - {rotina[0]}")
    print(f"    Status: {rotina[1]}")
    print(f"    Intervalo: {rotina[2]} minutos")
    print()

print("=" * 60)
print("FONTES AUTORIZADAS:")
print("=" * 60)
cursor.execute("SELECT COUNT(*) FROM fontes_autorizadas;")
count = cursor.fetchone()[0]
print(f"  Total: {count}")

print("\n" + "=" * 60)
print("COBRANCAS:")
print("=" * 60)
cursor.execute("SELECT COUNT(*) FROM cobrancas;")
count = cursor.fetchone()[0]
print(f"  Total: {count}")

conn.close()

print("\n>>> BANCO DE DADOS FUNCIONANDO PERFEITAMENTE!")
