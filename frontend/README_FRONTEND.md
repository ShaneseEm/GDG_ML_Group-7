# FaceAuth AI Frontend

This folder contains the Streamlit frontend for the FaceAuth AI capstone project.

## Purpose

The frontend provides a clean UI for:

- home and landing experience
- face registration flow
- face login flow
- welcome and approved session flow
- connection-ready placeholders for webcam, backend logic, preprocessing, and model inference

## Folder Structure

frontend/
|-- main.py
|-- pages/
|   |-- register.py
|   |-- login.py
|   `-- welcome.py
|-- components/
|   |-- navbar.py
|   |-- status_card.py
|   |-- instructions.py
|   `-- ui_blocks.py
|-- services/
|   |-- api.py
|   `-- mock_backend.py
|-- assets/
|   `-- styles.css
|-- utils/
|   |-- session.py
|   `-- validators.py
`-- README_FRONTEND.md

## How to Run

From the project root, run:

```bash
streamlit run frontend/main.py
```

## What Is Mocked Right Now

- registration image capture response
- registration workflow response
- login scan response
- prediction result and confidence score
- authenticated welcome session display

These mocks exist only so the frontend can be demonstrated before the real backend is connected.

## Where To Connect Real Logic Later

- frontend/services/api.py
  - connect registration requests to backend functions
  - connect login requests to prediction logic
- frontend/services/mock_backend.py
  - replace temporary mock responses with real implementations
- frontend/pages/register.py
  - connect webcam capture and registration actions
- frontend/pages/login.py
  - connect face scan and inference results

## Planned Backend Hooks

- capture_user_images(name)
- save_registration(name)
- preprocess_registered_faces(name)
- capture_login_face()
- predict_user()
- verify_confidence()

## Notes

- The UI intentionally avoids real ML logic.
- The service layer keeps the frontend easy to merge later into a larger app or src structure.
- Session state is used to preserve registration and login results during the Streamlit session.