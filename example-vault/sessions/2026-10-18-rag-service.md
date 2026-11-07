---
type: session
project: rag-service
date: "2026-10-18"
touched:
  - "[[retrieval-regression-set]]"
  - "[[checks-beat-checklists]]"
  - "[[rag-service/project|rag-service]]"
---

## Done

- Built the retrieval regression set from the support-ticket notes; CI job gates on recall@10. Baseline 0.71.
- Wrote [[checks-beat-checklists]] after replacing the manual checklist item with the job.

## Decisions

- Threshold is a 2-point drop, not any drop: run-to-run noise on 240 queries is about 1 point.

## Next

- Hybrid search ([[hybrid-bm25-dense]]) against the new baseline.
