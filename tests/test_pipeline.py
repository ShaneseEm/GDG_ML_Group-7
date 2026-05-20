import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import numpy as np

from src.preprocessing import process_image
from src.train import load_dataset, train_model


def test_process_image_invalid_input():
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    assert process_image(image) is None


def test_load_dataset_empty_directory(tmp_path):
    X, y = load_dataset(str(tmp_path))
    assert X.size == 0
    assert y.size == 0


def test_train_model_empty_directory(tmp_path):
    result = train_model(dataset_dir=str(tmp_path))
    assert isinstance(result, dict)
    assert "error" in result
