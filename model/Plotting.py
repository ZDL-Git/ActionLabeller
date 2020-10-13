from abc import abstractmethod
from typing import List

import numpy as np
import pyqtgraph as pg
from zdl.utils.io.log import logger

from model.Playable import Playable
from model.Scheduleable import Scheduleable
from presenter.CommonUnit import CommonUnit


class Plotting(Playable, Scheduleable):
    def __init__(self):
        super().__init__()
        self.plotter = None
        self._fdata = None
        self._flag_clear_per_frame = True
        self.indices = None  # type: List

        self.flag_plotting = False
        self.flag_plotted_count = 0
        # self.clear_per_frame = True

    def set_data(self, v):
        logger.debug('')
        self._fdata = v
        if isinstance(self._fdata, np.ndarray):
            self.indices = len(self._fdata)
        elif isinstance(self._fdata, dict):
            self.indices = sorted(list(self._fdata.keys()), key=lambda x: int(x))
            # assert type(self.indices[0]) == int, 'covert please!'

        # self.plotter.setXRange(0, 1280, padding=0)
        # self.plotter.setYRange(0, 720, padding=0)
        # self.plotter.vb.setLimits(xMin=0, xMax=1280, yMin=0, yMax=720)
        return self

    @property
    def clear_per_frame(self):
        return self._flag_clear_per_frame

    @clear_per_frame.setter
    def clear_per_frame(self, v):
        self._flag_clear_per_frame = v

    def set_range(self, x_range=None, y_range=None):
        logger.debug('')
        if x_range is None:
            x_range = [0, 1280]
        if y_range is None:
            y_range = [0, 720]
        self.plotter: pg.PlotItem
        self.plotter.setRange(xRange=x_range, yRange=y_range, padding=False, disableAutoRange=True)
        return self

    def schedule(self, jump_to, bias, stop_at, emitter):
        logger.debug(f'{jump_to}, {bias}, {stop_at}, {emitter}, {self._flag_cur_index}')
        if jump_to != -1:
            bias = None

        jump_to = self._flag_cur_index + bias if jump_to == -1 else max(0, min(jump_to, int(self.indices[-1])))
        stop_at = None if stop_at == -1 else max(0, min(stop_at, int(self.indices[-1])))
        self.scheduled.set(emitter, jump_to, stop_at)

    def flush(self):
        if not self._flag_playing and self.scheduled.jump_to is None:
            return None
        if self.scheduled.jump_to is not None:
            dest_index = self.scheduled.jump_to
            dest_key = str(dest_index)
            self.scheduled.jump_to = None
            if dest_key not in self.indices:
                CommonUnit.status_prompt(f'frame {dest_key} not exists!')
                return
            self.flag_plotted_count = self.indices.index(dest_key) + 1
        else:
            if self.flag_plotted_count == len(self._fdata):
                return None
            indices_index = self.flag_plotted_count
            dest_key = self.indices[indices_index]
            dest_index = int(dest_key)
            self.flag_plotted_count += 1

        if self.scheduled.stop_at is not None and dest_index > self.scheduled.stop_at:
            self.scheduled.clear()
            self.stop()
            return None

        self.plot(dest_key)
        self.signals.flushed.emit(dest_index)
        return dest_index

    @abstractmethod
    def plot(self, index):
        pass
