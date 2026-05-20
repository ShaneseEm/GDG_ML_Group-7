import cv2
import numpy as np
from config import IMG_SIZE

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_face(img):
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    return gray[y:y+h, x:x+w]


def process_image(img):
    face = detect_face(img)
    if face is None:
        return None
    face_resized = cv2.resize(face, IMG_SIZE)
    face_normalized = face_resized.astype("float32") / 255.0
    return face_normalized.flatten()
