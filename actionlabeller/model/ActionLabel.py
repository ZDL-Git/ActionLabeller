from typing import Optional

from PyQt5.QtGui import QBrush
from zdl.utils.helper.python import BResult
from zdl.utils.io.log import logger


class ActionLabel:
    def __init__(self, action: str, action_id: int, color, begin: int, end: int,
                 timeline_row: Optional[int],
                 pose_index: int = -1):
        self.action = action
        self.action_id = action_id
        if isinstance(color, QBrush):
            color = color.color()
        self.color = color
        self.begin = begin
        self.end = end
        try:
            self.duration = self.end - self.begin + 1
        except TypeError:
            self.duration = None
        self.pose_index = pose_index  # pose index from 0, within one frame.
        self.timeline_row = timeline_row

    def merge(self, label_section):
        if self.action != label_section.action:
            logger.error('different actions:')
            logger.error(self)
            logger.error(label_section)
        elif self.begin <= label_section.begin <= self.end or self.begin <= label_section.end <= self.end:
            self.begin = min(self.begin, label_section.begin)
            self.end = max(self.end, label_section.end)
        else:
            logger.error('actions not continuous')

    def is_valid(self, checklist: list) -> BResult:
        logger.debug(self)
        for attr in checklist:
            value = eval(f'self.{attr}')
            if value in [None, '', []]:
                warn_ = f"Label's attr {attr}={value}, invalid."
                logger.warn(warn_)
                return BResult(False, warn_)
        if self.begin is not None and self.end is not None and self.begin > self.end:
            warn_ = f"Label's begin[{self.begin}] exceeds end[{self.end}], invalid."
            logger.warn(warn_)
            return BResult(False, warn_)
        return BResult(True)

    def __repr__(self):
        return f"{self.__class__.__name__}: " \
               f"action[{self.action}] " \
               f"action_id[{self.action_id}] " \
               f"color[{self.color.getRgb()}] " \
               f"begin[{self.begin}] end[{self.end}] " \
               f"pose_index[{self.pose_index}] " \
               f"timeline_row[{self.timeline_row}]"
