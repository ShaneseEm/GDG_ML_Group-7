import os
import pickle
import cv2
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split

from config import DATASET_DIR, MODEL_PATH
from src.preprocessing import process_image
from src.evaluate import evaluate_model

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")


def load_dataset(dataset_dir=None):
    dataset_dir = dataset_dir or DATASET_DIR
    X = []
    y = []

    if not os.path.isdir(dataset_dir):
        return np.array(X), np.array(y)

    for label in sorted(os.listdir(dataset_dir)):
        label_dir = os.path.join(dataset_dir, label)
        if not os.path.isdir(label_dir):
            continue

        for file_name in sorted(os.listdir(label_dir)):
            if not file_name.lower().endswith(SUPPORTED_EXTENSIONS):
                continue

            image_path = os.path.join(label_dir, file_name)
            image = cv2.imread(image_path)
            if image is None:
                continue

            features = process_image(image)
            if features is None:
                continue

            X.append(features)
            y.append(label)

    return np.array(X), np.array(y)


def build_model(n_neighbors=5):
    return Pipeline([
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=0.95, whiten=True)),
        ("knn", KNeighborsClassifier(n_neighbors=n_neighbors, weights="distance"))
    ])


def train_model(dataset_dir=None):
    X, y = load_dataset(dataset_dir)
    if len(X) == 0:
        return {"error": "No processed face images found. Register users first."}

    # Filter out users with fewer than 2 samples
    from collections import Counter
    class_counts = Counter(y)
    valid_classes = [cls for cls, count in class_counts.items() if count >= 2]
    
    if len(valid_classes) < 2:
        return {"error": "Need at least two users with at least 2 face samples each to train the model."}
    
    # Filter X and y to only include valid classes
    valid_indices = [i for i, label in enumerate(y) if label in valid_classes]
    X_filtered = X[valid_indices]
    y_filtered = [y[i] for i in valid_indices]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_filtered, y_filtered, test_size=0.2, stratify=y_filtered, random_state=42
    )

    n_neighbors = min(5, max(1, len(X_train) // 2))
    model = build_model(n_neighbors=n_neighbors)
    model.fit(X_train, y_train)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as model_file:
        pickle.dump(model, model_file)

    metrics = evaluate_model(model, X_test, y_test)
    return {
        "message": f"Model trained with {len(X_train)} samples.",
        "metrics": metrics,
        "model_path": MODEL_PATH,
        "classes": sorted(set(y))
    }
