# 💻 FaceAuth: AI Face Login System

**FaceAuth** is an AI-based authentication system that enables users to **register and log in using facial recognition** rather than traditional passwords. This project demonstrates a complete **machine learning pipeline** integrated with a user-friendly interface.

---

## 📌 Features

- **Face Registration:** Capture multiple images per user through a webcam.  
- **Face Recognition:** Preprocess and identify users using a K-Nearest Neighbors (KNN) model.  
- **Confidence Threshold:** Ensures reliable access control by verifying prediction confidence.  
- **Streamlit UI:** Provides an interactive interface for user registration and login.  
- **Multi-User Support:** Supports registration and authentication for multiple users.

---

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/ShaneseEm/GDG_ML_Group-7.git
cd GDG_ML_Group-7


- **Backend / Logic Engineer – Prediction System**  
  **Arsema Negash**  
  - Implements `src/predict.py`.
  - Runs webcam login loop (`run_system`).
  - Detects face with OpenCV Haar Cascade, preprocesses images (convert to grayscale, resize to 64×64, flatten to feature vector), and loads the trained model from `models/face_model.pkl`.
  - Uses a confidence threshold (default `0.6`) to decide whether to show “Access Granted” (high confidence) or “Access Denied / Unknown / Low Confidence” (low confidence or no face).
  - Handles the case when the model file is not yet created, so the webcam still runs and displays “Model not loaded” instead of crashing.
