"""Conexão, schema e consultas parametrizadas (R09).

Regras da casa:
- Toda consulta SQL usa parâmetros (``?``), nunca concatenação ou f-string.
"""

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


def connect(path):
    """Abre uma conexão sqlite3. A ser completado na T3."""
    raise NotImplementedError("Implementar em T3")


def init_schema(conn):
    """Cria as tabelas. A ser completado na T3."""
    raise NotImplementedError("Implementar em T3")
