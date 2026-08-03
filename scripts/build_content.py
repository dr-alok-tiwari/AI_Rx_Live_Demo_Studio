"""Generate deterministic workshop data and labelled simulation assets."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
IMAGES = ROOT / "assets" / "sample_medical_images"
ASSETS = ROOT / "assets" / "images"
HANDOUTS = ROOT / "assets" / "handouts"
MARKETING = ROOT / "assets" / "marketing"
VERIFIED = "2026-08-03"


SPECIALTIES = [
    "General Medicine", "Family Medicine", "Radiology", "Cardiology", "Dermatology",
    "Pathology", "Oncology", "Psychiatry", "Paediatrics", "Obstetrics and Gynaecology",
    "Surgery", "Emergency Medicine", "Dentistry", "Ophthalmology", "Orthopaedics",
    "Public Health", "Medical Education", "Hospital Administration", "Research",
]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def write_json(filename: str, value: object) -> None:
    (DATA / filename).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# name, official URL, primary category, purpose, specialty emphasis, access profile
TOOL_SPECS = [
    ("Freed", "https://www.getfreed.ai/", "Clinical Documentation", "Drafts structured clinical notes from clinician–patient conversations.", ["General Medicine", "Family Medicine", "Psychiatry"], "Professional clinical decision support"),
    ("Heidi", "https://www.heidihealth.com/", "Clinical Documentation", "Drafts notes, letters, and summaries from a consultation transcript.", ["General Medicine", "Family Medicine", "Psychiatry"], "Professional clinical decision support"),
    ("Abridge", "https://www.abridge.com/", "Clinical Documentation", "Supports enterprise ambient documentation and related clinical workflows.", ["General Medicine", "Hospital Administration"], "Enterprise/institutional platform"),
    ("Nabla Copilot", "https://www.nabla.com/", "Clinical Documentation", "Creates draft clinical documentation for clinician review and EHR workflows.", ["General Medicine", "Family Medicine"], "Enterprise/institutional platform"),
    ("Suki", "https://www.suki.ai/", "Clinical Documentation", "Supports ambient documentation and voice-assisted clinical work.", ["General Medicine", "Hospital Administration"], "Enterprise/institutional platform"),
    ("Ambience Healthcare", "https://www.ambiencehealthcare.com/", "Clinical Documentation", "Supports health-system documentation and clinical workflow automation.", ["General Medicine", "Hospital Administration"], "Enterprise/institutional platform"),
    ("Doximity Scribe", "https://www.doximity.com/clinicians/scribe", "Clinical Documentation", "Generates customisable draft notes for eligible verified U.S. clinicians.", ["General Medicine", "Family Medicine"], "Professional clinical decision support"),
    ("DeepScribe", "https://www.deepscribe.ai/", "Clinical Documentation", "Provides ambient medical documentation designed for specialty practices.", ["General Medicine", "Oncology"], "Enterprise/institutional platform"),
    ("Augmedix", "https://www.augmedix.com/", "Clinical Documentation", "Supports ambient documentation and related clinician workflows.", ["General Medicine", "Hospital Administration"], "Enterprise/institutional platform"),
    ("ChatGPT", "https://chatgpt.com/", "Patient Communication", "Drafts plain-language explanations, checklists, and educational material from safe input.", ["General Medicine", "Medical Education", "Research"], "Public educational demonstration"),
    ("Claude", "https://claude.ai/", "Patient Communication", "Reworks authorised text into clearer explanations and structured educational drafts.", ["General Medicine", "Medical Education", "Research"], "Public educational demonstration"),
    ("Google Gemini", "https://gemini.google.com/", "Patient Communication", "Drafts multilingual and audience-adjusted educational material for review.", ["General Medicine", "Medical Education"], "Public educational demonstration"),
    ("Microsoft Copilot", "https://copilot.microsoft.com/", "Patient Communication", "Supports general writing, summarisation, and non-clinical productivity tasks.", ["General Medicine", "Hospital Administration"], "Public educational demonstration"),
    ("DeepL", "https://www.deepl.com/", "Patient Communication", "Translates and refines patient-facing text while preserving a clinician review step.", ["General Medicine", "Public Health"], "Public educational demonstration"),
    ("ElevenLabs", "https://elevenlabs.io/", "Patient Communication", "Creates synthetic voice narration for reviewed educational content.", ["Medical Education", "Public Health"], "Public educational demonstration"),
    ("HeyGen", "https://www.heygen.com/", "Patient Communication", "Creates avatar-led educational videos from reviewed scripts.", ["Medical Education", "Public Health"], "Public educational demonstration"),
    ("Synthesia", "https://www.synthesia.io/", "Patient Communication", "Produces presenter-style videos for approved education and training scripts.", ["Medical Education", "Hospital Administration"], "Public educational demonstration"),
    ("Perplexity", "https://www.perplexity.ai/", "Research & Evidence", "Provides a rapid source-linked orientation to a research or clinical question.", ["Research", "General Medicine"], "Public educational demonstration"),
    ("NotebookLM", "https://notebooklm.google.com/", "Research & Evidence", "Summarises authorised source collections for comparison and journal-club preparation.", ["Research", "Medical Education"], "Public educational demonstration"),
    ("Elicit", "https://elicit.com/", "Research & Evidence", "Supports literature discovery and structured evidence extraction.", ["Research"], "Public educational demonstration"),
    ("Consensus", "https://consensus.app/", "Research & Evidence", "Provides research-oriented answers with linked academic sources for checking.", ["Research", "General Medicine"], "Public educational demonstration"),
    ("Scite", "https://scite.ai/", "Research & Evidence", "Shows how papers have been cited to support citation-context review.", ["Research"], "Public educational demonstration"),
    ("SciSpace", "https://scispace.com/", "Research & Evidence", "Supports paper reading, explanation, and literature workflows.", ["Research"], "Public educational demonstration"),
    ("ResearchRabbit", "https://www.researchrabbit.ai/", "Research & Evidence", "Maps related papers and authors to broaden a literature search.", ["Research"], "Public educational demonstration"),
    ("Connected Papers", "https://www.connectedpapers.com/", "Research & Evidence", "Builds a visual graph of papers related to a seed article.", ["Research"], "Public educational demonstration"),
    ("Litmaps", "https://www.litmaps.com/", "Research & Evidence", "Tracks and visualises literature around seed publications.", ["Research"], "Public educational demonstration"),
    ("Semantic Scholar", "https://www.semanticscholar.org/", "Research & Evidence", "Searches scholarly literature and surfaces related research metadata.", ["Research"], "Public educational demonstration"),
    ("PubMed", "https://pubmed.ncbi.nlm.nih.gov/", "Research & Evidence", "Searches biomedical literature through the U.S. National Library of Medicine interface.", ["Research", "General Medicine"], "Public educational demonstration"),
    ("Zotero", "https://www.zotero.org/", "Research & Evidence", "Collects, organises, cites, and shares research sources.", ["Research", "Medical Education"], "Public educational demonstration"),
    ("Rayyan", "https://www.rayyan.ai/", "Research & Evidence", "Supports screening and collaboration in systematic-review workflows.", ["Research"], "Public educational demonstration"),
    ("monday.com", "https://monday.com/", "Workflow & Knowledge", "Organises non-clinical projects, audit tasks, deadlines, and dashboards.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("xTiles", "https://xtiles.app/", "Workflow & Knowledge", "Creates a visual knowledge hub for protocols, reading, teaching, and tasks.", ["Medical Education", "Research"], "Public educational demonstration"),
    ("Notion", "https://www.notion.com/", "Workflow & Knowledge", "Combines notes, databases, projects, and knowledge pages in one workspace.", ["Research", "Medical Education", "Hospital Administration"], "Public educational demonstration"),
    ("ClickUp", "https://clickup.com/", "Workflow & Knowledge", "Tracks tasks, projects, documents, responsibilities, and status.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Trello", "https://trello.com/", "Workflow & Knowledge", "Uses visual boards to track simple departmental and research workflows.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Asana", "https://asana.com/", "Workflow & Knowledge", "Coordinates team projects, responsibilities, milestones, and approvals.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Airtable", "https://www.airtable.com/", "Workflow & Knowledge", "Builds structured trackers and forms for non-clinical operational data.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Miro", "https://miro.com/", "Workflow & Knowledge", "Maps protocols, journeys, ideas, and team decisions on a visual canvas.", ["Hospital Administration", "Medical Education"], "Public educational demonstration"),
    ("Microsoft Loop", "https://loop.cloud.microsoft/", "Workflow & Knowledge", "Creates collaborative workspaces and portable team components.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Todoist", "https://www.todoist.com/", "Workflow & Knowledge", "Manages personal and team tasks, priorities, and reminders.", ["General Medicine", "Research"], "Public educational demonstration"),
    ("Canva", "https://www.canva.com/", "Presentations & Teaching", "Designs patient handouts, professional posts, infographics, and teaching slides.", ["Medical Education", "Public Health"], "Public educational demonstration"),
    ("Gamma", "https://gamma.app/", "Presentations & Teaching", "Creates a first-pass presentation or visual document from a reviewed outline.", ["Medical Education", "Research"], "Public educational demonstration"),
    ("Adobe Express", "https://www.adobe.com/express/", "Presentations & Teaching", "Produces branded educational graphics, short videos, and handouts.", ["Medical Education", "Public Health"], "Public educational demonstration"),
    ("Napkin AI", "https://www.napkin.ai/", "Presentations & Teaching", "Converts text into editable visual explanations for teaching material.", ["Medical Education", "Research"], "Public educational demonstration"),
    ("Beautiful.ai", "https://www.beautiful.ai/", "Presentations & Teaching", "Assists with structured slide design and consistent layouts.", ["Medical Education", "Research"], "Public educational demonstration"),
    ("Tome", "https://tome.app/", "Presentations & Teaching", "Creates narrative presentation drafts; current product access should be rechecked before use.", ["Medical Education"], "Public educational demonstration"),
    ("PowerPoint with Copilot", "https://www.microsoft.com/en-us/microsoft-365/powerpoint", "Presentations & Teaching", "Supports slide drafting and refinement inside eligible Microsoft 365 environments.", ["Medical Education", "Hospital Administration"], "Enterprise/institutional platform"),
    ("Google Slides with Gemini", "https://workspace.google.com/products/slides/", "Presentations & Teaching", "Supports presentation creation in eligible Google Workspace plans.", ["Medical Education", "Hospital Administration"], "Enterprise/institutional platform"),
    ("Mentimeter", "https://www.mentimeter.com/", "Presentations & Teaching", "Runs live polls, word clouds, and audience questions.", ["Medical Education"], "Public educational demonstration"),
    ("Slido", "https://www.slido.com/", "Presentations & Teaching", "Adds live Q&A, polls, and audience interaction to sessions.", ["Medical Education"], "Public educational demonstration"),
    ("Kahoot", "https://kahoot.com/", "Presentations & Teaching", "Runs game-based formative assessments and review activities.", ["Medical Education"], "Public educational demonstration"),
    ("Quizizz", "https://quizizz.com/", "Presentations & Teaching", "Creates self-paced and live formative assessments.", ["Medical Education"], "Public educational demonstration"),
    ("Wooclap", "https://www.wooclap.com/", "Presentations & Teaching", "Runs interactive questions and active-learning activities.", ["Medical Education"], "Public educational demonstration"),
    ("Curipod", "https://curipod.com/", "Presentations & Teaching", "Supports interactive lesson and student-response activities.", ["Medical Education"], "Public educational demonstration"),
    ("Buffer", "https://buffer.com/", "Professional Engagement", "Plans, schedules, and reviews professional social-media content.", ["General Medicine", "Public Health"], "Public educational demonstration"),
    ("Hootsuite", "https://www.hootsuite.com/", "Professional Engagement", "Manages social publishing, monitoring, and team review.", ["Public Health", "Hospital Administration"], "Enterprise/institutional platform"),
    ("Metricool", "https://metricool.com/", "Professional Engagement", "Plans and analyses professional social-media publishing.", ["General Medicine", "Public Health"], "Public educational demonstration"),
    ("SocialPilot", "https://www.socialpilot.co/", "Professional Engagement", "Schedules and coordinates social content across accounts.", ["General Medicine", "Hospital Administration"], "Public educational demonstration"),
    ("Later", "https://later.com/", "Professional Engagement", "Plans visual social content and publishing calendars.", ["General Medicine", "Public Health"], "Public educational demonstration"),
    ("Typefully", "https://typefully.com/", "Professional Engagement", "Drafts and schedules text-led social posts and threads.", ["General Medicine", "Research"], "Public educational demonstration"),
    ("Taplio", "https://taplio.com/", "Professional Engagement", "Supports LinkedIn content planning and publishing.", ["General Medicine", "Research"], "Public educational demonstration"),
    ("Descript", "https://www.descript.com/", "Professional Engagement", "Edits educational video and audio through a transcript-based workflow.", ["Medical Education", "Public Health"], "Public educational demonstration"),
    ("CapCut", "https://www.capcut.com/", "Professional Engagement", "Edits short-form educational videos and captions.", ["Medical Education", "Public Health"], "Public educational demonstration"),
    ("OpusClip", "https://www.opus.pro/", "Professional Engagement", "Creates short clips from longer reviewed educational video.", ["Medical Education", "Public Health"], "Public educational demonstration"),
    ("Grammarly", "https://www.grammarly.com/", "Professional Engagement", "Reviews clarity, grammar, and tone in professional drafts.", ["General Medicine", "Research"], "Public educational demonstration"),
    ("Bitly", "https://bitly.com/", "Professional Engagement", "Creates managed short links and QR codes for approved resources.", ["Public Health", "Medical Education"], "Public educational demonstration"),
    ("Google Trends", "https://trends.google.com/trends/", "Professional Engagement", "Explores public search interest for communication planning, not disease prevalence.", ["Public Health", "Research"], "Public educational demonstration"),
    ("Qure.ai qXR/qER", "https://www.qure.ai/", "Precision Diagnostics", "Supports specified chest X-ray and head CT analysis or triage workflows, depending on product and indication.", ["Radiology", "Emergency Medicine"], "Regulated medical device (specific variants; verify)"),
    ("Aidoc", "https://www.aidoc.com/", "Precision Diagnostics", "Provides enterprise clinical AI and care-coordination solutions for selected imaging workflows.", ["Radiology", "Emergency Medicine"], "Enterprise/institutional platform"),
    ("Lunit INSIGHT", "https://www.lunit.io/en/", "Precision Diagnostics", "Supports selected radiology and oncology image-analysis workflows.", ["Radiology", "Oncology"], "Regulated medical device (specific variants; verify)"),
    ("Gleamer", "https://www.gleamer.ai/", "Precision Diagnostics", "Provides image-analysis assistance for selected radiography workflows.", ["Radiology", "Orthopaedics"], "Regulated medical device (specific variants; verify)"),
    ("Annalise.ai / Harrison.ai", "https://harrison.ai/us/", "Precision Diagnostics", "Represents the current Harrison.ai destination for Annalise imaging products and related clinical AI.", ["Radiology", "Emergency Medicine"], "Enterprise/institutional platform"),
    ("Viz.ai", "https://www.viz.ai/", "Precision Diagnostics", "Supports AI-enabled detection and care coordination for selected conditions and workflows.", ["Radiology", "Cardiology", "Emergency Medicine"], "Enterprise/institutional platform"),
    ("RapidAI", "https://www.rapidai.com/", "Precision Diagnostics", "Provides imaging analysis and workflow coordination for selected neurovascular and vascular care pathways.", ["Radiology", "Emergency Medicine"], "Enterprise/institutional platform"),
    ("HeartFlow", "https://www.heartflow.com/", "Precision Diagnostics", "Provides coronary analysis products used within specified cardiac imaging pathways.", ["Cardiology", "Radiology"], "Regulated medical device (specific variants; verify)"),
    ("VUNO Med", "https://www.vuno.co/", "Precision Diagnostics", "Offers medical AI products across selected imaging and biosignal applications.", ["Radiology", "Cardiology"], "Enterprise/institutional platform"),
    ("Oxipit", "https://oxipit.ai/", "Precision Diagnostics", "Provides radiology workflow and image-analysis products for institutional deployment.", ["Radiology"], "Enterprise/institutional platform"),
    ("AZmed", "https://www.azmed.co/", "Precision Diagnostics", "Provides selected radiology AI products including fracture-related workflows.", ["Radiology", "Orthopaedics"], "Regulated medical device (specific variants; verify)"),
    ("Enlitic", "https://enlitic.com/", "Precision Diagnostics", "Supports imaging data standardisation and healthcare data workflows.", ["Radiology", "Hospital Administration"], "Enterprise/institutional platform"),
    ("SkinVision", "https://www.skinvision.com/", "Precision Diagnostics", "Offers a consumer-facing skin-spot assessment pathway with geography-specific availability.", ["Dermatology"], "Professional clinical decision support"),
    ("DermEngine", "https://www.dermengine.com/", "Precision Diagnostics", "Provides a dermatology imaging, documentation, and analytics platform.", ["Dermatology"], "Enterprise/institutional platform"),
    ("Skin Analytics", "https://skin-analytics.com/", "Precision Diagnostics", "Provides institutional AI-supported skin-cancer pathways in specified settings.", ["Dermatology"], "Regulated medical device (specific variants; verify)"),
    ("AliveCor Kardia", "https://alivecor.com/", "Precision Diagnostics", "Records personal ECGs through compatible Kardia devices and associated services.", ["Cardiology", "General Medicine"], "Regulated medical device (specific variants; verify)"),
    ("Tricog Health", "https://tricog.com/", "Precision Diagnostics", "Supports remote cardiac diagnostics and ECG-enabled care pathways.", ["Cardiology", "Emergency Medicine"], "Enterprise/institutional platform"),
    ("Eko Health", "https://www.ekohealth.com/", "Precision Diagnostics", "Combines digital auscultation hardware with selected AI-enabled cardiac and pulmonary workflows.", ["Cardiology", "General Medicine"], "Regulated medical device (specific variants; verify)"),
    ("Cardiomatics", "https://cardiomatics.com/", "Precision Diagnostics", "Supports ECG analysis workflows for healthcare professionals.", ["Cardiology"], "Enterprise/institutional platform"),
    ("Butterfly Network", "https://www.butterflynetwork.com/", "Precision Diagnostics", "Provides handheld ultrasound hardware, software, and workflow capabilities.", ["Radiology", "Emergency Medicine", "Obstetrics and Gynaecology"], "Regulated medical device (specific variants; verify)"),
    ("GE HealthCare Caption AI / Vscan Air SL", "https://www.gehealthcare.com/en-us/about/newsroom/press-releases/ge-healthcare-introduces-caption-ai-on-vscan-air-sl-wireless-handheld-ultrasound-system-to-help-more-clinicians-capture-diagnostic-quality-cardiac-images", "Precision Diagnostics", "Represents the current GE HealthCare product path for Caption AI-guided cardiac image acquisition.", ["Cardiology", "Emergency Medicine"], "Regulated medical device (specific variants; verify)"),
    ("Clarius", "https://clarius.com/", "Precision Diagnostics", "Provides wireless handheld ultrasound systems for qualified users and selected applications.", ["Radiology", "Emergency Medicine", "Obstetrics and Gynaecology"], "Regulated medical device (specific variants; verify)"),
    ("Zapier", "https://zapier.com/", "Administrative Productivity", "Connects non-clinical apps and automates approved administrative handoffs.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Make", "https://www.make.com/en", "Administrative Productivity", "Builds visual non-clinical automations across approved apps.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Otter", "https://otter.ai/", "Administrative Productivity", "Creates meeting transcripts, summaries, and action items for approved non-clinical meetings.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Fireflies.ai", "https://fireflies.ai/", "Administrative Productivity", "Captures and summarises approved non-clinical meetings.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Calendly", "https://calendly.com/", "Administrative Productivity", "Coordinates scheduling for education, research, and administrative meetings.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Text Blaze", "https://blaze.today/", "Administrative Productivity", "Expands reviewed text snippets for repetitive non-clinical writing.", ["Hospital Administration", "General Medicine"], "Public educational demonstration"),
    ("DocuSign", "https://www.docusign.com/", "Administrative Productivity", "Supports electronic signatures and agreement workflows within approved processes.", ["Hospital Administration", "Research"], "Enterprise/institutional platform"),
    ("Jotform", "https://www.jotform.com/", "Administrative Productivity", "Builds forms and simple workflows for approved non-clinical data collection.", ["Hospital Administration", "Research"], "Public educational demonstration"),
    ("Tally", "https://tally.so/", "Administrative Productivity", "Creates simple forms for workshop, education, and other non-clinical use.", ["Medical Education", "Research"], "Public educational demonstration"),
    ("Power Automate", "https://www.microsoft.com/en-us/power-platform/products/power-automate", "Administrative Productivity", "Automates approved Microsoft-based business processes and task handoffs.", ["Hospital Administration"], "Enterprise/institutional platform"),
    ("Google Workspace with Gemini", "https://workspace.google.com/", "Administrative Productivity", "Supports writing, summarisation, and productivity in eligible Google Workspace environments.", ["Hospital Administration", "Research"], "Enterprise/institutional platform"),
    ("Microsoft 365 Copilot", "https://www.microsoft.com/en-us/microsoft-365-copilot", "Administrative Productivity", "Supports productivity and content work inside eligible Microsoft 365 environments.", ["Hospital Administration", "Research"], "Enterprise/institutional platform"),
]


CATEGORY_META = {
    "Clinical Documentation": {
        "problem": "Clinicians need to convert conversations or dictation into structured documentation without adding unsupported facts.",
        "solution": "The tool can produce a draft that the clinician compares line by line with the source before transfer to an approved record.",
        "inputs": ["Synthetic consultation transcript", "Clinician dictation"],
        "outputs": ["Draft note", "Summary", "Follow-up letter"],
        "use_type": "Clinical",
        "steps": ["Confirm consent and data policy", "Use the synthetic transcript", "Select a note template", "Generate the draft", "Compare with the transcript", "Flag omissions and additions", "Complete clinician review", "Discuss approved EHR transfer"],
    },
    "Patient Communication": {
        "problem": "Clinical explanations may be too technical, long, or poorly matched to a patient’s language and health-literacy level.",
        "solution": "The tool can draft clearer educational language that a clinician checks for accuracy, omissions, warning signs, and cultural fit.",
        "inputs": ["Reviewed clinical facts", "Audience and reading level"],
        "outputs": ["Plain-language explanation", "Multilingual draft", "Patient checklist"],
        "use_type": "Clinical",
        "steps": ["Remove identifiers", "State audience and reading level", "Provide only verified facts", "Request observation–inference separation", "Generate the draft", "Check warnings and escalation", "Review translation and tone", "Approve final patient material"],
    },
    "Research & Evidence": {
        "problem": "Clinicians and researchers need a fast but traceable way to orient themselves to a question or source collection.",
        "solution": "The tool can support discovery or synthesis, while the user opens primary sources and verifies every material claim.",
        "inputs": ["PICO question", "Authorised papers", "Search terms"],
        "outputs": ["Source list", "Evidence table", "Research brief"],
        "use_type": "Non-clinical",
        "steps": ["Frame the question", "Set date and population limits", "Run the search or source-grounded query", "Classify evidence types", "Open primary sources", "Record populations and dates", "Log uncertainty", "Write a checked brief"],
    },
    "Workflow & Knowledge": {
        "problem": "Departmental, education, audit, and research work is often fragmented across email, spreadsheets, and personal notes.",
        "solution": "The tool can organise tasks, responsibilities, status, protocols, and knowledge without storing unapproved patient information.",
        "inputs": ["Synthetic project plan", "Non-clinical tasks"],
        "outputs": ["Board", "Dashboard", "Knowledge hub"],
        "use_type": "Non-clinical",
        "steps": ["Choose a non-clinical template", "Define stages", "Assign roles", "Set deadlines", "Add status fields", "Create a dashboard", "Review overdue escalation", "Check that no PHI is stored"],
    },
    "Presentations & Teaching": {
        "problem": "Doctors need clear teaching and patient-education material but may have limited design time.",
        "solution": "The tool can turn a verified outline into an editable draft that the clinician reviews for accuracy, attribution, accessibility, and audience fit.",
        "inputs": ["Verified outline", "Audience", "Learning objectives"],
        "outputs": ["Slide draft", "Infographic", "Interactive activity"],
        "use_type": "Non-clinical",
        "steps": ["Define audience and objective", "Provide verified source material", "Generate an outline", "Limit slide density", "Add citations", "Check accessibility", "Run a clinical accuracy review", "Rehearse the activity"],
    },
    "Professional Engagement": {
        "problem": "A doctor wants a useful professional presence without disclosing patient information or making promotional clinical claims.",
        "solution": "The tool can help draft, design, schedule, or review evidence-based content under explicit consent, disclosure, and editorial safeguards.",
        "inputs": ["Evidence-based topic", "Audience", "Platform"],
        "outputs": ["Reviewed post", "Visual brief", "Content calendar"],
        "use_type": "Non-clinical",
        "steps": ["Choose audience and platform", "Use an evidence-based topic", "Draft three angles", "Add source links", "Screen clinical claims", "Check consent and conflicts", "Create a visual brief", "Approve before scheduling"],
    },
    "Precision Diagnostics": {
        "problem": "Clinicians need to understand where a medical AI product fits in an imaging or biosignal workflow without assuming public access or universal approval.",
        "solution": "The directory distinguishes modality, user, intended output, access, product status, evidence, and the mandatory human-review step.",
        "inputs": ["Medical image or biosignal in an approved environment"],
        "outputs": ["Product-specific analysis, triage, measurement, or workflow alert"],
        "use_type": "Clinical",
        "steps": ["Confirm intended use", "Verify exact product and indication", "Check image or signal quality", "Run only in an approved environment", "Review visual or numerical output", "Assess false-positive and false-negative risk", "Integrate clinical context", "Document qualified review"],
    },
    "Administrative Productivity": {
        "problem": "Administrative follow-up, meeting actions, forms, and routine communication consume time and are vulnerable to fragmented ownership.",
        "solution": "The tool can support approved non-clinical automation while staff retain review, override, and accountability.",
        "inputs": ["Non-clinical meeting or workflow data"],
        "outputs": ["Action tracker", "Form", "Draft message", "Automation"],
        "use_type": "Non-clinical",
        "steps": ["Select a non-clinical task", "Remove patient data", "Map human owners", "Draft the workflow", "Add approval steps", "Test with synthetic data", "Review exceptions", "Monitor the live process"],
    },
}


def build_tools() -> list[dict]:
    names = [spec[0] for spec in TOOL_SPECS]
    tools: list[dict] = []
    for position, (name, url, category, purpose, specialties, access) in enumerate(TOOL_SPECS):
        meta = CATEGORY_META[category]
        public_demo = access == "Public educational demonstration"
        clinical = meta["use_type"] == "Clinical"
        pricing_type = "Not independently verified"
        pricing_detail = "Current public price not independently verified; check the official pricing page or institutional quote."
        free_tier = "Not independently verified"
        if name == "Freed":
            pricing_type, pricing_detail, free_tier = "Paid", "Vendor page listed AI Scribe starting at USD 39/month on the check date.", "Trial or training offers may apply; verify eligibility."
        elif name == "Doximity Scribe":
            pricing_type, pricing_detail, free_tier = "Free (eligibility restricted)", "Official page states free access for eligible verified U.S. clinicians and medical students.", "Yes, for eligible verified U.S. users."
        elif name == "monday.com":
            pricing_type, pricing_detail, free_tier = "Freemium", "Official page displayed an unlimited-time Free plan; paid tiers vary.", "Yes; plan limits apply."
        elif public_demo:
            pricing_type = "Freemium or paid"
            free_tier = "Availability and limits not independently verified."
        india = "Institutional/region dependent" if not public_demo or category == "Precision Diagnostics" else "Public web access"
        phi = "Do not upload PHI in a workshop or unapproved account."
        phi_suitability = "Institutional assessment required"
        evidence = "Not independently verified for clinical performance in this catalogue record."
        regulatory = "Not independently verified; check exact product, indication, version, and geography."
        if category not in {"Precision Diagnostics", "Clinical Documentation"}:
            regulatory = "Not a diagnostic approval claim; intended here for supervised educational or administrative use."
            evidence = "Utility is workflow-dependent; this record does not establish clinical effectiveness."
        if name == "Qure.ai qXR/qER":
            regulatory = "Qure.ai's official regulatory page lists specific qXR and qER variants as U.S. FDA 510(k)-cleared. Verify the exact product and indication before use."
            evidence = "Official product and evidence pages are available; independent appraisal is still required."
        if name in {"Freed", "Doximity Scribe"}:
            phi_suitability = "Vendor makes U.S. privacy/security claims; institution must verify contract, data flow, geography, and intended use."
        alternatives = [candidate for candidate in names if candidate != name and next(spec[2] for spec in TOOL_SPECS if spec[0] == candidate) == category][:4]
        tools.append({
            "id": slug(name), "name": name, "safe_icon": "AI", "category": category,
            "subcategory": {
                "Clinical Documentation": "AI medical scribe", "Patient Communication": "Language and content assistant",
                "Research & Evidence": "Research workflow", "Workflow & Knowledge": "Work management",
                "Presentations & Teaching": "Visual learning", "Professional Engagement": "Professional communication",
                "Precision Diagnostics": "Clinical AI product", "Administrative Productivity": "Business productivity",
            }[category],
            "purpose": purpose, "problem": meta["problem"], "solution": meta["solution"], "official_url": url,
            "specialties": sorted(set(specialties + (["General Medicine"] if category in {"Patient Communication", "Clinical Documentation"} else []))),
            "intended_users": ["Qualified healthcare professional"] if clinical else ["Healthcare professional", "Educator", "Researcher"],
            "inputs": meta["inputs"], "outputs": meta["outputs"], "use_type": meta["use_type"], "access_type": access,
            "pricing_type": pricing_type, "pricing_detail": pricing_detail, "pricing_currency": "Original vendor currency; see official site",
            "approximate_inr": "Not calculated; exchange rates, taxes, and regional pricing vary.", "pricing_checked": VERIFIED,
            "free_tier": free_tier, "india_availability": india, "public_demo": public_demo, "no_code": True,
            "platforms": ["Web"] + (["Mobile or device support; verify current product"] if category == "Precision Diagnostics" else []),
            "mobile_support": "Check current official product page", "collaboration": "Varies by plan; not independently verified",
            "demo_duration_minutes": [3, 5, 10, 15][position % 4],
            "live_demo_suitability": "Use official interface with synthetic input" if public_demo else "Use a local simulation or vendor walkthrough; no open patient upload",
            "phi_suitability": phi_suitability, "phi_warning": phi, "regulatory_status": regulatory, "evidence_status": evidence,
            "limitations": ["Must not replace diagnosis, prescribing, or professional judgement", "Pricing, access, features, and performance may change", "Local policy, consent, security, and legal review may be required"],
            "demo_steps": meta["steps"],
            "sample_prompt": "Use only the fictional information below. Do not invent facts. State missing information, separate observation from inference, identify uncertainty, and end with a clinician-verification checklist.",
            "alternatives": alternatives, "exports": ["Varies by plan; verify"], "integrations": ["Varies by plan; verify"],
            "geography_notes": "Availability, device status, and permitted use vary by country and institution.", "last_verified": VERIFIED,
            "verification_status": (
                "Official URL could not be fetched automatically; identity retained and manual recheck required"
                if name in {"Heidi", "Scite", "Semantic Scholar", "Microsoft Loop", "Tome"}
                else "Official page reached"
            ),
            "source_urls": [url] + (["https://www.qure.ai/us/regulatory-and-privacy"] if name == "Qure.ai qXR/qER" else []),
        })
    return tools


KEY_WORKFLOWS = {
    "Freed SOAP note and patient summary": ("freed", "Clinical Documentation", 10, "Beginner", "Doctors spend excessive time converting patient conversations into structured documentation.", "Demonstrate a supervised transcript-to-note workflow and detect unsupported additions.", ["Open the official tool in a training account if available", "Prepare the fictional transcript", "Explain consent and local data rules"], "Fictional consultation: Maya, age range 45–55, reports a dry cough for four days and mild fever yesterday. No chest pain or breathlessness. History includes controlled hypertension. Current medicine is listed only as 'one blood-pressure tablet'; drug and dose are unknown. Examination and vital signs were not supplied.", ["Explain consent and data-protection requirements before recording or transcription.", "Use only the supplied fictional transcript; do not record workshop participants.", "Select a SOAP-note template.", "Generate a draft SOAP note.", "Generate a patient-friendly summary with warning signs and when to contact a doctor.", "Generate a referral or follow-up note without inventing examination findings.", "Compare each statement with the transcript.", "Highlight omissions, unsupported additions, and ambiguity around the medicine.", "Complete the physician-verification checklist.", "Discuss EHR transfer only as an approved institutional workflow."], "Create a SOAP-note draft from this fictional transcript. Do not add examination findings, diagnoses, medicines, doses, tests, or plans that are absent. Put unknowns under 'Information to verify'. Then draft a patient summary at approximately Grade 7 reading level with warning signs and a 'not a prescription' notice. End with a clinician-verification checklist.", "A structured draft note plus patient summary, with unknowns visible and no invented examination.", ["Every symptom and time point matches the transcript", "Medicine name and dose remain unknown", "No diagnosis or normal examination was fabricated", "Escalation advice is reviewed by a clinician"], ["Invented vital signs or normal examination", "Unsupported diagnosis", "Medication completion", "Loss of uncertainty during simplification"], ["Which line was hardest to verify?", "Would this draft change your clinical reasoning?", "What must happen before EHR transfer?"]),
    "Heidi consultation-to-document workflow": ("heidi", "Clinical Documentation", 10, "Beginner", "Clinicians need draft notes, follow-up documents, and patient summaries from the same consultation.", "Compare multiple document types against one source transcript.", ["Use a synthetic transcript", "Choose local consent language", "Prepare a note template"], "Fictional follow-up: Arjun, age range 55–65, has home blood-pressure readings between 142–154/86–94 over one week. He reports missing tablets twice. No acute symptoms are stated. Medicine name, clinic reading, examination, and laboratory results are absent.", ["Explain consent and exclude real participant audio.", "Paste the fictional consultation.", "Choose a structured follow-up-note template.", "Generate the note and preserve missing fields.", "Create a patient-friendly adherence summary.", "Draft a follow-up letter without changing the plan.", "Compare all documents with the same source.", "Mark contradictions, additions, and lost uncertainty.", "Complete clinician review.", "Discuss institutional approval before integration or storage."], "Using only this fictional hypertension follow-up, draft a structured note, a plain-language patient summary, and a follow-up letter. Do not infer a diagnosis, treatment change, or normal examination. List missing information and end each output with a verification checklist.", "Three source-consistent drafts with missing clinical information clearly labelled.", ["Readings and adherence details remain exact", "No medicine or dose is inferred", "No treatment change is proposed", "The patient version remains understandable"], ["Treating home readings as a confirmed clinic diagnosis", "Inventing a treatment plan", "Omitting missed doses", "Failing to state red flags"], ["Which output needs the most clinical editing?", "What consent is appropriate locally?", "What should never be copied automatically?"]),
    "Perplexity PICO evidence brief": ("perplexity", "Research & Evidence", 10, "Intermediate", "A doctor needs a fast, source-linked orientation to a clinical or research question.", "Move from PICO to a checked evidence brief without treating generated citations as verified.", ["Prepare a fictional PICO question", "Use date filters", "Have two primary sources ready for inspection"], "PICO: In adults with uncomplicated hypertension in primary care (P), does home blood-pressure monitoring with clinician feedback (I), compared with usual clinic monitoring (C), improve blood-pressure control and adherence (O)?", ["Convert the question into PICO form.", "Search for recent guidelines, systematic reviews, and trials.", "Separate evidence by publication type.", "Inspect every cited source title and date.", "Open at least two primary sources.", "Record population, setting, and outcome definitions.", "Identify disagreement and unresolved uncertainty.", "Draft a short evidence brief.", "Check that citations support each statement.", "State that the brief is orientation, not patient-specific advice."], "Answer the PICO question using recent source-linked evidence. Separate guidelines, systematic reviews, and primary trials. For each claim, provide the source and publication date. State population differences, limitations, and unresolved uncertainty. Do not invent citations.", "A dated, source-linked orientation with evidence types separated and uncertainties visible.", ["Sources exist and titles match", "Claims are supported by opened sources", "Population and setting are relevant", "Recency is not confused with quality"], ["Fabricated or misattributed citations", "Reliance on summaries without opening papers", "Mixing commentary with primary evidence", "Overgeneralising populations"], ["Which citation changed your interpretation?", "What evidence type was missing?", "What would you verify before clinical use?"]),
    "NotebookLM journal-club synthesis": ("notebooklm", "Research & Evidence", 15, "Intermediate", "Doctors have several papers but limited time to prepare a journal club.", "Create a source-grounded comparison while checking every statement against authorised papers.", ["Use openly shareable or authorised papers", "Label each source", "Prepare appraisal questions"], "Authorised source pack: three fictional study summaries on home blood-pressure monitoring, each with different populations, follow-up periods, and outcome definitions.", ["Upload only authorised or openly shareable papers.", "Request a study-by-study summary.", "Extract population, intervention, comparator, outcomes, and limitations.", "Generate a comparison table.", "Identify disagreements across studies.", "Create journal-club questions.", "Generate a presentation outline or audio overview if available.", "Verify all statements against the uploaded documents.", "Record missing information rather than filling gaps.", "Close with an applicability discussion."], "Using only the uploaded sources, create a table with design, population, intervention, comparator, outcomes, follow-up, risk of bias, and limitations. Cite the source name for every row. Identify disagreements without resolving them unless the source does. Draft six journal-club questions.", "A source-labelled comparison table, disagreement map, and journal-club discussion guide.", ["Every cell traces to an uploaded document", "Study designs are classified correctly", "Absence of evidence is not described as no effect", "Limitations remain study-specific"], ["Blending results across sources", "Inventing missing methods", "Treating source-grounded output as clinically correct", "Losing contradictory findings"], ["Where did the studies genuinely disagree?", "What information remained missing?", "Would an audio overview be sufficient for appraisal?"]),
    "monday.com clinic quality-improvement board": ("monday-com", "Workflow & Knowledge", 10, "Beginner", "Clinical teams manage audits, CME work, referrals, or research tasks through scattered emails and spreadsheets.", "Build a synthetic, non-clinical quality-improvement tracker with owners, deadlines, and escalation.", ["Open a training workspace", "Use the synthetic QI template", "Exclude patient-level records"], "Synthetic project: improve completion of a monthly equipment safety checklist across three clinic rooms. Roles are department lead, nursing lead, and biomedical support. No patient data are involved.", ["Select the synthetic clinic quality-improvement template.", "Create stages for planning, test, review, and close-out.", "Add responsibilities, deadlines, and status fields.", "Create checklist-completion and blocker columns.", "Add a non-clinical overdue reminder.", "Build a dashboard for pending actions.", "Demonstrate escalation for overdue work.", "Check that the board contains no identifiers or patient-level data.", "Discuss access control and audit expectations.", "Export a workshop plan."], "Create a board specification for a monthly equipment-safety checklist project. Include stages, owners, due dates, status, evidence link, blocker, and escalation. Use only fictional operational data and no patient records.", "A visible work board with clear ownership, overdue actions, and no patient data.", ["Every task has an owner and due date", "Automation is administrative, not clinical", "No patient-level field exists", "Escalation remains human-owned"], ["Adding patient names to referral tracking", "Automating clinical decisions", "No exception owner", "Dashboard without source tasks"], ["Which status field would support audit?", "Where does human override sit?", "What data should remain outside the board?"]),
    "xTiles specialty knowledge hub": ("xtiles", "Workflow & Knowledge", 10, "Beginner", "Doctors need one visual workspace for protocols, reading lists, ideas, tasks, and teaching material.", "Build a fictional specialty knowledge hub without patient-identifiable records.", ["Open a blank workspace", "Prepare public guideline links", "Use fictional task examples"], "Synthetic General Medicine hub with sections for guidelines, papers to read, teaching cases, protocol checklists, and weekly tasks.", ["Create a visual Specialty Knowledge Hub.", "Add tiles for guidelines, papers, cases, teaching, and tasks.", "Build a weekly learning dashboard.", "Add a protocol checklist.", "Link each guideline to its official source.", "Use fictional teaching cases only.", "Show how the topic can be organised spatially.", "Review sharing permissions.", "Exclude patient-identifiable records.", "Export a screenshot or plan for workshop debrief."], "Design a visual General Medicine knowledge hub with tiles for current guidelines, reading queue, fictional teaching cases, protocol checklist, and weekly learning tasks. Include source and review-date fields. Exclude patient data.", "A navigable visual hub with source dates, review status, and clear separation of knowledge from patient records.", ["Guidelines have sources and review dates", "Tasks are distinct from patient work", "Sharing permissions are explicit", "Cases are fictional"], ["Outdated guidance without review date", "Patient screenshots in teaching tiles", "Unclear ownership", "Mixing draft notes with approved protocols"], ["What belongs in a knowledge hub?", "How will outdated guidance be flagged?", "Which content needs restricted access?"]),
}


ADDITIONAL_WORKFLOWS = [
    ("Plain-language diagnosis explanation", "chatgpt", "Patient Communication"),
    ("Multilingual discharge-instruction draft", "google-gemini", "Patient Communication"),
    ("Visual patient handout", "canva", "Presentations & Teaching"),
    ("Evidence extraction matrix", "elicit", "Research & Evidence"),
    ("Citation-context audit", "scite", "Research & Evidence"),
    ("Literature discovery map", "researchrabbit", "Research & Evidence"),
    ("Reference-library setup", "zotero", "Research & Evidence"),
    ("Seven-day professional content plan", "buffer", "Professional Engagement"),
    ("Ethical LinkedIn post", "taplio", "Professional Engagement"),
    ("Ten-slide CME draft", "gamma", "Presentations & Teaching"),
    ("Live clinical teaching poll", "mentimeter", "Presentations & Teaching"),
    ("Radiology AI product-fit walkthrough", "qure-ai-qxr-qer", "Precision Diagnostics"),
    ("ECG decision-support awareness", "alivecor-kardia", "Precision Diagnostics"),
    ("Ultrasound guidance awareness", "ge-healthcare-caption-ai-vscan-air-sl", "Precision Diagnostics"),
    ("Dermatology image-workflow awareness", "dermengine", "Precision Diagnostics"),
    ("Research-study tracker", "clickup", "Workflow & Knowledge"),
    ("Protocol knowledge base", "notion", "Workflow & Knowledge"),
    ("Department action tracker", "microsoft-365-copilot", "Administrative Productivity"),
    ("Non-clinical workflow automation", "zapier", "Administrative Productivity"),
    ("CME registration form", "jotform", "Administrative Productivity"),
    ("Referral-summary verification", "heidi", "Clinical Documentation"),
    ("Two-scribe note comparison", "freed", "Clinical Documentation"),
    ("Systematic-review screening setup", "rayyan", "Research & Evidence"),
    ("Interactive risk-identification quiz", "kahoot", "Presentations & Teaching"),
    ("Responsible-AI five-step gate", "chatgpt", "Patient Communication"),
]


def build_workflows(tools: list[dict]) -> list[dict]:
    by_id = {tool["id"]: tool for tool in tools}
    workflows: list[dict] = []
    for title, values in KEY_WORKFLOWS.items():
        tool_id, category, duration, level, problem, objective, preparation, synthetic_input, steps, sample_prompt, expected, verification, failures, debrief = values
        workflows.append({"id": slug(title), "tool_id": tool_id, "title": title, "category": category, "duration_minutes": duration, "level": level, "problem": problem, "objective": objective, "preparation": preparation, "synthetic_input": synthetic_input, "steps": steps, "sample_prompt": sample_prompt, "expected_output": expected, "verification_points": verification, "failure_modes": failures, "debrief_questions": debrief, "safety_notice": "Synthetic input only; qualified review required."})
    for number, (title, tool_id, category) in enumerate(ADDITIONAL_WORKFLOWS, start=1):
        tool = by_id[tool_id]
        meta = CATEGORY_META[category]
        workflows.append({
            "id": slug(title), "tool_id": tool_id, "title": title, "category": category,
            "duration_minutes": [3, 5, 10, 15][number % 4], "level": ["Beginner", "Intermediate", "Advanced"][number % 3],
            "problem": tool["problem"], "objective": f"Demonstrate {tool['purpose'].lower()} while preserving source fidelity and human review.",
            "preparation": ["Open the official tool or local simulation", "Prepare synthetic input", "Review institutional and consent requirements"],
            "synthetic_input": f"Fictional workshop material for {title.casefold()}. No real patient identity, image, report, or confidential institutional data is included.",
            "steps": meta["steps"], "sample_prompt": tool["sample_prompt"] + f" Task: {title}. State the intended audience and intended use.",
            "expected_output": f"A reviewable {title.casefold()} draft with sources, unknowns, and responsibility for final approval visible.",
            "verification_points": ["Input is safe and authorised", "Material facts trace to the source", "Uncertainty remains visible", "A qualified person owns final approval"],
            "failure_modes": ["Invented detail", "Loss of uncertainty", "Unverified citation or claim", "Automation without an accountable reviewer"],
            "debrief_questions": ["What did the tool save?", "What required expert correction?", "What policy must be checked before routine use?"],
            "safety_notice": "Synthetic input only; qualified review required.",
        })
    return workflows


PROMPT_TASKS = {
    "Patient-friendly explanation": "Explain the supplied, clinician-verified facts in plain language at the stated reading level. Include key warning signs, when to contact a doctor, and a 'not a prescription' notice.",
    "Discharge-summary simplification": "Simplify the authorised discharge text without changing diagnoses, medicines, doses, dates, follow-up, or warning signs.",
    "Referral summary": "Draft a concise referral summary from the supplied notes, preserving chronology and labelling missing examination, investigation, and treatment details.",
    "Literature search": "Convert the question to PICO, propose a reproducible search string, and separate guidelines, reviews, trials, and commentary.",
    "Journal club": "Create a source-by-source journal-club table and discussion questions using only the supplied authorised papers.",
    "Critical appraisal": "Appraise design, population, bias, measurement, analysis, applicability, and uncertainty without inventing unreported methods or results.",
    "CME presentation": "Create a ten-slide teaching outline from verified sources with one learning objective and one audience interaction per section.",
    "Social-media post": "Draft an evidence-based professional post with source links, disclosure prompts, and no patient story, guarantee, fear-based wording, or personal medical advice.",
    "Professional biography": "Draft a factual professional biography using only the supplied CV facts and mark any missing date, role, award, or link for confirmation.",
    "Clinic workflow": "Map a non-clinical clinic process with roles, decisions, deadlines, exceptions, approvals, and audit points. Exclude patient-identifiable data.",
    "Audit checklist": "Create an auditable checklist from the supplied approved standard, preserving exact thresholds and distinguishing evidence from completion status.",
    "Research protocol": "Draft a protocol outline with question, design, population, measures, analysis, ethics, data governance, risks, and reporting plan.",
    "Clinical teaching": "Create a case discussion using fictional details, staged disclosure, reasoning questions, and a facilitator answer guide.",
    "Case-based MCQs": "Write case-based MCQs from the supplied learning objectives, with one best answer and an explanation for every option.",
    "Image-analysis observation checklist": "Create a modality-specific observation and image-quality checklist. Separate visible observations from clinical inference.",
    "Differential-diagnosis brainstorming": "Organise possible considerations by supporting and opposing features without choosing a final diagnosis or treatment.",
    "Administrative communication": "Draft a concise non-clinical email that states the decision needed, owner, deadline, context, and next step.",
}


PROMPT_SPECIALTIES = SPECIALTIES


PROMPT_OUTPUTS = {
    "Patient-friendly explanation": "A. What this means in plain language; B. What is known; C. What is not yet known; D. What the patient can do now; E. Warning signs; F. When and how to contact the care team; G. Teach-back questions; H. Clinician verification checklist.",
    "Discharge-summary simplification": "A. Reason for admission; B. What was found; C. What was done; D. Medicines exactly as supplied; E. Follow-up; F. Warning signs; G. Patient questions; H. Clinician verification checklist.",
    "Referral summary": "A. Referral question; B. Time-ordered history; C. Relevant positives; D. Relevant negatives; E. Examination; F. Investigations; G. Treatment and response; H. Missing information; I. Urgency rationale; J. Verification checklist.",
    "Literature search": "A. PICO/PEO question; B. Core concepts and synonyms; C. Database-ready search strings; D. Eligibility criteria; E. Evidence hierarchy; F. Screening log; G. Uncertainty; H. Source-verification checklist.",
    "Journal club": "A. Citation; B. Clinical question; C. Design; D. Population; E. Intervention/exposure; F. Comparator; G. Outcomes; H. Results as reported; I. Bias and limitations; J. Applicability; K. Discussion questions.",
    "Critical appraisal": "A. Decision being informed; B. Design fit; C. Selection; D. Measurement; E. Confounding; F. Analysis; G. Result precision; H. Harms; I. Applicability; J. Bottom line with uncertainty.",
    "CME presentation": "A. Audience; B. Learning outcomes; C. Ten-slide narrative; D. source for each claim; E. one specialty case; F. one poll; G. one AI-risk checkpoint; H. take-home decision rule.",
    "Social-media post": "A. Audience; B. communication objective; C. three content angles; D. final platform-specific copy; E. evidence links; F. disclaimer; G. conflict check; H. consent/privacy check; I. visual brief.",
    "Professional biography": "A. 50-word version; B. 120-word version; C. speaker introduction; D. verified expertise; E. selected achievements with relevance; F. facts that need confirmation.",
    "Clinic workflow": "A. Trigger; B. scope; C. roles; D. steps; E. decisions; F. approvals; G. exceptions; H. escalation; I. audit trail; J. measures; K. privacy boundary.",
    "Audit checklist": "A. Standard and source; B. item; C. exact criterion; D. evidence required; E. owner; F. status; G. exception; H. corrective action; I. review date.",
    "Research protocol": "A. question; B. rationale; C. design; D. population; E. variables; F. outcomes; G. sample-size logic; H. analysis; I. missing data; J. bias; K. ethics; L. governance; M. reporting.",
    "Clinical teaching": "A. learner level; B. objectives; C. staged case; D. pause points; E. reasoning questions; F. AI response; G. doctor response; H. tacit cues; I. debrief; J. patient-centred action.",
    "Case-based MCQs": "A. blueprint; B. case stem; C. one best answer; D. plausible options; E. explanation for every option; F. cognitive level; G. ambiguity check; H. source.",
    "Image-analysis observation checklist": "A. modality and body region; B. acquisition/date/series; C. quality; D. systematic observations; E. localisation; F. comparison; G. uncertainty; H. limitations; I. questions for the clinician.",
    "Differential-diagnosis brainstorming": "A. problem representation; B. cannot-miss considerations; C. common considerations; D. supporting features; E. opposing features; F. missing discriminators; G. next information needed; H. uncertainty statement.",
    "Administrative communication": "A. subject; B. decision needed; C. essential context; D. owner; E. deadline; F. requested action; G. escalation route; H. concise closing.",
}


def build_prompts() -> list[dict]:
    prompts = []
    for category, task in PROMPT_TASKS.items():
        for specialty in PROMPT_SPECIALTIES:
            ident = slug(f"{category}-{specialty}")
            prompt = f"""COPY-READY MASTER PROMPT

ROLE AND BOUNDARY
You are assisting a qualified {specialty} professional with {category.casefold()}. You are a decision-support assistant, not the final decision-maker. Do not diagnose, prescribe, approve a procedure, or communicate a clinical decision autonomously.

WORKSHOP TASK
{task}

PATIENT-CENTRIC PURPOSE
Make the output useful for the person receiving care. Preserve dignity, understandable language, patient preferences, access constraints, continuity of care, and appropriate safety-netting. If this is a research or administrative task, explain how the output could affect patient care or service quality.

INFORMATION I WILL PROVIDE
1. Intended audience: [patient / caregiver / clinician / researcher / administrator / public]
2. Intended decision or action: [state exactly what this output will inform]
3. Document or encounter date: [DD-MMM-YYYY]
4. Series, sequence, or comparison dates where relevant: [enter dates or write NOT PROVIDED]
5. Patient or population information: [use fictional, de-identified, openly licensed, or authorised information only]
6. Procedure, investigation, or source information: [modality, body region, test, paper, guideline, workflow, or communication channel]
7. Known facts: [paste only verified facts]
8. Relevant negatives: [paste only documented negatives]
9. Missing or conflicting information already noticed: [list]
10. Local constraints: [specialty, setting, geography, language, resources, institutional policy]
11. Desired reading level or technical depth: [state level]
12. Approved sources: [links, citations, or authorised documents]

NON-NEGOTIABLE RULES
- Use only the supplied material. Do not invent a patient fact, examination, diagnosis, medicine, dose, unit, date, procedure, result, citation, policy, or outcome.
- Preserve negation, laterality, chronology, units, ranges, uncertainty, and who reported each fact.
- Write NOT PROVIDED when a clinically material field is absent. Do not fill gaps with typical values or common practice.
- Separate direct observation, source-supported fact, interpretation, and recommendation under distinct labels.
- Do not convert a possibility into a confirmed diagnosis. If diagnostic considerations are requested, organise them for clinician review and state the missing discriminators.
- Flag time-sensitive or potentially urgent features for qualified review; do not issue an autonomous triage disposition.
- Cite only sources you can identify. If a citation cannot be verified, label it UNVERIFIED and do not use it to support a decision.
- Check whether the content generalises to the stated setting. Name population, language, equipment, workflow, or resource limits that may change applicability.
- Protect privacy. Do not request or reproduce identifiers that are unnecessary for the task.
- Keep the final answer concise enough to use, but do not omit a material fact, warning, limitation, or verification step.

SPECIALTY LENS: {specialty.upper()}
Prioritise the examination, investigation, workflow, and patient-communication issues that a {specialty} professional would reasonably review. Do not pretend that a text-only model can perform a physical examination, interpret an unavailable image or waveform, or replace specialty expertise.

DECISION-SUPPORT METHOD
Step 1: Restate the exact decision this output is meant to support.
Step 2: Build a one-sentence problem representation using only supplied facts.
Step 3: List verified facts, missing information, and contradictions separately.
Step 4: Produce the requested output using the structure below.
Step 5: Run a red-team check for unsupported additions, omitted warning signs, automation bias, non-generalising assumptions, and unclear responsibility.
Step 6: End with what the qualified professional must verify before use.

REQUIRED OUTPUT STRUCTURE
{PROMPT_OUTPUTS[category]}

AI VERSUS DOCTOR CHECK
After the main output, add a table with four rows:
1. What the AI can organise from the supplied data.
2. What the AI may misread or overstate.
3. What tacit clinical or contextual knowledge the doctor contributes.
4. Which final decision must remain with the qualified professional.

FINAL SAFETY BLOCK
End with:
- Missing information that could change the decision.
- Claims or citations requiring verification.
- Patient-centred risks if the output is wrong.
- Clinician verification checklist.
- Statement: "Decision-support draft. Not a diagnosis, prescription, clinical report, or substitute for qualified professional judgement."

MATERIAL TO REVIEW
[PASTE FICTIONAL, DE-IDENTIFIED, OPENLY LICENSED, OR OTHERWISE AUTHORISED MATERIAL HERE]"""
            prompts.append({
                "id": ident, "title": f"{category} — {specialty}", "category": category, "specialty": specialty,
                "use_case": task, "decision_question": f"What decision will this {category.casefold()} output support for {specialty}?",
                "prompt": prompt, "output_structure": PROMPT_OUTPUTS[category],
                "safety": "Qualified review required. Do not upload identifiable patient information.",
                "print_ready": True,
            })
    return prompts


CASE_SPECS = [
    ("Maya", "45–55", "Woman", "General Medicine", "Hypertension follow-up", "Two missed doses and a week of elevated home readings", "Home readings supplied; clinic examination not supplied", "No laboratory results supplied", "Clinical documentation"),
    ("Dev", "35–45", "Man", "General Medicine", "Diabetes counselling", "Irregular meals and uncertainty about carbohydrate portions", "No acute symptoms stated", "Recent HbA1c supplied as a fictional value for teaching", "Patient-friendly explanation"),
    ("Kabir", "55–65", "Man", "Emergency Medicine", "Chest-pain triage", "Pressure-like discomfort with incomplete timing and risk-factor data", "Synthetic triage observations only", "Fictional ECG description; no image", "Identify the AI risk"),
    ("Nila", "25–35", "Woman", "Family Medicine", "Respiratory infection", "Four days of cough and one day of fever; no breathlessness reported", "Vital signs absent", "No imaging supplied", "Documentation verification"),
    ("Ravi", "65–75", "Man", "General Medicine", "Medication-adherence discussion", "Confusion about timing of two medicines; names withheld", "No acute symptoms reported", "No medicine list supplied", "Patient communication"),
    ("Tara", "25–35", "Woman", "Dermatology", "Lesion documentation", "Fictional change in size over three months", "Synthetic ABCDE observations", "No dermoscopy image", "Observation versus inference"),
    ("Ira", "45–55", "Woman", "Radiology", "Radiology report explanation", "Needs a plain-language explanation of a fictional report", "Not applicable", "Synthetic report text with an incidental finding", "Patient-friendly explanation"),
    ("Sameer", "25–35", "Man", "Psychiatry", "Mental-health follow-up", "Reports lower mood and sleep difficulty; risk assessment incomplete", "Mental-status details incomplete", "No investigations", "Missing-information detection"),
    ("Avi", "2–5", "Not specified", "Paediatrics", "Paediatric fever counselling", "Caregiver reports fever and reduced appetite", "Hydration and activity details incomplete", "No test results", "Safety-netting"),
    ("Leela", "25–35", "Woman", "Obstetrics and Gynaecology", "Antenatal patient education", "Requests explanation of routine antenatal tests", "Routine fictional visit", "Synthetic test schedule only", "Health-literacy adaptation"),
    ("JC-01", "Not applicable", "Not applicable", "Research", "Journal-club preparation", "Three fictional study summaries with inconsistent outcome definitions", "Not applicable", "Authorised source pack", "Critical appraisal"),
    ("QI-01", "Not applicable", "Not applicable", "Hospital Administration", "Department quality-improvement project", "Monthly equipment checklist completion is inconsistent", "Not applicable", "Synthetic aggregate completion counts", "Workflow design"),
    ("Noor", "55–65", "Woman", "Cardiology", "Palpitation history", "Intermittent palpitations with incomplete trigger and duration data", "No acute instability stated", "Synthetic single-lead ECG description", "ECG-support awareness"),
    ("Arun", "65–75", "Man", "Ophthalmology", "Retinal report explanation", "Needs an explanation of a fictional screening note", "Visual acuity omitted", "Synthetic retinal-screening text", "Patient communication"),
    ("Mina", "35–45", "Woman", "Oncology", "Follow-up question list", "Wants to prepare questions after receiving a fictional pathology summary", "No new examination", "Synthetic pathology summary", "Question generation"),
    ("Zoya", "15–18", "Woman", "Paediatrics", "Asthma education", "Uncertain inhaler technique and trigger diary", "Technique not directly observed", "No spirometry supplied", "Education checklist"),
    ("Om", "45–55", "Man", "Orthopaedics", "Knee-pain documentation", "Pain after increased walking; red-flag history incomplete", "Synthetic range-of-motion notes", "No imaging supplied", "Clinical documentation"),
    ("ER-02", "35–45", "Not specified", "Emergency Medicine", "Imaging-priority simulation", "Synthetic queue contains three de-identified imaging summaries", "Not applicable", "No actual images", "Automation-bias recognition"),
    ("PH-01", "Not applicable", "Not applicable", "Public Health", "Vaccination handout", "Community clinic needs a multilingual educational draft", "Not applicable", "Approved source facts supplied", "Culturally neutral communication"),
    ("EDU-02", "Not applicable", "Not applicable", "Medical Education", "Clinical-case discussion", "Faculty needs a staged fictional case and poll", "Not applicable", "Learning objectives supplied", "Case-based teaching"),
    ("RES-03", "Not applicable", "Not applicable", "Research", "Systematic-review screening", "Team needs inclusion criteria and conflict resolution", "Not applicable", "Synthetic citations", "Review workflow"),
    ("ADMIN-02", "Not applicable", "Not applicable", "Hospital Administration", "CME event planning", "Tasks and deadlines are split across messages", "Not applicable", "Synthetic planning notes", "Administrative automation"),
]


AI_DOCTOR_CASES = [
    ("Maya", "45–55", "Woman", "General Medicine", "Hypertension follow-up", "Home readings 146–158/88–96 over seven days; two missed doses; no headache, chest pain, dyspnoea, weakness, or visual symptom stated.", "AI labels the pattern as hypertensive urgency and suggests immediate medication escalation.", "Doctor-confirmed teaching conclusion: suboptimally controlled hypertension with non-adherence; no emergency feature in the supplied history. Verify clinic BP, medicine, dose, technique, adherence barriers, examination, and end-organ symptoms before changing treatment.", "The clinician notices absent emergency symptoms, uncertainty about measurement technique, and the patient's difficulty maintaining the schedule."),
    ("Nila", "25–35", "Woman", "Family Medicine", "Acute respiratory symptoms", "Cough for four days, mild fever for one day, nasal symptoms, no breathlessness reported; vital signs and chest examination are not supplied.", "AI selects bacterial sinusitis from duration and fever and drafts an antibiotic plan.", "Doctor-confirmed teaching conclusion: uncomplicated viral upper-respiratory illness is more consistent with the short course; diagnosis and treatment remain provisional until vital signs, examination, risk factors, and progression are assessed.", "The family physician weighs illness trajectory, local epidemiology, access to follow-up, and the reliability of safety-netting."),
    ("Ira", "45–55", "Woman", "Radiology", "Portable chest radiograph review", "Single AP portable image; mild rotation; shallow inspiration; overlapping scapula; no prior image supplied.", "AI calls a right lower-zone opacity probable focal pneumonia.", "Doctor-confirmed teaching conclusion: technically limited film with no confident focal consolidation; apparent density is plausibly positional or overlapping anatomy. Correlate clinically and repeat standard imaging if indicated.", "The radiologist discounts an apparent finding because acquisition quality and projection explain the pattern."),
    ("Noor", "55–65", "Woman", "Cardiology", "Intermittent palpitations", "One consumer single-lead tracing labelled irregular; movement artefact present; symptoms last seconds; no syncope or chest pain; 12-lead ECG not supplied.", "AI reports atrial fibrillation with high confidence.", "Doctor-confirmed teaching conclusion: tracing is non-diagnostic; frequent ectopy or artefact is plausible. Confirm rhythm with a clinically appropriate 12-lead ECG or ambulatory monitor and assess symptoms and risk.", "The cardiologist recognises artefact, symptom–rhythm mismatch, and the limitations of a consumer single-lead strip."),
    ("Tara", "35–45", "Woman", "Dermatology", "Pigmented lesion assessment", "Long-standing waxy lesion with recent irritation after friction; asymmetry in a phone photograph; no dermoscopic image supplied.", "AI ranks melanoma first because of asymmetry and colour variation.", "Doctor-confirmed teaching conclusion: irritated seborrhoeic keratosis is the fictional clinician diagnosis after direct examination and dermoscopy; histopathology is considered if uncertainty remains.", "The dermatologist uses palpation, surface texture, dermoscopic structures, lesion history, and change pattern that a flat photograph does not contain."),
    ("Path-07", "55–65", "Man", "Pathology", "Gastric biopsy interpretation", "Small inflamed biopsy fragment with reactive nuclear enlargement; deeper levels and immunostains initially unavailable.", "AI-generated description overcalls invasive adenocarcinoma from atypia.", "Doctor-confirmed teaching conclusion: reactive epithelial atypia in active inflammation on the complete fictional slide set; no invasion identified. Correlation and additional work-up depend on the full specimen.", "The pathologist integrates architecture across levels, stromal response, inflammation, specimen handling, and threshold for invasion."),
    ("Mina", "45–55", "Woman", "Oncology", "Early post-treatment imaging", "Imaging six weeks after immunotherapy shows modest lesion enlargement with new inflammatory change; symptoms and laboratory results are stable.", "AI labels unequivocal disease progression from size increase alone.", "Doctor-confirmed teaching conclusion: possible treatment-related inflammatory change or pseudoprogression; apply the appropriate response criteria, compare serial imaging, and integrate symptoms before changing therapy.", "The oncologist uses treatment timing, response criteria, symptom trend, biological plausibility, and the consequence of stopping an effective therapy."),
    ("Sameer", "25–35", "Man", "Psychiatry", "Low mood after bereavement", "Sleep difficulty and reduced concentration for three weeks after a loss; function partly preserved; suicidality, mania, substances, and medical causes not fully assessed.", "AI assigns major depressive disorder from symptom keywords.", "Doctor-confirmed teaching conclusion: adjustment-related distress is the fictional working formulation after a complete assessment; continue risk review and reassess duration, severity, function, and alternative explanations.", "The psychiatrist interprets meaning, cultural context, longitudinal pattern, protective factors, function, rapport, and what the patient does not state directly."),
    ("Avi", "6–12 months", "Not specified", "Paediatrics", "Cough and feeding difficulty", "Two days of coryza, wheeze, reduced feeds, wet nappies still present; work of breathing must be examined; no chest radiograph supplied.", "AI recommends pneumonia and antibiotics from cough plus reduced feeding.", "Doctor-confirmed teaching conclusion: viral bronchiolitis is the fictional clinician diagnosis after age-appropriate examination; severity and hydration determine care, not the label alone.", "The paediatrician weighs age, feeding, hydration, respiratory effort, caregiver reliability, and rapid change over time."),
    ("Leela", "25–35", "Woman", "Obstetrics and Gynaecology", "Early pregnancy location", "Positive pregnancy test, mild unilateral discomfort, initial ultrasound inconclusive, beta-hCG series incomplete, haemodynamic status stable in the fictional case.", "AI calls ectopic pregnancy from pain plus an inconclusive scan.", "Doctor-confirmed teaching conclusion: pregnancy of unknown location initially; subsequent fictional serial beta-hCG and ultrasound confirm an early intrauterine pregnancy. Safety-netting remains essential until location is established.", "The obstetrician integrates gestational timing, discriminatory limitations, serial trends, symptoms, scan quality, and the cost of premature labelling."),
    ("Surg-11", "15–25", "Man", "Surgery", "Right lower-quadrant abdominal pain", "Pain migrated from central abdomen; anorexia and focal tenderness; ultrasound equivocal; serial examination shows increasing localised guarding.", "AI favours gastroenteritis because vomiting and a non-diagnostic ultrasound are present.", "Doctor-confirmed teaching diagnosis: acute appendicitis, supported by evolution and the fictional operative finding.", "The surgeon values serial examination and illness evolution more than one equivocal test or a symptom checklist."),
    ("Kabir", "55–65", "Man", "Emergency Medicine", "Evolving chest discomfort", "Initial ECG non-specific; first troponin below threshold; risk factors present; pain recurs; repeat ECG shows new dynamic change and serial troponin rises.", "AI classifies the first snapshot as low risk and suggests discharge.", "Doctor-confirmed teaching diagnosis: non-ST-elevation acute coronary syndrome based on serial change. The initial snapshot was insufficient for disposition.", "The emergency physician uses time, repeat testing, change from baseline, trajectory, and consequence of a missed time-sensitive condition."),
    ("Denta-13", "35–45", "Woman", "Dentistry", "Localised chewing pain", "Sharp pain on release after biting; routine radiograph unrevealing; no spontaneous night pain; cold response is brief.", "AI labels irreversible pulpitis from tooth pain.", "Doctor-confirmed teaching diagnosis: cracked-tooth syndrome in the fictional examination, localised with bite testing and transillumination.", "The dentist uses pain timing, release pattern, targeted provocation, transillumination, occlusion, and limitations of routine radiographs."),
    ("Arun", "55–65", "Man", "Ophthalmology", "New flashes and floaters", "Sudden flashes, new floaters, and a peripheral shadow; central vision preserved; fundus examination not yet documented.", "AI reassures the patient that age-related floaters are common.", "Doctor-confirmed teaching diagnosis: peripheral retinal tear found on urgent dilated examination in the fictional case.", "The ophthalmologist gives high weight to symptom onset and peripheral field description despite preserved central acuity."),
    ("Om", "55–65", "Man", "Orthopaedics", "Acute weight-bearing knee pain", "Sudden medial pain after increased walking; plain radiograph shows mild osteoarthritis; focal bony tenderness and night pain are present.", "AI attributes symptoms to osteoarthritis visible on the radiograph.", "Doctor-confirmed teaching diagnosis: subchondral insufficiency fracture detected on fictional MRI.", "The orthopaedic clinician distinguishes incidental chronic imaging findings from the acute pain pattern and chooses the next modality accordingly."),
    ("PH-16", "Population", "Not applicable", "Public Health", "Apparent outbreak signal", "Reported cases doubled after a new electronic reporting rule; testing volume and denominator also increased; severity and positivity are unchanged.", "AI declares a disease outbreak from the raw case count.", "Doctor-confirmed teaching conclusion: reporting and testing artefact is the leading explanation; verify rate, denominator, geography, time trend, case definition, and severity before escalation.", "The public-health expert understands surveillance-system changes, denominators, ascertainment, and the operational cost of a false alarm."),
    ("EDU-17", "Learner cohort", "Not applicable", "Medical Education", "Diagnostic-reasoning exercise", "Learners receive a staged fictional case; early details favour a common condition, but later data contradict it.", "AI anchors on the first pattern and repeats the original diagnosis after contradictory evidence appears.", "Doctor-confirmed teaching conclusion: the correct response is to reopen the problem representation, name disconfirming evidence, and revise the differential before choosing an answer.", "The educator observes reasoning process, confidence calibration, response to disconfirmation, and whether learners can explain a decision."),
    ("ADMIN-18", "Service", "Not applicable", "Hospital Administration", "Referral-delay dashboard", "Average turnaround appears acceptable, but a small high-risk subgroup repeatedly waits beyond the internal target.", "AI reports that the service meets its goal because the overall mean is within target.", "Doctor-administrator teaching conclusion: aggregate performance masks a safety-relevant tail; stratify by urgency and track the 90th/95th percentile and exception ownership.", "The administrator understands workflow queues, risk stratification, distribution tails, accountability, and patient harm hidden by averages."),
    ("RES-19", "Study population", "Not applicable", "Research", "Observational treatment comparison", "Treated patients have worse unadjusted outcomes but were sicker at baseline; treatment allocation was not random.", "AI concludes the treatment caused harm from the crude association.", "Doctor-researcher teaching conclusion: confounding by indication is a major alternative explanation; specify a causal question, adjust carefully, examine overlap, and avoid causal wording unsupported by design.", "The researcher distinguishes association from causal effect and anticipates why clinical decisions created baseline imbalance."),
]


def build_cases() -> list[dict]:
    cases = []
    for index, (alias, age, sex, specialty, problem, clinical_data, ai_view, doctor_view, tacit) in enumerate(AI_DOCTOR_CASES, start=1):
        document_date = f"{8 + (index % 20):02d}-JUL-2026"
        series = "Current encounter plus prior/serial information stated in the case; missing comparison data are labelled NOT PROVIDED."
        procedure = {
            "Radiology": "AP portable chest radiograph; review projection, rotation, inspiration, exposure, coverage, artefact, and prior imaging.",
            "Cardiology": "Consumer single-lead ECG recording; confirm device, lead, duration, signal quality, symptoms, and clinical ECG plan.",
            "Pathology": "Fictional gastric biopsy slide series; confirm specimen, levels, stain, orientation, artefact, and complete-slide context.",
            "Ophthalmology": "Urgent dilated peripheral retinal examination in the fictional final step.",
            "Obstetrics and Gynaecology": "Serial beta-hCG assessment and transvaginal ultrasound in a time-dependent pathway.",
        }.get(specialty, "Clinical or operational review using only the supplied fictional information; no real procedure is performed by the app.")
        ready_prompt = f"""You are supporting a {specialty} teaching discussion. Use only the fictional case below.

Document date: {document_date}
Specialty: {specialty}
Patient/population: {alias}; age/range: {age}; sex where relevant: {sex}
Presenting problem: {problem}
Procedure or source: {procedure}
Series/comparison: {series}
Case data: {clinical_data}

Task:
1. State the decision that must be made.
2. Build a one-sentence problem representation.
3. Separate verified facts, missing information, and contradictions.
4. List possible considerations without issuing a final diagnosis or treatment plan.
5. Identify cannot-miss risks and the information needed to assess them.
6. Explain what may not generalise across settings, populations, equipment, or workflows.
7. Provide a patient-centred communication plan and safety-netting topics for clinician review.
8. End with an AI-versus-doctor table showing AI contribution, AI blind spots, tacit clinical knowledge, and the decision reserved for the qualified professional.

Do not invent examination findings, results, diagnoses, medicines, doses, procedures, citations, or outcomes. Label absent information NOT PROVIDED. Output is a decision-support draft, not a clinical report."""
        cases.append({
            "id": f"case-{index:02d}-{slug(alias)}", "patient_alias": alias, "age_range": age, "sex": sex,
            "specialty": specialty, "document_date": document_date, "presenting_problem": problem,
            "patient_information": f"Alias {alias}; age/range {age}; sex where clinically relevant {sex}. Entirely fictional.",
            "procedure_information": procedure, "series_information": series, "relevant_history": clinical_data,
            "examination_summary": "Only information explicitly stated in the case is available; all other examination fields are NOT PROVIDED.",
            "investigation_data": procedure, "learning_objective": "AI versus Doctor decision support",
            "ready_prompt": ready_prompt, "simulated_ai_output": ai_view,
            "ai_perceived_diagnosis": ai_view, "doctor_actual_diagnosis": doctor_view,
            "tacit_knowledge_cues": tacit,
            "decision_support_value": "AI can organise the timeline, surface missing data, and generate questions. It must not own the final diagnosis, treatment, procedure, disposition, or patient communication.",
            "patient_centricity_action": "Explain uncertainty, preserve the patient's priorities and context, state what will happen next, and provide clinician-reviewed safety-netting.",
            "generalisation_note": "This case is intentionally specific enough to teach reasoning. Users must adapt it to local prevalence, population, language, equipment, resources, policy, and scope of practice.",
            "consent_note": "Literature-only reminder: use fictional, published, de-identified, openly licensed, or otherwise authorised teaching material. This app does not generate a clinical consent form.",
            "suitable_ai_tools": ["ChatGPT", "Heidi", "Perplexity"],
            "expected_workshop_output": "Ready prompt, supervised AI draft, doctor-confirmed teaching conclusion, tacit-knowledge discussion, and patient-centred next action.",
            "safety_considerations": "Fictional case. Teaching conclusions require local clinical review before delivery.",
            "fictional": True,
        })
    return cases


QUIZ_THEMES = [
    ("Privacy", "A participant proposes uploading a discharge summary containing name and phone number to a public AI account. What is the safest first action?", ["Upload it and delete the chat later", "Remove or avoid the identifiable data and use an approved workflow", "Ask the AI not to remember it", "Convert it to a PDF"], "Remove or avoid the identifiable data and use an approved workflow", "A prompt cannot substitute for data minimisation, approval, and an appropriate processing environment."),
    ("Hallucination", "An AI-generated note contains a normal chest examination that was never stated. How should it be handled?", ["Keep it because normal findings are common", "Delete or correct it and compare the full note with the source", "Mark it as AI-generated and keep it", "Send it directly to the EHR"], "Delete or correct it and compare the full note with the source", "An unsupported examination is a fabricated clinical fact and signals the need for complete source comparison."),
    ("Evidence", "A source-linked answer cites a recent trial. What is the next best step?", ["Accept the answer because it has a citation", "Open the trial and verify population, methods, outcome, and claim", "Prefer the newest source automatically", "Use the answer as patient-specific advice"], "Open the trial and verify population, methods, outcome, and claim", "A linked citation can still be wrong, irrelevant, or misinterpreted."),
    ("Automation bias", "A radiology AI flag conflicts with the clinician's review and clinical context. What is appropriate?", ["Follow AI because it is objective", "Ignore AI permanently", "Reassess image quality, intended use, context, and escalation pathway", "Average the two opinions"], "Reassess image quality, intended use, context, and escalation pathway", "AI output is decision support. Conflicts require structured review, not automatic acceptance or dismissal."),
    ("Consent", "Before demonstrating ambient scribing with audio, what is required?", ["A general workshop disclaimer only", "Explicit consent and an approved data workflow; synthetic text is safer for a demo", "No action if names are omitted", "A paid account"], "Explicit consent and an approved data workflow; synthetic text is safer for a demo", "Audio can contain identifiers and sensitive information even when names are not intentionally spoken."),
    ("Communication", "A patient handout is accurate but omits warning signs and escalation advice. What should the clinician do?", ["Publish it because the diagnosis is correct", "Add clinically reviewed warning signs and when to seek care", "Ask the patient to search online", "Add more graphics instead"], "Add clinically reviewed warning signs and when to seek care", "A readable handout still needs safe, context-appropriate escalation information."),
    ("Regulation", "A vendor says its company has FDA-cleared products. What can you infer about the exact tool shown?", ["Every company product is cleared", "The tool is cleared in India", "Nothing specific until product, version, indication, and geography are verified", "It can diagnose autonomously"], "Nothing specific until product, version, indication, and geography are verified", "Regulatory status attaches to a specific product and intended use, not a company name in general."),
    ("Workflow", "Which is the safest first automation for a workshop?", ["Automated diagnosis message", "Unreviewed discharge instruction", "Overdue reminder for a fictional CME planning task", "Automatic medicine change"], "Overdue reminder for a fictional CME planning task", "A non-clinical administrative reminder is lower risk and keeps clinical judgement outside automation."),
    ("Research", "NotebookLM summarises three uploaded papers. Which statement is correct?", ["Source-grounded output is clinically correct", "The summary replaces critical appraisal", "Each statement still requires checking against the source", "Uploaded papers cannot disagree"], "Each statement still requires checking against the source", "Grounding limits the source set but does not guarantee accurate interpretation."),
    ("Social media", "Which draft feature requires immediate review?", ["A guideline link", "A patient photograph with verbal consent only", "A neutral educational disclaimer", "A publication date"], "A patient photograph with verbal consent only", "Patient images require appropriate consent plus institutional, legal, and professional review; verbal consent alone may be insufficient."),
    ("Pricing", "A catalogue shows a price checked last month. How should it be used?", ["As a binding quote", "As dated orientation followed by an official price check", "As evidence of India availability", "As proof of a free tier"], "As dated orientation followed by an official price check", "Prices, taxes, eligibility, and regional terms change and must be checked before purchase."),
    ("Equity", "A diagnostic model performed well in one country and age group. What remains important?", ["Nothing; accuracy is universal", "Performance across the intended local population and workflow", "Only interface design", "Only model size"], "Performance across the intended local population and workflow", "Transportability cannot be assumed across prevalence, equipment, populations, and clinical pathways."),
    ("Copyright", "What is the safest journal-club upload practice?", ["Upload any publisher PDF to any public service", "Use openly shareable or authorised papers and respect licence terms", "Remove the first page only", "Convert the article to images"], "Use openly shareable or authorised papers and respect licence terms", "Changing file format does not remove copyright or confidentiality obligations."),
    ("Accountability", "Who owns the final clinical note after an AI scribe drafts it?", ["The AI vendor", "The patient", "The qualified clinician and responsible institution under applicable policy", "No one if it is labelled draft"], "The qualified clinician and responsible institution under applicable policy", "Draft generation does not transfer professional accountability."),
    ("Uncertainty", "The source does not state a medicine dose. What should the AI output do?", ["Infer the common dose", "Omit the medicine", "State that the dose is missing and requires verification", "Choose the lowest dose"], "State that the dose is missing and requires verification", "Unknown clinical information must remain visible rather than being guessed or silently removed."),
    ("Image quality", "Before interpreting an AI-highlighted region, what should be checked first?", ["The colour of the heatmap", "Image quality, modality, body region, and intended-use conditions", "The vendor logo", "The confidence score alone"], "Image quality, modality, body region, and intended-use conditions", "Poor or out-of-scope input can make downstream output unreliable regardless of interface confidence."),
    ("Human override", "A workflow has no way for staff to stop an automated action. What is missing?", ["A larger dataset", "Human override and exception handling", "A logo", "A shorter prompt"], "Human override and exception handling", "Safe systems need accountable owners, stopping rules, and a route for exceptions."),
    ("Differential reasoning", "What is a safe role for a general AI assistant in differential diagnosis?", ["Choose the final diagnosis", "Prescribe treatment", "Organise supporting, opposing, and missing features for clinician review", "Rule out emergencies autonomously"], "Organise supporting, opposing, and missing features for clinician review", "Structured brainstorming can support reasoning but cannot replace examination, testing, or clinical accountability."),
    ("Data retention", "A tool deletes audio after transcription but retains generated notes. What should the institution do?", ["Assume there is no privacy risk", "Review the complete data lifecycle, contract, retention, access, and subprocessors", "Use shorter recordings", "Rely only on the vendor homepage"], "Review the complete data lifecycle, contract, retention, access, and subprocessors", "Deletion of one data type does not answer how all sensitive content is stored, used, or shared."),
    ("Clinical communication", "An automated reminder is ready to send to patients. What is required?", ["Send it immediately", "Clinical, privacy, audience, escalation, and workflow review before use", "Only spelling review", "A social-media account"], "Clinical, privacy, audience, escalation, and workflow review before use", "Patient communication can influence care and must be governed and reviewed even when the message appears routine."),
]


def build_quiz() -> list[dict]:
    settings = ["outpatient clinic", "CME workshop", "research meeting", "hospital department", "teleconsultation planning", "journal club"]
    questions = []
    for theme_index, (category, question, options, answer, explanation) in enumerate(QUIZ_THEMES, start=1):
        for setting_index, setting in enumerate(settings, start=1):
            questions.append({
                "id": f"q-{theme_index:02d}-{setting_index:02d}", "category": category,
                "question": f"During a {setting}, {question[0].lower() + question[1:]}",
                "options": options, "answer": answer, "explanation": explanation,
                "difficulty": ["Beginner", "Intermediate", "Advanced"][setting_index % 3],
            })
    return questions


def build_resources() -> dict:
    return {
        "problem_routes": {
            "My clinical notes take too long.": ["documentation", "scribe", "note"],
            "I need to explain a diagnosis to a patient.": ["patient", "plain-language", "communication"],
            "I need evidence for a clinical question.": ["research", "evidence", "literature"],
            "I need to prepare a journal-club presentation.": ["journal", "presentation", "research"],
            "I need a professional LinkedIn post.": ["professional", "social", "LinkedIn"],
            "I need to organise clinic protocols.": ["workflow", "knowledge", "protocol"],
            "I want to understand AI-assisted image analysis.": ["imaging", "radiology", "diagnostic"],
            "I need to create patient education material.": ["patient", "education", "handout"],
        },
        "recommended_sequences": {
            "30": ["ChatGPT", "Perplexity", "Heidi"],
            "60": ["ChatGPT", "Freed", "Perplexity", "NotebookLM", "Canva", "Buffer"],
            "90": ["Freed", "Perplexity", "NotebookLM", "monday.com", "Canva", "Qure.ai qXR/qER", "Mentimeter"],
        },
        "patient_centricity_flow": ["Patient need", "Specialty context", "Evidence", "Decision support", "Doctor judgement", "Patient-centred action"],
        "literature_only_consent": "Use fictional, published, de-identified, openly licensed, or otherwise authorised teaching material. Obtain any consent and institutional clearance required for real-world material outside this app. This workshop does not create, replace, or interpret a clinical consent form.",
        "audience_marketing": {
            "Doctors": {
                "headline": "Spend workshop time on clinical judgement, not prompt engineering.",
                "copy": "Practise copy-ready prompts, specialty cases, source checking, and AI-versus-doctor review using fictional data.",
                "cta": "Join the hands-on AI Rx session for doctors.",
                "platform_post": "AI can draft and organise. The doctor still decides. AI Rx gives physicians copy-ready prompts, specialty-specific fictional cases, and structured AI-versus-doctor debriefs anchored in patient safety.",
            },
            "Hospital leaders": {
                "headline": "Move from scattered experimentation to governed clinical decision support.",
                "copy": "Use the workshop to examine privacy, accountability, evidence, workflow ownership, exceptions, and measurable patient-service impact.",
                "cta": "Bring a clinical, IT, quality, and governance team.",
                "platform_post": "AI adoption in hospitals needs more than a tool demonstration. AI Rx connects use cases with data boundaries, qualified review, human override, audit trails, and patient-centred measures.",
            },
            "Researchers": {
                "headline": "Use AI to accelerate evidence work without outsourcing critical appraisal.",
                "copy": "Build PICO questions, literature searches, evidence tables, and journal-club discussions while checking every citation and inference.",
                "cta": "Bring one authorised paper set and one research question.",
                "platform_post": "Source-grounded is not the same as scientifically correct. AI Rx trains researchers to use AI for discovery and synthesis while retaining transparent methods, source verification, and uncertainty.",
            },
            "Medical educators": {
                "headline": "Teach where AI stops and professional reasoning begins.",
                "copy": "Use staged cases, copy-ready prompts, AI-versus-doctor comparisons, polls, and reflection to make tacit clinical reasoning discussable.",
                "cta": "Adapt the specialty cases for your learner level.",
                "platform_post": "The useful teaching moment is not a perfect AI answer. It is the gap between the AI draft and the clinician's judgement. AI Rx turns that gap into a structured debrief.",
            },
            "Pharma and life sciences": {
                "headline": "Communicate evidence clearly while preserving medical, regulatory, and audience boundaries.",
                "copy": "Practise literature synthesis, audience-specific education, content review, and disclosure without turning workshop material into promotional clinical advice.",
                "cta": "Use the research and communication labs with approved sources.",
                "platform_post": "AI Rx helps medical and life-sciences teams convert authorised evidence into reviewable educational drafts, with source checks, audience fit, disclosure, and human approval built into the workflow.",
            },
        },
        "ethics_topics": [
            {"title": "Patient confidentiality", "description": "Use data minimisation, approved environments, role-based access, and explicit policy. De-identification reduces but may not remove risk."},
            {"title": "Consent", "description": "Explain what the tool does, what data it receives, choices available, and what happens after processing."},
            {"title": "Hallucination", "description": "Compare material outputs with the source and treat unsupported details as safety failures, not stylistic errors."},
            {"title": "Automation bias", "description": "Design review steps that make disagreement, uncertainty, and escalation visible before action."},
            {"title": "Population bias", "description": "Check evidence in the intended population, prevalence, equipment, language, setting, and workflow."},
            {"title": "Explainability", "description": "Users need enough information to understand intended output, limits, and appropriate response. A heatmap alone is not an explanation."},
            {"title": "Source verification", "description": "Open cited material and check that each claim matches the source, population, date, and evidence type."},
            {"title": "Copyright", "description": "Use authorised or openly licensed documents, images, and media. Format conversion does not change rights."},
            {"title": "Institutional policy", "description": "Local approval, procurement, information security, legal review, clinical governance, and audit requirements still apply."},
            {"title": "Medical-device regulation", "description": "Verify the exact product, version, intended use, indication, geography, and current listing. Do not generalise from company-level claims."},
            {"title": "Clinical accountability", "description": "A qualified professional owns review and final use. AI generation does not transfer responsibility."},
            {"title": "Audit trails and override", "description": "Record material inputs, versions, reviews, changes, exceptions, and who authorised the final action."},
        ],
        "facilitator": {
            "name": "Dr. Alok Tiwari",
            "role": "Assistant Professor, Big Data Analytics",
            "institution": "Goa Institute of Management, Goa",
            "tagline": "Building responsible AI for healthcare, education and decision science",
            "summary": "Dr. Alok Tiwari brings biomedical engineering, responsible AI and management education together to turn rigorous technical work into practical decisions.",
            "bio": "Dr. Alok Tiwari is an Assistant Professor in Big Data Analytics at Goa Institute of Management. With a PhD in Biomedical Engineering from IIT (BHU), Varanasi, he connects responsible AI system design, clinical decision support, medical imaging research and management education. His work is grounded in a simple aim: help learners and practitioners move from technical possibility to informed, accountable action.",
            "focus_statement": "Healthcare AI · Explainable AI · MLOps",
            "principle": "Engineering depth. Human purpose.",
            "education": [
                {"mark": "PhD", "degree": "Biomedical Engineering", "institution": "IIT (BHU), Varanasi", "focus": "Transfer learning · Cardiac MRI · COVID-19 AI"},
                {"mark": "MTech", "degree": "Biomedical Engineering", "institution": "NIT Kurukshetra", "focus": "Signal processing · Medical imaging"},
                {"mark": "BTech", "degree": "Electronics & Communication", "institution": "GBTU, Lucknow", "focus": "ECE foundations · Digital systems"},
            ],
            "expertise": ["Healthcare AI", "Medical imaging", "Explainable & responsible AI", "Clinical decision support", "Machine learning", "Computer vision", "MLOps", "Generative AI", "Management analytics", "Faculty development"],
            "research_areas": [
                {"icon": "🫁", "title": "Medical Image Analysis", "description": "Deep learning for MRI, chest X-ray and clinical imaging, including cardiac segmentation and respiratory disease detection.", "tags": ["CNN", "U-Net", "ResNet"]},
                {"icon": "🔍", "title": "Explainable & Ethical AI", "description": "Transparent and robust AI systems designed around trust, accountability and fairness for clinicians and managers.", "tags": ["XAI", "LIME", "SHAP"]},
                {"icon": "📈", "title": "Applied Data Science", "description": "Statistical learning and AI workflows for healthcare, business and policy questions where decisions have consequences.", "tags": ["Python", "Statistics", "Analytics"]},
                {"icon": "🧑‍🏫", "title": "Pedagogy & Learning Innovation", "description": "Generative AI and analytics-enabled approaches for learning design, faculty development and management education.", "tags": ["GenAI", "EdTech", "FDPs"]},
                {"icon": "🏭", "title": "Industry-Oriented Analytics", "description": "Executive and practitioner learning that turns analytics theory into organisational decision value.", "tags": ["MDPs", "BI tools", "SQL"]},
                {"icon": "⚙️", "title": "Production-Ready AI Workflows", "description": "Cloud, reproducibility, CI/CD and MLOps practices that carry data science work from notebook to deployment.", "tags": ["Docker", "MLflow", "Cloud"]},
            ],
            "experience": [
                {"period": "2024 – Present", "role": "Assistant Professor, Big Data Analytics", "organisation": "Goa Institute of Management, Goa", "description": "Teaches healthcare analytics, MLOps, logical reasoning, sports analytics and emerging technology modules, alongside faculty and executive development."},
                {"period": "2023", "role": "Assistant Professor", "organisation": "ATLAS SkillTech University, Mumbai", "description": "Taught statistics, calculus and industrial analytics, while contributing to curriculum design and student mentoring."},
                {"period": "2022 – 2023", "role": "Faculty, Data Engineering & AI", "organisation": "uGDX / INSOFE, Hyderabad", "description": "Delivered applied learning in Python, SQL, machine learning, computer vision, cloud workflows, DevOps and big data tools."},
                {"period": "2015 – 2021", "role": "PhD Research, Biomedical Engineering", "organisation": "IIT (BHU), Varanasi", "description": "Researched transfer learning for COVID-19 chest X-ray classification and weakly supervised cardiac MRI segmentation."},
            ],
            "teaching_summary": "Audience-specific courses, executive development, faculty programmes and applied AI experiences across management, healthcare, engineering, research and data engineering.",
            "teaching_areas": ["Healthcare Analytics", "MLOps", "Data Visualization", "Sports Analytics", "Intelligent Research", "Machine Learning", "Deep Learning", "NLP", "Python & R", "Executive GenAI"],
            "teaching_philosophy": "Every technical concept taught to a manager should arrive with a decision they can make.",
            "collaboration": "Open to research collaboration, invited talks, faculty opportunities, executive programme design and applied AI consulting.",
            "portfolio_url": "https://dr-alok-tiwari.github.io/",
            "profile_image_url": "https://dr-alok-tiwari.github.io/assets/img/prof_pic.jpg",
            "linkedin": "https://www.linkedin.com/in/dr-alok-tiwari/",
            "github": "https://github.com/dr-alok-tiwari",
            "orcid": "https://orcid.org/0000-0003-3605-8565",
            "email": "shodhkarta.alok@gmail.com",
            "profile_last_checked": "2026-08-03",
            "institution_logo": "",
            "partner_logo": "",
        },
    }


def build_prompt_handbook(prompts: list[dict]) -> None:
    HANDOUTS.mkdir(parents=True, exist_ok=True)
    core = [prompt for prompt in prompts if prompt["category"] in {"Patient-friendly explanation", "Differential-diagnosis brainstorming"}]
    sections = []
    text_sections = []
    for number, prompt in enumerate(core, start=1):
        sections.append(
            f"<section><p class='number'>PROMPT {number:02d} · {escape(prompt['specialty'])}</p>"
            f"<h2>{escape(prompt['title'])}</h2><pre>{escape(prompt['prompt'])}</pre></section>"
        )
        text_sections.append(f"PROMPT {number:02d}: {prompt['title']}\n{'=' * 88}\n{prompt['prompt']}\n")
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>AI Rx Copy-Ready Prompt Booklet</title>
<style>@page{{size:A4;margin:16mm}}body{{font-family:Aptos,Arial,sans-serif;color:#102a33;line-height:1.4}}header{{border-bottom:5px solid #0f766e;margin-bottom:20px}}h1{{color:#0f766e}}h2{{font-size:18px}}.number{{color:#b45309;font-weight:bold;letter-spacing:.08em}}pre{{white-space:pre-wrap;font:10pt/1.45 Consolas,monospace;border:1px solid #8bcac1;background:#f2fbf9;padding:12px}}section{{break-before:page}}section:first-of-type{{break-before:auto}}footer{{font-size:9pt;color:#47636b;margin-top:18px}}</style></head>
<body><header><h1>AI Rx Copy-Ready Prompt Booklet</h1><p>Patient first · Doctor led · AI assisted</p><p>Core patient-explanation and differential-reasoning prompts across 19 specialties. Fictional, de-identified, openly licensed, or authorised material only.</p></header>{''.join(sections)}<footer>Educational workshop resource. Qualified professional verification is mandatory.</footer></body></html>"""
    (HANDOUTS / "AI_Rx_Copy_Ready_Prompt_Booklet.html").write_text(html, encoding="utf-8")
    (HANDOUTS / "AI_Rx_Copy_Ready_Prompt_Booklet.txt").write_text("\n\n".join(text_sections), encoding="utf-8")


def build_promo_animation() -> None:
    MARKETING.mkdir(parents=True, exist_ok=True)
    frames = []
    headlines = [
        ("AI Rx", "AI tools for clinical practice and patient care"),
        ("Copy-ready prompts", "Doctors use the prompt. The workshop teaches the judgement."),
        ("Specialty cases", "Date, series, procedure, patient context and missing information upfront"),
        ("AI versus Doctor", "AI organises. Clinical acumen resolves ambiguity."),
        ("Decision support", "Evidence, uncertainty, human override and accountability"),
        ("Patient centricity", "Diagnosis · specialty · research · communication · follow-up"),
        ("AI Rx Live Demo Studio", "Patient first · Doctor led · AI assisted"),
    ]
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    title_font = ImageFont.truetype(bold_path, 58) if Path(bold_path).exists() else ImageFont.load_default()
    body_font = ImageFont.truetype(regular_path, 28) if Path(regular_path).exists() else ImageFont.load_default()
    small_font = ImageFont.truetype(bold_path, 17) if Path(bold_path).exists() else ImageFont.load_default()
    for index, (headline, subline) in enumerate(headlines):
        frame = Image.new("RGB", (1200, 675), "#07151C")
        draw = ImageDraw.Draw(frame)
        draw.ellipse((780-index*12, -210+index*10, 1370-index*12, 380+index*10), fill="#12313B", outline="#2DD4BF", width=6)
        draw.ellipse((900, -100, 1220, 220), fill="#F59E0B")
        draw.rectangle((0, 0, 18, 675), fill="#F59E0B")
        draw.text((74, 74), "AI RX · CLINICAL PRACTICE & PATIENT CARE", font=small_font, fill="#FBBF24")
        draw.text((74, 225), headline, font=title_font, fill="#F7FBFC")
        draw.multiline_text((78, 315), subline, font=body_font, fill="#B6CCD3", spacing=12)
        draw.text((78, 585), f"0{index+1} / 07", font=small_font, fill="#2DD4BF")
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=192))
    frames[0].save(MARKETING / "AI_Rx_Workshop_Promo.gif", format="GIF", save_all=True, append_images=frames[1:], duration=1700, loop=0, disposal=2)


def build_images() -> list[dict]:
    modalities = {
        "Chest X-ray": "Thorax", "Brain CT": "Head", "Brain MRI": "Brain", "Skin lesion": "Skin",
        "Retinal image": "Eye", "ECG waveform": "Cardiac electrical signal", "Histopathology slide": "Tissue",
        "Ultrasound image": "Selected organ or region",
    }
    palette = ["#F59E0B", "#2DD4BF", "#FBBF24", "#FB7185", "#6EE7B7"]
    index = []
    for modality_index, (modality, region) in enumerate(modalities.items()):
        for case_number in range(1, 6):
            ident = f"sim-{slug(modality)}-{case_number}"
            filename = f"{ident}.png"
            accent = palette[(modality_index + case_number) % len(palette)]
            x = 120 + case_number * 58
            y = 130 + (modality_index % 3) * 70
            image = Image.new("RGB", (960, 620), "#040D12")
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((34, 34, 926, 586), radius=24, fill="#0D222B", outline="#2A5560", width=2)
            draw.text((72, 70), f"{modality} | simulation {case_number}", fill="#FFF7E6")
            draw.text((72, 110), "Abstract interface training asset - not a medical image", fill="#B6CCD3")
            draw.rounded_rectangle((72, 164, 888, 464), radius=18, fill="#040D12", outline="#244852", width=2)
            points = [(105, 360), (170, 220 + case_number * 10), (230, 420 - case_number * 12), (300, 300), (430, 230), (500, 340), (650, 450), (840, 250)]
            draw.line(points, fill="#9c96a2", width=8, joint="curve")
            radius = 36 + case_number * 5
            cx, cy = x + 250, y + 120
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=accent, outline="#FFFFFF", width=3)
            draw.line((cx, cy, 760, 510), fill=accent, width=3)
            draw.rounded_rectangle((640, 488, 888, 546), radius=12, fill="#12313B", outline=accent, width=2)
            draw.text((664, 509), "Illustrative region marker", fill="#FFFFFF")
            draw.text((72, 548), "EDUCATIONAL SIMULATION - NOT A CLINICAL REPORT", fill="#FBBF24")
            image.save(IMAGES / filename, format="PNG", optimize=True)
            index.append({
                "id": ident, "title": f"{modality} simulation {case_number}", "modality": modality, "body_region": region,
                "path": f"assets/sample_medical_images/{filename}",
                "alt_text": f"Abstract educational simulation labelled {modality}, with a coloured illustrative region marker; not a diagnostic image.",
                "quality_checklist": ["Correct modality and body region", "Orientation and coverage are adequate", "Artefact and acquisition quality reviewed", "Comparison material identified where relevant"],
                "observation_task": "Describe only visible interface elements and image-quality considerations. Do not infer a diagnosis from this abstract placeholder.",
                "illustrative_confidence": f"{52 + modality_index * 3 + case_number * 2}%",
                "differential_considerations": "Not applicable to this abstract placeholder; in real use, a qualified clinician would integrate observations with history, examination, prior studies, and validated product scope.",
                "ground_truth": "Not applicable — synthetic user-interface placeholder with no patient content.",
                "limitations": "Not a medical image, not processed by a diagnostic model, and unsuitable for clinical interpretation.",
                "licence": "Project-generated synthetic PNG; MIT project licence applies.",
            })
    profile = '''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="720" role="img" aria-label="Configurable profile photograph placeholder"><rect width="720" height="720" rx="42" fill="#0D222B"/><circle cx="360" cy="270" r="118" fill="#2DD4BF"/><path d="M140 650c20-150 110-230 220-230s200 80 220 230" fill="#0F766E"/><text x="360" y="690" text-anchor="middle" fill="#FBBF24" font-family="Arial" font-size="26">Add authorised profile photograph</text></svg>'''
    (ASSETS / "profile_placeholder.svg").write_text(profile, encoding="utf-8")
    return index


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    tools = build_tools()
    prompts = build_prompts()
    write_json("tools_catalog.json", tools)
    write_json("demo_workflows.json", build_workflows(tools))
    write_json("prompts.json", prompts)
    write_json("synthetic_cases.json", build_cases())
    write_json("quiz_bank.json", build_quiz())
    write_json("specialties.json", SPECIALTIES)
    write_json("resources.json", build_resources())
    write_json("image_index.json", build_images())
    build_prompt_handbook(prompts)
    build_promo_animation()
    print(f"tools={len(tools)} workflows={len(build_workflows(tools))} prompts={len(prompts)} cases={len(build_cases())} quiz={len(build_quiz())}")


if __name__ == "__main__":
    main()
