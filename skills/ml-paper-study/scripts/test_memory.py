"""Regression tests using isolated temporary records, never live learning data."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
import memory as m


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.record = "papers/test/session.json"

    def seed(self, data):
        path = m.target(self.root, self.record)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def check(self, **changes):
        return dict(dict(id="q1", question="Explain", criteria=["Mechanism"], answer_evidence="Explained mechanism", result="pass", assistance="key_step_hint", transfer="new_application", depends_on=["c1"]), **changes)

    def test_merge_retains_unrelated_facts(self):
        m.update(self.root, "profile.json", {"facts": [{"key": "a", "scope": "global", "value": 1}, {"key": "b", "scope": "global", "value": 2}]}, 0)
        result = m.update(self.root, "profile.json", {"facts": [{"key": "a", "scope": "global", "value": 3}]}, 1)
        self.assertEqual([x["value"] for x in result["facts"]], [3, 2])

    def test_v1_migration_preserves_profile(self):
        path = self.root / "profile.json"
        facts = [{"key": "goal", "scope": "global", "value": "理解"}]
        path.write_text(json.dumps({"schema_version": 1, "facts": facts}), encoding="utf-8-sig")
        result = m.update(self.root, "profile.json", {}, 0)
        self.assertEqual(result["facts"], facts)
        self.assertEqual(result["schema_version"], 2)

    def test_legacy_capability_and_readiness_require_review(self):
        self.seed({"schema_version": 1, "capabilities": [{"concept": "attention", "status": "demonstrated_here"}], "checks": [{"result": "pass"}], "readiness": {"status": "ready"}})
        result = m.update(self.root, self.record, {}, 0)
        self.assertTrue(result["capabilities"][0]["id"])
        self.assertEqual(result["capabilities"][0]["status"], "needs_review")
        self.assertEqual(result["checks"][0]["result"], "unverified")
        self.assertEqual(result["readiness"]["status"], "needs_reassessment")
        self.assertEqual(result["legacy_readiness"]["status"], "ready")

    def test_v2_does_not_erase_reassessment(self):
        self.seed({"schema_version": 2, "checks": [self.check(answer_evidence="", result="needs_reassessment")]})
        result = m.update(self.root, self.record, {"phase": "reading"}, 0)
        self.assertEqual(result["checks"][0]["result"], "needs_reassessment")
        self.assertEqual(result["checks"][0]["assistance"], "key_step_hint")

    def test_transitive_correction_and_pending_readiness(self):
        self.seed({"schema_version": 2, "claims": [{"id": "c1", "text": "old"}, {"id": "c2", "depends_on": ["c1"]}], "checks": [self.check()], "artifacts": [{"id": "slide", "status": "ready", "depends_on": ["c2"]}]})
        result = m.update(self.root, self.record, {"id": "fix", "claim_id": "c1", "replacement": "new", "source": "Fig 2", "reason": "Misread"}, 0, correction=True)
        self.assertEqual(result["checks"][0]["result"], "needs_reassessment")
        self.assertEqual(result["artifacts"][0]["status"], "needs_review")
        self.assertEqual(result["corrections"][0]["previous"]["text"], "old")
        result = m.update(self.root, self.record, {"readiness": {"status": "ready"}}, 1)
        self.assertEqual(result["readiness"]["status"], "needs_reassessment")

    def test_duplicate_graph_ids_rejected(self):
        with self.assertRaises(m.MemoryError):
            m.validate({"schema_version": 2, "claims": [{"id": "x"}], "artifacts": [{"id": "x"}]})

    def test_corrupt_file_preserved(self):
        path = self.seed({"schema_version": 2})
        path.write_text("BROKEN", encoding="utf-8")
        with self.assertRaises(ValueError):
            m.update(self.root, self.record, {}, 0)
        self.assertEqual(path.read_text(), "BROKEN")
        self.assertFalse((self.root / ".memory.lock").exists())

    def test_atomic_replace_failure_preserves_record(self):
        path = self.seed({"schema_version": 2, "phase": "before"})
        before = path.read_bytes()
        with patch.object(m.os, "replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                m.update(self.root, self.record, {"phase": "after"}, 0)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(path.parent.glob(".pending-*")))

    def test_concurrent_updates_do_not_silently_overwrite(self):
        def writer(value):
            try:
                return m.update(self.root, self.record, {"phase": value}, 0)["revision"]
            except m.MemoryError:
                return "conflict"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(writer, ["one", "two"]))
        self.assertCountEqual(results, [1, "conflict"])

    def test_foreign_lock_preserved(self):
        lock = self.root / ".memory.lock"
        lock.write_text("other session")
        with self.assertRaises(m.MemoryError):
            with m.locked(self.root, timeout=0):
                self.fail("Acquired occupied lock")
        self.assertEqual(lock.read_text(), "other session")

    def test_path_escape_rejected(self):
        for relative in ("../profile.json", "papers/test/../../escape.json", "random.json"):
            with self.assertRaises(m.MemoryError):
                m.target(self.root, relative)

    def test_false_pass_rejected(self):
        with self.assertRaises(m.MemoryError):
            m.update(self.root, self.record, {"checks": [self.check(answer_evidence="")]}, 0)
        self.assertFalse(m.target(self.root, self.record).exists())


if __name__ == "__main__":
    unittest.main()
