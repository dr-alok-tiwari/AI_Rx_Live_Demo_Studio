from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.data import load_tools, validate_catalog


class CatalogTests(unittest.TestCase):
    def test_catalog_has_required_volume_and_unique_valid_records(self):
        tools = load_tools()
        self.assertGreaterEqual(len(tools), 60)
        self.assertEqual(validate_catalog(tools), {})

    def test_required_seed_tools_exist(self):
        names = {tool["name"] for tool in load_tools()}
        required = {"Freed", "Heidi", "Perplexity", "NotebookLM", "monday.com", "xTiles", "Qure.ai qXR/qER"}
        self.assertTrue(required.issubset(names))

    def test_official_urls_are_https_and_dated(self):
        for tool in load_tools():
            self.assertTrue(tool["official_url"].startswith("https://"))
            self.assertRegex(tool["last_verified"], r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
