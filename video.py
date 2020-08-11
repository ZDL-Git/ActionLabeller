import cv2
import collections
import queue

import global_
from utils.utils import Log


class Video:

    def __init__(self, fname):
        self.fname = fname
        self._cap = cv2.VideoCapture(self.fname)
        self._info = None
        self.cur_index = -1
        self.scheduled = self.Schedule(None, None, None)
        self.frames_buffer = queue.Queue(maxsize=100)

    def __del__(self):
        self._cap.release()

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
                          'fps': fps,
                          'Tms': 1000 / fps}
        return self._info

    def schedule(self, jump_to, bias, stop_at, emitter):
        Log.debug(jump_to, bias, stop_at, emitter, self.cur_index)

        jump_to = self.cur_index + bias if jump_to == -1 else max(0, min(jump_to, self.get_info()['frame_c'] - 1))
        stop_at = None if stop_at == -1 else max(0, min(stop_at, self.get_info()['frame_c'] - 1))
        self.scheduled.set(emitter, jump_to, stop_at)

    def read(self):
        # if self.scheduled.emitter and self.scheduled.emitter != global_.Emitter.T_HSCROLL:
        if self.scheduled.stop_at:
            _interval = 1
        else:
            _interval = global_.Settings.v_interval

        if self.scheduled.jump_to:
            dest_index = self.scheduled.jump_to
            emitter = self.scheduled.emitter
            self.scheduled.jump_to = None
        else:
            dest_index = self.cur_index + _interval
            emitter = global_.Emitter.TIMER

        if self.scheduled.stop_at and dest_index > self.scheduled.stop_at:
            self.scheduled.clear()
            return None, None, None

        _gap = dest_index - self.cur_index
        if _gap > 80 or _gap < 1:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, dest_index)
            _gap = 1
        while _gap:
            _gap -= 1
            ret, frame = self._cap.read()
            if not ret:
                self.schedule(0, -1, -1, global_.Emitter.V_PLAYER)
                return None, None, None
        self.cur_index = dest_index

        # if self.scheduled is None:
        #     self.cur_index += global_.Settings.v_interval
        #     emitter = global_.Emitter.TIMER
        #     if global_.Settings.v_interval > 80:
        #         self._cap.set(cv2.CAP_PROP_POS_FRAMES, self.cur_index)
        #         gap = 1
        #     else:
        #         gap = global_.Settings.v_interval
        #     while gap:
        #         gap -= 1
        #         ret, frame = self._cap.read()
        #         if not ret:
        #             self.schedule(0, None, global_.Emitter.V_PLAYER)
        #             return None, None, None
        # else:
        #     emitter, schedule_index = self.scheduled
        #     self.scheduled = None
        #
        #     gap = schedule_index - self.cur_index
        #     if gap > 80 or gap < 1:
        #         self._cap.set(cv2.CAP_PROP_POS_FRAMES, schedule_index)
        #         gap = 1
        #     while gap:
        #         gap -= 1
        #         ret, frame = self._cap.read()
        #         if not ret:
        #             return None, None, None
        #     self.cur_index = schedule_index
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # self.frames_buffer.append((self.cur_index, frame))
        return emitter, self.cur_index, frame

    class Schedule:
        def __init__(self, emitter, jump_to, stop_at):
            self.emitter = emitter
            self.jump_to = jump_to
            self.stop_at = stop_at

        def set(self, emitter, jump_to, stop_at):
            self.emitter = emitter
            self.jump_to = jump_to
            self.stop_at = stop_at

        def clear(self):
            self.emitter = None
            self.jump_to = None
            self.stop_at = None

        def __bool__(self):
            return self.emitter is not None and self.jump_to is not None
