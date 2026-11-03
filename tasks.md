# pagamentos-api: tasks

Ordem sugerida. Cada task é pequena o bastante para o agente executar e você conferir com `pytest -q`.

- [x] T1. Criar a estrutura do projeto, `README.md` e o steering da equipe (stack, centavos, sqlite com `?`, UTC, compare_digest, PAN nunca em log). Critério: `pytest -q` roda (zero testes ainda).
- [ ] T2. `money.py` + testes R01 e R02.
- [ ] T3. `db.py` com schema e helper de consulta parametrizada + `payments.py` + teste R03 (e um teste que tenta injeção para R09).
- [ ] T4. `refunds.py` + testes R04 e R05.
- [ ] T5. `webhooks.py` + testes R06, R07 e R08.
- [ ] T6. `ledger.py` extrato paginado + teste R11.
- [ ] T7. `ledger.py` débito com transação + teste R12 (threads).
- [ ] T8. `logging_.py` + teste R10 (capturar log e garantir que o PAN não aparece).
- [ ] T9. Revisar o README: como rodar, regras da casa, o que ficou fora.

Entrega: repositório `iapd-26t3-eNN-pagamentos` na org SENAI-IA, com `pytest -q` verde e os 12 testes `test_r..`.