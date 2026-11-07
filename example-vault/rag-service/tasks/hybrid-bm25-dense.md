---
type: task
project: rag-service
repo: "[[rag-service]]"
task_type: feature
status: done
areas: [retrieval/search.py, sql/indexes.sql]
date: 2026-10-14
---

## Goal

Dense-only retrieval misses exact identifiers (error codes, flag names). Add BM25 and fuse the two.

## Approach

Postgres `tsvector` for BM25-ish scoring next to pgvector, fused with reciprocal rank fusion (k=60). No second datastore, per [[pgvector-over-dedicated-vector-db]].

## Decisions

- RRF over weighted score blending: the two score scales aren't comparable, and RRF needs no tuning.

## Results log

- 2026-10-15: recall@10 on [[retrieval-regression-set]] 0.71 -> 0.83. Identifier queries 0.42 -> 0.90.
