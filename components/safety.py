"""Safety gates and reusable clinician review controls."""

from __future__ import annotations

import streamlit as st


SAFETY_GATE = [
    "The input is synthetic, anonymised, or approved for upload.",
    "The selected tool is approved for the intended purpose.",
    "The output will be checked against source evidence.",
    "A qualified professional will review the output.",
    "The final use and material decisions will be documented.",
]


def render_safety_gate(key_prefix: str = "safety") -> bool:
    st.markdown("### Five-step safety gate")
    checks = [
        st.checkbox(item, key=f"{key_prefix}_{index}")
        for index, item in enumerate(SAFETY_GATE, start=1)
    ]
    complete = all(checks)
    if not complete:
        st.info("Acknowledge every safety step to enter the diagnostic simulation area.")
    return complete


def clinician_verification_checklist(key_prefix: str) -> None:
    st.markdown("#### Clinician verification checklist")
    for index, item in enumerate(
        [
            "Names, dates, measurements, medicines, doses, and units match the source.",
            "No unsupported finding, diagnosis, examination, or plan was added.",
            "Missing, ambiguous, and contradictory information is visible.",
            "Urgent warning signs and escalation instructions are clinically appropriate.",
            "The final wording suits the patient, colleague, or institutional record.",
        ],
        start=1,
    ):
        st.checkbox(item, key=f"{key_prefix}_verify_{index}")


def social_media_flags(text: str) -> list[str]:
    lowered = text.casefold()
    rules = {
        "Possible patient identifier": ["patient name", "mrn", "mobile number", "address"],
        "Patient image or report reference": ["patient photo", "scan attached", "report attached"],
        "Guaranteed outcome": ["guaranteed", "100% cure", "always works"],
        "Fear-based language": ["terrifying", "you will die", "silent killer"],
        "Promotional exaggeration": ["miracle", "revolutionary cure", "best doctor"],
        "Before-and-after claim": ["before and after", "transformation photo"],
        "Unclear evidence": ["research proves", "studies show", "experts say"],
    }
    return [label for label, phrases in rules.items() if any(phrase in lowered for phrase in phrases)]

