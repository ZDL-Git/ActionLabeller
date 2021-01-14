from PyQt5.QtWidgets import QLabel


class VideoLabelWidget(QLabel):

    def __init__(self, parent):
        super().__init__()

        # self.v_buffer = collections.deque(maxlen=100)

        # self.cellClicked.connect(self.slot_cellClicked)
        # self.cellActivated.connect(self.slot_cellActivated)
        # self.itemSelectionChanged.connect(self.slot_itemSelectionChanged)
        # self.cellPressed.connect(self.slot_cellPressed)
