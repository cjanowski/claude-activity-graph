---
type: lesson
project: inference-gateway
stage: build
auto: true
source: "[[prompt-cache-keys]]"
date: 2026-10-20
---

Any cache of model output (or embeddings) keys on the resolved model id and revision, never an alias.

**Why:** an alias-keyed cache served the previous model's answers for a day after an upgrade ([[prompt-cache-keys]], 2026-10-20).

**How to apply:** when adding any cache in front of a model. Enforced in the gateway by a test over request fields (`auto: true`); elsewhere it's a review item.
