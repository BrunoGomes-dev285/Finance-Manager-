import tkinter as tk
from datetime import datetime

try:
    import pandas
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    pandas = None
    FigureCanvasTkAgg = None
    Figure = None

from banco import obter_resumo_painel
from .pagina_base import PaginaBase


class TelaPainel(PaginaBase):
    def __init__(self, pai, cores, abrir_contas_pagar):
        super().__init__(pai, cores)
        self.abrir_contas_pagar = abrir_contas_pagar
        self.rotulos_resumo = {}
        self.dados_grafico = []
        self.figura = None
        self.tela_grafico = None
        self.montar_tela()
        self.atualizar()

    def montar_tela(self):
        self.criar_cabecalho(
            "Painel",
            "Resumo financeiro e acompanhamento das contas principais.",
        )

        corpo = tk.Frame(self, bg=self.cores["fundo"])
        corpo.grid(row=1, column=0, sticky="nsew", padx=32, pady=12)
        corpo.grid_columnconfigure((0, 1, 2), weight=1, uniform="cartoes")
        corpo.grid_rowconfigure(1, weight=1)

        cartoes = [
            ("aberto", "Total em aberto", self.cores["informacao"]),
            ("pendentes", "Contas pendentes", self.cores["alerta"]),
            ("vencidas", "Contas vencidas", self.cores["perigo"]),
        ]

        for indice, (chave, titulo, cor) in enumerate(cartoes):
            self.criar_cartao_resumo(corpo, chave, titulo, cor).grid(
                row=0,
                column=indice,
                sticky="nsew",
                padx=(0 if indice == 0 else 10, 0 if indice == 2 else 10),
                pady=(0, 20),
            )

        painel_grafico = self.criar_painel(corpo)
        painel_grafico.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(0, 10))
        painel_grafico.grid_columnconfigure(0, weight=1)
        painel_grafico.grid_rowconfigure(1, weight=1)

        tk.Label(
            painel_grafico,
            text="Fluxo mensal",
            bg=self.cores["cartao"],
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(18, 6))

        if Figure is None or FigureCanvasTkAgg is None:
            tk.Label(
                painel_grafico,
                text="Instale pandas e matplotlib para visualizar o grafico.",
                bg=self.cores["cartao"],
                fg=self.cores["texto_suave"],
                font=("Segoe UI", 11, "bold"),
            ).grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        else:
            self.figura = Figure(figsize=(6, 3.4), dpi=100, facecolor=self.cores["cartao"])
            self.tela_grafico = FigureCanvasTkAgg(self.figura, master=painel_grafico)
            self.tela_grafico.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

        painel_acoes = self.criar_painel(corpo)
        painel_acoes.grid(row=1, column=2, sticky="nsew", padx=(10, 0))

        tk.Label(
            painel_acoes,
            text="Ações rápidas",
            bg=self.cores["cartao"],
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", padx=22, pady=(18, 12))

        self.criar_botao_acao(painel_acoes, "Nova conta", self.cores["informacao"], self.abrir_contas_pagar).pack(
            fill="x",
            padx=22,
            pady=6,
        )
        self.criar_botao_acao(
            painel_acoes,
            "Ver pendentes",
            self.cores["alerta"],
            self.abrir_contas_pagar,
        ).pack(fill="x", padx=22, pady=6)
        self.criar_botao_acao(painel_acoes, "Gerar relatório", self.cores["sucesso"]).pack(
            fill="x",
            padx=22,
            pady=6,
        )

    def atualizar(self):
        resumo = obter_resumo_painel()
        self.dados_grafico = resumo["fluxo_mensal"]

        self.rotulos_resumo["aberto"]["valor"].configure(text=self.formatar_moeda(resumo["total_aberto"]))
        self.rotulos_resumo["aberto"]["subtitulo"].configure(
            text=f'{resumo["qtd_total_aberto"]} contas em aberto'
        )

        self.rotulos_resumo["pendentes"]["valor"].configure(text=str(resumo["qtd_pendentes"]))
        self.rotulos_resumo["pendentes"]["subtitulo"].configure(
            text=f'{self.formatar_moeda(resumo["total_pendente"])} pendentes'
        )

        self.rotulos_resumo["vencidas"]["valor"].configure(text=str(resumo["qtd_vencidas"]))
        self.rotulos_resumo["vencidas"]["subtitulo"].configure(
            text=f'{self.formatar_moeda(resumo["total_vencido"])} vencidos'
        )

        self.desenhar_grafico_pandas()

    def criar_cartao_resumo(self, pai, chave, titulo, cor):
        cartao = self.criar_painel(pai)

        tk.Label(
            cartao,
            text=titulo,
            bg=self.cores["cartao"],
            fg=self.cores["texto_suave"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 4))

        valor = tk.Label(
            cartao,
            text="R$ 0,00",
            bg=self.cores["cartao"],
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 22, "bold"),
        )
        valor.pack(anchor="w", padx=20)

        subtitulo = tk.Label(
            cartao,
            text="0 contas",
            bg=self.cores["cartao"],
            fg=cor,
            font=("Segoe UI", 10, "bold"),
        )
        subtitulo.pack(anchor="w", padx=20, pady=(6, 18))

        self.rotulos_resumo[chave] = {"valor": valor, "subtitulo": subtitulo}
        return cartao

    def criar_botao_acao(self, pai, texto, cor, comando=None):
        return tk.Button(
            pai,
            text=texto,
            bd=0,
            cursor="hand2",
            bg=cor,
            fg=self.cores["texto_claro"],
            activebackground=cor,
            activeforeground=self.cores["texto_claro"],
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=11,
            command=comando,
        )

    def desenhar_grafico_pandas(self):
        if pandas is None or not self.figura or not self.tela_grafico:
            return

        self.figura.clear()
        eixo = self.figura.add_subplot(111)
        eixo.set_facecolor(self.cores["cartao"])

        tabela_grafico = self.criar_tabela_grafico()
        if tabela_grafico.empty:
            eixo.text(
                0.5,
                0.5,
                "Nenhuma conta cadastrada",
                color=self.cores["texto_suave"],
                fontsize=11,
                fontweight="bold",
                ha="center",
                va="center",
                transform=eixo.transAxes,
            )
            eixo.set_axis_off()
        else:
            tabela_grafico.plot(
                kind="bar",
                x="mes",
                y="total",
                ax=eixo,
                color=self.cores["informacao"],
                legend=False,
                width=0.62,
            )
            eixo.set_xlabel("")
            eixo.set_ylabel("Valor (R$)", color=self.cores["texto_suave"])
            eixo.tick_params(axis="x", rotation=0, colors=self.cores["texto_suave"])
            eixo.tick_params(axis="y", colors=self.cores["texto_suave"])
            eixo.grid(axis="y", color="#e2e8f0", linewidth=1)
            eixo.spines["top"].set_visible(False)
            eixo.spines["right"].set_visible(False)
            eixo.spines["left"].set_color("#cbd5e1")
            eixo.spines["bottom"].set_color("#cbd5e1")
            self.adicionar_rotulos_valor(eixo, tabela_grafico["total"].tolist())

        self.figura.tight_layout(pad=1.3)
        self.tela_grafico.draw_idle()

    def criar_tabela_grafico(self):
        if not self.dados_grafico:
            return pandas.DataFrame(columns=["mes", "total"])

        tabela = pandas.DataFrame(self.dados_grafico)
        tabela["total"] = pandas.to_numeric(tabela["total"], errors="coerce").fillna(0)
        tabela["mes"] = tabela["periodo"].apply(self.rotulo_mes)
        return tabela[["mes", "total"]]

    def adicionar_rotulos_valor(self, eixo, valores):
        for barra, valor in zip(eixo.patches, valores):
            eixo.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height(),
                self.formatar_moeda(valor),
                ha="center",
                va="bottom",
                fontsize=8,
                color=self.cores["texto_escuro"],
            )

    def formatar_moeda(self, valor):
        numero = float(valor or 0)
        formatado = f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatado}"

    def rotulo_mes(self, valor):
        try:
            return datetime.strptime(valor, "%Y-%m").strftime("%m/%Y")
        except (TypeError, ValueError):
            return valor or "-"
