import tkinter as tk
from tkinter import messagebox

cadastrar = 0
listar = 0
atualizar = 0
excluir = 0
registros = [ ]

def listar():
    nome = entrada_nome.get()
    cpf = entrada_cpf.get()
    placa = entrada_placa.get()
    data = entrada_data.get()
    hora_entrada = entrada_hora_entrada.get()
    hora_saida = entrada_hora_saida.get()
    status = entrada_status.get()
    texto_lista.delete("1.0", tk.END)
    registros.append(nome + "-" + cpf + "-" + placa + "-" + data + "-" + hora_entrada + "-" + hora_saida + "-" + "-" + status)
    
    for r in registros:
        texto_lista.insert(tk.END, f"{r}\n")

janela = tk.Tk()
janela.title("Controle de Vagas")

tk.Label(janela, text="NOME:").grid(row=0, column=0)
entrada_nome = tk.Entry(janela)
entrada_nome.grid(row=0, column=1)

tk.Label(janela, text="CPF:").grid(row=1, column=0)
entrada_cpf = tk.Entry(janela)
entrada_cpf.grid(row=1, column=1)

tk.Label(janela, text="PLACA:").grid(row=2, column=0)
entrada_placa = tk.Entry(janela)
entrada_placa.grid(row=2, column=1)

tk.Label(janela, text="Data (AAAA-MM-DD):").grid(row=3, column=0)
entrada_data = tk.Entry(janela)
entrada_data.grid(row=3, column=1)

tk.Label(janela, text="HORA DE ENTRADA:").grid(row=4, column=0)
entrada_hora_entrada = tk.Entry(janela)
entrada_hora_entrada.grid(row=4, column=1)

tk.Label(janela, text="HORA DE SAÍDA:").grid(row=5, column=0)
entrada_hora_saida = tk.Entry(janela)
entrada_hora_saida.grid(row=5, column=1)

tk.Label(janela, text="STATUS:").grid(row=7, column=0)
entrada_status = tk.Entry(janela)
entrada_status.grid(row=7, column=1)

tk.Label(janela, text="ID (para atualizar/excluir):").grid(row=8, column=0)
entrada_id = tk.Entry(janela)
entrada_id.grid(row=8, column=1)



tk.Button(janela, text="Cadastrar", command=cadastrar).grid(row=8, column=0)
tk.Button(janela, text="Listar", command=listar).grid(row=8, column=1)
tk.Button(janela, text="Atualizar Status", command=atualizar).grid(row=10, column=0)
tk.Button(janela, text="Excluir", command=excluir).grid(row=10, column=1)


texto_lista = tk.Text(janela, height=10, width=50)
texto_lista.grid(row=9, column=0, columnspan=2)

janela.mainloop()