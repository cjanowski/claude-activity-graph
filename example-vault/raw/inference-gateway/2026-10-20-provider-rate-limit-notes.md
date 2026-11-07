---
type: raw
project: inference-gateway
date: 2026-10-20
---

Pasted provider rate-limit notes, unchanged. (Synthetic example content.)

- Limits are per organisation and per model, in requests and tokens per minute.
- 429 responses carry a retry-after header; 529/503 mean overload, not quota.
