from common.utils import Log


class CommonUnit:
    get_default_action = lambda: (_ for _ in ()).throw(
        NotImplementedError('Please register CommonUnit.get_default_action!'))
    get_all_actions = lambda: (_ for _ in ()).throw(
        NotImplementedError('Please register CommonUnit.get_all_actions!'))
    status_prompt = lambda *args: Log.warn(
        'The status_prompt not implemented, please override CommonUnit.status_prompt!')
    get_all_labels = lambda: (_ for _ in ()).throw(
        NotImplementedError('Please register CommonUnit.get_all_labels!'))

    def __init__(self, mwindow):
        Log.debug('')
        self.mw = mwindow

        self.__class__.get_default_action = self.mw.table_action.get_default_action
        self.__class__.get_all_actions = self.mw.table_action.get_all_actions
        self.__class__.status_prompt = self.mw.label_note.setText
        self.__class__.get_all_labels = self.mw.table_labeled.get_all_labels
