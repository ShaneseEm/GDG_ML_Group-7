import os
import sys
import streamlit as st
import cv2
import pickle
import numpy as np

# --- ABSOLUTE PATH FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.preprocessing import process_image
from src.train import train_model

st.set_page_config(page_title="FaceAuth AI", page_icon="🔒")
st.title("FaceAuth AI Login System")

choice = st.sidebar.selectbox("Action", ["Home", "Register", "Login"])

# --- HOME SECTION ---
if choice == "Home":
    st.subheader("Welcome")
    st.write("Use the sidebar to register new faces or login to the system.")

# --- REGISTER SECTION (FIXED: REQUIRED & NO DUPLICATES) ---
elif choice == "Register":
    st.subheader("Face Registration")
    
    # 1. Capture Name/ID - The 'strip()' removes accidental spaces
    name = st.text_input("Enter Name/ID", key="reg_name").strip()
    
    if name:
        dataset_path = os.path.join(root_dir, "data", "dataset", name)
        
        # Check if folder already exists
        if os.path.exists(dataset_path):
            st.error(f"❌ User '{name}' is already registered. Please use a different ID or go to Login.")
        else:
            st.success(f"✅ ID '{name}' is available.")
            
            # 2. ONLY show camera if name is valid and unique
            img_file = st.camera_input("Register your face")
            
            if img_file:
                os.makedirs(dataset_path, exist_ok=True)
                img_count = len(os.listdir(dataset_path))
                file_path = os.path.join(dataset_path, f"{name}_{img_count}.jpg")
                
                with open(file_path, "wb") as f:
                    f.write(img_file.getbuffer())
                st.success(f"Image {img_count + 1} saved for {name}!")

            # 3. Finalize button inside the valid name block
            if st.button("Finalize & Train System"):
                with st.spinner("Training..."):
                    result = train_model()
                    st.info(result)
    else:
        st.info("💡 Please enter a Name/ID to unlock the camera and registration.")

# --- LOGIN SECTION (FIXED: NO HALLUCINATIONS) ---
elif choice == "Login":
    st.subheader("Face Login")
    login_file = st.camera_input("Scan for Login")
    
    if login_file:
        model_path = os.path.join(root_dir, "models", "face_model.pkl")
        if not os.path.exists(model_path):
            st.error("No model found. Please Register and Train first.")
        else:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            
            file_bytes = np.asarray(bytearray(login_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, 1)
            features = process_image(img)
            
            if features is not None:
                # Use kneighbors to see how "close" this face is to the database
                # This prevents being misidentified as "Natty_2021"
                distances, indices = model.kneighbors([features], n_neighbors=1)
                dist = distances[0][0]
                
                # THRESHOLD: Lower is stricter. 0.5 is usually the 'sweet spot'.
                THRESHOLD = 0.5 
                
                if dist < THRESHOLD:
                    prediction = model.classes_[indices[0][0]]
                    st.success(f"Access Granted: Welcome, {prediction}!")
                    st.balloons()
                else:
                    st.error("Access Denied: Face not recognized.")
                    st.info(f"Debug: Distance {dist:.2f} is too high (Threshold: {THRESHOLD})")
            else:
                st.error("Face not detected. Ensure your face is centered.")