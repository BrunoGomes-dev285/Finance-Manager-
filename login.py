import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
from banco import criar_tabelas, verificar_login

# Criando as funcoes
def confirmar_login():
    email = campo_nome.get().strip()
    senha = campo_senha.get().strip()

    if not email or not senha:
        messagebox.showwarning("Campos obrigatorios", "Preencha email e senha.")
        return

    usuario = verificar_login(email, senha)

    if usuario:
        messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario[1]}!")
    else:
        messagebox.showerror("Erro", "Email ou senha incorretos.")


# Criando a janela
janela = tk.Tk()

# Nomeando a janela
janela.title("Login - Finance Manager")

# Configurando o tamanho da janela e cor de fundo
janela.geometry("800x600")
janela.configure(bg="black")

criar_tabelas()

# Carregando a imagem de fundo
imagem_original = Image.open("fundo.png")

# Configurando a Label que abrigara a imagem de fundo
fundo = tk.Label(janela)
fundo.place(x=0, y=0, relwidth=1, relheight=1)


def ajustar_fundo(event=None):
    largura = janela.winfo_width()
    altura = janela.winfo_height()

    if largura <= 1 or altura <= 1:
        return

    imagem_ajustada = ImageOps.fit(imagem_original, (largura, altura))
    imagem_tk = ImageTk.PhotoImage(imagem_ajustada)
    fundo.config(image=imagem_tk)
    fundo.image = imagem_tk


janela.bind("<Configure>", ajustar_fundo)

# Frame central para manter os campos alinhados em qualquer tamanho de tela
frame_login = tk.Frame(janela, bg="black", padx=35, pady=25)
frame_login.place(relx=0.5, rely=0.5, anchor="center")

# Configurando o nome do app
label_p = tk.Label(frame_login, text="Finance Manager", font=("Arial", 35), fg="white", bg="black")
label_p.pack(pady=20)

# Configurando as boas-vindas
label_bv = tk.Label(frame_login, text="Bem-vindo!", font=("Arial", 25), fg="white", bg="black")
label_bv.pack(pady=10)

# Configurando as entradas
label_nome = tk.Label(frame_login, text="Email", font=("Arial", 15), fg="white", bg="black")
label_nome.pack(pady=5)

campo_nome = tk.Entry(frame_login, font=("Arial", 15), width=30)
campo_nome.pack(pady=5)

label_senha = tk.Label(frame_login, text="Senha", font=("Arial", 15), fg="white", bg="black")
label_senha.pack(pady=5)

campo_senha = tk.Entry(frame_login, font=("Arial", 15), width=30, show="*")
campo_senha.pack(pady=5)

# Configurando o botao de login
botao_login = tk.Button(frame_login, text="Login", font=("Arial", 15), command=confirmar_login)
botao_login.pack(pady=20)

janela.mainloop()
