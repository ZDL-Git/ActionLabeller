from PyQt5.QtWidgets import QFileDialog

from common.utils import Log


class CommonUnit:
    @classmethod
    def set_mw(cls, mwindow):
        Log.debug('')
        cls.mw = mwindow

        cls.get_default_action = cls.mw.table_action.get_default_action
        cls.get_all_actions = cls.mw.table_action.get_all_actions
        cls.status_prompt = cls.mw.label_note.setText
        cls.get_all_labels = cls.mw.table_labeled.get_all_labels

    @classmethod
    def get_save_name(cls, default=None):
        name = QFileDialog().getSaveFileName(cls.mw, 'Save File', default)
        return name[0]
