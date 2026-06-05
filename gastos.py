import tkinter as tk
from datetime import date
from tkinter import ttk

from banco import cadastrar_gasto, excluir_gasto, listar_gastos, marcar_gasto_pago


STATUS_IDS = {
    "Pendente": 1,
    "Pago": 2,
}


def formatar_moeda(valor):
    valor_formatado = f"R$ {float(valor):,.2f}"
    return valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")


def converter_valor(texto):
    texto = texto.replace("R$", "").replace(" ", "").strip()

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    return float(texto)


def tela_gastos(conteudo, usuario):
    id_usuario = usuario[0]

    for widget in conteudo.winfo_children():
        widget.destroy()
    #Criando o titulo da janela
    titulo = tk.Label(conteudo, text="Planilha de Gastos", font=("Arial", 28), bg="gray", fg="white")
    titulo.pack(pady=20)

    mensagem = tk.Label(conteudo, text="", font=("Arial", 12), bg="gray", fg="white")
    mensagem.pack()

    def mostrar_mensagem(texto, cor="white"):
        mensagem.config(text=texto, fg=cor)
    #Criando o formulario (caixa invisivel para a organizacao da tabela)
    formulario = tk.Frame(conteudo, bg="gray")
    formulario.pack(pady=10)
    #Criando os nomes e vampos para serem inseridos 
    lnome = tk.Label(formulario, text="Nome da Conta", bg="gray", fg="white")
    lnome.grid(row=0, column=0, padx=8, pady=5, sticky="w")
    cnome = tk.Entry(formulario, width=28)
    cnome.grid(row=1, column=0, padx=8, pady=5)

    lvalor = tk.Label(formulario, text="Valor", bg="gray", fg="white")
    lvalor.grid(row=0, column=1, padx=8, pady=5, sticky="w")
    cvalor = tk.Entry(formulario, width=18)
    cvalor.grid(row=1, column=1, padx=8, pady=5)

    #Metodo para ajustar a formatacao dos valores digitados
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

    ldata = tk.Label(formulario, text="Vencimento", bg="gray", fg="white")
    ldata.grid(row=0, column=2, padx=8, pady=5, sticky="w")
    cdata = tk.Entry(formulario, width=18)
    cdata.grid(row=1, column=2, padx=8, pady=5)

    #Formatacao da data dd/mm/aa
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

    #Status do gasto 
    lstatus = tk.Label(formulario, text="Status", bg="gray", fg="white")
    lstatus.grid(row=0, column=3, padx=8, pady=5, sticky="w")
    cstatus = ttk.Combobox(formulario, values=list(STATUS_IDS.keys()), width=16, state="readonly")
    cstatus.set("Pendente")
    cstatus.grid(row=1, column=3, padx=8, pady=5)

    lpagamento = tk.Label(formulario, text="Forma de Pagamento", bg="gray", fg="white")
    lpagamento.grid(row=2, column=0, padx=8, pady=5, sticky="w")
    cpagamento = tk.Entry(formulario, width=28)
    cpagamento.grid(row=3, column=0, padx=8, pady=5)

    ldescricao = tk.Label(formulario, text="Descricao", bg="gray", fg="white")
    ldescricao.grid(row=2, column=1, padx=8, pady=5, sticky="w")
    cdescricao = tk.Entry(formulario, width=58)
    cdescricao.grid(row=3, column=1, columnspan=3, padx=8, pady=5, sticky="we")

    #Criacao da tabela
    tabela = ttk.Treeview(
        conteudo,
        columns=("nome", "valor", "vencimento", "status", "pagamento", "descricao"),
        show="headings",
        height=8,
    )

    tabela.heading("nome", text="Nome")
    tabela.heading("valor", text="Valor")
    tabela.heading("vencimento", text="Vencimento")
    tabela.heading("status", text="Status")
    tabela.heading("pagamento", text="Pagamento")
    tabela.heading("descricao", text="Descricao")

    tabela.column("nome", width=170)
    tabela.column("valor", width=110)
    tabela.column("vencimento", width=120)
    tabela.column("status", width=100)
    tabela.column("pagamento", width=140)
    tabela.column("descricao", width=250)

    tabela.pack(pady=20, padx=40, fill="x")

    #Metodo para carregar a tabela
    def carregar_tabela():
        for item in tabela.get_children():
            tabela.delete(item)

        gastos = listar_gastos()

        for gasto in gastos:
            tabela.insert(
                "",
                tk.END,
                iid=str(gasto[0]),
                values=(
                    gasto[1],
                    formatar_moeda(gasto[2]),
                    gasto[3],
                    gasto[4],
                    gasto[5],
                    gasto[6],
                ),
            )

    def obter_id_selecionado():
        selecionado = tabela.selection()

        if not selecionado:
            mostrar_mensagem("Selecione um gasto na tabela.", "yellow")
            return None

        return int(selecionado[0])

    #Metodo para saalvar as indormacoes no banco
    def salvar_gasto():
        nome_conta = cnome.get().strip()
        valor = cvalor.get().strip()
        data_vencimento = cdata.get().strip()
        descricao = cdescricao.get().strip()
        forma_pagamento = cpagamento.get().strip()
        status = cstatus.get()

        if not nome_conta or not valor or not data_vencimento:
            mostrar_mensagem("Preencha nome, valor e vencimento.", "yellow")
            return

        try:
            valor = converter_valor(valor)
            id_status = STATUS_IDS[status]
            cadastrar_gasto(
                id_usuario,
                nome_conta,
                valor,
                data_vencimento,
                descricao,
                forma_pagamento,
                id_status,
            )

            cnome.delete(0, tk.END)
            cvalor.delete(0, tk.END)
            cdata.delete(0, tk.END)
            cdescricao.delete(0, tk.END)
            cpagamento.delete(0, tk.END)
            cstatus.set("Pendente")

            carregar_tabela()
            mostrar_mensagem("Gasto salvo.", "lightgreen")
        except ValueError:
            mostrar_mensagem("Digite um valor valido.", "yellow")
        except Exception as erro:
            mostrar_mensagem(f"Erro ao salvar: {erro}", "red")

    #Metodo para excluir itens da tabela
    def excluir_item():
        id_gasto = obter_id_selecionado()

        if id_gasto is None:
            return

        excluir_gasto(id_gasto)
        carregar_tabela()
        mostrar_mensagem("Gasto excluido.", "lightgreen")
    #Marcando o gasto como pago
    def pagar_gasto():
        id_gasto = obter_id_selecionado()

        if id_gasto is None:
            return

        data_pagamento = date.today().strftime("%d/%m/%Y")
        marcar_gasto_pago(id_gasto, data_pagamento)
        carregar_tabela()
        mostrar_mensagem("Gasto marcado como pago.", "lightgreen")

    #Criando um botao para salvar os gastos
    botoes = tk.Frame(conteudo, bg="gray")
    botoes.pack(pady=10)

    botao_salvar = tk.Button(botoes, text="Salvar", command=salvar_gasto)
    botao_salvar.grid(row=0, column=0, padx=8)

    botao_pagar = tk.Button(botoes, text="Marcar como pago", command=pagar_gasto)
    botao_pagar.grid(row=0, column=1, padx=8)

    botao_excluir = tk.Button(botoes, text="Excluir", command=excluir_item)
    botao_excluir.grid(row=0, column=2, padx=8)

    carregar_tabela()
