import os
import cv2
import pickle
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

from preprocessing import detect_and_preprocess
from feature_engineering import create_dataset


DATASET_PATH = "data/raw"
MODEL_PATH = "models/face_model.pkl"


def load_data():
    """
    Load dataset from folders

    Folder structure:
    data/raw/user1/*.jpg
    data/raw/user2/*.jpg
    """

    images = []
    labels = []

    print("📂 Loading dataset...")

    for user in os.listdir(DATASET_PATH):
        user_path = os.path.join(DATASET_PATH, user)

        if not os.path.isdir(user_path):
            continue

        print(f"👤 Processing user: {user}")

        for img_name in os.listdir(user_path):
            img_path = os.path.join(user_path, img_name)

            image = cv2.imread(img_path)

            if image is None:
                continue

            processed = detect_and_preprocess(image)

            if processed is not None:
                images.append(processed)
                labels.append(user)

    return images, labels


def train():
    print("🚀 Starting training process...")

    images, labels = load_data()

    if len(images) == 0:
        print("❌ No data found! Please collect images first.")
        return

    # Feature engineering
    X, y = create_dataset(images, labels)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"📊 Training samples: {len(X_train)}")
    print(f"📊 Testing samples: {len(X_test)}")

    # Model (KNN)
    model = KNeighborsClassifier(n_neighbors=3)

    print("🧠 Training model...")
    model.fit(X_train, y_train)

    # Save model
    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"💾 Model saved at {MODEL_PATH}")

    # Evaluation
    print("📈 Evaluating model...")
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)

    print(f"🎯 Accuracy: {acc * 100:.2f}%")

    print("✅ Training complete!")


if __name__ == "__main__":
    train()