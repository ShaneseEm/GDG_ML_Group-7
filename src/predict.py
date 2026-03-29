import cv2
import numpy as np
import joblib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_PATH = Path("models/face_model.pkl")
                  
def load_model(model_path=MODEL_PATH):
    if not model_path.exists():
        raise FileNotFoundError(f"Critical Error: Model file not found at {model_path}")
    logging.info(f"Loading model from {model_path}")
    return joblib.load(model_path)
def preprocess_face(face_img, target_size=(64, 64)):
    """Convert face image to grayscale, resize, and flatten
    for model prediction."""
    if len(face_img.shape) == 3:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    face_resized = cv2.resize(face_img, target_size)
    return face_resized.flatten().reshape(1, -1)
