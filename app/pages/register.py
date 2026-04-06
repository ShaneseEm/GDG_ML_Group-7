import hashlib
import importlib
from pathlib import Path
import sys
import time

import streamlit as st
from streamlit_webrtc import webrtc_streamer

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from components.live_capture import RegistrationAutoCaptureProcessor
from components.navbar import load_css, render_sidebar
from components.status_card import render_status_card
from components.ui_blocks import (
    render_camera_progress_overlay,
    render_feedback_banner,
    render_page_intro,
)
from services.api import capture_registration_images, register_user
from utils.session import initialize_session_state, reset_registration_state
from utils.validators import validate_user_identifier


def _reset_registration_frames(user_identifier: str) -> None:
    data_collection_module = importlib.import_module("src.data_collection")
    if not hasattr(data_collection_module, "reset_registration_frames"):
        data_collection_module = importlib.reload(data_collection_module)
    data_collection_module.reset_registration_frames(user_identifier)


def _extract_capture_bytes(uploaded_file) -> bytes:
    if uploaded_file is None:
        return b""

    if isinstance(uploaded_file, (bytes, bytearray)):
        return bytes(uploaded_file)

    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.getvalue()

    if hasattr(uploaded_file, "read"):
        return uploaded_file.read()

    return b""


def resolve_registration_capture(uploaded_file=None) -> tuple[bytes, str]:
    capture_bytes = _extract_capture_bytes(uploaded_file)
    if not capture_bytes:
        return b"", ""

    capture_digest = hashlib.sha256(capture_bytes).hexdigest()
    st.session_state.registration_pending_capture_bytes = capture_bytes
    st.session_state.registration_pending_capture_digest = capture_digest
    return capture_bytes, capture_digest


def save_registration_capture_if_new(
    user_identifier: str,
    photo_count: int,
    capture_bytes: bytes,
    capture_digest: str,
) -> None:
    if not capture_bytes or not capture_digest:
        return

    if capture_digest == st.session_state.registration_last_processed_capture_digest:
        return

    capture_result = capture_registration_images(
        user_identifier,
        target_image_count=photo_count,
        uploaded_file=capture_bytes,
    )
    st.session_state.registration_capture = {
        **capture_result,
        "backend_images_captured": capture_result.get("images_captured", 0),
        "requested_photo_count": photo_count,
    }
    captured_images = capture_result.get("images_captured", 0)
    st.session_state.registration_scanned_images = captured_images
    st.session_state.registration_progress = (
        int((captured_images / photo_count) * 100) if capture_result["success"] else 0
    )

    if capture_result["success"]:
        if captured_images >= photo_count:
            st.session_state.registration_status = "collecting"
            st.session_state.registration_message = (
                f"Captured {captured_images} of {photo_count} photo(s). Training the model now..."
            )
        else:
            st.session_state.registration_status = "camera_ready"
            st.session_state.registration_message = (
                f"Captured {captured_images} of {photo_count} photo(s). Take photo {captured_images + 1}."
            )
    else:
        st.session_state.registration_status = "error"
        st.session_state.registration_message = capture_result["message"]

    st.session_state.registration_last_processed_capture_digest = capture_digest
    if capture_result["success"]:
        st.session_state.registration_last_capture_digest = capture_digest


def train_registration_if_ready(user_identifier: str, photo_count: int) -> None:
    captured_images = st.session_state.registration_scanned_images
    if captured_images < photo_count:
        return

    if st.session_state.registration_last_trained_count >= captured_images:
        return

    st.session_state.registration_status = "collecting"
    st.session_state.registration_message = (
        f"Captured {captured_images} of {photo_count} photo(s). Training the model now..."
    )
    registration_result = register_user(user_identifier, photo_count)
    st.session_state.registration_result = {
        **registration_result,
        "backend_images_captured": registration_result.get("images_captured", 0),
        "requested_photo_count": photo_count,
    }
    st.session_state.registration_status = (
        "complete" if registration_result["success"] else "error"
    )
    st.session_state.registration_message = registration_result["message"]
    st.session_state.registration_progress = 100 if registration_result["success"] else int(
        (captured_images / photo_count) * 100
    )
    st.session_state.registration_last_trained_count = captured_images


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

left_col, right_col = st.columns([1.12, 0.88], gap="small")

with left_col:
    with st.container():
        st.markdown(
            """
            <div class="register-section-header fade-in-section">
                <p class="card-label">Registration</p>
                <h3>Create your face profile</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="register-subsection-header fade-in-section">
                <p class="card-label">Profile Details</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
            help="Choose how many face captures to collect before training the model.",
        )
        st.session_state.registration_form["photo_count"] = photo_count

        st.markdown(
            """
            <div class="register-subsection-header fade-in-section compact-register-subsection">
                <p class="card-label">Capture Session</p>
            </div>
            """,
            unsafe_allow_html=True,
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
            title="Status",
        )

        st.caption("Click Start Capturing to open the live browser camera. The app will capture photos automatically until it reaches the selected target, then it will train the model.")

        action_col1, action_col2 = st.columns([1, 1], gap="small")

        with action_col1:
            if st.button("Start Capturing", use_container_width=True, type="primary"):
                is_valid, message = validate_user_identifier(user_identifier)
                if not is_valid:
                    st.session_state.registration_status = "error"
                    st.session_state.registration_message = message
                    st.session_state.registration_progress = 0
                    st.session_state.registration_scanned_images = 0
                else:
                    _reset_registration_frames(user_identifier)
                    st.session_state.registration_capture_active = True
                    st.session_state.registration_last_processed_capture_digest = ""
                    st.session_state.registration_last_capture_digest = ""
                    st.session_state.registration_pending_capture_bytes = b""
                    st.session_state.registration_pending_capture_digest = ""
                    st.session_state.registration_last_trained_count = 0
                    st.session_state.registration_scanned_images = 0
                    st.session_state.registration_progress = 0
                    st.session_state.registration_capture = {}
                    st.session_state.registration_result = {}
                    st.session_state.registration_status = "camera_ready"
                    st.session_state.registration_message = (
                        f"Camera is starting. Hold still while {photo_count} photo(s) are captured automatically."
                    )
                    st.rerun()

        if st.session_state.registration_capture_active:
            live_capture_context = webrtc_streamer(
                key="registration-live-capture",
                desired_playing_state=True,
                media_stream_constraints={"video": True, "audio": False},
                video_processor_factory=lambda: RegistrationAutoCaptureProcessor(
                    user_identifier,
                    photo_count,
                ),
                async_processing=True,
                sendback_audio=False,
                video_html_attrs={
                    "style": {"width": "100%", "borderRadius": "20px"},
                    "autoPlay": True,
                    "controls": False,
                    "muted": True,
                },
            )

            if live_capture_context and live_capture_context.video_processor:
                snapshot = live_capture_context.video_processor.get_snapshot()
                st.session_state.registration_scanned_images = snapshot.captured_images
                st.session_state.registration_progress = int(
                    (snapshot.captured_images / photo_count) * 100
                )
                st.session_state.registration_status = snapshot.status
                st.session_state.registration_message = snapshot.message

                if snapshot.completed:
                    train_registration_if_ready(user_identifier, photo_count)
                    st.session_state.registration_capture_active = False
                    st.rerun()

                if snapshot.failed:
                    st.session_state.registration_status = "error"
                    st.session_state.registration_message = snapshot.message
                    st.session_state.registration_capture_active = False
                    st.rerun()

                if not snapshot.completed and not snapshot.failed:
                    time.sleep(0.2)
                    st.rerun()

        with action_col2:
            if st.button("Reset Registration", use_container_width=True):
                reset_registration_state()
                st.rerun()

        st.markdown(
            """
            <div class="register-subsection-header fade-in-section compact-register-subsection">
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
            "pages/login.py",
            label="Go to Login",
            icon=":material/verified_user:",
            use_container_width=True,
        )

        if st.session_state.registration_status == "error":
            st.error(st.session_state.registration_message)
        elif st.session_state.registration_status in {"collecting", "captured", "complete"}:
            st.info(st.session_state.registration_message)

with right_col:
    st.markdown(
        """
        <div class="register-section-header register-side-header fade-in-section">
            <p class="card-label">Capture Overview</p>
            <h3>Progress and quality</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        state="complete" if st.session_state.registration_status == "complete" else "captured",
        caption="Tracks the number of photos collected for this profile.",
        icon="✅",
    )

    render_status_card(
        "Progress",
        f"{int(st.session_state.registration_progress)}%",
        state="info" if st.session_state.registration_progress else "idle",
        caption="Tracks how far the current capture sequence has progressed.",
        icon="📈",
    )
