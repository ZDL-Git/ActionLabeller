from functools import partial
from typing import List, Dict

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QColor
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem
from zdl.utils.io.log import logger

from model.Action import Action
from model.ActionLabel import ActionLabel
from presenter import MySignals
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from view.widgets.Common import TableDecorators
from view.widgets.TableViewExtended import TableViewExtended


class LabeledTableWidget(QTableWidget, TableViewExtended):
    def __init__(self, parent):
        super().__init__()

        self.RowLabel = partial(self._Row, table=self)

        self.cellDoubleClicked.connect(self.slot_cellDoubleClicked)
        self.itemSelectionChanged.connect(self.slot_itemSelectionChanged)
        # self.cellChanged.connect(self.slot_cellChanged)

    def __init_later__(self):
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(self._Row.COLS)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setColumnHidden(3, True)
        self.setColumnHidden(4, True)
        self.setColumnHidden(5, True)
        self.setColumnHidden(6, False)

    # def slot_cellChanged(self, r, c):
    #     Log.debug(r, c)

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        if self.state() == QtGui.QAbstractItemView.EditingState:
            return

        logger.debug(e.key())
        if e.key() in [Qt.Key_Backspace, Qt.Key_D]:
            rows, labels = self._labels_selected()
            mySignals.labeled_delete.emit(labels, MySignals.Emitter.T_LABELED)
            self._delete_rows(rows)

    def slot_itemSelectionChanged(self):
        logger.debug('here')

    def slot_cellDoubleClicked(self, r, c):
        logger.debug(f'{r}, {c}')
        label = self.label_at(r)
        mySignals.labeled_selected.emit(label, MySignals.Emitter.T_LABELED)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_created(self, action_label: ActionLabel, emitter):
        logger.debug(f'{action_label}, {emitter}')
        self._label_cells_delete({action_label.timeline_row: list(range(action_label.begin, action_label.end + 1))})
        row_i = self.add_label(action_label)
        self._select_row(row_i)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_select(self, action_label, emitter):
        logger.debug(f'{action_label}, {emitter}')
        label_row = self._get_label_row_num(action_label)
        if label_row is not None:
            self.selectRow(label_row)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_delete(self, action_label, emitter):
        logger.debug(f'{action_label}, {emitter}')
        row_i = self._get_label_row_num(action_label)
        if row_i is not None:
            self._delete_rows([row_i])

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_cells_delete(self, label_cells: Dict[int, List[int]], emitter):
        logger.debug(f'{label_cells}, {emitter}')
        self._label_cells_delete(label_cells)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_action_info_update_by_row(self, r, action: Action, emitter):
        logger.debug(f'{r}, {action}, {emitter}')
        self.RowLabel(r).set_action(action.name).set_action_color(action.color)

    def get_all_labels(self) -> list:
        labels = []
        for r in range(self.rowCount()):
            labels.append(self.label_at(r))
        labels.sort(key=lambda l: l.begin)
        return labels

    def label_at(self, r) -> ActionLabel:
        label = self.RowLabel(r).to_actionlabel()
        logger.debug(label)
        return label

    def _labels_selected(self) -> (set, List[ActionLabel]):
        rows = set()
        for index in self.selectedIndexes():
            rows.add(index.row())
        labels = []
        for r in rows:
            labels.append(self.label_at(r))
        return rows, labels

    def _get_label_row_num(self, action_label: ActionLabel):
        for r in range(self.rowCount()):
            row_label = self.RowLabel(r)
            if row_label.begin == action_label.begin \
                    and row_label.end == action_label.end \
                    and row_label.timeline_row == action_label.timeline_row:
                return r
        return None

    def add_label(self, action_label: ActionLabel):
        action = QTableWidgetItem(action_label.action)
        action.setFlags(action.flags() & ~Qt.ItemIsEditable)
        begin = QTableWidgetItem()
        begin.setFlags(begin.flags() & ~Qt.ItemIsEditable)
        begin.setData(Qt.DisplayRole, action_label.begin)
        end = QTableWidgetItem()
        end.setFlags(end.flags() & ~Qt.ItemIsEditable)
        end.setData(Qt.DisplayRole, action_label.end)
        pose_index = QTableWidgetItem()
        pose_index.setData(Qt.DisplayRole, action_label.pose_index)
        timeline_row = QTableWidgetItem(str(action_label.timeline_row))
        action_id = QTableWidgetItem(str(action_label.action_id))
        action_color = QTableWidgetItem()
        action_color.setBackground(action_label.color)
        # timeline_row.setData(Qt.DisplayRole, action_label.timeline_row)
        new_row_i = self.rowCount()
        self.insertRow(new_row_i)
        self.setItem(new_row_i, 0, action)
        self.setItem(new_row_i, 1, begin)
        self.setItem(new_row_i, 2, end)
        self.setItem(new_row_i, 3, timeline_row)
        self.setItem(new_row_i, 4, action_id)
        self.setItem(new_row_i, 5, action_color)
        self.setItem(new_row_i, 6, pose_index)
        return new_row_i

    def _label_cells_delete(self, label_cells: Dict[int, List[int]]):
        for k in label_cells:
            label_cells[k].sort()
        rows_delete_later = set()
        labels_add_later = []
        for t_r in range(self.rowCount()):
            row_label: LabeledTableWidget._Row = self.RowLabel(t_r)
            if row_label.timeline_row not in label_cells:
                continue
            left_cell = label_cells[row_label.timeline_row][0]
            right_cell = label_cells[row_label.timeline_row][-1]
            if left_cell > row_label.end or right_cell < row_label.begin:
                continue
            elif left_cell <= row_label.begin:
                row_label.set_begin(right_cell + 1)
            elif right_cell >= row_label.end:
                row_label.set_end(left_cell - 1)
            else:
                new_label = row_label.to_actionlabel()
                new_label.begin = right_cell + 1
                labels_add_later.append(new_label)
                row_label.set_end(left_cell - 1)

            if row_label.begin > row_label.end:
                rows_delete_later.add(t_r)

        self._delete_rows(rows_delete_later)

        for l_add in labels_add_later:
            self.add_label(l_add)

    class _Row:
        COLS = ['Action', 'Begin', 'End', 'Timeline Row', 'Action Id', 'Action Color', 'Pose Index']

        def __init__(self, row_num: int, table: 'LabeledTableWidget'):
            self.table = table
            self.row_num = row_num

        @property
        def action(self):
            return self.table.item(self.row_num, 0).text()

        def set_action(self, action: str):
            self.table.item(self.row_num, 0).setText(action)
            return self

        @property
        def begin(self):
            text = self.table.item(self.row_num, 1).text()
            return text and int(text)

        def set_begin(self, begin_: int):
            self.table.item(self.row_num, 1).setText(str(begin_))
            return self

        @property
        def end(self):
            text = self.table.item(self.row_num, 2).text()
            return text and int(text)

        def set_end(self, end_: int):
            self.table.item(self.row_num, 2).setText(str(end_))
            return self

        @property
        def timeline_row(self):
            text = self.table.item(self.row_num, 3).text()
            return text and int(text)

        def set_timeline_row(self, row_num: int):
            self.table.item(self.row_num, 3).setText(str(row_num))
            return self

        @property
        def action_id(self):
            text = self.table.item(self.row_num, 4).text()
            return text and int(text)

        def set_action_id(self, id_: int):
            self.table.item(self.row_num, 4).setText(str(id_))
            return self

        @property
        def action_color(self):
            return self.table.item(self.row_num, 5).background()

        def set_action_color(self, color: QColor):
            self.table.item(self.row_num, 5).setBackground(color)
            return self

        @property
        def pose_index(self):
            text = self.table.item(self.row_num, 6).text()
            return text and int(text)

        def set_pose_index(self, index: int):
            self.table.item(self.row_num, 6).setText(str(index))
            return self

        def delete(self):
            self.table._delete_rows([self.row_num])

        def to_actionlabel(self) -> ActionLabel:
            label = ActionLabel(self.action,
                                self.action_id,
                                self.action_color,
                                self.begin,
                                self.end,
                                self.timeline_row,
                                self.pose_index)
            return label
