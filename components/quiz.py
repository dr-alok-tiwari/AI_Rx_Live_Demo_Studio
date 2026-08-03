"""Assessment widgets with explanations and lightweight badge tracking."""

from __future__ import annotations

import streamlit as st


def render_questions(questions: list[dict], key_prefix: str, limit: int = 10) -> tuple[int, int]:
    score = 0
    shown = questions[:limit]
    for index, item in enumerate(shown, start=1):
        st.markdown(f"#### {index}. {item['question']}")
        choice = st.radio(
            "Select one answer",
            item["options"],
            index=None,
            key=f"{key_prefix}_{item['id']}",
            label_visibility="collapsed",
        )
        if choice is not None:
            if choice == item["answer"]:
                st.success(f"Correct. {item['explanation']}")
                score += 1
            else:
                st.error(f"Review this one. {item['explanation']}")
        st.divider()
    return score, len(shown)


def badge_for_score(score: int, total: int) -> str:
    if total == 0:
        return "Safe AI Starter"
    ratio = score / total
    if ratio >= 0.9:
        return "Responsible AI Champion"
    if ratio >= 0.75:
        return "Clinical Workflow Designer"
    if ratio >= 0.6:
        return "Evidence Explorer"
    return "Safe AI Starter"

