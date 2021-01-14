from typing import Optional

import numpy as np
import pyqtgraph as pg
from zdl.AI.pose_estimation.pose import *
from zdl.utils.io.file import FileInfo

from actionlabeller.model.AbcPlotting import AbcPlotting


class PosePlotting(AbcPlotting):
    def __init__(self, pose_type):
        super().__init__()
        all_sub_pose_types = {cls.__name__: cls for cls in base_pose.BasePose.__subclasses__()}
        assert pose_type in all_sub_pose_types, f'pose_type {pose_type} not in {list(all_sub_pose_types.keys())}'
        self.pose_type = all_sub_pose_types[pose_type]

        self.file = None  # type:Optional[FileInfo]
        # self.clear_per_frame = True

    def plot(self, key):
        pose_colors = ['#fe8a71', '#0e9aa7', 'gray']  # orange, green, gray
        pose_sections = self.pose_type.SECTIONS

        if self.flag_clear_per_frame:
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
                name = f'pose {p}' if i == 0 else None
                self.plotter.plot(x=x_a, y=y_a, pen=pen,
                                  symbolBrush=symbol_brush, symbolPen=symbol_pen, symbolSize=markersize,
                                  name=name)
