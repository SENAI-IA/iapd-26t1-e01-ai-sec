from datetime import datetime

from app.db import connect, init_schema
from app.payments import create_payment, get_payment


def test_r03_pagamento_valido_e_gravado_com_timestamp_utc(tmp_path):
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)

    payment = create_payment(conn, "customer-1", 1250, "BRL")

    assert payment["status"] == "approved"
    assert payment["amount_cents"] == 1250
    assert payment["customer_id"] == "customer-1"
    timestamp = datetime.fromisoformat(payment["created_at"])
    assert timestamp.utcoffset().total_seconds() == 0
    assert get_payment(conn, payment["id"]) == payment


def test_r09_valor_de_cliente_nao_interpreta_sql(tmp_path):
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    customer_id = "'; DROP TABLE payments; --"

    payment = create_payment(conn, customer_id, 100, "BRL")

    assert get_payment(conn, payment["id"])["customer_id"] == customer_id
    assert get_payment(conn, payment["id"]) is not None
