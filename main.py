import sys
import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import global_
from video import Video
from utils import *

Ui_MainWindow, QtBaseClass = uic.loadUiType("qt_gui/mainwindow.ui")


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # self.table_timeline.set_column_count(1000)
        for i in range(20):
            rowPosition = self.table_labeled.rowCount()
            self.table_labeled.insertRow(rowPosition)
            self.table_labeled.setItem(rowPosition, 0, QTableWidgetItem("jab"))
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, i)
            self.table_labeled.setItem(rowPosition, 1, item)
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, i + 7)
            self.table_labeled.setItem(rowPosition, 2, item)

        # header = self.table_labeled.horizontalHeader()
        # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # self.line_interval.addItems(['1', '2', '3', '1.25', '1.5', '1.75'])
        # self.line_interval.setCurrentIndex(2)
        self.combo_speed.addItems(['0.5', '0.75', '1', '1.25', '1.5', '1.75'])
        self.combo_speed.setCurrentIndex(2)

        self.combo_sortby.addItems(['timestamp', 'filename'])
        self.combo_sortby.setCurrentIndex(1)

        # TODO
        # global_.mySignals.timer_video.timeout.connect(self.flush_frame)
        global_.mySignals.timer_start()

        self.cur_index = 0

        self.prettify()

        self.btn_open_video.clicked.connect(self.slot_open_file)
        self.spin_interval.textChanged.connect(self.set_interval)
        self.line_jumpto.textChanged.connect(
            lambda text: text and global_.mySignals.jump_to.emit(int(text), None, global_.Emitter.Line_JUMPTO))
        # self.label_note.installEventFilter(self)
        self.label_show.installEventFilter(self)

        self.state_mouse_pressing = False
        self.state_mouse_last_point = None

        # self.verticalLayout_7.setFocus()
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.btn_stop.click()

        def init_buttons():
            # self.btn_play.clicked.connect(self.pause_or_resume)
            self.btn_play.clicked.connect(global_.mySignals.video_pause_or_resume.emit)
            self.btn_to_head.clicked.connect(self.to_head)
            self.btn_to_tail.clicked.connect(self.to_tail)
            self.btn_test.clicked.connect(
                lambda: Log.error(self.table_timeline.width(), self.table_timeline.columnWidth(0),
                                  self.table_timeline._center_col(), global_.mySignals.timer_video.setInterval(10)))

        def init_settings():
            global_.Settings.v_interval = int(self.spin_interval.text())

        # def init_table():
        #     self.table_timeline.cellPressed.connect(self.pause)
        #     self.table_timeline.itemSelectionChanged.connect(self.common_slot)
        # self.table_timeline.view().horizontalScrollBar().
        # self.table_timeline.currentCellChanged.connect(self.common_slot)

        # init_table()
        init_buttons()
        init_settings()

        self.btn_open_video.setFocus()
        self.table_timeline.__init_later__()
        global_.mySignals.jump_to.connect(self.common_slot)
        global_.mySignals.follow_to.connect(self.slot_follow_to)

    def common_slot(self, *arg):
        print(f'common slot print:', arg)

    def slot_open_file(self):
        # TODO
        # got = QFileDialog.getOpenFileName(self, "Open Image", "/Users/zdl/Downloads/下载-视频",
        #                                   "Image Files (*.mp4 *.jpg *.bmp)")
        got = ['/Users/zdl/Downloads/下载-视频/金鞭溪-张家界.mp4']
        Log.info(got)
        fname = got[0]
        if fname:
            video = Video(fname)
            self.table_timeline.set_column_count(video.get_info()['frame_c'])
            self.label_show.set_video(video)
            self.btn_play.click()

    def to_head(self):
        self.cur_index = 0

    def to_tail(self):
        self.cur_index = 11111

    def set_interval(self):
        global_.Settings.v_interval = int(self.spin_interval.text() or 1)

    def slot_follow_to(self, emitter, to):
        # to = to or self.line_jumpto.text()
        # if to:
        #     to = int(to)
        #     self.cap.set(cv2.CAP_PROP_POS_FRAMES, to)
        #     self.cur_index = to
        #     self.flush_frame()
        self.label_note.setText(f'frame {to}')

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
        # if event.type() == QEvent.FocusIn and source is self.ledit_corteB:
        #     print("B")
        #     self.flag = 1

        # if event.type() == QEvent.
        return super(QMainWindow, self).eventFilter(source, event)

    # def resizeEvent(self, e):
    #     pass
    # Log.warn(self.table_timeline.width())
    # super(MyApp, self).resizeEvent(e)

    # def flush_frame(self, reverse=False):
    #     """ Slot function to capture frame and process it
    #     """
    #
    #     def switch_to_specific_frame(i):
    #         self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    #
    #     if self.setting_v_interval < 80 and 1:
    #         pass
    #     ret, frame = self.cap.read()
    #     self.cur_index += 1
    #
    #     if ret and self.cur_index % self.setting_v_interval == 0:
    #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         height, width, bytesPerComponent = frame.shape
    #         bytesPerLine = bytesPerComponent * width
    #         q_image = QImage(frame.data, width, height, bytesPerLine,
    #                          QImage.Format_RGB888).scaled(self.label_show.width(), self.label_show.height(),
    #                                                       Qt.KeepAspectRatio, Qt.SmoothTransformation)
    #         q_pixmap = QPixmap.fromImage(q_image)
    #         self.v_buffer.append((q_pixmap, self.cur_index))
    #         self.label_show.setPixmap(q_pixmap)
    #         self.label_note.setText(f'frame:{self.cur_index}')
    #     elif not ret:
    #         self.cap.release()
    #         # self.timer_video.stop()
    #         # self.statusBar.showMessage('播放结束！')
    #     else:
    #         self.flush_frame()

    def prettify(self):
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setColor(QColor(0, 0, 0, 255 * 0.9))
        shadowEffect.setOffset(0)
        shadowEffect.setBlurRadius(8)
        self.label_show.setGraphicsEffect(shadowEffect)
        self.label_note.setGraphicsEffect(shadowEffect)

        vheader = self.table_timeline.verticalHeader()
        vheader.setDefaultSectionSize(5)
        vheader.sectionResizeMode(QHeaderView.Fixed)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
