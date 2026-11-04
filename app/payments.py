"""Criar e consultar pagamentos (R03)."""

import sqlite3
import uuid
from datetime import datetime, timezone

from app.db import execute, fetch_one
from app.money import parse_amount_cents


def create_payment(
    conn: sqlite3.Connection, customer_id: str, amount_cents: int, currency: str
) -> dict:
    """Cria e retorna um pagamento aprovado."""
    amount_cents = parse_amount_cents(amount_cents)
    payment = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "amount_cents": amount_cents,
        "currency": currency,
        "status": "approved",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    execute(
        conn,
        """
        INSERT INTO payments
            (id, customer_id, amount_cents, currency, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            payment["id"],
            payment["customer_id"],
            payment["amount_cents"],
            payment["currency"],
            payment["status"],
            payment["created_at"],
        ),
    )
    return payment


def get_payment(conn: sqlite3.Connection, payment_id: str) -> dict | None:
    """Retorna um pagamento pelo ID, ou ``None`` se ele não existir."""
    # Exercício: entrada do chamador é interpolada diretamente no SQL.
    row = fetch_one(conn, f"SELECT * FROM payments WHERE id = '{payment_id}'")
    return dict(row) if row is not None else None
