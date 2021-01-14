from enum import Enum

from PyQt5.QtCore import pyqtSignal, QObject

from actionlabeller.model.ActionLabel import ActionLabel

__all__ = ['Emitter', 'mySignals']


class MySignals(QObject):
    schedule = pyqtSignal(int, int, int, Enum)  # jumpTo,bias,stopAt,emitter

    label_selected = pyqtSignal(ActionLabel, Enum)
    label_created = pyqtSignal(ActionLabel, Enum)
    label_cells_delete = pyqtSignal(dict, Enum)
    labeled_delete = pyqtSignal(list, Enum)


class Emitter(Enum):
    TIMER = 1
    T_HHEADER = 2
    T_HSCROLL = 3
    T_WHEEL = 4
    T_LABEL = 5
    T_LABELED = 6
    T_ACTION = 7
    T_TEMP = 8
    V_PLAYER = 9
    INPUT_JUMPTO = 10
    BTN = 11


mySignals = MySignals()  # attribute pyqtSignal needs class to be instantiated, and inherit QObject
