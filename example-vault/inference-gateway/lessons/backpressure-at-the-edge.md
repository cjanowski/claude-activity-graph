---
type: lesson
project: inference-gateway
stage: build
auto: false
source: "[[streaming-backpressure]]"
date: 2026-10-21
---

A streaming proxy propagates backpressure upstream; it never absorbs a slow consumer into its own memory.

**Why:** unbounded buffering per stream OOMed the gateway under throttled clients ([[streaming-backpressure]], 2026-10-21).

**How to apply:** design review of anything that relays a stream: what happens when the reader is slower than the writer?
