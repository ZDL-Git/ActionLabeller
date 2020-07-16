import sys
import collections
import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("qt_gui/mainwindow.ui")


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        for i in range(20):
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem("jab"))
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, i)
            self.tableWidget.setItem(rowPosition, 1, item)
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, i + 7)
            self.tableWidget.setItem(rowPosition, 2, item)

        for i in range(38):
            self.table_timeline.setColumnCount(self.table_timeline.horizontalHeader().count() + 1)

            if i > 9:
                continue
            rowPosition = self.table_timeline.rowCount()
            self.table_timeline.insertRow(rowPosition)
            self.table_timeline.setItem(rowPosition, 0, QTableWidgetItem(None))
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, None)
            self.table_timeline.setItem(rowPosition, 1, item)
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, None)
            self.table_timeline.setItem(rowPosition, 2, item)

        vheader = self.table_timeline.verticalHeader()
        vheader.setDefaultSectionSize(5)
        vheader.sectionResizeMode(QHeaderView.Fixed)

        # header = self.tableWidget.horizontalHeader()
        # header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # self.line_interval.addItems(['1', '2', '3', '1.25', '1.5', '1.75'])
        # self.line_interval.setCurrentIndex(2)
        self.combo_speed.addItems(['0.5', '0.75', '1', '1.25', '1.5', '1.75'])
        self.combo_speed.setCurrentIndex(2)

        self.combo_sortby.addItems(['timestamp', 'filename'])
        self.combo_sortby.setCurrentIndex(1)

        self.video_obj = None
        self.cap = cv2.VideoCapture('resources/388.mp4')
        self.timer_video = QTimer()
        self.timer_video.timeout.connect(self.flush_frame)
        self.timer_video.start(50)

        self.cur_index = 0

        self.prettify()

        self.spin_interval.textChanged.connect(self.set_interval)
        self.line_jumpto.textChanged.connect(self.jump_to)
        # self.label_timeline.installEventFilter(self)
        self.label_show.installEventFilter(self)
        self.table_timeline.installEventFilter(self)

        self.v_buffer = collections.deque(maxlen=100)

        self.state_mouse_pressing = False
        self.state_mouse_last_point = None

        def init_buttons():
            self.btn_play.clicked.connect(self.pause_or_resume)
            self.btn_to_head.clicked.connect(self.to_head)
            self.btn_to_tail.clicked.connect(self.to_tail)

        def init_settings():
            self.setting_v_interval = int(self.spin_interval.text())

        def init_table():
            self.table_timeline.cellPressed.connect(self.pause)
            self.table_timeline.itemSelectionChanged.connect(self.common_slot)
            # self.table_timeline.view().horizontalScrollBar().
            # self.table_timeline.currentCellChanged.connect(self.common_slot)

        init_table()
        init_buttons()
        init_settings()

    def common_slot(self):
        print(f'common slot print')

    def to_head(self):
        self.cur_index = 0

    def to_tail(self):
        self.cur_index = 11111

    def set_interval(self):
        self.setting_v_interval = int(self.spin_interval.text() or 1)

    def pause_or_resume(self):
        if self.timer_video.isActive():
            self.pause()
        else:
            self.start()

    def pause(self):
        self.timer_video.stop()
        self.btn_play.setText('Play')

    def start(self):
        self.timer_video.start()
        self.btn_play.setText('Pause')

    def jump_to(self, to=None):
        to = to or self.line_jumpto.text()
        if to:
            to = int(to)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, to)
            self.cur_index = to
            self.flush_frame()

    def eventFilter(self, source, event):
        if event.type() != 12:
            print(f'event type {event.type()} source {source}')
        else:
            return False
        if source is self.label_timeline:
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
        elif source is self.label_show:
            if event.type() == QEvent.MouseButtonPress:
                self.pause_or_resume()
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

    def flush_frame(self, reverse=False):
        """ Slot function to capture frame and process it
        """

        def switch_to_specific_frame(i):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)

        if self.setting_v_interval < 80 and 1:
            pass
        ret, frame = self.cap.read()
        self.cur_index += 1

        if ret and self.cur_index % self.setting_v_interval == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, bytesPerComponent = frame.shape
            bytesPerLine = bytesPerComponent * width
            q_image = QImage(frame.data, width, height, bytesPerLine,
                             QImage.Format_RGB888).scaled(self.label_show.width(), self.label_show.height(),
                                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
            q_pixmap = QPixmap.fromImage(q_image)
            self.v_buffer.append((q_pixmap, self.cur_index))
            self.label_show.setPixmap(q_pixmap)
            self.label_timeline.setText(f'frame:{self.cur_index}')
        elif not ret:
            self.cap.release()
            self.timer_video.stop()
            # self.statusBar.showMessage('播放结束！')
        else:
            self.flush_frame()

    def prettify(self):
        shadowEffect = QGraphicsDropShadowEffect()

        shadowEffect.setColor(QColor(0, 0, 0, 255 * 0.9))
        shadowEffect.setOffset(0)
        shadowEffect.setBlurRadius(15)
        self.label_show.setGraphicsEffect(shadowEffect)
        self.label_timeline.setGraphicsEffect(shadowEffect)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()

    # pixmap = QPixmap('resources/388.mp4')
    # pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # window.label_show.setPixmap(pixmap)
    print(window.label_show.size())
    sys.exit(app.exec_())
