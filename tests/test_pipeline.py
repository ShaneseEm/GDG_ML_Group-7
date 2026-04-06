from pathlib import Path
import sys
import unittest

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_collection import sanitize_user_identifier
from src.feature_engineering import image_to_feature_vector
from src.predict import predict_face



class PipelineTests(unittest.TestCase):
    def test_sanitize_user_identifier(self):
        self.assertEqual(sanitize_user_identifier(" Jane:/Doe "), "Jane_Doe")

    def test_image_to_feature_vector_shape(self):
        image = np.zeros((64, 64), dtype=np.uint8)
        features = image_to_feature_vector(image)
        self.assertEqual(features.shape, (4096,))
        self.assertTrue(np.all(features == 0.0))

    def test_predict_face_returns_no_face_for_blank_image(self):
        blank_frame = np.zeros((128, 128, 3), dtype=np.uint8)
        result = predict_face(blank_frame, model={"model_type": "simple_knn", "samples": [], "labels": [], "k": 1})
        self.assertFalse(result["access_granted"])
        self.assertIsNone(result["recognized_user"])


if __name__ == "__main__":
    unittest.main()