from abc import abstractmethod
from typing import List, Optional

import numpy as np
import pyqtgraph as pg
from zdl.utils.io.log import logger

from model.AbcPlayable import AbcPlayable


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

    @property
    def indices(self):
        return self._indices

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

    def set_range(self, x_range=None, y_range=None):
        logger.debug('')
        if x_range is None:
            x_range = [0, 1280]
        if y_range is None:
            y_range = [0, 720]
        self.plotter: pg.PlotItem
        self.plotter.setRange(xRange=x_range, yRange=y_range, padding=False, disableAutoRange=True)
        return self

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
            if self.flag_indices_index == len(self._fdata):
                return None
            dest_key = self.indices[self.flag_indices_index]

        if self.scheduled.stop_at is not None and dest_key > self.scheduled.stop_at:
            self.scheduled.clear()
            self.stop()
            return None

        self.plot(dest_key)
        self._flag_cur_index = dest_key
        self.signals.flushed.emit(dest_key)
        return dest_key

    @abstractmethod
    def plot(self, index):
        pass
