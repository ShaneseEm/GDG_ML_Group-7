import cv2
import os

# Configuration
USER_NAME = "Befa_2023"
DATASET_PATH = "dataset/"
USER_FOLDER = os.path.join(DATASET_PATH, USER_NAME)

if not os.path.exists(USER_FOLDER):
    os.makedirs(USER_FOLDER)

# --- IMPROVED WEBCAM INITIALIZATION ---
# Try index 0 with DirectShow first. If it fails, try index 1.
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) 

if not cam.isOpened():
    print("Warning: Index 0 failed. Trying Index 1...")
    cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cam.isOpened():
    print("CRITICAL ERROR: No webcam found at Index 0 or 1.")
    print("1. Check if another app is using the camera.")
    print("2. Check Windows Privacy Settings for Camera.")
    exit()
# --------------------------------------

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print(f"--- Starting capture for {USER_NAME} ---")
print("Instructions: Press 's' to save a photo. Press 'q' to quit.")

count = 0
while count < 30:
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame. Closing...")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, f"Captured: {count}/30", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Face Registration", frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('s') and len(faces) > 0:
        # Optimization: Save the cropped face for better KNN training
        (x, y, w, h) = faces[0]
        face_roi = frame[y:y+h, x:x+w] 
        
        img_name = f"{USER_NAME}_{count}.jpg"
        img_path = os.path.join(USER_FOLDER, img_name)
        cv2.imwrite(img_path, face_roi) # Saving the crop, not the whole frame
        print(f"Saved: {img_name}")
        count += 1
    
    elif key & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()