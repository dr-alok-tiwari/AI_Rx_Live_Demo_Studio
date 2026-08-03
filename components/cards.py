"""Tool-card rendering and workshop-selection actions."""

from __future__ import annotations

import streamlit as st


def _ensure_selection_state() -> None:
    st.session_state.setdefault("compare_tools", [])
    st.session_state.setdefault("workshop_tools", [])


def _toggle(collection: str, tool_id: str, maximum: int | None = None) -> None:
    items = list(st.session_state.get(collection, []))
    if tool_id in items:
        items.remove(tool_id)
    elif maximum is None or len(items) < maximum:
        items.append(tool_id)
    st.session_state[collection] = items


def tool_card(tool: dict, key_prefix: str = "tool") -> None:
    _ensure_selection_state()
    access_badge = "Public demo" if tool["public_demo"] else "Institutional access"
    regulatory = tool["regulatory_status"] or "Not independently verified"
    st.markdown(
        f"""
        <article class="tool-card">
          <div class="tool-card-top"><div class="tool-icon">{tool.get('safe_icon', 'AI')}</div>
          <div><div class="tool-category">{tool['category']}</div><h3>{tool['name']}</h3></div></div>
          <p class="tool-purpose">{tool['purpose']}</p>
          <div class="badge-row"><span>{tool['pricing_type']}</span><span>{access_badge}</span>
          <span>{tool['demo_duration_minutes']} min</span></div>
          <p><strong>Problem:</strong> {tool['problem']}</p>
          <p><strong>How it helps:</strong> {tool['solution']}</p>
          <p class="muted"><strong>PHI:</strong> {tool['phi_warning']}</p>
          <p class="muted"><strong>Evidence/regulatory:</strong> {regulatory}</p>
          <p class="verified">URL checked {tool['last_verified']} · {tool['verification_status']}</p>
        </article>
        """,
        unsafe_allow_html=True,
    )
    controls = st.columns([1.25, 1.25, 1.25, 1.6])
    with controls[0]:
        st.link_button("Visit official tool", tool["official_url"], width="stretch")
    with controls[1]:
        if st.button("View demo", key=f"{key_prefix}_demo_{tool['id']}", width="stretch"):
            st.session_state["selected_demo_tool"] = tool["id"]
            st.switch_page("pages/04_Live_Demos.py")
    with controls[2]:
        selected = tool["id"] in st.session_state["compare_tools"]
        if st.button("Remove compare" if selected else "Compare", key=f"{key_prefix}_compare_{tool['id']}", width="stretch"):
            _toggle("compare_tools", tool["id"], maximum=4)
            st.rerun()
    with controls[3]:
        planned = tool["id"] in st.session_state["workshop_tools"]
        if st.button("Remove from plan" if planned else "Add to workshop plan", key=f"{key_prefix}_plan_{tool['id']}", width="stretch"):
            _toggle("workshop_tools", tool["id"])
            st.rerun()
    with st.expander("Clinical detail, limitations, and alternatives"):
        left, right = st.columns(2)
        with left:
            st.markdown("#### Use profile")
            st.write(f"**Intended users:** {', '.join(tool['intended_users'])}")
            st.write(f"**Specialties:** {', '.join(tool['specialties'])}")
            st.write(f"**Inputs:** {', '.join(tool['inputs'])}")
            st.write(f"**Outputs:** {', '.join(tool['outputs'])}")
            st.write(f"**Access:** {tool['access_type']} · {tool['india_availability']}")
            st.write(f"**Pricing:** {tool['pricing_detail']} ({tool['pricing_checked']}; prices may change)")
        with right:
            st.markdown("#### Safety and fit")
            st.write(f"**Evidence:** {tool['evidence_status']}")
            st.write(f"**Regulatory:** {tool['regulatory_status']}")
            st.write(f"**Not recommended for:** {tool['limitations'][0]}")
            st.write(f"**Known limitations:** {'; '.join(tool['limitations'])}")
            st.write(f"**Alternatives:** {', '.join(tool['alternatives'])}")
