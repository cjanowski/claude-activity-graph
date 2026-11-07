---
type: decision
project: inference-gateway
task: "[[streaming-backpressure]]"
date: 2026-10-21
---

**Decision:** Keep server-sent events for token streaming.

**Options rejected:** WebSockets; gRPC streaming at the edge.

**Why:** traffic is one-way, SSE passes through every proxy and load balancer we run, and the providers already speak it, so the gateway relays rather than translates. Backpressure is solved in the buffer, not the transport.

**Revisit if:** we need client-to-server messages mid-stream (e.g. tool results).
