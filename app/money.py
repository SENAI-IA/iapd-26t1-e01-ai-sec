"""Parse e validação de valores monetários em centavos (R01, R02).

Regras da casa:
- Todo valor monetário é um inteiro em centavos.
- Valores em float são rejeitados com ValidationError (R01).
- Valores menores ou iguais a zero são rejeitados (R02).
"""

from app.errors import ValidationError


def parse_amount_cents(value):
    """Valida e retorna um valor monetário em centavos.

    O valor deve ser um ``int`` positivo expresso em centavos. Floats são
    sempre rejeitados para evitar arredondamentos; ``bool`` também é rejeitado,
    embora seja uma subclasse de ``int`` em Python.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError("O valor deve ser um inteiro em centavos")

    if value <= 0:
        raise ValidationError("O valor deve ser maior que zero")

    return value
