"""Verificação de assinatura e idempotência de webhooks (R06, R07, R08).

Regras da casa:
- Assinaturas e tokens são comparados com ``hmac.compare_digest`` (R08).
- A assinatura é verificada ANTES de qualquer gravação (R07); assinatura
  inválida lança ``AuthError`` (HTTP 401) e nada é gravado.
- Idempotência via PRIMARY KEY em ``webhook_events.event_id`` (R06): um
  ``event_id`` já processado responde sucesso sem reprocessar.
"""

import hmac
import sqlite3
from datetime import datetime, timezone
from hashlib import sha256

from app.errors import AuthError


def sign_payload(payload: bytes | str, secret: bytes | str) -> str:
    """Calcula a assinatura HMAC-SHA256 de um payload em hexadecimal.

    Utilitário usado tanto para assinar (nos testes/produtor) quanto como
    referência para verificação. Aceita ``str`` ou ``bytes`` e normaliza para
    ``bytes`` usando UTF-8.
    """
    payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
    secret_bytes = secret.encode("utf-8") if isinstance(secret, str) else secret
    return hmac.new(secret_bytes, payload_bytes, sha256).hexdigest()


def verify_signature(
    payload: bytes | str, signature: str, secret: bytes | str
) -> bool:
    """Verifica a assinatura de um payload em tempo constante (R08).

    Returns:
        ``True`` se a assinatura for válida, ``False`` caso contrário.
    """
    expected = sign_payload(payload, secret)
    # R08: comparação em tempo constante, nunca com igualdade direta.
    return hmac.compare_digest(expected, signature)


def handle_webhook(
    conn: sqlite3.Connection,
    event_id: str,
    payload: bytes | str,
    signature: str,
    secret: bytes | str,
) -> dict:
    """Processa um webhook de forma idempotente e autenticada.

    A assinatura é verificada antes de qualquer gravação (R07). Um evento com
    ``event_id`` já processado responde sucesso sem reprocessar (R06). A trava
    de idempotência é o ``PRIMARY KEY`` de ``webhook_events.event_id``.

    Args:
        conn: Conexão com o banco de dados.
        event_id: Identificador único do evento do provedor.
        payload: Corpo do webhook (bytes ou texto).
        signature: Assinatura HMAC-SHA256 em hexadecimal enviada pelo provedor.
        secret: Segredo compartilhado usado para verificar a assinatura.

    Returns:
        Dicionário com ``event_id``, ``status`` (``"processed"`` para o
        primeiro processamento ou ``"duplicate"`` quando já processado antes).

    Raises:
        AuthError: Se a assinatura for inválida (R07). Nada é gravado.
    """
    # R07: verificar a assinatura ANTES de qualquer gravação.
    if not verify_signature(payload, signature, secret):
        raise AuthError("Assinatura de webhook inválida")

    # R06: idempotência. O INSERT com PRIMARY KEY é a trava: se o event_id já
    # existe, o IntegrityError indica que o evento já foi processado.
    try:
        with conn:
            conn.execute(
                "INSERT INTO webhook_events (event_id, received_at) VALUES (?, ?)",
                (event_id, datetime.now(timezone.utc).isoformat()),
            )
    except sqlite3.IntegrityError:
        return {"event_id": event_id, "status": "duplicate"}

    return {"event_id": event_id, "status": "processed"}
