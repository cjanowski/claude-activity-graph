---
type: lesson
project: shared
stage: debug
auto: false
source: "[[streaming-backpressure]]"
date: 2026-10-21
---

Reproduce a failure on demand before changing code; a fix you can't trigger the bug for is a guess.

**Why:** the throttled-reader load test found the real cause of the OOM in an hour after a day of reading code ([[streaming-backpressure]]). The first failover attempt skipped this and spliced streams ([[provider-failover]]).

**How to apply:** first step of any bug task: write the reproduction, then the fix.
