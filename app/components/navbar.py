from pathlib import Path

import streamlit as st


def load_css() -> None:
    css_path = Path(__file__).resolve().parents[1] / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def render_sidebar(current_page: str) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <p class="sidebar-label">FaceAuth AI</p>
                <h2>Face Login System</h2>
                <p class="sidebar-copy">A simple interface for face registration, login, and welcome access.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page_titles = {
            "home": "Home page active",
            "register": "Registration flow active",
            "login": "Recognition flow active",
            "welcome": "Approved session active",
        }

        st.markdown(
            f"<div class=\"active-chip\">{page_titles.get(current_page, 'FaceAuth AI')}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("### Navigation")
        st.page_link("main.py", label="Home", icon=":material/home:", use_container_width=True)
        st.page_link("pages/register.py", label="Register", icon=":material/person_add:", use_container_width=True)
        st.page_link("pages/login.py", label="Login", icon=":material/verified_user:", use_container_width=True)

        authenticated_user = st.session_state.get("authenticated_user")
        if authenticated_user:
            st.page_link(
                "pages/welcome.py",
                label="Welcome",
                icon=":material/waving_hand:",
                use_container_width=True,
            )
            st.caption(f"Approved user: {authenticated_user}")

        st.markdown(
            """
            <div class="sidebar-note">
                <p class="sidebar-label">Quick Guide</p>
                <p class="sidebar-copy">Use Register to add a face profile and Login to check access with a face scan.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )