import random


MOCK_USERS = ["Jane Doe", "Michael Kim", "Amina Yusuf", "Guest User"]
DEFAULT_THRESHOLD = 0.85


def capture_registration_images(name: str) -> dict:
    image_count = random.randint(6, 12)
    return {
        "success": True,
        "status": "images_captured",
        "message": f"Images captured for {name}. Ready for registration.",
        "images_captured": image_count,
        "user_identifier": name,
        "next_step": "TODO: Send captured images to preprocessing pipeline.",
    }


def save_registration(name: str) -> dict:
    return {
        "success": True,
        "status": "registration_saved",
        "message": f"Registration record prepared for {name}.",
        "user_identifier": name,
    }


def preprocess_registered_faces(name: str) -> dict:
    return {
        "success": True,
        "status": "preprocessing_ready",
        "message": f"Preprocessing placeholder completed for {name}.",
        "user_identifier": name,
        "next_step": "TODO: Connect image normalization, detection, and feature extraction.",
    }


def register_user(name: str) -> dict:
    capture_result = capture_registration_images(name)
    save_result = save_registration(name)
    preprocess_result = preprocess_registered_faces(name)

    return {
        "success": True,
        "status": "registration_complete",
        "message": f"Registration complete for {name}.",
        "user_identifier": name,
        "images_captured": capture_result["images_captured"],
        "workflow": {
            "capture": capture_result,
            "save": save_result,
            "preprocess": preprocess_result,
        },
        "todo": "Replace mock registration flow with real backend functions.",
    }


def capture_login_face() -> dict:
    return {
        "success": True,
        "status": "scan_complete",
        "message": "Face scan completed. Ready to run prediction.",
        "frame_source": "camera_placeholder",
        "todo": "Connect this step to webcam capture and face detection.",
    }


def verify_confidence(confidence: float, threshold: float = DEFAULT_THRESHOLD) -> bool:
    return confidence >= threshold


def predict_login_result() -> dict:
    recognized_user = random.choice(MOCK_USERS)
    confidence = round(random.uniform(0.68, 0.98), 4)
    access_granted = verify_confidence(confidence)

    return {
        "success": True,
        "status": "prediction_complete",
        "message": "Access granted." if access_granted else "Access denied.",
        "recognized_user": recognized_user if access_granted else "Unknown",
        "confidence": confidence,
        "threshold": DEFAULT_THRESHOLD,
        "access_granted": access_granted,
        "todo": "Replace mock prediction with trained model inference.",
    }