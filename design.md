# pagamentos-api: design

Decisões mínimas. O que não está aqui, a equipe decide e registra no steering.

## Stack

Python 3.10+, só biblioteca padrão mais `pytest`. SQLite em arquivo (`sqlite3`, sem ORM). Sem framework web: a "API" é um módulo de funções puras chamado pelos testes (`app/api.py`); expor em HTTP é opcional e fora do critério de pronto.

## Módulos

```
app/
├── money.py      parse e validação de valores em centavos (R01, R02)
├── db.py         conexão, schema, consultas parametrizadas (R09)
├── payments.py   criar pagamento, consultar (R03)
├── refunds.py    reembolso total e parcial (R04, R05)
├── webhooks.py   verificação de assinatura e idempotência (R06, R07, R08)
├── ledger.py     extrato paginado e débito com transação (R11, R12)
└── logging_.py   log sem dados sensíveis (R10)
tests/            um test_rNN_*.py por requisito
```

## Esquema

```
payments(id TEXT PK, customer_id TEXT, amount_cents INTEGER, currency TEXT, status TEXT, created_at TEXT)
refunds(id TEXT PK, payment_id TEXT FK, amount_cents INTEGER, created_at TEXT)
webhook_events(event_id TEXT PK, received_at TEXT)
balances(customer_id TEXT PK, balance_cents INTEGER)
```

## Sequências que merecem cuidado

- Reembolso: `SELECT SUM(amount_cents) FROM refunds WHERE payment_id=?` + novo valor <= `amount_cents` do pagamento, tudo dentro de uma transação.
- Webhook: verificar assinatura (`hmac.compare_digest`) antes de qualquer gravação; `INSERT` em `webhook_events` com `event_id` PK é a trava de idempotência.
- Débito: `BEGIN IMMEDIATE`, ler saldo, gravar saldo, `COMMIT`; o teste de R12 usa threads.

## Erros

Exceções próprias: `ValidationError` (R01, R02), `RefundError` com código 422 (R04, R05), `AuthError` com código 401 (R07).

## Testes

`pytest` com banco temporário por teste (`tmp_path`). O nome do teste carrega o requisito: `test_r04_reembolso_maior_que_pago_rejeita`.