import json

import numpy as np
from zdl.utils.io.log import logger


def load_np_array(fname: str) -> np.array:
    return np.load(fname)


def load_dict(fname: str) -> dict:
    with open(fname, 'rb') as f:
        content = json.load(f)
    logger.info(f'frames num of opened file: {len(content)}')
    return content
