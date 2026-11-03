"""Extrato paginado (R11) e débito com transação (R12)."""


def statement(conn, customer_id, page, page_size):
    """Extrato cronológico paginado. A ser implementado na T6."""
    raise NotImplementedError("Implementar em T6")


def debit(conn, customer_id, amount_cents):
    """Débito com transação BEGIN IMMEDIATE. A ser implementado na T7."""
    raise NotImplementedError("Implementar em T7")
