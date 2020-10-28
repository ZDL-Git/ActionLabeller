from abc import ABC, abstractmethod

from zdl.utils.io.log import logger


class AbcScheduleable(ABC):
    def __init__(self):
        self.scheduled = self.Schedule(None, None, None)

    @abstractmethod
    def schedule(self):
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
            logger.debug(f'scheduled: {self}')

        def clear(self):
            self.emitter = None
            self.jump_to = None
            self.stop_at = None

        def __str__(self):
            return f'emitter:{self.emitter} jumpTo:{self.jump_to} stopAt:{self.stop_at}'

        def __bool__(self):
            return self.emitter is not None and self.jump_to is not None
