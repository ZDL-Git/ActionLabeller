import queue

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

from common.Log import Log
from model.Playable import Playable
from presenter import MySignals
from presenter.Settings import Settings


class Video(Playable):
    def __init__(self, fname):
        super().__init__()
        self.fname = fname
        self._cap = cv2.VideoCapture(self.fname)
        self._info = None
        self.cur_index = -1
        self.frames_buffer = queue.Queue(maxsize=100)

    def __del__(self):
        self._cap.release()

    def set_view(self, view):
        self.label_show = view
        return self

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

    def flush(self):
        if not self._flag_playing and self.scheduled.jump_to is None:
            return None
        if self.scheduled.stop_at:
            _interval = 1
        else:
            _interval = Settings.v_interval

        if self.scheduled.jump_to is not None:
            dest_index = self.scheduled.jump_to
            # emitter = self.scheduled.emitter
            self.scheduled.jump_to = None
        else:
            dest_index = self.cur_index + _interval
            # emitter = MySignals.Emitter.TIMER

        if self.scheduled.stop_at is not None and dest_index > self.scheduled.stop_at:
            self.scheduled.clear()
            self.stop()
            return None

        _gap = dest_index - self.cur_index
        if _gap > 80 or _gap < 1:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, dest_index)
            _gap = 1
        while _gap:
            _gap -= 1
            ret, frame = self._cap.read()
            if not ret:
                self.schedule(0, -1, 0, MySignals.Emitter.V_PLAYER)
                return None
        self.cur_index = dest_index

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # self.frames_buffer.append((self.cur_index, frame))

        height, width, bytesPerComponent = frame.shape
        bytesPerLine = bytesPerComponent * width
        q_image = QImage(frame.data, width, height, bytesPerLine,
                         QImage.Format_RGB888).scaled(self.label_show.width(), self.label_show.height(),
                                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        q_pixmap = QPixmap.fromImage(q_image)
        self.label_show.setPixmap(q_pixmap)
        self.signals.flushed.emit(self.cur_index)
        return self.cur_index
