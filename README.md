
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
=======
# FaceAuth AI - Capstone Project

## Overview
This is a real-world AI-powered authentication system that allows users to register and log in using their face instead of a password.

## Project Goal
An end-to-end Machine Learning pipeline where:
- A user creates a profile using their facial data (live webcam).
- The system embeds their facial features.
- The user can log in by scanning their face against the trained database.
- A confidence threshold protects against false positives.

## Features Built
- **Duplicate Protection:** The system actively checks if a face already exists in the database before allowing registration under a new name.
- **Modern UI:** Built with Flask, HTML, CSS, and JS.
- **Machine Learning Integration:** Uses ArcFace embeddings with Cosine Similarity for extremely high accuracy, handling lighting differences and varying angles far better than basic Haar Cascades + KNN.

## Setup Instructions
1. Clone this repository to your local machine.
2. Install the necessary dependencies: `pip install -r requirements.txt` (including flask, opencv-python, insightface).
3. Start the server using: `python web_app/app.py`
4. Open your browser and navigate to `http://127.0.0.1:5050`.

## Directory Structure
- `web_app/` : Contains the Flask backend and the HTML templates.
- `faces_db/` : Stored database of registered user images.
- `faceauth-ai/` : Alternative original Streamlit implementation files.

## ML Model
This project uses InsightFace's `buffalo_l` model to extract a 512-dimensional embedding of a human face. During evaluation (login), it calculates the Cosine Similarity between the incoming webcam frame and the average embedding of each registered user's face to find a match that passes the confidence threshold.
>>>>>>> 1d7b6260967d14f84a65906bf3c5100c95d64a4f
