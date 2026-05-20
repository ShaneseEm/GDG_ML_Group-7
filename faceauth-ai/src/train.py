import os
import cv2
import pickle
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from .preprocessing import detect_and_crop_face

DATA_ROOT = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'face_model.pkl')

def train_model():
    X = []
    y = []
    
    if not os.path.exists(DATA_ROOT):
        return False, "No data directory found."
        
    users = [d for d in os.listdir(DATA_ROOT) if os.path.isdir(os.path.join(DATA_ROOT, d))]
    if len(users) < 1:
        return False, "Not enough user data to train."

    for user in users:
        user_dir = os.path.join(DATA_ROOT, user)
        for img_name in os.listdir(user_dir):
            if not img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            
            img_path = os.path.join(user_dir, img_name)
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            face = detect_and_crop_face(img)
            if face is not None:
                # Flatten the 64x64 image into a 1D array of length 4096
                X.append(face.flatten())
                y.append(user)
                
    if len(X) == 0:
        return False, "No valid faces could be extracted from the images."
        
    X = np.array(X)
    y = np.array(y)
    
    # Normalize pixel values
    X = X / 255.0
    
    # Train KNN classifier
    knn = KNeighborsClassifier(n_neighbors=1, weights='distance')
    knn.fit(X, y)
    
    # Save the model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(knn, f)
        
    return True, "Model trained successfully!"
