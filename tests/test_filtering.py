from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.data import (
    closest_alternatives,
    filter_tools,
    load_prompts,
    load_quiz,
    load_tools,
    load_workflows,
    resolve_assessment_pool,
    resolve_prompts,
    resolve_tool_results,
    resolve_workflows,
)
from scripts.audit_input_matrix import run_audit


class FilteringTests(unittest.TestCase):
    def setUp(self):
        self.tools = load_tools()

    def test_category_and_specialty_filter(self):
        filters = {"query": "", "category": "Precision Diagnostics", "specialty": "Cardiology", "max_time": 15}
        results = filter_tools(self.tools, filters)
        self.assertTrue(results)
        self.assertTrue(all(item["category"] == "Precision Diagnostics" for item in results))
        self.assertTrue(all("Cardiology" in item["specialties"] for item in results))

    def test_impossible_combination_has_closest_alternatives(self):
        filters = {"query": "nonexistent-unicorn-workflow", "category": "Clinical Documentation", "specialty": "Dentistry", "pricing": "Free", "max_time": 3}
        self.assertEqual(filter_tools(self.tools, filters), [])
        self.assertGreater(len(closest_alternatives(self.tools, filters)), 0)

    def test_search_matches_problem_language(self):
        results = filter_tools(self.tools, {"query": "journal club", "max_time": 15})
        self.assertTrue(any(item["category"] == "Research & Evidence" for item in results))

    def test_resolvers_never_return_an_empty_output(self):
        tools, exact = resolve_tool_results(
            self.tools,
            {"query": "no-such-tool-9z7q", "category": "Clinical Documentation", "max_time": 3},
        )
        self.assertFalse(exact)
        self.assertTrue(tools)

        workflows, exact = resolve_workflows(load_workflows(), "Professional Engagement", "Intermediate")
        self.assertFalse(exact)
        self.assertTrue(workflows)

        prompts, exact = resolve_prompts(load_prompts(), query="no-such-prompt-9z7q")
        self.assertFalse(exact)
        self.assertTrue(prompts)

        questions, supplemented = resolve_assessment_pool(load_quiz(), "Privacy", 20)
        self.assertEqual(len(questions), 20)
        self.assertGreater(supplemented, 0)

    def test_exhaustive_finite_input_matrix_has_no_dead_ends(self):
        report = run_audit()
        for section, result in report.items():
            empty = result.get("zero_output", result.get("zero_or_underfilled_output", 0))
            self.assertEqual(empty, 0, section)


if __name__ == "__main__":
    unittest.main()
