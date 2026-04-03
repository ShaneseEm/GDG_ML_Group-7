import streamlit as st

from components.navbar import load_css, render_sidebar
from components.status_card import render_status_card
from components.ui_blocks import render_feedback_banner, render_page_intro
from utils.session import initialize_session_state, logout_user


st.set_page_config(
    page_title="Welcome | FaceAuth AI",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
load_css()
render_sidebar(current_page="welcome")

authenticated_user = st.session_state.get("authenticated_user")
login_timestamp = st.session_state.get("login_timestamp", "")

if not authenticated_user:
    render_page_intro(
        eyebrow="Approved Access",
        title="Welcome Page",
        subtitle="No active session found",
        description="Sign in from the login page to access your welcome screen.",
        icon="🔒",
    )
    render_feedback_banner(
        "No authenticated user is stored in the current session.",
        state="warning",
        title="Session Required",
    )

    action_col1, action_col2 = st.columns(2)
    action_col1.page_link(
        "main.py",
        label="Back to Home",
        icon=":material/home:",
        use_container_width=True,
    )
    action_col2.page_link(
        "pages/login.py",
        label="Go to Login",
        icon=":material/verified_user:",
        use_container_width=True,
    )
else:
    render_page_intro(
        eyebrow="Approved Access",
        title=f"Welcome, {authenticated_user}",
        subtitle="Authentication completed successfully",
        description="Your session is active and you can continue securely.",
        icon="✅",
    )

    st.markdown(
        """
        <div class="welcome-card fade-in-section">
            <div class="welcome-emoji">🎉</div>
            <div class="approved-badge">Authenticated Session</div>
            <h3>Face recognition approved</h3>
            <p>Access has been granted and your session is ready.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status_col1, status_col2, status_col3 = st.columns(3)
    with status_col1:
        render_status_card(
            "User",
            authenticated_user,
            state="success",
            caption="Signed in account.",
            icon="🧑",
        )
    with status_col2:
        render_status_card(
            "Approval",
            "Approved",
            state="success",
            caption="Identity confirmed successfully.",
            icon="✅",
        )
    with status_col3:
        render_status_card(
            "Timestamp",
            login_timestamp or "Not available",
            state="info",
            caption="Time of the current sign-in.",
            icon="🕒",
        )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Back to Home", use_container_width=True, type="primary"):
            st.switch_page("main.py")
    with action_col2:
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.switch_page("main.py")