from dataclasses import dataclass
import importlib
from pathlib import Path
import sys
import threading
import time

import av
import cv2
from streamlit_webrtc import VideoProcessorBase

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def _get_data_collection_module():
    data_collection_module = importlib.import_module("src.data_collection")
    if not hasattr(data_collection_module, "save_registration_frame"):
        data_collection_module = importlib.reload(data_collection_module)
    return data_collection_module


@dataclass
class CaptureSnapshot:
    captured_images: int
    target_images: int
    status: str
    message: str
    completed: bool
    failed: bool


class RegistrationAutoCaptureProcessor(VideoProcessorBase):
    def __init__(
        self,
        user_identifier: str,
        target_images: int,
        capture_interval_seconds: float = 0.8,
    ) -> None:
        self.user_identifier = user_identifier
        self.target_images = max(1, int(target_images))
        self.capture_interval_seconds = capture_interval_seconds
        self._lock = threading.Lock()
        self._last_capture_at = 0.0
        self._snapshot = CaptureSnapshot(
            captured_images=0,
            target_images=self.target_images,
            status="camera_ready",
            message=f"Camera is ready. Hold still for photo 1 of {self.target_images}.",
            completed=False,
            failed=False,
        )

    def recv(self, frame):
        data_collection_module = _get_data_collection_module()
        image_frame = frame.to_ndarray(format="bgr24")
        preview_frame = image_frame.copy()
        face_bounds = data_collection_module.detect_face_bounds(image_frame)

        if face_bounds is not None:
            x, y, w, h = face_bounds
            cv2.rectangle(preview_frame, (x, y), (x + w, y + h), (0, 200, 0), 2)

        with self._lock:
            snapshot = self._snapshot

        if snapshot.completed:
            cv2.putText(
                preview_frame,
                "Capture complete",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            return av.VideoFrame.from_ndarray(preview_frame, format="bgr24")

        now = time.monotonic()
        if face_bounds is None:
            self._update_snapshot(
                status="camera_ready",
                message=(
                    f"Face not detected. Position your face for photo {snapshot.captured_images + 1} "
                    f"of {self.target_images}."
                ),
                captured_images=snapshot.captured_images,
                completed=False,
                failed=False,
            )
        elif now - self._last_capture_at >= self.capture_interval_seconds:
            save_result = data_collection_module.save_registration_frame(
                self.user_identifier,
                image_frame,
            )
            if save_result["success"]:
                captured_images = int(save_result.get("images_captured", snapshot.captured_images))
                completed = captured_images >= self.target_images
                message = (
                    f"Captured {captured_images} of {self.target_images}. Training will start automatically."
                    if completed
                    else f"Captured {captured_images} of {self.target_images}. Hold still for the next photo."
                )
                self._update_snapshot(
                    status="collecting" if completed else "camera_ready",
                    message=message,
                    captured_images=captured_images,
                    completed=completed,
                    failed=False,
                )
                self._last_capture_at = now
            else:
                self._update_snapshot(
                    status="error",
                    message=save_result["message"],
                    captured_images=snapshot.captured_images,
                    completed=False,
                    failed=True,
                )

        with self._lock:
            current = self._snapshot

        cv2.putText(
            preview_frame,
            f"Captured: {current.captured_images}/{self.target_images}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0) if not current.failed else (0, 0, 255),
            2,
        )
        return av.VideoFrame.from_ndarray(preview_frame, format="bgr24")

    def _update_snapshot(
        self,
        *,
        status: str,
        message: str,
        captured_images: int,
        completed: bool,
        failed: bool,
    ) -> None:
        with self._lock:
            self._snapshot = CaptureSnapshot(
                captured_images=captured_images,
                target_images=self.target_images,
                status=status,
                message=message,
                completed=completed,
                failed=failed,
            )

    def get_snapshot(self) -> CaptureSnapshot:
        with self._lock:
            return CaptureSnapshot(**self._snapshot.__dict__)