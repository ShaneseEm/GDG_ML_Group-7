import cv2
import pickle
import numpy as np

# Load the model you downloaded from Kaggle
with open('models/face_model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict_face(frame):
    # Step 3 & 4: Preprocessing (Must match your Kaggle training exactly!)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return None, 0

    (x, y, w, h) = faces[0]
    face_roi = gray[y:y+h, x:x+w]
    face_resized = cv2.resize(face_roi, (64, 64)).flatten().reshape(1, -1)
    
    # Normalization (if you used /255.0 in Kaggle, do it here too!)
    face_normalized = face_resized / 255.0

    # Step 7: Prediction
    prediction = model.predict(face_normalized)
    
    # Step 8: Confidence Threshold (KNN logic)
    # Get the actual distance to the nearest neighbors
    distances, indices = model.kneighbors(face_normalized)
    confidence = np.mean(distances) 
    
    # Higher distance means less confidence. 
    # Adjust this '0.8' based on your testing!
    if confidence < 0.8: 
        return prediction[0], confidence
    else:
        return "Unknown", confidence