from enum import Enum

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from utils import *


class MySignals(QObject):
    jump_to = pyqtSignal(int, int, Enum)  # index,bias,emitter
    follow_to = pyqtSignal(Enum, int)  # emitter,index
    video_pause_or_resume = pyqtSignal()
    video_pause = pyqtSignal()
    video_start = pyqtSignal(int)  # stopAt

    timer_video = QTimer()

    @classmethod
    def timer_start(cls, Tms=50):
        cls.timer_video.start(Tms)

    def slot_toTest(self):
        Log.info('here')


class Settings:
    pass
    v_interval = None


class Emitter(Enum):
    TIMER = 1
    T_HHEADER = 2
    T_HSCROLL = 3
    T_WHEEL = 4
    T_LABEL = 5
    Line_JUMPTO = 6


mySignals = MySignals()
