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

        self.scheduled = self.Schedule(None, None, None)

        self.timer.timeout.connect(self.flush)

    @property
    @abstractmethod
    def indices(self):
        pass

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
        self.scheduled.clear()
        if not self.timer.isActive():
            self.timer.start()

    @abstractmethod
    def set_viewer(self, view):
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

    def schedule(self, jump_to, bias, stop_at, emitter):
        logger.debug(f'{jump_to}, {bias}, {stop_at}, {emitter}, {self._flag_cur_index}')
        last_frame_index = self.indices[-1]
        jump_to = self._flag_cur_index + bias if jump_to == -1 else max(0, min(jump_to, last_frame_index))
        stop_at = None if stop_at == -1 else max(0, min(stop_at, last_frame_index))
        self.scheduled.set(emitter, jump_to, stop_at)

    class Signals(QObject):
        flushed = pyqtSignal(int)

    class Schedule:
        def __init__(self, emitter, jump_to, stop_at):
            self.emitter = emitter
            self.jump_to = jump_to
            self.stop_at = stop_at

        def set(self, emitter, jump_to, stop_at):
            self.emitter = emitter
            self.jump_to = jump_to
            self.stop_at = stop_at
            logger.debug(f'scheduled: {self}')

        def clear(self):
            self.emitter = None
            self.jump_to = None
            self.stop_at = None

        def __str__(self):
            return f'emitter:{self.emitter} jumpTo:{self.jump_to} stopAt:{self.stop_at}'

        def __bool__(self):
            return self.emitter is not None and self.jump_to is not None
