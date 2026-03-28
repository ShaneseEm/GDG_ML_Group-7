from html import escape

import streamlit as st


REACTION_PRESETS = {
    "idle": ("👀", "Ready to scan", "Position your face inside the frame and begin when you are ready."),
    "scanning": ("🤖", "Checking your identity", "Hold still for a moment while your face is verified."),
    "success": ("😎", "Access granted", "You are verified and can continue."),
    "error": ("🚫", "Access denied", "We could not verify your face. Adjust your position and try again."),
}


def render_page_intro(
    eyebrow: str,
    title: str,
    subtitle: str,
    description: str,
    icon: str,
) -> None:
    st.markdown(
        f"""
        <section class="hero-card hero-layout fade-in-section">
            <div class="hero-content">
                <p class="eyebrow">{escape(eyebrow)}</p>
                <h1>{escape(title)}</h1>
                <p class="hero-subtitle">{escape(subtitle)}</p>
                <p class="hero-copy">{escape(description)}</p>
            </div>
            <div class="hero-visual">
                <div class="hero-avatar-wrap">
                    <div class="hero-orbit"></div>
                    <div class="hero-orbit-alt"></div>
                    <div class="hero-avatar">{escape(icon)}</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_feedback_banner(message: str, state: str = "info", title: str = "Status") -> None:
    safe_state = escape(state if state in {"info", "warning", "success", "error"} else "info")
    st.markdown(
        f"""
        <div class="feedback-banner feedback-{safe_state}">
            <p class="feedback-label">{escape(title)}</p>
            <p class="feedback-copy">{escape(message)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reaction_avatar(state: str) -> None:
    emoji, title, caption = REACTION_PRESETS.get(state, REACTION_PRESETS["idle"])
    safe_state = escape(state if state in REACTION_PRESETS else "idle")
    st.markdown(
        f"""
        <div class="reaction-card reaction-{safe_state}">
            <div class="reaction-avatar">{escape(emoji)}</div>
            <h3>{escape(title)}</h3>
            <p class="reaction-caption">{escape(caption)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tip_card(title: str, tips: list[str]) -> None:
    items = "".join(f"<li>{escape(tip)}</li>" for tip in tips)
    st.markdown(
        f"""
        <div class="tip-card">
            <p class="card-label">Capture Tips</p>
            <h3>{escape(title)}</h3>
            <ul>{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_camera_progress_overlay(
    progress_value: int,
    primary_text: str,
    secondary_text: str,
    caption: str,
    tone: str = "info",
) -> None:
    safe_progress = max(0, min(100, progress_value))
    safe_tone = tone if tone in {"idle", "info", "warning", "success", "error"} else "info"
    st.markdown(
        f"""
        <div class="camera-progress-overlay">
            <div class="camera-progress-panel tone-{escape(safe_tone)}">
                <div class="camera-progress-head">
                    <div class="camera-progress-copy">
                        <p class="camera-progress-primary">{escape(primary_text)}</p>
                        <p class="camera-progress-secondary">{escape(secondary_text)}</p>
                    </div>
                    <p class="camera-progress-caption">{escape(caption)}</p>
                </div>
                <div class="camera-progress-track" aria-hidden="true">
                    <div class="camera-progress-fill tone-{escape(safe_tone)}" style="width: {safe_progress}%;"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )