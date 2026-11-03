# pagamentos-api

API de pagamentos de brinquedo da turma IAPD-26T1-E01. O projeto usa Python e SQLite em arquivo; não movimenta dinheiro real nem se conecta a provedores.

## Funcionalidades

- Criar pagamentos aprovados com valores inteiros em centavos.
- Fazer reembolsos parciais ou totais, sem exceder o valor pago.
- Consultar extrato cronológico paginado de pagamentos e reembolsos.
- Debitar saldos com transação SQLite para serializar operações concorrentes.
- Mascarar PAN antes de incluí-lo em logs.

O recebimento e a verificação de webhooks ainda estão pendentes na T5; `app/webhooks.py` permanece como stub.

## Stack e estrutura

- Python 3.10 ou superior e biblioteca padrão na aplicação (`sqlite3`, `datetime`, `hmac` etc.).
- `pytest` como dependência de desenvolvimento.
- Sem framework web: as operações são funções Python em `app/`, chamadas diretamente pelo código e pelos testes.

```text
app/
├── api.py        funções da aplicação reexportadas como fachada
├── money.py      validação de valores em centavos (R01, R02)
├── db.py         conexão, schema e consultas parametrizadas (R09)
├── payments.py   criação e consulta de pagamentos (R03)
├── refunds.py    reembolsos totais e parciais (R04, R05)
├── webhooks.py   stub; implementação planejada na T5 (R06–R08)
├── ledger.py     extrato paginado e débito transacional (R11, R12)
├── logging_.py   máscara do PAN para logs (R10)
└── errors.py     exceções de domínio
tests/            testes dos requisitos implementados
```

## Como instalar e rodar

Pré-requisito: Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
```

A aplicação não precisa instalar dependências externas. No Windows, ative o ambiente com `.venv\Scripts\activate`.

## Testes

Os testes usam bancos SQLite temporários, criados por teste. A cobertura atual inclui validação de valores (R01/R02), pagamentos e reembolsos (R03–R05), SQL parametrizado (R09), logs (R10), extrato (R11) e débito concorrente (R12). R06–R08 dependem da implementação de webhooks na T5.

## Regras do projeto

Os valores são inteiros em centavos; as consultas SQL usam parâmetros; os timestamps incluem fuso UTC; tokens e assinaturas devem ser comparados com `hmac.compare_digest`; dados sensíveis não podem aparecer em logs. As convenções completas estão em [`AGENTS.md`](./AGENTS.md).

## Fora de escopo

Interface web ou API HTTP, autenticação de usuários, conversão entre moedas e conexão real com provedores de pagamento. Webhooks assinados ainda não estão implementados.
