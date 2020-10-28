from abc import ABC, abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from zdl.utils.io.log import logger


class AbcPlayable(ABC):
    def __init__(self):
        super().__init__()
        # self.signals = Signals()
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.signals = self.Signals()

        self._flag_playing = False
        self._flag_cur_index = -1

        self.timer.timeout.connect(self.flush)

    @property
    def fps(self):
        return 1000 / self.timer.interval()

    @fps.setter
    def fps(self, fps):
        logger.debug(fps)
        self.timer.setInterval(1000 / fps)

    def is_playing(self):
        return self._flag_playing

    def stop(self):
        logger.debug('')
        self._flag_playing = False
        # self.timer.stop()

    def start(self):
        logger.debug('')
        self._flag_playing = True
        if not self.timer.isActive():
            self.timer.start()

    @abstractmethod
    def set_view(self, view):
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def to_head(self):
        pass

    @abstractmethod
    def to_tail(self):
        pass

    @abstractmethod
    def schedule(self, jump_to, bias, stop_at, emitter):
        pass

    class Signals(QObject):
        flushed = pyqtSignal(int)
