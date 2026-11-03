# pagamentos-api: requisitos

Projeto da Semana 3 da turma IAPD-26T3. Uma API de pagamentos de brinquedo, pequena o bastante para nascer em 30 minutos e grande o bastante para ter bugs interessantes.

## Contexto

Um marketplace precisa registrar pagamentos, reembolsar total ou parcialmente e receber webhooks do provedor de pagamento. Nada de dinheiro real, nada de rede: tudo local, em Python, com banco SQLite em arquivo.

## Histórias

- Como lojista, quero registrar um pagamento para um cliente, para saber quanto cada um pagou.
- Como atendente, quero reembolsar um pagamento, total ou parcialmente, sem nunca devolver mais do que foi pago.
- Como sistema, quero receber webhooks do provedor sem processar o mesmo evento duas vezes.
- Como auditor, quero consultar o extrato de um cliente em ordem cronológica, com paginação.

## Requisitos (notação EARS)

Formato: `WHEN <evento> THE SYSTEM SHALL <resposta>` (gatilho), `WHILE <estado> THE SYSTEM SHALL <resposta>` (estado), `THE SYSTEM SHALL <resposta>` (sempre). Cada frase vira pelo menos um teste.

| # | Requisito |
|---|---|
| R01 | THE SYSTEM SHALL representar todo valor monetário como inteiro em centavos; valores em float SHALL ser rejeitados com erro de validação. |
| R02 | WHEN um pagamento for criado com valor menor ou igual a zero THE SYSTEM SHALL rejeitar com erro de validação e não gravar nada. |
| R03 | WHEN um pagamento válido for criado THE SYSTEM SHALL gravá-lo com id único, cliente, valor em centavos, moeda, status `approved` e timestamp UTC com fuso. |
| R04 | WHEN um reembolso for solicitado THE SYSTEM SHALL permitir apenas se a soma dos reembolsos anteriores mais o novo for menor ou igual ao valor pago; caso contrário SHALL rejeitar com erro `422` e não alterar nada. |
| R05 | WHILE um pagamento estiver com status `pending` THE SYSTEM SHALL recusar reembolso. |
| R06 | WHEN um webhook chegar com um `event_id` já processado THE SYSTEM SHALL responder sucesso sem processar de novo (idempotência). |
| R07 | WHEN um webhook chegar com assinatura inválida THE SYSTEM SHALL rejeitar com erro `401` e não gravar nada. |
| R08 | THE SYSTEM SHALL comparar tokens e assinaturas com comparação em tempo constante, nunca com `==`. |
| R09 | THE SYSTEM SHALL montar toda consulta SQL com parâmetros (`?`), nunca por concatenação ou f-string. |
| R10 | THE SYSTEM SHALL nunca gravar em log o número do cartão (PAN), o token ou a assinatura; no máximo os 4 últimos dígitos do cartão. |
| R11 | WHEN o extrato de um cliente for consultado com `page` e `page_size` THE SYSTEM SHALL devolver os lançamentos em ordem cronológica, sem repetir nem pular itens entre páginas. |
| R12 | WHEN dois débitos no mesmo saldo forem solicitados ao mesmo tempo THE SYSTEM SHALL garantir que o saldo final seja o mesmo de uma execução sequencial (sem race no read-modify-write). |

## Fora de escopo

Interface web, autenticação de usuário, múltiplas moedas com conversão, rede real com provedor.

## Critérios de pronto

- `python -m pytest -q` verde, com pelo menos um teste por requisito (R01 a R12), nomeado `test_r01_...`.
- README com como rodar e as regras da casa (steering) da equipe.
- Steering da equipe no formato da ferramenta escolhida (ou `AGENTS.md`).