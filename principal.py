import tkinter as tk
from tkinter import ttk

from banco import criar_tabelas
from telas import TelaContasPagar, TelaPainel, TelaPlanilhaGastos, TelaSaldosReceber


class AplicativoFinanceiro(tk.Tk):
    def __init__(self, usuario=None):
        super().__init__()

        criar_tabelas()

        self.usuario = usuario
        self.title("Gerenciador Financeiro")
        self.geometry("1100x700")
        self.minsize(920, 600)
        self.configure(bg="#f4f7fb")

        self.cores = {
            "fundo": "#f4f7fb",
            "menu": "#17202f",
            "menu_ativo": "#2563eb",
            "menu_hover": "#23324a",
            "texto_claro": "#f8fafc",
            "texto_suave": "#64748b",
            "texto_escuro": "#0f172a",
            "cartao": "#ffffff",
            "borda": "#dbe3ef",
            "sucesso": "#059669",
            "alerta": "#d97706",
            "perigo": "#dc2626",
            "informacao": "#2563eb",
        }

        self.botoes_menu = {}
        self.tela_ativa = None
        self.telas = {}

        self.configurar_estilos()
        self.montar_layout()
        self.criar_telas()
        self.mostrar_tela("painel")

    def configurar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            background="#ffffff",
            foreground=self.cores["texto_escuro"],
            rowheight=34,
            fieldbackground="#ffffff",
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Treeview.Heading",
            background="#eef2f7",
            foreground=self.cores["texto_escuro"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        estilo.map("Treeview", background=[("selected", "#dbeafe")])

    def montar_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.menu_lateral = tk.Frame(self, bg=self.cores["menu"], width=230)
        self.menu_lateral.grid(row=0, column=0, sticky="nsew")
        self.menu_lateral.grid_propagate(False)

        self.area_conteudo = tk.Frame(self, bg=self.cores["fundo"])
        self.area_conteudo.grid(row=0, column=1, sticky="nsew")
        self.area_conteudo.grid_columnconfigure(0, weight=1)
        self.area_conteudo.grid_rowconfigure(0, weight=1)

        self.montar_menu_lateral()

    def montar_menu_lateral(self):
        titulo = tk.Label(
            self.menu_lateral,
            text="Gerenciador\nFinanceiro",
            bg=self.cores["menu"],
            fg=self.cores["texto_claro"],
            justify="left",
            font=("Segoe UI", 20, "bold"),
        )
        titulo.pack(anchor="w", padx=24, pady=(28, 32))

        self.adicionar_botao_menu("painel", "Painel")
        self.adicionar_botao_menu("contas_pagar", "Contas a pagar")
        self.adicionar_botao_menu("saldos_receber", "Saldos a receber")
        self.adicionar_botao_menu("planilha_gastos", "Planilha de gastos")

        botao_logout = tk.Button(
            self.menu_lateral,
            text="Logout",
            anchor="w",
            cursor="hand2",
            bd=0,
            padx=18,
            pady=12,
            bg=self.cores["menu"],
            fg="#cbd5e1",
            activebackground=self.cores["perigo"],
            activeforeground=self.cores["texto_claro"],
            font=("Segoe UI", 11, "bold"),
            command=self.fazer_logout,
        )
        botao_logout.pack(side="bottom", fill="x", padx=16, pady=20)

    def adicionar_botao_menu(self, nome_tela, texto):
        botao = tk.Button(
            self.menu_lateral,
            text=texto,
            anchor="w",
            cursor="hand2",
            bd=0,
            padx=18,
            pady=12,
            bg=self.cores["menu"],
            fg="#cbd5e1",
            activebackground=self.cores["menu_ativo"],
            activeforeground=self.cores["texto_claro"],
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.mostrar_tela(nome_tela),
        )
        botao.pack(fill="x", padx=16, pady=4)
        botao.bind(
            "<Enter>",
            lambda evento, botao_atual=botao, tela=nome_tela: self.ao_passar_mouse_menu(botao_atual, tela),
        )
        botao.bind(
            "<Leave>",
            lambda evento, botao_atual=botao, tela=nome_tela: self.atualizar_botao_menu(botao_atual, tela),
        )
        self.botoes_menu[nome_tela] = botao

    def criar_telas(self):
        self.telas = {
            "painel": TelaPainel(
                self.area_conteudo,
                self.cores,
                abrir_contas_pagar=lambda: self.mostrar_tela("contas_pagar"),
            ),
            "contas_pagar": TelaContasPagar(
                self.area_conteudo,
                self.cores,
                usuario=self.usuario,
                ao_alterar_dados=self.atualizar_telas,
            ),
            "saldos_receber": TelaSaldosReceber(
                self.area_conteudo,
                self.cores,
                usuario=self.usuario,
            ),
            "planilha_gastos": TelaPlanilhaGastos(
                self.area_conteudo,
                self.cores,
                usuario=self.usuario,
            ),
        }

        for tela in self.telas.values():
            tela.grid(row=0, column=0, sticky="nsew")

    def atualizar_telas(self):
        for tela in self.telas.values():
            if hasattr(tela, "atualizar"):
                tela.atualizar()

    def ao_passar_mouse_menu(self, botao, nome_tela):
        if self.tela_ativa != nome_tela:
            botao.configure(bg=self.cores["menu_hover"], fg=self.cores["texto_claro"])

    def atualizar_botao_menu(self, botao, nome_tela):
        ativo = self.tela_ativa == nome_tela
        botao.configure(
            bg=self.cores["menu_ativo"] if ativo else self.cores["menu"],
            fg=self.cores["texto_claro"] if ativo else "#cbd5e1",
        )

    def mostrar_tela(self, nome_tela):
        self.tela_ativa = nome_tela

        for nome, botao in self.botoes_menu.items():
            self.atualizar_botao_menu(botao, nome)

        tela = self.telas[nome_tela]
        tela.tkraise()
        if hasattr(tela, "atualizar"):
            tela.atualizar()

    def fazer_logout(self):
        self.destroy()

        from login import abrir_login

        abrir_login()


if __name__ == "__main__":
    aplicativo = AplicativoFinanceiro()
    aplicativo.mainloop()
