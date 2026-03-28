import numpy as np

def flatten_image(image):
    """
    Convert 2D image into 1D feature vector

    Args:
        image: Preprocessed image (64x64)

    Returns:
        Flattened 1D numpy array
    """

    if image is None:
        return None

    features = image.flatten()

    print(f"📊 Feature vector size: {features.shape}")

    return features


def create_dataset(images, labels):
    """
    Convert lists into ML-ready dataset

    Args:
        images: list of images
        labels: corresponding labels

    Returns:
        X, y numpy arrays
    """

    X = []
    y = []

    for img, label in zip(images, labels):
        features = flatten_image(img)

        if features is not None:
            X.append(features)
            y.append(label)

    print(f"✅ Dataset created with {len(X)} samples")

    return np.array(X), np.array(y)