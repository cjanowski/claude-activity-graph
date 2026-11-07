---
type: task
project: rag-service
repo: "[[rag-service]]"
task_type: performance
status: in-progress
areas: [ingest/embed.py]
date: 2026-10-27
---

## Goal

Re-ingestion re-embeds unchanged chunks. Cache embeddings by content.

## Approach

Key on `sha256(text) + embedding model id + model revision`, the rule from [[cache-keys-include-model-version]] in the gateway project. A model upgrade must miss the cache, not serve stale vectors.

## Results log

- 2026-10-27: prototype cuts a full re-ingest from 41 min to 6 min. Eviction policy still open.
