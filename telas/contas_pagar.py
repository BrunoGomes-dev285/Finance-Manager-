import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from banco import (
    atualizar_conta_pagar,
    cadastrar_conta_pagar,
    listar_categorias,
    listar_contas_pagar,
    listar_status_conta,
    obter_conta_pagar,
)
from .pagina_base import PaginaBase


class TelaContasPagar(PaginaBase):
    def __init__(self, pai, cores, usuario=None, ao_alterar_dados=None):
        super().__init__(pai, cores)
        self.usuario = usuario
        self.ao_alterar_dados = ao_alterar_dados
        self.variavel_busca = tk.StringVar()
        self.filtro_status = "Todas"
        self.botoes_filtro = {}
        self.rotulo_total = None
        self.tabela = None
        self.botao_editar = None
        self.contas_por_id = {}
        self.montar_tela()
        self.atualizar()

    def montar_tela(self):
        self.criar_cabecalho(
            "Contas a pagar",
            "Cadastro e acompanhamento das obrigações pendentes no SQLite.",
        )

        corpo = tk.Frame(self, bg=self.cores["fundo"])
        corpo.grid(row=1, column=0, sticky="nsew", padx=32, pady=12)
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_rowconfigure(2, weight=1)

        barra_superior = self.criar_painel(corpo)
        barra_superior.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        barra_superior.grid_columnconfigure(0, weight=1)

        campo_busca = tk.Entry(
            barra_superior,
            bd=0,
            relief="flat",
            textvariable=self.variavel_busca,
            fg=self.cores["texto_escuro"],
            bg="#eef2f7",
            font=("Segoe UI", 11),
            insertbackground=self.cores["texto_escuro"],
        )
        campo_busca.grid(row=0, column=0, sticky="ew", padx=18, pady=18, ipady=10)
        campo_busca.bind("<KeyRelease>", lambda evento: self.atualizar())

        botao_nova_conta = tk.Button(
            barra_superior,
            text="+ Nova conta",
            bd=0,
            cursor="hand2",
            bg=self.cores["informacao"],
            fg=self.cores["texto_claro"],
            activebackground="#1d4ed8",
            activeforeground=self.cores["texto_claro"],
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10,
            command=self.abrir_dialogo_nova_conta,
        )
        botao_nova_conta.grid(row=0, column=1, padx=(0, 8), pady=18)

        self.botao_editar = tk.Button(
            barra_superior,
            text="Editar",
            bd=0,
            cursor="hand2",
            bg="#e2e8f0",
            fg=self.cores["texto_escuro"],
            activebackground="#cbd5e1",
            activeforeground=self.cores["texto_escuro"],
            disabledforeground="#94a3b8",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=10,
            state="disabled",
            command=self.abrir_dialogo_conta_selecionada,
        )
        self.botao_editar.grid(row=0, column=2, padx=(0, 8), pady=18)

        botao_atualizar = tk.Button(
            barra_superior,
            text="Atualizar",
            bd=0,
            cursor="hand2",
            bg="#e2e8f0",
            fg=self.cores["texto_escuro"],
            activebackground="#cbd5e1",
            activeforeground=self.cores["texto_escuro"],
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=10,
            command=self.atualizar,
        )
        botao_atualizar.grid(row=0, column=3, padx=(0, 18), pady=18)

        area_filtros = tk.Frame(corpo, bg=self.cores["fundo"])
        area_filtros.grid(row=1, column=0, sticky="ew", pady=(0, 18))

        for texto, cor in [
            ("Todas", self.cores["informacao"]),
            ("Pendentes", self.cores["alerta"]),
            ("Vencidas", self.cores["perigo"]),
            ("Pagas", self.cores["sucesso"]),
        ]:
            botao = self.criar_botao_filtro(area_filtros, texto, cor)
            botao.configure(command=lambda valor=texto: self.definir_filtro(valor))
            botao.pack(side="left", padx=(0, 10))
            self.botoes_filtro[texto] = (botao, cor)

        painel_tabela = self.criar_painel(corpo)
        painel_tabela.grid(row=2, column=0, sticky="nsew")
        painel_tabela.grid_columnconfigure(0, weight=1)
        painel_tabela.grid_rowconfigure(1, weight=1)

        cabecalho_tabela = tk.Frame(painel_tabela, bg=self.cores["cartao"])
        cabecalho_tabela.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 10))
        cabecalho_tabela.grid_columnconfigure(0, weight=1)

        tk.Label(
            cabecalho_tabela,
            text="Lista de contas",
            bg=self.cores["cartao"],
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.rotulo_total = tk.Label(
            cabecalho_tabela,
            text="Total listado: R$ 0,00",
            bg=self.cores["cartao"],
            fg=self.cores["texto_suave"],
            font=("Segoe UI", 10, "bold"),
        )
        self.rotulo_total.grid(row=0, column=1, sticky="e")

        area_tabela = tk.Frame(painel_tabela, bg=self.cores["cartao"])
        area_tabela.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 22))
        area_tabela.grid_columnconfigure(0, weight=1)
        area_tabela.grid_rowconfigure(0, weight=1)

        colunas = ("conta", "categoria", "vencimento", "valor", "status")
        self.tabela = ttk.Treeview(area_tabela, columns=colunas, show="headings", selectmode="browse")

        titulos = {
            "conta": "Conta",
            "categoria": "Categoria",
            "vencimento": "Vencimento",
            "valor": "Valor",
            "status": "Status",
        }
        larguras = {
            "conta": 240,
            "categoria": 160,
            "vencimento": 130,
            "valor": 120,
            "status": 120,
        }

        for coluna in colunas:
            self.tabela.heading(coluna, text=titulos[coluna])
            self.tabela.column(coluna, width=larguras[coluna], anchor="w")

        barra_rolagem = ttk.Scrollbar(area_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra_rolagem.set)

        self.tabela.grid(row=0, column=0, sticky="nsew")
        barra_rolagem.grid(row=0, column=1, sticky="ns")
        self.tabela.bind("<<TreeviewSelect>>", lambda evento: self.atualizar_botao_editar())
        self.tabela.bind("<Double-1>", lambda evento: self.abrir_dialogo_conta_selecionada())
        self.atualizar_estilos_filtros()

    def atualizar(self):
        if not self.tabela:
            return

        contas = listar_contas_pagar(
            busca=self.variavel_busca.get().strip(),
            status_nome=self.filtro_status,
        )
        self.contas_por_id = {str(conta["id_conta_pagar"]): conta for conta in contas}
        self.tabela.delete(*self.tabela.get_children())

        if not contas:
            self.tabela.insert("", "end", values=("Nenhuma conta encontrada", "-", "-", "R$ 0,00", "-"))
            self.rotulo_total.configure(text="Total listado: R$ 0,00")
            self.atualizar_botao_editar()
            return

        total = 0
        for conta in contas:
            total += float(conta["valor"] or 0)
            self.tabela.insert(
                "",
                "end",
                iid=str(conta["id_conta_pagar"]),
                values=(
                    conta["nome_conta"],
                    conta["categoria"],
                    self.formatar_data(conta["data_vencimento"]),
                    self.formatar_moeda(conta["valor"]),
                    conta["status_exibicao"],
                ),
            )

        self.rotulo_total.configure(text=f"Total listado: {self.formatar_moeda(total)}")
        self.atualizar_botao_editar()

    def criar_botao_filtro(self, pai, texto, cor):
        return tk.Button(
            pai,
            text=texto,
            bd=0,
            cursor="hand2",
            bg="#ffffff",
            fg=cor,
            activebackground="#eef2f7",
            activeforeground=cor,
            highlightbackground=self.cores["borda"],
            highlightthickness=1,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
        )

    def definir_filtro(self, status):
        self.filtro_status = status
        self.atualizar_estilos_filtros()
        self.atualizar()

    def atualizar_estilos_filtros(self):
        for texto, (botao, cor) in self.botoes_filtro.items():
            ativo = texto == self.filtro_status
            botao.configure(
                bg=cor if ativo else "#ffffff",
                fg=self.cores["texto_claro"] if ativo else cor,
                activebackground=cor if ativo else "#eef2f7",
                activeforeground=self.cores["texto_claro"] if ativo else cor,
            )

    def atualizar_botao_editar(self):
        if not self.botao_editar:
            return

        self.botao_editar.configure(
            state="normal" if self.id_conta_selecionada(mostrar_aviso=False) else "disabled"
        )

    def id_conta_selecionada(self, mostrar_aviso=True):
        if not self.tabela:
            return None

        selecao = self.tabela.selection()
        if not selecao or selecao[0] not in self.contas_por_id:
            if mostrar_aviso:
                messagebox.showwarning("Seleção obrigatória", "Selecione uma conta para editar.")
            return None

        return int(selecao[0])

    def abrir_dialogo_nova_conta(self):
        self.abrir_dialogo_conta()

    def abrir_dialogo_conta_selecionada(self):
        id_conta = self.id_conta_selecionada()
        if not id_conta:
            return

        conta = obter_conta_pagar(id_conta)
        if not conta:
            messagebox.showerror("Erro", "Conta não encontrada no banco.")
            self.atualizar()
            return

        self.abrir_dialogo_conta(conta)

    def abrir_dialogo_conta(self, conta=None):
        categorias = listar_categorias()
        opcoes_status = listar_status_conta()

        if not categorias:
            messagebox.showerror("Erro", "Nenhuma categoria foi encontrada no banco.")
            return

        if not opcoes_status:
            messagebox.showerror("Erro", "Nenhum status foi encontrado no banco.")
            return

        editando = conta is not None
        janela_dialogo = tk.Toplevel(self)
        janela_dialogo.title("Editar conta" if editando else "Nova conta")
        janela_dialogo.geometry("460x505")
        janela_dialogo.minsize(420, 470)
        janela_dialogo.configure(bg=self.cores["fundo"])
        janela_dialogo.transient(self.winfo_toplevel())
        janela_dialogo.grab_set()

        conteudo = tk.Frame(janela_dialogo, bg=self.cores["cartao"], padx=24, pady=20)
        conteudo.pack(fill="both", expand=True, padx=18, pady=18)
        conteudo.grid_columnconfigure(1, weight=1)

        tk.Label(
            conteudo,
            text="Editar conta a pagar" if editando else "Nova conta a pagar",
            bg=self.cores["cartao"],
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        campo_nome = self.criar_campo_dialogo(conteudo, "Conta", 1)
        campo_valor = self.criar_campo_dialogo(conteudo, "Valor", 2)
        campo_vencimento = self.criar_campo_dialogo(conteudo, "Vencimento", 3)
        campo_forma_pagamento = self.criar_campo_dialogo(conteudo, "Forma pagamento", 6)

        categorias_por_nome = {categoria["nome"]: categoria["id_categoria"] for categoria in categorias}
        categoria_atual = self.nome_por_id(categorias, "id_categoria", conta.get("id_categoria") if conta else None)
        categoria_escolhida = tk.StringVar(value=categoria_atual or categorias[0]["nome"])
        self.criar_combo_dialogo(conteudo, "Categoria", 4, categoria_escolhida, list(categorias_por_nome))

        status_por_nome = {status["nome"]: status["id_status"] for status in opcoes_status}
        status_atual = self.nome_por_id(opcoes_status, "id_status", conta.get("id_status") if conta else None)
        status_escolhido = tk.StringVar(value=status_atual or "Pendente")
        self.criar_combo_dialogo(conteudo, "Status", 5, status_escolhido, list(status_por_nome))

        tk.Label(
            conteudo,
            text="Descrição",
            bg=self.cores["cartao"],
            fg=self.cores["texto_suave"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=7, column=0, sticky="nw", pady=7)

        campo_descricao = tk.Text(
            conteudo,
            height=4,
            bd=0,
            bg="#eef2f7",
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 10),
        )
        campo_descricao.grid(row=7, column=1, sticky="ew", pady=7)

        if editando:
            campo_nome.insert(0, conta["nome_conta"] or "")
            campo_valor.insert(0, self.formatar_decimal(conta["valor"]))
            campo_vencimento.insert(0, self.formatar_data(conta["data_vencimento"]))
            campo_forma_pagamento.insert(0, conta["forma_pagamento"] or "")
            campo_descricao.insert("1.0", conta["descricao"] or "")

        area_acoes = tk.Frame(conteudo, bg=self.cores["cartao"])
        area_acoes.grid(row=8, column=0, columnspan=2, sticky="e", pady=(16, 0))

        tk.Button(
            area_acoes,
            text="Cancelar",
            bd=0,
            cursor="hand2",
            bg="#e2e8f0",
            fg=self.cores["texto_escuro"],
            activebackground="#cbd5e1",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            command=janela_dialogo.destroy,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            area_acoes,
            text="Salvar",
            bd=0,
            cursor="hand2",
            bg=self.cores["informacao"],
            fg=self.cores["texto_claro"],
            activebackground="#1d4ed8",
            activeforeground=self.cores["texto_claro"],
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            command=lambda: self.salvar_conta(
                janela_dialogo=janela_dialogo,
                campo_nome=campo_nome,
                campo_valor=campo_valor,
                campo_vencimento=campo_vencimento,
                id_categoria=categorias_por_nome[categoria_escolhida.get()],
                id_status=status_por_nome[status_escolhido.get()],
                campo_forma_pagamento=campo_forma_pagamento,
                campo_descricao=campo_descricao,
                id_conta=conta["id_conta_pagar"] if editando else None,
            ),
        ).pack(side="left")

    def criar_campo_dialogo(self, pai, texto, linha):
        tk.Label(
            pai,
            text=texto,
            bg=self.cores["cartao"],
            fg=self.cores["texto_suave"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=linha, column=0, sticky="w", pady=7)

        campo = tk.Entry(
            pai,
            bd=0,
            bg="#eef2f7",
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 10),
            insertbackground=self.cores["texto_escuro"],
        )
        campo.grid(row=linha, column=1, sticky="ew", pady=7, ipady=7)
        return campo

    def criar_combo_dialogo(self, pai, texto, linha, variavel, valores):
        tk.Label(
            pai,
            text=texto,
            bg=self.cores["cartao"],
            fg=self.cores["texto_suave"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=linha, column=0, sticky="w", pady=7)

        combo = ttk.Combobox(
            pai,
            textvariable=variavel,
            values=valores,
            state="readonly",
            font=("Segoe UI", 10),
        )
        combo.grid(row=linha, column=1, sticky="ew", pady=7, ipady=4)
        return combo

    def salvar_conta(
        self,
        janela_dialogo,
        campo_nome,
        campo_valor,
        campo_vencimento,
        id_categoria,
        id_status,
        campo_forma_pagamento,
        campo_descricao,
        id_conta=None,
    ):
        nome = campo_nome.get().strip()
        forma_pagamento = campo_forma_pagamento.get().strip() or None
        descricao = campo_descricao.get("1.0", tk.END).strip() or None

        if not nome:
            messagebox.showwarning("Campos obrigatórios", "Informe o nome da conta.")
            return

        try:
            valor = self.converter_moeda(campo_valor.get())
            data_vencimento = self.converter_data(campo_vencimento.get())
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            return

        if id_conta:
            atualizar_conta_pagar(
                id_conta_pagar=id_conta,
                nome_conta=nome,
                valor=valor,
                data_vencimento=data_vencimento,
                id_categoria=id_categoria,
                id_status=id_status,
                descricao=descricao,
                forma_pagamento=forma_pagamento,
                id_usuario=self.obter_id_usuario(),
            )
        else:
            cadastrar_conta_pagar(
                nome_conta=nome,
                valor=valor,
                data_vencimento=data_vencimento,
                id_categoria=id_categoria,
                id_status=id_status,
                descricao=descricao,
                forma_pagamento=forma_pagamento,
                id_usuario=self.obter_id_usuario(),
            )

        janela_dialogo.destroy()
        self.atualizar()
        if self.ao_alterar_dados:
            self.ao_alterar_dados()

    def obter_id_usuario(self):
        if not self.usuario:
            return None

        try:
            return self.usuario["id_usuario"]
        except (KeyError, TypeError):
            return self.usuario[0]

    def nome_por_id(self, itens, chave_id, valor_id):
        for item in itens:
            if item[chave_id] == valor_id:
                return item["nome"]
        return None

    def converter_moeda(self, valor):
        texto = valor.strip().replace("R$", "").replace(" ", "")
        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")

        try:
            numero = float(texto)
        except ValueError as erro:
            raise ValueError("Informe um valor válido.") from erro

        if numero <= 0:
            raise ValueError("O valor precisa ser maior que zero.")

        return numero

    def converter_data(self, valor):
        texto = valor.strip()
        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(texto, formato).date().isoformat()
            except ValueError:
                pass

        raise ValueError("Informe uma data válida em DD/MM/AAAA ou AAAA-MM-DD.")

    def formatar_moeda(self, valor):
        numero = float(valor or 0)
        formatado = f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatado}"

    def formatar_decimal(self, valor):
        numero = float(valor or 0)
        return f"{numero:.2f}".replace(".", ",")

    def formatar_data(self, valor):
        try:
            return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
        except (TypeError, ValueError):
            return valor or "-"
