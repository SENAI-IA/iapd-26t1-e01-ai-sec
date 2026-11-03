"""Parse e validação de valores monetários em centavos (R01, R02).

Regras da casa:
- Todo valor monetário é um inteiro em centavos.
- Valores em float são rejeitados com ValidationError (R01).
- Valores menores ou iguais a zero são rejeitados (R02).
"""

from app.errors import ValidationError


def parse_amount_cents(value):
    """Valida e retorna um valor monetário em centavos.

    A ser implementado na T2.
    """
    raise NotImplementedError("Implementar em T2")
