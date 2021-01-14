from PyQt5.QtWidgets import QHeaderView

from actionlabeller.view.widgets.ActionTableWidget import ActionTableWidget
from actionlabeller.view.widgets.TableHelpers import TableViewExtended


class XmlSettingTableView(TableViewExtended):
    def __init__(self, parent):
        super().__init__()

    def __init_later__(self, model):
        self.setModel(model)
        # self.setSortingEnabled(True) # has set in ActionTableWidget, here will trigger reverse sorting.
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        delegate = TableViewExtended.IntItemDelegate()
        self.setItemDelegateForColumn(ActionTableWidget.Cols.xml_ymin.value.index, delegate)
        self.setItemDelegateForColumn(ActionTableWidget.Cols.xml_ymax.value.index, delegate)
        for col in ActionTableWidget.Cols:
            if col in [ActionTableWidget.Cols.name, ActionTableWidget.Cols.xml_ymin,
                       ActionTableWidget.Cols.xml_ymax]:
                self.setColumnHidden(col.value.index, False)
            else:
                self.setColumnHidden(col.value.index, True)
