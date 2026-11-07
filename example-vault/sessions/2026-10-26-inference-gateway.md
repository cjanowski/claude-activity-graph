---
type: session
project: inference-gateway
date: "2026-10-26"
touched:
  - "[[provider-failover]]"
  - "[[reproduce-before-fixing]]"
---

## Done

- Circuit breaker per provider and model; failover only before the first token.
- First attempt failed over mid-stream and spliced two answers together; reverted. Added that case to [[reproduce-before-fixing]].

## Decisions

## Next

- Per-team retry budgets.
