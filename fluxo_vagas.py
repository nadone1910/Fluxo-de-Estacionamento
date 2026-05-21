import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from stilo import Estilo
from datetime import datetime
from PIL import Image, ImageTk
from fpdf import FPDF

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
    valor TEXT,
    status TEXT
    );
""")
conexao.commit()


def cadastrar():
    nome = entrada_nome.get().strip()
    cpf = entrada_cpf.get().strip()
    placa = entrada_placa.get().strip()
    data = datetime.now().strftime("%Y-%m-%d")
    hora_entrada = datetime.now().strftime("%H:%M")
    hora_saida = ""
    status = "pendente"
    if nome == "" or cpf == "" or placa == "":
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
        return
    cursor.execute("""
    INSERT INTO titulos (nome, cpf, placa, data, hora_entrada, hora_saida, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, cpf, placa, data, hora_entrada, hora_saida, status))

    conexao.commit()
    messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")


def listar():
    cursor.execute("SELECT * FROM titulos")
    registros = cursor.fetchall()
    texto_lista.delete("1.0", tk.END)
    for r in registros:
        texto_lista.insert(tk.END,
        f"ID:{r[0]} | Nome:{r[1]} | Placa:{r[3]} | Entrada:{r[5]} | Saída:{r[6]} | Status:{r[8]} | Valor:R${r[7]}\n")


def atualizar():
    entrada_placa_titulo = entrada_placa_update.get().strip()
    novo_status = entrada_status_update.get().strip()
    if entrada_placa_titulo == "":
        messagebox.showerror("Erro", "Informe a placa do cliente.")
        return
    if novo_status not in ["pendente", "pago"]:
        messagebox.showerror("Erro", "Status deve ser 'pendente' ou 'pago'.")
        return
    cursor.execute("UPDATE titulos SET status = ? WHERE placa = ?", (novo_status, entrada_placa_titulo))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Status atualizado com sucesso!")
    

def excluir():
    placa_titulo = entrada_placa_update.get().strip()
    if placa_titulo == "":
        messagebox.showerror("Erro", "Informe a placa do cliente.")
        return
    cursor.execute("DELETE FROM titulos WHERE placa = ?", (placa_titulo,))
    conexao.commit()
    messagebox.showinfo("Sucesso", "Vaga excluída com sucesso!")


def verificar_login():
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    
    if usuario == "adm" and senha == "1234":
        messagebox.showinfo("Login", "Login realizado com sucesso!")
        janela.deiconify()   # mostra janela principal
        janela2.withdraw()   # esconde login
    else:
        messagebox.showerror("Login", "Usuário ou senha incorretos.")


def gerar_pdf():
    texto = texto_lista.get("1.0", tk.END).strip() #pega texto do widget para gerar PDF
    if not texto:
        messagebox.showwarning("Aviso", "Digite algum texto antes de gerar o PDF.")
        return
    # Escolher local para salvar
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Arquivos PDF", "*.pdf")],
        title="Salvar PDF"
    )
    if not caminho_arquivo:
        return  # Usuário cancelou
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, texto)
        pdf.output(caminho_arquivo)
        messagebox.showinfo("Sucesso", f"PDF salvo em:\n{caminho_arquivo}")
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível gerar o PDF:\n{e}")


# ============================================================
# Funções de Relatórios
# ============================================================
def relatorio_pendentes():
    cursor.execute("SELECT * FROM titulos WHERE status = 'pendente'")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "----------------------------------- RECEBIMENTOS PENDENTES ----------------------------------  \n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"{r}\n")


def relatorio_totais():
    cursor.execute("SELECT status, SUM(valor) FROM titulos GROUP BY status")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "----------------------------------- TOTAL DE RECEBIMENTOS -----------------------------------  \n")
    texto_relatorio.tag_config("pago", foreground="#27ae60")
    texto_relatorio.tag_config("pendente", foreground="#c0392b")
    for r in registros:
        if r[0] == "pago":
            texto_relatorio.insert(tk.END, f"{r[0]}: R$ {r[1]:.2f}\n", "pago")
        else:
            texto_relatorio.insert(tk.END, f"{r[0]}: R$ {r[1]:.2f}\n", "pendente")


def registrar_saida():
    id_cliente = entrada_id_pagamento.get().strip() # pega ID digitado
    if not id_cliente.isdigit():  #valida ID numérico
        messagebox.showerror("Erro", "Informe um ID válido.")
        return
    cursor.execute("SELECT hora_entrada FROM titulos WHERE id = ?", (id_cliente,))#busca hora de entrada no banco
    registro = cursor.fetchone()
    if not registro:  #verifica se cliente existe
        messagebox.showerror("Erro", "Cliente não encontrado.")
        return
    hora_entrada = registro[0]
    hora_saida = datetime.now().strftime("%H:%M")#define hora de saída automática
    hora_entrada_dt = datetime.strptime(hora_entrada, "%H:%M") #converte string para datetime para calcular diferença, formato "%H:%M" para horas e minutos
    hora_saida_dt = datetime.strptime(hora_saida, "%H:%M")
    
    diferenca = hora_saida_dt - hora_entrada_dt
    horas = diferenca.total_seconds() / 3600
    if horas < 1:
        horas = 1
    valor_por_hora = 15
    valor_total = horas * valor_por_hora
    # atualiza banco com hora_saida, valor e status pago
    cursor.execute("""
    UPDATE titulos
    SET hora_saida = ?, valor = ?, status = ?
    WHERE id = ?
    """, (hora_saida, valor_total, "pago", id_cliente))
    conexao.commit()
    messagebox.showinfo("Pagamento Concluído",
                        f"Tempo: {horas:.2f}h\nValor: R$ {valor_total:.2f}")


def relatorio_clientes():
    cursor.execute("SELECT nome, cpf, placa FROM titulos")
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "----------------------------------- CLIENTES CADASTRADOS ------------------------------------  \n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"Cliente: {r[0]}, CPF: {r[1]}, Placa: {r[2]}\n")


def relatorio_melhores_clientes():
    cursor.execute("""
    SELECT nome, cpf, COUNT(*) as total_visitas
    FROM titulos
    GROUP BY nome, cpf
    ORDER BY total_visitas DESC
    LIMIT 5
    """)
    registros = cursor.fetchall()
    texto_relatorio.delete("1.0", tk.END)
    texto_relatorio.insert(tk.END, "----------------------------------- 5 MELHORES CLIENTES -------------------------------------   \n")
    for r in registros:
        texto_relatorio.insert(tk.END, f"Cliente: {r[0]}, CPF: {r[1]}, VISITAS: {r[2]}\n")


def gerar_recibo():
    id_cliente = entrada_id_pagamento.get().strip() #pega ID digitado para gerar recibo
    if not id_cliente.isdigit():
        messagebox.showerror("Erro", "Informe um ID válido.")
        return
    cursor.execute("""
    SELECT nome, placa, data, hora_entrada, hora_saida, valor
    FROM titulos WHERE id = ?
    """, (id_cliente,)) #busca dados do cliente para gerar recibo
    registro = cursor.fetchone()
    if not registro:
        messagebox.showerror("Erro", "Cliente não encontrado.")
        return
    nome, placa, data, entrada, saida, valor = registro #atribui dados a variáveis para exibir no recibo
    recibo = tk.Toplevel()
    recibo.title("RECIBO DE PAGAMENTO")
    recibo.geometry("400x450")
    recibo.configure(bg="white")

    # Centraliza janela
    recibo.update_idletasks() # Atualiza para pegar dimensões corretas
    largura = 400
    altura = 450
    x = (recibo.winfo_screenwidth() // 2) - (largura // 2) # Centraliza horizontalmente
    y = (recibo.winfo_screenheight() // 2) - (altura // 2) # Centraliza verticalmente
    recibo.geometry(f"{largura}x{altura}+{x}+{y}")

    tk.Label(recibo, text="ESTACIONE& CO", font=("Consolas", 14, "bold"), bg="white").pack(pady=10)
    tk.Label(recibo, text="----------------------------------------", bg="white").pack()
    info_frame = tk.Frame(recibo, bg="white")
    info_frame.pack(pady=20)
    
    tk.Label(info_frame, text=f"Cliente:", bg="white", anchor="w", width=15).grid(row=0, column=0, sticky="w")
    tk.Label(info_frame, text=nome, bg="white").grid(row=0, column=1, sticky="w")

    tk.Label(info_frame, text=f"Placa:", bg="white", anchor="w", width=15).grid(row=1, column=0, sticky="w")
    tk.Label(info_frame, text=placa, bg="white").grid(row=1, column=1, sticky="w")

    tk.Label(info_frame, text=f"Data:", bg="white", anchor="w", width=15).grid(row=2, column=0, sticky="w")
    tk.Label(info_frame, text=data, bg="white").grid(row=2, column=1, sticky="w")

    tk.Label(info_frame, text=f"Entrada:", bg="white", anchor="w", width=15).grid(row=3, column=0, sticky="w")
    tk.Label(info_frame, text=entrada, bg="white").grid(row=3, column=1, sticky="w")

    tk.Label(info_frame, text=f"Saída:", bg="white", anchor="w", width=15).grid(row=4, column=0, sticky="w")
    tk.Label(info_frame, text=saida, bg="white").grid(row=4, column=1, sticky="w")

    tk.Label(recibo, text="----------------------------------------", bg="white").pack(pady=10)
    tk.Label(recibo, text=f"VALOR PAGO: R$ {valor:.2f}", font=("Consolas", 12, "bold"), fg="green", bg="white").pack(pady=10)
    tk.Label(recibo, text=f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", bg="white", font=("Consolas", 9)).pack(pady=10)
    tk.Button(recibo, text="FECHAR", command=recibo.destroy, width=20).pack(pady=20) # Botão para fechar recibo


# ============================================================
# FRONTEND
# ============================================================

# Criando janela principal de login
janela2 = tk.Tk()
janela2.title("LOGIN v1.0")
janela2.geometry("400x300")
janela2.configure(bg="white")

# Labels e entradas
label_usuario = tk.Label(janela2, text="USUÁRIO", bg="white", fg=Estilo.COR_FONTE)
label_usuario.pack(anchor="w", pady=(50,0), padx=17)
entry_usuario = tk.Entry(janela2, width=59, bg="#d5f2fa", bd=2, relief="flat")
entry_usuario.pack(pady=5)

label_senha = tk.Label(janela2, text="SENHA", bg="white", fg=Estilo.COR_FONTE)
label_senha.pack(anchor="w", pady=(10,0), padx=17)
entry_senha = tk.Entry(janela2, show="*", width=59, bg="#d5f2fa", bd=2, relief="flat")
entry_senha.pack(pady=(0, 10))

# Botão de login
botao_login = tk.Button(janela2, text="LOGIN", command=verificar_login,  **Estilo.BOTAO)
botao_login.pack(pady=(30, 0))


# ============================================================
#  Construção da janela principal com abas
# ============================================================
janela = tk.Toplevel(janela2)
janela.title("Controle de Vagas")
janela.geometry("800x500")
janela.configure(bg=Estilo.COR_FUNDO_JANELA)

janela.withdraw()# deixa a janela principal escondida até fazer login

imagem_logo = Image.open("22.png")# Redimensiona (opcional)
imagem_logo = imagem_logo.resize((800, 100))
logo = ImageTk.PhotoImage(imagem_logo) # Cria objeto PhotoImage para usar no Tkinter

label_logo = tk.Label(janela, image=logo, bg=Estilo.COR_FUNDO_JANELA)
label_logo.image = logo
label_logo.pack(pady=0)

style = ttk.Style()
style.theme_use("clam") # tema mais moderno e personalizável
style.configure("TNotebook", background=Estilo.COR_FUNDO_JANELA, borderwidth=0)
style.configure("TNotebook.Tab", padding=[12, 8], font=Estilo.FONTE_LABEL)

abas = ttk.Notebook(janela) 
abas.pack(expand=True, fill="both", padx=10, pady=10)

style.configure("TNotebook.Tab",
    background="#00607b",   # cor das abas
    foreground="white",
    padding=(15, 8),
    font=("Consolas", 10, "bold")
)
style.map("TNotebook.Tab",
    background=[("selected", "#ffffff")],
    foreground=[("selected",  "#003f50")]
)


# Aba Cadastro
aba_cadastro = tk.Frame(abas, bg=Estilo.COR_FUNDO_ABA)
abas.add(aba_cadastro, text="CADASTRO")
aba_cadastro.grid_columnconfigure(0, weight=1) #coluna 0 é espaçamento, coluna 1 é conteúdo, coluna 2 é espaçamento, weight=1 para centralizar conteúdo
aba_cadastro.grid_columnconfigure(1, weight=1)
aba_cadastro.grid_columnconfigure(2, weight=1)

tk.Label(aba_cadastro, text="NOME", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=0, column=1, pady=(40,0), sticky="w", padx=17) #sticky alinha à esquerda, padx para afastar da borda
entrada_nome = tk.Entry(aba_cadastro, width=110, bg="#d5f2fa", bd=2, relief="flat")
entrada_nome.grid(row=1, column=1, pady=0)

tk.Label(aba_cadastro, text="CPF", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=2, column=1, pady=(15,0), sticky="w", padx=17)
entrada_cpf = tk.Entry(aba_cadastro, width=110, bg="#d5f2fa", bd=2, relief="flat")
entrada_cpf.grid(row=3, column=1, pady=0)

tk.Label(aba_cadastro, text="PLACA", bg=Estilo.COR_FUNDO_FONTE, fg=Estilo.COR_FONTE).grid(row=4, column=1, pady=(15,0), sticky="w", padx=17)
entrada_placa = tk.Entry(aba_cadastro, width=110, bg="#d5f2fa", bd=2, relief="flat")
entrada_placa.grid(row=5, column=1, pady=0)

tk.Button(aba_cadastro, text="REGISTRAR ENTRADA", command=cadastrar, **Estilo.BOTAO4).grid(row=6, column=1, pady=(100, 0))


# Aba Consulta
aba_consulta = tk.Frame(abas, bg="#ffffff")
abas.add(aba_consulta, text="CONSULTAR")

aba_consulta.grid_columnconfigure(0, weight=1)
aba_consulta.grid_columnconfigure(1, weight=1)
aba_consulta.grid_columnconfigure(2, weight=1)

texto_lista = tk.Text(aba_consulta, height=26, width=93, bd=2, relief="flat", bg="#d5f2fa")
tk.Button(aba_consulta, text="LISTAR CLIENTES", command=listar,  **Estilo.BOTAO4).pack(pady=(5, 0))
tk.Button(aba_consulta, text="GERAR PDF", command=gerar_pdf, **Estilo.BOTAO5).pack(pady=(5, 5))# Botão para gerar PDF


#Aba Pagamento
aba_pagamento = tk.Frame(abas, bg= Estilo.COR_FUNDO_ABA)
abas.add(aba_pagamento, text="CÁLCULO PAGAMENTO")
aba_pagamento.grid_columnconfigure(0, weight=1)
aba_pagamento.grid_columnconfigure(1, weight=1)
aba_pagamento.grid_columnconfigure(2, weight=1)

tk.Label(aba_pagamento, text="ID DO CLIENTE", bg="#ffffff").grid(row=0, column=1, pady=(40,0), sticky="w", padx=17)
entrada_id_pagamento = tk.Entry(aba_pagamento, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_id_pagamento.grid(row=1, column=1, pady=0)

tk.Button(aba_pagamento, text="REGISTRAR SAÍDA", command=registrar_saida, **Estilo.BOTAO4).grid(row=2, column=1, pady=(180,0))

tk.Button(aba_pagamento, text="GERAR RECIBO", command=gerar_recibo, **Estilo.BOTAO5).grid(row=3, column=1, pady=(10,0))
texto_lista.pack()


# Aba Atualização/Exclusão
aba_update = tk.Frame(abas, bg= Estilo.COR_FUNDO_ABA)
abas.add(aba_update, text="ATUALIZAR/EXCLUIR")
aba_update.grid_columnconfigure(0, weight=1)
aba_update.grid_columnconfigure(1, weight=1)
aba_update.grid_columnconfigure(2, weight=1)

tk.Label(aba_update, text="PLACA DO CLIENTE", bg="#ffffff").grid(row=0, column=1, pady=(40,0), sticky="w", padx=17)
entrada_placa_update = tk.Entry(aba_update, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_placa_update.grid(row=1, column=1, pady=0)

tk.Label(aba_update, text="NOVO STATUS", bg="#ffffff").grid(row=3, column=1, pady=(15,0), sticky="w", padx=17)
entrada_status_update = tk.Entry(aba_update, width=Estilo.LARGURA_ENTRY, bg="#d5f2fa", bd=2, relief="flat")
entrada_status_update.grid(row=4, column=1, pady=0)

tk.Button(aba_update, text="ATUALIZAR STATUS", command=atualizar, **Estilo.BOTAO4).grid(row=5, column=1, pady=(120, 0))
tk.Button(aba_update, text="EXCLUIR CLIENTE", command=excluir, **Estilo.BOTAO_EXCLUIR).grid(row=6, column=1, pady=(10, 0))


# Aba Relatórios
aba_relatorios = tk.Frame(abas, bg="#ffffff" )
abas.add(aba_relatorios, text="RELATÓRIOS")

frame_botoes = tk.Frame(aba_relatorios)
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="PAGAMENTOS PENDENTES", command=relatorio_pendentes, **Estilo.BOTAO5).pack(side="left", padx=5)
tk.Button(frame_botoes, text="TOTAL PAGOS|PENDENTES", command=relatorio_totais, **Estilo.BOTAO5).pack(side="left", padx=5)
tk.Button(frame_botoes, text="CLIENTES CADASTRADOS", command=relatorio_clientes, **Estilo.BOTAO5).pack(side="left", padx=5)
tk.Button(frame_botoes, text="MELHORES CLIENTES", command=relatorio_melhores_clientes, **Estilo.BOTAO5).pack(side="left", padx=5)
texto_relatorio = tk.Text(aba_relatorios, height=26, width=93, bd=2, relief="flat", bg="#d5f2fa")
texto_relatorio.pack(pady=10)


janela.mainloop()
conexao.close()
