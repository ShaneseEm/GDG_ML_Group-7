# FaceAuth AI App

This folder contains the Streamlit app for the FaceAuth AI project.

## Purpose

The app provides a clean UI for:

- home and landing experience
- face registration flow
- face login flow
- welcome and approved session flow
- connection-ready placeholders for webcam, backend logic, preprocessing, and model inference

## Folder Structure

app/
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
streamlit run app/main.py
```

## What Is Mocked Right Now

- registration image capture response
- registration workflow response
- login scan response
- prediction result and confidence score
- authenticated welcome session display

These mocks exist only so the app can be demonstrated before the real backend is connected.

## Where To Connect Real Logic Later

- app/services/api.py
  - connect registration requests to backend functions
  - connect login requests to prediction logic
- app/services/mock_backend.py
  - replace temporary mock responses with real implementations
- app/pages/register.py
  - connect webcam capture and registration actions
- app/pages/login.py
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
- The service layer keeps the app easy to merge later into a larger app or src structure.
- Session state is used to preserve registration and login results during the Streamlit session.