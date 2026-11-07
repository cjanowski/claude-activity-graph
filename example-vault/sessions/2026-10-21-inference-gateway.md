---
type: session
project: inference-gateway
date: "2026-10-21"
touched:
  - "[[prompt-cache-keys]]"
  - "[[streaming-backpressure]]"
  - "[[cache-keys-include-model-version]]"
  - "[[backpressure-at-the-edge]]"
  - "[[reproduce-before-fixing]]"
  - "[[sse-over-websockets]]"
---

## Done

- Fixed the alias-keyed response cache; added a field-classification test, so [[cache-keys-include-model-version]] is `auto: true`.
- Reproduced the slow-client OOM with k6, bounded the stream buffer, propagated backpressure. 3k streams at 410 MB.

## Decisions

- [[sse-over-websockets]]: keep SSE.

## Next

- Provider failover.
