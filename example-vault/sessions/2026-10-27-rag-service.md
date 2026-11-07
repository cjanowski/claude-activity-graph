---
type: session
project: rag-service
date: "2026-10-27"
touched:
  - "[[embedding-cache]]"
  - "[[cache-keys-include-model-version]]"
---

## Done

- Embedding cache prototype keyed on content hash + model revision, reusing the gateway lesson [[cache-keys-include-model-version]]. Re-ingest 41 min -> 6 min.

## Decisions

## Next

- Eviction policy; decide between LRU and keep-all-for-current-revision.
