import streamlit as st
import os
import cv2
import numpy as np
import pickle
from PIL import Image
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.preprocessing import detect_and_crop_face

st.title("🔐 Face Login")

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'face_model.pkl'))

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

model = load_model()

if model is None:
    st.warning("No face model found! Please go to the Register page and train the model first.")
else:
    st.write("Look at the camera to log in.")
    img_file_buffer = st.camera_input("Login Camera")
    
    if img_file_buffer is not None:
        img = Image.open(img_file_buffer)
        img_array = np.array(img)
        
        face = detect_and_crop_face(img_array)
        
        if face is None:
            st.error("❌ No face detected. Please ensure your face is clearly visible and well-lit.")
        else:
            # Flatten and normalize
            face_flat = face.flatten().reshape(1, -1) / 255.0
            
            # Predict
            dist, idx = model.kneighbors(face_flat, n_neighbors=1)
            predicted_name = model.predict(face_flat)[0]
            confidence_dist = dist[0][0]
            
            # Distance threshold for KNN (Lower distance = more similar)
            # You can tweak this threshold! Usually something between 5.0 and 15.0 works well for this technique.
            THRESHOLD = 12.0 
            
            if confidence_dist < THRESHOLD:
                st.success(f"✅ Access Granted: **{predicted_name}**")
                st.write(f"*(Confidence Distance: {confidence_dist:.2f} — lower is better)*")
                st.balloons()
            else:
                st.error(f"❌ Access Denied! (Face unrecognized or confidence too low)")
                st.write(f"*(Confidence Distance: {confidence_dist:.2f})*")
