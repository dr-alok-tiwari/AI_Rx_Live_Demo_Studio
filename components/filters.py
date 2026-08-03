"""Directory filter controls."""

from __future__ import annotations

import streamlit as st
from components.data import unique_values
from components.nudges import text_nudge


def directory_filters(tools: list[dict], key_prefix: str = "directory") -> dict:
    st.markdown("### Refine the directory")
    text_nudge(
        title="Prefer a starting point?",
        description="Choose a common task, or type your own search below.",
        choices={
            "Draft a clinical note": "clinical documentation note",
            "Prepare a patient handout": "patient education handout",
            "Run a journal club": "journal club evidence",
            "Explore image-analysis tools": "medical image analysis",
            "Build a teaching presentation": "medical teaching presentation",
        },
        target_key=f"{key_prefix}_query",
        key_prefix=f"{key_prefix}_nudge",
    )
    query = st.text_input(
        "Search by tool, problem, category, or specialty",
        placeholder="Example: journal club, cardiology, patient handout",
        key=f"{key_prefix}_query",
    )
    row1 = st.columns(4)
    any_label = lambda value: value or "Any"
    category = row1[0].selectbox("Category", [""] + unique_values(tools, "category"), key=f"{key_prefix}_category", format_func=any_label)
    specialty = row1[1].selectbox("Specialty", [""] + unique_values(tools, "specialties"), key=f"{key_prefix}_specialty", format_func=any_label)
    use_type = row1[2].selectbox("Use", [""] + unique_values(tools, "use_type"), key=f"{key_prefix}_use", format_func=any_label)
    pricing = row1[3].selectbox("Pricing", [""] + unique_values(tools, "pricing_type"), key=f"{key_prefix}_pricing", format_func=any_label)
    row2 = st.columns(4)
    access = row2[0].selectbox("Access", [""] + unique_values(tools, "access_type"), key=f"{key_prefix}_access", format_func=any_label)
    india = row2[1].selectbox("India availability", [""] + unique_values(tools, "india_availability"), key=f"{key_prefix}_india", format_func=any_label)
    no_code = row2[2].selectbox("Technical level", ["", "No-code", "Technical"], key=f"{key_prefix}_technical", format_func=any_label)
    public_demo = row2[3].selectbox("Demo access", ["", "Public demo", "Institutional"], key=f"{key_prefix}_demo", format_func=any_label)
    max_time = st.select_slider("Maximum demonstration time", options=[3, 5, 10, 15], value=15, key=f"{key_prefix}_time")
    return {
        "query": query,
        "category": category,
        "specialty": specialty,
        "use_type": use_type,
        "pricing": pricing,
        "access": access,
        "india": india,
        "no_code": no_code,
        "public_demo": public_demo,
        "max_time": max_time,
    }
