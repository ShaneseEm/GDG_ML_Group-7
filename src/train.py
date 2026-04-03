import os
import pickle
import cv2
import numpy as np
from src.preprocessing import process_image
from sklearn.neighbors import KNeighborsClassifier

def train_model():
    X, y = [], []
    # Use absolute path to avoid WinError 3
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.abspath(os.path.join(current_dir, "..", "data", "dataset"))
    
    if not os.path.exists(data_path):
        return f"❌ Error: {data_path} folder not found."

    for user_name in os.listdir(data_path):
        user_path = os.path.join(data_path, user_name)
        if os.path.isdir(user_path):
            for img_name in os.listdir(user_path):
                img = cv2.imread(os.path.join(user_path, img_name))
                if img is not None:
                    features = process_image(img)
                    if features is not None:
                        X.append(features)
                        y.append(user_name)
    
    if len(X) < 5:
        return "❌ Error: Not enough data. Please register at least 5 images."

    # Settings optimized from your Kaggle results (93% accuracy)
    model = KNeighborsClassifier(n_neighbors=5, metric='euclidean')
    model.fit(X, y)
    
    model_dir = os.path.abspath(os.path.join(current_dir, "..", "models"))
    os.makedirs(model_dir, exist_ok=True)
    with open(os.path.join(model_dir, "face_model.pkl"), "wb") as f:
        pickle.dump(model, f)
    
    return f"✅ Success! Model trained on {len(X)} images."