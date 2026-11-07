---
type: task
project: rag-service
repo: "[[rag-service]]"
task_type: feature
status: done
areas: [ingest/chunker.py]
date: 2026-10-19
---

## Goal

Fixed 512-token windows split tables and code blocks mid-way, so answers cited half a procedure.

## Approach

Split on Markdown/HTML heading structure first, then pack sections up to a token budget, never splitting a fenced block or table. Each chunk carries its heading path as a prefix.

## Results log

- 2026-10-19: answer citation accuracy (manual sample of 50) 68% -> 86%. Taught [[chunk-on-structure-not-tokens]].
