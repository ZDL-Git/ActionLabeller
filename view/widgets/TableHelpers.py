from abc import abstractmethod, ABC
from collections import namedtuple
from enum import Enum

from PyQt5.QtCore import QItemSelection, QItemSelectionModel, QModelIndex, Qt
from PyQt5.QtGui import QIntValidator, QBrush, QColor
from PyQt5.QtWidgets import QTableView, QItemDelegate, QWidget, QStyleOptionViewItem, QLineEdit, QTableWidgetItem, \
    QTableWidget
from zdl.utils.helper.python import except_as_None
from zdl.utils.io.log import logger


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
    def ColType(cls):
        if not hasattr(cls, 'col_info_namedtuple'):
            cls.col_info_namedtuple = namedtuple('Col_namedtuple',
                                                 ['index', 'value_type', 'header',
                                                  'editable', 'selectable', 'num_sort',
                                                  'show'])
        return cls.col_info_namedtuple

    @classmethod
    def values(cls):
        return [m.value for m in cls.members()]

    @classmethod
    def members(cls):
        return [v for v in cls.__members__.values() if isinstance(v.value, cls.ColType())]

    @classmethod
    def col_index_to_col(cls, c: int) -> 'EnumColsHelper':
        return list(filter(lambda m: m.value.index == c, cls.members()))[0]

    @classmethod
    def headers(cls):
        return [str(v.header) for v in cls.values()]

    @classmethod
    def hidden_cols(cls):
        return [v.index for v in cls.values() if not v.show]

    @classmethod
    def to_table(cls, table: QTableView):
        col_headers = cls.headers()
        table.setColumnCount(len(col_headers))
        table.setHorizontalHeaderLabels(col_headers)
        for i in cls.hidden_cols():
            table.setColumnHidden(i, True)


class RowHelper(ABC):
    def __init__(self, table: QTableWidget, row_num: int):
        self.table = table
        self.row_num = row_num

    def __repr__(self):
        return f'{self.__class__}: row_num={self.row_num}'

    def __col_item(self, col: EnumColsHelper):
        r, c, e, s = self.row_num, col.value.index, col.value.editable, col.value.selectable
        if self.table.item(r, c) is None:
            item = QTableWidgetItem()
            if not e:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            if not s:
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.table.setItem(r, c, item)
        return self.table.item(r, c)

    @except_as_None()
    def _col_value(self, col: EnumColsHelper):
        vt = col.value.value_type
        if vt in [QBrush, QColor]:
            v = self.__col_item(col).background()
        elif vt in [bool]:
            v = self.__col_item(col).checkState() == Qt.Checked
        else:
            v = vt(self.__col_item(col).text())
        return v

    def _set_col_value(self, value, col: EnumColsHelper):
        vt = col.value.value_type
        if vt in [QBrush, QColor]:
            self.__col_item(col).setBackground(value)
        elif vt in [bool]:
            self.__col_item(col).setCheckState(Qt.Checked if value else Qt.Unchecked)
        elif col.value.num_sort:
            self.__col_item(col).setData(Qt.DisplayRole, value)
        else:
            self.__col_item(col).setText(str(value))
        return self

    def _col_del(self, col: EnumColsHelper):
        pass

    @abstractmethod
    def _insert(self):
        pass

    def delete(self):
        self.table._delete_rows([self.row_num])

    def to_edit(self, col: EnumColsHelper):
        self.table.editItem(self.__col_item(col))
