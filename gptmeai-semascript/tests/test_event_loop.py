import unittest

from core.event_store import EventStore
from runtime.loop_runner import LoopRunner


class EventLoopTests(unittest.TestCase):
    def test_event_store_is_append_only_and_immutable(self):
        store = EventStore()
        event = {
            "event_id": "event::001",
            "event_type": "ARTIFACT_REGISTERED",
            "artifact_id": "artifact::001",
            "payload": {"state": "ACTIVE", "type": "demo"},
        }

        stored = store.append(event)
        event["payload"]["state"] = "MUTATED"
        stored["payload"]["state"] = "MUTATED_AGAIN"

        self.assertEqual("ACTIVE", store.get_all()[0]["payload"]["state"])
        self.assertEqual(1, store.get_all()[0]["sequence"])

        with self.assertRaises(ValueError):
            store.append({"event_id": "event::001", "event_type": "DUP", "artifact_id": "x"})

    def test_loop_runs_multiple_deterministic_cycles(self):
        runner_a = LoopRunner(EventStore())
        runner_b = LoopRunner(EventStore())

        result_a = runner_a.run_cycles(4)
        result_b = runner_b.run_cycles(4)

        self.assertEqual(result_a, result_b)
        self.assertEqual(4, result_a["cycles"])
        self.assertEqual("STABLE", result_a["loop_status"])
        self.assertGreaterEqual(len(result_a["events"]), 4)


if __name__ == "__main__":
    unittest.main()
