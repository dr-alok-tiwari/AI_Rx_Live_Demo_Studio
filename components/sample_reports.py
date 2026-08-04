"""Generate complete fictional PDF attachments and attachment-ready prompts."""

from __future__ import annotations

from html import escape
from io import BytesIO
import re
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


DOCUMENT_DATE = "09-JUL-2026"
SERIES_DATE = "02-JUL-2026"


SPECIALTY_SCENARIOS: dict[str, dict[str, Any]] = {
    "General Medicine": {
        "subject": "Maya; age range 45-55; woman; fictional outpatient follow-up",
        "context": "Hypertension follow-up after seven days of home monitoring.",
        "source": "Patient-reported home-reading log and fictional follow-up note; no device export or physical examination is attached.",
        "facts": ["Home readings were 146-158/88-96 over seven days.", "Two doses were reported missed.", "No headache, chest pain, dyspnoea, weakness, or visual symptom was stated."],
        "negatives": ["No acute symptom was stated in the supplied note.", "No treatment change or diagnosis is supplied."],
        "missing": ["Medicine name and dose: NOT PROVIDED.", "Clinic blood pressure, technique check, examination, and laboratory results: NOT PROVIDED."],
        "constraints": "Primary-care teaching setting in India; English output; no access to the patient, prescribing record, or calibrated-device check.",
    },
    "Family Medicine": {
        "subject": "Nila; age range 25-35; woman; fictional primary-care encounter",
        "context": "Four days of dry cough and a mild fever reported on the previous day.",
        "source": "Fictional consultation summary; no audio, image, or device data.",
        "facts": ["Dry cough was reported for four days.", "Mild fever was reported yesterday.", "Controlled hypertension is listed in the history."],
        "negatives": ["No chest pain or breathlessness was reported.", "No medicine allergy was stated."],
        "missing": ["Vital signs and physical examination: NOT PROVIDED.", "Medicine name, dose, tests, diagnosis, and treatment plan: NOT PROVIDED."],
        "constraints": "General family-practice teaching context; Grade 7 language for patient material; access and follow-up route must be reviewed locally.",
    },
    "Emergency Medicine": {
        "subject": "Asha; age range 45-55; sex not specified; fictional triage encounter",
        "context": "Pressure-like central chest discomfort with incomplete timing and risk-factor information.",
        "source": "Synthetic triage text only; no ECG image, monitor trace, or clinician examination.",
        "facts": ["Central pressure-like discomfort is stated.", "Symptoms began on the encounter date; exact onset time is not supplied.", "The exercise is intended to expose missing-data and automation-bias risk."],
        "negatives": ["No loss of consciousness is stated.", "No final disposition or diagnosis is supplied."],
        "missing": ["Vital signs, severity, duration, radiation, risk factors, examination, ECG, and biomarkers: NOT PROVIDED.", "Urgency decision: RESERVED FOR QUALIFIED CLINICIAN."],
        "constraints": "Time-sensitive teaching simulation; the model must flag missing discriminators without issuing an autonomous triage disposition.",
    },
    "Cardiology": {
        "subject": "Noor; age range 55-65; woman; fictional cardiology referral",
        "context": "Intermittent palpitations with incomplete trigger and duration data.",
        "source": "Referral note and written description of a synthetic single-lead recording; no waveform is provided.",
        "facts": ["Palpitations are intermittent.", "The referral note states no acute instability.", "A single-lead recording is described as having artefact."],
        "negatives": ["No syncope or chest pain is documented.", "No confirmed rhythm interpretation is supplied."],
        "missing": ["Episode duration, triggers, pulse, 12-lead ECG, medicines, and laboratory results: NOT PROVIDED.", "Direct waveform review: NOT AVAILABLE."],
        "constraints": "Educational use only; a text-only model cannot interpret the unavailable waveform or establish a rhythm diagnosis.",
    },
    "Dermatology": {
        "subject": "Tara; age range 25-35; woman; fictional dermatology encounter",
        "context": "Patient-reported change in size of a pigmented lesion over three months.",
        "source": "Structured fictional ABCDE observations; no clinical or dermoscopic image.",
        "facts": ["Location is the left forearm.", "Change in size over three months is reported.", "The supplied note describes colour variation but provides no measurement."],
        "negatives": ["Bleeding and ulceration are not reported.", "No pathology result is supplied."],
        "missing": ["Exact dimensions, palpation, full-skin examination, dermoscopy, image scale, and histology: NOT PROVIDED.", "Final assessment: RESERVED FOR QUALIFIED CLINICIAN."],
        "constraints": "Observation-inference separation is mandatory; no visual diagnosis can be made from the text-only attachment.",
    },
    "Dentistry": {
        "subject": "Rohan; age range 35-45; man; fictional dental encounter",
        "context": "Intermittent lower-right molar pain when chewing for five days.",
        "source": "Fictional dental history; no oral photograph or radiograph.",
        "facts": ["Pain is reported during chewing.", "The patient identifies the lower-right posterior region.", "Symptoms have been present for five days."],
        "negatives": ["No facial swelling, difficulty swallowing, or trauma is stated.", "No diagnosis or procedure is supplied."],
        "missing": ["Dental examination, vitality testing, periodontal findings, radiograph, medicine history, and pain score: NOT PROVIDED.", "Tooth number: NOT CONFIRMED."],
        "constraints": "Dental teaching exercise; laterality and uncertainty must be preserved, and unavailable imaging must not be inferred.",
    },
    "Obstetrics and Gynaecology": {
        "subject": "Leela; age range 25-35; woman; fictional antenatal education encounter",
        "context": "Requests a plain-language explanation of the routine antenatal test schedule.",
        "source": "Synthetic visit summary and locally drafted teaching schedule; not an approved clinical guideline.",
        "facts": ["The encounter is described as a routine antenatal education visit.", "The patient prefers a one-page English explanation.", "No individual test result is supplied."],
        "negatives": ["No pain, bleeding, reduced movement, or acute concern is stated in the exercise.", "No treatment or procedure decision is supplied."],
        "missing": ["Gestational age, obstetric history, examination, test results, and local protocol version: NOT PROVIDED.", "Applicable schedule requires local clinician verification."],
        "constraints": "Do not generalise schedules across settings; preserve dignity, consent, access, and local-policy review.",
    },
    "Oncology": {
        "subject": "Mina; age range 35-45; woman; fictional oncology follow-up preparation",
        "context": "Wants to prepare questions after receiving a synthetic pathology summary.",
        "source": "Fictional pathology-summary text; no slide, treatment record, staging work-up, or multidisciplinary decision.",
        "facts": ["A pathology summary is stated to have been received.", "The task is question preparation and source clarification.", "The patient preference recorded is to include a caregiver in the discussion."],
        "negatives": ["No new symptom or acute deterioration is stated.", "No treatment recommendation is supplied."],
        "missing": ["Full pathology report, stage, imaging, biomarkers, performance status, and treatment options: NOT PROVIDED.", "Final interpretation and plan: RESERVED FOR THE ONCOLOGY TEAM."],
        "constraints": "High-emotion communication setting; uncertainty and patient preferences must stay visible without creating prognosis or treatment claims.",
    },
    "Ophthalmology": {
        "subject": "Arun; age range 65-75; man; fictional retinal-screening follow-up",
        "context": "Requests an explanation of a fictional retinal-screening note.",
        "source": "Synthetic screening-note text; no fundus image, OCT, or visual-field data.",
        "facts": ["The note states that image quality was adequate for screening.", "A non-specific abnormality is flagged for review.", "The patient requests large-print instructions."],
        "negatives": ["No sudden vision loss, severe eye pain, or trauma is stated.", "No diagnosis is supplied."],
        "missing": ["Visual acuity, intraocular pressure, dilated examination, image, OCT, laterality confirmation, and previous comparison: NOT PROVIDED.", "Screening flag requires specialist review."],
        "constraints": "Accessible large-print wording is requested; a text model cannot inspect the unavailable retinal image.",
    },
    "Orthopaedics": {
        "subject": "Om; age range 45-55; man; fictional orthopaedic encounter",
        "context": "Knee pain after an increase in walking activity.",
        "source": "Fictional history and partial range-of-motion note; no image.",
        "facts": ["Pain followed increased walking.", "The right knee is named in the note.", "A partial range-of-motion observation is supplied without numerical measurement."],
        "negatives": ["No fall, visible deformity, fever, or inability to bear weight is stated.", "No diagnosis is supplied."],
        "missing": ["Pain severity, full red-flag history, examination, neurovascular status, radiograph, and previous injury details: NOT PROVIDED.", "Management plan: NOT PROVIDED."],
        "constraints": "Preserve laterality and functional context; do not infer imaging findings or issue rehabilitation instructions.",
    },
    "Paediatrics": {
        "subject": "Avi; age range 2-5; sex not specified; fictional caregiver consultation",
        "context": "Caregiver reports fever and reduced appetite.",
        "source": "Fictional caregiver note; no direct examination or device record.",
        "facts": ["Fever and reduced appetite are caregiver-reported.", "The child is in the 2-5 year age range.", "The exercise focuses on clear safety-netting questions."],
        "negatives": ["No seizure, rash, or breathing difficulty is stated.", "No medicine or dose is supplied."],
        "missing": ["Temperature, duration, hydration, urine output, activity, weight, examination, vaccination context, and tests: NOT PROVIDED.", "Any dose calculation is OUT OF SCOPE."],
        "constraints": "Caregiver-facing language; paediatric age, weight, safeguarding, and access considerations prevent adult generalisation.",
    },
    "Pathology": {
        "subject": "PX-07; adult age range not provided; fictional pathology teaching specimen",
        "context": "Structured review of a synthetic histopathology-summary extract.",
        "source": "Text-only fictional specimen and report metadata; no slide or whole-slide image.",
        "facts": ["Specimen label is PX-07.", "The summary records tissue type and processing date.", "One descriptive phrase is marked uncertain in the source."],
        "negatives": ["No final integrated diagnosis is supplied.", "No molecular or immunohistochemistry result is supplied."],
        "missing": ["Clinical history, gross description, slide, magnification, stain details, ancillary tests, and sign-out: NOT PROVIDED.", "Morphology cannot be verified from text alone."],
        "constraints": "Laboratory teaching workflow; traceability and observation-inference separation are required.",
    },
    "Psychiatry": {
        "subject": "Sameer; age range 25-35; man; fictional mental-health follow-up",
        "context": "Reports lower mood and sleep difficulty; risk assessment is incomplete.",
        "source": "Fictional follow-up note; no recording, examination, or collateral history.",
        "facts": ["Lower mood and sleep difficulty are reported.", "The note states that work stress has increased.", "The risk section is explicitly incomplete."],
        "negatives": ["No substance use or psychotic symptom is documented in the supplied note.", "Absence of documentation is not evidence of absence."],
        "missing": ["Duration, function, mental-status examination, self-harm and suicide assessment, supports, medicines, and previous history: NOT PROVIDED.", "Urgency and diagnosis require qualified assessment."],
        "constraints": "Trauma-informed, non-stigmatising language; safety assessment cannot be automated or inferred from missing text.",
    },
    "Public Health": {
        "subject": "PH-2026-07; fictional district-level population dataset; no person-level records",
        "context": "Planning an educational brief about a synthetic rise in fever-clinic attendance.",
        "source": "Aggregate weekly counts from four fictional facilities; no surveillance confirmation or individual data.",
        "facts": ["Aggregate attendance rose from 118 to 151 visits between two supplied weeks.", "Four facilities used the same fictional reporting form.", "The task is communication and data-quality review, not outbreak confirmation."],
        "negatives": ["No laboratory-confirmed case count is supplied.", "No causal attribution is supplied."],
        "missing": ["Catchment denominators, duplicate checks, test results, case definition, reporting completeness, and baseline seasonality: NOT PROVIDED.", "Public-health action threshold: NOT PROVIDED."],
        "constraints": "Aggregate-data teaching exercise; avoid ecological inference, alarmist language, or claims that exceed surveillance evidence.",
    },
    "Radiology": {
        "subject": "Ira; age range 45-55; woman; fictional radiology communication case",
        "context": "Requests a plain-language explanation of a synthetic chest-imaging report.",
        "source": "Text of a fictional report only; no image or acquisition record.",
        "facts": ["The supplied report contains an incidental non-acute phrase.", "The report date is 09-JUL-2026.", "The patient asks what questions to discuss with the clinician."],
        "negatives": ["The source text does not describe an acute emergency.", "No diagnosis or management plan is supplied."],
        "missing": ["Images, modality parameters, indication, prior study, full report wording, and clinical correlation: NOT PROVIDED.", "Image interpretation is OUT OF SCOPE."],
        "constraints": "Text-only explanation task; do not reinterpret or overrule the radiologist, and do not infer unavailable images.",
    },
    "Research": {
        "subject": "JC-01; fictional evidence pack; no patient-level data",
        "context": "Three synthetic study summaries use different populations, follow-up periods, and outcome definitions.",
        "source": "Authorised fictional source pack labelled Study A, Study B, and Study C.",
        "facts": ["Study A is a 12-week randomised pilot with 84 participants.", "Study B is a six-month observational cohort with 210 participants.", "Study C is a qualitative study with 24 interviews.", "The outcome definitions are not interchangeable."],
        "negatives": ["No pooled estimate or systematic review is supplied.", "No source is presented as clinically definitive."],
        "missing": ["Full protocols, complete statistical output, funding details, and risk-of-bias assessment: NOT PROVIDED.", "External validity requires explicit review."],
        "constraints": "Research-methods lab; distinguish study design, source-supported claims, inference, and missing reporting.",
    },
    "Surgery": {
        "subject": "Neel; age range 35-45; man; fictional postoperative follow-up",
        "context": "Telephone follow-up after a fictional minor procedure.",
        "source": "Synthetic discharge text and telephone note; no wound image or direct examination.",
        "facts": ["The note records that the patient is eating and mobilising.", "Mild discomfort is reported.", "A follow-up date is included in the source."],
        "negatives": ["No vomiting, heavy bleeding, or breathlessness is stated.", "No new medicine or procedure is supplied."],
        "missing": ["Procedure name, wound examination, temperature, medicine list, pathology, and operative details: NOT PROVIDED.", "Postoperative decision requires the surgical team."],
        "constraints": "Remote follow-up teaching case; absence of direct examination limits generalisation and safety assessment.",
    },
    "Hospital Administration": {
        "subject": "QI-01; fictional department quality-improvement project; no patient-level data",
        "context": "Monthly equipment-safety checklist completion is inconsistent across three clinic rooms.",
        "source": "Synthetic aggregate completion log and meeting note.",
        "facts": ["Completion was 62%, 78%, and 71% across the last three months.", "Roles are department lead, nursing lead, and biomedical support.", "The next review is scheduled for 31-JUL-2026."],
        "negatives": ["No patient record or clinical outcome is included.", "No automated sanction or escalation is authorised."],
        "missing": ["Approved target, exception policy, evidence-retention period, and final owner sign-off: NOT PROVIDED.", "Local governance approval is required."],
        "constraints": "Non-clinical operational lab; exclude identifiers and keep decisions, exceptions, and escalation human-owned.",
    },
    "Medical Education": {
        "subject": "EDU-01; fictional postgraduate teaching cohort; 24 learners",
        "context": "Designing a supervised case discussion on responsible use of clinical AI.",
        "source": "Synthetic learning objectives, assessment blueprint, and aggregate pre-session confidence ratings.",
        "facts": ["The cohort has 24 postgraduate learners.", "Session duration is 75 minutes.", "Objectives cover source fidelity, uncertainty, privacy, and human oversight."],
        "negatives": ["No learner identity or grade is supplied.", "The material is not a professional credential or clinical protocol."],
        "missing": ["Institutional assessment weight, accessibility requirements, and final faculty approval: NOT PROVIDED.", "Learner-specific performance data: NOT PROVIDED."],
        "constraints": "Education lab; align content, activity, and assessment while keeping all cases fictional and reviewable.",
    },
}


TASK_CONTEXT: dict[str, dict[str, Any]] = {
    "Patient-friendly explanation": {"audience": "Patient and caregiver", "decision": "Prepare a plain-language draft for clinician review before a care discussion.", "depth": "Approximately Grade 7 reading level; define necessary technical terms.", "details": ["Use short sections and teach-back questions.", "Keep warning signs and contact routes in a separate review block."]},
    "Discharge-summary simplification": {"audience": "Patient and caregiver", "decision": "Create a source-faithful simplified discharge summary for clinician approval.", "depth": "Plain language; preserve every supplied medicine, date, dose, follow-up item, and uncertainty exactly.", "details": ["Do not add a diagnosis, medicine, dose, investigation, or instruction.", "Separate follow-up, warning signs, and unresolved questions."]},
    "Referral summary": {"audience": "Receiving clinician", "decision": "Draft a concise chronological referral that makes missing information and the referral question visible.", "depth": "Professional clinical summary; no inferred findings.", "details": ["Referral question: clarify the next qualified review needed from the supplied facts.", "Urgency rationale must quote only source-supported features."]},
    "Literature search": {"audience": "Clinician-researcher", "decision": "Approve a reproducible search strategy before database execution.", "depth": "Advanced research-methods level with database-ready syntax.", "details": ["Frame PICO or PEO from the specialty scenario.", "Propose concepts, synonyms, eligibility criteria, date limits, databases, and a screening log."], "sources": ["No external evidence is attached; the deliverable is a search plan, not an evidence conclusion."]},
    "Journal club": {"audience": "Clinician and postgraduate learners", "decision": "Prepare a source-by-source journal-club discussion without blending results.", "depth": "Critical appraisal level; every statement must carry a source label.", "details": ["Source A: fictional 12-week randomised pilot; n=84.", "Source B: fictional six-month observational cohort; n=210.", "Source C: fictional qualitative interview study; n=24.", "Outcome definitions differ and must not be pooled."], "sources": ["Only the three fictional source summaries inside this PDF are authorised."]},
    "Critical appraisal": {"audience": "Clinician-researcher", "decision": "Identify whether the supplied fictional evidence is sufficiently credible and applicable to inform further review.", "depth": "Advanced appraisal covering design, bias, measurement, analysis, precision, harms, and applicability.", "details": ["Reported result: Study A states a between-group mean difference of 4.2 units with 95% CI 0.8 to 7.6.", "Allocation concealment and attrition handling are NOT PROVIDED.", "Do not treat statistical significance as clinical importance."], "sources": ["Synthetic Study A extract in this PDF; no external article is authorised."]},
    "CME presentation": {"audience": "Qualified healthcare professionals", "decision": "Approve a ten-slide educational narrative for a supervised CME session.", "depth": "Specialist teaching level with one source and one interaction per section.", "details": ["Session duration: 20 minutes plus 10 minutes discussion.", "Include one fictional case, one poll, and one responsible-AI checkpoint.", "Claims without an approved source must be marked SOURCE REQUIRED."], "sources": ["This fictional report supplies the case only; clinical teaching claims require current approved sources before delivery."]},
    "Social-media post": {"audience": "Professional public audience", "decision": "Approve an evidence-aware educational post without patient disclosure or clinical advice.", "depth": "Plain, professional language; target 120-180 words.", "details": ["Platform: LinkedIn.", "Purpose: invite discussion about responsible, supervised AI use.", "Exclude patient stories, guarantees, fear-based claims, and diagnostic advice."], "sources": ["No external evidence claim is authorised; include a SOURCE REQUIRED marker if a claim needs support."]},
    "Professional biography": {"audience": "Conference organiser and professional audience", "decision": "Prepare 50-word, 120-word, and spoken-introduction drafts for factual verification.", "depth": "Professional, specific, and modest; no invented achievement.", "details": ["Fictional professional: Dr Kavya Rao, qualified specialist in the selected field.", "Current role: faculty clinician at a fictional teaching institution since 2023.", "Interests: responsible AI education and quality improvement.", "Degrees, awards, publications, memberships, and profile links: NOT PROVIDED and must be marked for confirmation."], "sources": ["Only the fictional CV facts listed in this PDF are authorised."]},
    "Clinic workflow": {"audience": "Clinic manager and clinical team", "decision": "Approve a non-clinical workflow map with owners, deadlines, exceptions, and audit points.", "depth": "Operational specification; exclude person-level patient data.", "details": ["Trigger: monthly equipment-safety checklist opens on the first working day.", "Roles: department lead, nursing lead, biomedical support.", "Deadline: fifth working day; overdue escalation remains human-owned."], "sources": ["Synthetic workflow brief in this PDF; local policy is NOT PROVIDED."]},
    "Audit checklist": {"audience": "Quality lead and audit team", "decision": "Create a traceable checklist for review against an approved standard.", "depth": "Exact criteria, evidence, owner, status, exception, corrective action, and review date.", "details": ["Synthetic criterion: each equipment check must record date, room, item identifier, reviewer role, evidence link, and exception status.", "Approved threshold and retention period: NOT PROVIDED.", "Completion status must not be inferred from missing evidence."], "sources": ["Synthetic criterion in this PDF; replace only after an authorised local standard is supplied."]},
    "Research protocol": {"audience": "Research team and ethics reviewer", "decision": "Prepare a protocol outline for methodological and ethics review, not study launch.", "depth": "Advanced protocol detail covering question, design, measures, analysis, bias, ethics, governance, and reporting.", "details": ["Proposed design: prospective observational feasibility study using fictional or authorised de-identified data.", "Primary outcome: feasibility of complete data capture at the planned review point.", "Sample-size assumptions, effect size, data dictionary, consent route, and statistical analysis plan: NOT PROVIDED."], "sources": ["This PDF is a fictional protocol brief; no ethics or institutional approval is implied."]},
    "Clinical teaching": {"audience": "Postgraduate clinical learners", "decision": "Approve a staged fictional case discussion and facilitator guide.", "depth": "Intermediate-to-advanced reasoning level with explicit pause points.", "details": ["Duration: 30 minutes.", "Reveal order: source facts, missing information, AI draft, clinician correction, patient-centred action.", "Include questions about tacit knowledge, automation bias, and non-generalisation."], "sources": ["Only this fictional scenario may be used in the teaching case."]},
    "Case-based MCQs": {"audience": "Postgraduate clinical learners", "decision": "Approve a small formative question set aligned to the supplied learning objective.", "depth": "Application and analysis level; one best answer with explanation for every option.", "details": ["Create five questions.", "Learning objective: distinguish verified facts, missing information, inference, and the qualified professional's final decision.", "Avoid trick wording, double negatives, and unsupported clinical detail."], "sources": ["Only the fictional scenario and learning objective in this PDF are authorised."]},
    "Image-analysis observation checklist": {"audience": "Qualified clinician or image reviewer", "decision": "Prepare an observation and image-quality checklist for a supervised review.", "depth": "Modality-specific professional checklist; visible observation must be separated from inference.", "details": ["No image is attached to this sample report.", "Acquisition, body region, laterality, series, comparison, calibration, and artefact fields must be marked NOT PROVIDED where absent.", "The model must not claim to see or interpret an unavailable image."], "sources": ["Text-only fictional report; image data are NOT PROVIDED."]},
    "Differential-diagnosis brainstorming": {"audience": "Qualified clinician", "decision": "Organise considerations and missing discriminators for clinician review without selecting a final diagnosis or treatment.", "depth": "Clinical reasoning scaffold with cannot-miss, common, supporting, opposing, and missing-feature columns.", "details": ["Rank nothing as confirmed.", "State which unavailable examination, test, timeline, or contextual feature could change each consideration.", "Keep the final diagnostic and treatment decision with the qualified professional."], "sources": ["Only the fictional facts in this PDF are authorised."]},
    "Administrative communication": {"audience": "Department lead and operational owner", "decision": "Approve a concise non-clinical email that secures a named decision and next step.", "depth": "Professional email under 180 words.", "details": ["Decision needed: confirm the owner and review date for the fictional action.", "Requested response deadline: 16-JUL-2026.", "Do not include patient-level information or invent authority, approval, or policy."], "sources": ["Synthetic operational context in this PDF."]},
}


def _clean_pdf_text(value: Any) -> str:
    """Keep built-in PDF fonts readable and comply with the ASCII-punctuation rule."""
    return (
        str(value)
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2011", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2026", "...")
        .replace("\u00a0", " ")
    )


def prompt_pdf_filename(prompt: dict[str, Any]) -> str:
    return f"AI_Rx_Sample_{prompt['id']}.pdf"


def workflow_pdf_filename(workflow: dict[str, Any]) -> str:
    return f"AI_Rx_Live_Demo_{workflow['id']}.pdf"


def attachment_ready_prompt(prompt: dict[str, Any]) -> str:
    """Replace fill-in placeholders with an exact attachment contract."""
    filename = prompt_pdf_filename(prompt)
    attachment_section = f"""ATTACHMENT TO UPLOAD WITH THIS PROMPT
Before submitting this prompt, upload the accompanying file named \"{filename}\".
Treat that PDF as the complete source record for this fictional {prompt['specialty']} workshop exercise. It already supplies the intended audience, exact decision, dates, subject or population, source information, verified facts, relevant negatives, explicit missing information, local constraints, desired depth, approved sources, and task-specific instructions.
Read the full PDF before answering. If the file is missing, unreadable, or internally inconsistent, stop and state the problem. Do not ask the user to replace template placeholders and do not use facts from outside the attachment."""
    output = re.sub(
        r"INFORMATION I WILL PROVIDE\n.*?\n\nNON-NEGOTIABLE RULES",
        attachment_section + "\n\nNON-NEGOTIABLE RULES",
        prompt["prompt"],
        count=1,
        flags=re.DOTALL,
    )
    output = re.sub(
        r"MATERIAL TO REVIEW\n.*\Z",
        f"MATERIAL TO REVIEW\nUse only the attached fictional report \"{filename}\". Every absent field remains NOT PROVIDED; the attachment does not authorise diagnosis, prescribing, treatment, triage, procedure approval, or autonomous communication.",
        output,
        count=1,
        flags=re.DOTALL,
    )
    return output


def workflow_attachment_prompt(workflow: dict[str, Any]) -> str:
    filename = workflow_pdf_filename(workflow)
    return f"""COPY-READY LIVE-DEMO PROMPT

ATTACHMENT
Upload \"{filename}\" before submitting this prompt. Read the complete fictional report and use it as the only source. If the file cannot be read, stop and say so. Preserve every explicit unknown and do not invent missing facts.

TASK
{workflow['sample_prompt']}

REQUIRED BOUNDARY
This is a decision-support draft for a practical lab. A qualified professional must verify the source fidelity, uncertainty, safety, applicability, and final use. Do not diagnose, prescribe, approve a procedure, issue autonomous triage, or communicate a clinical decision."""


def complete_workflow_copy_package(workflow: dict[str, Any]) -> str:
    """Create one clipboard payload for ChatGPT and the practical labs."""
    prompt = workflow_attachment_prompt(workflow)

    def block(label: str, value: Any) -> str:
        if isinstance(value, list):
            value = "\n".join(f"- {item}" for item in value)
        return f"{label}\n{value}"

    sections = [
        "AI RX COMPLETE LIVE-DEMO PACKAGE",
        block("DEMONSTRATION", workflow["title"]),
        block("CATEGORY / LEVEL / DURATION", f"{workflow['category']} / {workflow['level']} / {workflow['duration_minutes']} minutes"),
        block("PDF TO ATTACH", workflow_pdf_filename(workflow)),
        block("PROBLEM", workflow["problem"]),
        block("OBJECTIVE", workflow["objective"]),
        block("PREPARATION", workflow["preparation"]),
        block("SYNTHETIC INPUT", workflow["synthetic_input"]),
        block("DEMONSTRATION STEPS", [f"{number}. {item}" for number, item in enumerate(workflow["steps"], 1)]),
        block("PROMPT TO SUBMIT", prompt),
        block("EXPECTED OUTPUT", workflow["expected_output"]),
        block("VERIFICATION POINTS", workflow["verification_points"]),
        block("COMMON FAILURE MODES", workflow["failure_modes"]),
        block("DEBRIEF QUESTIONS", workflow["debrief_questions"]),
        block("SAFETY NOTICE", workflow.get("safety_notice", "Synthetic input only; qualified review required.")),
    ]
    return "\n\n".join(sections)


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("AI Rx title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor("#0F4C5C"), alignment=TA_LEFT, spaceAfter=5 * mm),
        "subtitle": ParagraphStyle("AI Rx subtitle", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=colors.HexColor("#B45309"), spaceAfter=3 * mm),
        "heading": ParagraphStyle("AI Rx heading", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#0F766E"), spaceBefore=4 * mm, spaceAfter=2 * mm, keepWithNext=True),
        "body": ParagraphStyle("AI Rx body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.3, leading=13.2, textColor=colors.HexColor("#17343D"), spaceAfter=2 * mm),
        "small": ParagraphStyle("AI Rx small", parent=base["BodyText"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#49646C")),
        "warning": ParagraphStyle("AI Rx warning", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8.6, leading=12, textColor=colors.HexColor("#8A3B12")),
    }


def _paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    cleaned = _clean_pdf_text(text)
    return Paragraph(escape(cleaned).replace("\n", "<br/>"), style)


def _bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(_paragraph(item, style), leftIndent=4 * mm) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=7 * mm,
        bulletFontName="Helvetica",
        bulletFontSize=6,
    )


def _header_footer(canvas: Canvas, document: SimpleDocTemplate) -> None:
    canvas.saveState()
    page_width, page_height = A4
    canvas.setFillColor(colors.HexColor("#0D222B"))
    canvas.rect(0, page_height - 17 * mm, page_width, 17 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#2DD4BF"))
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(17 * mm, page_height - 10.5 * mm, "AI Rx Live Demo Studio")
    canvas.setFillColor(colors.HexColor("#FBBF24"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(page_width - 17 * mm, page_height - 10.5 * mm, "Fictional workshop attachment")
    canvas.setStrokeColor(colors.HexColor("#C7DBDF"))
    canvas.line(17 * mm, 14 * mm, page_width - 17 * mm, 14 * mm)
    canvas.setFillColor(colors.HexColor("#49646C"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(17 * mm, 9.5 * mm, "Patient first. Doctor led. AI assisted. Qualified review required.")
    canvas.drawRightString(page_width - 17 * mm, 9.5 * mm, f"Page {document.page}")
    canvas.restoreState()


def _build_pdf(title: str, subtitle: str, metadata: list[tuple[str, str]], sections: list[tuple[str, str | list[str]]]) -> bytes:
    output = BytesIO()
    styles = _styles()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=24 * mm,
        bottomMargin=20 * mm,
        title=_clean_pdf_text(title),
        author="AI Rx Live Demo Studio",
        subject="Complete fictional input for a supervised AI practical lab",
    )
    story: list[Any] = [
        _paragraph(title, styles["title"]),
        _paragraph(subtitle, styles["subtitle"]),
    ]
    table_data = [[_paragraph(label, styles["small"]), _paragraph(value, styles["body"])] for label, value in metadata]
    table = Table(table_data, colWidths=[42 * mm, 119 * mm], repeatRows=0, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E6F5F3")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F8FBFB")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9ABFC2")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#C8DCDD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([table, Spacer(1, 2 * mm)])
    for heading, content in sections:
        heading_flowable = _paragraph(heading, styles["heading"])
        if isinstance(content, list):
            cleaned_items = [_clean_pdf_text(item) for item in content]
            story.append(KeepTogether([heading_flowable, _bullets(cleaned_items[:1], styles["body"])]))
            if len(cleaned_items) > 1:
                story.append(_bullets(cleaned_items[1:], styles["body"]))
        else:
            story.append(KeepTogether([heading_flowable, _paragraph(content, styles["body"])]))
    story.extend([
        Spacer(1, 4 * mm),
        _paragraph("Educational safety statement", styles["heading"]),
        _paragraph(
            "This PDF contains fictional or synthetic information for a supervised practical lab. It is not a diagnosis, prescription, clinical report, treatment plan, triage decision, procedure approval, or substitute for qualified professional judgement. Do not use it for real patient care.",
            styles["warning"],
        ),
    ])
    document.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return output.getvalue()


def build_prompt_sample_pdf(prompt: dict[str, Any]) -> bytes:
    """Build a complete, tailored source PDF for one of the 323 prompt combinations."""
    scenario = SPECIALTY_SCENARIOS[prompt["specialty"]]
    task = TASK_CONTEXT[prompt["category"]]
    comparison = SERIES_DATE if prompt["category"] in {"Critical appraisal", "Journal club", "Audit checklist"} else "NOT PROVIDED unless explicitly stated below"
    sources = task.get("sources", ["This fictional PDF is the only authorised source for the exercise.", "No external clinical source is supplied; any external claim must be labelled UNVERIFIED."])
    metadata = [
        ("Attachment file", prompt_pdf_filename(prompt)),
        ("Prompt combination", f"{prompt['category']} - {prompt['specialty']}"),
        ("Intended audience", task["audience"]),
        ("Intended decision/action", task["decision"]),
        ("Document/encounter date", DOCUMENT_DATE),
        ("Series/comparison date", comparison),
        ("Technical depth", task["depth"]),
    ]
    sections: list[tuple[str, str | list[str]]] = [
        ("1. Patient, professional, or population information", scenario["subject"]),
        ("2. Presenting problem or operational context", scenario["context"]),
        ("3. Procedure, investigation, or source information", scenario["source"]),
        ("4. Verified facts supplied", scenario["facts"]),
        ("5. Relevant documented negatives", scenario["negatives"]),
        ("6. Missing, uncertain, or conflicting information", scenario["missing"]),
        ("7. Local constraints and generalisation limits", scenario["constraints"]),
        ("8. Task-specific material", task["details"]),
        ("9. Approved sources", sources),
        ("10. Required output structure", prompt["output_structure"]),
        ("11. Privacy and provenance", ["All names, codes, dates, values, organisations, and scenarios in this attachment are fictional and created for teaching.", "No real patient, learner, employee, or institution is represented.", "Do not combine this exercise with identifiable or confidential information."]),
        ("12. Qualified-review checklist", ["Confirm every material statement traces to this attachment.", "Keep NOT PROVIDED fields explicit.", "Separate observation, source-supported fact, inference, and recommendation.", "Review urgency, safety-netting, citations, applicability, and patient-centred language.", "Retain the final decision, approval, communication, and follow-up with the qualified professional."]),
    ]
    return _build_pdf(
        f"Sample report: {prompt['title']}",
        "Complete fictional input for the matching copy-ready master prompt",
        metadata,
        sections,
    )


def build_workflow_sample_pdf(workflow: dict[str, Any]) -> bytes:
    """Build a complete attachment containing every field used by a live workflow."""
    metadata = [
        ("Attachment file", workflow_pdf_filename(workflow)),
        ("Demonstration", workflow["title"]),
        ("Category", workflow["category"]),
        ("Level", workflow["level"]),
        ("Duration", f"{workflow['duration_minutes']} minutes"),
        ("Document date", DOCUMENT_DATE),
        ("Intended audience", "Workshop participant using ChatGPT or an equivalent supervised practical-lab tool"),
        ("Intended decision/action", "Produce a reviewable draft for debrief and qualified professional verification."),
    ]
    sections: list[tuple[str, str | list[str]]] = [
        ("1. Problem", workflow["problem"]),
        ("2. Objective", workflow["objective"]),
        ("3. Preparation", workflow["preparation"]),
        ("4. Complete synthetic input", workflow["synthetic_input"]),
        ("5. Demonstration steps", [f"{number}. {step}" for number, step in enumerate(workflow["steps"], 1)]),
        ("6. Exact task instruction", workflow["sample_prompt"]),
        ("7. Expected output", workflow["expected_output"]),
        ("8. Verification points", workflow["verification_points"]),
        ("9. Common failure modes", workflow["failure_modes"]),
        ("10. Debrief questions", workflow["debrief_questions"]),
        ("11. Missing information", ["Any field not explicitly stated above is NOT PROVIDED.", "No real patient data, clinical image, recording, device output, or confidential institutional document is included."]),
        ("12. Safety and ownership", workflow.get("safety_notice", "Synthetic input only; qualified review required.")),
    ]
    return _build_pdf(
        f"Live-demo report: {workflow['title']}",
        "Complete fictional source attachment for ChatGPT and practical-lab use",
        metadata,
        sections,
    )
