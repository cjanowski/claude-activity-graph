---
type: project
name: inference-gateway
status: active
repo: "[[inference-gateway]]"
---

# inference-gateway

An HTTP gateway in front of several LLM providers: routing, prompt caching, per-team rate limits, streaming, failover, and cost accounting. Go.

- Code: `~/code/inference-gateway`
- Load tests: `loadtest/` (k6)

Stages: design, build, test, deploy.

Tasks: [[prompt-cache-keys]], [[streaming-backpressure]], [[provider-failover]]
