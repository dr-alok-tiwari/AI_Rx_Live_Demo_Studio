from pathlib import Path
from io import BytesIO
import json
import math
import re
import sys
import textwrap
import unittest

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.data import load_cases, load_prompts, load_quiz, load_workflows
from components.navigation import PAGES
from components.sample_reports import (
    attachment_ready_prompt,
    build_prompt_sample_pdf,
    build_workflow_sample_pdf,
    complete_workflow_copy_package,
    prompt_pdf_filename,
    workflow_attachment_prompt,
    workflow_pdf_filename,
)


class ContentTests(unittest.TestCase):
    def test_required_content_volumes(self):
        self.assertGreaterEqual(len(load_workflows()), 25)
        self.assertGreaterEqual(len(load_prompts()), 323)
        self.assertGreaterEqual(len(load_cases()), 19)
        self.assertGreaterEqual(len(load_quiz()), 100)

    def test_prompts_are_complete_and_fully_copy_ready(self):
        required = {"specialty", "decision_question", "prompt", "output_structure", "safety", "print_ready"}
        for item in load_prompts():
            self.assertTrue(required.issubset(item))
            self.assertGreater(len(item["prompt"]), 3000)
            self.assertIn("AI VERSUS DOCTOR CHECK", item["prompt"])
            self.assertIn("FINAL SAFETY BLOCK", item["prompt"])
            self.assertTrue(item["print_ready"])

    def test_every_prompt_combination_has_a_complete_pdf_attachment(self):
        filenames = set()
        for item in load_prompts():
            filename = prompt_pdf_filename(item)
            prompt = attachment_ready_prompt(item)
            pdf = build_prompt_sample_pdf(item)
            reader = PdfReader(BytesIO(pdf))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

            self.assertNotIn("[PASTE FICTIONAL", prompt)
            self.assertNotIn("INFORMATION I WILL PROVIDE", prompt)
            self.assertNotRegex(prompt, r"\[[^\]]+\]")
            self.assertIn("ATTACHMENT TO UPLOAD WITH THIS PROMPT", prompt)
            self.assertIn(filename, prompt)
            self.assertTrue(pdf.startswith(b"%PDF-"))
            self.assertGreater(len(pdf), 4_000)
            self.assertGreaterEqual(len(reader.pages), 2)
            self.assertIn(item["category"], text)
            self.assertIn(item["specialty"], text)
            self.assertIn("Qualified-review checklist", text)
            filenames.add(filename)
        self.assertEqual(len(filenames), len(load_prompts()))

    def test_every_live_workflow_has_pdf_prompt_and_one_click_package(self):
        filenames = set()
        for workflow in load_workflows():
            filename = workflow_pdf_filename(workflow)
            prompt = workflow_attachment_prompt(workflow)
            package = complete_workflow_copy_package(workflow)
            pdf = build_workflow_sample_pdf(workflow)
            reader = PdfReader(BytesIO(pdf))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

            self.assertIn(filename, prompt)
            self.assertIn("AI RX COMPLETE LIVE-DEMO PACKAGE", package)
            self.assertIn("SYNTHETIC INPUT", package)
            self.assertIn("PROMPT TO SUBMIT", package)
            self.assertIn("VERIFICATION POINTS", package)
            self.assertTrue(pdf.startswith(b"%PDF-"))
            self.assertIn(workflow["title"], text)
            filenames.add(filename)
        self.assertEqual(len(filenames), len(load_workflows()))

    def test_detailed_prompts_fit_the_three_column_desktop_budget(self):
        for item in load_prompts():
            wrapped_lines = 0
            for paragraph in re.split(r"\n\s*\n", item["prompt"]):
                wrapped_lines += sum(
                    max(1, len(textwrap.wrap(line, width=42, break_long_words=True)))
                    for line in paragraph.splitlines()
                ) + 1
            self.assertLessEqual(math.ceil(wrapped_lines / 3), 56, item["id"])

    def test_cases_follow_ai_versus_doctor_structure(self):
        required = {
            "document_date",
            "patient_information",
            "procedure_information",
            "series_information",
            "ready_prompt",
            "simulated_ai_output",
            "ai_perceived_diagnosis",
            "doctor_actual_diagnosis",
            "tacit_knowledge_cues",
            "decision_support_value",
            "patient_centricity_action",
            "generalisation_note",
            "consent_note",
        }
        for case in load_cases():
            self.assertTrue(required.issubset(case))
            self.assertTrue(case["fictional"])

    def test_take_home_assets_exist(self):
        assets = [
            ROOT / "assets" / "handouts" / "AI_Rx_Copy_Ready_Prompt_Booklet.html",
            ROOT / "assets" / "handouts" / "AI_Rx_Copy_Ready_Prompt_Booklet.txt",
            ROOT / "assets" / "marketing" / "AI_Rx_Workshop_Promo.gif",
            ROOT / "assets" / "presentations" / "AI_Rx_Facilitator_Deck.pptx",
            ROOT / "assets" / "presentations" / "AI_Rx_Participant_Recap.pptx",
        ]
        for asset in assets:
            self.assertTrue(asset.exists(), asset)
            self.assertGreater(asset.stat().st_size, 10_000, asset)

    def test_prompt_visibility_and_clinical_theme_are_locked_in(self):
        css = (ROOT / "styles" / "custom.css").read_text(encoding="utf-8")
        prompt_component = (ROOT / "components" / "prompt_sheet.py").read_text(encoding="utf-8")
        self.assertIn("--saffron: #f59e0b", css)
        self.assertIn("--teal: #2dd4bf", css)
        self.assertIn(".prompt-sheet-dense .prompt-sheet-body", css)
        self.assertIn("column-count: 3", css)
        self.assertIn("FULL PROMPT · ONE-VIEW SHEET", prompt_component)
        self.assertIn("st.iframe", prompt_component)
        self.assertIn("Copy entire prompt", prompt_component)
        self.assertNotIn("st.code(prompt", prompt_component)
        self.assertIn('[data-testid="stCodeBlock"]', css)
        self.assertIn("max-height: none !important", css)
        self.assertIn("overflow: visible !important", css)
        demo_component = (ROOT / "components" / "demo_renderer.py").read_text(encoding="utf-8")
        self.assertIn("Copy complete live-demo package for ChatGPT / lab", demo_component)

    def test_developer_profile_is_complete(self):
        resources = json.loads((ROOT / "data" / "resources.json").read_text(encoding="utf-8"))
        profile = resources["facilitator"]
        self.assertEqual(profile["name"], "Dr. Alok Tiwari")
        self.assertIn("Assistant Professor", profile["role"])
        self.assertIn("Goa Institute of Management", profile["institution"])
        self.assertTrue(profile["bio"])
        self.assertGreaterEqual(len(profile["education"]), 3)
        self.assertEqual(len(profile["research_areas"]), 6)
        self.assertEqual(len(profile["experience"]), 4)
        self.assertIn("decision", profile["teaching_philosophy"].lower())
        self.assertTrue(all(item.get("focus") for item in profile["education"]))
        for key in ("portfolio_url", "linkedin", "github", "orcid"):
            self.assertTrue(profile[key].startswith("https://"), key)

    def test_project_identifiers_are_absent(self):
        checked = [
            ROOT / "README.md",
            ROOT / "FACULTY_FACILITATION_GUIDE.md",
            ROOT / "page_views.py",
            ROOT / "scripts" / "build_content.py",
            ROOT / "data" / "synthetic_cases.json",
        ]
        blocked = (
            "kol" + "kata",
            "workshop" + "_feedback",
            "bhagwa" + " edition",
            "workshop" + " mentor",
        )
        for path in checked:
            text = path.read_text(encoding="utf-8").lower()
            for term in blocked:
                self.assertNotIn(term, text, f"{term!r} found in {path}")

    def test_workflows_are_complete(self):
        required = {"problem", "objective", "preparation", "synthetic_input", "steps", "sample_prompt", "expected_output", "verification_points", "failure_modes", "debrief_questions"}
        for workflow in load_workflows():
            self.assertTrue(required.issubset(workflow))
            self.assertGreaterEqual(len(workflow["steps"]), 8)

    def test_quiz_answers_and_explanations(self):
        for question in load_quiz():
            self.assertIn(question["answer"], question["options"])
            self.assertGreater(len(question["explanation"]), 25)

    def test_navigation_targets_exist(self):
        for _, path in PAGES:
            self.assertTrue((ROOT / path).exists(), path)

    def test_five_simulations_per_modality(self):
        index = json.loads((ROOT / "data" / "image_index.json").read_text(encoding="utf-8"))
        counts = {}
        for item in index:
            counts[item["modality"]] = counts.get(item["modality"], 0) + 1
            self.assertTrue((ROOT / item["path"]).exists())
        self.assertEqual(set(counts.values()), {5})


if __name__ == "__main__":
    unittest.main()
