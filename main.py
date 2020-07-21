import sys
import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import global_
from video import Video
from utils import *
from action import ActionLabel

Ui_MainWindow, QtBaseClass = uic.loadUiType("qt_gui/mainwindow.ui")


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.combo_speed.addItems(['0.5', '0.75', '1', '1.25', '1.5', '1.75'])
        self.combo_speed.setCurrentIndex(2)
        self.combo_sortby.addItems(['timestamp', 'filename'])
        self.combo_sortby.setCurrentIndex(1)

        self.spin_interval.textChanged.connect(self.slot_interval_changed)
        self.combo_speed.currentTextChanged.connect(self.slot_speed_changed)
        self.input_jumpto.textChanged.connect(
            lambda text: text and global_.mySignals.jump_to.emit(int(text), None, global_.Emitter.INPUT_JUMPTO))
        self.label_show.installEventFilter(self)

        def init_buttons():
            self.btn_open_video.setFocus()
            self.btn_open_video.clicked.connect(self.slot_open_file)
            self.btn_play.clicked.connect(global_.mySignals.video_pause_or_resume.emit)
            self.btn_to_head.clicked.connect(self.to_head)
            self.btn_to_tail.clicked.connect(self.to_tail)
            self.btn_eval.clicked.connect(self.slot_eval)
            self.btn_new_label_temp.clicked.connect(self.table_label_temp.slot_action_add)
            self.btn_del_label_temp.clicked.connect(self.table_label_temp.slot_del_selected_action)

        def init_settings():
            global_.Settings.v_interval = int(self.spin_interval.text())
            # global_.Settings.v_speed = float(self.combo_speed.currentText())

        def prettify():
            shadowEffect = QGraphicsDropShadowEffect()
            shadowEffect.setColor(QColor(0, 0, 0, 255 * 0.9))
            shadowEffect.setOffset(0)
            shadowEffect.setBlurRadius(8)
            self.label_show.setGraphicsEffect(shadowEffect)
            self.label_note.setGraphicsEffect(shadowEffect)

            vheader = self.table_timeline.verticalHeader()
            vheader.setDefaultSectionSize(5)
            vheader.sectionResizeMode(QHeaderView.Fixed)

        init_buttons()
        init_settings()
        prettify()

        self.table_timeline.__init_later__()
        self.table_labeled.__init_later__()
        self.table_label_temp.__init_later__()

        self.state_mouse_pressing = False
        self.state_mouse_last_point = None

        global_.mySignals.follow_to.connect(self.slot_follow_to)

    def common_slot(self, *arg):
        Log.debug(f'common slot print:', arg)

    def slot_open_file(self):
        # TODO
        got = QFileDialog.getOpenFileName(self, "Open Image", "/Users/zdl/Downloads/下载-视频",
                                          "Image Files (*.mp4 *.jpg *.bmp)")
        # got = ['/Users/zdl/Downloads/下载-视频/金鞭溪-张家界.mp4']
        Log.info(got)
        fname = got[0]
        if fname:
            video = Video(fname)
            self.table_timeline.set_column_count(video.get_info()['frame_c'])
            self.label_show.set_video(video)
            global_.mySignals.timer_start(1000 / video.get_info()['fps'] / float(self.combo_speed.currentText()))
            global_.mySignals.video_start.emit(-1)

    def to_head(self):
        pass

    def to_tail(self):
        pass

    def slot_interval_changed(self):
        global_.Settings.v_interval = int(self.spin_interval.text() or 1)

    def slot_speed_changed(self):
        Log.debug('here')
        new_speed = 1000 / self.label_show.video_obj.get_info()['fps'] / float(self.combo_speed.currentText())
        global_.mySignals.timer_video.setInterval(new_speed)

    def slot_follow_to(self, emitter, to):
        self.label_note.setText(f'Frame {to}')

    def eventFilter(self, source, event):
        if event.type() != 12:
            Log.debug(f'etype {event.type()} source {source}')
        else:
            return False
        if source is self.label_note:
            if event.type() == QEvent.MouseButtonPress:
                print("pressed...")
                self.pause()
                self.state_mouse_pressing = 1
                self.state_mouse_last_point = event.pos()
            elif event.type() == QEvent.MouseButtonRelease:
                self.state_mouse_pressing = 0
            elif event.type() == QEvent.MouseMove:
                print(event.pos())
                cur_pos = event.pos()
                if self.state_mouse_pressing:
                    dis = cur_pos.x() - self.state_mouse_last_point.x()
                    dis = dis // 2
                    if dis > 0:
                        print('forward')
                        self.flush_frame()
                    elif dis < 0:
                        print('backward')
                        self.flush_frame(reverse=True)
                self.state_mouse_last_point = cur_pos
        elif source is self.table_timeline:
            print(f'table_timeline event type {event.type()}')
            if event.type() == QEvent.Wheel:
                print(f'wheel{event.angleDelta()}')
                zoom_in = event.angleDelta().y() > 0
                col_width = self.table_timeline.columnWidth(0)
                col_width += 3 if zoom_in else -3
                width = self.table_timeline.width()
                cols = self.table_timeline.horizontalHeader().count()
                col_width = max(col_width, int(width / cols))
                self.table_timeline.horizontalHeader().setDefaultSectionSize(col_width)
            elif event.type() == QEvent.Wheel:
                pass

        return super(QMainWindow, self).eventFilter(source, event)

    # def resizeEvent(self, e):
    #     pass
    # Log.warn(self.table_timeline.width())
    # super(MyApp, self).resizeEvent(e)

    def slot_eval(self):
        cont = self.ptext_eval_in.toPlainText()  # type:QPlainTextEdit
        Log.info(cont)
        try:
            resp = eval(cont)
        except Exception as e:
            resp = e.__str__()
        self.textb_eval_out.setText(str(resp))

    # def slot_new_label_temp(self):
    #     Log.debug('here')
    #     global_.mySignals.action_add.emit(global_.Emitter.T_TEMP)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
