"""Log sem dados sensíveis (R10).

Regras da casa:
- Nunca gravar PAN, token ou assinatura em log.
- No máximo os 4 últimos dígitos do cartão.
"""


def mask_pan(pan):
    """Retorna somente os quatro últimos dígitos do PAN sem máscara.

    O resultado pode ser incluído em logs sem expor o número completo do
    cartão. Espaços e separadores são removidos antes da máscara.
    """
    if isinstance(pan, bool) or not isinstance(pan, (str, int)):
        raise TypeError("O PAN deve ser informado como texto ou inteiro")

    digits = "".join(character for character in str(pan) if character in "0123456789")
    if not digits:
        raise ValueError("O PAN deve conter ao menos um dígito")

    visible_digits = digits[-4:]
    return "*" * (len(digits) - len(visible_digits)) + visible_digits
