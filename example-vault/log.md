# Log

Append-only. One line per ingest, query, lint or session, prefixed `## [YYYY-MM-DD] op | title`, so `grep "^## \[" log.md | tail -5` shows the latest.

## [2026-10-13] create | vault scaffolded, rag-service project
## [2026-10-18] ingest | support ticket notes -> retrieval-regression-set
## [2026-10-18] session | rag-service: regression set in CI, checks-beat-checklists
## [2026-10-19] session | rag-service: hybrid search, structure-aware chunking
## [2026-10-20] create | inference-gateway project
## [2026-10-20] ingest | provider rate-limit notes
## [2026-10-21] session | inference-gateway: cache key fix, streaming backpressure
## [2026-10-23] session | rag-service: reranker latency
## [2026-10-26] session | inference-gateway: failover, first attempt reverted
## [2026-10-27] session | rag-service: embedding cache prototype
## [2026-10-28] session | tooling: dev environment reference, GitHub ingest
## [2026-11-02] rollup | 2026-W44
## [2026-11-07] lint | 36 notes, 0 problems: 
