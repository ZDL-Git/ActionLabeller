import random
import typing
from typing import List

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import global_
from action import ActionLabel, Action
from utils import *


class TableDecorators:
    @classmethod
    def dissort(cls, func):
        def func_wrapper(*arg):
            arg[0].setSortingEnabled(False)
            func(*arg)
            arg[0].setSortingEnabled(True)

        return func_wrapper

    @classmethod
    def block_signals(cls, func):
        def func_wrapper(*arg):
            arg[0].blockSignals(True)
            func(*arg)
            arg[0].blockSignals(False)

        return func_wrapper


class TableViewCommon(QTableView):
    def _delete_rows(self: QTableView, rows):
        for r_d in sorted(rows, reverse=True):
            self.model().removeRow(r_d)

    def _select_row(self: QTableView, row):
        self.selectRow(row)

    def _unselect_all(self: QTableView):
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


class LabeledTableWidget(QTableWidget, TableViewCommon):
    def __init__(self, parent):
        super().__init__()

        self.cellDoubleClicked.connect(self.slot_cellDoubleClicked)
        self.itemSelectionChanged.connect(self.slot_itemSelectionChanged)
        # self.cellChanged.connect(self.slot_cellChanged)

        global_.mySignals.label_created.connect(self.slot_label_created)
        global_.mySignals.label_selected.connect(self.slot_label_selected)
        global_.mySignals.label_delete.connect(self.slot_label_delete)
        global_.mySignals.label_cells_delete.connect(self.slot_label_cells_delete)
        global_.mySignals.action_update.connect(self.slot_action_update)

    def __init_later__(self):
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['Action', 'Begin', 'End', 'Timeline Row', 'Action Id', 'Action Color'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setColumnHidden(3, True)
        self.setColumnHidden(4, True)
        self.setColumnHidden(5, True)

        global_.g_all_labels = self.get_all_labels

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_created(self, action_label: ActionLabel, emitter):
        Log.debug(action_label, emitter)
        self._label_cells_delete({action_label.timeline_row: list(range(action_label.begin, action_label.end + 1))})
        row_i = self._add_label(action_label)
        self._select_row(row_i)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_selected(self, action_label, emitter):
        Log.debug(action_label, emitter)
        label_row = self._get_label_row(action_label)
        if label_row is not None:
            self.selectRow(label_row)

    @TableDecorators.dissort
    @TableDecorators.block_signals
    def slot_label_delete(self, action_label, emitter):
        Log.debug(action_label, emitter)
        row_i = self._get_label_row(action_label)
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
        actions = global_.g_all_actions()
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
        global_.mySignals.labeled_update.emit(labels_updated, global_.Emitter.T_LABELED)

    # def slot_cellChanged(self, r, c):
    #     Log.debug(r, c)

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        Log.debug('here', e.key())
        if e.key() in [Qt.Key_Backspace, Qt.Key_D]:
            rows, labels = self._labels_selected()
            global_.mySignals.labeled_delete.emit(labels, global_.Emitter.T_LABELED)
            self._delete_rows(rows)
        elif e.key() == Qt.Key_R:
            if self.label_clicked is not None:
                self._slot_video_play(self.label_clicked.begin, self.label_clicked.end)

    def slot_itemSelectionChanged(self):
        Log.debug('here')

    def slot_cellDoubleClicked(self, r, c):
        Log.debug(r, c)
        label = self._label_at(r)
        global_.mySignals.labeled_selected.emit(label, global_.Emitter.T_LABELED)

    def get_all_labels(self) -> list:
        labels = []
        for r in range(self.rowCount()):
            labels.append(self._label_at(r))
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
                    ActionLabel(self.item(t_r, 0).text(), int(self.item(t_r, 4).text()), self.item(t_r, 5).background(),
                                label_cells[timeline_row][-1] + 1,
                                label_end, timeline_row))

            if int(self.item(t_r, 1).text()) > int(self.item(t_r, 2).text()):
                rows_delete_later.add(t_r)

        self._delete_rows(rows_delete_later)

        for l_add in labels_add_later:
            self._add_label(l_add)

    def _get_label_row(self, action_label: ActionLabel):
        rows = self.rowCount()
        for r in range(rows):
            if self.item(r, 1) and self.item(r, 1).text() == str(action_label.begin):
                if self.item(r, 2) and self.item(r, 2).text() == str(action_label.end):
                    if self.item(r, 3) and self.item(r, 3).text() == str(action_label.timeline_row):
                        return r
        return None

    def _add_label(self, action_label: ActionLabel):
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


class ActionTableWidget(QTableWidget, TableViewCommon):
    def __init__(self, parent):
        super().__init__()
        # TODO
        self.header_labels = {''}

        self.cellChanged.connect(self.slot_cellChanged)
        self.cellDoubleClicked.connect(self.slot_cellDoubleClicked)

    def __init_later__(self):
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['Action Name', 'Label Color', 'Default', 'Action Id', 'Y-min', 'Y-max'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setColumnHidden(3, True)
        self.setColumnHidden(4, True)
        self.setColumnHidden(5, True)

        global_.g_default_action = self.get_default_action
        global_.g_all_actions = self.get_all_actions

        self.blockSignals(True)
        for i in range(2):
            action = Action(self._generate_id(), f"action{i + 1}",
                            QColor('#fe8a71') if i == 0 else QColor('#0e9aa7'),
                            i == 0)
            self._insert_action(action)
        self.blockSignals(False)

    def slot_cellChanged(self, r, c):
        Log.debug(r, c)
        if c == 2:
            if self.item(r, c).checkState() == Qt.Checked:
                self._unselect_others(except_=r)
            elif self.item(r, c).checkState() == Qt.Unchecked:
                pass
        elif c == 0:
            pass

        global_.mySignals.action_update.emit(global_.Emitter.T_TEMP)
        # global_.g_all_actions = self.get_all_actions

    def slot_cellDoubleClicked(self, r, c):
        Log.debug(r, c)
        if c == 1:
            item = self.item(r, c)
            color = QColorDialog.getColor(initial=item.background().color())  # type:QColor
            if color.isValid():
                if color == Qt.white:
                    global_.g_status_prompt('Cannot set white color to action!')
                    Log.warn('Cannot set white color to action!')
                    return
                item.setBackground(color)

    @TableDecorators.block_signals
    def slot_action_add(self, checked):  # if use decorator, must receive checked param of button clicked event
        Log.debug('')
        action = Action(self._generate_id(), '', QColor(QRandomGenerator().global_().generate()), False)
        self._insert_action(action)
        self.editItem(self.item(self.rowCount() - 1, 0))

    @TableDecorators.dissort
    def slot_del_selected_actions(self,
                                  checked):  # if use decorator, must receive checked param of button clicked event
        Log.debug('')
        if not self.selectedIndexes():
            QMessageBox.information(self, 'ActionLabel Warning',
                                    "Select action first!",
                                    QMessageBox.Ok, QMessageBox.Ok)
            return

        if QMessageBox.Cancel == QMessageBox.warning(self, 'ActionLabel Warning',
                                                     "All you sure to delete action template?"
                                                     " All the related action label will be deleted!",
                                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel):
            return
        rows = set()
        for index in self.selectedIndexes():
            rows.add(index.row())
        for r in sorted(rows, reverse=True):
            self.removeRow(r)
        global_.mySignals.action_update.emit(global_.Emitter.T_TEMP)

    def get_all_actions(self):
        Log.debug('')
        actions = []
        try:
            for r in range(self.rowCount()):
                actions.append(self._row_to_action(r))
        except Exception as e:
            Log.error(e.__str__())
        finally:
            return actions

    def get_default_action(self):
        rows = self.rowCount()
        if rows == 0:
            QMessageBox.information(self, 'ActionLabel',
                                    "Please add action first!",
                                    QMessageBox.Ok, QMessageBox.Ok)
            return None

        actions = self.get_all_actions()
        for action in actions:
            if action.default:
                if not action.name:
                    QMessageBox.information(self, 'ActionLabel',
                                            "Please complete action name first!",
                                            QMessageBox.Ok, QMessageBox.Ok)
                    return None
                # 1.return default
                return action
        # 2.select from dialog
        action_name, ok_pressed = QInputDialog.getItem(self, "ActionLabel", "Actions:", [a.name for a in actions], 0,
                                                       False)
        if ok_pressed and action_name:
            return list(filter(lambda a: a.name == action_name, actions))[0]

        return None

    def _generate_id(self):
        actions = global_.g_all_actions()
        if actions:
            return max([action.id for action in actions]) + 1
        return 0

    def _insert_action(self, action: Action):
        id = QTableWidgetItem(str(action.id))
        name = QTableWidgetItem(action.name)
        color = QTableWidgetItem()
        color.setFlags(Qt.ItemIsEnabled)
        color.setBackground(action.color)
        default = QTableWidgetItem()
        default.setCheckState(Qt.Checked if action.default else Qt.Unchecked)
        r = self.rowCount()
        self.insertRow(r)
        self.setItem(r, 0, name)
        self.setItem(r, 1, color)
        self.setItem(r, 2, default)
        self.setItem(r, 3, id)

    def _del_action(self, id):
        for r in range(self.rowCount()):
            if self.item(r, 3).text() == str(id):
                self.removeRow(r)

    def _unselect_others(self, except_):
        for r in range(self.rowCount()):
            if r == except_:
                continue
            self.item(r, 2).setCheckState(Qt.Unchecked)

    def _row_to_action(self, r):
        id = self.item(r, 3) and int(self.item(r, 3).text())
        name = self.item(r, 0) and self.item(r, 0).text()
        xml_ymin = self.item(r, 4) and self.item(r, 4).text() and int(self.item(r, 4).text()) or None
        xml_ymax = self.item(r, 5) and self.item(r, 5).text() and int(self.item(r, 5).text()) or None
        return Action(id, name,
                      self.item(r, 1).background(), self.item(r, 2).checkState() == Qt.Checked,
                      xml_ymin, xml_ymax)

    def slot_test(self, *arg):
        Log.debug(*arg)


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


class TimelineTableView(TableViewCommon):
    def __init__(self, parent):
        super().__init__()

        self.key_control_pressing = False
        self.entry_cell_pos = None
        self.label_clicked = None
        self.hcenter_before_wheeling = None
        self.current_column = 0

        self.clicked.connect(self.slot_cellClicked)
        self.pressed.connect(self.slot_cellPressed)
        self.doubleClicked.connect(self.slot_cellDoubleClicked)

        self.label_create_dialog = self.TimelineDialog(self)

        # global_.mySignals.jump_to.connect(self.slot_jump_to)
        global_.mySignals.follow_to.connect(self.slot_follow_to)
        global_.mySignals.labeled_selected.connect(self.slot_label_play)
        global_.mySignals.labeled_update.connect(self.slot_label_update)
        global_.mySignals.labeled_delete.connect(self.slot_label_delete)

    def __init_later__(self):
        self.setModel(TimelineTableModel(20, 50))

        header = self.horizontalHeader()
        header.sectionPressed.disconnect()
        header.sectionClicked.connect(self.slot_horizontalHeaderClicked)

        self.horizontalScrollBar().installEventFilter(self)
        self.horizontalScrollBar().sliderMoved.connect(self.slot_sliderMoved)
        # self.installEventFilter(self)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        Log.debug(e, e.key(), e.type())
        if e.key() == Qt.Key_Control:
            self.key_control_pressing = True
            self.hcenter_before_wheeling = self._center_col()
        # elif e.key() == Qt.Key_Control:
        #     pass

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        Log.debug('here', e.key())
        if e.key() == Qt.Key_Control:
            self.key_control_pressing = False
        elif e.key() in [Qt.Key_Backspace, Qt.Key_D]:
            cells_deleted = self._del_selected_label_cells()
            global_.mySignals.label_cells_delete.emit(cells_deleted, global_.Emitter.T_LABEL)
        elif e.key() == Qt.Key_R:
            if self.label_clicked is not None:
                self._label_play(self.label_clicked)
                # self._emit_video_play(self.label_clicked.begin, self.label_clicked.end)

    def mouseReleaseEvent(self, e):
        Log.debug('here')
        super().mouseReleaseEvent(e)
        if not self.entry_cell_pos:
            return
        # rect = self.selectionModel() and self.selectionModel().selectedIndexes()[-1]
        _selected = self.selectionModel()
        if not _selected.hasSelection():
            return
        rows, cols = set(), set()
        for qindex in _selected.selectedIndexes():
            rows.add(qindex.row())
            cols.add(qindex.column())
        l, r, t, b = min(cols), max(cols), min(rows), max(rows)
        Log.debug('l r t b', l, r, t, b)
        if l == r and t == b or b - t == self.model().rowCount() - 1:
            return
        entry_item = self.model().item(*self.entry_cell_pos)
        if entry_item.background() == Qt.white:
            default_action = global_.g_default_action()
            if not default_action:
                return
            name, color, id = default_action.name, default_action.color, default_action.id
        else:
            name, color, id = entry_item.toolTip(), entry_item.background(), entry_item.whatsThis()
        changed = False
        for c in range(l, r + 1):
            item = self.model().item(self.entry_cell_pos[0], c)
            if item is None:
                item = QStandardItem()
                self.model().setItem(self.entry_cell_pos[0], c, item)
            if item.background() != color:
                changed = True
                item.setBackground(color)
                item.setToolTip(name)
                item.setWhatsThis(str(id))

        if changed:
            found_label = self._detect_label(*self.entry_cell_pos)  # redetect after update, for sections connection
            if found_label is not None:
                global_.mySignals.label_created.emit(found_label, global_.Emitter.T_LABEL)

    def wheelEvent(self, e: QWheelEvent) -> None:
        Log.debug(f'wheel {e.angleDelta()}')
        idler_forward = e.angleDelta().y() > 0
        if self.key_control_pressing:
            col_width = self.columnWidth(0)
            col_width += 3 if idler_forward else -3
            t_width = self.width()  # no vertical header
            cols = self.horizontalHeader().count()
            col_width_to = max(col_width, int(t_width / cols))

            Log.warn(self.hcenter_before_wheeling)
            self.horizontalHeader().setDefaultSectionSize(col_width_to)
            self._col_to_center(self.hcenter_before_wheeling)
        else:
            bias = -2 if idler_forward else 2
            # self._col_scroll(bias) # conflicts with follow_to
            global_.mySignals.schedule.emit(-1, bias, -1, global_.Emitter.T_WHEEL)

    def slot_cellPressed(self, qindex):
        r, c = qindex.row(), qindex.column()
        Log.debug(r, c, self.model().item(r, c))
        global_.mySignals.video_pause.emit()
        if not self.model().item(r, c):
            item = QStandardItem('')
            item.setBackground(Qt.white)
            self.model().setItem(r, c, item)
        self.entry_cell_pos = (r, c)

    def slot_cellClicked(self, qindex):
        r, c = qindex.row(), qindex.column()
        Log.debug(r, c)
        label = self._detect_label(r, c)
        if label is None:
            self.label_clicked = None
        else:
            self.label_clicked = label
            self._select_label(label)
            global_.mySignals.label_selected.emit(label, global_.Emitter.T_LABEL)

    def slot_cellDoubleClicked(self, qindex):
        r, c = qindex.row(), qindex.column()
        label = self._detect_label(r, c)  # type:ActionLabel
        if label is not None:
            self._label_play(label)
            # self._emit_video_play(label.begin, label.end)
        else:
            global_.g_status_prompt(str(f'Current Frame {self.current_column}'))
            # self.label_create_dialog.set_actions(actions)
            # self.label_create_dialog.set_cur_index(self.current_column)
            self.label_create_dialog.load(self.current_column)
            self.label_create_dialog.exec_()
            # if self.label_create_dialog.exec_():
            #     label = self.label_create_dialog.take_label()
            #     Log.debug('', label)
            #     if label.end is not None:
            #         if label.begin > label.end:
            #             warn_ = "Label's begin exceeds the end, ignored!"
            #             global_.g_status_prompt(warn_)
            #             Log.warn(warn_)
            #             return
            #         if self._settle_label(label):
            #             global_.mySignals.label_created.emit(label, global_.Emitter.T_LABEL)

    def slot_sliderMoved(self, pos):
        Log.debug(pos)
        # col_c = self.columnCount()
        # hscrollbar = self.horizontalScrollBar()
        index = (self.model().columnCount() - 1) * pos / self.horizontalScrollBar().maximum()

        global_.mySignals.schedule.emit(index, -1, -1, global_.Emitter.T_HSCROLL)
        # self.selectColumn(index)  # crash bug

    def slot_horizontalHeaderClicked(self, i):
        Log.info('index', i)
        global_.mySignals.schedule.emit(i, -1, -1, global_.Emitter.T_HHEADER)

    @TableDecorators.block_signals
    def slot_label_delete(self, action_labels: List[ActionLabel], emitter):
        Log.debug(action_labels, emitter)
        self._unselect_all()
        for label in action_labels:
            self._del_label(label)

    @TableDecorators.block_signals
    def slot_label_update(self, action_labels: List[ActionLabel], emitter):
        Log.debug(action_labels, emitter)
        self._unselect_all()
        for label in action_labels:
            self._update_label(label)

    @TableDecorators.block_signals
    def slot_label_play(self, action_label: ActionLabel, emitter):
        Log.debug(action_label, emitter)
        self._label_play(action_label)

    @TableDecorators.block_signals
    def slot_follow_to(self, emitter, index):
        self.current_column = index
        if emitter == global_.Emitter.T_HSCROLL:
            return
        self._col_to_center(index)

    def set_column_count(self, c):
        self.model().setColumnCount(c)

    def _label_play(self, action_label: ActionLabel):
        self._unselect_all()
        self._select_label(action_label)
        self._emit_video_play(action_label.begin, action_label.end)

    def _emit_video_play(self, start_at, stop_at=-1):
        global_.mySignals.schedule.emit(start_at, -1, stop_at, global_.Emitter.T_LABEL)
        global_.mySignals.video_start.emit()

    def _settle_label(self, label: ActionLabel):
        t_r = None
        choices = list(range(self.model().rowCount()))
        while choices:
            r = random.choice(choices)
            for c in range(max(0, label.begin), min(self.model().columnCount(), label.end + 1)):
                if self.model().item(r, c) and self.model().item(r, c).background() != Qt.white:
                    choices.remove(r)
                    break
            else:
                t_r = r
                break
        if t_r is None:
            warn_ = 'All related lines are not empty, please check!'
            Log.warn(warn_)
            global_.g_status_prompt(warn_)
            return None
        label.timeline_row = t_r
        if not self._plot_label(label):
            return None
        return t_r

    def _plot_label(self, label: ActionLabel):
        Log.debug(label)
        if label.end >= self.model().columnCount() and \
                QMessageBox.Cancel == QMessageBox.information(self, 'ActionLabel',
                                                              "The end exceeds video frames count, "
                                                              "are you sure to create this action label?",
                                                              QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel):
            return False
        for c in range(max(0, label.begin), label.end + 1):
            item = self.model().item(label.timeline_row, c)
            if item is None:
                item = QStandardItem()
                self.model().setItem(label.timeline_row, c, item)

            item.setBackground(label.color)
            item.setToolTip(label.action)
            item.setWhatsThis(str(label.action_id))
        return True

    def _detect_label(self, row, col):
        item = self.model().item(row, col)
        if not item or item.background() == Qt.white:
            return None

        color = item.background()
        l = r = col
        for ci in range(col - 1, -1, -1):
            if self.model().item(row, ci) and self.model().item(row, ci).background() == color:
                l = ci
            else:
                break
        for ci in range(col + 1, self.model().columnCount()):
            if self.model().item(row, ci) and self.model().item(row, ci).background() == color:
                r = ci
            else:
                break
        Log.debug(item.toolTip(), item.whatsThis(), item.background())
        return ActionLabel(item.toolTip(), int(item.whatsThis()), item.background(), l, r, row)

    def _select_label(self, label: ActionLabel):
        Log.debug(label)
        Log.debug(QRect(label.begin, label.timeline_row, label.end - label.begin + 1, 1))
        self.selectionModel().select(
            QItemSelection(self.model().index(label.timeline_row, label.begin),
                           self.model().index(label.timeline_row, label.end)),
            QItemSelectionModel.ClearAndSelect)

    def _update_label(self, label: ActionLabel):
        for c in range(label.begin, label.end + 1):
            item = self.model().item(label.timeline_row, c)
            if item is None:
                item = QStandardItem()
                self.model().setItem(label.timeline_row, c, item)
            item.setBackground(label.color)
            item.setWhatsThis(str(label.action_id))
            item.setToolTip(label.action)

    def _del_label(self, label: ActionLabel):
        for c in range(label.begin, label.end + 1):
            item = self.model().item(label.timeline_row, c)
            if item is None:
                continue
            item.setBackground(Qt.white)
            item.setWhatsThis(None)
            item.setToolTip(None)

    def _del_selected_label_cells(self):
        Log.info('here')
        label_cells = {}  # key:row,value:cols list
        for qindex in self.selectedIndexes():
            r, c = qindex.row(), qindex.column()
            item = self.model().item(r, c)
            if item is None or item.background() == Qt.white:
                continue
            item.setBackground(Qt.white)
            item.setWhatsThis(None)
            item.setToolTip(None)
            if r in label_cells:
                label_cells[r].append(c)
            else:
                label_cells[r] = [c]
        self._unselect_all()
        return label_cells

    def _col_to_center(self, index):
        hscrollbar = self.horizontalScrollBar()
        # bias_to_center = self.width() / 2 / self.columnWidth(0)
        page_half = hscrollbar.pageStep() / 2
        left_index = index - page_half
        hscrollbar.setSliderPosition(max(0, left_index))

    def _center_col(self):  # only supports static case
        t_width = self.width()  # no vertical header
        return self.columnAt(int(t_width / 2))

    Ui_Dialog, _ = uic.loadUiType("qt_gui/timelinedialog.ui")

    class TimelineDialog(QDialog, Ui_Dialog):
        def __init__(self, parent=None):
            QDialog.__init__(self, parent, flags=Qt.Dialog)
            self.setupUi(self)
            self.line_begin.setValidator(QIntValidator())
            self.line_end.setValidator(QIntValidator())

            self.cur_frame_index = None
            self.labels_unfinished = []  # type:List
            # self.stress_color = QColor('#b88481')

            self.btn_new.clicked.connect(self.slot_btn_new_clicked)

        def load(self, cur_frame_index):
            self.cur_frame_index = cur_frame_index
            self._load_new_comb()
            self._load_unfinished()

        def _load_new_comb(self):
            # created in qt creator IDE
            self.combo_action_names.clear()
            self.actions = actions = global_.g_all_actions()
            if actions:
                _action_names = [a.name for a in actions]
                self.combo_action_names.addItems(_action_names)
                default = list(filter(lambda action: action.default, actions))
                if default:
                    default = default[0].name
                    self.combo_action_names.setCurrentIndex(_action_names.index(default))
            self.line_begin.setText(str(self.cur_frame_index))
            self.line_end.clear()

        def _load_unfinished(self):
            clear_layout(self.instore_layout)
            for i, label in enumerate(self.labels_unfinished):
                self._add_comb(label, i)

        def _add_comb(self, action_label: ActionLabel, index_in_labels_unfinished: int):
            layout = QHBoxLayout()
            combox = QComboBox()
            begin_editor = QLineEdit()
            end_editor = QLineEdit()
            btn_finish = QPushButton()
            layout.addWidget(combox, 2)
            layout.addWidget(begin_editor, 1)
            layout.addWidget(end_editor, 1)
            layout.addWidget(btn_finish, 1)
            layout.setSpacing(5)
            self.instore_layout.addLayout(layout, 1)

            _action_names = [a.name for a in global_.g_all_actions()]
            combox.addItems(_action_names)
            combox.setCurrentIndex(
                action_label.action in _action_names and _action_names.index(action_label.action)
                or 0)
            int_validator = QIntValidator()
            begin_editor.setValidator(int_validator)
            end_editor.setValidator(int_validator)
            begin_editor.setText(str(action_label.begin))
            end_editor.setText(str(self.cur_frame_index))
            btn_finish.setText('Finish')
            begin_editor.setPlaceholderText('required')
            end_editor.setPlaceholderText('required')
            end_editor.setStyleSheet("QLineEdit { color: darkred;}")

            btn_finish.clicked.connect(
                lambda: self.slot_btn_finish_clicked(combox, begin_editor, end_editor, index_in_labels_unfinished))

        # FIXME
        def slot_btn_finish_clicked(self, w_action, w_begin, w_end, index_in_labels_unfinished):
            Log.debug('')
            action_name = w_action.currentText()
            action = list(filter(lambda a: a.name == action_name, self.actions))[0]
            begin = w_begin.text() and int(w_begin.text())
            end = w_end.text() and int(w_end.text())
            label = ActionLabel(action.name, action.id, action.color, begin, end, None)
            if not label.is_valid(['action', 'begin', 'end']):
                return
            if not self._commit_label(label):
                return
            del self.labels_unfinished[index_in_labels_unfinished]

            if self.checkb_autoclose.isChecked():
                self.buttonBox.accepted.emit()
            else:
                self._load_unfinished()

        def slot_btn_new_clicked(self):
            Log.debug('')
            action_name = self.combo_action_names.currentText()
            if not action_name:
                Log.info('Please add action first!')
                return
            action = list(filter(lambda a: a.name == action_name, self.actions))[0]
            begin = self.line_begin.text() and int(self.line_begin.text())
            end = self.line_end.text() and int(self.line_end.text()) or None
            label = ActionLabel(action.name, action.id, action.color, begin,
                                end, None)
            if not label.is_valid(['action', 'begin']):
                return
            if end:
                self._commit_label(label)
            else:
                self.labels_unfinished.append(label)

            if self.checkb_autoclose.isChecked():
                self.buttonBox.accepted.emit()
            else:
                self._load_unfinished()

        def _commit_label(self, label: ActionLabel):
            Log.debug('', label)
            if not label.is_valid(['action', 'action_id', 'color', 'begin', 'end']):
                return False
            if self.parent()._settle_label(label) is None:
                return False
            global_.mySignals.label_created.emit(label, global_.Emitter.T_LABEL)
            return True

        def exec_(self):
            # self.setFixedWidth(self.width())
            # self.setMaximumHeight(self.height())
            return super().exec_()

        # def take_label(self):
        #     take = self.label_changed
        #     self.label_changed = None
        #     return take


class TimelineTableModel(QStandardItemModel):
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(section)
        return QVariant()


class MyVideoLabelWidget(QLabel):

    def __init__(self, parent):
        super().__init__()
        self.entry_row_index = None
        self.video_obj = None
        self.video_playing = False
        # self.v_buffer = collections.deque(maxlen=100)

        # self.cellClicked.connect(self.slot_cellClicked)
        # self.cellActivated.connect(self.slot_cellActivated)
        # self.itemSelectionChanged.connect(self.slot_itemSelectionChanged)
        # self.cellPressed.connect(self.slot_cellPressed)
        global_.mySignals.schedule.connect(self.slot_schedule)
        global_.mySignals.timer_video.timeout.connect(self.timer_flush_frame)
        global_.mySignals.video_pause_or_resume.connect(self.pause_or_resume)
        global_.mySignals.video_start.connect(self.slot_start)
        global_.mySignals.video_pause.connect(self.slot_pause)

    def set_video(self, video):
        self.video_obj = video

    def slot_schedule(self, jump_to, bias, stop_at, emitter):
        # index: related signal defined to receive int parameters, None will be cast to large number 146624904,
        #        hence replace None with -1
        if jump_to != -1:
            bias = None
        Log.info(jump_to, bias)

        if self.video_obj:
            self.video_obj.schedule(jump_to, bias, stop_at, emitter)

    def mousePressEvent(self, e):
        self.pause_or_resume()

    def pause_or_resume(self):
        if self.video_playing:
            self.slot_pause()
        else:
            self.slot_start()

    def slot_pause(self):
        Log.info('')
        self.video_playing = False

    def slot_start(self):
        # self.timer_video.start()
        if not self.video_obj:
            return
        self.video_playing = True

    def timer_flush_frame(self):
        if self.video_obj is None:
            return
        if not self.video_playing and not self.video_obj.scheduled:
            return

        emitter, i, frame = self.video_obj.read()
        if frame is None:
            self.video_playing = False
            return
        global_.mySignals.follow_to.emit(emitter, i)

        height, width, bytesPerComponent = frame.shape
        bytesPerLine = bytesPerComponent * width
        q_image = QImage(frame.data, width, height, bytesPerLine,
                         QImage.Format_RGB888).scaled(self.width(), self.height(),
                                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        q_pixmap = QPixmap.fromImage(q_image)
        self.setPixmap(q_pixmap)

        # self.label_note.setText(f'frame:{self.cur_index}')

        # elif not ret:
        #     self.cap.release()
        #     # self.timer_video.stop()
        #     # self.statusBar.showMessage('播放结束！')
        # else:
        #     self.flush_frame()


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().setParent(None)
        elif child.layout() is not None:
            clear_layout(child.layout())
