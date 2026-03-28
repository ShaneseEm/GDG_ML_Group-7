from services import mock_backend


def capture_registration_images(name: str) -> dict:
    # TODO: Replace mock capture with OpenCV webcam capture logic or backend API request.
    return mock_backend.capture_registration_images(name)


def register_user(name: str) -> dict:
    # TODO: Replace mock orchestration with calls to:
    # - capture_user_images(name)
    # - save_registration(name)
    # - preprocess_registered_faces(name)
    return mock_backend.register_user(name)


def login_with_face() -> dict:
    # TODO: Replace mock scan with capture_login_face() integration.
    return mock_backend.capture_login_face()


def get_prediction_result() -> dict:
    # TODO: Replace mock prediction with trained model inference and confidence checks.
    return mock_backend.predict_login_result()