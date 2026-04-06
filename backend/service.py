from src.data_collection import count_registered_images, decode_uploaded_image, save_registration_capture
from src.predict import load_model, predict_face
from src.preprocessing import process_image
from src.train import train_model


def capture_registration_images(
    name: str,
    target_image_count: int | None = None,
    uploaded_file=None,
) -> dict:
    if uploaded_file is None:
        return {
            "success": False,
            "status": "capture_failed",
            "message": "Capture an image first before continuing.",
            "images_captured": count_registered_images(name),
            "user_identifier": name.strip(),
            "required_images": max(30, int(target_image_count or 45)),
        }

    return save_registration_capture(name, uploaded_file)


def register_user(name: str, target_image_count: int | None = None) -> dict:
    image_count = count_registered_images(name)
    if image_count == 0:
        return {
            "success": False,
            "status": "registration_failed",
            "message": "No captured face image was found for this user. Capture an image first.",
            "images_captured": 0,
            "user_identifier": name.strip(),
        }

    required_count = max(30, target_image_count or 45)
    if image_count < required_count:
        return {
            "success": False,
            "status": "registration_incomplete",
            "message": f"Capture {required_count - image_count} more image(s) before training.",
            "images_captured": image_count,
            "user_identifier": name.strip(),
            "required_images": required_count,
        }

    training_message = train_model()
    success = training_message.startswith("✅")
    return {
        "success": success,
        "status": "registration_complete" if success else "registration_failed",
        "message": training_message,
        "images_captured": image_count,
        "user_identifier": name.strip(),
        "required_images": required_count,
    }


def capture_login_face(uploaded_file=None) -> dict:
    image_frame, _, error_message = decode_uploaded_image(uploaded_file)

    if error_message:
        return {
            "success": False,
            "status": "scan_failed",
            "message": error_message,
        }

    if process_image(image_frame) is None:
        return {
            "success": False,
            "status": "scan_failed",
            "message": "No face was detected in the captured image.",
        }

    return {
        "success": True,
        "status": "scan_complete",
        "message": "Face scan completed. Ready to run prediction.",
    }


def predict_login_result(uploaded_file=None) -> dict:
    image_frame, _, error_message = decode_uploaded_image(uploaded_file)

    if error_message:
        return {
            "success": False,
            "status": "prediction_failed",
            "message": error_message,
            "recognized_user": "Unknown",
            "access_granted": False,
        }

    try:
        model = load_model()
    except FileNotFoundError:
        return {
            "success": False,
            "status": "prediction_failed",
            "message": "No trained model was found. Complete registration and training first.",
            "recognized_user": "Unknown",
            "access_granted": False,
        }

    prediction_result = predict_face(image_frame, model=model)
    if prediction_result["recognized_user"] is None:
        return {
            "success": False,
            "status": "prediction_failed",
            "message": prediction_result["message"],
            "recognized_user": "Unknown",
            "access_granted": False,
            "metric": prediction_result["metric"],
            "threshold": prediction_result["threshold"],
        }

    access_granted = prediction_result["access_granted"]
    score_label = "distance" if prediction_result["metric"] == "distance" else "confidence"
    return {
        "success": access_granted,
        "status": "prediction_complete" if access_granted else "access_denied",
        "message": "Access granted." if access_granted else "Access denied.",
        "recognized_user": prediction_result["recognized_user"],
        "access_granted": access_granted,
        score_label: prediction_result["score"],
        "metric": prediction_result["metric"],
        "threshold": prediction_result["threshold"],
    }