import cv2

from src.feature_engineering import image_to_feature_vector

def process_image(image_frame):
    # 1. Grayscale
    gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Face Detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]

        # 3. Resize, flatten, and normalize
        return image_to_feature_vector(face_roi)
        
    return None