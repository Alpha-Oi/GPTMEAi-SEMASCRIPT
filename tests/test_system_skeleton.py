import unittest

from closed_loop.orchestrator import ClosedEvolutionLoop
from event_store import EventStore, EventValidator, EventWriter
from governance import CanonicalResolver
from risk import RiskClassifier
from snapshot import SnapshotGenerator
from state_engine import StateRebuilder
from validation import DriftDetector


class SystemSkeletonTests(unittest.TestCase):
    def test_event_replay_is_deterministic(self):
        store = EventStore()
        writer = EventWriter(store, EventValidator())
        writer.append(
            {
                "event_id": "event::001",
                "event_type": "ARTIFACT_CREATED",
                "artifact_id": "artifact::demo::001",
                "new_state": "CREATED",
                "payload": {"type": "demo"},
            }
        )
        writer.append(
            {
                "event_id": "event::002",
                "event_type": "STATE_CHANGED",
                "artifact_id": "artifact::demo::001",
                "previous_state": "CREATED",
                "new_state": "ACTIVE",
            }
        )

        rebuilder = StateRebuilder()

        self.assertEqual(
            rebuilder.rebuild(store.read_all()),
            rebuilder.rebuild(reversed(store.read_all())),
        )

    def test_duplicate_event_ids_are_rejected(self):
        store = EventStore()
        writer = EventWriter(store, EventValidator())
        event = {
            "event_id": "event::duplicate",
            "event_type": "ARTIFACT_CREATED",
            "artifact_id": "artifact::demo::duplicate",
            "new_state": "CREATED",
        }

        writer.append(event)

        with self.assertRaises(ValueError):
            writer.append(dict(event))

    def test_risk_classification_is_stable_and_blocks_mutation(self):
        classifier = RiskClassifier()
        proposal = {
            "proposal_id": "proposal::001",
            "actions": [{"operation": "mutate_runtime", "target": "runtime"}],
        }

        first = classifier.classify(proposal)
        second = classifier.classify(proposal)

        self.assertEqual(first, second)
        self.assertEqual("BLOCKED", first["risk_level"])

    def test_governance_selection_is_consistent(self):
        resolver = CanonicalResolver()
        artifacts = [
            {
                "id": "artifact::low",
                "type": "demo",
                "state": "ACTIVE",
                "trust": {"level": "low"},
                "integrity": {"validated": True},
                "balance_metrics": {"final_score": 99},
                "lineage": {"depth": 10},
            },
            {
                "id": "artifact::canonical",
                "type": "demo",
                "state": "ACTIVE",
                "trust": {"level": "high"},
                "integrity": {"validated": True},
                "balance_metrics": {"final_score": 80},
                "lineage": {"depth": 3},
            },
        ]

        self.assertEqual(
            "artifact::canonical",
            resolver.resolve("demo", artifacts)["artifact_id"],
        )

    def test_closed_loop_records_approved_dry_run_action(self):
        loop = ClosedEvolutionLoop()
        result = loop.run(
            {
                "proposal_id": "proposal::dry-run",
                "artifact_type": "system_consistency_contract_layer",
                "actions": [{"operation": "document", "target": "reports/codex"}],
            },
            approval={"approved": True, "approved_by": "local-test"},
        )

        self.assertEqual("COMPLETED", result["status"])
        self.assertTrue(result["runtime"]["dry_run"])
        self.assertEqual("LOW", result["risk"]["risk_level"])
        self.assertGreaterEqual(len(loop.event_store.read_all()), 1)

    def test_drift_detector_detects_snapshot_mismatch(self):
        store = EventStore()
        writer = EventWriter(store, EventValidator())
        writer.append(
            {
                "event_id": "event::drift::001",
                "event_type": "ARTIFACT_CREATED",
                "artifact_id": "artifact::drift",
                "new_state": "ACTIVE",
            }
        )
        snapshot = SnapshotGenerator(StateRebuilder()).generate(store.read_all())
        drifted_snapshot = dict(snapshot)
        drifted_snapshot["state_hash"] = "sha256:not-the-real-hash"

        result = DriftDetector().detect(store.read_all(), drifted_snapshot)

        self.assertTrue(result["drift_detected"])
        self.assertEqual("SNAPSHOT_MISMATCH", result["reason"])


if __name__ == "__main__":
    unittest.main()
