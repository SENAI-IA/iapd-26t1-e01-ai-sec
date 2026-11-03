# pagamentos-api

API local de pagamentos de brinquedo, feita em Python com SQLite. Cria pagamentos, faz reembolsos, consulta extratos paginados e debita saldos com proteção contra concorrência. Não movimenta dinheiro real. Webhooks ainda estão pendentes (T5).

## Rodar

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
```

## Regras principais

- Valores monetários são inteiros em centavos; `float` é rejeitado.
- SQL usa parâmetros (`?`) e timestamps incluem fuso UTC.
- Tokens e assinaturas devem usar `hmac.compare_digest`; PAN, tokens e assinaturas não podem aparecer em logs.
- Veja as convenções completas em [`AGENTS.md`](./AGENTS.md).

## Fora de escopo

Interface web ou HTTP, autenticação de usuários, conversão entre moedas e conexão real com provedores de pagamento.
