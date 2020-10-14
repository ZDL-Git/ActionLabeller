from collections import namedtuple
from enum import Enum
from functools import partial
from typing import List, Dict, Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem, QAbstractItemView
from zdl.utils.decorator import except_as_None
from zdl.utils.io.log import logger

from model.Action import Action
from model.ActionLabel import ActionLabel
from presenter import MySignals
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
        self.setHorizontalHeaderLabels(self._Cols.headers())
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
            if row_label.begin() == action_label.begin \
                    and row_label.end() == action_label.end \
                    and row_label.timeline_row() == action_label.timeline_row:
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
            row_label_b, row_label_e, row_label_t = row_label.begin(), row_label.end(), row_label.timeline_row()
            if row_label_t not in label_cells:
                continue
            left_cell = label_cells[row_label_t][0]
            right_cell = label_cells[row_label_t][-1]
            if left_cell > row_label_e or right_cell < row_label_b:
                continue
            elif left_cell <= row_label_b:
                row_label.set_begin(right_cell + 1)
            elif right_cell >= row_label_e:
                row_label.set_end(left_cell - 1)
            else:
                new_label = row_label.to_actionlabel()
                new_label.begin = right_cell + 1
                labels_add_later.append(new_label)
                row_label.set_end(left_cell - 1)

            if row_label_b > row_label_e:
                rows_delete_later.add(t_r)

        self._delete_rows(rows_delete_later)

        for l_add in labels_add_later:
            self.add_label(l_add)

    class _Cols(Enum):
        _attrs = namedtuple('attrs', ['index', 'value_type', 'header', 'editable', 'num_sort'])
        action = _attrs(0, str, 'Action', False, False)
        begin = _attrs(1, int, 'Begin', False, True)
        end = _attrs(2, int, 'End', False, True)
        duration = _attrs(3, int, 'Duration', False, True)
        timeline_row = _attrs(4, int, 'Timeline Row', False, False)
        pose_index = _attrs(5, int, 'Pose Index', True, True)
        action_id = _attrs(6, int, 'Action Id', False, False)
        action_color = _attrs(7, QColor, 'Action Color', False, False)

        @classmethod
        def headers(cls):
            return [v.value.header for k, v in cls.__members__.items() if isinstance(v.value, cls._attrs.value)]

    class _Row:

        def __init__(self, row_num_or_actionlabel: Union[int, ActionLabel], table: 'LabeledTableWidget'):
            self.table = table

            self.action: callable = partial(self._col_value, col=self.table._Cols.action)
            self.begin: callable = partial(self._col_value, col=self.table._Cols.begin)
            self.end: callable = partial(self._col_value, col=self.table._Cols.end)
            self.duration: callable = partial(self._col_value, col=self.table._Cols.duration)
            self.timeline_row: callable = partial(self._col_value, col=self.table._Cols.timeline_row)
            self.pose_index: callable = partial(self._col_value, col=self.table._Cols.pose_index)
            self.action_id: callable = partial(self._col_value, col=self.table._Cols.action_id)
            self.action_color: callable = partial(self._col_value, col=self.table._Cols.action_color)

            self.set_action: callable = partial(self._set_col_value, col=self.table._Cols.action)
            self.set_timeline_row: callable = partial(self._set_col_value, col=self.table._Cols.timeline_row)
            self.set_pose_index: callable = partial(self._set_col_value, col=self.table._Cols.pose_index)
            self.set_action_id: callable = partial(self._set_col_value, col=self.table._Cols.action_id)
            self.set_action_color: callable = partial(self._set_col_value, col=self.table._Cols.action_color)

            if isinstance(row_num_or_actionlabel, int):
                self.row_num = row_num_or_actionlabel
            elif isinstance(row_num_or_actionlabel, ActionLabel):
                self.row_num = self.table.rowCount()
                self._insert(row_num_or_actionlabel)
            else:
                raise TypeError

        def set_begin(self, begin_: int):
            self._set_col_value(begin_, self.table._Cols.begin)
            self._set_duration()
            return self

        def set_end(self, end_: int):
            self._set_col_value(end_, self.table._Cols.end)
            self._set_duration()
            return self

        def _set_duration(self):
            b, e = self.begin(), self.end()
            if b is not None and e is not None:
                self._set_col_value(e - b + 1, self.table._Cols.duration)
            return self

        def _col_item(self, col: 'LabeledTableWidget._Cols'):
            r, c, e = self.row_num, col.value.index, col.value.editable
            if self.table.item(r, c) is None:
                item = QTableWidgetItem()
                if not e:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, item)
            return self.table.item(r, c)

        @except_as_None()
        def _col_value(self, col: 'LabeledTableWidget._Cols'):
            r, c, vt = self.row_num, col.value.index, col.value.value_type
            if vt in [QBrush, QColor]:
                v = self._col_item(col).background()
            else:
                v = vt(self._col_item(col).text())
            return v

        def _set_col_value(self, value, col: 'LabeledTableWidget._Cols'):
            r, c, vt = self.row_num, col.value.index, col.value.value_type
            if vt in [QBrush, QColor]:
                self._col_item(col).setBackground(value)
            elif col.value.num_sort:
                self._col_item(col).setData(Qt.DisplayRole, value)
            else:
                self._col_item(col).setText(str(value))
            return self

        def _disable_sort(self, disable=True):
            self.table.setSortingEnabled(not disable)

        def _insert(self, action_label: ActionLabel):
            self._disable_sort(True)
            self.table.insertRow(self.row_num)
            self.set_action(action_label.action) \
                .set_begin(action_label.begin) \
                .set_end(action_label.end) \
                .set_timeline_row(action_label.timeline_row) \
                .set_pose_index(action_label.pose_index) \
                .set_action_id(action_label.action_id) \
                .set_action_color(action_label.color)
            self._disable_sort(False)

        def delete(self):
            self.table._delete_rows([self.row_num])

        def to_actionlabel(self) -> ActionLabel:
            label = ActionLabel(self.action(),
                                self.action_id(),
                                self.action_color(),
                                self.begin(),
                                self.end(),
                                self.timeline_row(),
                                self.pose_index())
            return label
