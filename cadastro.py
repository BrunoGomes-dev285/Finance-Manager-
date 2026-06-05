import sqlite3
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk, ImageOps

from banco import cadastrar_usuario, criar_tabelas


def abrir_cadastro():
    # Criando a janela
    janela_c = tk.Tk()

    # Nomeando a janela
    janela_c.title("Cadastro - Finance Manager")

    # Configurando o tamanho da janela e cor de fundo
    janela_c.geometry("800x600")
    janela_c.configure(bg="black")

    criar_tabelas()

    # Carregando a imagem de fundo
    imagem_original = Image.open("fundo.png")

    # Configurando a Label que abrigara a imagem de fundo
    fundo = tk.Label(janela_c)
    fundo.place(x=0, y=0, relwidth=1, relheight=1)
    #Metodo para ajustar a imagem de fundo
    def ajustar_fundo(event=None):
        largura = janela_c.winfo_width()
        altura = janela_c.winfo_height()

        if largura <= 1 or altura <= 1:
            return

        imagem_ajustada = ImageOps.fit(imagem_original, (largura, altura))
        imagem_tk = ImageTk.PhotoImage(imagem_ajustada)
        fundo.config(image=imagem_tk)
        fundo.image = imagem_tk

    #Metodo para coletar as credenciais e confirmar as mesmas no banco
    def confirmar_cadastro():
        nome = campo_nome.get().strip()
        email = campo_email.get().strip()
        senha = campo_senha.get().strip()

        if not nome or not email or not senha:
            messagebox.showwarning("Campos obrigatorios", "Preencha nome, email e senha.") #Caso algum campo nao tenha sido prenchido
            return

        try:
            cadastrar_usuario(nome, email, senha)
            messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso!")
            campo_nome.delete(0, tk.END)
            campo_email.delete(0, tk.END)
            campo_senha.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Esse email ja esta cadastrado.")
        except Exception as erro:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {erro}")
    #Metodo para redirecionar para o login caso nao tenha cadastro
    def voltar_login():
        janela_c.destroy()

        from login import abrir_login

        abrir_login()

    janela_c.bind("<Configure>", ajustar_fundo)

    # Frame central para manter os campos alinhados em qualquer tamanho de tela
    frame_cadastro = tk.Frame(janela_c, bg="black", padx=35, pady=25)
    frame_cadastro.place(relx=0.5, rely=0.5, anchor="center")

    # Configurando o nome do app
    label_p = tk.Label(frame_cadastro, text="Finance Manager", font=("Arial", 35), fg="white", bg="black")
    label_p.pack(pady=20)

    # Configurando o titulo da tela
    label_bv = tk.Label(frame_cadastro, text="Cadastro", font=("Arial", 25), fg="white", bg="black")
    label_bv.pack(pady=10)

    # Configurando as entradas
    label_nome = tk.Label(frame_cadastro, text="Nome", font=("Arial", 15), fg="white", bg="black")
    label_nome.pack(pady=5)

    campo_nome = tk.Entry(frame_cadastro, font=("Arial", 15), width=30)
    campo_nome.pack(pady=5)

    label_email = tk.Label(frame_cadastro, text="Email", font=("Arial", 15), fg="white", bg="black")
    label_email.pack(pady=5)

    campo_email = tk.Entry(frame_cadastro, font=("Arial", 15), width=30)
    campo_email.pack(pady=5)

    label_senha = tk.Label(frame_cadastro, text="Senha", font=("Arial", 15), fg="white", bg="black")
    label_senha.pack(pady=5)

    campo_senha = tk.Entry(frame_cadastro, font=("Arial", 15), width=30, show="*")
    campo_senha.pack(pady=5)

    # Configurando os botoes
    botao_cadastro = tk.Button(frame_cadastro, text="Cadastrar", font=("Arial", 15), command=confirmar_cadastro)
    botao_cadastro.pack(pady=(20, 8))

    botao_login = tk.Button(frame_cadastro, text="Ja tenho cadastro", font=("Arial", 12), command=voltar_login)
    botao_login.pack(pady=5)

    janela_c.mainloop()


if __name__ == "__main__":
    abrir_cadastro()
