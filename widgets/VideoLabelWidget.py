from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel

import global_
from utils.utils import Log


class VideoLabelWidget(QLabel):

    def __init__(self, parent):
        super().__init__()
        self.entry_row_index = None
        self.video_obj = None
        self.video_playing = False
        # self.v_buffer = collections.deque(maxlen=100)

        # self.cellClicked.connect(self.slot_cellClicked)
        # self.cellActivated.connect(self.slot_cellActivated)
        # self.itemSelectionChanged.connect(self.slot_itemSelectionChanged)
        # self.cellPressed.connect(self.slot_cellPressed)
        global_.mySignals.schedule.connect(self.slot_schedule)
        global_.mySignals.timer_video.timeout.connect(self.timer_flush_frame)
        global_.mySignals.video_pause_or_resume.connect(self.pause_or_resume)
        global_.mySignals.video_start.connect(self.slot_start)
        global_.mySignals.video_pause.connect(self.slot_pause)

    def set_video(self, video):
        self.video_obj = video

    def slot_schedule(self, jump_to, bias, stop_at, emitter):
        # index: related signal defined to receive int parameters, None will be cast to large number 146624904,
        #        hence replace None with -1
        if jump_to != -1:
            bias = None
        Log.info(jump_to, bias)

        if self.video_obj:
            self.video_obj.schedule(jump_to, bias, stop_at, emitter)

    def mousePressEvent(self, e):
        self.pause_or_resume()

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
        if not self.video_obj:
            return
        self.video_playing = True

    @pyqtSlot()
    def timer_flush_frame(self):
        if self.video_obj is None:
            return
        if not self.video_playing and not self.video_obj.scheduled:
            return

        emitter, i, frame = self.video_obj.read()
        if frame is None:
            self.video_playing = False
            return
        global_.mySignals.follow_to.emit(emitter, i)

        height, width, bytesPerComponent = frame.shape
        bytesPerLine = bytesPerComponent * width
        q_image = QImage(frame.data, width, height, bytesPerLine,
                         QImage.Format_RGB888).scaled(self.width(), self.height(),
                                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        q_pixmap = QPixmap.fromImage(q_image)
        self.setPixmap(q_pixmap)

        # self.label_note.setText(f'frame:{self.cur_index}')

        # elif not ret:
        #     self.cap.release()
        #     # self.timer_video.stop()
        #     # self.statusBar.showMessage('播放结束！')
        # else:
        #     self.flush_frame()
