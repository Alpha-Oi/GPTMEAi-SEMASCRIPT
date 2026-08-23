# GPTMEAI_LIVE_READONLY_STATUS_REPORT.md

- Generated: `2026-05-02T20:07:21.045418Z`
- Project root: `D:\GPTMEAi-SEMASCRIPT`
- GPTMEAi base URL: `http://127.0.0.1:8010`
- Strict mode: `False`
- Status: `UNAVAILABLE`

## Endpoints

### `/health`

- URL: `http://127.0.0.1:8010/health`
- Available: `False`
- HTTP status: `None`
- OK: `False`
- Malformed: `False`
- Duration seconds: `2.044`
- Error: `<urlopen error timed out>`
- Top-level keys: ``

```json
{}
```

### `/planner/status`

- URL: `http://127.0.0.1:8010/planner/status`
- Available: `False`
- HTTP status: `None`
- OK: `False`
- Malformed: `False`
- Duration seconds: `2.002`
- Error: `<urlopen error timed out>`
- Top-level keys: ``

```json
{}
```

### `/execution/status`

- URL: `http://127.0.0.1:8010/execution/status`
- Available: `False`
- HTTP status: `None`
- OK: `False`
- Malformed: `False`
- Duration seconds: `2.002`
- Error: `<urlopen error timed out>`
- Top-level keys: ``

```json
{}
```

## Safety

- This tool performs GET requests only.
- It checks only `/health`, `/planner/status`, and `/execution/status`.
- It is optional for v0.1 local verification.
- It does not start GPTMEAi or enable bridge execution.
