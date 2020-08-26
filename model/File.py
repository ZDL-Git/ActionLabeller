import json

import numpy as np


def load_np_array(fname: str) -> np.array:
    return np.load(fname)


def load_dict(fname: str) -> dict:
    with open(fname, 'rb') as f:
        content = json.load(f)
    return content
