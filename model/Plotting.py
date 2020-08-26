from abc import ABC, abstractmethod

import numpy as np
import pyqtgraph as pg

from common.utils import Log


class Plotting(ABC):
    def __init__(self, plotter: pg.PlotItem):
        self.plotter = plotter
        self._fdata = None
        self._flag_clear_per_frame = True
        self.indices = None

        self.flag_plotting = False
        self.flag_plotted_count = 0
        # self.clear_per_frame = True

    @property
    def fdata(self):
        return self._fdata

    @fdata.setter
    def fdata(self, v):
        Log.debug('')
        self._fdata = v
        type_ = type(self._fdata)
        if type_ == np.array:
            self.indices = len(self._fdata)
        elif type_ == dict:
            self.indices = sorted(list(self._fdata.keys()))
            # assert type(self.indices[0]) == int, 'covert please!'

        # self.plotter.setXRange(0, 1280, padding=0)
        # self.plotter.setYRange(0, 720, padding=0)
        # self.plotter.vb.setLimits(xMin=0, xMax=1280, yMin=0, yMax=720)

    @property
    def clear_per_frame(self):
        return self._flag_clear_per_frame

    @clear_per_frame.setter
    def clear_per_frame(self, v):
        self._flag_clear_per_frame = v

    def set_range(self, x_range: list = [0, 1280], y_range: list = [0, 720]):
        Log.debug('')
        self.plotter: pg.PlotItem
        self.plotter.setRange(xRange=x_range, yRange=y_range, padding=False, disableAutoRange=True)

    @abstractmethod
    def plot(self, index, clear: bool = None, pose_sections=None):
        pass

    def timer_flush(self) -> int:
        if self.flag_plotted_count == len(self._fdata) - 1:
            return None
        index = self.indices[self.flag_plotted_count]
        self.plot(index)
        self.flag_plotted_count += 1

        return index
