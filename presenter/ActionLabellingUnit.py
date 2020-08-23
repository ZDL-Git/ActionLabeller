from common.utils import Log
from presenter.MySignals import mySignals


class ActionLabellingUnit:
    def __init__(self, mwindow):
        Log.debug('')
        self.mw = mwindow

        (
            mySignals.follow_to.connect(self.mw.table_timeline.slot_follow_to),
            mySignals.labeled_selected.connect(self.mw.table_timeline.slot_label_play),
            mySignals.labeled_update.connect(self.mw.table_timeline.slot_label_update),
            mySignals.labeled_delete.connect(self.mw.table_timeline.slot_label_delete),
        )
        (
            mySignals.label_created.connect(self.mw.table_labeled.slot_label_created),
            mySignals.label_selected.connect(self.mw.table_labeled.slot_label_selected),
            mySignals.label_delete.connect(self.mw.table_labeled.slot_label_delete),
            mySignals.label_cells_delete.connect(self.mw.table_labeled.slot_label_cells_delete),
            mySignals.action_update.connect(self.mw.table_labeled.slot_action_update),
        )
