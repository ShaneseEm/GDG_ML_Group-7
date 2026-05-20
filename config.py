import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_SIZE = (64, 64)
DATA_RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
DATASET_DIR = os.path.join(ROOT_DIR, "data", "dataset")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
MODEL_PATH = os.path.join(ROOT_DIR, "models", "face_model.pkl")
