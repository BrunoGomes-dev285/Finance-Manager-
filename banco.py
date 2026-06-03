import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path


ARQUIVO_BANCO = Path(__file__).with_name("gerenciador_financeiro.db")
ARQUIVO_SQL = Path(__file__).with_name("banco_sqlite.sql")
EMAIL_USUARIO_SISTEMA = "sistema@gerenciador-financeiro.local"


def conectar():
    conexao = sqlite3.connect(ARQUIVO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


@contextmanager
def abrir_conexao():
    conexao = conectar()
    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def criar_tabelas():
    with abrir_conexao() as conexao:
        with open(ARQUIVO_SQL, "r", encoding="utf-8") as arquivo:
            conexao.executescript(arquivo.read())


def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def cadastrar_usuario(nome, email, senha):
    with abrir_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (nome_completo, email, senha_hash)
            VALUES (?, ?, ?)
            """,
            (nome, email, gerar_hash_senha(senha)),
        )
        return cursor.lastrowid


def verificar_acesso(email, senha):
    with abrir_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            SELECT id_usuario, nome_completo, email
            FROM usuarios
            WHERE email = ? AND senha_hash = ?
            """,
            (email, gerar_hash_senha(senha)),
        )
        return cursor.fetchone()


def garantir_usuario_sistema():
    with abrir_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE email = ?",
            (EMAIL_USUARIO_SISTEMA,),
        )
        usuario = cursor.fetchone()

        if usuario:
            return usuario["id_usuario"]

        cursor.execute(
            """
            INSERT INTO usuarios (nome_completo, email, senha_hash)
            VALUES (?, ?, ?)
            """,
            (
                "Sistema",
                EMAIL_USUARIO_SISTEMA,
                gerar_hash_senha("finance-manager"),
            ),
        )
        return cursor.lastrowid


def listar_categorias(apenas_ativas=True):
    sql = "SELECT id_categoria, nome, descricao, ativo FROM categorias"
    if apenas_ativas:
        sql += " WHERE ativo = 1"
    sql += " ORDER BY nome"

    with abrir_conexao() as conexao:
        return [dict(row) for row in conexao.execute(sql).fetchall()]


def listar_status_conta():
    with abrir_conexao() as conexao:
        return [
            dict(row)
            for row in conexao.execute(
                "SELECT id_status, nome, descricao FROM status_conta ORDER BY id_status"
            ).fetchall()
        ]


def _resolver_status_filtro(status_nome):
    filtros = {
        "Todas": None,
        "Pendente": "Pendente",
        "Pendentes": "Pendente",
        "Vencida": "Vencida",
        "Vencidas": "Vencida",
        "Pago": "Pago",
        "Pagas": "Pago",
        "Cancelado": "Cancelado",
        "Canceladas": "Cancelado",
    }
    return filtros.get(status_nome, status_nome)


def listar_contas_pagar(busca="", status_nome=None, limite=None):
    hoje = date.today().isoformat()
    status_filtro = _resolver_status_filtro(status_nome)
    parametros = [hoje]
    filtros = []

    if busca:
        termo = f"%{busca.strip()}%"
        filtros.append(
            """
            (
                cp.nome_conta LIKE ?
                OR c.nome LIKE ?
                OR s.nome LIKE ?
                OR IFNULL(cp.descricao, '') LIKE ?
                OR IFNULL(cp.forma_pagamento, '') LIKE ?
            )
            """
        )
        parametros.extend([termo, termo, termo, termo, termo])

    if status_filtro == "Vencida":
        filtros.append("cp.data_vencimento < ? AND s.nome = 'Pendente'")
        parametros.append(hoje)
    elif status_filtro:
        filtros.append("s.nome = ?")
        parametros.append(status_filtro)

    sql = """
        SELECT
            cp.id_conta_pagar,
            cp.id_categoria,
            cp.id_status,
            cp.nome_conta,
            cp.valor,
            cp.data_vencimento,
            cp.data_pagamento,
            cp.descricao,
            cp.forma_pagamento,
            c.nome AS categoria,
            s.nome AS status,
            CASE
                WHEN cp.data_vencimento < ? AND s.nome = 'Pendente' THEN 'Vencida'
                ELSE s.nome
            END AS status_exibicao
        FROM contas_pagar cp
        JOIN categorias c ON c.id_categoria = cp.id_categoria
        JOIN status_conta s ON s.id_status = cp.id_status
    """

    if filtros:
        sql += " WHERE " + " AND ".join(filtros)

    sql += " ORDER BY date(cp.data_vencimento) ASC, cp.id_conta_pagar DESC"

    if limite:
        sql += " LIMIT ?"
        parametros.append(limite)

    with abrir_conexao() as conexao:
        return [dict(row) for row in conexao.execute(sql, parametros).fetchall()]


def obter_conta_pagar(id_conta_pagar):
    contas = listar_contas_pagar()
    for conta in contas:
        if conta["id_conta_pagar"] == id_conta_pagar:
            return conta
    return None


def cadastrar_conta_pagar(
    nome_conta,
    valor,
    data_vencimento,
    id_categoria,
    id_status=1,
    descricao=None,
    forma_pagamento=None,
    id_usuario=None,
):
    usuario_criacao = id_usuario or garantir_usuario_sistema()

    with abrir_conexao() as conexao:
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
                descricao,
                forma_pagamento
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_categoria,
                id_status,
                usuario_criacao,
                nome_conta,
                valor,
                data_vencimento,
                descricao,
                forma_pagamento,
            ),
        )
        return cursor.lastrowid


def atualizar_conta_pagar(
    id_conta_pagar,
    nome_conta,
    valor,
    data_vencimento,
    id_categoria,
    id_status,
    descricao=None,
    forma_pagamento=None,
    id_usuario=None,
):
    usuario_edicao = id_usuario or garantir_usuario_sistema()

    with abrir_conexao() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM status_conta WHERE id_status = ?", (id_status,))
        status = cursor.fetchone()
        data_pagamento = date.today().isoformat() if status and status["nome"] == "Pago" else None

        cursor.execute(
            """
            UPDATE contas_pagar
            SET
                id_categoria = ?,
                id_status = ?,
                id_usuario_edicao = ?,
                nome_conta = ?,
                valor = ?,
                data_vencimento = ?,
                data_pagamento = ?,
                descricao = ?,
                forma_pagamento = ?
            WHERE id_conta_pagar = ?
            """,
            (
                id_categoria,
                id_status,
                usuario_edicao,
                nome_conta,
                valor,
                data_vencimento,
                data_pagamento,
                descricao,
                forma_pagamento,
                id_conta_pagar,
            ),
        )
        return cursor.rowcount


def obter_resumo_painel():
    hoje = date.today().isoformat()

    with abrir_conexao() as conexao:
        cursor = conexao.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(cp.valor), 0) AS total, COUNT(*) AS quantidade
            FROM contas_pagar cp
            JOIN status_conta s ON s.id_status = cp.id_status
            WHERE s.nome NOT IN ('Pago', 'Cancelado')
            """
        )
        total_aberto = dict(cursor.fetchone())

        cursor.execute(
            """
            SELECT COALESCE(SUM(cp.valor), 0) AS total, COUNT(*) AS quantidade
            FROM contas_pagar cp
            JOIN status_conta s ON s.id_status = cp.id_status
            WHERE s.nome = 'Pendente'
            """
        )
        pendentes = dict(cursor.fetchone())

        cursor.execute(
            """
            SELECT COALESCE(SUM(cp.valor), 0) AS total, COUNT(*) AS quantidade
            FROM contas_pagar cp
            JOIN status_conta s ON s.id_status = cp.id_status
            WHERE cp.data_vencimento < ? AND s.nome = 'Pendente'
            """,
            (hoje,),
        )
        vencidas = dict(cursor.fetchone())

        cursor.execute(
            """
            SELECT
                substr(cp.data_vencimento, 1, 7) AS periodo,
                COALESCE(SUM(cp.valor), 0) AS total
            FROM contas_pagar cp
            GROUP BY substr(cp.data_vencimento, 1, 7)
            ORDER BY periodo
            LIMIT 6
            """
        )
        fluxo_mensal = [dict(row) for row in cursor.fetchall()]

    return {
        "total_aberto": total_aberto["total"],
        "qtd_total_aberto": total_aberto["quantidade"],
        "total_pendente": pendentes["total"],
        "qtd_pendentes": pendentes["quantidade"],
        "total_vencido": vencidas["total"],
        "qtd_vencidas": vencidas["quantidade"],
        "fluxo_mensal": fluxo_mensal,
    }
