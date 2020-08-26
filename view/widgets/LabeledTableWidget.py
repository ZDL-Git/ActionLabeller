from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem

from common.utils import Log
from model.ActionLabel import ActionLabel
from presenter import MySignals
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from view.widgets.Common import TableDecorators
from view.widgets.TableViewCommon import TableViewCommon


class LabeledTableWidget(QTableWidget, TableViewCommon):
    def __init__(self, parent):
        super().__init__()

        self.cellDoubleClicked.connect(self.slot_cellDoubleClicked)
        self.itemSelectionChanged.connect(self.slot_itemSelectionChanged)
        # self.cellChanged.connect(self.slot_cellChanged)

    def __init_later__(self):
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['Action', 'Begin', 'End', 'Timeline Row', 'Action Id', 'Action Color'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setColumnHidden(3, True)
        self.setColumnHidden(4, True)
        self.setColumnHidden(5, True)

    # def slot_cellChanged(self, r, c):
    #     Log.debug(r, c)

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        Log.debug('here', e.key())
        if e.key() in [Qt.Key_Backspace, Qt.Key_D]:
            rows, labels = self._labels_selected()
            mySignals.labeled_delete.emit(labels, MySignals.Emitter.T_LABELED)
            self._delete_rows(rows)
        elif e.key() == Qt.Key_R:
            if self.label_clicked is not None:
                self._slot_video_play(self.label_clicked.begin, self.label_clicked.end)

    def slot_itemSelectionChanged(self):
        Log.debug('here')

    def slot_cellDoubleClicked(self, r, c):
        Log.debug(r, c)
        label = self._label_at(r)
        mySignals.labeled_selected.emit(label, MySignals.Emitter.T_LABELED)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_created(self, action_label: ActionLabel, emitter):
        Log.debug(action_label, emitter)
        self._label_cells_delete({action_label.timeline_row: list(range(action_label.begin, action_label.end + 1))})
        row_i = self.add_label(action_label)
        self._select_row(row_i)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_selected(self, action_label, emitter):
        Log.debug(action_label, emitter)
        label_row = self._get_label_row_num(action_label)
        if label_row is not None:
            self.selectRow(label_row)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_delete(self, action_label, emitter):
        Log.debug(action_label, emitter)
        row_i = self._get_label_row_num(action_label)
        if row_i is not None:
            self._delete_rows(row_i)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_cells_delete(self, label_cells, emitter):
        Log.debug(label_cells, emitter)
        self._label_cells_delete(label_cells)

    @TableDecorators.dissort
    def slot_action_update(self, emitter):
        rows_delete_later = set()
        labels_updated = []
        actions = CommonUnit.get_all_actions()
        _actions_dict = {a.id: a for a in actions}
        for r in range(self.rowCount()):
            id = int(self.item(r, 4).text())
            if id in _actions_dict:
                self.item(r, 0).setText(_actions_dict[id].name)
                self.item(r, 5).setBackground(_actions_dict[id].color)
                labels_updated.append(self._label_at(r))
            else:
                Log.debug(_actions_dict)
                rows_delete_later.add(r)
        self._delete_rows(rows_delete_later)
        mySignals.labeled_update.emit(labels_updated, MySignals.Emitter.T_LABELED)

    def get_all_labels(self) -> list:
        labels = []
        for r in range(self.rowCount()):
            labels.append(self._label_at(r))
        labels.sort(key=lambda l: l.begin)
        return labels

    def _label_at(self, r):
        return ActionLabel(self.item(r, 0).text(), int(self.item(r, 4).text()), self.item(r, 5).background(),
                           int(self.item(r, 1).text()),
                           int(self.item(r, 2).text()),
                           int(self.item(r, 3).text()))

    def _labels_selected(self) -> (set, List[ActionLabel]):
        rows = set()
        for index in self.selectedIndexes():
            rows.add(index.row())
        labels = []
        for r in rows:
            labels.append(self._label_at(r))
        return rows, labels

    def _get_label_row_num(self, action_label: ActionLabel):
        rows = self.rowCount()
        for r in range(rows):
            if self.item(r, 1) and self.item(r, 1).text() == str(action_label.begin):
                if self.item(r, 2) and self.item(r, 2).text() == str(action_label.end):
                    if self.item(r, 3) and self.item(r, 3).text() == str(action_label.timeline_row):
                        return r
        return None

    def add_label(self, action_label: ActionLabel):
        action = QTableWidgetItem(action_label.action)
        # action.setFlags(action.flags() & ~Qt.ItemIsEditable)
        begin = QTableWidgetItem()
        begin.setData(Qt.DisplayRole, action_label.begin)
        end = QTableWidgetItem()
        end.setData(Qt.DisplayRole, action_label.end)
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
        return new_row_i

    def _label_cells_delete(self, label_cells):
        for k in label_cells:
            label_cells[k].sort()
        rows_delete_later = set()
        labels_add_later = []
        for t_r in range(self.rowCount()):
            timeline_row = self.item(t_r, 3).text() and int(self.item(t_r, 3).text())
            if timeline_row not in label_cells:
                continue
            label_begin = int(self.item(t_r, 1).text())
            label_end = int(self.item(t_r, 2).text())
            if label_cells[timeline_row][0] > label_end or label_cells[timeline_row][-1] < label_begin:
                continue
            elif label_cells[timeline_row][0] <= label_begin:
                self.item(t_r, 1).setData(Qt.DisplayRole, label_cells[timeline_row][-1] + 1)
            elif label_cells[timeline_row][-1] >= label_end:
                self.item(t_r, 2).setData(Qt.DisplayRole, label_cells[timeline_row][0] - 1)
            else:
                self.item(t_r, 2).setData(Qt.DisplayRole, label_cells[timeline_row][0] - 1)
                labels_add_later.append(
                    ActionLabel(self.item(t_r, 0).text(),
                                int(self.item(t_r, 4).text()),
                                self.item(t_r, 5).background(),
                                label_cells[timeline_row][-1] + 1,
                                label_end, timeline_row))

            if int(self.item(t_r, 1).text()) > int(self.item(t_r, 2).text()):
                rows_delete_later.add(t_r)

        self._delete_rows(rows_delete_later)

        for l_add in labels_add_later:
            self.add_label(l_add)
