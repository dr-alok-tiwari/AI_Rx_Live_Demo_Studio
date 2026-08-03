"""Side-by-side comparison table for up to four selected tools."""

from __future__ import annotations

import pandas as pd
import streamlit as st


COMPARISON_ROWS = [
    ("Primary use", "purpose"),
    ("Intended user", "intended_users"),
    ("Free tier", "free_tier"),
    ("Pricing", "pricing_detail"),
    ("Approximate INR", "approximate_inr"),
    ("India availability", "india_availability"),
    ("Public demo", "public_demo"),
    ("Input", "inputs"),
    ("Output", "outputs"),
    ("Learning curve", "no_code"),
    ("Mobile support", "mobile_support"),
    ("Collaboration", "collaboration"),
    ("PHI suitability", "phi_suitability"),
    ("Clinical evidence", "evidence_status"),
    ("Regulatory information", "regulatory_status"),
    ("Exports", "exports"),
    ("Integrations", "integrations"),
    ("Limitations", "limitations"),
    ("Best workshop use", "live_demo_suitability"),
]


def _format(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def render_comparison(tools: list[dict]) -> None:
    selected_ids = st.session_state.get("compare_tools", [])[:4]
    selected = [tool for tool in tools if tool["id"] in selected_ids]
    if not selected:
        st.info("Select up to four tools using the Compare button in the directory.")
        return
    table = {tool["name"]: [_format(tool.get(key, "Not independently verified")) for _, key in COMPARISON_ROWS] for tool in selected}
    frame = pd.DataFrame(table, index=[label for label, _ in COMPARISON_ROWS])
    st.dataframe(frame, width="stretch", height=680)
    st.caption("Pricing was checked on the date shown in each tool record. Prices and availability may change.")
