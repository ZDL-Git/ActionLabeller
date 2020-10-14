from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableView, QHeaderView

from view.widgets.ActionTableWidget import ActionTableWidget
from view.widgets.TableHelpers import TableViewExtended, EnumColsHelper


class XmlSettingTableView(QTableView):
    def __init__(self, parent):
        super().__init__()

    def __init_later__(self, model):
        self.setModel(model)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        delegate = TableViewExtended.IntDelegate()
        self.setItemDelegateForColumn(ActionTableWidget.Cols.xml_ymin.value.index, delegate)
        self.setItemDelegateForColumn(ActionTableWidget.Cols.xml_ymax.value.index, delegate)
        for col in ActionTableWidget.Cols:
            if col in [ActionTableWidget.Cols.name, ActionTableWidget.Cols.xml_ymin,
                       ActionTableWidget.Cols.xml_ymax]:
                self.setColumnHidden(col.value.index, False)
            else:
                self.setColumnHidden(col.value.index, True)
