import cv2
import numpy as np

# Load Haar Cascade once (efficient)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_and_preprocess(image, size=(64, 64)):
    """
    Detect face, crop it, resize, normalize.

    Args:
        image: Input image (BGR from OpenCV)
        size: Target size (width, height)

    Returns:
        Preprocessed face as numpy array OR None if no face found
    """

    # Convert to grayscale (better for face detection)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) == 0:
        print("⚠️ No face detected in image.")
        return None

    # Take first detected face
    (x, y, w, h) = faces[0]

    # Crop face region
    face = gray[y:y+h, x:x+w]

    # Resize face
    face_resized = cv2.resize(face, size)

    # Normalize pixel values (0 → 1)
    face_normalized = face_resized / 255.0

    print("✅ Face detected and preprocessed")

    return face_normalized