from functools import partial
from typing import List, Dict, Union

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QColor
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QAbstractItemView
from zdl.utils.decorator import except_as_None
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
        self.setColumnCount(8)
        self.setHorizontalHeaderLabels(self._Row.COLS)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setColumnHidden(4, True)
        self.setColumnHidden(6, True)
        self.setColumnHidden(7, True)

    # def slot_cellChanged(self, r, c):
    #     Log.debug(r, c)

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        if self.state() == QAbstractItemView.EditingState:
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
        # label = self.label_at(r)
        # mySignals.labeled_selected.emit(label, MySignals.Emitter.T_LABELED)

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
        return self.RowLabel(action_label).row_num

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
        COLS = ['Action', 'Begin', 'End', 'Duration', 'Timeline Row', 'Pose Index', 'Action Id', 'Action Color']

        def __init__(self, row_num_or_actionlabel: Union[int, ActionLabel], table: 'LabeledTableWidget'):
            self.table = table
            if isinstance(row_num_or_actionlabel, int):
                self.row_num = row_num_or_actionlabel
            elif isinstance(row_num_or_actionlabel, ActionLabel):
                self.row_num = self.table.rowCount()
                self._insert(row_num_or_actionlabel)
            else:
                raise TypeError

        @property
        @except_as_None()
        def action(self):
            return self.table.item(self.row_num, 0).text()

        def set_action(self, action_name: str):
            self._touch_item(0)
            self.table.item(self.row_num, 0).setText(action_name)
            return self

        @property
        @except_as_None()
        def begin(self):
            return int(self.table.item(self.row_num, 1).text())

        def set_begin(self, begin_: int):
            self._touch_item(1)
            self.table.item(self.row_num, 1).setData(Qt.DisplayRole, begin_)
            self._set_duration()
            return self

        @property
        @except_as_None()
        def end(self):
            return int(self.table.item(self.row_num, 2).text())

        def set_end(self, end_: int):
            self._touch_item(2)
            self.table.item(self.row_num, 2).setData(Qt.DisplayRole, end_)
            self._set_duration()
            return self

        @property
        @except_as_None()
        def duration(self):
            return int(self.table.item(self.row_num, 3).text())

        def _set_duration(self):
            self._touch_item(3)
            if self.begin and self.end:
                self.table.item(self.row_num, 3).setData(Qt.DisplayRole, self.end - self.begin + 1)
            return self

        @property
        @except_as_None()
        def timeline_row(self):
            return int(self.table.item(self.row_num, 4).text())

        def set_timeline_row(self, row_num: int):
            self._touch_item(4)
            self.table.item(self.row_num, 4).setText(str(row_num))
            return self

        @property
        @except_as_None()
        def pose_index(self):
            return int(self.table.item(self.row_num, 5).text())

        def set_pose_index(self, index: int):
            self._touch_item(5, editable=True)
            self.table.item(self.row_num, 5).setData(Qt.DisplayRole, index)
            return self

        @property
        @except_as_None()
        def action_id(self):
            return int(self.table.item(self.row_num, 6).text())

        def set_action_id(self, id_: int):
            self._touch_item(6)
            self.table.item(self.row_num, 6).setText(str(id_))
            return self

        @property
        @except_as_None()
        def action_color(self):
            return self.table.item(self.row_num, 7).background()

        def set_action_color(self, color: QColor):
            self._touch_item(7)
            self.table.item(self.row_num, 7).setBackground(color)
            return self

        def _touch_item(self, c, editable=False):
            if self.table.item(self.row_num, c) is None:
                item = QTableWidgetItem()
                if not editable:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(self.row_num, c, item)

        def _insert(self, action_label: ActionLabel):
            self.table.insertRow(self.row_num)
            self.set_action(action_label.action) \
                .set_begin(action_label.begin) \
                .set_end(action_label.end) \
                .set_timeline_row(action_label.timeline_row) \
                .set_pose_index(action_label.pose_index) \
                .set_action_id(action_label.action_id) \
                .set_action_color(action_label.color)

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
