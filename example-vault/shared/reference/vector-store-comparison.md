---
type: reference
project: rag-service
date: 2026-10-13
---

Question: does a 1-2M chunk corpus with hybrid search need a dedicated vector database? No. pgvector with HNSW meets the latency target with filters and full-text search in the same query, which a separate store would need a join service for.

Evidence: local benchmark at 1.2M x 1024-d, HNSW m=16, ef_search=80: p95 38 ms, recall@10 0.97 against exact search. Used by [[pgvector-over-dedicated-vector-db]].
