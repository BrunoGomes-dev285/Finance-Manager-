import tkinter as tk
from gastos import tela_gastos
from saldos import tela_saldo

# Funcao responsavel por abrir a tela principal depois do login
def abrir_main(usuario):
    # Criando a janela da tela principal
    janela_m = tk.Tk()

    # Nomeando a tela
    janela_m.title("Finance Manager")

    # Configurando aspectos da janela
    janela_m.geometry("1200x700")
    janela_m.configure(bg="gray")

    # Criando um menu lateral para abrigar todas as abas
    menu_lateral = tk.Frame(janela_m, bg="green", width=250)
    menu_lateral.pack(side="left", fill="y")

    # Impede que o menu lateral diminua conforme o tamanho dos botoes
    menu_lateral.pack_propagate(False)

    # Frame da direita onde cada tela do sistema sera carregada
    conteudo = tk.Frame(janela_m, bg="gray")
    conteudo.pack(side="right", fill="both", expand=True)

    # Remove os widgets da tela atual antes de carregar outra tela
    def limpar_conteudo():
        for widget in conteudo.winfo_children():
            widget.destroy()

    # Funcao temporaria para mostrar o titulo da pagina selecionada
    # Depois ela pode ser substituida pelas telas reais, como saldos.py e gastos.py
    def mostrar_pagina(titulo):
        limpar_conteudo()
        label_titulo = tk.Label(conteudo, text=titulo, font=("Arial", 28), bg="gray", fg="white")
        label_titulo.pack(pady=40)

    # Fecha a tela principal e abre a tela de login novamente
    def fazer_logout():
        janela_m.destroy()

        # Import aqui dentro evita conflito de importacao circular entre login.py e main.py
        from login import abrir_login

        abrir_login()

    # Criando os botoes do menu lateral
    botao_dashboard = tk.Button(menu_lateral,
        text="Dashboard",
        font=("Arial", 14),
        command=lambda: mostrar_pagina("Dashboard"),
    )
    botao_dashboard.pack(fill="x", padx=20, pady=(30, 10))

    botao_contas = tk.Button(menu_lateral,
        text="Contas a pagar",
        font=("Arial", 14),
        command=lambda: mostrar_pagina("Contas a pagar"),
    )
    botao_contas.pack(fill="x", padx=20, pady=10)

    botao_saldos = tk.Button(menu_lateral,
        text="Saldo a receber",
        font=("Arial", 14),
        command=lambda: tela_saldo(conteudo, usuario),
    )
    botao_saldos.pack(fill="x", padx=20, pady=10)

    botao_gastos = tk.Button(
        menu_lateral,
        text="Planilha de gastos",
        font=("Arial", 14),
        command=lambda: tela_gastos(conteudo, usuario)
    )
    botao_gastos.pack(fill="x", padx=20, pady=10)

    botao_logout = tk.Button(
        menu_lateral,
        text="Logout",
        font=("Arial", 14),
        command=fazer_logout,
    )
    botao_logout.pack(side="bottom", fill="x", padx=20, pady=30)

    # Tela inicial exibida assim que a janela principal abre
    mostrar_pagina("Dashboard")

    # Mantem a janela principal aberta
    janela_m.mainloop()


# Garante que a tela principal so abra automaticamente quando este arquivo for executado diretamente
if __name__ == "__main__":
    abrir_main((1, "Usuario Teste", "teste@email.com"))
