---
type: project
name: rag-service
status: active
repo: "[[rag-service]]"
---

# rag-service

Retrieval service behind an internal docs assistant: ingestion, hybrid search (BM25 + dense), reranking, and a citation-checked answer step. Python, FastAPI, Postgres with pgvector.

- Code: `~/code/rag-service`
- Tracker: this folder's `tasks/`
- Regression set: `evals/retrieval.jsonl` in the repo, see [[retrieval-regression-set]]

Stages: design, build, test, deploy.

Tasks: [[hybrid-bm25-dense]], [[chunk-by-headings]], [[reranker-latency]], [[retrieval-regression-set]], [[embedding-cache]]
