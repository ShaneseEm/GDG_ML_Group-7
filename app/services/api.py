from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

def _get_backend_service_module():
    from backend import service as backend_service_module

    return backend_service_module


def capture_registration_images(
    name: str,
    target_image_count: int | None = None,
    uploaded_file=None,
) -> dict:
    backend_service_module = _get_backend_service_module()
    return backend_service_module.capture_registration_images(
        name,
        target_image_count=target_image_count,
        uploaded_file=uploaded_file,
    )


def register_user(name: str, target_image_count: int | None = None) -> dict:
    backend_service_module = _get_backend_service_module()
    return backend_service_module.register_user(name, target_image_count)


def login_with_face(uploaded_file=None) -> dict:
    backend_service_module = _get_backend_service_module()
    return backend_service_module.capture_login_face(uploaded_file)


def get_prediction_result(uploaded_file=None) -> dict:
    backend_service_module = _get_backend_service_module()
    return backend_service_module.predict_login_result(uploaded_file)