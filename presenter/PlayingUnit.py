import os
from typing import Optional

import pyqtgraph as pg
from PyQt5.QtCore import QEvent, QObject
from zdl.utils.io.file import FileInfo
from zdl.utils.io.log import logger

from model.AbcPlayable import AbcPlayable
from model.ActionLabel import ActionLabel
from model.JsonFilePoses import JsonFilePoses
from model.PosePlotting import PosePlotting
from model.Video import Video
from presenter import MySignals
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from presenter.Settings import Settings


class PlayingUnit(QObject):
    # Simple implementation, not real singleton.
    # Cannot use class object, cause there is an event installer, must inherit QObject and do instantiation
    only_ins = None

    def __init__(self, mwindow):
        logger.debug('')
        super().__init__()
        self.__class__.only_ins = self
        self.mw = mwindow

        self.media_model = None  # type:Optional[AbcPlayable]
        self.video_model = None  # type:Optional[Video]
        self.images_model = None
        self.pose_model = None  # type:Optional[PosePlotting]
        self.video_playing = False

        self._init_pyqtgraph()

        (
            self.mw.tab_media.currentChanged.connect(self.slot_tabmedia_current_changed),
            self.mw.table_timeline.horizontalHeader().sectionClicked.connect(
                self.slot_tabletimeline_header_clicked),
            self.mw.table_timeline.pressed.connect(self.slot_stop),
            self.mw.table_timeline.doubleClicked.connect(self.table_timeline_cell_double_clicked),
            self.mw.table_labeled.cellDoubleClicked.connect(self.table_labeled_cell_double_clicked),
        )
        (
            mySignals.schedule.connect(self.slot_schedule),
        )
        (
            self.mw.label_show.installEventFilter(self),
        )
        (
            self.mw.spin_interval.textChanged.connect(self.slot_interval_changed),
            self.mw.combo_speed.currentTextChanged.connect(self.slot_speed_changed),
            self.mw.input_jumpto.textChanged.connect(self.slot_input_jumpto_changed),
        )
        (
            self.mw.btn_to_head.clicked.connect(self.slot_to_head),
            self.mw.btn_to_tail.clicked.connect(self.slot_to_tail),
            self.mw.btn_backward.clicked.connect(self.slot_fast_backward),
            self.mw.btn_rewind.clicked.connect(self.slot_fast_rewind),
            self.mw.btn_open_video.clicked.connect(self.slot_open_file),
            self.mw.btn_stop.clicked.connect(self.slot_btn_stop),
            self.mw.btn_play.clicked.connect(self.slot_play_toggle),
        )

    def eventFilter(self, source, event):
        # Log.debug(source, event)
        if source == self.mw.label_show:
            if event.type() == QEvent.MouseButtonPress:
                logger.debug(source)
                logger.debug(event)
                self.slot_play_toggle()

        return False

    def slot_open_file(self):
        # TODO: remove native directory
        all_types_filter = f'*{" *".join(Settings.video_exts + Settings.image_exts + Settings.plotting_exts)}'
        file_uri = CommonUnit.get_open_name(filter_=f"Media Files ({all_types_filter})")
        # got = '/Users/zdl/Downloads/下载-视频/poses.json'
        # got = '/Users/zdl/Downloads/下载-视频/金鞭溪-张家界.mp4'
        logger.info(file_uri)
        if not file_uri:
            return
        ext = os.path.splitext(file_uri)[1]
        if ext in Settings.video_exts:
            self.mw.tab_media.setCurrentIndex(0)
            video_model = Video(file_uri) \
                .set_viewer(self.mw.label_show)
            video_model.fps = video_model.get_info()['fps'] * float(self.mw.combo_speed.currentText())
            video_model.file = FileInfo(file_uri)
            self.video_model = video_model
            self.set_model(video_model)

            self.mw.table_timeline.set_column_num(video_model.get_info()['frame_c'])
            self.mw.video_textBrowser.append(file_uri)
        elif ext in Settings.plotting_exts:
            self.mw.tab_media.setCurrentIndex(2)
            file = JsonFilePoses.load(file_uri)
            pose_model = PosePlotting(file['info.pose_type']) \
                .set_data(file['poses']) \
                .set_viewer(self.main_plotter) \
                .set_range()
            pose_model.file = file
            self.pose_model = pose_model
            self.set_model(pose_model)

            self.mw.table_timeline.set_column_num(int(pose_model.indices[-1]) + 1)
            self.mw.plotting_textBrowser.append(file_uri)
        else:
            logger.warn(f'{file_uri} type {ext} not supported.')
            return
        self.media_model.signals.flushed.connect(self.mw.table_timeline.slot_follow_to)
        self.media_model.signals.flushed.connect(self.slot_follow_to)
        self.media_model.start()

    def slot_btn_stop(self):
        logger.debug('')
        self.video_playing = False
        self.mw.label_show.clear()

    def slot_play_toggle(self):
        logger.debug('')
        if self.media_model is None:
            return
        if self.media_model.is_playing():
            self.media_model.stop()
        else:
            self.media_model.start()

    def slot_stop(self):
        logger.debug('')
        if self.media_model is None:
            return
        self.media_model.stop()

    def slot_start(self):
        logger.debug('')
        if self.media_model is None:
            return
        self.media_model.start()

    def set_model(self, model):
        logger.debug(type(model))
        self.media_model = model

    def slot_fast_backward(self):
        logger.debug('')
        if self.media_model is None:
            return
        step = CommonUnit.get_value(self.mw.input_step, int)
        self.media_model.schedule(-1, -1 * step, -1, MySignals.Emitter.BTN)

    def slot_fast_rewind(self):
        logger.debug('')
        if self.media_model is None:
            return
        step = CommonUnit.get_value(self.mw.input_step, int)
        self.media_model.schedule(-1, step, -1, MySignals.Emitter.BTN)

    def slot_to_head(self):
        logger.debug('')
        self.media_model.to_head()

    def slot_to_tail(self):
        logger.debug('')
        self.media_model.to_tail()

    def slot_interval_changed(self):
        Settings.v_interval = int(self.mw.spin_interval.text() or 1)

    def slot_speed_changed(self):
        logger.debug('')
        try:
            factor = float(self.mw.combo_speed.currentText())
            if isinstance(self.media_model, Video):
                self.media_model.fps = self.media_model.get_info()['fps'] * factor
            elif isinstance(self.media_model, PosePlotting):
                self.media_model.fps = 20 * factor
        except Exception:
            logger.warning('slot_speed_changed fail.', exc_info=True)

    def slot_input_jumpto_changed(self, text):
        try:
            if self.media_model is None:
                return
            jump_to = int(text)
            self.media_model.schedule(jump_to, -1, -1, MySignals.Emitter.INPUT_JUMPTO)
        except Exception:
            logger.warn('Only int number supported!')

    def slot_tabmedia_current_changed(self, index):
        logger.debug(index)
        self.media_model and self.media_model.stop()
        if index == 0:
            self.mw.stacked_widget.setCurrentIndex(0)
            self.set_model(self.video_model)
        elif index == 1:
            self.mw.stacked_widget.setCurrentIndex(0)
            self.set_model(self.images_model)
        elif index == 2:
            self.mw.stacked_widget.setCurrentIndex(1)
            self.set_model(self.pose_model)

    def slot_tabletimeline_header_clicked(self, i):
        logger.debug(f'index {i}')
        self.slot_schedule(i, -1, -1, MySignals.Emitter.T_HSCROLL)

    def slot_schedule(self, jump_to, bias, stop_at, emitter):
        # index: related signal defined to receive int parameters, None will be cast to large number 146624904,
        #        hence replace None with -1
        logger.info(f'{jump_to}, {bias}, {stop_at}, {emitter}')
        if self.media_model is None:
            return
        if jump_to != -1:
            bias = None
        self.media_model.schedule(jump_to, bias, stop_at, emitter)

    def slot_follow_to(self, to):
        CommonUnit.status_prompt(f'Frame {to}')

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

    def table_labeled_cell_double_clicked(self, r, c):
        logger.debug('')
        label = self.mw.table_labeled.label_at(r)
        if not self.label_play(label):
            self.mw.table_timeline.col_to_center(label.begin)

    def table_timeline_cell_double_clicked(self, qindex):
        logger.debug('')
        r, c = qindex.row(), qindex.column()
        label = self.mw.table_timeline.detect_label(r, c)  # type:ActionLabel
        if label:
            self.label_play(label)

    def label_play(self, action_label: ActionLabel):
        self.mw.table_timeline.unselect_all()
        self.mw.table_timeline.select_label(action_label)
        if self.media_model is None:
            return False
        self.media_model.schedule(action_label.begin, -1, action_label.end, MySignals.Emitter.T_LABEL)
        self.media_model.start()
        return True
