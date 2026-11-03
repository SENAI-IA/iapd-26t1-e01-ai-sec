"""Testes de webhooks: R06 (idempotência), R07 (assinatura inválida), R08
(comparação em tempo constante)."""

import inspect

import pytest

from app.db import connect, init_schema
from app.errors import AuthError
from app.webhooks import handle_webhook, sign_payload, verify_signature


SECRET = "segredo-compartilhado"
PAYLOAD = '{"type": "payment.approved", "amount_cents": 1000}'


def _fresh_conn(tmp_path):
    conn = connect(tmp_path / "payments.sqlite")
    init_schema(conn)
    return conn


def _count_events(conn):
    return conn.execute("SELECT COUNT(*) FROM webhook_events").fetchone()[0]


# ---------------------------------------------------------------------------
# R06 – idempotência: mesmo event_id não processa duas vezes
# ---------------------------------------------------------------------------


def test_r06_webhook_duplicado_nao_processa_de_novo(tmp_path):
    conn = _fresh_conn(tmp_path)
    signature = sign_payload(PAYLOAD, SECRET)

    first = handle_webhook(conn, "evt-1", PAYLOAD, signature, SECRET)
    second = handle_webhook(conn, "evt-1", PAYLOAD, signature, SECRET)

    assert first["status"] == "processed"
    assert second["status"] == "duplicate"
    # Apenas uma linha gravada apesar das duas chamadas.
    assert _count_events(conn) == 1


def test_r06_eventos_distintos_sao_processados(tmp_path):
    conn = _fresh_conn(tmp_path)
    signature = sign_payload(PAYLOAD, SECRET)

    handle_webhook(conn, "evt-1", PAYLOAD, signature, SECRET)
    handle_webhook(conn, "evt-2", PAYLOAD, signature, SECRET)

    assert _count_events(conn) == 2


# ---------------------------------------------------------------------------
# R07 – assinatura inválida rejeita com 401 e não grava nada
# ---------------------------------------------------------------------------


def test_r07_assinatura_invalida_rejeita_e_nao_grava(tmp_path):
    conn = _fresh_conn(tmp_path)

    with pytest.raises(AuthError) as exc:
        handle_webhook(conn, "evt-1", PAYLOAD, "assinatura-falsa", SECRET)

    assert exc.value.code == 401
    # R07: nada é gravado quando a assinatura é inválida.
    assert _count_events(conn) == 0


def test_r07_segredo_errado_rejeita(tmp_path):
    conn = _fresh_conn(tmp_path)
    # Assinatura calculada com um segredo diferente do esperado.
    signature = sign_payload(PAYLOAD, "outro-segredo")

    with pytest.raises(AuthError):
        handle_webhook(conn, "evt-1", PAYLOAD, signature, SECRET)

    assert _count_events(conn) == 0


def test_r07_assinatura_valida_processa(tmp_path):
    conn = _fresh_conn(tmp_path)
    signature = sign_payload(PAYLOAD, SECRET)

    result = handle_webhook(conn, "evt-1", PAYLOAD, signature, SECRET)

    assert result["status"] == "processed"
    assert _count_events(conn) == 1


# ---------------------------------------------------------------------------
# R08 – comparação em tempo constante, nunca com ==
# ---------------------------------------------------------------------------


def _code_lines(func):
    """Retorna as linhas de código de ``func`` sem comentários nem docstring."""
    source = inspect.getsource(func)
    lines = []
    in_docstring = False
    for raw in source.splitlines():
        stripped = raw.strip()
        if stripped.startswith(('"""', "'''")):
            # Alterna o estado de docstring (assume docstring de bloco fechada).
            in_docstring = not in_docstring
            continue
        if in_docstring or stripped.startswith("#"):
            continue
        # Remove comentários inline.
        lines.append(raw.split("#", 1)[0])
    return "\n".join(lines)


def test_r08_usa_compare_digest_nao_igualdade():
    code = _code_lines(verify_signature)
    assert "compare_digest" in code
    # R08: nenhum operador de igualdade no código que compara a assinatura.
    assert "==" not in code


def test_r08_verify_signature_valida_e_invalida():
    good = sign_payload(PAYLOAD, SECRET)
    assert verify_signature(PAYLOAD, good, SECRET) is True
    assert verify_signature(PAYLOAD, "nope", SECRET) is False
