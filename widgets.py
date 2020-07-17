import collections
from random import random

import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import global_
from utils import *


class MyTableWidget(QTableWidget):

    def __init__(self, parent):
        QTableWidget.__init__(self)

        self.key_control_pressed = False
        self.entry_row_index = None
        self.cellClicked.connect(self.slot_cellClicked)
        self.cellActivated.connect(self.slot_cellActivated)
        self.itemSelectionChanged.connect(self.slot_itemSelectionChanged)
        self.cellPressed.connect(self.slot_cellPressed)
        global_.mySignals.jump_to.connect(self.slot_jump_to)

        self.setHorizontalHeaderLabels([str(i) for i in range(50)])

    # FIXME
    def __init_later__(self):
        header = self.horizontalHeader()
        header.sectionPressed.disconnect()
        header.sectionClicked.connect(self.slot_horizontalHeaderClicked)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        print(f'mytable {e} {e.key()} {e.type()}')
        if e.key() == Qt.Key_Control:
            self.key_control_pressed = True
        # elif e.key() == Qt.Key_Control:
        #     pass

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Control:
            print('released')
            self.key_control_pressed = False

    def wheelEvent(self, e: QWheelEvent) -> None:
        print(f'wheel{e.angleDelta()}')
        idler_forward = e.angleDelta().y() > 0
        if self.key_control_pressed:
            col_width = self.columnWidth(0)
            col_width += 3 if idler_forward else -3
            t_width = self.width()  # no vertical header, so
            cols = self.horizontalHeader().count()
            per_col_width = max(col_width, int(t_width / cols))
            self.horizontalHeader().setDefaultSectionSize(per_col_width)
        else:
            scrollbar = self.horizontalScrollBar()
            pos = scrollbar.value()
            pos += 2 if idler_forward else -2
            scrollbar.setValue(pos)

    def slot_cellClicked(self, r, c):
        print(f'uuuuuuu {r} {c}')
        # if self.item(r, c) and self.item(r, c).background() is not Qt.white:
        #     self.item(r, c).setBackground(Qt.white)
        # elif self.item(r, c - 1) and self.item(r, c - 1).background() is not Qt.white:
        #     self.setItem(r, c, QTableWidgetItem(''))
        #     self.item(r, c).setBackground(self.item(r, c - 1).background())
        # else:
        #     self.setItem(r, c, QTableWidgetItem(''))
        #     self.item(r, c).setBackground(QColor(QRandomGenerator().global_().generate()))

    def slot_cellActivated(self, r, c):
        pass

    def slot_itemSelectionChanged(self):
        Log.info('here')
        rect = self.selectedRanges() and self.selectedRanges()[0]
        if rect:
            l, r, t, b = rect.leftColumn(), rect.rightColumn(), rect.topRow(), rect.bottomRow()
            Log.debug('l r t b', l, r, t, b)
            if l != r or t != b:
                r_color = QColor(QRandomGenerator().global_().generate())
                for c in range(l, r + 1):
                    self.setItem(t, c, QTableWidgetItem(''))
                    self.item(t, c).setBackground(r_color)

    def slot_cellPressed(self, r, c):
        Log.info('here', self.item(r, c))
        if not self.item(r, c):
            self.setItem(r, c, QTableWidgetItem(''))
            # self.item(r, c).setBackground(Qt.white)
            # self.item(r, c).setText('10')
        if self.item(r, c).background().color() is not QColor(Qt.white):
            Log.debug('clear color')
            self.item(r, c).setBackground(Qt.white)
        elif self.item(r, c - 1) and self.item(r, c - 1).background() is not Qt.white:
            Log.debug('follow left neighbour color')
            self.item(r, c).setBackground(self.item(r, c - 1).background())
        else:
            Log.debug('fill random color')
            self.item(r, c).setBackground(QColor(QRandomGenerator().global_().generate()))

    def slot_horizontalHeaderClicked(self, i):
        Log.info('index', i)
        global_.mySignals.jump_to.emit(i)

    def slot_jump_to(self, index):
        Log.info(index, self.horizontalHeaderItem(index))
        # self.scrollToItem(self.horizontalHeaderItem(index))
        bias = self.width() / 2 / self.columnWidth(0) - 1
        self.horizontalScrollBar().setSliderPosition(max(0, index - bias))

    def set_column_count(self, c):
        self.setColumnCount(c)
        # self.setHorizontalHeaderLabels([str(i) for i in range(c)])

    # def headerData(self, col, orientation, role):
    #     Log.warn('here')
    #     if orientation == Qt.Horizontal and role == Qt.DisplayRole:
    #         return col - 1
    #     return QVariant()


class MyVideoLabelWidget(QLabel):

    def __init__(self, parent):
        QLabel.__init__(self)
        self.key_control_pressed = False
        self.entry_row_index = None
        self.video_obj = None
        self.video_playing = False
        self.v_buffer = collections.deque(maxlen=100)

        # self.cellClicked.connect(self.slot_cellClicked)
        # self.cellActivated.connect(self.slot_cellActivated)
        # self.itemSelectionChanged.connect(self.slot_itemSelectionChanged)
        # self.cellPressed.connect(self.slot_cellPressed)
        global_.mySignals.jump_to.connect(self.slot_jump_to)
        global_.mySignals.timer_video.timeout.connect(self.flush_frame)

    def set_video(self, video):
        self.video_obj = video

    def slot_jump_to(self, index):
        Log.info('here')
        # self.flush_frame(index)
        self.video_obj.schedule_index = index

    def mousePressEvent(self, e):
        self.pause_or_resume()

    def pause_or_resume(self):
        if self.video_playing:
            self.pause()
        else:
            self.start()

    def pause(self):
        # self.timer_video.stop()
        self.video_playing = False

    def start(self):
        # self.timer_video.start()
        if not self.video_obj:
            return
        self.video_playing = True

    def flush_frame(self):
        Log.debug('here')
        if not self.video_playing and self.video_obj.schedule_index is None:
            return

        frame = self.video_obj.read()
        if frame is None:
            self.video_playing = False
            return
        height, width, bytesPerComponent = frame.shape
        bytesPerLine = bytesPerComponent * width
        q_image = QImage(frame.data, width, height, bytesPerLine,
                         QImage.Format_RGB888).scaled(self.width(), self.height(),
                                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        q_pixmap = QPixmap.fromImage(q_image)
        self.v_buffer.append((q_pixmap, self.video_obj.cur_index))
        self.setPixmap(q_pixmap)
        # self.label_timeline.setText(f'frame:{self.cur_index}')

        # elif not ret:
        #     self.cap.release()
        #     # self.timer_video.stop()
        #     # self.statusBar.showMessage('播放结束！')
        # else:
        #     self.flush_frame()
