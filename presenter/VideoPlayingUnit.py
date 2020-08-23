from PyQt5.QtCore import pyqtSlot, Qt, QEvent, QObject
from PyQt5.QtGui import QPixmap, QImage

from common.utils import Log
from model.video import Video
from presenter.MySignals import mySignals


class VideoPlayingUnit(QObject):
    def __init__(self, mwindow):
        Log.debug('')
        self.mw = mwindow
        super().__init__()

        self.entry_row_index = None
        self.video_model = None
        self.video_playing = False

        (
            self.mw.table_timeline.horizontalHeader().sectionClicked.connect(
                self.mw.table_timeline.slot_horizontalHeaderClicked),
        )
        (
            mySignals.schedule.connect(self.slot_schedule),
            mySignals.timer_video.timeout.connect(self.timer_flush_frame),
            mySignals.video_pause_or_resume.connect(self.pause_or_resume),
            mySignals.video_start.connect(self.slot_start),
            mySignals.video_pause.connect(self.slot_pause),
            mySignals.follow_to.connect(self.mw.slot_follow_to),
        )
        (
            self.mw.label_show.installEventFilter(self),
        )
        (
            self.mw.spin_interval.textChanged.connect(self.mw.slot_interval_changed),
            self.mw.combo_speed.currentTextChanged.connect(self.mw.slot_speed_changed),
            self.mw.input_jumpto.textChanged.connect(self.mw.slot_input_jumpto_changed),
        )
        (
            self.mw.btn_to_head.clicked.connect(self.to_head),
            self.mw.btn_to_tail.clicked.connect(self.to_tail),
            self.mw.btn_stop.clicked.connect(self.slot_btn_stop),
            self.mw.btn_open_video.clicked.connect(self.slot_open_file),
        )

    def eventFilter(self, source, event):
        # Log.debug(source, event)
        if source == self.mw.label_show:
            if event.type() == QEvent.MouseButtonPress:
                Log.debug(source, event)
                self.pause_or_resume()

        return False

    def slot_open_file(self):
        # TODO: remove native directory
        # got = QFileDialog().getOpenFileName(self.mw, "Open Image", "/Users/zdl/Downloads/下载-视频",
        #                                     "Media Files (*.mp4 *.jpg *.bmp)", options=QFileDialog.ReadOnly)
        got = ['/Users/zdl/Downloads/下载-视频/金鞭溪-张家界.mp4']
        Log.info(got)
        fname = got[0]
        if fname:
            video = Video(fname)
            self.mw.table_timeline.set_column_count(video.get_info()['frame_c'])
            self.set_video(video)
            mySignals.timer_start(1000 / video.get_info()['fps'] / float(self.mw.combo_speed.currentText()))
            mySignals.video_start.emit()

    def slot_btn_stop(self):
        Log.debug('')
        self.video_playing = False
        self.mw.label_show.clear()

    def slot_schedule(self, jump_to, bias, stop_at, emitter):
        # index: related signal defined to receive int parameters, None will be cast to large number 146624904,
        #        hence replace None with -1
        if jump_to != -1:
            bias = None
        Log.info(jump_to, bias)

        if self.video_model:
            self.video_model.schedule(jump_to, bias, stop_at, emitter)

    @pyqtSlot()
    def timer_flush_frame(self):
        if self.video_model is None:
            return
        if not self.video_playing and not self.video_model.scheduled:
            return

        emitter, i, frame = self.video_model.read()
        if frame is None:
            self.video_playing = False
            return
        # mySignals.follow_to.emit(emitter, i)
        self.mw.slot_follow_to(emitter, i)
        self.mw.table_timeline.slot_follow_to(emitter, i)

        height, width, bytesPerComponent = frame.shape
        bytesPerLine = bytesPerComponent * width
        q_image = QImage(frame.data, width, height, bytesPerLine,
                         QImage.Format_RGB888).scaled(self.mw.label_show.width(), self.mw.label_show.height(),
                                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        q_pixmap = QPixmap.fromImage(q_image)
        self.mw.label_show.setPixmap(q_pixmap)

        # self.label_note.setText(f'frame:{self.cur_index}')

        # elif not ret:
        #     self.cap.release()
        #     # self.timer_video.stop()
        #     # self.statusBar.showMessage('播放结束！')
        # else:
        #     self.flush_frame()

    def pause_or_resume(self):
        if self.video_playing:
            self.slot_pause()
        else:
            self.slot_start()

    def slot_pause(self):
        Log.info('')
        self.video_playing = False

    def slot_start(self):
        # self.timer_video.start()
        if not self.video_model:
            return
        self.video_playing = True

    def set_video(self, video):
        self.video_model = video

    def to_head(self):
        pass

    def to_tail(self):
        pass
