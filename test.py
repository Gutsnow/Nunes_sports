import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Funções do Banco de Dados e CRUD
def connect_db():
    conn = sqlite3.connect('nunes_sports.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            codigo TEXT NOT NULL UNIQUE,
            descricao TEXT,
            preco REAL
        )
    ''')
    conn.commit()
    return conn, cursor

def gerar_codigo_unico():
    conn, cursor = connect_db()
    cursor.execute('SELECT IFNULL(MAX(id), 0) + 1 FROM produtos')
    novo_id = cursor.fetchone()[0]
    conn.close()
    return f"P{novo_id:06d}"

def inserir_produto(nome, descricao, preco):
    conn, cursor = connect_db()
    try:
        codigo = gerar_codigo_unico()  # Gera o código antes da inserção
        cursor.execute('''
            INSERT INTO produtos (nome, codigo, descricao, preco) 
            VALUES (?, ?, ?, ?)
        ''', (nome, codigo, descricao, preco))
        conn.commit()
    except sqlite3.IntegrityError as e:
        messagebox.showerror("Erro", f"Erro ao inserir o produto: {e}")
    finally:
        conn.close()

def visualizar_produtos():
    conn, cursor = connect_db()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def excluir_produto_do_bd(produto_id):
    conn, cursor = connect_db()
    cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
    conn.commit()
    conn.close()

def atualizar_produto(produto_id, nome, descricao, preco):
    conn, cursor = connect_db()
    try:
        cursor.execute('''
            UPDATE produtos 
            SET nome = ?, descricao = ?, preco = ?
            WHERE id = ?
        ''', (nome, descricao, preco, produto_id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        messagebox.showerror("Erro", f"Erro ao atualizar o produto: {e}")
    finally:
        conn.close()

# Funções de Interface
def atualizar_tabela():
    for i in tree.get_children():
        tree.delete(i)
    produtos = visualizar_produtos()
    for produto in produtos:
        tree.insert("", "end", values=produto)

def cadastrar_produto():
    def salvar_produto():
        nome = entry_nome.get()
        descricao = entry_descricao.get()
        preco = entry_preco.get()
        inserir_produto(nome, descricao, preco)
        atualizar_tabela()
        janela_cadastro.destroy()

    janela_cadastro = tk.Toplevel(root)
    janela_cadastro.title("Cadastrar Produto")
    janela_cadastro.geometry("400x300")

    tk.Label(janela_cadastro, text="Nome:").pack(pady=5)
    entry_nome = tk.Entry(janela_cadastro)
    entry_nome.pack(pady=5)

    tk.Label(janela_cadastro, text="Descrição:").pack(pady=5)
    entry_descricao = tk.Entry(janela_cadastro)
    entry_descricao.pack(pady=5)

    tk.Label(janela_cadastro, text="Preço:").pack(pady=5)
    entry_preco = tk.Entry(janela_cadastro)
    entry_preco.pack(pady=5)

    btn_salvar = tk.Button(janela_cadastro, text="Salvar", bg='blue', fg='white', command=salvar_produto)
    btn_salvar.pack(pady=20)

    btn_cancelar = tk.Button(janela_cadastro, text="Cancelar", bg='blue', fg='white', command=janela_cadastro.destroy)
    btn_cancelar.pack()

def editar_produto():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Erro", "Por favor, selecione um produto para editar")
        return
    
    produto = tree.item(selected_item[0])['values']
    produto_id = produto[0]

    def salvar_edicao():
        nome = entry_nome.get()
        descricao = entry_descricao.get()
        preco = entry_preco.get()
        atualizar_produto(produto_id, nome, descricao, preco)
        atualizar_tabela()
        janela_edicao.destroy()

    def excluir_produto():
        excluir_produto_do_bd(produto_id)
        atualizar_tabela()
        janela_edicao.destroy()
        messagebox.showinfo("Sucesso", "Produto excluído com sucesso")

    janela_edicao = tk.Toplevel(root)
    janela_edicao.title("Editar Produto")
    janela_edicao.geometry("400x350")

    tk.Label(janela_edicao, text="Nome:").pack(pady=5)
    entry_nome = tk.Entry(janela_edicao)
    entry_nome.insert(0, produto[1])
    entry_nome.pack(pady=5)

    tk.Label(janela_edicao, text="Descrição:").pack(pady=5)
    entry_descricao = tk.Entry(janela_edicao)
    entry_descricao.insert(0, produto[3])
    entry_descricao.pack(pady=5)

    tk.Label(janela_edicao, text="Preço:").pack(pady=5)
    entry_preco = tk.Entry(janela_edicao)
    entry_preco.insert(0, produto[4])
    entry_preco.pack(pady=5)

    btn_salvar = tk.Button(janela_edicao, text="Salvar", bg='blue', fg='white', command=salvar_edicao)
    btn_salvar.pack(side='left', padx=10, pady=20)

    btn_excluir = tk.Button(janela_edicao, text="Excluir Produto", bg='blue', fg='white', command=excluir_produto)
    btn_excluir.pack(side='left', padx=10, pady=20)

    btn_cancelar = tk.Button(janela_edicao, text="Cancelar", bg='blue', fg='white', command=janela_edicao.destroy)
    btn_cancelar.pack(side='left', padx=10, pady=20)

def excluir_produto():
    selected_item = tree.selection()
    
    if not selected_item:
        messagebox.showwarning("Erro", "Por favor, selecione um produto para excluir")
        return
    
    item_id = selected_item[0]
    produto = tree.item(item_id)['values']
    
    if not produto:
        messagebox.showerror("Erro", "Erro ao recuperar os dados do produto selecionado")
        return
    
    produto_id = produto[0]
    
    try:
        excluir_produto_do_bd(produto_id)
        atualizar_tabela()
        messagebox.showinfo("Sucesso", "Produto excluído com sucesso")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao excluir o produto: {e}")

# Configuração da Janela Principal e Botões
root = tk.Tk()
root.title("Nunes Sports")
root.geometry("800x600")

# Criação do header
header = tk.Frame(root, bg='blue', height=50)
header.pack(fill='x')

title_label = tk.Label(header, text="Nunes Sports", fg='white', bg='blue', font=('Arial', 20, 'bold'))
title_label.pack(side='left', padx=10)

# Área principal
main_frame = tk.Frame(root)
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Tabela de produtos
columns = ("id", "nome", "codigo", "descricao", "preco")
tree = ttk.Treeview(main_frame, columns=columns, show='headings')
tree.heading("id", text="ID")
tree.heading("nome", text="Nome do Produto")
tree.heading("codigo", text="Código do Produto")
tree.heading("descricao", text="Descrição do Produto")
tree.heading("preco", text="Preço do Produto")
tree.column("id", width=50)
tree.column("nome", width=200)
tree.column("codigo", width=100)
tree.column("descricao", width=300)
tree.column("preco", width=100)
tree.pack(fill='both', expand=True)

# Botões de ação
button_frame = tk.Frame(main_frame)
button_frame.pack(fill='x', pady=10)

btn_cadastrar = tk.Button(button_frame, text="Cadastrar Produto", bg='blue', fg='white', font=('Arial', 12, 'bold'), command=cadastrar_produto)
btn_cadastrar.pack(side='left', padx=5)

btn_editar = tk.Button(button_frame, text="Editar Produto", bg='blue', fg='white', font=('Arial', 12, 'bold'), command=editar_produto)
btn_editar.pack(side='left', padx=5)

btn_excluir = tk.Button(button_frame, text="Excluir Produto", bg='blue', fg='white', font=('Arial', 12, 'bold'), command=excluir_produto)
btn_excluir.pack(side='left', padx=5)

# Atualizando a tabela ao iniciar
atualizar_tabela()

# Inicialização da interface gráfica
root.mainloop()
