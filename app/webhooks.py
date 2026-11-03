"""Verificação de assinatura e idempotência de webhooks (R06, R07, R08).

Regras da casa:
- Assinaturas e tokens são comparados com ``hmac.compare_digest`` (R08).
- Idempotência via PRIMARY KEY em ``webhook_events.event_id`` (R06).
"""


def handle_webhook(conn, event_id, payload, signature, secret):
    """Processa um webhook de forma idempotente. A ser implementado na T5."""
    raise NotImplementedError("Implementar em T5")
