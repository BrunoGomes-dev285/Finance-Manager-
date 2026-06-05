import hashlib
import sqlite3
from pathlib import Path


ARQUIVO_BANCO = Path(__file__).with_name("finance_manager.db")
ARQUIVO_SQL = Path(__file__).with_name("banco_sqlite.sql")


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


def cadastrar_conta_receber(id_usuario, nome_conta, valor, data_recebimento, descricao, id_status=1):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO contas_receber (
            id_categoria,
            id_status,
            id_usuario_criacao,
            nome_conta,
            valor,
            data_recebimento,
            data_recebido_em,
            descricao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            7,
            id_status,
            id_usuario,
            nome_conta,
            valor,
            data_recebimento,
            None,
            descricao,
        ),
    )

    conexao.commit()
    conexao.close()


def listar_contas_receber():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            cr.id_conta_receber,
            cr.nome_conta,
            cr.valor,
            cr.data_recebimento,
            sc.nome,
            cr.descricao
        FROM contas_receber cr
        JOIN status_conta sc ON sc.id_status = cr.id_status
        ORDER BY cr.id_conta_receber DESC
        """
    )

    contas = cursor.fetchall()
    conexao.close()

    return contas


def excluir_receber(id_conta_receber):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM contas_receber
        WHERE id_conta_receber = ?
        """,
        (id_conta_receber,),
    )

    conexao.commit()
    conexao.close()


def marcar_recebido(id_conta_receber, data_recebido_em):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE contas_receber
        SET id_status = 3,
            data_recebido_em = ?
        WHERE id_conta_receber = ?
        """,
        (data_recebido_em, id_conta_receber),
    )

    conexao.commit()
    conexao.close()


def cadastrar_gasto(
    id_usuario,
    nome_conta,
    valor,
    data_vencimento,
    descricao,
    forma_pagamento,
    id_status=1,
):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO contas_pagar (
            id_categoria,
            id_status,
            id_usuario_criacao,
            nome_conta,
            valor,
            data_vencimento,
            data_pagamento,
            descricao,
            forma_pagamento
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            7,
            id_status,
            id_usuario,
            nome_conta,
            valor,
            data_vencimento,
            None,
            descricao,
            forma_pagamento,
        ),
    )

    conexao.commit()
    conexao.close()


def listar_gastos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            cp.id_conta_pagar,
            cp.nome_conta,
            cp.valor,
            cp.data_vencimento,
            sc.nome,
            cp.forma_pagamento,
            cp.descricao
        FROM contas_pagar cp
        JOIN status_conta sc ON sc.id_status = cp.id_status
        ORDER BY cp.id_conta_pagar DESC
        """
    )

    gastos = cursor.fetchall()
    conexao.close()

    return gastos


def excluir_gasto(id_conta_pagar):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM contas_pagar
        WHERE id_conta_pagar = ?
        """,
        (id_conta_pagar,),
    )

    conexao.commit()
    conexao.close()


def marcar_gasto_pago(id_conta_pagar, data_pagamento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE contas_pagar
        SET id_status = 2,
            data_pagamento = ?
        WHERE id_conta_pagar = ?
        """,
        (data_pagamento, id_conta_pagar),
    )

    conexao.commit()
    conexao.close()
