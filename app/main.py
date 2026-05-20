import os
import sys
import streamlit as st

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

st.set_page_config(page_title="FaceAuth AI", page_icon="🔒")
st.title("FaceAuth AI")
st.write(
    "FaceAuth AI is an end-to-end face login system built with OpenCV, scikit-learn, and Streamlit. "
    "Use the Streamlit pages to register a new user and then login with your face."
)

st.markdown("---")
st.header("How to use")
st.write(
    "1. Open the Register page and add a new user with 5–10 face samples.\n"
    "2. Train the model once there are at least two users.\n"
    "3. Open the Login page to authenticate with your face."
)
