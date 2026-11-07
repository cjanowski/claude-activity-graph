---
type: lesson
project: rag-service
stage: design
auto: false
source: "[[chunk-by-headings]]"
date: 2026-10-19
---

Chunk on document structure first and token budget second; never split a table or code block.

**Why:** fixed windows produced chunks that cited half a procedure. Structure-aware chunks raised citation accuracy from 68% to 86% ([[chunk-by-headings]], 2026-10-19).

**How to apply:** for any new source type in ingestion, define its structural boundaries before choosing a chunk size.
