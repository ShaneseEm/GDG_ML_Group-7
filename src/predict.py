import os
import pickle
import numpy as np
from config import MODEL_PATH
from src.preprocessing import process_image


def load_model(model_path=None):
    path = model_path or MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}")

    with open(path, "rb") as model_file:
        return pickle.load(model_file)


def predict_face(frame, threshold=5.0):
    features = process_image(frame)
    if features is None:
        return None, None, "Face not detected"

    model = load_model()
    features = features.reshape(1, -1)
    
    # Transform features through the pipeline (scaler and pca)
    features_transformed = model.named_steps["scaler"].transform(features)
    features_transformed = model.named_steps["pca"].transform(features_transformed)
    
    distances, _ = model.named_steps["knn"].kneighbors(features_transformed, n_neighbors=1)
    distance = float(distances[0][0])

    if distance < threshold:
        label = model.predict(features)[0]
        return label, distance, None

    return None, distance, "Access Denied"
