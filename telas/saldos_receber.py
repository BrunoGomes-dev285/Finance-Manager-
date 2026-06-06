import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from banco import cadastrar_conta_receber, excluir_receber, listar_contas_receber, marcar_recebido
from .pagina_base import PaginaBase


STATUS_IDS = {
    "Pendente": 1,
    "Recebido": 3,
}


def formatar_moeda(valor):
    valor_formatado = f"R$ {float(valor):,.2f}"
    return valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")


def converter_valor(texto):
    texto = texto.replace("R$", "").replace(" ", "").strip()

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    return float(texto)


class TelaSaldosReceber(PaginaBase):
    def __init__(self, pai, cores, usuario=None):
        super().__init__(pai, cores)
        self.usuario = usuario
        self.montar_tela()

    def montar_tela(self):
        id_usuario = self.usuario[0]

        for widget in self.winfo_children():
            widget.destroy()

        self.criar_cabecalho("Saldos a Receber", "Cadastro e acompanhamento dos valores a receber.")

        corpo = tk.Frame(self, bg=self.cores["fundo"])
        corpo.grid(row=1, column=0, sticky="nsew", padx=32, pady=12)
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_rowconfigure(1, weight=1)

        formulario = self.criar_painel(corpo)
        formulario.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        lnome = tk.Label(formulario, text="Nome da Conta", bg=self.cores["cartao"], fg=self.cores["texto_suave"])
        lnome.grid(row=0, column=0, padx=12, pady=(14, 5), sticky="w")
        cnome = tk.Entry(formulario, width=28)
        cnome.grid(row=1, column=0, padx=12, pady=(0, 12))

        lvalor = tk.Label(formulario, text="Valor", bg=self.cores["cartao"], fg=self.cores["texto_suave"])
        lvalor.grid(row=0, column=1, padx=12, pady=(14, 5), sticky="w")
        cvalor = tk.Entry(formulario, width=18)
        cvalor.grid(row=1, column=1, padx=12, pady=(0, 12))

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

        ldata = tk.Label(formulario, text="Data", bg=self.cores["cartao"], fg=self.cores["texto_suave"])
        ldata.grid(row=0, column=2, padx=12, pady=(14, 5), sticky="w")
        cdata = tk.Entry(formulario, width=18)
        cdata.grid(row=1, column=2, padx=12, pady=(0, 12))

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

        lstatus = tk.Label(formulario, text="Status", bg=self.cores["cartao"], fg=self.cores["texto_suave"])
        lstatus.grid(row=0, column=3, padx=12, pady=(14, 5), sticky="w")
        cstatus = ttk.Combobox(formulario, values=list(STATUS_IDS.keys()), width=16, state="readonly")
        cstatus.set("Pendente")
        cstatus.grid(row=1, column=3, padx=12, pady=(0, 12))

        ldescricao = tk.Label(formulario, text="Descricao", bg=self.cores["cartao"], fg=self.cores["texto_suave"])
        ldescricao.grid(row=2, column=0, padx=12, pady=5, sticky="w")
        cdescricao = tk.Entry(formulario, width=88)
        cdescricao.grid(row=3, column=0, columnspan=4, padx=12, pady=(0, 14), sticky="we")

        painel_tabela = self.criar_painel(corpo)
        painel_tabela.grid(row=1, column=0, sticky="nsew", pady=(0, 18))
        painel_tabela.grid_columnconfigure(0, weight=1)
        painel_tabela.grid_rowconfigure(1, weight=1)

        cabecalho_tabela = tk.Frame(painel_tabela, bg=self.cores["cartao"])
        cabecalho_tabela.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 10))
        cabecalho_tabela.grid_columnconfigure(0, weight=1)

        tk.Label(
            cabecalho_tabela,
            text="Lista de saldos",
            bg=self.cores["cartao"],
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w")

        area_tabela = tk.Frame(painel_tabela, bg=self.cores["cartao"])
        area_tabela.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 22))
        area_tabela.grid_columnconfigure(0, weight=1)
        area_tabela.grid_rowconfigure(0, weight=1)

        tabela = ttk.Treeview(
            area_tabela,
            columns=("nome", "valor", "data", "status", "descricao"),
            show="headings",
            selectmode="browse",
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

        barra_rolagem = ttk.Scrollbar(area_tabela, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=barra_rolagem.set)

        tabela.grid(row=0, column=0, sticky="nsew")
        barra_rolagem.grid(row=0, column=1, sticky="ns")

        def carregar_tabela():
            for item in tabela.get_children():
                tabela.delete(item)

            contas = listar_contas_receber()

            for conta in contas:
                tabela.insert(
                    "",
                    tk.END,
                    iid=str(conta[0]),
                    values=(conta[1], formatar_moeda(conta[2]), conta[3], conta[4], conta[5]),
                )

        def obter_id_selecionado():
            selecionado = tabela.selection()

            if not selecionado:
                messagebox.showwarning("Selecione um item", "Selecione um saldo na tabela.")
                return None

            return int(selecionado[0])

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

        botoes = tk.Frame(corpo, bg=self.cores["fundo"])
        botoes.grid(row=2, column=0, pady=10)

        botao_s = tk.Button(botoes, text="Salvar", bg=self.cores["informacao"], fg=self.cores["texto_claro"], command=salvar_saldo)
        botao_s.grid(row=0, column=0, padx=8)

        botao_receber = tk.Button(botoes, text="Marcar como recebido", bg=self.cores["sucesso"], fg=self.cores["texto_claro"], command=receber_saldo)
        botao_receber.grid(row=0, column=1, padx=8)

        botao_excluir = tk.Button(botoes, text="Excluir", bg=self.cores["perigo"], fg=self.cores["texto_claro"], command=excluir_saldo)
        botao_excluir.grid(row=0, column=2, padx=8)

        carregar_tabela()
