# Regras da casa — pagamentos-api

Steering da equipe. Toda contribuição (humana ou de agente) segue estas regras. Cada regra existe para atender a um requisito e tem pelo menos um teste `test_rNN_...`.

## Stack

- Python 3.10+ e **apenas biblioteca padrão** no código de aplicação. A única dependência de desenvolvimento é o `pytest`.
- Persistência com `sqlite3` em arquivo, **sem ORM**.
- Sem framework web: a API é um conjunto de funções puras em `app/`, chamadas pelos testes.
- O que não estiver decidido no `design.md` a equipe decide e registra aqui.

## Dinheiro é inteiro em centavos (R01, R02)

- Todo valor monetário é um `int` em **centavos**. Nunca `float`.
- Valor em `float` é rejeitado com `ValidationError` (R01).
- Valor menor ou igual a zero é rejeitado com `ValidationError` e **nada é gravado** (R02).
- Toda entrada de valor passa por `money.parse_amount_cents`.

## SQL sempre parametrizado (R09)

- Toda consulta usa parâmetros (`?`). **Nunca** concatenação de string nem f-string para montar SQL.
- Exemplo certo: `cur.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))`.
- Exemplo proibido: `cur.execute(f"SELECT * FROM payments WHERE id = '{payment_id}'")`.

## Tempo em UTC com fuso (R03)

- Timestamps são gravados em UTC **com informação de fuso** (`datetime.now(timezone.utc)`), serializados em ISO 8601.
- Nunca usar `datetime.now()` sem fuso nem horário local.

## Comparação em tempo constante (R08)

- Tokens e assinaturas são comparados **sempre** com `hmac.compare_digest`.
- **Nunca** comparar segredo, token ou assinatura com `==`.

## Dados sensíveis nunca em log (R10)

- Nunca gravar em log o número do cartão (PAN), o token ou a assinatura.
- No máximo os **4 últimos dígitos** do cartão, via `logging_.mask_pan`.

## Erros do domínio

- `ValidationError` — entrada inválida (R01, R02).
- `RefundError` — reembolso inválido, mapeia para HTTP **422** (R04, R05).
- `AuthError` — assinatura/token inválido, mapeia para HTTP **401** (R07).

## Transações e idempotência

- Reembolso valida a soma dos reembolsos anteriores + o novo `<=` valor pago, tudo dentro de uma transação (R04).
- Pagamento `pending` não aceita reembolso (R05).
- Webhook: verificar assinatura **antes** de qualquer gravação; idempotência via `PRIMARY KEY` em `webhook_events.event_id` (R06, R07).
- Débito concorrente usa `BEGIN IMMEDIATE` (ler saldo → gravar saldo → `COMMIT`) para evitar race no read-modify-write (R12).

## Testes

- `pytest` com banco temporário por teste (`tmp_path`), sem estado compartilhado.
- Um teste por requisito, no mínimo, nomeado com o prefixo do requisito: `test_r04_reembolso_maior_que_pago_rejeita`.
- Critério de pronto: `python -m pytest -q` verde com os 12 testes `test_r01..test_r12`.

## Fora de escopo

Interface web, autenticação de usuário, múltiplas moedas com conversão, rede real com o provedor.
