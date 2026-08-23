import unittest

from core.event_store import EventStore
from core.state_engine import StateEngine


class DeterminismTests(unittest.TestCase):
    def test_replay_is_order_deterministic(self):
        store = EventStore()
        store.append(
            {
                "event_id": "event::a",
                "event_type": "ARTIFACT_REGISTERED",
                "artifact_id": "artifact::a",
                "payload": {"type": "demo", "state": "CREATED"},
            }
        )
        store.append(
            {
                "event_id": "event::b",
                "event_type": "STATE_TRANSITION",
                "artifact_id": "artifact::a",
                "payload": {"state": "ACTIVE"},
            }
        )

        engine = StateEngine()
        forward = engine.rebuild(store.get_all())
        reverse = engine.rebuild(reversed(store.get_all()))

        self.assertEqual(forward, reverse)
        self.assertTrue(engine.validate_replay_determinism(store.get_all()))


if __name__ == "__main__":
    unittest.main()
