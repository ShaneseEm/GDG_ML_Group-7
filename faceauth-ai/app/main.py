import streamlit as st
import os

st.set_page_config(page_title="AI FaceAuth", page_icon="👤", layout="centered")

st.title("👤 AI Face Login System")
st.markdown("""
Welcome to the FaceAuth Capstone Project! 
This is a complete end-to-end Machine Learning pipeline that uses **K-Nearest Neighbors** and OpenCV Haar Cascades to perform facial recognition.

### Instructions:
1. Go to the **Register** page from the sidebar to create a profile and capture your face data.
2. Go to the **Login** page to attempt to authenticate using your face!

*(Make sure to grant camera permissions to your browser)*
""")
