import hashlib
import sqlite3
from pathlib import Path


ARQUIVO_BANCO = Path(__file__).with_name("finance_manager.db")
ARQUIVO_SQL = Path(__file__).with_name("banco_sqlite.sql")


def conectar():
    conexao = sqlite3.connect(ARQUIVO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def conectar_dict():
    conexao = conectar()
    conexao.row_factory = sqlite3.Row
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


def listar_categorias():
    conexao = conectar_dict()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id_categoria, nome, descricao, ativo
        FROM categorias
        WHERE ativo = 1
        ORDER BY nome
        """
    )

    categorias = [dict(categoria) for categoria in cursor.fetchall()]
    conexao.close()

    return categorias


def listar_status_conta():
    conexao = conectar_dict()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id_status, nome, descricao
        FROM status_conta
        ORDER BY id_status
        """
    )

    status = [dict(item) for item in cursor.fetchall()]
    conexao.close()

    return status


def cadastrar_conta_pagar(
    nome_conta,
    valor,
    data_vencimento,
    id_categoria,
    id_status,
    descricao=None,
    forma_pagamento=None,
    id_usuario=None,
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
            id_categoria,
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
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE contas_pagar
        SET nome_conta = ?,
            valor = ?,
            data_vencimento = ?,
            id_categoria = ?,
            id_status = ?,
            descricao = ?,
            forma_pagamento = ?,
            id_usuario_edicao = ?
        WHERE id_conta_pagar = ?
        """,
        (
            nome_conta,
            valor,
            data_vencimento,
            id_categoria,
            id_status,
            descricao,
            forma_pagamento,
            id_usuario,
            id_conta_pagar,
        ),
    )

    conexao.commit()
    conexao.close()


def obter_conta_pagar(id_conta_pagar):
    conexao = conectar_dict()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT *
        FROM contas_pagar
        WHERE id_conta_pagar = ?
        """,
        (id_conta_pagar,),
    )

    conta = cursor.fetchone()
    conexao.close()

    return dict(conta) if conta else None


def listar_contas_pagar(busca="", status_nome="Todas"):
    conexao = conectar_dict()
    cursor = conexao.cursor()

    filtros = []
    parametros = []

    if busca:
        filtros.append("(cp.nome_conta LIKE ? OR cp.descricao LIKE ? OR c.nome LIKE ?)")
        termo = f"%{busca}%"
        parametros.extend([termo, termo, termo])

    if status_nome == "Pendentes":
        filtros.append("sc.nome = 'Pendente'")
    elif status_nome == "Pagas":
        filtros.append("sc.nome = 'Pago'")
    elif status_nome == "Vencidas":
        filtros.append("sc.nome = 'Pendente' AND cp.data_vencimento < date('now')")

    where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    cursor.execute(
        f"""
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
            sc.nome AS status,
            CASE
                WHEN sc.nome = 'Pendente' AND cp.data_vencimento < date('now') THEN 'Vencida'
                ELSE sc.nome
            END AS status_exibicao
        FROM contas_pagar cp
        JOIN categorias c ON c.id_categoria = cp.id_categoria
        JOIN status_conta sc ON sc.id_status = cp.id_status
        {where}
        ORDER BY cp.data_vencimento ASC, cp.id_conta_pagar DESC
        """,
        parametros,
    )

    contas = [dict(conta) for conta in cursor.fetchall()]
    conexao.close()

    return contas


def obter_resumo_painel():
    conexao = conectar_dict()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN sc.nome <> 'Pago' THEN cp.valor ELSE 0 END), 0) AS total_aberto,
            COUNT(CASE WHEN sc.nome <> 'Pago' THEN 1 END) AS qtd_total_aberto,
            COUNT(CASE WHEN sc.nome = 'Pendente' THEN 1 END) AS qtd_pendentes,
            COALESCE(SUM(CASE WHEN sc.nome = 'Pendente' THEN cp.valor ELSE 0 END), 0) AS total_pendente,
            COUNT(CASE WHEN sc.nome = 'Pendente' AND cp.data_vencimento < date('now') THEN 1 END) AS qtd_vencidas,
            COALESCE(SUM(CASE WHEN sc.nome = 'Pendente' AND cp.data_vencimento < date('now') THEN cp.valor ELSE 0 END), 0) AS total_vencido
        FROM contas_pagar cp
        JOIN status_conta sc ON sc.id_status = cp.id_status
        """
    )
    resumo = dict(cursor.fetchone())

    cursor.execute(
        """
        SELECT
            substr(data_vencimento, 1, 7) AS periodo,
            COALESCE(SUM(valor), 0) AS total
        FROM contas_pagar
        GROUP BY substr(data_vencimento, 1, 7)
        ORDER BY periodo
        LIMIT 6
        """
    )
    fluxo_mensal = [dict(item) for item in cursor.fetchall() if item["periodo"]]
    conexao.close()

    resumo["fluxo_mensal"] = fluxo_mensal
    return resumo
