from PyQt5.QtWidgets import QTableView, QHeaderView

from view.widgets.TableViewCommon import TableViewCommon


class XmlSettingTableView(QTableView):
    def __init__(self, parent):
        super().__init__()

    def __init_later__(self, model):
        self.setModel(model)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)
        self.setColumnHidden(4, False)
        self.setColumnHidden(5, False)
        delegate = TableViewCommon.IntDelegate()
        self.setItemDelegateForColumn(4, delegate)
        self.setItemDelegateForColumn(5, delegate)
