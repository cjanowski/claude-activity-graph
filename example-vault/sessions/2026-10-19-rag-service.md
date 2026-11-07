---
type: session
project: rag-service
date: "2026-10-19"
touched:
  - "[[hybrid-bm25-dense]]"
  - "[[chunk-by-headings]]"
  - "[[chunk-on-structure-not-tokens]]"
  - "[[pgvector-over-dedicated-vector-db]]"
---

## Done

- Landed hybrid search with RRF; recall@10 0.71 -> 0.83.
- Rewrote the chunker around heading structure; citation accuracy 68% -> 86%. Lesson [[chunk-on-structure-not-tokens]].

## Decisions

- Stayed on Postgres: [[pgvector-over-dedicated-vector-db]].

## Next

- Reranker latency.
