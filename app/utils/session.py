import streamlit as st


def initialize_session_state() -> None:
    defaults = {
        "registration_form": {"user_identifier": "", "photo_count": 45},
        "registration_status": "idle",
        "registration_message": "Waiting for user input.",
        "registration_progress": 0,
        "registration_scanned_images": 0,
        "registration_capture": {},
        "registration_result": {},
        "login_scan": {},
        "login_result": {},
        "login_status": "idle",
        "login_message": "Waiting for a face scan.",
        "login_progress": 0,
        "authenticated_user": "",
        "login_timestamp": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_registration_state() -> None:
    st.session_state.registration_status = "idle"
    st.session_state.registration_message = "Waiting for user input."
    st.session_state.registration_progress = 0
    st.session_state.registration_scanned_images = 0
    st.session_state.registration_capture = {}
    st.session_state.registration_result = {}


def reset_login_state() -> None:
    st.session_state.login_scan = {}
    st.session_state.login_result = {}
    st.session_state.login_status = "idle"
    st.session_state.login_message = "Waiting for a face scan."
    st.session_state.login_progress = 0


def logout_user() -> None:
    reset_login_state()
    st.session_state.authenticated_user = ""
    st.session_state.login_timestamp = ""