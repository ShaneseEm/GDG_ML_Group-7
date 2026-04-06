import numpy as np


def top1_accuracy(predictions, labels) -> float:
    if not labels:
        return 0.0

    prediction_array = np.asarray(predictions)
    label_array = np.asarray(labels)
    return float(np.mean(prediction_array == label_array))