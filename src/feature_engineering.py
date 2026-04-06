import cv2
import numpy as np

from config import IMG_SIZE


def image_to_feature_vector(image, target_size=IMG_SIZE, normalize: bool = True):
    if image is None:
        return None

    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    resized_image = cv2.resize(image, target_size).astype(np.float32)
    flattened = resized_image.flatten()
    if normalize:
        flattened /= 255.0

    return flattened