"""Structural regressions; fictional data, no claims about actual papers."""
from copy import deepcopy
import unittest
import graph


def fixture():
    paper = {"id": "p1", "title": "Fictional fixture: EqualMix", "url": None, "version": "test-1", "access": "full_text", "expansion": "not_needed", "stop_reason": "Fixture base is sufficient"}
    target = dict(paper, id="p2", title="Fictional fixture: DynamicMix", expansion="expanded", stop_reason="")
    stage = {"id": "s1", "title": "Given weights", "kind": "pedagogical", "input": "two vectors", "output": "weighted sum", "operation": "sum weighted vectors", "training_note": "fixed numerical illustration", "source_ids": [], "limitations": "weights are fixed"}
    final = dict(stage, id="s2", title="Dynamic weights", kind="target", operation="compute weights then sum", source_ids=["p2"], limitations="fixture scope")
    return {"schema_version": 1, "target": {"title": "Fixture", "scope": "single mixing unit", "source_ids": ["p2"], "status": "complete"}, "papers": [paper, target], "relations": [{"id": "r1", "from": "p2", "to": "p1", "type": "inherits", "status": "verified", "detail": "fixture explicitly replaces equal weighting", "evidence": [{"paper_id": "p2", "locator": "section 1", "note": "changes equal weights"}, {"paper_id": "p1", "locator": "section 1", "note": "defines equal weights"}]}], "stages": [stage, final], "transitions": [{"from": "s1", "to": "s2", "change": "restore weight generation", "reason": "show adaptive weighting", "basis": "teaching_choice", "source_ids": []}], "restoration": [{"item": "fixed weights", "critical": True, "status": "restored", "stage_id": "s2", "note": "weight computation restored"}]}


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture()

    def rejected(self):
        with self.assertRaises(graph.GraphError):
            graph.validate(self.data)

    def test_valid_graph_renders_two_distinct_views(self):
        text = graph.render(self.data)
        self.assertEqual(text.count("```mermaid"), 2)
        self.assertIn("教学简化", text)
        self.assertIn("不表示真实研发历史", text)

    def test_dangling_paper_rejected(self):
        self.data["relations"][0]["to"] = "missing"
        self.rejected()

    def test_unverified_relation_visible(self):
        self.data["relations"][0].update(status="unverified", evidence=[])
        text = graph.render(self.data)
        self.assertIn("未核验", text)
        self.assertIn("-.->", text)

    def test_inheritance_requires_both_endpoint_evidence(self):
        self.data["relations"][0]["evidence"].pop()
        self.rejected()

    def test_metadata_does_not_prove_inheritance(self):
        self.data["papers"][0]["access"] = "metadata_only"
        self.rejected()

    def test_citation_needs_only_citing_endpoint(self):
        self.data["relations"][0]["type"] = "cites"
        self.data["relations"][0]["evidence"].pop()
        graph.validate(self.data)

    def test_teaching_cycle_rejected(self):
        edge = deepcopy(self.data["transitions"][0])
        edge.update({"from": "s2", "to": "s1"})
        self.data["transitions"].append(edge)
        self.rejected()

    def test_shared_source_and_multiple_parents_allowed(self):
        paper = dict(self.data["papers"][1], id="p3", title="Other fixture")
        self.data["papers"].append(paper)
        self.data["relations"].append({"id": "r2", "from": "p3", "to": "p1", "type": "cites", "status": "unverified", "detail": "shared source", "evidence": []})
        graph.validate(self.data)

    def test_critical_deferred_cannot_be_complete(self):
        self.data["restoration"][0]["status"] = "deferred"
        self.rejected()
        self.data["target"]["status"] = "partial"
        graph.validate(self.data)

    def test_cannot_evade_restore_with_not_applicable(self):
        self.data["restoration"][0]["status"] = "not_applicable"
        self.rejected()

    def test_empty_checklist_cannot_claim_complete(self):
        self.data["restoration"] = []
        self.rejected()

    def test_disconnected_stage_cannot_claim_complete(self):
        self.data["stages"].append(dict(self.data["stages"][0], id="s3"))
        self.rejected()

    def test_unsafe_link_rejected_and_labels_escaped(self):
        self.data["papers"][0]["url"] = "javascript:alert(1)"
        self.rejected()
        self.data["papers"][0]["url"] = None
        self.data["stages"][0]["title"] = '<script>"bad"</script>'
        text = graph.render(self.data)
        self.assertNotIn("<script>", text)
        self.assertIn("&lt;script&gt;", text)


if __name__ == "__main__":
    unittest.main()
