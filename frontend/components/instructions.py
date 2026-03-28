from html import escape

import streamlit as st


def render_instruction_block(title: str, steps: list[str]) -> None:
    items = "".join(f"<li>{escape(step)}</li>" for step in steps)
    st.markdown(
        f"""
        <div class="panel-card instruction-card">
            <h3>{escape(title)}</h3>
            <ol>{items}</ol>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_project_flow(steps: list[str]) -> None:
    columns = st.columns(len(steps))
    for index, step in enumerate(steps):
        with columns[index]:
            st.markdown(
                f"""
                <div class="flow-card fade-in-section">
                    <p class="flow-index">Step {index + 1}</p>
                    <h4>{escape(step)}</h4>
                    <p>Key step in the access process.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )