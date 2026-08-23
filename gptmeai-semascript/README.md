# GPTMEAi-SEMASCRIPT Bootstrap

This nested repository is the first executable bootstrap implementation of the
GPTMEAi-SEMASCRIPT governed event-driven system.

It implements a deterministic local loop:

```text
event_store -> state_engine -> logical snapshot -> mental model
-> risk_engine -> governance_engine -> validation_engine
-> execution_boundary -> event_store append
```

Hard rules:

- `EventStore` is the only source of truth.
- State is rebuilt only by deterministic event replay.
- Risk classification runs before governance approval.
- `BLOCKED` and `HIGH` risk proposals cannot execute.
- Validation is mandatory before the execution boundary records an approved action.
- The execution boundary records approved actions only; it performs no external side effects.

Run tests:

```powershell
python -B -m unittest discover -s tests
```

Run the bootstrap loop:

```powershell
python -B main.py
```

The expected loop is deterministic: the same initial empty event log produces
the same events and final state every time.
