import sqlite3
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DO BANCO DE DATOS ---
def iniciar_db():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS livros 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, autor TEXT, categoria TEXT, qtd INTEGER, emprestados_count INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (id INTEGER PRIMARY KEY, nome TEXT, tipo TEXT, livros_ativos INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS emprestimos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, id_user INTEGER, titulo_livro TEXT, data_saida DATE, data_prevista DATE, status TEXT)''')
    conn.commit()
    return conn

# --- FUNÇÕES DO SISTEMA ---
def cadastrar_livro(titulo, autor, categoria, qtd):
    conn = iniciar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO livros (titulo, autor, categoria, qtd) VALUES (?, ?, ?, ?)", (titulo, autor, categoria, qtd))
    conn.commit()
    print(f"\n✅ Livro '{titulo}' cadastrado com sucesso!")
    conn.close()

def registrar_emprestimo(id_user, titulo):
    conn = iniciar_db()
    cursor = conn.cursor()
    
    # Validações
    user = cursor.execute("SELECT tipo, livros_ativos FROM usuarios WHERE id = ?", (id_user,)).fetchone()
    livro = cursor.execute("SELECT qtd, emprestados_count FROM livros WHERE titulo = ?", (titulo,)).fetchone()

    if not user or not livro:
        print("\n❌ Erro: Usuário ou Livro não encontrado.")
        return

    if user[0] == 'Aluno' and user[1] >= 2:
        print("\n⚠️ Limite atingido! Alunos só podem ter 2 livros por vez.")
        return

    if livro[0] <= 0:
        print("\n⚠️ Livro esgotado no estoque.")
        return

    # Registrar
    data_saida = datetime.now()
    data_prevista = data_saida + timedelta(days=7)
    
    cursor.execute("INSERT INTO emprestimos (id_user, titulo_livro, data_saida, data_prevista, status) VALUES (?, ?, ?, ?, 'Ativo')", 
                   (id_user, titulo, data_saida.date(), data_prevista.date()))
    cursor.execute("UPDATE usuarios SET livros_ativos = livros_ativos + 1 WHERE id = ?", (id_user,))
    cursor.execute("UPDATE livros SET qtd = qtd - 1, emprestados_count = emprestados_count + 1 WHERE titulo = ?", (titulo,))
    
    conn.commit()
    print(f"\n📖 Empréstimo realizado! Devolução até: {data_prevista.strftime('%d/%m/%Y')}")
    conn.close()

def relatorio_mais_emprestados():
    conn = iniciar_db()
    cursor = conn.cursor()
    dados = cursor.execute("SELECT titulo, emprestados_count FROM livros ORDER BY emprestados_count DESC").fetchall()
    print("\n--- 🏆 LIVROS MAIS EMPRESTADOS ---")
    for d in dados:
        print(f"{d[0]}: {d[1]} vezes")
    conn.close()

# --- MENU PRINCIPAL ---
if __name__ == "__main__":
    iniciar_db()
    # Aqui você pode criar um loop simples de input ou rodar testes:
    # cadastrar_livro("Dom Casmurro", "Machado de Assis", "Literatura", 5)
    # registrar_emprestimo(1, "Dom Casmurro")
    relatorio_mais_emprestados()
