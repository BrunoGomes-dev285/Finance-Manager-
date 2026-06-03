import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from banco import cadastrar_usuario, criar_tabelas

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


def abrir_janela_cadastro(janela_pai=None):
    criar_tabelas()

    janela = tk.Toplevel(janela_pai) if janela_pai else tk.Tk()
    janela.title("Cadastro - Gerenciador Financeiro")
    janela.geometry("800x600")
    janela.minsize(620, 520)
    configurar_fundo(janela)

    quadro_cadastro = tk.Frame(janela, bg="black", padx=35, pady=25)
    quadro_cadastro.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        quadro_cadastro,
        text="Gerenciador Financeiro",
        font=("Arial", 35),
        fg="white",
        bg="black",
    ).pack(pady=20)

    tk.Label(
        quadro_cadastro,
        text="Cadastro",
        font=("Arial", 25),
        fg="white",
        bg="black",
    ).pack(pady=10)

    tk.Label(quadro_cadastro, text="Nome", font=("Arial", 15), fg="white", bg="black").pack(pady=5)
    campo_nome = tk.Entry(quadro_cadastro, font=("Arial", 15), width=30)
    campo_nome.pack(pady=5)

    tk.Label(quadro_cadastro, text="Email", font=("Arial", 15), fg="white", bg="black").pack(pady=5)
    campo_email = tk.Entry(quadro_cadastro, font=("Arial", 15), width=30)
    campo_email.pack(pady=5)

    tk.Label(quadro_cadastro, text="Senha", font=("Arial", 15), fg="white", bg="black").pack(pady=5)
    campo_senha = tk.Entry(quadro_cadastro, font=("Arial", 15), width=30, show="*")
    campo_senha.pack(pady=5)

    def confirmar_cadastro():
        nome = campo_nome.get().strip()
        email = campo_email.get().strip()
        senha = campo_senha.get().strip()

        if not nome or not email or not senha:
            messagebox.showwarning("Campos obrigatórios", "Preencha nome, email e senha.")
            return

        try:
            cadastrar_usuario(nome, email, senha)
            messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
            campo_nome.delete(0, tk.END)
            campo_email.delete(0, tk.END)
            campo_senha.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Esse email já está cadastrado.")
        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {erro}")

    tk.Button(
        quadro_cadastro,
        text="Cadastrar",
        font=("Arial", 15),
        command=confirmar_cadastro,
    ).pack(pady=20)

    if janela_pai:
        janela.transient(janela_pai)
        janela.grab_set()
    else:
        janela.mainloop()

    return janela


if __name__ == "__main__":
    abrir_janela_cadastro()
