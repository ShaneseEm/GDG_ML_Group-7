import os
import sys
import base64
import json
import numpy as np
import cv2
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

# ── insightface ──────────────────────────────────────────────────────────────
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__, static_folder="static", template_folder="templates")

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'faces_db'))
os.makedirs(DB_PATH, exist_ok=True)

# Load model once at startup
print("Loading ArcFace model …")
face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=-1, det_size=(640, 640))
print("Model ready ✅")

# ── helpers ───────────────────────────────────────────────────────────────────

def decode_image(data_url: str) -> np.ndarray:
    """Turn a base64 data-URL into a BGR numpy array."""
    header, encoded = data_url.split(",", 1)
    data = base64.b64decode(encoded)
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def get_embedding(img_bgr: np.ndarray):
    faces = face_app.get(img_bgr)
    if not faces:
        return None
    return faces[0].embedding


def build_database():
    database = {}
    if not os.path.isdir(DB_PATH):
        return database
    for person in os.listdir(DB_PATH):
        person_path = os.path.join(DB_PATH, person)
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
        if embeddings:
            database[person] = np.mean(embeddings, axis=0)
    return database


def identify(emb, database, threshold=0.45):
    if not database:
        return "Unknown", 0.0
    best_name, best_score = "Unknown", -1
    for name, db_emb in database.items():
        score = cosine_similarity([emb], [db_emb])[0][0]
        if score > best_score:
            best_score = score
            best_name = name
    if best_score < threshold:
        return "Unknown", float(best_score)
    return best_name, float(best_score)


# ── routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/register")
def register_page():
    return send_from_directory("templates", "register.html")


@app.route("/login")
def login_page():
    return send_from_directory("templates", "login.html")


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    image_data = data.get("image", "")

    if not name or "/" in name or "\\" in name:
        return jsonify({"success": False, "message": "Invalid name."}), 400

    try:
        img = decode_image(image_data)
    except Exception:
        return jsonify({"success": False, "message": "Could not decode image."}), 400

    emb = get_embedding(img)
    if emb is None:
        return jsonify({"success": False, "message": "No face detected. Try again with better lighting!"})

    # ── Duplicate face check ──────────────────────────────────────────────────
    # Compare new face against ALL existing users (regardless of their name).
    # If it's similar enough to someone already in the DB, block the registration.
    DUPLICATE_THRESHOLD = 0.55   # cosine similarity — tune if needed
    database = build_database()
    for existing_name, db_emb in database.items():
        score = float(cosine_similarity([emb], [db_emb])[0][0])
        if score >= DUPLICATE_THRESHOLD and existing_name.lower() != name.lower():
            return jsonify({
                "success": False,
                "message": (
                    f"⚠️ This face is already registered as '{existing_name}' "
                    f"(similarity: {score:.0%}). "
                    f"You cannot register the same face under a different name."
                )
            })
    # ─────────────────────────────────────────────────────────────────────────

    person_dir = os.path.join(DB_PATH, name)
    os.makedirs(person_dir, exist_ok=True)
    filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".jpg"
    cv2.imwrite(os.path.join(person_dir, filename), img)

    count = len(os.listdir(person_dir))
    return jsonify({
        "success": True,
        "message": f"Face saved! ({count} image{'s' if count != 1 else ''} for '{name}')",
        "count": count
    })



@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    image_data = data.get("image", "")

    try:
        img = decode_image(image_data)
    except Exception:
        return jsonify({"success": False, "message": "Could not decode image."}), 400

    emb = get_embedding(img)
    if emb is None:
        return jsonify({"granted": False, "message": "No face detected. Move closer or improve lighting."}), 200

    database = build_database()
    name, score = identify(emb, database)

    if name == "Unknown":
        return jsonify({
            "granted": False,
            "message": f"Access Denied — face not recognized.",
            "score": round(score, 4)
        })
    return jsonify({
        "granted": True,
        "name": name,
        "message": f"Access Granted! Welcome, {name}",
        "score": round(score, 4)
    })


@app.route("/api/users", methods=["GET"])
def api_users():
    if not os.path.isdir(DB_PATH):
        return jsonify({"users": []})
    users = []
    for person in os.listdir(DB_PATH):
        p = os.path.join(DB_PATH, person)
        if os.path.isdir(p):
            users.append({"name": person, "images": len(os.listdir(p))})
    return jsonify({"users": users})


@app.route("/api/train", methods=["POST"])
def api_train():
    """Rebuild the in-memory database (no separate sklearn model needed — we use ArcFace + cosine)."""
    db = build_database()
    if not db:
        return jsonify({"success": False, "message": "No face data found. Please register users first."})
    names = list(db.keys())
    return jsonify({"success": True, "message": f"Database rebuilt with {len(names)} user(s): {', '.join(names)}"})


if __name__ == "__main__":
    app.run(debug=True, port=5050)
