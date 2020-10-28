from typing import Optional

from zdl.utils.helper import time
from zdl.utils.helper.python import ZDict
from zdl.utils.io.file import JsonFile


class JsonFileLabels(JsonFile):
    def __init__(self, path: Optional[str] = None):
        super().__init__(path)
        self.content = ZDict({
            'video_info': {
                'uri': None,
                'hash_md5': None,
                'w': None,
                'h': None,
            },  # about video file
            'pose_info': {
                'uri': None,
                'hash_md5': None,
            },  # about pose file
            'timestamp': None,
            'labels': {},
        })

    def dump_hooks(self):
        self.content['timestamp'] = time.prettyYToMs()
