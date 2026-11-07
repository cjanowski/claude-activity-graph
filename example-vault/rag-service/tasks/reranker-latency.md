---
type: task
project: rag-service
repo: "[[rag-service]]"
task_type: performance
status: done
areas: [retrieval/rerank.py, deploy/gpu.yaml]
date: 2026-10-23
---

## Goal

The cross-encoder reranker pushed p95 to 1.9 s. Target under 600 ms.

## Approach

First checked what the reranker buys: measured recall@50 vs recall@10 before touching the model ([[measure-recall-before-reranking]]). Recall@50 was 0.95, so reranking 50 candidates was justified, but 200 was not.

## Results log

- 2026-10-23: candidates 200 -> 50, batch on GPU, fp16. p95 1.9 s -> 480 ms, nDCG@10 unchanged within noise.
