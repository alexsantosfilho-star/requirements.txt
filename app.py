import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

# --- CONFIGURAÇÃO DO BANCO DE DATOS ---
def iniciar_db():
    conn = sqlite3.connect('biblioteca.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS livros 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, autor TEXT, categoria TEXT, qtd INTEGER, emprestados_count INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (id INTEGER PRIMARY KEY, nome TEXT, tipo TEXT, livros_ativos INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS emprestimos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, id_user INTEGER, titulo_livro TEXT, data_saida DATE, data_prevista DATE, status TEXT)''')
    conn.commit()
    return conn

conn = iniciar_db()

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Sistema de Biblioteca", layout="centered")
st.title("📚 Sistema de Gestão de Biblioteca")

menu = ["Cadastrar Livro", "Registrar Empréstimo", "Relatórios"]
escolha = st.sidebar.selectbox("Menu", menu)

if escolha == "Cadastrar Livro":
    st.subheader("Novo Cadastro")
    with st.form("form_livro"):
        titulo = st.text_input("Título do Livro")
        autor = st.text_input("Autor")
        categoria = st.text_input("Categoria")
        qtd = st.number_input("Quantidade em Estoque", min_value=1, step=1)
        btn = st.form_submit_button("Salvar")
        
        if btn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO livros (titulo, autor, categoria, qtd) VALUES (?, ?, ?, ?)", (titulo, autor, categoria, qtd))
            conn.commit()
            st.success(f"Livro '{titulo}' cadastrado!")

elif escolha == "Registrar Empréstimo":
    st.subheader("Novo Empréstimo")
    id_user = st.number_input("ID do Usuário", min_value=1, step=1)
    
    # Busca livros disponíveis para o selectbox
    livros_disponiveis = pd.read_sql("SELECT titulo FROM livros WHERE qtd > 0", conn)
    titulo_selecionado = st.selectbox("Selecione o Livro", livros_disponiveis['titulo']) if not livros_disponiveis.empty else None

    if st.button("Confirmar Empréstimo"):
        if titulo_selecionado:
            cursor = conn.cursor()
            user = cursor.execute("SELECT tipo, livros_ativos FROM usuarios WHERE id = ?", (id_user,)).fetchone()
            
            if not user:
                st.error("Usuário não cadastrado! (Cadastre no banco primeiro)")
            elif user[0] == 'Aluno' and user[1] >= 2:
                st.warning("⚠️ Limite atingido! Alunos só podem ter 2 livros.")
            else:
                data_saida = datetime.now()
                data_prevista = data_saida + timedelta(days=7)
                
                cursor.execute("INSERT INTO emprestimos (id_user, titulo_livro, data_saida, data_prevista, status) VALUES (?, ?, ?, ?, 'Ativo')", 
                               (id_user, titulo_selecionado, data_saida.date(), data_prevista.date()))
                cursor.execute("UPDATE usuarios SET livros_ativos = livros_ativos + 1 WHERE id = ?", (id_user,))
                cursor.execute("UPDATE livros SET qtd = qtd - 1, emprestados_count = emprestados_count + 1 WHERE titulo = ?", (titulo_selecionado,))
                conn.commit()
                st.success(f"📖 Empréstimo realizado! Devolução: {data_prevista.strftime('%d/%m/%Y')}")
        else:
            st.error("Nenhum livro disponível no momento.")

elif escolha == "Relatórios":
    st.subheader("🏆 Livros Mais Emprestados")
    dados = pd.read_sql("SELECT titulo, emprestados_count FROM livros ORDER BY emprestados_count DESC", conn)
    st.table(dados)
    
    st.subheader("📋 Todos os Empréstimos")
    todos = pd.read_sql("SELECT * FROM emprestimos", conn)
    st.dataframe(todos)
