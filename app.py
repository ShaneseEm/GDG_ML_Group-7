from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
import os
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Load model
print("Loading ArcFace model...")
app_model = FaceAnalysis(name="buffalo_l")
app_model.prepare(ctx_id=-1, det_size=(640, 640))
print("Model loaded ✅")

# Database
database = {}

def build_database(db_path="faces_db"):
    db = {}
    if not os.path.exists(db_path):
        return db
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
            faces = app_model.get(img)
            if len(faces) > 0:
                embeddings.append(faces[0].embedding)
        if len(embeddings) > 0:
            db[person] = np.mean(embeddings, axis=0)
    return db

def get_embedding(img):
    faces = app_model.get(img)
    if len(faces) == 0:
        return None
    return faces[0].embedding

def identify(emb, db, threshold=0.5):
    best_name = "Unknown"
    best_score = -1.0
    for name, db_emb in db.items():
        score = float(cosine_similarity([emb], [db_emb])[0][0])
        if score > best_score:
            best_score = score
            best_name = name
    if best_score < threshold:
        return "Unknown", float(best_score)
    return best_name, float(best_score)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        image_data = request.form['image']
        # Decode base64
        image_data = image_data.split(',')[1]
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Save to db
        db_root = "faces_db"
        person_dir = os.path.join(db_root, name)
        os.makedirs(person_dir, exist_ok=True)
        filename = f"{name}_{len(os.listdir(person_dir))}.jpg"
        cv2.imwrite(os.path.join(person_dir, filename), img)
        
        # Update database
        global database
        database = build_database()
        
        return jsonify({'status': 'success'})
    return render_template('register.html')

@app.route('/recognize', methods=['GET', 'POST'])
def recognize():
    if request.method == 'POST':
        image_data = request.form['image']
        # Decode base64
        image_data = image_data.split(',')[1]
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        emb = get_embedding(img)
        if emb is None:
            return jsonify({'name': 'No face detected', 'score': 0})
        name, score = identify(emb, database)
        return jsonify({'name': name, 'score': score})
    return render_template('recognize.html')

if __name__ == '__main__':
    database = build_database()
    app.run(debug=True)