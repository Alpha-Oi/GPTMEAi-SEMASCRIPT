# GPTMEAi Adapter

This adapter contains only read-only GPTMEAi client helpers for v0.1.

Allowed:

- `health()`
- `planner_status()`
- `execution_status()`

Forbidden in v0.1:

- mutation endpoints
- execution endpoints
- memory/storage/ledger writes
- secrets or `.env` copying
