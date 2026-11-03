import pytest

from app.errors import ValidationError
from app.money import parse_amount_cents


def test_r01_valor_inteiro_em_centavos_e_aceito():
    assert parse_amount_cents(1250) == 1250


@pytest.mark.parametrize("value", [1.5, 1.0, 0.01])
def test_r01_float_e_rejeitado(value):
    with pytest.raises(ValidationError):
        parse_amount_cents(value)


@pytest.mark.parametrize("value", [0, -1])
def test_r02_valor_menor_ou_igual_a_zero_e_rejeitado(value):
    with pytest.raises(ValidationError):
        parse_amount_cents(value)


def test_r01_bool_nao_e_aceito_como_inteiro():
    with pytest.raises(ValidationError):
        parse_amount_cents(True)
