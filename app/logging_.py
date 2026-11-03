"""Log sem dados sensíveis (R10).

Regras da casa:
- Nunca gravar PAN, token ou assinatura em log.
- No máximo os 4 últimos dígitos do cartão.
"""


def mask_pan(pan):
    """Mascara o PAN, mantendo no máximo os 4 últimos dígitos. A ser implementado na T8."""
    raise NotImplementedError("Implementar em T8")
