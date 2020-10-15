from PyQt5.QtGui import *


class Action:
    def __init__(self, id: int, name: str, color, default: bool, xml_ymin: int = None, xml_ymax: int = None):
        self.id = id
        self.name = name
        if isinstance(color, QBrush):
            color = color.color()
        self.color = color
        self.default = default
        self.xml_ymin = xml_ymin
        self.xml_ymax = xml_ymax

    def __repr__(self):
        return f"{self.__class__.__name__}: " \
               f"id={self.id} " \
               f"name={self.name} " \
               f"color={self.color.getRgb()} " \
               f"default={self.default}"
