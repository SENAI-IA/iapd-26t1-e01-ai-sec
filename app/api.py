"""Fachada da API: funções puras chamadas pelos testes.

Reexporta as operações de cada módulo para um ponto único de entrada.
"""

from app.errors import AuthError, RefundError, ValidationError  # noqa: F401
from app.payments import create_payment, get_payment  # noqa: F401
