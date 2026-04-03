import cv2
import numpy as np

def process_image(image_frame):
    # 1. Grayscale
    gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Face Detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        # 3. Resize to 64x64 matching original dataset logic
        face_resized = cv2.resize(face_roi, (64, 64))
        
        # 4. Flatten and Normalize (0 to 1 range)
        return face_resized.flatten() / 255.0 
        
    return None