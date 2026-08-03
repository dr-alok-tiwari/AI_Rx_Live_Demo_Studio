"""Readable, full-prompt presentation without nested scrolling."""

from __future__ import annotations

from html import escape
import json
import re

import streamlit as st


def _prompt_chunks(prompt: str) -> list[str]:
    return [chunk.strip() for chunk in re.split(r"\n\s*\n", prompt.strip()) if chunk.strip()]


def _render_chunk(chunk: str) -> str:
    lines = chunk.splitlines()
    first = lines[0].strip()
    is_heading = first.isupper() and len(first) <= 90
    if is_heading:
        body = "<br>".join(escape(line) for line in lines[1:])
        return (
            "<section class='prompt-sheet-section'>"
            f"<div class='prompt-sheet-heading'>{escape(first)}</div>"
            f"<div>{body}</div></section>"
        )
    return (
        "<section class='prompt-sheet-section'>"
        f"<div>{'<br>'.join(escape(line) for line in lines)}</div></section>"
    )


def render_prompt_sheet(prompt: str, *, label: str, key_prefix: str) -> None:
    """Show the exact prompt as a balanced desktop sheet plus a copy source."""
    words = len(prompt.split())
    density = "dense" if len(prompt) > 3_500 else "standard" if len(prompt) > 1_200 else "short"
    sections = "".join(_render_chunk(chunk) for chunk in _prompt_chunks(prompt))
    st.markdown(
        f"""
        <article class='prompt-sheet prompt-sheet-{density}' aria-label='{escape(label)}'>
          <div class='prompt-sheet-toolbar'>
            <span>FULL PROMPT · ONE-VIEW SHEET</span>
            <span>{words:,} words · {len(prompt):,} characters</span>
          </div>
          <div class='prompt-sheet-body'>{sections}</div>
        </article>
        """,
        unsafe_allow_html=True,
    )
    payload = json.dumps(prompt, ensure_ascii=False).replace("</", "<\\/")
    st.iframe(
        f"""
        <!doctype html><html><head><meta charset='utf-8'><style>
          body {{ margin: 0; font-family: Aptos, 'Segoe UI', sans-serif; background: transparent; }}
          button {{ width: 100%; min-height: 42px; color: #07151c; font-weight: 800;
            background: linear-gradient(120deg, #fbbf24, #f59e0b); border: 0; border-radius: 11px;
            cursor: pointer; box-shadow: 0 8px 22px rgba(245,158,11,.18); }}
          button:focus {{ outline: 3px solid #2dd4bf; outline-offset: 2px; }}
          button.done {{ color: #05251f; background: linear-gradient(120deg, #6ee7b7, #2dd4bf); }}
          textarea {{ position: fixed; left: -9999px; top: -9999px; }}
        </style></head><body>
          <button id='copy' type='button' data-prompt-key='{escape(key_prefix)}'>Copy entire prompt · {len(prompt):,} characters</button>
          <textarea id='source' aria-hidden='true'></textarea>
          <script>
            const exactPrompt = {payload};
            const button = document.getElementById('copy');
            async function copyPrompt() {{
              try {{ await navigator.clipboard.writeText(exactPrompt); }}
              catch (error) {{
                const source = document.getElementById('source');
                source.value = exactPrompt; source.focus(); source.select();
                document.execCommand('copy');
              }}
              button.textContent = 'Entire prompt copied'; button.classList.add('done');
              setTimeout(() => {{ button.textContent = 'Copy entire prompt · {len(prompt):,} characters'; button.classList.remove('done'); }}, 1800);
            }}
            button.addEventListener('click', copyPrompt);
          </script>
        </body></html>
        """,
        width="stretch",
        height=48,
    )
