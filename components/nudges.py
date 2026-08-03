"""Predefined starters for free-text inputs."""

from __future__ import annotations

import streamlit as st


def text_nudge(
    *,
    title: str,
    description: str,
    choices: dict[str, str],
    target_key: str,
    key_prefix: str,
) -> None:
    """Offer a safe predefined input without replacing free-text entry."""
    st.markdown(
        f"<div class='nudge-card'><strong>{title}</strong><br><span>{description}</span></div>",
        unsafe_allow_html=True,
    )
    columns = st.columns([3, 1])
    labels = ["Choose a predefined nudge"] + list(choices)
    selected = columns[0].selectbox(
        "Predefined nudge",
        labels,
        key=f"{key_prefix}_choice",
        label_visibility="collapsed",
    )
    if columns[1].button(
        "Use nudge",
        key=f"{key_prefix}_apply",
        disabled=selected == labels[0],
        width="stretch",
    ):
        st.session_state[target_key] = choices[selected]
        st.rerun()

