import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from zdl.utils.helper.opencv import countFrames

from actionlabeller.model.AbcPlayable import AbcPlayable
from actionlabeller.presenter import MySignals
from actionlabeller.presenter.Settings import Settings


class Video(AbcPlayable):
    def __init__(self, fname):
        super().__init__()
        self.fname = fname
        self._cap = cv2.VideoCapture(self.fname)
        self._info = None
        self._indices = list(range(self.get_info()['frame_c']))
        # self.frames_buffer = queue.Queue(maxsize=100)

    def __del__(self):
        self._cap.release()

    def set_viewer(self, viewer):
        self.viewer = viewer
        return self

    def get_info(self):
        if self._info is None:
            cap = cv2.VideoCapture(self.fname)
            success, img = cap.read()
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = countFrames(cap=cap)
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

    @property
    def indices(self):
        return self._indices

    def to_head(self):
        self.schedule(0, -1, 0, self.__class__)

    def to_tail(self):
        tail = self.get_info()['frame_c'] - 1
        self.schedule(tail, -1, tail, self.__class__)

    def flush(self):
        if not self._flag_playing and self.scheduled.jump_to is None:
            return None
        if self.scheduled.stop_at:
            _interval = 1
        else:
            _interval = Settings.v_interval

        if self.scheduled.jump_to is not None:
            dest_index, self.scheduled.jump_to = self.scheduled.jump_to, None
        else:
            dest_index = self._flag_cur_index + _interval

        if self.scheduled.stop_at is not None and dest_index > self.scheduled.stop_at:
            self.scheduled.clear()
            self.pause()
            return None

        _gap = dest_index - self._flag_cur_index
        if _gap > 80 or _gap < 1:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, dest_index)
            _gap = 1
        while _gap:
            _gap -= 1
            ret, frame = self._cap.read()
            if not ret:
                self.schedule(0, -1, 0, MySignals.Emitter.V_PLAYER)
                return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # self.frames_buffer.append((self.cur_index, frame))
        height, width, bytesPerComponent = frame.shape
        bytesPerLine = bytesPerComponent * width
        q_image = QImage(frame.data, width, height, bytesPerLine,
                         QImage.Format_RGB888).scaled(self.viewer.width(), self.viewer.height(),
                                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        q_pixmap = QPixmap.fromImage(q_image)
        self.viewer.setPixmap(q_pixmap)

        self._flag_cur_index = dest_index
        self.signals.flushed.emit(self._flag_cur_index)
        return self._flag_cur_index
