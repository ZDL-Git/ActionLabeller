from abc import abstractmethod
from typing import List, Optional

import numpy as np
from zdl.utils.io.log import logger

from actionlabeller.model.AbcPlayable import AbcPlayable


class AbcPlotting(AbcPlayable):
    def __init__(self):
        super().__init__()
        self.plotter = None
        self._fdata = None
        self._indices = None  # type: Optional[List]

        self.flag_plotting = False
        self.flag_indices_index = -1
        self.flag_clear_per_frame = True
        # self.clear_per_frame = True

    def set_viewer(self, view):
        logger.debug('')
        self.plotter = view
        self.plotter.addLegend()
        return self

    def set_data(self, v):
        logger.debug('')
        self._fdata = v
        if isinstance(self._fdata, np.ndarray):
            self._indices = list(range(len(self._fdata)))
        elif isinstance(self._fdata, dict):
            self._indices = sorted(self._fdata.keys())
        else:
            raise ValueError
        # self.plotter.setXRange(0, 1280, padding=0)
        # self.plotter.setYRange(0, 720, padding=0)
        # self.plotter.vb.setLimits(xMin=0, xMax=1280, yMin=0, yMax=720)
        return self

    def to_head(self):
        head = self.indices[0]
        self.schedule(head, -1, head, self.__class__)

    def to_tail(self):
        tail = self.indices[-1]
        self.schedule(tail, -1, tail, self.__class__)

    @property
    def indices(self):
        return self._indices

    def flush(self):
        if not self._flag_playing and self.scheduled.jump_to is None:
            return None
        if self.scheduled.jump_to is not None:
            dest_key, self.scheduled.jump_to = self.scheduled.jump_to, None
            if dest_key not in self.indices:
                logger.error(f'frame {dest_key} not exists!')
                return
            self.flag_indices_index = self.indices.index(dest_key)
        else:
            self.flag_indices_index += 1
            if self.flag_indices_index >= len(self._indices):
                return None
            dest_key = self.indices[self.flag_indices_index]

        if self.scheduled.stop_at is not None and dest_key > self.scheduled.stop_at:
            self.scheduled.clear()
            self.pause()
            return None

        self.plot(dest_key)
        self._flag_cur_index = dest_key
        self.signals.flushed.emit(dest_key)
        return dest_key

    @abstractmethod
    def plot(self, index):
        pass
