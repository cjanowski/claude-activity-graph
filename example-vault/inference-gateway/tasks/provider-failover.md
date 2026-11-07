---
type: task
project: inference-gateway
repo: "[[inference-gateway]]"
task_type: feature
status: in-progress
areas: [route/failover.go, route/health.go]
date: 2026-10-26
---

## Goal

Fail over to a secondary provider on 429/5xx without duplicating side effects or blowing per-team budgets.

## Approach

Circuit breaker per provider and model, failover only before the first streamed token, retry budget per team. Provider limits from [[raw/inference-gateway/2026-10-20-provider-rate-limit-notes|rate-limit notes]].

## Results log

- 2026-10-26: breaker and pre-first-token failover done; budget accounting next. First attempt failed over mid-stream and produced spliced answers; reverted ([[reproduce-before-fixing]]).
