"""Reembolso total e parcial (R04, R05).

Regras da casa:
- Reembolso só é permitido se a soma dos reembolsos anteriores + o novo valor
  for menor ou igual ao valor pago (R04).
- Pagamentos com status ``pending`` não aceitam reembolso (R05).
- A verificação da soma e a inserção ocorrem dentro de uma transação para
  evitar race condition.
"""

import sqlite3
import uuid
from datetime import datetime, timezone

from app.db import fetch_one, fetch_all
from app.errors import RefundError, ValidationError
from app.money import parse_amount_cents


def refund_payment(
    conn: sqlite3.Connection, payment_id: str, amount_cents: int
) -> dict:
    """Reembolsa um pagamento, total ou parcialmente.

    Args:
        conn: Conexão com o banco de dados.
        payment_id: ID do pagamento a ser reembolsado.
        amount_cents: Valor do reembolso em centavos.

    Returns:
        Dicionário com os dados do reembolso criado.

    Raises:
        ValidationError: Se ``amount_cents`` for inválido (não-int ou <= 0).
        RefundError: Se o pagamento estiver ``pending`` (R05) ou se a soma dos
            reembolsos ultrapassar o valor pago (R04).
    """
    amount_cents = parse_amount_cents(amount_cents)

    row = fetch_one(conn, "SELECT * FROM payments WHERE id = ?", (payment_id,))
    if row is None:
        raise RefundError(f"Pagamento '{payment_id}' não encontrado")

    payment = dict(row)

    # R05: pagamento com status pending não pode ser reembolsado
    if payment["status"] == "pending":
        raise RefundError(
            "Não é possível reembolsar um pagamento com status 'pending'"
        )

    # R04: verificação e inserção dentro de uma transação para evitar race
    with conn:
        rows = fetch_all(
            conn,
            "SELECT SUM(amount_cents) AS total FROM refunds WHERE payment_id = ?",
            (payment_id,),
        )
        already_refunded = rows[0]["total"] or 0

        if already_refunded + amount_cents > payment["amount_cents"]:
            raise RefundError(
                f"Reembolso de {amount_cents} centavos excede o saldo disponível "
                f"({payment['amount_cents'] - already_refunded} centavos restantes)"
            )

        refund = {
            "id": str(uuid.uuid4()),
            "payment_id": payment_id,
            "amount_cents": amount_cents,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        conn.execute(
            """
            INSERT INTO refunds (id, payment_id, amount_cents, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                refund["id"],
                refund["payment_id"],
                refund["amount_cents"],
                refund["created_at"],
            ),
        )

    return refund
