"""Extrato paginado (R11) e débito com transação (R12)."""

import sqlite3

from app.db import fetch_all
from app.errors import ValidationError
from app.money import parse_amount_cents


def _validate_pagination(page: int, page_size: int) -> None:
    if isinstance(page, bool) or not isinstance(page, int) or page < 1:
        raise ValidationError("page deve ser um inteiro maior ou igual a 1")
    if (
        isinstance(page_size, bool)
        or not isinstance(page_size, int)
        or page_size < 1
    ):
        raise ValidationError("page_size deve ser um inteiro maior ou igual a 1")


def statement(
    conn: sqlite3.Connection, customer_id: str, page: int, page_size: int
) -> list[dict]:
    """Retorna lançamentos de pagamentos e reembolsos em ordem cronológica.

    Pagamentos aparecem com valor positivo e reembolsos com valor negativo.
    As linhas empatadas por timestamp são ordenadas por tipo e ID, garantindo
    uma ordem estável entre páginas.
    """
    _validate_pagination(page, page_size)
    offset = (page - 1) * page_size

    rows = fetch_all(
        conn,
        """
        WITH entries AS (
            SELECT
                p.id AS id,
                p.customer_id AS customer_id,
                'payment' AS type,
                p.amount_cents AS amount_cents,
                p.currency AS currency,
                p.id AS payment_id,
                p.created_at AS created_at,
                0 AS type_order
            FROM payments AS p
            WHERE p.customer_id = ?

            UNION ALL

            SELECT
                r.id AS id,
                p.customer_id AS customer_id,
                'refund' AS type,
                -r.amount_cents AS amount_cents,
                p.currency AS currency,
                r.payment_id AS payment_id,
                r.created_at AS created_at,
                1 AS type_order
            FROM refunds AS r
            JOIN payments AS p ON p.id = r.payment_id
            WHERE p.customer_id = ?
        )
        SELECT
            id, customer_id, type, amount_cents, currency, payment_id, created_at
        FROM entries
        ORDER BY created_at ASC, type_order ASC, id ASC
        LIMIT ? OFFSET ?
        """,
        (customer_id, customer_id, page_size, offset),
    )
    return [dict(row) for row in rows]


def debit(
    conn: sqlite3.Connection, customer_id: str, amount_cents: int
) -> int:
    """Debita centavos do saldo e retorna o saldo restante.

    ``BEGIN IMMEDIATE`` serializa a leitura e a atualização entre conexões.
    Um cliente sem saldo cadastrado ou sem fundos suficientes recebe
    ``ValueError``; a transação é desfeita sem alterar o saldo.
    """
    amount_cents = parse_amount_cents(amount_cents)

    conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute(
            "SELECT balance_cents FROM balances WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()
        if row is None:
            raise ValueError("Saldo do cliente não encontrado")

        balance_cents = row["balance_cents"]
        if balance_cents < amount_cents:
            raise ValueError("Saldo insuficiente")

        remaining_cents = balance_cents - amount_cents
        conn.execute(
            "UPDATE balances SET balance_cents = ? WHERE customer_id = ?",
            (remaining_cents, customer_id),
        )
        conn.commit()
        return remaining_cents
    except Exception:
        conn.rollback()
        raise
