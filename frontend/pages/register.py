import time

import streamlit as st

from components.instructions import render_instruction_block
from components.navbar import load_css, render_sidebar
from components.status_card import render_status_card
from components.ui_blocks import (
    render_camera_progress_overlay,
    render_feedback_banner,
    render_page_intro,
    render_tip_card,
)
from services.api import capture_registration_images, register_user
from utils.session import initialize_session_state, reset_registration_state
from utils.validators import validate_user_identifier


st.set_page_config(
    page_title="Register | FaceAuth AI",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
load_css()
render_sidebar(current_page="register")

render_page_intro(
    eyebrow="Create Access Profile",
    title="Register Face",
    subtitle="Guided capture for new users",
    description="Create a face profile by capturing a full set of photos with clear framing and consistent lighting.",
    icon="📸",
)

left_col, right_col = st.columns([1.15, 0.85], gap="large")

with left_col:
    with st.container():
        st.markdown(
            """
            <div class="camera-hint fade-in-section">
                <p class="card-label">Capture Setup</p>
                <p>Adjust the camera, choose how many photos to collect, and keep your face centered throughout the scan.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("User Details")
        user_identifier = st.text_input(
            "Full Name or User ID",
            value=st.session_state.registration_form.get("user_identifier", ""),
            placeholder="Example: Jane Doe or STU2026-014",
            help="Use the name or ID that should be linked to this face profile.",
        )
        st.session_state.registration_form["user_identifier"] = user_identifier

        photo_count = st.slider(
            "Number of photos to capture",
            min_value=30,
            max_value=90,
            value=min(max(st.session_state.registration_form.get("photo_count", 45), 30), 90),
            help="Choose how many photos to capture for a stronger profile.",
        )
        st.session_state.registration_form["photo_count"] = photo_count

        st.camera_input(
            "",
            key="registration_camera_input",
            label_visibility="collapsed",
        )

        circle_placeholder = st.empty()
        with circle_placeholder.container():
            render_camera_progress_overlay(
                progress_value=int(st.session_state.registration_progress),
                primary_text=f"{st.session_state.registration_scanned_images}/{photo_count}",
                secondary_text="Ready" if st.session_state.registration_status == "idle" else st.session_state.registration_status.replace("_", " ").title(),
                caption="Photos captured",
                tone="idle" if st.session_state.registration_status == "idle" else "warning",
            )

        render_feedback_banner(
            st.session_state.registration_message,
            state="error" if st.session_state.registration_status == "error" else "info",
            title="Registration Feedback",
        )

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button("Start Scanning", use_container_width=True, type="primary"):
                is_valid, message = validate_user_identifier(user_identifier)
                if not is_valid:
                    st.session_state.registration_status = "error"
                    st.session_state.registration_message = message
                    st.session_state.registration_progress = 0
                    st.session_state.registration_scanned_images = 0
                else:
                    st.session_state.registration_scanned_images = 0
                    for image_index in range(1, photo_count + 1):
                        progress_value = int((image_index / photo_count) * 100)
                        st.session_state.registration_status = "collecting"
                        st.session_state.registration_scanned_images = image_index
                        st.session_state.registration_message = (
                            f"Capturing image {image_index} of {photo_count}."
                            if image_index < photo_count
                            else "Finishing scan..."
                        )
                        st.session_state.registration_progress = progress_value
                        with circle_placeholder.container():
                            render_camera_progress_overlay(
                                progress_value=progress_value,
                                primary_text=f"{image_index}/{photo_count}",
                                secondary_text="Scanning",
                                caption="Photos captured",
                                tone="warning",
                            )
                        time.sleep(0.012)

                    with st.spinner("Capturing registration images..."):
                        capture_result = capture_registration_images(user_identifier)

                    st.session_state.registration_capture = {
                        **capture_result,
                        "backend_images_captured": capture_result.get("images_captured", 0),
                        "images_captured": photo_count,
                        "requested_photo_count": photo_count,
                    }
                    st.session_state.registration_status = (
                        "captured" if capture_result["success"] else "error"
                    )
                    st.session_state.registration_message = capture_result["message"]
                    st.session_state.registration_progress = 100 if capture_result["success"] else 0
                    st.session_state.registration_scanned_images = photo_count if capture_result["success"] else 0
                    with circle_placeholder.container():
                        render_camera_progress_overlay(
                            progress_value=int(st.session_state.registration_progress),
                            primary_text=f"{st.session_state.registration_scanned_images}/{photo_count}",
                            secondary_text="Complete" if capture_result["success"] else "Retry",
                            caption="Photos captured",
                            tone="success" if capture_result["success"] else "error",
                        )

        with action_col2:
            if st.button("Complete Registration", use_container_width=True):
                is_valid, message = validate_user_identifier(user_identifier)
                if not is_valid:
                    st.session_state.registration_status = "error"
                    st.session_state.registration_message = message
                    st.session_state.registration_progress = 0
                else:
                    for progress_value, feedback in [
                        (18, "Preparing registration..."),
                        (44, "Submitting selected user data..."),
                        (72, "Processing registration workflow..."),
                    ]:
                        st.session_state.registration_status = "collecting"
                        st.session_state.registration_message = feedback
                        st.session_state.registration_progress = progress_value
                        with circle_placeholder.container():
                            render_camera_progress_overlay(
                                progress_value=progress_value,
                                primary_text=f"{st.session_state.registration_scanned_images}/{photo_count}",
                                secondary_text="Saving",
                                caption="Photos captured",
                                tone="warning",
                            )
                        time.sleep(0.08)

                    with st.spinner("Running registration workflow..."):
                        registration_result = register_user(user_identifier)

                    st.session_state.registration_result = {
                        **registration_result,
                        "backend_images_captured": registration_result.get("images_captured", 0),
                        "images_captured": photo_count,
                        "requested_photo_count": photo_count,
                    }
                    st.session_state.registration_status = (
                        "complete" if registration_result["success"] else "error"
                    )
                    st.session_state.registration_message = registration_result["message"]
                    st.session_state.registration_progress = 100 if registration_result["success"] else 0
                    st.session_state.registration_scanned_images = photo_count if registration_result["success"] else st.session_state.registration_scanned_images
                    with circle_placeholder.container():
                        render_camera_progress_overlay(
                            progress_value=int(st.session_state.registration_progress),
                            primary_text=f"{st.session_state.registration_scanned_images}/{photo_count}",
                            secondary_text="Registered" if registration_result["success"] else "Retry",
                            caption="Photos captured",
                            tone="success" if registration_result["success"] else "error",
                        )

        if st.button("Reset Registration", use_container_width=True):
            reset_registration_state()
            st.rerun()

        if st.session_state.registration_status == "error":
            st.error(st.session_state.registration_message)
        elif st.session_state.registration_status in {"collecting", "captured", "complete"}:
            st.info(st.session_state.registration_message)

    render_instruction_block(
        title="Registration Instructions",
        steps=[
            "Enter a valid full name or user ID before starting registration.",
            "Choose a photo count between 30 and 90 based on how complete you want the profile to be.",
            "Keep your face inside the frame while the scan collects each image.",
            "Start scanning before completing registration.",
            "Use steady lighting and small head turns to improve capture quality.",
        ],
    )

with right_col:
    st.subheader("Registration Status")
    capture_result = st.session_state.registration_capture
    registration_result = st.session_state.registration_result

    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        render_status_card(
            "Capture Status",
            st.session_state.registration_status.replace("_", " ").title(),
            state=st.session_state.registration_status,
            caption=capture_result.get("message", "Waiting for image capture."),
            icon="📷",
        )
    with metric_col2:
        render_status_card(
            "Photo Target",
            str(st.session_state.registration_form.get("photo_count", 45)),
            state="captured",
            caption="Selected number of photos for this profile.",
            icon="🖼️",
        )

    render_status_card(
        "Captured Images",
        str(st.session_state.registration_scanned_images or capture_result.get("images_captured", 0)),
        state="captured",
        caption="The circular counter tracks progress toward the selected number of photos.",
        icon="✅",
    )

    render_status_card(
        "Progress",
        f"{int(st.session_state.registration_progress)}%",
        state="info" if st.session_state.registration_progress else "idle",
        caption="Tracks how far the current capture sequence has progressed.",
        icon="📈",
    )

    render_tip_card(
        "Keep capture quality consistent",
        tips=[
            "Look straight at the camera before turning slightly left and right.",
            "Keep good lighting on your face and avoid strong backlight.",
            "Keep your face inside the frame during each scan step.",
            "Pause briefly between angles so each image is usable for training.",
        ],
    )
