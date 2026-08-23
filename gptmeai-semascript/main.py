"""Bootstrap entrypoint for GPTMEAi-SEMASCRIPT."""

from __future__ import annotations

from core.event_store import EventStore
from runtime.loop_runner import LoopRunner


def main() -> int:
    store = EventStore()
    runner = LoopRunner(store)
    result = runner.run_cycles(4)

    print("GPTMEAi-SEMASCRIPT BOOTSTRAP")
    print(f"cycles={result['cycles']}")
    print(f"loop_status={result['loop_status']}")
    for event in result["events"]:
        print(
            "event "
            f"sequence={event['sequence']} "
            f"id={event['event_id']} "
            f"type={event['event_type']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
