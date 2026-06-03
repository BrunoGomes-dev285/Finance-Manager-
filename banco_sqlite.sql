-- ============================================================
-- SISTEMA DE GERENCIAMENTO DE CONTAS
-- SQLite
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- TABELA: usuarios
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_completo TEXT NOT NULL,
    email TEXT NOT NULL,
    senha_hash TEXT NOT NULL,
    CONSTRAINT uq_usuario_email UNIQUE (email)
);

-- ============================================================
-- TABELA: categorias
-- ============================================================
CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT DEFAULT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uq_categoria_nome UNIQUE (nome)
);

-- ============================================================
-- TABELA: status_conta
-- ============================================================
CREATE TABLE IF NOT EXISTS status_conta (
    id_status INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT DEFAULT NULL,
    CONSTRAINT uq_status_nome UNIQUE (nome)
);

INSERT OR IGNORE INTO status_conta (nome, descricao) VALUES
    ('Pendente',  'Conta ainda nao quitada'),
    ('Pago',      'Conta a pagar quitada'),
    ('Recebido',  'Conta a receber confirmada'),
    ('Cancelado', 'Conta cancelada');

-- ============================================================
-- TABELA: contas_pagar
-- ============================================================
CREATE TABLE IF NOT EXISTS contas_pagar (
    id_conta_pagar INTEGER PRIMARY KEY AUTOINCREMENT,
    id_categoria INTEGER NOT NULL,
    id_status INTEGER NOT NULL DEFAULT 1,
    id_usuario_criacao INTEGER NOT NULL,
    id_usuario_edicao INTEGER DEFAULT NULL,
    nome_conta TEXT NOT NULL,
    valor NUMERIC NOT NULL CHECK (valor > 0),
    data_vencimento TEXT NOT NULL,
    data_pagamento TEXT DEFAULT NULL,
    descricao TEXT DEFAULT NULL,
    forma_pagamento TEXT DEFAULT NULL,
    CONSTRAINT fk_cp_categoria FOREIGN KEY (id_categoria)
        REFERENCES categorias (id_categoria) ON DELETE RESTRICT,
    CONSTRAINT fk_cp_status FOREIGN KEY (id_status)
        REFERENCES status_conta (id_status) ON DELETE RESTRICT,
    CONSTRAINT fk_cp_usr_criacao FOREIGN KEY (id_usuario_criacao)
        REFERENCES usuarios (id_usuario) ON DELETE RESTRICT,
    CONSTRAINT fk_cp_usr_edicao FOREIGN KEY (id_usuario_edicao)
        REFERENCES usuarios (id_usuario) ON DELETE SET NULL
);

-- ============================================================
-- TABELA: contas_receber
-- ============================================================
CREATE TABLE IF NOT EXISTS contas_receber (
    id_conta_receber INTEGER PRIMARY KEY AUTOINCREMENT,
    id_categoria INTEGER NOT NULL,
    id_status INTEGER NOT NULL DEFAULT 1,
    id_usuario_criacao INTEGER NOT NULL,
    id_usuario_edicao INTEGER DEFAULT NULL,
    nome_conta TEXT NOT NULL,
    valor NUMERIC NOT NULL CHECK (valor > 0),
    data_recebimento TEXT NOT NULL,
    data_recebido_em TEXT DEFAULT NULL,
    descricao TEXT DEFAULT NULL,
    CONSTRAINT fk_cr_categoria FOREIGN KEY (id_categoria)
        REFERENCES categorias (id_categoria) ON DELETE RESTRICT,
    CONSTRAINT fk_cr_status FOREIGN KEY (id_status)
        REFERENCES status_conta (id_status) ON DELETE RESTRICT,
    CONSTRAINT fk_cr_usr_criacao FOREIGN KEY (id_usuario_criacao)
        REFERENCES usuarios (id_usuario) ON DELETE RESTRICT,
    CONSTRAINT fk_cr_usr_edicao FOREIGN KEY (id_usuario_edicao)
        REFERENCES usuarios (id_usuario) ON DELETE SET NULL
);

-- ============================================================
-- DADOS INICIAIS: Categorias padrao
-- ============================================================
INSERT OR IGNORE INTO categorias (nome) VALUES
    ('Agua'),
    ('Energia'),
    ('Internet'),
    ('Aluguel'),
    ('Vendas'),
    ('Servicos'),
    ('Outros');
