import pyqtgraph as pg
from PyQt5.QtCore import Qt, pyqtSlot, QObject

from common.utils import Log
from model import File
from model.PosePlotting import PosePlotting
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals


class PosePlottingUnit(QObject):
    # inheriting QObject, required by pyqtSlot decorator
    def __init__(self, mwindow):
        Log.debug('')
        self.mw = mwindow
        super().__init__()

        self.fname = None
        self.flag_plotting = False

        self._init_pyqtgraph()
        self.main_plotting_model = PosePlotting(self.main_plotter)

        (
            # self.mw.btn_play_plotting.clicked.connect(self.slot_play),
        )

        (
            mySignals.timer_plotting.timeout.connect(self.slot_timer_flush),
        )

        # self.mw.slider_frame: QSlider
        # self.mw.slider_frame.valueChanged.connect(self.slot_slider_changed)
        # self.mw.btn_open_pose.clicked.connect(self.slot_open_file)
        # self.mw.btn_clear.clicked.connect(self.slot_btn_clear)

        # self.mw.ckb_clear: QCheckBox
        # self.main_plotting.clear_per_frame = self.mw.ckb_clear.checkState() == Qt.Checked
        # self.mw.ckb_clear.stateChanged.connect(self.slot_ckb_clear)
        # global_.mySignals.timer_video.timeout.connect()

    def _init_pyqtgraph(self):
        pg.setConfigOptions(antialias=True)

        # p3 = self.graphics_view.addPlot(title="Drawing with points")  # type: pg.PlotItem

        # self.mw.graphics_view.setBackground('w')
        # self.graphics_view.setAspectLocked(True)

        h, w = 200, 300
        self.main_plotter = self.mw.graphics_view.addPlot()  # type: pg.PlotItem
        self.main_plotter.hideButtons()

        # self.main_plotter.plot(np.random.normal(size=100), pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w')

        # self.main_plot.setFixedHeight(h)
        # self.main_plot.setFixedWidth(w)

        # view_box = pg.ViewBox(p3)
        # view_box.setRange(xRange=[0, 200], yRange=[0, 100], padding=0)
        # self.main_plot.setAxisItems({'left': pg.AxisItem(orientation='left', linkView=view_box)})
        self.main_plotter.setRange(xRange=[0, 200], yRange=[0, 100], padding=False, disableAutoRange=True)
        # self.main_plot.vb.setLimits(xMax=w, yMax=h)

        view_box = self.main_plotter.getViewBox()  # type:pg.ViewBox
        view_box.setMouseEnabled(False, False)
        view_box.invertY(True)
        view_box.setAspectLocked(True, ratio=1)  # keep the content's x y scale consistent, not window

        left_axis = self.main_plotter.getAxis('left')  # type:pg.AxisItem
        bottom_axis = self.main_plotter.getAxis('bottom')  # type:pg.AxisItem
        left_axis.setWidth(22)
        bottom_axis.setHeight(4)

        # left_axis.setTicks([[(i, str(i)) for i in range(0, h + 1, 20)], []])
        # bottom_axis.setTicks([[(i, str(i)) for i in range(0, w + 1, 20)], []])

    def slot_open_file(self):
        # TODO: remove native directory
        got = CommonUnit.get_open_name(filter_="(*.json)")
        # got = ['../sequence_poses_008-part2-count388-dur16s.npy']
        Log.info(got)
        self.fname = got
        if not self.fname:
            return

        self.main_plotting_model.fdata = File.load_dict(self.fname)

        # self.mw.slider_frame: QSlider
        # self.mw.slider_frame.setRange(0, len(self.main_plotting.fdata) - 1)
        # self.mw.slider_frame.setValue(0)

        self.main_plotting_model.plot(self.main_plotting_model.indices[0], True)
        self.main_plotting_model.plotter.plot(x=[0, 0, 1280, 1280, 0], y=[0, 720, 720, 0, 0])
        self.main_plotting_model.set_range([0, 1280], [0, 720])

        self.mw.table_timeline.set_column_num(int(self.main_plotting_model.indices[-1]) + 1)

        mySignals.timer_plotting.start()
        self.flag_plotting = True

    def slot_play(self, checked):
        Log.debug('')

        if self.flag_plotting:
            mySignals.timer_plotting.stop()
            self.flag_plotting = False
        else:
            mySignals.timer_plotting.start()
            self.flag_plotting = True

    def slot_slider_changed(self, v):
        if self.main_plotting_model.fdata is not None:
            self.main_plotting_model.plot(v)

    def slot_btn_clear(self):
        self.main_plotter.clear()

    def slot_ckb_clear(self, state):
        self.main_plotting_model.clear_per_frame = state == Qt.Checked

    @pyqtSlot()
    def slot_timer_flush(self):
        if self.fname is None:
            return
        if not self.flag_plotting:
            return

        index = self.main_plotting_model.timer_flush()
        if index is None:
            mySignals.timer_plotting.stop()
