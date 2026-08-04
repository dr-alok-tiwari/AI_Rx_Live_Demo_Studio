"""Render complete demonstration workflows from local JSON."""

from __future__ import annotations

import streamlit as st
from components.prompt_sheet import render_copy_button, render_prompt_sheet
from components.sample_reports import (
    build_workflow_sample_pdf,
    complete_workflow_copy_package,
    workflow_attachment_prompt,
    workflow_pdf_filename,
)
from components.safety import clinician_verification_checklist


def render_workflow(workflow: dict, key_prefix: str = "workflow") -> None:
    attachment_prompt = workflow_attachment_prompt(workflow)
    copy_package = complete_workflow_copy_package(workflow)
    pdf_filename = workflow_pdf_filename(workflow)
    st.markdown(f"## {workflow['title']}")
    st.caption(f"{workflow['duration_minutes']} minutes · {workflow['level']} · {workflow['category']}")
    st.markdown("### One-click ChatGPT and practical-lab package")
    st.write("Download the matching fictional PDF, attach it in ChatGPT, then copy the complete demonstration package in one click.")
    package_actions = st.columns(2)
    package_actions[0].download_button(
        "1 · Download sample PDF attachment",
        build_workflow_sample_pdf(workflow),
        file_name=pdf_filename,
        mime="application/pdf",
        key=f"{key_prefix}_pdf_{workflow['id']}",
        width="stretch",
    )
    package_actions[1].download_button(
        "Download complete lab package",
        copy_package,
        file_name=f"{workflow['id']}_complete_lab_package.txt",
        mime="text/plain",
        key=f"{key_prefix}_package_{workflow['id']}",
        width="stretch",
    )
    render_copy_button(
        copy_package,
        button_label="2 · Copy complete live-demo package for ChatGPT / lab",
        success_label="Complete live-demo package copied",
        key_prefix=f"{key_prefix}_copy_all_{workflow['id']}",
    )
    columns = st.columns(2)
    with columns[0]:
        st.markdown("#### Problem")
        st.write(workflow["problem"])
        st.markdown("#### Objective")
        st.write(workflow["objective"])
        st.markdown("#### Preparation")
        for item in workflow["preparation"]:
            st.write(f"- {item}")
    with columns[1]:
        st.markdown("#### Synthetic input")
        st.code(workflow["synthetic_input"], language=None)
        st.markdown("#### Expected output")
        st.write(workflow["expected_output"])
    st.markdown("### Demonstration steps")
    for number, step in enumerate(workflow["steps"], start=1):
        st.markdown(f"<div class='step-card'><span>{number}</span><p>{step}</p></div>", unsafe_allow_html=True)
    st.markdown("### Example prompt")
    render_prompt_sheet(
        attachment_prompt,
        label=f"Example prompt for {workflow['title']}",
        key_prefix=f"{key_prefix}_{workflow['id']}",
    )
    st.download_button(
        "Download example prompt",
        attachment_prompt,
        file_name=f"{workflow['id']}_prompt.txt",
        mime="text/plain",
        key=f"{key_prefix}_download_{workflow['id']}",
    )
    tabs = st.tabs(["Verification points", "Common failure modes", "Debrief questions"])
    for tab, key in zip(tabs, ["verification_points", "failure_modes", "debrief_questions"]):
        with tab:
            for item in workflow[key]:
                st.write(f"- {item}")
    clinician_verification_checklist(f"{key_prefix}_{workflow['id']}")
