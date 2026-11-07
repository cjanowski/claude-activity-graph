# Log

Append-only. One line per ingest, query, lint or session, prefixed `## [YYYY-MM-DD] op | title`, so `grep "^## \[" log.md | tail -5` shows the latest.
