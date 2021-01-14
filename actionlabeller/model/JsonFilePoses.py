from typing import Optional, Dict

from numpy.core.multiarray import ndarray
from zdl.utils.helper import time
from zdl.utils.helper.python import ZDict
from zdl.utils.io.file import JsonFile


class JsonFilePoses(JsonFile):
    def __init__(self, path: Optional[str] = None):
        super().__init__(path)
        self.content = ZDict({
            'video_info': {
                'uri': None,
                'hash_md5': None,
                'w': None,
                'h': None,
            },  # about video file
            'info': {
                'pose_type': None,
            },
            'timestamp': None,
            'poses': {},  # type:Dict[int,ndarray]
        })

    def dump_hooks(self):
        self.content['timestamp'] = time.prettyYToMs()

    def load_hooks(self):
        self.content['poses'] = {int(k): v for k, v in self.content['poses'].items()}
