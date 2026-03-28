import pickle
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

from train import load_data
from feature_engineering import create_dataset


MODEL_PATH = "models/face_model.pkl"


def evaluate():
    print("📊 Evaluating model...")

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    images, labels = load_data()

    X, y = create_dataset(images, labels)

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    y_pred = model.predict(X_test)

    print("\n📊 Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\n📄 Classification Report:")
    print(classification_report(y_test, y_pred))

    print("✅ Evaluation complete!")


if __name__ == "__main__":
    evaluate()