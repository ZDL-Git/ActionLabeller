from abc import ABC, abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from zdl.io.log import darkThemeColorLogger as logger


class Playable(ABC):
    def __init__(self):
        super().__init__()
        # self.signals = Signals()
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.signals = self.Signals()
        self.scheduled = self.Schedule(None, None, None)

        self._flag_playing = False
        self._flag_cur_index = 0

        self.timer.timeout.connect(self.flush)

    def set_fps(self, fps):
        logger.debug(fps)
        self.timer.setInterval(1000 / fps)
        return self

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
    def schedule(self, jump_to, bias, stop_at, emitter):
        pass

    class Schedule:
        def __init__(self, emitter, jump_to, stop_at):
            self.emitter = emitter
            self.jump_to = jump_to
            self.stop_at = stop_at

        def set(self, emitter, jump_to, stop_at):
            self.emitter = emitter
            self.jump_to = jump_to
            self.stop_at = stop_at
            logger.debug('scheduled--')
            logger.debug(self)

        def clear(self):
            self.emitter = None
            self.jump_to = None
            self.stop_at = None

        def __str__(self):
            return f'emitter:{self.emitter} jumpTo:{self.jump_to} stopAt:{self.stop_at}'

        def __bool__(self):
            return self.emitter is not None and self.jump_to is not None

    class Signals(QObject):
        flushed = pyqtSignal(int)
