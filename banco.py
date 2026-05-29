import hashlib
import sqlite3
from pathlib import Path


ARQUIVO_BANCO = Path(__file__).with_name("finance_manager.db")
ARQUIVO_SQL = Path(__file__).with_name("BD_ProjetoPython_sqlite.sql")


def conectar():
    conexao = sqlite3.connect(ARQUIVO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabelas():
    conexao = conectar()

    with open(ARQUIVO_SQL, "r", encoding="utf-8") as arquivo:
        conexao.executescript(arquivo.read())

    conexao.commit()
    conexao.close()


def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def cadastrar_usuario(nome, email, senha):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO usuarios (nome_completo, email, senha_hash)
        VALUES (?, ?, ?)
        """,
        (nome, email, gerar_hash_senha(senha)),
    )

    conexao.commit()
    conexao.close()


def verificar_login(email, senha):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id_usuario, nome_completo, email
        FROM usuarios
        WHERE email = ? AND senha_hash = ?
        """,
        (email, gerar_hash_senha(senha)),
    )

    usuario = cursor.fetchone()
    conexao.close()

    return usuario
