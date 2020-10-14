from abc import ABCMeta, abstractmethod, ABC
from collections import namedtuple
from enum import Enum
from typing import NamedTuple

from PyQt5.QtCore import QItemSelection, QItemSelectionModel, QModelIndex, Qt
from PyQt5.QtGui import QIntValidator, QBrush, QColor
from PyQt5.QtWidgets import QTableView, QItemDelegate, QWidget, QStyleOptionViewItem, QLineEdit, QTableWidgetItem
from zdl.utils.helper.python import except_as_None


class TableViewExtended(QTableView):
    def _delete_rows(self: QTableView, rows):
        for r_d in sorted(rows, reverse=True):
            self.model().removeRow(r_d)

    def _select_row(self: QTableView, row):
        self.selectRow(row)

    def _delete_selected_rows(self):
        rows = set()
        for index in self.selectedIndexes():
            rows.add(index.row())
        for r in sorted(rows, reverse=True):
            self.removeRow(r)

    def unselect_all(self: QTableView):
        rowc = self.model().rowCount()
        colc = self.model().columnCount()
        if rowc > 0 and colc > 0:
            self.selectionModel().select(
                QItemSelection(self.model().index(0, 0),
                               self.model().index(rowc - 1, colc - 1)),
                QItemSelectionModel.Clear)

    class IntDelegate(QItemDelegate):
        def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
            line_edit = QLineEdit(parent)
            validator = QIntValidator(line_edit)
            line_edit.setValidator(validator)
            return line_edit


class EnumColsHelper(Enum):
    # _attrs = namedtuple('attrs', ['index', 'value_type', 'header', 'editable', 'num_sort', 'show'])
    # can not use any class var as this _attrs, cause:
    #     TypeError: Cannot extend enumerations
    @classmethod
    def Col(cls):
        if not hasattr(cls, 'col_info_namedtuple'):
            cls.col_info_namedtuple = namedtuple('Col_namedtuple',
                                                 ['index', 'value_type', 'header', 'editable', 'num_sort', 'show'])
        return cls.col_info_namedtuple

    @classmethod
    def headers(cls):
        # using isinstance(v.value, cls.Col()) to get rid of cls.col_info_namedtuple
        return [str(v.value.header) for k, v in cls.__members__.items() if isinstance(v.value, cls.Col())]

    @classmethod
    def hidden_cols(cls):
        return [v.value.index for k, v in cls.__members__.items() if
                isinstance(v.value, cls.Col()) and not v.value.show]

    @classmethod
    def to_table(cls, table: QTableView):
        col_headers = cls.headers()
        table.setColumnCount(len(col_headers))
        table.setHorizontalHeaderLabels(col_headers)
        for i in cls.hidden_cols():
            table.setColumnHidden(i, True)


class RowHelper(ABC):
    def __init__(self, table: TableViewExtended):
        self.table = table

    def _col_item(self, col: EnumColsHelper):
        r, c, e = self.row_num, col.value.index, col.value.editable
        if self.table.item(r, c) is None:
            item = QTableWidgetItem()
            if not e:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(r, c, item)
        return self.table.item(r, c)

    @except_as_None()
    def _col_value(self, col: EnumColsHelper):
        vt = col.value.value_type
        if vt in [QBrush, QColor]:
            v = self._col_item(col).background()
        elif vt in [bool]:
            v = self._col_item(col).checkState() == Qt.Checked
        else:
            v = vt(self._col_item(col).text())
        return v

    def _set_col_value(self, value, col: EnumColsHelper):
        vt = col.value.value_type
        if vt in [QBrush, QColor]:
            self._col_item(col).setBackground(value)
        elif vt in [bool]:
            self._col_item(col).setCheckState(Qt.Checked if value else Qt.Unchecked)
        elif col.value.num_sort:
            self._col_item(col).setData(Qt.DisplayRole, value)
        else:
            self._col_item(col).setText(str(value))
        return self

    @abstractmethod
    def _insert(self):
        pass

    def delete(self):
        self.table._delete_rows([self.row_num])
