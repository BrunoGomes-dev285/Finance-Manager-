import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
#Importando as credecinais do banco
from banco import (
    cadastrar_conta_receber,
    excluir_receber,
    listar_contas_receber,
    marcar_recebido,
)


STATUS_IDS = {
    "Pendente": 1,
    "Recebido": 3,
}

#Metodo para formatar o avlor que iara aparecer na  tabela para reais
def formatar_moeda(valor):
    valor_formatado = f"R$ {float(valor):,.2f}"
    return valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")

#Metodo para ajustar o valor para ficar na  formatacao certa
def converter_valor(texto):
    texto = texto.replace("R$", "").replace(" ", "").strip()

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    return float(texto)


# Metodo para criar a funcao que ira exibir a tela no frame
def tela_saldo(conteudo, usuario):
    id_usuario = usuario[0]

    for widget in conteudo.winfo_children():
        widget.destroy()

    # Criando um titulo para a tela de saldos
    titulo = tk.Label(conteudo, text="Saldos a Receber", font=("Arial", 28), bg="gray", fg="white")
    titulo.pack(pady=20)

    # Frame para organizar os campos do formulario
    formulario = tk.Frame(conteudo, bg="gray")
    formulario.pack(pady=10)

    # Criando o campo de inserir o nome
    lnome = tk.Label(formulario, text="Nome da Conta", bg="gray", fg="white")
    lnome.grid(row=0, column=0, padx=8, pady=5, sticky="w")
    cnome = tk.Entry(formulario, width=28)
    cnome.grid(row=1, column=0, padx=8, pady=5)

    # Criando o campo do valor
    lvalor = tk.Label(formulario, text="Valor", bg="gray", fg="white")
    lvalor.grid(row=0, column=1, padx=8, pady=5, sticky="w")
    cvalor = tk.Entry(formulario, width=18)
    cvalor.grid(row=1, column=1, padx=8, pady=5)

    def formatar_valor_digitado(event=None):
        valor_digitado = cvalor.get().strip()

        if not valor_digitado:
            return

        try:
            valor = converter_valor(valor_digitado)
            cvalor.delete(0, tk.END)
            cvalor.insert(0, formatar_moeda(valor))
        except ValueError:
            pass

    cvalor.bind("<FocusOut>", formatar_valor_digitado)

    # Criando o campo da data
    ldata = tk.Label(formulario, text="Data", bg="gray", fg="white")
    ldata.grid(row=0, column=2, padx=8, pady=5, sticky="w")
    cdata = tk.Entry(formulario, width=18)
    cdata.grid(row=1, column=2, padx=8, pady=5)

    # Formata a data automaticamente no modelo dd/mm/aaaa
    def formatar_data(event=None):
        texto = cdata.get()
        numeros = "".join(caractere for caractere in texto if caractere.isdigit())
        numeros = numeros[:8]

        if len(numeros) >= 5:
            formatado = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"
        elif len(numeros) >= 3:
            formatado = f"{numeros[:2]}/{numeros[2:]}"
        else:
            formatado = numeros

        cdata.delete(0, tk.END)
        cdata.insert(0, formatado)

    cdata.bind("<KeyRelease>", formatar_data)

    # Criando o campo de status
    lstatus = tk.Label(formulario, text="Status", bg="gray", fg="white")
    lstatus.grid(row=0, column=3, padx=8, pady=5, sticky="w")
    cstatus = ttk.Combobox(formulario, values=list(STATUS_IDS.keys()), width=16, state="readonly")
    cstatus.set("Pendente")
    cstatus.grid(row=1, column=3, padx=8, pady=5)

    # Criando o campo de descricao
    ldescricao = tk.Label(formulario, text="Descricao", bg="gray", fg="white")
    ldescricao.grid(row=2, column=0, padx=8, pady=5, sticky="w")
    cdescricao = tk.Entry(formulario, width=88)
    cdescricao.grid(row=3, column=0, columnspan=4, padx=8, pady=5, sticky="we")

    # Criando a tabela de saldos cadastrados
    tabela = ttk.Treeview(
        conteudo,
        columns=("nome", "valor", "data", "status", "descricao"),
        show="headings",
        height=8,
    )

    tabela.heading("nome", text="Nome")
    tabela.heading("valor", text="Valor")
    tabela.heading("data", text="Data")
    tabela.heading("status", text="Status")
    tabela.heading("descricao", text="Descricao")

    tabela.column("nome", width=180)
    tabela.column("valor", width=110)
    tabela.column("data", width=120)
    tabela.column("status", width=100)
    tabela.column("descricao", width=280)

    tabela.pack(pady=20, padx=40, fill="x")

    # Carrega os dados do banco dentro da tabela
    def carregar_tabela():
        for item in tabela.get_children():
            tabela.delete(item)

        contas = listar_contas_receber()

        for conta in contas:
            tabela.insert(
                "",
                tk.END,
                iid=str(conta[0]),
                values=(
                    conta[1],
                    formatar_moeda(conta[2]),
                    conta[3],
                    conta[4],
                    conta[5],
                ),
            )

    def obter_id_selecionado():
        selecionado = tabela.selection()

        if not selecionado:
            messagebox.showwarning("Selecione um item", "Selecione um saldo na tabela.")
            return None

        return int(selecionado[0])

    # Funcao para salvar os saldos a receber no banco
    def salvar_saldo():
        nome_conta = cnome.get().strip()
        valor = cvalor.get().strip()
        data_recebimento = cdata.get().strip()
        descricao = cdescricao.get().strip()
        status = cstatus.get()

        if not nome_conta or not valor or not data_recebimento:
            messagebox.showwarning("Campos obrigatorios", "Preencha nome, valor e data.")
            return

        try:
            valor = converter_valor(valor)
            id_status = STATUS_IDS[status]
            cadastrar_conta_receber(id_usuario, nome_conta, valor, data_recebimento, descricao, id_status)

            cnome.delete(0, tk.END)
            cvalor.delete(0, tk.END)
            cdata.delete(0, tk.END)
            cdescricao.delete(0, tk.END)
            cstatus.set("Pendente")

            carregar_tabela()
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor valido.")
        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao salvar: {erro}")

    def excluir_saldo():
        id_conta = obter_id_selecionado()

        if id_conta is None:
            return

        confirmar = messagebox.askyesno("Confirmar exclusao", "Deseja excluir o saldo selecionado?")

        if confirmar:
            excluir_receber(id_conta)
            carregar_tabela()

    def receber_saldo():
        id_conta = obter_id_selecionado()

        if id_conta is None:
            return

        data_recebido_em = date.today().strftime("%d/%m/%Y")
        marcar_recebido(id_conta, data_recebido_em)
        carregar_tabela()

    # Botoes de acao
    botoes = tk.Frame(conteudo, bg="gray")
    botoes.pack(pady=10)

    botao_s = tk.Button(botoes, text="Salvar", command=salvar_saldo)
    botao_s.grid(row=0, column=0, padx=8)

    botao_receber = tk.Button(botoes, text="Marcar como recebido", command=receber_saldo)
    botao_receber.grid(row=0, column=1, padx=8)

    botao_excluir = tk.Button(botoes, text="Excluir", command=excluir_saldo)
    botao_excluir.grid(row=0, column=2, padx=8)

    carregar_tabela()
