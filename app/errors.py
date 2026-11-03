"""Exceções próprias do domínio.

- ValidationError: entrada inválida (R01, R02).
- RefundError: reembolso inválido, código 422 (R04, R05).
- AuthError: assinatura/token inválido, código 401 (R07).
"""


class ValidationError(Exception):
    """Erro de validação de entrada (R01, R02)."""


class RefundError(Exception):
    """Reembolso inválido (R04, R05). Mapeia para HTTP 422."""

    code = 422


class AuthError(Exception):
    """Assinatura ou token inválido (R07). Mapeia para HTTP 401."""

    code = 401
