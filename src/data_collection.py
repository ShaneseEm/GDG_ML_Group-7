import os
import cv2

from config import DATASET_DIR
from src.preprocessing import detect_face


def capture_face_samples(user_id, sample_count=8, camera_index=0):
    save_dir = os.path.join(DATASET_DIR, user_id)
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Unable to access the webcam. Make sure the camera is connected.")

    saved = 0
    while saved < sample_count:
        ret, frame = cap.read()
        if not ret:
            break

        face = detect_face(frame)
        if face is not None:
            face_resized = cv2.resize(face, (64, 64))
            filename = f"{user_id}_{saved + 1}.jpg"
            cv2.imwrite(os.path.join(save_dir, filename), face_resized)
            saved += 1

    cap.release()
    return saved
