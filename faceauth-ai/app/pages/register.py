import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import sys

# Ensure src modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.train import train_model
from src.preprocessing import detect_and_crop_face

st.title("📝 Register Profile")
st.write("Enter your name and capture at least 5 images to train the model.")

name = st.text_input("Enter your Name (ID):")

# Create raw data folder if it doesn't exist
DATA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw'))
os.makedirs(DATA_ROOT, exist_ok=True)

if name:
    user_dir = os.path.join(DATA_ROOT, name)
    os.makedirs(user_dir, exist_ok=True)
    
    existing_images = len(os.listdir(user_dir))
    st.info(f"Currently saved images for '{name}': **{existing_images}** (Try to get 5 or more!)")
    
    img_file_buffer = st.camera_input("Take a picture")
    
    if img_file_buffer is not None:
        # Check if the image contains a valid face before saving!
        img = Image.open(img_file_buffer)
        img_array = np.array(img)
        
        # Test detection
        face = detect_and_crop_face(img_array)
        
        if face is None:
            st.warning("⚠️ No face detected in this image. Try moving closer or improving lighting!")
        else:
            # Save as BGR for standard expected format later
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            save_path = os.path.join(user_dir, f"capture_{existing_images + 1}.jpg")
            cv2.imwrite(save_path, img_bgr)
            st.success(f"Image {existing_images + 1} saved successfully!")
        
    st.divider()
    st.write("Once you have taken enough images, tell the AI to learn your face!")
    if st.button("🧠 Train AI Model"):
        with st.spinner("Training Model..."):
            success, message = train_model()
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)
