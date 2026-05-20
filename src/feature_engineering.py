import numpy as np


def build_feature_matrix(features_list):
    if len(features_list) == 0:
        return np.empty((0, 0))
    return np.vstack(features_list)
