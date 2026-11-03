# pagamentos-api

API de pagamentos de brinquedo da Semana 3 (turma IAPD-26T1-E01). Registra pagamentos, faz reembolsos total/parcial, recebe webhooks idempotentes e gera extrato paginado. Sem dinheiro real, sem rede: tudo local, em Python puro, com SQLite em arquivo.

## Stack

- Python 3.10+
- Somente biblioteca padrão (`sqlite3`, `hmac`, `datetime`, ...)
- `pytest` apenas para os testes

Não há framework web: a "API" é um conjunto de funções puras em `app/`, chamadas diretamente pelos testes. Expor em HTTP é opcional e está fora do critério de pronto.

## Estrutura

```
app/
├── api.py        fachada: ponto único de entrada
├── money.py      parse e validação de valores em centavos (R01, R02)
├── db.py         conexão, schema e consultas parametrizadas (R09)
├── payments.py   criar e consultar pagamento (R03)
├── refunds.py    reembolso total e parcial (R04, R05)
├── webhooks.py   verificação de assinatura e idempotência (R06, R07, R08)
├── ledger.py     extrato paginado (R11) e débito com transação (R12)
├── logging_.py   log sem dados sensíveis (R10)
└── errors.py     exceções de domínio (ValidationError, RefundError, AuthError)
tests/            um test_rNN_*.py por requisito
```

## Como rodar

Pré-requisito: Python 3.10 ou superior.

```bash
# 1. (opcional) criar e ativar um ambiente virtual
python -m venv .venv
source .venv/bin/activate

# 2. instalar a dependência de desenvolvimento (pytest)
pip install -r requirements-dev.txt

# 3. rodar a suíte
python -m pytest -q
```

A aplicação em si não tem dependências externas; o `requirements-dev.txt` traz apenas o `pytest`.

## Testes

- Banco temporário por teste (`tmp_path`), sem estado compartilhado.
- Cada requisito (R01 a R12) tem pelo menos um teste nomeado `test_rNN_...`, por exemplo `test_r04_reembolso_maior_que_pago_rejeita`.

## Regras da casa

As convenções da equipe (centavos, SQL parametrizado, UTC, `compare_digest`, PAN nunca em log) estão em [`AGENTS.md`](./AGENTS.md).

## Fora de escopo

Interface web, autenticação de usuário, múltiplas moedas com conversão, rede real com o provedor de pagamento.
