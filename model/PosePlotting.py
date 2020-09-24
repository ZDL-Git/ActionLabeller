import numpy as np
import pyqtgraph as pg
from zdl.utils.io.log import logger

from model.Plotting import Plotting


class PosePlotting(Plotting):
    def __init__(self, ):
        super().__init__()

        self.flag_playing = False
        # self.clear_per_frame = True

    def plot(self, key):
        pose_colors = ['#fe8a71', '#0e9aa7', 'gray']
        pose_sections = [[4, 2, 0, 1, 3], [18, 17, 6, 12, 11, 5, 17], [6, 8, 10], [5, 7, 9],
                         [12, 14, 16],
                         [11, 13, 15], [16, 22, 23, 16, 24], [15, 19, 20, 15, 21]]

        if self.clear_per_frame:
            self.plotter.clear()

        frame_points = self._fdata[key]
        pen = pg.mkPen((200, 200, 200), width=3)

        for p, person_points in enumerate(frame_points):
            person_points = np.asarray(person_points)
            pose_nonzero_b = person_points != 0
            pose_x_or_y_nonzero_b = np.logical_or(pose_nonzero_b[..., 0], pose_nonzero_b[..., 1])

            symbol_pen = pg.mkPen(pose_colors[p])
            symbol_brush = pg.mkBrush(pose_colors[p])
            for i, s in enumerate(pose_sections):
                s_nonzero = np.asarray(s)[pose_x_or_y_nonzero_b[s]]
                x_a = person_points[s_nonzero][..., 0]
                y_a = person_points[s_nonzero][..., 1]

                markersize = 6 if i in [0, 6, 7] else 8
                self.plotter.plot(x=x_a, y=y_a, pen=pen,
                                  symbolBrush=symbol_brush, symbolPen=symbol_pen, symbolSize=markersize)

    def set_view(self, view):
        logger.debug('')
        self.plotter = view
        return self
