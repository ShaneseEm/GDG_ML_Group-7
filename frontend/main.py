import streamlit as st

from components.navbar import load_css, render_sidebar
from utils.session import initialize_session_state


st.set_page_config(
    page_title="FaceAuth AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_session_state()
load_css()
render_sidebar(current_page="home")

top_col1, top_col2, top_col3 = st.columns([6.2, 1.3, 1.3])

with top_col1:
    st.markdown(
        """
        <div class="home-topbar fade-in-section">
            <div>
                <p class="card-label">Secure Access</p>
                <h2>FaceAuth AI</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

top_col2.page_link(
    "pages/login.py",
    label="Login",
    icon=":material/login:",
    use_container_width=True,
)
top_col3.page_link(
    "pages/register.py",
    label="Register",
    icon=":material/person_add:",
    use_container_width=True,
)

hero_col1, hero_col2 = st.columns([1.35, 0.65], gap="medium")

with hero_col1:
    st.markdown(
        """
        <section class="hero-card simple-hero fade-in-section">
            <p class="eyebrow">Simple and secure access</p>
            <h1>Sign in with your face.</h1>
            <p class="hero-subtitle">A clean login system built for fast and secure access.</p>
            <p class="hero-copy">
                Create an account with a face profile, then log in without typing a password.
                Everything is organized to keep access simple, clear, and easy to use.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    hero_action_col1, hero_action_col2 = st.columns(2)
    hero_action_col1.page_link(
        "pages/register.py",
        label="Register Face",
        icon=":material/person_add:",
        use_container_width=True,
    )
    hero_action_col2.page_link(
        "pages/login.py",
        label="Login With Face",
        icon=":material/verified_user:",
        use_container_width=True,
    )

with hero_col2:
    st.markdown(
        """
        <div class="panel-card home-purpose-card fade-in-section">
            <p class="card-label">Secure Login</p>
            <h3>Password-free sign in</h3>
            <p>
                Register once, scan on login, and move straight into the system when access is approved.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

section_col1, section_col2 = st.columns(2, gap="medium")

with section_col1:
    st.markdown(
        """
        <div class="feature-card fade-in-section">
            <div class="feature-icon">📝</div>
            <p class="card-label">Register</p>
            <h3>Create a face profile</h3>
            <p>
                Enter a name or user ID, capture face images, and prepare the account for future login.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with section_col2:
    st.markdown(
        """
        <div class="feature-card fade-in-section">
            <div class="feature-icon">🔓</div>
            <p class="card-label">Login</p>
            <h3>Verify identity quickly</h3>
            <p>
                Scan a face, review the result, and move to the welcome page when access is granted.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### How It Works")
step_col1, step_col2, step_col3 = st.columns(3, gap="medium")

with step_col1:
    st.markdown(
        """
        <div class="panel-card simple-step-card fade-in-section">
            <p class="card-label">Step 1</p>
            <h3>Register your face</h3>
            <p>Open Register and capture the images needed to create a face profile.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with step_col2:
    st.markdown(
        """
        <div class="panel-card simple-step-card fade-in-section">
            <p class="card-label">Step 2</p>
            <h3>Open the login page</h3>
            <p>Use the scan area to check identity and review the login result.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with step_col3:
    st.markdown(
        """
        <div class="panel-card simple-step-card fade-in-section">
            <p class="card-label">Step 3</p>
            <h3>Access the welcome page</h3>
            <p>When the face is recognized, continue directly to the approved welcome page.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
