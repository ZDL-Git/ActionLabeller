from PyQt5.QtCore import QItemSelection, QItemSelectionModel, QModelIndex
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QTableView, QItemDelegate, QWidget, QStyleOptionViewItem, QLineEdit


class TableViewCommon(QTableView):
    def _delete_rows(self: QTableView, rows):
        for r_d in sorted(rows, reverse=True):
            self.model().removeRow(r_d)

    def _select_row(self: QTableView, row):
        self.selectRow(row)

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
