import time
from datetime import datetime

import streamlit as st

from components.navbar import load_css, render_sidebar
from components.ui_blocks import (
    render_camera_progress_overlay,
    render_feedback_banner,
    render_page_intro,
    render_reaction_avatar,
)
from services.api import get_prediction_result, login_with_face
from utils.session import initialize_session_state


st.set_page_config(
    page_title="Login | FaceAuth AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
load_css()
render_sidebar(current_page="login")

render_page_intro(
    eyebrow="Secure Access",
    title="Login With Face",
    subtitle="Fast and secure identity check",
    description="Use the camera to verify your identity and continue directly to your account once access is approved.",
    icon="🛰️",
)

left_col, right_col = st.columns([1.12, 0.88], gap="small")

with left_col:
    with st.container():
        st.markdown(
            """
            <div class="login-section-header fade-in-section">
                <p class="card-label">Verification</p>
                <h3>Scan your face</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.camera_input(
            "",
            key="login_camera_input",
            label_visibility="collapsed",
        )

        circle_placeholder = st.empty()
        with circle_placeholder.container():
            render_camera_progress_overlay(
                progress_value=int(st.session_state.login_progress),
                primary_text=f"{int(st.session_state.login_progress)}%",
                secondary_text="Ready" if st.session_state.login_status == "idle" else st.session_state.login_status.replace("_", " ").title(),
                caption="Scan status",
                tone="idle" if st.session_state.login_status == "idle" else "warning",
            )

        banner_state = "info"
        if st.session_state.login_status == "success":
            banner_state = "success"
        elif st.session_state.login_status == "error":
            banner_state = "error"
        elif st.session_state.login_status == "scanning":
            banner_state = "warning"

        render_feedback_banner(
            st.session_state.login_message,
            state=banner_state,
            title="Status",
        )

        action_col1, action_col2 = st.columns([1.3, 0.7], gap="small")

        if action_col1.button("Scan Face", use_container_width=True, type="primary"):
            for progress_value, feedback in [
                (12, "Camera ready."),
                (34, "Checking your position..."),
                (58, "Verifying your face..."),
            ]:
                st.session_state.login_status = "scanning"
                st.session_state.login_message = feedback
                st.session_state.login_progress = progress_value
                with circle_placeholder.container():
                    render_camera_progress_overlay(
                        progress_value=progress_value,
                        primary_text=f"{progress_value}%",
                        secondary_text="Scanning",
                        caption="Scan status",
                        tone="warning",
                    )
                time.sleep(0.08)

            with st.spinner("Scanning your face..."):
                scan_result = login_with_face()

            st.session_state.login_status = "scanning"
            st.session_state.login_scan = scan_result
            st.session_state.login_message = scan_result.get("message", "Face scan completed.")
            st.session_state.login_progress = 74
            with circle_placeholder.container():
                render_camera_progress_overlay(
                    progress_value=74,
                    primary_text="74%",
                    secondary_text="Matching",
                    caption="Scan status",
                    tone="warning",
                )

            with st.spinner("Verifying your identity..."):
                prediction_result = get_prediction_result()

            st.session_state.login_result = prediction_result
            st.session_state.login_progress = 100
            st.session_state.login_message = prediction_result.get(
                "message",
                "Verification finished.",
            )

            if prediction_result.get("access_granted"):
                st.session_state.login_status = "success"
                st.session_state.authenticated_user = prediction_result.get(
                    "recognized_user",
                    "Authorized User",
                )
                st.session_state.login_timestamp = datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
            else:
                st.session_state.login_status = "error"
                st.session_state.authenticated_user = ""
                st.session_state.login_timestamp = ""

            with circle_placeholder.container():
                render_camera_progress_overlay(
                    progress_value=int(st.session_state.login_progress),
                    primary_text="100%" if prediction_result.get("access_granted") else f"{int(st.session_state.login_progress)}%",
                    secondary_text="Approved" if prediction_result.get("access_granted") else "Denied",
                    caption="Scan status",
                    tone="success" if prediction_result.get("access_granted") else "error",
                )

            if prediction_result.get("access_granted"):
                st.switch_page("pages/welcome.py")

        st.markdown(
            """
            <div class="login-subsection-header fade-in-section">
                <p class="card-label">Navigation</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_col1, nav_col2 = st.columns(2, gap="small")
        nav_col1.page_link(
            "main.py",
            label="Back to Home",
            icon=":material/home:",
            use_container_width=True,
        )
        nav_col2.page_link(
            "pages/register.py",
            label="Register",
            icon=":material/person_add:",
            use_container_width=True,
        )

with right_col:
    result = st.session_state.login_result or {}
    live_state = st.session_state.login_status

    st.markdown(
        """
        <div class="login-section-header login-side-header fade-in-section">
            <p class="card-label">Recognition Status</p>
            <h3>Current response</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_reaction_avatar(
        "success"
        if live_state == "success"
        else "error"
        if live_state == "error"
        else "scanning"
        if live_state == "scanning"
        else "idle"
    )

    if live_state == "success":
        render_feedback_banner(
            f"Welcome back, {result.get('recognized_user', st.session_state.get('authenticated_user', 'user'))}.",
            state="success",
            title="Verified",
        )
    elif live_state == "error":
        render_feedback_banner(
            "We could not verify your identity. Try again with better lighting and a centered position.",
            state="error",
            title="Try Again",
        )
