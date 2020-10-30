import pyqtgraph as pg
from zdl.utils.io.log import logger


class PlotterGraphicWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._init_pyqtgraph()
        self.main_plotter = self.get_plotter()

    def _init_pyqtgraph(self):
        pg.setConfigOptions(antialias=True)

    def get_plotter(self):
        # p3 = self.graphics_view.addPlot(title="Drawing with points")  # type: pg.PlotItem

        # self.mw.graphics_view.setBackground('w')
        # self.graphics_view.setAspectLocked(True)

        # plotter = self.Plotter(self.addPlot())  # type: PlotterGraphicWidget.Plotter
        plotter = self.addPlot()  # type: pg.PlotItem
        plotter.__class__ = self.Plotter
        plotter.hideButtons()

        # plotter.plot(np.random.normal(size=100), pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w')

        # self.main_plot.setFixedHeight(h)
        # self.main_plot.setFixedWidth(w)

        # view_box = pg.ViewBox(p3)
        # view_box.setRange(xRange=[0, 200], yRange=[0, 100], padding=0)
        # self.main_plot.setAxisItems({'left': pg.AxisItem(orientation='left', linkView=view_box)})
        plotter.setRange(xRange=[0, 200], yRange=[0, 100], padding=False, disableAutoRange=True)
        # self.main_plot.vb.setLimits(xMax=w, yMax=h)

        view_box = plotter.getViewBox()  # type:pg.ViewBox
        view_box.setMouseEnabled(False, False)
        view_box.invertY(True)
        view_box.setAspectLocked(True, ratio=1)  # keep the content's x y scale consistent, not window

        left_axis = plotter.getAxis('left')  # type:pg.AxisItem
        bottom_axis = plotter.getAxis('bottom')  # type:pg.AxisItem
        left_axis.setWidth(22)
        bottom_axis.setHeight(4)

        # left_axis.setTicks([[(i, str(i)) for i in range(0, h + 1, 20)], []])
        # bottom_axis.setTicks([[(i, str(i)) for i in range(0, w + 1, 20)], []])
        return plotter

    class Plotter(pg.PlotItem):
        def __init__(self):
            super().__init__()

        def set_range(self, x_range=None, y_range=None):
            logger.debug(f'{x_range} {y_range}')
            if x_range is None:
                x_range = [0, 1280]
            elif isinstance(x_range, int):
                x_range = [0, x_range]
            if y_range is None:
                y_range = [0, 720]
            elif isinstance(y_range, int):
                y_range = [0, y_range]
            self.setRange(xRange=x_range, yRange=y_range, padding=False, disableAutoRange=True)
            return self
