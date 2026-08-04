"""Page renderers for the AI Rx Streamlit application."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from components.cards import tool_card
from components.comparison import render_comparison
from components.data import (
    ROOT,
    load_cases,
    load_json,
    load_prompts,
    load_quiz,
    load_tools,
    load_workflows,
    recommend_guided_workflow,
    resolve_assessment_pool,
    resolve_prompts,
    resolve_tool_results,
    resolve_workflows,
    tool_filter_match_count,
    unique_values,
    validate_catalog,
)
from components.demo_renderer import render_workflow
from components.export import as_json_bytes, tools_as_csv
from components.filters import directory_filters
from components.nudges import text_nudge
from components.prompt_sheet import render_prompt_sheet
from components.quiz import badge_for_score, render_questions
from components.sample_reports import attachment_ready_prompt, build_prompt_sample_pdf, prompt_pdf_filename
from components.safety import render_safety_gate, social_media_flags
from components.ui import configure_page, footer, metric_cards, page_header, safety_notice


def _finish() -> None:
    safety_notice()
    footer()


def _workflow_by_category(categories: list[str], key: str) -> None:
    workflows = [item for item in load_workflows() if item["category"] in categories]
    if not workflows:
        st.info("No local workflow is available for this category. Use the Prompt Library as a safe fallback.")
        return
    title = st.selectbox("Choose a demonstration", [item["title"] for item in workflows], key=f"{key}_workflow")
    selected = next(item for item in workflows if item["title"] == title)
    render_workflow(selected, key_prefix=key)


def render_home() -> None:
    configure_page("Home")
    tools, workflows, cases = load_tools(), load_workflows(), load_cases()
    st.markdown(
        """
        <section class="hero">
          <div class="eyebrow">Clinical decision workshop · Responsible AI in practice</div>
          <h1>AI <span>Rx</span> Live Demo Studio</h1>
          <p>Use complete prompts, specialty cases, evidence workflows, and structured clinical comparisons to examine how AI
          can support a decision. The workshop focuses on judgement, verification, and patient communication.</p>
          <div class="principle">Patient first. Doctor led. AI assisted. The qualified professional owns the final decision.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    safety_notice()
    actions = st.columns(3)
    with actions[0]:
        st.page_link("pages/04_Live_Demos.py", label="Start live demo", icon="▶️", width="stretch")
    with actions[1]:
        st.page_link("pages/10_Prompt_Library.py", label="Copy a prompt", icon="📋", width="stretch")
    with actions[2]:
        st.page_link("pages/11_Synthetic_Cases.py", label="AI vs Doctor", icon="⚖️", width="stretch")
    metric_cards(
        [
            (str(len(unique_values(tools, "category"))), "Tool categories", "Curated clinical and professional workflows"),
            (str(len(tools)), "Tool records", "Official links, safety notes, and demo fit"),
            (str(len(unique_values(tools, "specialties"))), "Specialties", "General, specialty, education, and research"),
            (str(len(cases)), "Specialty cases", "Ready prompt → AI view → doctor judgement"),
            (str(len(workflows)), "Live demos", "Facilitator steps and verification points"),
        ]
    )
    st.markdown("## Patient centricity is the workshop north star")
    st.markdown(
        """
        <div class="north-star" aria-label="Patient-centred decision flow">
          <div><b>01 · NEED</b>Start with the patient or service problem.</div>
          <div><b>02 · SPECIALTY</b>Add clinical context, tacit knowledge, and limits.</div>
          <div><b>03 · EVIDENCE</b>Check sources, population, date, and applicability.</div>
          <div><b>04 · AI SUPPORT</b>Organise, draft, compare, and expose missing data.</div>
          <div><b>05 · DOCTOR</b>Resolve ambiguity and own the final decision.</div>
          <div><b>06 · PATIENT</b>Explain, act, document, and follow up responsibly.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("## What do you need to do?")
    quick = [
        ("Copy a complete prompt", "Select a specialty and use a fully visible, detailed prompt without prompt engineering.", "pages/10_Prompt_Library.py"),
        ("Compare AI and Doctor", "See what AI perceived, what the doctor concluded, and which tacit cues changed the decision.", "pages/11_Synthetic_Cases.py"),
        ("Use a decision framework", "Tie AI output to evidence, uncertainty, human override, and a patient-centred action.", "pages/17_Decision_Support.py"),
        ("Document faster", "Turn a synthetic consultation into a clinician-reviewed draft note.", "pages/06_Documentation_Lab.py"),
        ("Research smarter", "Move from a PICO question to a source-checked evidence brief.", "pages/05_Research_Lab.py"),
        ("Open the resource centre", "Download the prompt booklet, presentation decks, animated invitation, and audience-specific copy.", "pages/18_Publicity_and_PPTs.py"),
    ]
    for row_start in range(0, len(quick), 3):
        columns = st.columns(3)
        for column, (title, text, path) in zip(columns, quick[row_start:row_start + 3]):
            with column:
                st.markdown(f"<div class='quick-card'><h3>{title}</h3><p>{text}</p></div>", unsafe_allow_html=True)
                st.page_link(path, label=f"Open {title.lower()}", width="stretch")
    footer()


def render_find_tool() -> None:
    configure_page("Find a Tool", "🧭")
    page_header("Route A–D", "Start with your need", "Choose a route that matches how you think during the workshop. Recommendations use the local verified catalogue and always offer a practical fallback.")
    tools = load_tools()
    tabs = st.tabs(["I have a problem", "Explore by category", "Explore by specialty", "Guided live demo"])
    with tabs[0]:
        problems = load_json("resources.json")["problem_routes"]
        problem = st.selectbox("What are you trying to do?", list(problems))
        terms = problems[problem]
        matches = [tool for tool in tools if any(term.casefold() in (tool["problem"] + " " + tool["purpose"] + " " + tool["category"]).casefold() for term in terms)]
        st.caption(f"Recommended starting points for: {problem}")
        for column, tool in zip(st.columns(min(3, max(1, len(matches[:3])))), matches[:3]):
            with column:
                tool_card(tool, key_prefix="problem")
    with tabs[1]:
        category = st.selectbox("Tool category", unique_values(tools, "category"), key="route_category")
        matches = [tool for tool in tools if tool["category"] == category]
        st.write(f"{len(matches)} tools in this category")
        for tool in matches[:8]:
            tool_card(tool, key_prefix="category")
    with tabs[2]:
        specialty = st.selectbox("Medical specialty", load_json("specialties.json"), key="route_specialty")
        matches = [tool for tool in tools if specialty in tool["specialties"]]
        if not matches:
            matches = [tool for tool in tools if "General Medicine" in tool["specialties"]][:6]
            st.info("No exact specialty record was found. Showing adaptable general-purpose options.")
        for tool in matches[:8]:
            tool_card(tool, key_prefix="specialty")
    with tabs[3]:
        row = st.columns(4)
        duration = row[0].selectbox("Time", [3, 5, 10, 15], format_func=lambda value: f"{value} minutes")
        specialty = row[1].selectbox("Specialty", load_json("specialties.json"), key="guided_specialty")
        objective = row[2].selectbox("Objective", ["Patient communication", "Documentation", "Research", "Workflow", "Professional engagement", "Diagnostic awareness"])
        level = row[3].selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
        selected, reasons = recommend_guided_workflow(
            load_workflows(),
            tools,
            duration=duration,
            specialty=specialty,
            objective=objective,
            level=level,
        )
        st.success(f"Recommended sequence for {specialty}: {selected['title']}")
        st.caption("Why this output is shown: " + " · ".join(reasons))
        render_workflow(selected, key_prefix="guided")
    _finish()


def render_directory() -> None:
    configure_page("Tool Directory", "🧰")
    page_header("Curated catalogue", "AI Tool Directory", "A curated and periodically verified directory of high-value tools relevant to medical professionals. Entries distinguish public demos from institutional products and do not treat vendor claims as clinical evidence.")
    tools = load_tools()
    tabs = st.tabs(["Browse", "Compare up to four", "Directory notes"])
    with tabs[0]:
        filters = directory_filters(tools)
        matches, exact = resolve_tool_results(tools, filters)
        if not exact:
            st.warning("No catalogue record truthfully satisfies every selected filter. Ranked alternatives are shown and labelled by how many selected criteria they match.")
            if st.button("Reset filters", type="primary"):
                for key in list(st.session_state):
                    if key.startswith("directory_"):
                        del st.session_state[key]
                st.rerun()
        else:
            st.success(f"{len(matches)} matching tools")
        maximum = st.slider("Cards to show", 6, min(30, max(6, len(matches))), min(12, max(6, len(matches)))) if len(matches) > 6 else len(matches)
        for start in range(0, maximum, 2):
            columns = st.columns(2)
            for column, tool in zip(columns, matches[start:start + 2]):
                with column:
                    if not exact:
                        matched, total = tool_filter_match_count(tool, filters)
                        st.caption(f"Closest alternative · matches {matched}/{total} selected criteria")
                    tool_card(tool, key_prefix="directory_card")
    with tabs[1]:
        render_comparison(tools)
        if st.button("Clear comparison"):
            st.session_state["compare_tools"] = []
            st.rerun()
    with tabs[2]:
        st.markdown("### How to read a record")
        st.write("A checked official URL confirms that the vendor or product page was reachable on the recorded date. It does not confirm price, India access, regulatory clearance, clinical validity, privacy compliance, or suitability for a particular institution.")
        st.write("When these details were not confirmed from a current official source, the catalogue says **Not independently verified**. Users should repeat due diligence before procurement or patient-facing use.")
        st.download_button("Download catalogue CSV", tools_as_csv(tools), "ai_rx_tools_catalog.csv", "text/csv")
    _finish()


def render_live_demos() -> None:
    configure_page("Live Demos", "▶️")
    page_header("Facilitator-ready", "Guided live demonstrations", "Each module contains synthetic input, exact steps, expected output, failure modes, debrief questions, and a clinician verification checklist.")
    workflows = load_workflows()
    category = st.selectbox("Filter demonstrations", ["All"] + sorted({item["category"] for item in workflows}))
    level = st.selectbox("Level", ["All", "Beginner", "Intermediate", "Advanced"])
    shown, exact = resolve_workflows(workflows, category, level)
    if not exact:
        st.warning("No demonstration has both selected attributes. The nearest available workflows are shown instead; the category and level on each workflow remain visible.")
    default_id = st.session_state.get("selected_demo_tool")
    index = next((i for i, item in enumerate(shown) if item.get("tool_id") == default_id), 0)
    title = st.selectbox("Demonstration", [item["title"] for item in shown], index=index)
    render_workflow(next(item for item in shown if item["title"] == title), key_prefix="live")
    _finish()


def render_research_lab() -> None:
    configure_page("Research Lab", "📚")
    page_header("Source-linked orientation", "Research and evidence lab", "Practise PICO framing, evidence-type separation, source inspection, journal-club synthesis, and uncertainty logging using fictional or openly shareable material.")
    st.info("Source-grounded does not mean clinically correct. Open cited papers, inspect populations and dates, and verify each claim.")
    _workflow_by_category(["Research & Evidence"], "research")
    _finish()


def render_documentation_lab() -> None:
    configure_page("Documentation Lab", "📝")
    page_header("Synthetic consultations only", "Clinical documentation lab", "Demonstrate how an AI scribe can draft a SOAP note, patient summary, and follow-up note without recording workshop participants or using real patient data.")
    _workflow_by_category(["Clinical Documentation"], "documentation")
    _finish()


def render_social_media_lab() -> None:
    configure_page("Social Media Lab", "📣")
    page_header("Professional, evidence-based, confidential", "Ethical social media lab", "Create useful professional content, then screen the draft for patient identifiers, unsupported claims, exaggerated outcomes, conflicts, and missing evidence.")
    _workflow_by_category(["Professional Engagement"], "social")
    st.markdown("## Ethical Social Media Checker")
    text_nudge(
        title="Need a draft to test?",
        description="Load a safe or deliberately risky synthetic example, or paste your own text below.",
        choices={
            "Safe educational announcement": "Join our clinician education session on responsible AI. We will use fictional cases and discuss evidence checks, privacy, uncertainty, and human oversight. No patient data or clinical advice will be shared.",
            "Risky claim for the checker": "Our breakthrough AI guarantees 100% accurate diagnosis and is completely safe for every patient. Message us a patient report for instant advice.",
        },
        target_key="social_draft",
        key_prefix="social_draft_nudge",
    )
    draft = st.text_area("Paste a draft for a quick rule-based screen", height=180, placeholder="Use synthetic text only. This screen does not replace editorial, legal, or institutional review.", key="social_draft")
    if st.button("Check draft", type="primary"):
        if not draft.strip():
            st.info("Enter a draft or use one of the predefined nudges above before running the screen.")
        elif flags := social_media_flags(draft):
            st.error("Review needed: " + "; ".join(flags))
        else:
            st.success("No listed phrase-level flags were detected. Evidence, consent, conflicts, and context still require human review.")
    st.warning("Never use a patient story, image, report, or testimonial without appropriate consent and institutional or legal clearance.")
    _finish()


def render_precision_diagnostics() -> None:
    configure_page("Precision Diagnostics", "🩻")
    page_header("Educational simulation", "Precision diagnostics and image-analysis awareness", "Explore how clinical AI products differ by modality, user, integration, regulatory position, and public access. The image lab contains labelled simulation placeholders, not outputs from a validated diagnostic model.")
    if not render_safety_gate("diagnostics_gate"):
        safety_notice()
        footer()
        return
    tools = [tool for tool in load_tools() if tool["category"] == "Precision Diagnostics"]
    st.markdown("## Product access map")
    access = st.selectbox("Product group", sorted({tool["access_type"] for tool in tools}))
    matching = [tool for tool in tools if tool["access_type"] == access]
    for start in range(0, min(8, len(matching)), 2):
        columns = st.columns(2)
        for column, tool in zip(columns, matching[start:start + 2]):
            with column:
                tool_card(tool, key_prefix="diagnostic")
    st.markdown("## Educational image-analysis lab")
    index = load_json("image_index.json")
    modality = st.selectbox("Modality", sorted({item["modality"] for item in index}))
    cases = [item for item in index if item["modality"] == modality]
    case = st.selectbox("Simulation case", [item["title"] for item in cases])
    selected = next(item for item in cases if item["title"] == case)
    left, right = st.columns([1.15, 1])
    with left:
        st.image(str(ROOT / selected["path"]), caption=selected["alt_text"], width="stretch")
        st.error("Educational simulation—not a clinical report")
    with right:
        st.write(f"**Body region:** {selected['body_region']}")
        st.write(f"**Illustrative confidence:** {selected['illustrative_confidence']} (invented for interface teaching)")
        st.markdown("#### Image-quality checklist")
        for item in selected["quality_checklist"]:
            st.checkbox(item, key=f"image_{selected['id']}_{hashlib.md5(item.encode()).hexdigest()[:6]}")
        st.markdown("#### Observation task")
        st.write(selected["observation_task"])
        st.write(f"**Differential considerations:** {selected['differential_considerations']}")
        st.write(f"**Ground truth:** {selected['ground_truth']}")
        st.write(f"**Limitations:** {selected['limitations']}")
    st.info("This visualisation demonstrates how an AI-assisted workflow may appear. It is not generated by a validated diagnostic model.")
    _finish()


def render_workflow_lab() -> None:
    configure_page("Workflow Lab", "🗂️")
    page_header("Non-clinical automation", "Workflow and knowledge-management lab", "Build a quality-improvement board, research tracker, knowledge hub, audit checklist, or CME plan without placing identifiable patient data in an unapproved environment.")
    _workflow_by_category(["Workflow & Knowledge", "Administrative Productivity"], "workflow_lab")
    _finish()


def render_prompt_library() -> None:
    configure_page("Prompt Library", "💬")
    page_header("Choose · review · use", "Prompt library for doctors", "Select a task and specialty, then review the complete instruction before copying it. Each prompt stays expanded on the page, including its clinical boundaries and verification steps.")
    prompts = load_prompts()
    st.session_state.setdefault("prompt_pack", [])
    metric_cards([
        (str(len(prompts)), "Pre-loaded prompts", "No prompt engineering required during the session"),
        (str(len({item['specialty'] for item in prompts})), "Specialties", "Clinical, research, education, and administration"),
        (str(len({item['category'] for item in prompts})), "Tasks", "Communication, evidence, workflow, teaching, and more"),
    ])
    st.markdown("### 1. Find the right prompt")
    text_nudge(
        title="Not sure what to type?",
        description="Load a common clinical or academic task, or write your own search.",
        choices={
            "Explain a diagnosis to a patient": "patient-friendly explanation",
            "Prepare a referral summary": "referral summary",
            "Run a journal club": "journal club",
            "Review an image-analysis task": "image-analysis observation checklist",
            "Plan a literature search": "literature search",
        },
        target_key="prompt_query",
        key_prefix="prompt_search_nudge",
    )
    row = st.columns(3)
    query = row[0].text_input("Search prompts", placeholder="discharge, journal club, referral", key="prompt_query")
    category = row[1].selectbox("Category", ["All"] + sorted({item["category"] for item in prompts}))
    specialty = row[2].selectbox("Specialty", ["All"] + sorted({item["specialty"] for item in prompts}))
    filtered, exact = resolve_prompts(prompts, query=query, category=category, specialty=specialty)
    if not exact:
        st.warning("No prompt matches every input exactly. The closest adaptable prompts are shown; their task and specialty labels remain visible so the mismatch is not hidden.")
    st.caption(f"{len(filtered)} {'exactly matching' if exact else 'ranked alternative'} prompts are available for this input state.")
    st.markdown("### 2. Select and review")
    selected_title = st.selectbox("Choose one complete prompt", [item["title"] for item in filtered])
    item = next(entry for entry in filtered if entry["title"] == selected_title)
    st.markdown(
        f"<div class='prompt-head'><h3>{escape(item['title'])}</h3>"
        f"<div class='prompt-meta'>{escape(item['use_case'])}</div></div>",
        unsafe_allow_html=True,
    )
    attachment_prompt = attachment_ready_prompt(item)
    sample_filename = prompt_pdf_filename(item)
    st.markdown("#### Matching sample PDF attachment")
    st.write("This fictional report is unique to the selected specialty-task combination and supplies every input field used by the prompt. Download it, attach it in ChatGPT, and then copy the full prompt below.")
    st.download_button(
        "1 · Download sample PDF to upload",
        build_prompt_sample_pdf(item),
        file_name=sample_filename,
        mime="application/pdf",
        key=f"sample_pdf_{item['id']}",
        type="primary",
        width="stretch",
    )
    render_prompt_sheet(attachment_prompt, label=item["title"], key_prefix=f"library_{item['id']}")
    st.caption(f"The prompt names {sample_filename} and uses that attachment as its complete fictional source. No square-bracket fields need to be replaced.")
    st.markdown("### 3. Use or save for the session")
    actions = st.columns(4)
    actions[0].download_button("Download this prompt", attachment_prompt, f"{item['id']}.txt", "text/plain", key=f"prompt_{item['id']}", width="stretch")
    packed = item["id"] in st.session_state["prompt_pack"]
    if actions[1].button("Remove from session" if packed else "Add to session pack", key=f"pack_{item['id']}", width="stretch"):
        if packed:
            st.session_state["prompt_pack"].remove(item["id"])
        else:
            st.session_state["prompt_pack"].append(item["id"])
        st.rerun()
    filtered_text = "\n\n".join(f"{entry['title']}\n{'='*88}\n{attachment_ready_prompt(entry)}" for entry in filtered)
    actions[2].download_button("Download filtered set", filtered_text, "AI_Rx_Filtered_Prompts.txt", "text/plain", width="stretch")
    booklet = ROOT / "assets" / "handouts" / "AI_Rx_Copy_Ready_Prompt_Booklet.html"
    if booklet.exists():
        actions[3].download_button("Download print booklet", booklet.read_bytes(), booklet.name, "text/html", width="stretch")
    if st.session_state["prompt_pack"]:
        packed_prompts = [entry for entry in prompts if entry["id"] in st.session_state["prompt_pack"]]
        pack_text = "\n\n".join(f"{entry['title']}\n{'='*88}\n{attachment_ready_prompt(entry)}" for entry in packed_prompts)
        st.markdown(f"<div class='decision-box'><strong>Session prompt pack</strong><br>{len(packed_prompts)} selected prompts, ready to share with participants.</div>", unsafe_allow_html=True)
        pack_actions = st.columns([1, 1, 2])
        pack_actions[0].download_button("Download session pack", pack_text, "AI_Rx_Session_Prompt_Pack.txt", "text/plain", width="stretch")
        if pack_actions[1].button("Clear session pack", width="stretch"):
            st.session_state["prompt_pack"] = []
            st.rerun()
    st.info("For hard copy, download the booklet, open it in a browser, and choose Print. It contains core patient-explanation and differential-reasoning prompts across all 19 specialties.")
    _finish()


def render_cases() -> None:
    configure_page("Synthetic Cases", "🧪")
    page_header("Progressive clinical reveal", "Specialty AI-versus-Doctor case library", "Read the source facts first, inspect the AI interpretation second, and reveal the clinician's conclusion only when the group has committed to its own reasoning.")
    cases = load_cases()
    specialty = st.selectbox("Specialty", ["All"] + sorted({item["specialty"] for item in cases}))
    filtered = [item for item in cases if specialty == "All" or item["specialty"] == specialty]
    if not filtered:
        filtered = cases[:5]
        st.info("No exact specialty case was found. Showing adaptable fictional cases.")
    selected_title = st.selectbox("Case", [f"{item['patient_alias']} — {item['presenting_problem']}" for item in filtered])
    case = filtered[[f"{item['patient_alias']} — {item['presenting_problem']}" for item in filtered].index(selected_title)]
    stage_key = f"case_stage_{case['id']}"
    st.session_state.setdefault(stage_key, 1)
    stage = st.session_state[stage_key]
    rail = []
    for number, label in [(1, "Source facts and prompt"), (2, "AI interpretation"), (3, "Clinical comparison")]:
        state = "done" if number < stage else "active" if number == stage else ""
        rail.append(f"<div class='reveal-step {state}'><strong>{number}</strong> · {label}</div>")
    st.markdown(f"<div class='reveal-rail'>{''.join(rail)}</div>", unsafe_allow_html=True)
    st.markdown(
        f"""<div class='case-banner'><div class='date'>{escape(case['document_date'])} · {escape(case['specialty'])}</div>
        <h2>{escape(case['presenting_problem'])}</h2><p>{escape(case['patient_information'])}</p>
        <p><strong>Procedure/source:</strong> {escape(case['procedure_information'])}</p>
        <p><strong>Date and series:</strong> {escape(case['series_information'])}</p></div>""",
        unsafe_allow_html=True,
    )
    st.warning("Fictional teaching case with no patient identifiers. A qualified clinician should review the case before workshop delivery.")
    st.markdown("## 1. Ready prompt")
    st.write("Copy this prompt directly. It already contains the case, decision-support structure, generalisation guard, and clinician-verification boundary.")
    render_prompt_sheet(case["ready_prompt"], label=f"Case prompt for {case['patient_alias']}", key_prefix=f"case_{case['id']}")
    st.download_button("Download this case prompt", case["ready_prompt"], f"{case['id']}_prompt.txt", "text/plain", width="stretch")
    if stage == 1:
        if st.button("Reveal the AI interpretation", type="primary", width="stretch"):
            st.session_state[stage_key] = 2
            st.rerun()
        st.info("Pause here. Ask participants to identify the decision, missing information, and the features that could change their interpretation.")
        _finish()
        return
    st.markdown("## 2. AI output and perceived diagnosis")
    st.markdown(f"<div class='ai-panel'><h3>AI pattern-based view</h3><p>{escape(case['simulated_ai_output'])}</p></div>", unsafe_allow_html=True)
    if stage == 2:
        controls = st.columns([2, 1])
        if controls[0].button("Reveal the clinician comparison", type="primary", width="stretch"):
            st.session_state[stage_key] = 3
            st.rerun()
        if controls[1].button("Reset case", width="stretch"):
            st.session_state[stage_key] = 1
            st.rerun()
        st.info("Before revealing the comparison, ask the group what the AI may have over-weighted, omitted, or treated with too much confidence.")
        _finish()
        return
    st.markdown("## 3. AI versus Doctor")
    st.markdown(
        f"""<div class='ai-doctor-grid'>
        <div class='ai-panel'><h3>What AI perceived</h3><p>{escape(case['ai_perceived_diagnosis'])}</p>
        <p><strong>Typical weakness:</strong> It may over-weight surface patterns, one snapshot, or an incidental finding.</p></div>
        <div class='doctor-panel'><h3>Clinician conclusion in the teaching case</h3><p>{escape(case['doctor_actual_diagnosis'])}</p>
        <p><strong>Tacit knowledge:</strong> {escape(case['tacit_knowledge_cues'])}</p></div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='decision-box'><strong>Decision-support value</strong><br>{escape(case['decision_support_value'])}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='patient-star'><h3>Patient-centred next action</h3><p>{escape(case['patient_centricity_action'])}</p><p><strong>Generalisation guard:</strong> {escape(case['generalisation_note'])}</p></div>", unsafe_allow_html=True)
    st.markdown("### Literature-only consent reminder")
    st.write(case["consent_note"])
    st.markdown("### Source information supplied to the exercise")
    left, right = st.columns(2)
    with left:
        st.write(f"**Alias:** {case['patient_alias']}")
        st.write(f"**Age range:** {case['age_range']}")
        st.write(f"**Sex, where relevant:** {case['sex']}")
        st.write(f"**Presenting problem:** {case['presenting_problem']}")
        st.write(f"**History:** {case['relevant_history']}")
        st.write(f"**Examination:** {case['examination_summary']}")
        st.write(f"**Investigations:** {case['investigation_data']}")
    with right:
        st.write(f"**Learning objective:** {case['learning_objective']}")
        st.write(f"**Suitable AI tools:** {', '.join(case['suitable_ai_tools'])}")
        st.write(f"**Expected workshop output:** {case['expected_workshop_output']}")
        st.write(f"**Safety considerations:** {case['safety_considerations']}")
    st.download_button("Download case JSON", as_json_bytes(case), f"{case['id']}.json", "application/json")
    if st.button("Reset case for the next group", width="stretch"):
        st.session_state[stage_key] = 1
        st.rerun()
    _finish()


def render_decision_support() -> None:
    configure_page("Decision Support", "⚖️")
    page_header("AI organises · Doctor decides", "Patient-centred decision-support framework", "Use AI only when its output feeds a defined decision, an accountable reviewer, and a patient-centred action. A fluent answer without a decision boundary is workshop noise.")
    st.markdown(
        """<div class='north-star'>
        <div><b>1 · INPUT</b>Is the information safe, sufficient, dated, and correctly sequenced?</div>
        <div><b>2 · QUESTION</b>Which decision or action is this output meant to inform?</div>
        <div><b>3 · EVIDENCE</b>Which facts, sources, and populations support the output?</div>
        <div><b>4 · LIMITS</b>What is missing, uncertain, out of scope, or non-generalising?</div>
        <div><b>5 · OWNER</b>Which qualified professional reviews and can override it?</div>
        <div><b>6 · PATIENT</b>How will the decision be explained, documented, and followed up?</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("## The AI-versus-Doctor boundary")
    left, right = st.columns(2)
    with left:
        st.markdown("<div class='ai-panel'><h3>AI can support</h3><p>Structuring a timeline, finding missing fields, converting technical language, organising possible considerations, drafting a search strategy, comparing authorised sources, and creating a review checklist.</p></div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='doctor-panel'><h3>The doctor must own</h3><p>Clinical examination, interpretation of unavailable context, final diagnosis, treatment, procedure, triage, consent, communication, accountability, and the response when evidence and AI output conflict.</p></div>", unsafe_allow_html=True)
    cases = load_cases()
    specialty = st.selectbox("Apply the framework to a specialty", sorted({item["specialty"] for item in cases}))
    case = next(item for item in cases if item["specialty"] == specialty)
    st.markdown(f"### Example: {case['presenting_problem']}")
    table = pd.DataFrame([
        {"Decision layer": "AI contribution", "Workshop example": case["simulated_ai_output"]},
        {"Decision layer": "Doctor contribution", "Workshop example": case["doctor_actual_diagnosis"]},
        {"Decision layer": "Tacit knowledge", "Workshop example": case["tacit_knowledge_cues"]},
        {"Decision layer": "Patient-centred action", "Workshop example": case["patient_centricity_action"]},
    ])
    st.dataframe(table, width="stretch", hide_index=True)
    st.markdown("## Decision-readiness check")
    st.write("Complete all six checks before treating an AI output as ready for qualified review or downstream use.")
    readiness_items = [
        ("The decision is stated in one sentence.", "The team knows exactly what the output is meant to inform."),
        ("The input is safe, dated, and sufficiently complete.", "Identifiers, missing fields, chronology, and source quality have been checked."),
        ("Plausible options and alternatives are visible.", "The output does not collapse uncertainty into one convenient answer."),
        ("Unsupported claims and uncertainty are marked.", "The reviewer can see where evidence is missing or unverified."),
        ("The next action is safe and proportionate.", "The action accounts for urgency, reversibility, and the cost of error."),
        ("A qualified owner can verify, override, communicate, and follow up.", "Responsibility is assigned before the output moves forward."),
    ]
    readiness = []
    readiness_columns = st.columns(2)
    for index, (label, help_text) in enumerate(readiness_items):
        with readiness_columns[index % 2]:
            readiness.append(st.checkbox(label, help=help_text, key=f"decision_ready_{case['id']}_{index}"))
    completed = sum(readiness)
    st.progress(completed / len(readiness_items), text=f"{completed} of {len(readiness_items)} checks complete")
    if completed == len(readiness_items):
        st.success("Ready for qualified professional review. This checklist does not convert the AI output into a clinical decision.")
    elif completed >= 4:
        st.warning("Almost ready. Resolve the remaining checks before the output moves forward.")
    else:
        st.info("The output is not decision-ready. Keep it in draft status.")
    st.page_link("pages/11_Synthetic_Cases.py", label="Open the full AI-versus-Doctor case", icon="🧪", width="stretch")
    _finish()


def render_publicity_resources() -> None:
    configure_page("Publicity and PPTs", "🎬")
    page_header("Teaching files · participant handouts · invitation assets", "Workshop resource centre", "Download the presentation decks, prompt packs, animated invitation, and audience-specific copy. Keep promotional content separate from clinical teaching material.")
    resources = load_json("resources.json")
    promo = ROOT / "assets" / "marketing" / "AI_Rx_Workshop_Promo.gif"
    if promo.exists():
        st.markdown("## Animated workshop promo")
        st.image(str(promo), caption="AI Rx workshop animation", width="stretch")
        st.download_button("Download promo animation", promo.read_bytes(), promo.name, "image/gif", width="stretch")
    audience = st.selectbox("Choose the publicity audience", list(resources["audience_marketing"]))
    copy = resources["audience_marketing"][audience]
    st.markdown(f"<div class='audience-copy'><h2>{escape(copy['headline'])}</h2><p>{escape(copy['copy'])}</p><p><strong>Call to action:</strong> {escape(copy['cta'])}</p></div>", unsafe_allow_html=True)
    st.markdown("### Copy-ready platform post")
    st.code(copy["platform_post"], language=None, wrap_lines=True)
    st.download_button("Download audience copy", "\n\n".join([copy["headline"], copy["copy"], copy["cta"], copy["platform_post"]]), f"AI_Rx_{audience.replace(' ', '_')}_Publicity.txt", "text/plain")
    st.markdown("## Included PowerPoint decks")
    presentation_dir = ROOT / "assets" / "presentations"
    decks = sorted(presentation_dir.glob("*.pptx")) if presentation_dir.exists() else []
    if not decks:
        st.info("Presentation files are generated during the project build and will appear here.")
    for deck in decks:
        st.download_button(f"Download {deck.stem.replace('_', ' ')}", deck.read_bytes(), deck.name, "application/vnd.openxmlformats-officedocument.presentationml.presentation", key=f"deck_{deck.name}", width="stretch")
    st.markdown("## Prompt handouts")
    handout_dir = ROOT / "assets" / "handouts"
    for handout in sorted(handout_dir.glob("AI_Rx_Copy_Ready_Prompt_Booklet.*")) if handout_dir.exists() else []:
        mime = "text/html" if handout.suffix == ".html" else "text/plain"
        st.download_button(f"Download {handout.name}", handout.read_bytes(), handout.name, mime, key=f"handout_{handout.name}", width="stretch")
    st.markdown("### Consent stays literature-only")
    st.info(resources["literature_only_consent"])
    st.caption("Keep audience publicity, clinical teaching, and consent material as separate assets. Marketing copy must never imply guaranteed outcomes or autonomous diagnosis.")
    _finish()


def render_assessment() -> None:
    configure_page("Assessment", "✅")
    page_header("Professional learning check", "Assessment and reflection", "Use confidence ratings, knowledge questions, case-based risks, and post-session reflection to check whether participants can select and supervise tools safely.")
    questions = load_quiz()
    st.markdown("### Confidence check")
    pre = st.slider("Before this workshop, how confident were you in supervising AI output?", 1, 5, 2)
    post = st.slider("How confident are you now?", 1, 5, 3)
    st.caption(f"Self-reported change: {post - pre:+d} points. Confidence is not a substitute for competence or institutional approval.")
    category = st.selectbox("Question set", ["Mixed"] + sorted({item["category"] for item in questions}))
    count = st.select_slider("Number of questions", options=[5, 10, 15, 20], value=10)
    pool, supplemented = resolve_assessment_pool(questions, category, count)
    if supplemented:
        st.info(f"This category contains fewer than {count} questions. {supplemented} clearly labelled questions from other safety categories complete the requested set.")
    score, total = render_questions(pool, f"assessment_{category}", count)
    st.markdown(f"### Current score: {score}/{total}")
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Completion badge</div><div class='metric-value'>{badge_for_score(score, total)}</div><div class='metric-note'>Awarded for this practice set; not a professional credential.</div></div>", unsafe_allow_html=True)
    text_nudge(
        title="Reflection starter",
        description="Choose a sentence stem if a blank box slows you down.",
        choices={
            "Verification habit": "The AI task I will change is ____. Before using the output, I will verify ____ against ____.",
            "Patient communication": "I will use AI to draft ____, but I will personally review ____ before explaining it to the patient.",
            "Research workflow": "I will use AI to organise ____. I will open and verify every source used for ____.",
        },
        target_key="assessment_reflection",
        key_prefix="assessment_reflection_nudge",
    )
    st.text_area("Reflection: one AI task you will change, one safeguard you will add, and one question you still have", key="assessment_reflection")
    _finish()


def render_ethics() -> None:
    configure_page("Ethics and Safety", "🛡️")
    page_header("Clinical accountability remains human", "Responsible-AI centre", "Use this page before any demonstration involving patient-like content, medical images, clinical notes, or automated communication.")
    render_safety_gate("ethics_gate")
    topics = load_json("resources.json")["ethics_topics"]
    for start in range(0, len(topics), 3):
        columns = st.columns(3)
        for column, topic in zip(columns, topics[start:start + 3]):
            with column:
                st.markdown(f"<div class='quick-card'><h3>{topic['title']}</h3><p>{topic['description']}</p></div>", unsafe_allow_html=True)
    st.markdown("## Before procurement or deployment")
    st.write("Confirm intended use, data flows, retention, subcontractors, security controls, evidence, device status, local regulation, consent processes, failure handling, audit logs, human override, and institutional accountability. A vendor statement is not the same as independent verification.")
    st.page_link("pages/08_Precision_Diagnostics.py", label="Continue to diagnostic simulation", icon="🩻")
    _finish()


def _facilitator_allowed() -> bool:
    expected = os.getenv("FACILITATOR_PASSWORD", "")
    if not expected:
        st.caption("Local facilitator mode is open because no FACILITATOR_PASSWORD environment variable is configured.")
        return True
    supplied = st.text_input("Facilitator password", type="password")
    return bool(supplied) and hmac.compare_digest(supplied, expected)


def render_facilitator() -> None:
    configure_page("Facilitator Mode", "🎙️")
    page_header("Presentation control", "Facilitator mode", "Plan a timed sequence, keep notes private, mark demonstrations complete, run a quick poll, and export the workshop plan.")
    if not _facilitator_allowed():
        st.info("Enter the configured facilitator password to continue.")
        footer()
        return
    tools = load_tools()
    row = st.columns(4)
    duration = row[0].selectbox("Session duration", [30, 60, 90])
    specialty = row[1].selectbox("Participant specialty", load_json("specialties.json"))
    objective = row[2].selectbox("Workshop objective", ["Balanced", "AI versus Doctor", "Patient centricity", "Communication", "Documentation", "Research", "Workflow", "Diagnostic awareness"])
    presentation = row[3].toggle("Presentation-friendly mode")
    if presentation:
        st.markdown("<style>[data-testid='stSidebar']{display:none}.block-container{max-width:1450px;padding-top:1rem}</style>", unsafe_allow_html=True)
    planned_ids = set(st.session_state.get("workshop_tools", []))
    planned_names = [tool["name"] for tool in tools if tool["id"] in planned_ids]
    recommended = planned_names or load_json("resources.json")["recommended_sequences"][str(duration)]
    selected_names = st.multiselect("Choose demonstrations", [tool["name"] for tool in tools], default=recommended)
    selected = [tool for tool in tools if tool["name"] in selected_names]
    if not selected:
        selected = [tool for tool in tools if tool["name"] in recommended]
        st.info("No demonstrations are selected. A predefined sequence is shown below so the plan never becomes a dead end; choose one or more demonstrations above to replace it.")
    st.markdown("### Workshop sequence")
    plan_rows = []
    for index, tool in enumerate(selected, start=1):
        columns = st.columns([.5, 3, 1, 1])
        columns[0].write(index)
        columns[1].write(f"**{tool['name']}** — {tool['purpose']}")
        columns[2].write(f"{tool['demo_duration_minutes']} min")
        completed = columns[3].checkbox("Done", key=f"fac_done_{tool['id']}")
        plan_rows.append({"order": index, "tool": tool["name"], "duration_minutes": tool["demo_duration_minutes"], "completed": completed, "specialty": specialty, "objective": objective})
    notes = st.text_area("Private facilitator notes", placeholder="These notes remain in this browser session and are excluded from participant display.")
    with st.expander("Quick poll"):
        question = st.text_input("Poll question", "Which workflow would save you the most time this week?")
        options = st.text_input("Options separated by commas", "Documentation, Patient communication, Research, Workflow management")
        display_question = question.strip() or "Which workflow would save you the most time this week?"
        option_items = [item.strip() for item in options.split(",") if item.strip()]
        if not option_items:
            option_items = ["Documentation", "Patient communication", "Research", "Workflow management"]
            st.info("No poll options were entered. Predefined workshop options are shown instead.")
        st.write(f"**Live prompt:** {display_question}")
        for option in option_items:
            st.button(option, key=f"poll_{hashlib.md5(option.encode()).hexdigest()[:8]}")
    export = {"duration_minutes": duration, "specialty": specialty, "objective": objective, "sequence": plan_rows, "facilitator_notes": notes}
    st.download_button("Export workshop plan", as_json_bytes(export), "ai_rx_workshop_plan.json", "application/json", type="primary")
    _finish()


def render_about() -> None:
    configure_page("About the Developer", "👤")
    profile = load_json("resources.json")["facilitator"]
    page_header("About the developer", profile["tagline"], profile["summary"])
    left, right = st.columns([1, 2.15], gap="large")
    with left:
        st.image(profile["profile_image_url"], caption=profile["name"], width="stretch")
        st.markdown(
            f"<div class='developer-card about-identity'><div class='about-kicker'>CURRENT ROLE</div>"
            f"<strong>{escape(profile['role'])}</strong><br><span class='muted'>{escape(profile['institution'])}</span>"
            f"<div class='about-focus'>{escape(profile['focus_statement'])}</div></div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"<div class='developer-card about-intro'><div class='about-kicker'>RESEARCHER · EDUCATOR · BUILDER</div>"
            f"<h2>{escape(profile['name'])}</h2><p>{escape(profile['bio'])}</p>"
            f"<blockquote>{escape(profile['principle'])}</blockquote></div>",
            unsafe_allow_html=True,
        )
        st.markdown("### Core expertise")
        chips = "".join(f"<span class='expertise-chip'>{escape(item)}</span> " for item in profile["expertise"])
        st.markdown(f"<div class='about-chip-cloud'>{chips}</div>", unsafe_allow_html=True)

    st.markdown("## Academic foundation")
    education_columns = st.columns(3)
    for column, degree in zip(education_columns, profile["education"]):
        with column:
            st.markdown(
                f"<div class='about-education'><div class='about-mark'>{escape(degree['mark'])}</div>"
                f"<h3>{escape(degree['degree'])}</h3><p>{escape(degree['institution'])}</p>"
                f"<span>{escape(degree['focus'])}</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown("## Research and applied work")
    st.caption("Six connected areas where technical depth is tied to responsible, real-world decisions.")
    for start in range(0, len(profile["research_areas"]), 3):
        columns = st.columns(3)
        for column, area in zip(columns, profile["research_areas"][start:start + 3]):
            with column:
                tags = "".join(f"<span>{escape(tag)}</span>" for tag in area["tags"])
                st.markdown(
                    f"<div class='about-research'><div class='about-research-icon'>{escape(area['icon'])}</div>"
                    f"<h3>{escape(area['title'])}</h3><p>{escape(area['description'])}</p>"
                    f"<div class='about-mini-tags'>{tags}</div></div>",
                    unsafe_allow_html=True,
                )

    st.markdown("## Academic and professional trajectory")
    timeline_columns = st.columns(2)
    for index, item in enumerate(profile["experience"]):
        with timeline_columns[index % 2]:
            st.markdown(
                f"<div class='about-timeline'><div class='about-year'>{escape(item['period'])}</div>"
                f"<h3>{escape(item['role'])}</h3><strong>{escape(item['organisation'])}</strong>"
                f"<p>{escape(item['description'])}</p></div>",
                unsafe_allow_html=True,
            )

    st.markdown("## From classroom to boardroom")
    teaching_left, teaching_right = st.columns([1.35, 1], gap="large")
    with teaching_left:
        st.markdown(
            f"<div class='developer-card about-teaching'><h3>Teaching and learning design</h3>"
            f"<p>{escape(profile['teaching_summary'])}</p></div>",
            unsafe_allow_html=True,
        )
        teaching_chips = "".join(f"<span class='expertise-chip'>{escape(item)}</span> " for item in profile["teaching_areas"])
        st.markdown(f"<div class='about-chip-cloud'>{teaching_chips}</div>", unsafe_allow_html=True)
    with teaching_right:
        st.markdown(
            f"<div class='developer-card about-philosophy'><div class='about-kicker'>TEACHING PHILOSOPHY</div>"
            f"<blockquote>{escape(profile['teaching_philosophy'])}</blockquote></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"<div class='about-connect'><div><div class='about-kicker'>OPEN TO MEANINGFUL CONVERSATIONS</div>"
        f"<h2>Research, teaching and applied AI collaboration</h2><p>{escape(profile['collaboration'])}</p>"
        f"<strong>{escape(profile['email'])}</strong></div></div>",
        unsafe_allow_html=True,
    )
    links = st.columns(4)
    links[0].link_button("Portfolio", profile["portfolio_url"], width="stretch")
    links[1].link_button("LinkedIn", profile["linkedin"], width="stretch")
    links[2].link_button("GitHub", profile["github"], width="stretch")
    links[3].link_button("ORCID", profile["orcid"], width="stretch")
    st.caption(f"Profile details verified against the developer's public portfolio on {profile['profile_last_checked']}.")
    _finish()


@st.cache_data(ttl=900, show_spinner=False)
def _check_url(url: str) -> tuple[str, int | None]:
    try:
        import requests
        response = requests.get(url, timeout=6, allow_redirects=True, headers={"User-Agent": "AI-Rx-Workshop-Link-Checker/1.0"})
        return ("Reachable" if response.status_code < 400 else "Review", response.status_code)
    except Exception:
        return "Could not verify", None


def render_admin() -> None:
    configure_page("Catalogue Admin", "⚙️")
    page_header("Local catalogue maintenance", "Catalogue administrator", "Edit descriptions, add records, refresh verification dates, import or export data, and optionally check official URLs. Changes remain in the current session unless exported and committed to the project.")
    if not _facilitator_allowed():
        st.info("Enter the configured facilitator password to continue.")
        footer()
        return
    st.session_state.setdefault("admin_tools", load_tools())
    tools = st.session_state["admin_tools"]
    tabs = st.tabs(["Edit a tool", "Add a tool", "Import or export", "URL health"])
    with tabs[0]:
        name = st.selectbox("Tool", [tool["name"] for tool in tools])
        index = next(i for i, tool in enumerate(tools) if tool["name"] == name)
        record = dict(tools[index])
        description = st.text_area("Purpose", record["purpose"])
        official_url = st.text_input("Official URL", record["official_url"])
        verified = st.date_input("Verification date")
        if st.button("Apply session edit", type="primary"):
            record.update({"purpose": description, "official_url": official_url, "last_verified": verified.isoformat()})
            tools[index] = record
            st.session_state["admin_tools"] = tools
            st.success("Session copy updated. Export the catalogue to preserve the change.")
    with tabs[1]:
        with st.form("add_tool"):
            new_name = st.text_input("Tool name")
            new_url = st.text_input("Official URL")
            new_category = st.selectbox("Category", unique_values(tools, "category"))
            new_purpose = st.text_area("Purpose")
            submitted = st.form_submit_button("Add to session catalogue")
        if submitted:
            base = dict(tools[0])
            base.update({
                "id": new_name.casefold().replace(" ", "-")[:60], "name": new_name,
                "official_url": new_url, "category": new_category, "purpose": new_purpose,
                "verification_status": "Administrator-added; review required", "last_verified": "Not checked",
                "source_urls": [new_url] if new_url else [], "regulatory_status": "Not independently verified",
                "evidence_status": "Not independently verified", "pricing_detail": "Not independently verified",
            })
            errors = validate_catalog(tools + [base])
            if errors.get(base["id"]):
                st.error("Cannot add: " + "; ".join(errors[base["id"]]))
            else:
                tools.append(base)
                st.session_state["admin_tools"] = tools
                st.success("Tool added to the session catalogue.")
    with tabs[2]:
        upload = st.file_uploader("Import tools JSON", type=["json"])
        if upload is not None and st.button("Validate and import"):
            try:
                imported = json.load(upload)
                errors = validate_catalog(imported)
                if errors:
                    st.error(f"Import rejected: {len(errors)} invalid records.")
                    st.json(errors)
                else:
                    st.session_state["admin_tools"] = imported
                    st.success(f"Imported {len(imported)} records into this session.")
            except Exception as exc:
                st.error(f"Import failed: {exc}")
        st.download_button("Export JSON", as_json_bytes(tools), "tools_catalog.json", "application/json")
        st.download_button("Export CSV", tools_as_csv(tools), "tools_catalog.csv", "text/csv")
    with tabs[3]:
        sample_size = st.slider("URLs to check", 1, min(20, len(tools)), 5)
        if st.button("Run optional URL-health check"):
            with st.spinner("Checking selected official pages with short timeouts…"):
                results = [{"Tool": tool["name"], "URL": tool["official_url"], "Status": _check_url(tool["official_url"])[0], "HTTP": _check_url(tool["official_url"])[1]} for tool in tools[:sample_size]]
            st.dataframe(pd.DataFrame(results), width="stretch")
            st.caption("A successful HTTP response does not verify pricing, privacy, regulation, evidence, or clinical suitability.")
    _finish()
