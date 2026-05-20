import cv2
import numpy as np
import os
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Load ArcFace model
# -----------------------------
print("Loading ArcFace model...")
app = FaceAnalysis(name="buffalo_l")

# ctx_id=0 → GPU, ctx_id=-1 → CPU
app.prepare(ctx_id=-1, det_size=(640, 640))
print("Model loaded ✅")

# -----------------------------
# Get embedding
# -----------------------------
def get_embedding(img):
    faces = app.get(img)
    if len(faces) == 0:
        return None
    return faces[0].embedding

# -----------------------------
# Build database
# -----------------------------
def build_database(db_path="faces_db"):
    database = {}

    for person in os.listdir(db_path):
        person_path = os.path.join(db_path, person)

        if not os.path.isdir(person_path):
            continue

        embeddings = []

        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)

            img = cv2.imread(img_path)
            if img is None:
                continue

            emb = get_embedding(img)
            if emb is not None:
                embeddings.append(emb)

        if len(embeddings) > 0:
            database[person] = np.mean(embeddings, axis=0)

    return database

# -----------------------------
# Identify face
# -----------------------------
def identify(emb, database, threshold=0.5):
    best_name = "Unknown"
    best_score = -1

    for name, db_emb in database.items():
        score = cosine_similarity([emb], [db_emb])[0][0]

        if score > best_score:
            best_score = score
            best_name = name

    if best_score < threshold:
        return "Unknown", best_score

    return best_name, best_score

# -----------------------------
# Load database
# -----------------------------
print("Building face database...")
database = build_database()

if len(database) == 0:
    print("❌ No faces found in database!")
    exit()

print("Loaded people:", list(database.keys()))

# -----------------------------
# Start webcam
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot access camera")
    exit()

print("Starting camera... Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = app.get(frame)

    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)
        emb = face.embedding

        name, score = identify(emb, database)

        label = f"{name} ({score:.2f})"

        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (96, 46, 155), 2)

        # Put name
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (96, 46, 155), 2)

    cv2.imshow("ArcFace Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()