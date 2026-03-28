from html import escape

import streamlit as st


STATE_CLASS = {
    "idle": "idle",
    "info": "info",
    "warning": "warning",
    "error": "error",
    "success": "success",
    "collecting": "warning",
    "captured": "info",
    "complete": "success",
    "scanning": "warning",
}


def render_status_card(
    title: str,
    value: str,
    state: str = "info",
    caption: str = "",
    icon: str = "",
) -> None:
    css_state = STATE_CLASS.get(state, "info")
    safe_title = escape(title)
    safe_value = escape(value)
    safe_caption = escape(caption)
    safe_icon = escape(icon)
    icon_markup = f'<span class="status-icon">{safe_icon}</span>' if icon else ""

    st.markdown(
        f"""
        <div class="status-card status-{css_state}">
            <p class="status-title">{safe_title}</p>
            <h3>{icon_markup}{safe_value}</h3>
            <p class="status-caption">{safe_caption}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )