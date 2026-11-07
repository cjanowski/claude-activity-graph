---
type: decision
project: rag-service
task: "[[hybrid-bm25-dense]]"
date: 2026-10-13
---

**Decision:** Keep vectors in Postgres with pgvector (HNSW) instead of adding a dedicated vector database.

**Options rejected:** a managed vector DB; a self-hosted vector engine alongside Postgres.

**Why:** 1.2M chunks fit comfortably; hybrid search needs the text index and filters next to the vectors; one datastore means one backup and one permission model. Comparison in [[vector-store-comparison]].

**Revisit if:** the corpus passes ~20M chunks or p95 search latency exceeds 150 ms.
