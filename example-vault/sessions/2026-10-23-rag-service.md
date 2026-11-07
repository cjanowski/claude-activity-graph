---
type: session
project: rag-service
date: "2026-10-23"
touched:
  - "[[reranker-latency]]"
  - "[[measure-recall-before-reranking]]"
---

## Done

- Reranker p95 1.9 s -> 480 ms by cutting candidates to where recall plateaus. Lesson [[measure-recall-before-reranking]].

## Decisions

- Candidate depth 50, revisit if the corpus doubles.

## Next

- Embedding cache for re-ingest.
