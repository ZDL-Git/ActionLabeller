from utils import Log


class ActionLabel:
    def __init__(self, action, begin, end, timeline_row):
        self.action = action
        self.begin = begin
        self.end = end
        self.timeline_row = timeline_row

    def merge(self, label_section):
        if self.action != label_section.action:
            Log.error('different actions:', self, label_section)
        elif self.begin <= label_section.begin <= self.end or self.begin <= label_section.end <= self.end:
            self.begin = min(self.begin, label_section.begin)
            self.end = max(self.end, label_section.end)
        else:
            Log.error('actions not continuous')

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.action} {self.begin} {self.end} {self.timeline_row}"
