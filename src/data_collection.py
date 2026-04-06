from datetime import datetime
import re
import shutil
import time

import cv2
import numpy as np

from config import DATASET_DIR, IMG_SIZE, PROCESSED_DATA_DIR, RAW_DATA_DIR


def sanitize_user_identifier(user_identifier: str) -> str:
	cleaned_value = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", user_identifier.strip())
	cleaned_value = cleaned_value.strip(" .")
	return cleaned_value or "user"


def decode_uploaded_image(uploaded_file) -> tuple[object, bytes, str]:
	if uploaded_file is None:
		return None, b"", "Capture an image first before continuing."

	if isinstance(uploaded_file, (bytes, bytearray)):
		file_bytes = bytes(uploaded_file)
	else:
		file_bytes = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
	if not file_bytes:
		return None, b"", "Capture an image first before continuing."

	image_array = np.frombuffer(file_bytes, dtype=np.uint8)
	image_frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
	if image_frame is None:
		return None, b"", "The captured image could not be decoded. Try capturing again."

	return image_frame, file_bytes, ""


def encode_image_frame(image_frame) -> bytes:
	success, encoded_image = cv2.imencode(".jpg", image_frame)
	if not success:
		return b""
	return encoded_image.tobytes()


def detect_face_bounds(image_frame):
	gray_image = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
	face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
	faces = face_cascade.detectMultiScale(gray_image, 1.3, 5)
	if len(faces) == 0:
		return None

	return faces[0]


def count_registered_images(user_identifier: str) -> int:
	user_directory = DATASET_DIR / sanitize_user_identifier(user_identifier)
	if not user_directory.exists():
		return 0

	return sum(1 for path in user_directory.iterdir() if path.is_file())


def _prepare_user_directories(safe_identifier: str):
	raw_directory = RAW_DATA_DIR / safe_identifier
	dataset_directory = DATASET_DIR / safe_identifier
	processed_directory = PROCESSED_DATA_DIR / safe_identifier

	for directory in (raw_directory, dataset_directory, processed_directory):
		directory.mkdir(parents=True, exist_ok=True)

	return raw_directory, dataset_directory, processed_directory


def _reset_user_capture_directories(safe_identifier: str) -> None:
	for base_directory in (RAW_DATA_DIR, DATASET_DIR, PROCESSED_DATA_DIR):
		user_directory = base_directory / safe_identifier
		if user_directory.exists():
			shutil.rmtree(user_directory)


def _save_capture_frame(user_identifier: str, image_frame, file_bytes: bytes | None = None, face_bounds=None) -> dict:
	safe_identifier = sanitize_user_identifier(user_identifier)
	face_bounds = face_bounds or detect_face_bounds(image_frame)
	if face_bounds is None:
		return {
			"success": False,
			"status": "capture_failed",
			"message": "No face was detected in the captured image.",
			"images_captured": count_registered_images(safe_identifier),
			"user_identifier": safe_identifier,
		}

	if file_bytes is None:
		file_bytes = encode_image_frame(image_frame)
	if not file_bytes:
		return {
			"success": False,
			"status": "capture_failed",
			"message": "The captured frame could not be encoded. Try again.",
			"images_captured": count_registered_images(safe_identifier),
			"user_identifier": safe_identifier,
		}

	raw_directory, dataset_directory, processed_directory = _prepare_user_directories(safe_identifier)
	capture_index = count_registered_images(safe_identifier)
	file_stem = f"{safe_identifier}_{capture_index:03d}_{datetime.now():%Y%m%d%H%M%S}"
	raw_path = raw_directory / f"{file_stem}.jpg"
	dataset_path = dataset_directory / f"{file_stem}.jpg"
	processed_path = processed_directory / f"{file_stem}.jpg"

	raw_path.write_bytes(file_bytes)
	dataset_path.write_bytes(file_bytes)

	x, y, w, h = face_bounds
	cropped_face = image_frame[y:y + h, x:x + w]
	processed_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
	processed_face = cv2.resize(processed_face, IMG_SIZE)
	cv2.imwrite(str(processed_path), processed_face)

	saved_count = count_registered_images(safe_identifier)
	return {
		"success": True,
		"status": "images_captured",
		"message": f"Captured and saved {saved_count} image(s) for {safe_identifier}.",
		"images_captured": saved_count,
		"user_identifier": safe_identifier,
		"raw_path": str(raw_path),
		"dataset_path": str(dataset_path),
		"processed_path": str(processed_path),
	}


def save_registration_capture(user_identifier: str, uploaded_file) -> dict:
	image_frame, file_bytes, error_message = decode_uploaded_image(uploaded_file)
	if error_message:
		return {
			"success": False,
			"status": "capture_failed",
			"message": error_message,
			"images_captured": count_registered_images(user_identifier),
			"user_identifier": sanitize_user_identifier(user_identifier),
		}

	return _save_capture_frame(user_identifier, image_frame, file_bytes=file_bytes)


def save_registration_frame(user_identifier: str, image_frame) -> dict:
	return _save_capture_frame(
		user_identifier,
		image_frame,
		file_bytes=encode_image_frame(image_frame),
	)


def reset_registration_frames(user_identifier: str) -> None:
	_reset_user_capture_directories(sanitize_user_identifier(user_identifier))


def _open_camera(camera_index: int = 0):
	preferred_backend = cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else None
	camera_indices = [camera_index, 1, 2]
	seen_indices = set()

	for current_index in camera_indices:
		if current_index in seen_indices:
			continue
		seen_indices.add(current_index)

		if preferred_backend is not None:
			camera = cv2.VideoCapture(current_index, preferred_backend)
			if camera.isOpened():
				return camera
			camera.release()

		camera = cv2.VideoCapture(current_index)
		if camera.isOpened():
			return camera
		camera.release()

	return cv2.VideoCapture(camera_index)


def capture_registration_images_from_webcam(
	user_identifier: str,
	target_image_count: int,
	camera_index: int = 0,
	capture_interval_seconds: float = 0.35,
	max_duration_seconds: float | None = None,
) -> dict:
	required_count = max(1, int(target_image_count))
	safe_identifier = sanitize_user_identifier(user_identifier)
	_reset_user_capture_directories(safe_identifier)

	camera = _open_camera(camera_index)
	if not camera.isOpened():
		return {
			"success": False,
			"status": "capture_failed",
			"message": "Webcam could not be opened. Close other camera apps and try again.",
			"images_captured": 0,
			"user_identifier": safe_identifier,
		}

	captured_count = 0
	cancelled = False
	started_at = time.monotonic()
	max_duration_seconds = max_duration_seconds or max(30.0, required_count * 1.5)
	last_capture_at = 0.0
	window_name = "FaceAuth Registration Capture"

	try:
		while captured_count < required_count:
			if time.monotonic() - started_at > max_duration_seconds:
				break

			frame_ready, frame = camera.read()
			if not frame_ready:
				continue

			preview_frame = frame.copy()
			face_bounds = detect_face_bounds(frame)
			if face_bounds is not None:
				x, y, w, h = face_bounds
				cv2.rectangle(preview_frame, (x, y), (x + w, y + h), (0, 200, 0), 2)

			cv2.putText(
				preview_frame,
				f"Captured: {captured_count}/{required_count}",
				(20, 30),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.8,
				(0, 255, 0),
				2,
			)
			cv2.putText(
				preview_frame,
				"Look at the camera. Press Q to cancel.",
				(20, 60),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.6,
				(255, 255, 255),
				2,
			)
			cv2.imshow(window_name, preview_frame)

			key = cv2.waitKey(1) & 0xFF
			if key in (ord("q"), 27):
				cancelled = True
				break

			if face_bounds is None:
				continue

			now = time.monotonic()
			if now - last_capture_at < capture_interval_seconds:
				continue

			save_result = _save_capture_frame(
				safe_identifier,
				frame,
				file_bytes=encode_image_frame(frame),
				face_bounds=face_bounds,
			)
			if save_result["success"]:
				captured_count = save_result["images_captured"]
				last_capture_at = now
	finally:
		camera.release()
		cv2.destroyAllWindows()

	if cancelled:
		return {
			"success": False,
			"status": "capture_cancelled",
			"message": "Capture was cancelled before all photos were collected.",
			"images_captured": captured_count,
			"user_identifier": safe_identifier,
		}

	if captured_count < required_count:
		return {
			"success": False,
			"status": "capture_incomplete",
			"message": f"Only {captured_count} of {required_count} photo(s) were captured. Try again with better lighting and keep your face centered.",
			"images_captured": captured_count,
			"user_identifier": safe_identifier,
		}

	return {
		"success": True,
		"status": "images_captured",
		"message": f"Captured {captured_count} image(s) for {safe_identifier}.",
		"images_captured": captured_count,
		"user_identifier": safe_identifier,
	}


def capture_login_frame_from_webcam(camera_index: int = 0, timeout_seconds: float = 10.0):
	camera = _open_camera(camera_index)
	if not camera.isOpened():
		return None, "Webcam could not be opened. Close other camera apps and try again."

	started_at = time.monotonic()
	window_name = "FaceAuth Login Scan"

	try:
		while time.monotonic() - started_at <= timeout_seconds:
			frame_ready, frame = camera.read()
			if not frame_ready:
				continue

			preview_frame = frame.copy()
			face_bounds = detect_face_bounds(frame)
			if face_bounds is not None:
				x, y, w, h = face_bounds
				cv2.rectangle(preview_frame, (x, y), (x + w, y + h), (0, 200, 0), 2)

			cv2.putText(
				preview_frame,
				"Align your face. Press Q to cancel.",
				(20, 30),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.7,
				(255, 255, 255),
				2,
			)
			cv2.imshow(window_name, preview_frame)

			key = cv2.waitKey(1) & 0xFF
			if key in (ord("q"), 27):
				return None, "Login scan was cancelled."

			if face_bounds is not None:
				return frame, ""
	finally:
		camera.release()
		cv2.destroyAllWindows()

	return None, "No face was detected before the login scan timed out."
