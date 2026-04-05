import cv2
import numpy as np
import joblib
from pathlib import Path
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


MODEL_PATH = Path("models/face_model.pkl")
                  

def load_model(model_path=MODEL_PATH):
    if not model_path.exists():
        raise FileNotFoundError(f"Critical Error: Model file not found at {model_path}")
    logging.info(f"Loading model from {model_path}")
    return joblib.load(model_path)


def preprocess_face(face_img, target_size=(64, 64)):
    """Convert face image to grayscale, resize, and flatten
    for model prediction."""
    if len(face_img.shape) == 3:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    face_resized = cv2.resize(face_img, target_size)

    face_normalized = face_resized / 255.0

    return face_normalized.flatten().reshape(1, -1)


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


def run_system(confidence_threshold=0.6):
    try:
        model = load_model()
    except FileNotFoundError as e:
        # Model not there yet; just run webcam
        logging.error(e)
        model = None
    except Exception as e:
        logging.error(e)
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
                frame, "No face detected",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
            )
            cv2.imshow("Face Login", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        x, y, w, h = face_rect
        face_roi = frame[y:y+h, x:x+w]

        if model is None:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)  # blue
            cv2.putText(
                frame, "Model not loaded",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2
            )
        else:
            try:
                features = preprocess_face(face_roi)
                name = model.predict(features)[0]
                probs = model.predict_proba(features)
                confidence = np.max(probs)

                if confidence > confidence_threshold:
                    label = f"{name} ({confidence:.2f})"
                    color = (0, 255, 0)
                else:
                    label = "Unknown / Low Confidence"
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            except Exception as e:
                logging.error(f"Prediction failed: {e}")

        cv2.imshow("Face Login", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    logging.info("System stopped.")


if __name__ == "__main__":
    run_system()