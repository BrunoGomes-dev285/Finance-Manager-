import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from banco import criar_tabelas, verificar_acesso
from cadastro import abrir_janela_cadastro

try:
    from PIL import Image, ImageOps, ImageTk
except ImportError:
    Image = None
    ImageOps = None
    ImageTk = None


IMAGEM_FUNDO = Path(__file__).with_name("fundo.png")


def configurar_fundo(janela):
    janela.configure(bg="black")

    if Image is None or not IMAGEM_FUNDO.exists():
        return

    imagem_original = Image.open(IMAGEM_FUNDO)
    fundo = tk.Label(janela)
    fundo.place(x=0, y=0, relwidth=1, relheight=1)

    def ajustar_fundo(evento=None):
        largura = janela.winfo_width()
        altura = janela.winfo_height()

        if largura <= 1 or altura <= 1:
            return

        imagem_ajustada = ImageOps.fit(imagem_original, (largura, altura))
        imagem_tk = ImageTk.PhotoImage(imagem_ajustada)
        fundo.config(image=imagem_tk)
        fundo.image = imagem_tk

    janela.bind("<Configure>", ajustar_fundo)
    janela.after(100, ajustar_fundo)


def abrir_janela_acesso():
    criar_tabelas()

    janela = tk.Tk()
    janela.title("Acesso - Gerenciador Financeiro")
    janela.geometry("800x600")
    janela.minsize(620, 500)
    configurar_fundo(janela)

    quadro_acesso = tk.Frame(janela, bg="black", padx=35, pady=25)
    quadro_acesso.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        quadro_acesso,
        text="Gerenciador Financeiro",
        font=("Arial", 35),
        fg="white",
        bg="black",
    ).pack(pady=20)

    tk.Label(
        quadro_acesso,
        text="Bem-vindo!",
        font=("Arial", 25),
        fg="white",
        bg="black",
    ).pack(pady=10)

    tk.Label(quadro_acesso, text="Email", font=("Arial", 15), fg="white", bg="black").pack(pady=5)
    campo_email = tk.Entry(quadro_acesso, font=("Arial", 15), width=30)
    campo_email.pack(pady=5)

    tk.Label(quadro_acesso, text="Senha", font=("Arial", 15), fg="white", bg="black").pack(pady=5)
    campo_senha = tk.Entry(quadro_acesso, font=("Arial", 15), width=30, show="*")
    campo_senha.pack(pady=5)

    def confirmar_acesso():
        email = campo_email.get().strip()
        senha = campo_senha.get().strip()

        if not email or not senha:
            messagebox.showwarning("Campos obrigatórios", "Preencha email e senha.")
            return

        usuario = verificar_acesso(email, senha)

        if not usuario:
            messagebox.showerror("Erro", "Email ou senha incorretos.")
            return

        messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario['nome_completo']}!")
        janela.destroy()

        from principal import AplicativoFinanceiro

        aplicativo = AplicativoFinanceiro(usuario=dict(usuario))
        aplicativo.mainloop()

    tk.Button(quadro_acesso, text="Entrar", font=("Arial", 15), command=confirmar_acesso).pack(pady=(20, 8))
    tk.Button(
        quadro_acesso,
        text="Criar cadastro",
        font=("Arial", 12),
        command=lambda: abrir_janela_cadastro(janela),
    ).pack(pady=(0, 10))

    campo_senha.bind("<Return>", lambda evento: confirmar_acesso())
    janela.mainloop()


if __name__ == "__main__":
    abrir_janela_acesso()
