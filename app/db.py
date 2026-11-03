"""Conexão, schema e consultas parametrizadas (R09).

Regras da casa:
- Toda consulta SQL usa parâmetros (``?``), nunca concatenação ou f-string.
"""

from pathlib import Path
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS refunds (
    id TEXT PRIMARY KEY,
    payment_id TEXT NOT NULL REFERENCES payments(id),
    amount_cents INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS webhook_events (
    event_id TEXT PRIMARY KEY,
    received_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS balances (
    customer_id TEXT PRIMARY KEY,
    balance_cents INTEGER NOT NULL
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    """Abre uma conexão SQLite configurada para o banco da aplicação."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Cria as tabelas da aplicação caso ainda não existam."""
    conn.executescript(SCHEMA)
    conn.commit()


def execute(
    conn: sqlite3.Connection, sql: str, params: tuple = ()
) -> sqlite3.Cursor:
    """Executa uma consulta com parâmetros e confirma a transação."""
    cursor = conn.execute(sql, params)
    conn.commit()
    return cursor


def fetch_one(
    conn: sqlite3.Connection, sql: str, params: tuple = ()
) -> sqlite3.Row | None:
    """Busca uma linha usando uma consulta parametrizada."""
    return conn.execute(sql, params).fetchone()


def fetch_all(
    conn: sqlite3.Connection, sql: str, params: tuple = ()
) -> list[sqlite3.Row]:
    """Busca várias linhas usando uma consulta parametrizada."""
    return conn.execute(sql, params).fetchall()
