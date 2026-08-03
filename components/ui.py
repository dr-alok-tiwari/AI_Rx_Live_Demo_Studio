"""Shared visual system for all Streamlit pages."""

from __future__ import annotations

from pathlib import Path
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]


def configure_page(title: str, icon: str = "🩺") -> None:
    st.set_page_config(
        page_title=f"{title} | AI Rx Live Demo Studio",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    sidebar_brand()


def inject_css() -> None:
    css = (ROOT / "styles" / "custom.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def sidebar_brand() -> None:
    with st.sidebar:
        planned = len(st.session_state.get("workshop_tools", []))
        packed = len(st.session_state.get("prompt_pack", []))
        st.markdown(
            """
            <div class="sidebar-brand">
              <div class="brand-mark">AI<span>Rx</span></div>
              <div><strong>Live Demo Studio</strong><br><small>Patient first · Doctor led · AI assisted</small></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """<div class="sidebar-path"><span>1</span> Define the decision<br>
            <span>2</span> Use safe input<br><span>3</span> Compare reasoning<br>
            <span>4</span> Verify and act</div>""",
            unsafe_allow_html=True,
        )
        st.caption(f"Session tray · {packed} prompts · {planned} tools")


def safety_notice() -> None:
    st.markdown(
        """
        <div class="safety-strip" role="note">
          <strong>Workshop safety:</strong> Educational platform. Do not upload identifiable patient information.
          AI-generated outputs must be independently verified by a qualified healthcare professional.
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(kicker: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <section class="page-header">
          <div class="kicker">{kicker}</div>
          <h1>{title}</h1>
          <p>{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def metric_cards(items: list[tuple[str, str, str]]) -> None:
    columns = st.columns(len(items))
    for column, (value, label, note) in zip(columns, items):
        with column:
            st.markdown(
                f"<div class='metric-card'><div class='metric-value'>{value}</div>"
                f"<div class='metric-label'>{label}</div><div class='metric-note'>{note}</div></div>",
                unsafe_allow_html=True,
            )


def section_intro(title: str, text: str) -> None:
    st.markdown(f"## {title}")
    st.write(text)


def footer() -> None:
    st.markdown(
        "<div class='footer'>AI Rx Live Demo Studio · Patient-centred decision support · Developed by Dr. Alok Tiwari</div>",
        unsafe_allow_html=True,
    )
