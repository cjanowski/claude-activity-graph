---
type: lesson
project: rag-service
stage: debug
auto: false
source: "[[reranker-latency]]"
date: 2026-10-23
---

Before tuning a reranker, measure recall at the candidate depth; it sets both the ceiling and the right depth.

**Why:** the reranker was scoring 200 candidates when recall plateaued at 50 ([[reranker-latency]], 2026-10-23). Cutting to 50 removed most of the latency with no quality loss.

**How to apply:** first step of any latency or quality work on a retrieve-then-rerank pipeline.
