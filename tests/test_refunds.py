"""Testes de reembolso: R04 e R05."""

import pytest

from app.db import connect, init_schema
from app.errors import RefundError, ValidationError
from app.payments import create_payment
from app.refunds import refund_payment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_payment(conn, amount_cents=1000, status="approved"):
    """Cria um pagamento e opcionalmente força um status diferente de 'approved'."""
    payment = create_payment(conn, "customer-1", amount_cents, "BRL")
    if status != "approved":
        conn.execute(
            "UPDATE payments SET status = ? WHERE id = ?",
            (status, payment["id"]),
        )
        conn.commit()
        payment["status"] = status
    return payment


# ---------------------------------------------------------------------------
# R04 – reembolso não pode ultrapassar o valor pago
# ---------------------------------------------------------------------------


def test_r04_reembolso_maior_que_pago_rejeita(tmp_path):
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=500)

    with pytest.raises(RefundError):
        refund_payment(conn, payment["id"], 501)


def test_r04_reembolso_parcial_acumulado_excede_rejeita(tmp_path):
    """Dois reembolsos parciais cuja soma excede o valor pago devem ser rejeitados."""
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=1000)

    # Primeiro reembolso: 600 centavos (OK)
    refund_payment(conn, payment["id"], 600)

    # Segundo reembolso: 401 centavos – soma seria 1001 > 1000 (deve rejeitar)
    with pytest.raises(RefundError):
        refund_payment(conn, payment["id"], 401)


def test_r04_reembolso_exato_aceita(tmp_path):
    """Reembolso igual ao valor total pago deve ser aceito."""
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=800)

    refund = refund_payment(conn, payment["id"], 800)

    assert refund["amount_cents"] == 800
    assert refund["payment_id"] == payment["id"]


def test_r04_dois_reembolsos_parciais_que_somam_exato_aceita(tmp_path):
    """Dois reembolsos cuja soma exata iguala o valor pago devem ser aceitos."""
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=1000)

    refund_payment(conn, payment["id"], 400)
    refund2 = refund_payment(conn, payment["id"], 600)

    assert refund2["amount_cents"] == 600


def test_r04_rejeicao_nao_altera_banco(tmp_path):
    """Quando o reembolso é rejeitado, nenhuma linha deve ser inserida em refunds."""
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=300)

    with pytest.raises(RefundError):
        refund_payment(conn, payment["id"], 999)

    count = conn.execute(
        "SELECT COUNT(*) FROM refunds WHERE payment_id = ?", (payment["id"],)
    ).fetchone()[0]
    assert count == 0


# ---------------------------------------------------------------------------
# R05 – pagamento com status pending não pode ser reembolsado
# ---------------------------------------------------------------------------


def test_r05_reembolso_em_pagamento_pending_rejeita(tmp_path):
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=1000, status="pending")

    with pytest.raises(RefundError):
        refund_payment(conn, payment["id"], 100)


def test_r05_reembolso_em_pagamento_approved_aceita(tmp_path):
    """Status 'approved' é o caminho feliz; não deve lançar RefundError."""
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=1000, status="approved")

    refund = refund_payment(conn, payment["id"], 100)

    assert refund["amount_cents"] == 100


# ---------------------------------------------------------------------------
# Validação de entrada
# ---------------------------------------------------------------------------


def test_valor_float_rejeita(tmp_path):
    """amount_cents float deve lançar ValidationError antes de qualquer consulta."""
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=1000)

    with pytest.raises(ValidationError):
        refund_payment(conn, payment["id"], 10.0)


def test_valor_zero_rejeita(tmp_path):
    """amount_cents == 0 deve lançar ValidationError."""
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    payment = _make_payment(conn, amount_cents=1000)

    with pytest.raises(ValidationError):
        refund_payment(conn, payment["id"], 0)
