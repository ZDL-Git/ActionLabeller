from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from utils import *


class MySignals(QObject):
    jump_to = pyqtSignal(int)
    video_pause = pyqtSignal()
    video_start = pyqtSignal()

    timer_video = QTimer()

    @classmethod
    def timer_start(cls, Tms=50):
        cls.timer_video.start(Tms)

    def slot_toTest(self):
        Log.info('here')


class Settings:
    pass
    v_interval = None

mySignals = MySignals()
