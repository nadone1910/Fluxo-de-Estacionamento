import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from stilo import Estilo
from datetime import datetime

# ============================================================
# 1. Conexão com o banco de dados
# ============================================================
conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS titulos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cpf TEXT,
    placa TEXT,
    data TEXT,
    hora_entrada TEXT,
    hora_saida TEXT,
    status TEXT
    );
""")
conexao.commit()

# ============================================================
# 2. Funções principais (cadastro, consulta, atualização, exclusão)
# ============================================================
def cadastrar():
    nome = entrada_nome.get().strip()
    cpf = entrada_cpf.get().strip()
    placa = entrada_placa.get().strip()
    data = entrada_data.get().strip()
    hora_entrada = entrada_hora_entrada.get().strip()
    hora_saida = entrada_hora_saida.get().strip()
    status = entrada_status.get().strip()

    if nome == "" or cpf == "" or placa == "" or data == "" or hora_entrada == "" or hora_saida == "" or status == "":
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
        return
    if status not in ["pendente", "pago"]:
        messagebox.showerror("Erro", "Status deve ser 'pendente' ou 'pago'.")
        return

    cursor.execute("""
    INSERT INTO titulos (nome, cpf, placa, data, hora_entrada, hora_saida, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, cpf, placa, data, hora_entrada, hora_saida, status))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Vaga cadastrada com sucesso!")

def listar():
    cursor.execute("SELECT * FROM titulos")
    registros = cursor.fetchall()
    texto_lista.delete("1.0", tk.END)
    for r in registros:
        texto_lista.insert(tk.END, f"{r}\n")

def atualizar():
    id_titulo = entrada_id.get().strip()
    novo_status = entrada_status_update.get().strip()

    if id_titulo == "" or not id_titulo.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return
    if novo_status not in ["pendente", "pago"]:
        messagebox.showerror("Erro", "Status deve ser 'pendente' ou 'pago'.")
        return

    cursor.execute("UPDATE titulos SET status = ? WHERE id = ?", (novo_status, id_titulo))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Status atualizado com sucesso!")

def excluir():
    id_titulo = entrada_id.get().strip()

    if id_titulo == "" or not id_titulo.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return

    cursor.execute("DELETE FROM titulos WHERE id = ?", (id_titulo,))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Vaga excluída com sucesso!")

# ============================================================
# 3. Funções de Relatórios
# ============================================================
def relatorio_pendentes():
    cursor.execute("SELECT * FROM titulos WHERE status = 'pendente'")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "------------------ RECEBIMENTOS PENDENTES ------------------\n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"{r}\n")

def relatorio_totais():
    cursor.execute("SELECT status, SUM(valor) FROM titulos GROUP BY status")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "-----------------  TOTAL DE RECEBIMENTOS ------------------ \n")
    texto_relatorio.tag_config("pago", foreground="#27ae60")
    texto_relatorio.tag_config("pendente", foreground="#c0392b")
    for r in registros:
        if r[0] == "pago":
            texto_relatorio.insert(tk.END, f"{r[0]}: R$ {r[1]:.2f}\n", "pago")
        else:
            texto_relatorio.insert(tk.END, f"{r[0]}: R$ {r[1]:.2f}\n", "pendente")

def calcular_pagamento():
    id_cliente = entrada_calculo_id.get().strip()

    if not id_cliente.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return

    cursor.execute("SELECT nome, hora_entrada, hora_saida FROM titulos WHERE id = ?", (id_cliente,))
    registro = cursor.fetchone()

    if not registro:
        messagebox.showerror("Erro", "Cliente não encontrado.")
        return

    nome, entrada, saida = registro

    try:
        hora_entrada = datetime.strptime(entrada, "%H:%M")
        hora_saida = datetime.strptime(saida, "%H:%M")

        diferenca = hora_saida - hora_entrada
        horas = diferenca.total_seconds() / 3600

        VALOR_POR_HORA = 15
        valor_total = horas * VALOR_POR_HORA

        # Atualiza o valor no banco
        cursor.execute("UPDATE titulos SET valor = ? WHERE id = ?", (valor_total, id_cliente))
        conexao.commit()

        resultado_calculo.config(
            text=f"Cliente: {nome}\nTempo: {horas:.2f}h\nValor: R$ {valor_total:.2f}"
        )

    except:
        messagebox.showerror("Erro", "Formato de horário inválido.")
    
    
def relatorio_clientes():
    cursor.execute("SELECT nome, cpf, placa FROM titulos")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "------------------- CLIENTES CADASTRADOS ------------------- \n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"Cliente: {r[0]}, CPF: {r[1]}, Placa: {r[2]}\n")
        
def relatorio_melhores_clientes():
    cursor.execute("""
    SELECT nome, COUNT(*) as total_visitas
    FROM titulos
    GROUP BY nome
    ORDER BY total_visitas DESC
    LIMIT 5
    """)
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "------------------- 5 MELHORES CLIENTES -------------------  \n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"Cliente: {r[0]}, Visitas: {r[1]}\n")
    
# ============================================================
# 4. Construção da janela principal com abas
# ============================================================
janela = tk.Tk()
janela.title("Controle de Vagas")
janela.geometry("700x400")
janela.configure(bg=Estilo.COR_FUNDO_JANELA)

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=Estilo.COR_FUNDO_JANELA, borderwidth=0)
style.configure("TNotebook.Tab", padding=[12, 8], font=Estilo.FONTE_LABEL)

abas = ttk.Notebook(janela)
abas.pack(expand=True, fill="both", padx=10, pady=10)

# Aba Cadastro
aba_cadastro = tk.Frame(abas, bg=Estilo.COR_FUNDO_ABA)
abas.add(aba_cadastro, text="CADASTRO")


tk.Label(aba_cadastro, text="NOME:", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=0, column=0)
entrada_nome = tk.Entry(aba_cadastro, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_nome.grid(row=0, column=1, pady=2)

tk.Label(aba_cadastro, text="CPF:", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=1, column=0)
entrada_cpf = tk.Entry(aba_cadastro, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_cpf.grid(row=1, column=1, pady=2)

tk.Label(aba_cadastro, text="PLACA:", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=2, column=0)
entrada_placa = tk.Entry(aba_cadastro, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_placa.grid(row=2, column=1, pady=2)

tk.Label(aba_cadastro, text="DATA (AAAA-MM-DD):", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=3, column=0)
entrada_data = tk.Entry(aba_cadastro, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_data.grid(row=3, column=1, pady=2)

tk.Label(aba_cadastro, text="HORA ENTRADA (HH:MM):", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=4, column=0)
entrada_hora_entrada = tk.Entry(aba_cadastro, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_hora_entrada.grid(row=4, column=1, pady=2)

tk.Label(aba_cadastro, text="Hora SAÍDA (HH:MM):", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=5, column=0)
entrada_hora_saida = tk.Entry(aba_cadastro, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_hora_saida.grid(row=5, column=1, pady=2)

tk.Label(aba_cadastro, text="STATUS (pendente/pago):", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=7, column=0)
entrada_status = tk.Entry(aba_cadastro, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_status.grid(row=7, column=1, pady=2)

tk.Button(aba_cadastro, text="CADASTRAR", command=cadastrar, **Estilo.BOTAO).grid(row=8, column=0, columnspan=2, pady=10)



aba_calculo = tk.Frame(abas, bg="#d5f2fa")
abas.add(aba_calculo, text="CÁLCULO PAGAMENTO")

tk.Label(aba_calculo, text="ID DO CLIENTE:", bg="#d5f2fa").pack(pady=5)
entrada_calculo_id = tk.Entry(aba_calculo, width=20)
entrada_calculo_id.pack(pady=5)

resultado_calculo = tk.Label(aba_calculo, text="", bg="#d5f2fa", font=("Consolas", 10, "bold"))
resultado_calculo.pack(pady=10)
tk.Button(aba_calculo,text="CALCULAR VALOR",command=calcular_pagamento,**Estilo.BOTAO).pack(pady=10)



# Aba Consulta
aba_consulta = tk.Frame(abas, bg="#d5f2fa")
abas.add(aba_consulta, text="CONSULTAR")

texto_lista = tk.Text(aba_consulta, height=17, width=80, bd=2, relief="flat")
tk.Button(aba_consulta, text="LISTAR CLIENTES", command=listar,  **Estilo.BOTAO).pack()
tk.Label(aba_consulta,text="ID           NOME           CPF           PLACA            DATA             HORA ENTRADA           HORA SAÍDA           STATUS", bg="#d5f2fa").pack()

texto_lista.pack()

# Aba Atualização/Exclusão
aba_update = tk.Frame(abas, bg= Estilo.COR_FUNDO_ABA)
abas.add(aba_update, text="ATUALIZAR/EXCLUIR")

tk.Label(aba_update, text="ID DO CLIENTE:", bg="#ffffff").grid(row=0, column=0)
entrada_id = tk.Entry(aba_update, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_id.grid(row=0, column=1, pady=2)

tk.Label(aba_update, text="NOVO STATUS\n(pendente/pago):", bg="#ffffff").grid(row=1, column=0)
entrada_status_update = tk.Entry(aba_update, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_status_update.grid(row=1, column=1, pady=2)
tk.Label(aba_update, text="", bg="#ffffff").grid(row=4, column=0)
tk.Label(aba_update, text="", bg="#ffffff").grid(row=5, column=0)
tk.Label(aba_update, text="", bg="#ffffff").grid(row=6, column=0)
tk.Label(aba_update, text="", bg="#ffffff").grid(row=7, column=0)
tk.Button(aba_update, text="ATUALIZAR STATUS", command=atualizar, **Estilo.BOTAO).grid(row=8, column=1)
tk.Button(aba_update, text="EXCLUIR CLIENTE", command=excluir, **Estilo.BOTAO_EXCLUIR).grid(row=9, column=1, pady=10)

# Aba Relatórios
aba_relatorios = tk.Frame(abas, bg="#d5f2fa" )
abas.add(aba_relatorios, text="RELATÓRIOS")

frame_botoes = tk.Frame(aba_relatorios)
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="PAGAMENTOS PENDENTES", command=relatorio_pendentes, **Estilo.BOTAO3).pack(side="left", padx=5)
tk.Button(frame_botoes, text="TOTAL PAGOS|PENDENTES", command=relatorio_totais, **Estilo.BOTAO3).pack(side="left", padx=5)
tk.Button(frame_botoes, text="CLIENTES CADASTRADOS", command=relatorio_clientes, **Estilo.BOTAO3).pack(side="left", padx=5)
tk.Button(frame_botoes, text="MELHORES CLIENTES", command=relatorio_melhores_clientes, **Estilo.BOTAO3).pack(side="left", padx=5)
texto_relatorio = tk.Text(aba_relatorios, height=15, width=60)
texto_relatorio.pack(pady=10)

# ============================================================
# 5. Iniciar programa
# ============================================================
janela.mainloop()
conexao.close()
