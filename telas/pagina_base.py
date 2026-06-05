import tkinter as tk


class PaginaBase(tk.Frame):
    def __init__(self, pai, cores):
        super().__init__(pai, bg=cores["fundo"])
        self.cores = cores
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def criar_cabecalho(self, titulo, subtitulo):
        cabecalho = tk.Frame(self, bg=self.cores["fundo"])
        cabecalho.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 12))
        cabecalho.grid_columnconfigure(0, weight=1)

        tk.Label(
            cabecalho,
            text=titulo,
            bg=self.cores["fundo"],
            fg=self.cores["texto_escuro"],
            font=("Segoe UI", 24, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            cabecalho,
            text=subtitulo,
            bg=self.cores["fundo"],
            fg=self.cores["texto_suave"],
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def criar_painel(self, pai):
        return tk.Frame(
            pai,
            bg=self.cores["cartao"],
            highlightbackground=self.cores["borda"],
            highlightthickness=1,
        )
