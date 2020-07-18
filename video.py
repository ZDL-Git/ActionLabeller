import cv2
import collections

import global_
from utils import Log


class Video:

    def __init__(self, fname):
        self.fname = fname
        self._cap = cv2.VideoCapture(self.fname)
        self._info = None
        self.cur_index = -1
        self.scheduled = None
        self.frames_buffer = collections.deque(maxlen=100)

    def get_info(self):
        def _count_frames(cap=None):
            cap = cap or cv2.VideoCapture(self.fname)
            cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
            count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            return count

        if self._info is None:
            cap = cv2.VideoCapture(self.fname)
            success, img = cap.read()
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = _count_frames(cap=cap)
            duration = frame_count / fps
            self._info = {'fname': self.fname,
                          'frame_c': frame_count,
                          'duration': duration,
                          'shape': img.shape,
                          'width': img.shape[1],
                          'height': img.shape[0],
                          'channels': img.shape[2],
                          'fps': fps}
        return self._info

    def schedule(self, index, bias, emitter):
        Log.debug(index, bias, self.cur_index)
        if index == -1:
            index = self.cur_index + bias
        self.scheduled = emitter, max(0, min(index, self.get_info()['frame_c'] - 1))

    def read(self):
        if self.scheduled is None:
            self.cur_index += global_.Settings.v_interval
            emitter = global_.Emitter.TIMER
            if global_.Settings.v_interval > 80:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, self.cur_index)
                gap = 1
            else:
                gap = global_.Settings.v_interval
            while gap:
                gap -= 1
                ret, frame = self._cap.read()
                if not ret:
                    return None, None, None
        else:
            emitter, schedule_index = self.scheduled
            self.scheduled = None

            gap = schedule_index - self.cur_index
            if gap > 80 or gap < 1:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, schedule_index)
                gap = 1
            while gap:
                gap -= 1
                ret, frame = self._cap.read()
                if not ret:
                    return None, None, None
            self.cur_index = schedule_index
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # self.frames_buffer.append((self.cur_index, frame))
        return emitter, self.cur_index, frame
