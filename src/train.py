import os
import pickle

import cv2
import numpy as np

from config import MODEL_PATH, PROCESSED_DATA_DIR, TRAINING_DATA_PATH
from src.feature_engineering import image_to_feature_vector
from src.preprocessing import process_image


def _load_user_features(user_name: str, user_path: str, processed: bool) -> tuple[list, list]:
    user_features = []
    user_labels = []

    for img_name in os.listdir(user_path):
        image_path = os.path.join(user_path, img_name)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE if processed else cv2.IMREAD_COLOR)
        if img is None:
            continue

        features = image_to_feature_vector(img) if processed else process_image(img)
        if features is not None:
            user_features.append(features)
            user_labels.append(user_name)

    return user_features, user_labels


def _has_training_images(directory) -> bool:
    if not directory.exists():
        return False

    for user_dir in directory.iterdir():
        if user_dir.is_dir() and any(path.is_file() for path in user_dir.iterdir()):
            return True

    return False


def train_model():
    X, y = [], []
    data_root = PROCESSED_DATA_DIR if _has_training_images(PROCESSED_DATA_DIR) else TRAINING_DATA_PATH
    data_path = str(data_root)

    if not os.path.exists(data_path):
        return f"❌ Error: {data_path} folder not found."

    for user_name in os.listdir(data_path):
        user_path = os.path.join(data_path, user_name)
        if os.path.isdir(user_path):
            user_features, user_labels = _load_user_features(
                user_name,
                user_path,
                processed=data_root == PROCESSED_DATA_DIR,
            )
            X.extend(user_features)
            y.extend(user_labels)

    if len(X) < 30:
        return "❌ Error: Not enough data. Please register at least 30 images."

    features_array = np.asarray(X, dtype=np.float32)
    labels_array = np.asarray(y)
    neighbor_count = min(5, len(features_array))
    model = {
        "model_type": "simple_knn",
        "samples": features_array,
        "labels": labels_array,
        "k": neighbor_count,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("wb") as model_file:
        pickle.dump(model, model_file)

    return f"✅ Success! Model trained on {len(X)} images."