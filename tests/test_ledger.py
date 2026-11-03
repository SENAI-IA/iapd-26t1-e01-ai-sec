import pytest

from app.db import connect, init_schema
from app.errors import ValidationError
from app.ledger import statement
from app.payments import create_payment
from app.refunds import refund_payment


def test_r11_extrato_paginado_cronologico_sem_repetir_ou_pular(tmp_path):
    conn = connect(tmp_path / "ledger.sqlite")
    init_schema(conn)

    first = create_payment(conn, "customer-1", 1000, "BRL")
    second = create_payment(conn, "customer-1", 2000, "BRL")
    third = create_payment(conn, "customer-1", 3000, "BRL")
    other_customer = create_payment(conn, "customer-2", 4000, "BRL")
    first_refund = refund_payment(conn, first["id"], 100)
    second_refund = refund_payment(conn, first["id"], 200)

    timestamps = [
        ("2026-01-01T00:00:00+00:00", first["id"]),
        ("2026-01-02T00:00:00+00:00", second["id"]),
        ("2026-01-04T00:00:00+00:00", third["id"]),
        ("2026-01-01T00:00:00+00:00", other_customer["id"]),
    ]
    conn.executemany(
        "UPDATE payments SET created_at = ? WHERE id = ?", timestamps
    )
    conn.executemany(
        "UPDATE refunds SET created_at = ? WHERE id = ?",
        [
            ("2026-01-02T00:00:00+00:00", first_refund["id"]),
            ("2026-01-03T00:00:00+00:00", second_refund["id"]),
        ],
    )
    conn.commit()

    pages = [statement(conn, "customer-1", page, 2) for page in (1, 2, 3)]
    entries = [entry for page in pages for entry in page]

    assert [entry["id"] for entry in entries] == [
        first["id"],
        second["id"],
        first_refund["id"],
        second_refund["id"],
        third["id"],
    ]
    assert len({entry["id"] for entry in entries}) == 5
    assert [entry["amount_cents"] for entry in entries] == [1000, 2000, -100, -200, 3000]
    assert all(entry["customer_id"] == "customer-1" for entry in entries)


@pytest.mark.parametrize(
    ("page", "page_size"), [(0, 10), (1, 0), (True, 10), (1, 2.5)]
)
def test_r11_paginacao_com_argumentos_invalidos_rejeita(
    tmp_path, page, page_size
):
    conn = connect(tmp_path / "ledger.sqlite")
    init_schema(conn)

    with pytest.raises(ValidationError):
        statement(conn, "customer-1", page, page_size)
