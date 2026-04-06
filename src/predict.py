import logging
import pickle
from pathlib import Path

import cv2
import joblib
import numpy as np

from config import KNN_DISTANCE_THRESHOLD, MODEL_PATH, PROBABILITY_THRESHOLD
from src.preprocessing import process_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_model(model_path: Path = MODEL_PATH):
    if not model_path.exists():
        raise FileNotFoundError(f"Critical Error: Model file not found at {model_path}")

    logging.info("Loading model from %s", model_path)
    try:
        return joblib.load(model_path)
    except Exception:
        with model_path.open("rb") as model_file:
            return pickle.load(model_file)


def preprocess_face(face_img, target_size=(64, 64), normalize: bool = False):
    if len(face_img.shape) == 3:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)

    face_resized = cv2.resize(face_img, target_size).astype("float32")
    if normalize:
        face_resized /= 255.0

    return face_resized.flatten().reshape(1, -1)


def detect_face(img, cascade_path="haarcascade_frontalface_default.xml"):
    cascade = cv2.CascadeClassifier(cascade_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    if len(faces) == 0:
        return None

    return faces[0]


def predict_face(frame, model=None, distance_threshold: float = KNN_DISTANCE_THRESHOLD):
    model = model or load_model()
    features = process_image(frame)
    if features is None:
        return {
            "recognized_user": None,
            "access_granted": False,
            "score": 0.0,
            "metric": "distance",
            "threshold": distance_threshold,
            "message": "No face was detected in the captured image.",
        }

    sample = np.asarray(features, dtype=np.float32).reshape(1, -1)

    if isinstance(model, dict) and model.get("model_type") == "simple_knn":
        samples = np.asarray(model.get("samples", []), dtype=np.float32)
        labels = np.asarray(model.get("labels", []))
        if len(samples) == 0 or len(labels) == 0:
            return {
                "recognized_user": None,
                "access_granted": False,
                "score": 0.0,
                "metric": "distance",
                "threshold": distance_threshold,
                "message": "The trained model does not contain any saved samples.",
            }

        normalized_distances = np.linalg.norm(samples - sample, axis=1) / np.sqrt(sample.shape[1])
        nearest_indices = np.argsort(normalized_distances)[: max(1, int(model.get("k", 1)))]
        nearest_labels = labels[nearest_indices]
        nearest_distances = normalized_distances[nearest_indices]
        unique_labels, counts = np.unique(nearest_labels, return_counts=True)
        best_label = unique_labels[np.argmax(counts)]
        score = float(np.mean(nearest_distances))
        access_granted = score <= distance_threshold

        return {
            "recognized_user": str(best_label) if access_granted else "Unknown",
            "access_granted": access_granted,
            "score": score,
            "metric": "distance",
            "threshold": distance_threshold,
            "message": "Access granted." if access_granted else "Access denied.",
        }

    if hasattr(model, "kneighbors") and hasattr(model, "classes_"):
        distances, indices = model.kneighbors(sample, n_neighbors=1)
        distance = float(distances[0][0])
        recognized_user = model.classes_[indices[0][0]] if distance < distance_threshold else "Unknown"
        return {
            "recognized_user": recognized_user,
            "access_granted": recognized_user != "Unknown",
            "score": distance,
            "metric": "distance",
            "threshold": distance_threshold,
            "message": "Access granted." if recognized_user != "Unknown" else "Access denied.",
        }

    prediction = model.predict(sample)[0]
    confidence = 1.0
    if hasattr(model, "predict_proba"):
        confidence = float(np.max(model.predict_proba(sample)))

    return {
        "recognized_user": str(prediction),
        "access_granted": confidence >= PROBABILITY_THRESHOLD,
        "score": confidence,
        "metric": "confidence",
        "threshold": PROBABILITY_THRESHOLD,
        "message": "Access granted." if confidence >= PROBABILITY_THRESHOLD else "Access denied.",
    }


def run_system(confidence_threshold: float = 0.6):
    try:
        model = load_model()
    except FileNotFoundError as error:
        logging.error(error)
        model = None
    except Exception as error:
        logging.error(error)
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("Cannot open webcam")
        return

    logging.info("System Active. Press 'q' to exit.")
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.warning("Failed to grab frame")
            break

        face_rect = detect_face(frame, cascade_path)
        if face_rect is None:
            cv2.putText(
                frame,
                "No face detected",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )
            cv2.imshow("Face Login", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue

        x, y, w, h = face_rect
        face_roi = frame[y:y + h, x:x + w]

        if model is None:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(
                frame,
                "Model not loaded",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2,
            )
        else:
            try:
                prediction_result = predict_face(frame, model=model, distance_threshold=KNN_DISTANCE_THRESHOLD)
                if prediction_result["access_granted"]:
                    label = f"{prediction_result['recognized_user']} ({prediction_result['score']:.2f})"
                    color = (0, 255, 0)
                else:
                    label = "Unknown / Low Confidence"
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(
                    frame,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )
            except Exception as error:
                logging.error("Prediction failed: %s", error)

        cv2.imshow("Face Login", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    logging.info("System stopped.")


if __name__ == "__main__":
    run_system()
