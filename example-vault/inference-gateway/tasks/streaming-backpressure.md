---
type: task
project: inference-gateway
repo: "[[inference-gateway]]"
task_type: bug
status: done
areas: [stream/sse.go, stream/buffer.go]
date: 2026-10-21
---

## Goal

Slow clients on long streams grew gateway memory without bound (OOM at ~3k concurrent streams in a load test).

## Approach

Reproduced it with a k6 scenario of throttled readers ([[reproduce-before-fixing]]). Bounded per-stream buffer; when it fills, pause reading from the provider instead of buffering. Transport stays SSE, per [[sse-over-websockets]].

## Results log

- 2026-10-21: 3k throttled streams hold at 410 MB RSS (was unbounded). Taught [[backpressure-at-the-edge]].
