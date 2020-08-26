from common.utils import Log


class ApplicationUnit:

    def __init__(self, mwindow):
        Log.debug('')
        self.mw = mwindow

        (
            # self.mw.tool_box.currentChanged.connect(self.slot_toolbox_index_changed)
        )

    # def slot_toolbox_index_changed(self, index):
    #     Log.debug(index)
    #     if index in [0, 1]:
    #         self.mw.stacked_widget.setCurrentIndex(0)
    #     elif index == 2:
    #         self.mw.stacked_widget.setCurrentIndex(1)
