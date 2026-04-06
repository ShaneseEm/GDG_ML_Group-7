import cv2
import numpy as np

# Load the built-in OpenCV Haar Cascade for face detection
# Using cv2.data.haarcascades to automatically locate the XML
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_and_crop_face(image_np, size=(64, 64)):
    """
    Takes an RGB or BGR numpy array image, detects the face,
    crops it, converts to grayscale, and resizes it.
    Returns the processed face array, or None if no face is found.
    """
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) == 0:
        return None
        
    # Get the first face found
    (x, y, w, h) = faces[0]
    face_crop = gray[y:y+h, x:x+w]
    
    # Resize to standard size
    face_resized = cv2.resize(face_crop, size)
    
    return face_resized
