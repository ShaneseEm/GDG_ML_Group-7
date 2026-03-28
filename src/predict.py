import joblib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_PATH = Path("models/face_model.pkl"
                  
    def load_model(model_path=MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(f"Critical Error: Model file not found at {model_path}")
        logging.info(f"Loading model from {model_path}")
        return joblib.load(model_path)