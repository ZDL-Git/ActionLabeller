from enum import Enum

from PyQt5.QtCore import pyqtSignal, QObject, QTimer

from model.action_label import ActionLabel


class MySignals(QObject):
    schedule = pyqtSignal(int, int, int, Enum)  # jumpTo,bias,stopAt,emitter
    follow_to = pyqtSignal(Enum, int)  # emitter,index
    video_pause_or_resume = pyqtSignal()
    video_pause = pyqtSignal()
    video_start = pyqtSignal()

    label_selected = pyqtSignal(ActionLabel, Enum)
    label_created = pyqtSignal(ActionLabel, Enum)
    label_delete = pyqtSignal(ActionLabel, Enum)
    label_cells_delete = pyqtSignal(dict, Enum)
    labeled_selected = pyqtSignal(ActionLabel, Enum)
    labeled_update = pyqtSignal(list, Enum)
    labeled_delete = pyqtSignal(list, Enum)
    action_update = pyqtSignal(Enum)

    timer_video = QTimer()

    @classmethod
    def timer_start(cls, Tms=50):
        cls.timer_video.start(Tms)


mySignals = MySignals()  # attribute pyqtSignal needs class to be instantiated, and inherit QObject
