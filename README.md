# FaceAuth AI

FaceAuth AI is a simple face-based authentication system built with OpenCV, scikit-learn, and Streamlit. It supports:

- Registering users with face samples
- Training a KNN-based face recognition model
- Logging in using live webcam facial data

## Features

- Webcam capture for face registration
- Face detection and preprocessing using OpenCV Haar Cascades
- K-Nearest Neighbors model for user classification
- Streamlit UI for registration and login

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:

```bash
streamlit run app/main.py
```

## Usage

1. Open the **Register** page.
2. Enter a user name and capture 5–10 face samples.
3. Train the model once at least two users are registered.
4. Open the **Login** page and authenticate with your face.

## Repository Structure

- `app/` - Streamlit application
  - `main.py` - Landing page and home information
  - `pages/` - Register and Login pages
  - `utils.py` - UI helpers
- `data/` - Dataset storage
  - `dataset/` - Registered face images
- `models/` - Saved model file
- `src/` - Core ML and preprocessing logic
- `tests/` - Basic pipeline tests

## Notes

- Keep `data/dataset` and `models/face_model.pkl` out of version control for privacy and reproducibility.
- Use at least two users to train a stable face recognition model.
