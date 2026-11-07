---
type: task
project: rag-service
repo: "[[rag-service]]"
task_type: infra
status: done
areas: [evals/, .github/workflows/retrieval.yml]
date: 2026-10-18
---

## Goal

A fixed query set with known-relevant chunks, run in CI on every retrieval change.

## Approach

Built from real support questions ([[raw/rag-service/2026-10-18-support-ticket-notes|ticket notes]]), 240 queries, each with 1-3 relevant doc IDs. CI fails if recall@10 drops more than 2 points. Applied [[checks-beat-checklists]]: the "re-run retrieval numbers before merging" checklist item became this job.

## Results log

- 2026-10-18: baseline recall@10 0.71.
