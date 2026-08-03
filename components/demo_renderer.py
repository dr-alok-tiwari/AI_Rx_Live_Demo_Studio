"""Render complete demonstration workflows from local JSON."""

from __future__ import annotations

import streamlit as st
from components.prompt_sheet import render_prompt_sheet
from components.safety import clinician_verification_checklist


def render_workflow(workflow: dict, key_prefix: str = "workflow") -> None:
    st.markdown(f"## {workflow['title']}")
    st.caption(f"{workflow['duration_minutes']} minutes · {workflow['level']} · {workflow['category']}")
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
        workflow["sample_prompt"],
        label=f"Example prompt for {workflow['title']}",
        key_prefix=f"{key_prefix}_{workflow['id']}",
    )
    st.download_button(
        "Download example prompt",
        workflow["sample_prompt"],
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
