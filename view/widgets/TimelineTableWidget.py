import random
import typing

from PyQt5 import uic
from PyQt5.QtCore import Qt, QVariant, QRect, QItemSelection, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QKeyEvent, QStandardItem, QWheelEvent, QIntValidator
from PyQt5.QtWidgets import QCheckBox, QAbstractItemView, QDialog, QHBoxLayout, QComboBox, QLineEdit, \
    QPushButton
from zdl.utils.helper.qt import TableDecorators, clear_layout
from zdl.utils.io.log import logger

from model.Action import Action
from model.ActionLabel import ActionLabel
from presenter import MySignals
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from view.widgets.TableHelpers import TableViewExtended


class TimelineTableView(TableViewExtended):
    def __init__(self, parent):
        super().__init__()

        self.key_control_pressing = False
        self.entry_cell_pos = None
        self.label_clicked = None
        self.hcenter_before_wheeling = None
        self.current_column = 0
        self.b_scroll_follow = True

        self.clicked.connect(self.slot_cellClicked)
        self.pressed.connect(self.slot_cellPressed)

        self.label_create_dialog = self.TimelineDialog(self)

    def __init_later__(self):
        self.setModel(TimelineTableModel(20, 50))
        self.setSortingEnabled(False)

        header = self.horizontalHeader()
        header.sectionPressed.disconnect()

        self.horizontalScrollBar().sliderMoved.connect(self.slot_sliderMoved)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollbar_h = 6
        self.horizontalScrollBar().setStyleSheet(
            f'height: {scrollbar_h}px;'
            f'color: red;'
            f'background-color: lightgray;')
        self.setFixedHeight(self.model().rowCount() * self.rowHeight(0)
                            + self.horizontalHeader().height()
                            + 2 * self.frameWidth()
                            + scrollbar_h)

        self.ckb_follow = QCheckBox('Follow', self)
        self.ckb_follow.setToolTip('Table column scrolling follows the video playing, will consume a lot of resources')
        self.ckb_follow.setCheckState(Qt.Checked if self.b_scroll_follow else Qt.Unchecked)
        self.ckb_follow.stateChanged.connect(self.slot_ckb_follow)
        self.ckb_follow.setStyleSheet(
            f'''QCheckBox {{margin-top: {self.horizontalHeader().height() + 5};
                            margin-left: 5px;
                            font-size: 10px;}}
                QCheckBox::indicator {{ height: 10px;
                                        width: 10px;}}
                QCheckBox::indicator:checked {{ background-color: red;}}
                QCheckBox::indicator:unchecked {{ background-color: gray;}}''')

    def keyPressEvent(self, e: QKeyEvent) -> None:
        logger.debug(f'{e}, {e.key()}, {e.type()}')
        if e.key() == Qt.Key_Control:
            self.key_control_pressing = True
            self.hcenter_before_wheeling = self._center_col()
        # elif e.key() == Qt.Key_Control:
        #     pass

    def keyReleaseEvent(self, e: QKeyEvent) -> None:
        logger.debug(e.key())
        if e.key() == Qt.Key_Control:
            self.key_control_pressing = False
        elif e.key() in [Qt.Key_Backspace, Qt.Key_D]:
            cells_deleted = self._del_selected_label_cells()
            mySignals.label_cells_delete.emit(cells_deleted, MySignals.Emitter.T_LABEL)
        elif e.key() == Qt.Key_R:
            if self.label_clicked is not None:
                self._label_play(self.label_clicked)

    def mouseReleaseEvent(self, e):
        logger.debug('')
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
        logger.debug(f'l r t b {l} {r} {t} {b}')
        if l == r and t == b or b - t == self.model().rowCount() - 1:
            return
        entry_item = self.model().item(*self.entry_cell_pos)
        if entry_item.background() == Qt.white:
            default_action = CommonUnit.get_default_action()
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
                mySignals.label_created.emit(found_label, MySignals.Emitter.T_LABEL)

    def wheelEvent(self, e: QWheelEvent) -> None:
        logger.debug(f'wheel {e.angleDelta()}')
        idler_forward = e.angleDelta().y() > 0
        if self.key_control_pressing:
            col_width = self.columnWidth(0)
            col_width += 3 if idler_forward else -3
            t_width = self.width()  # no vertical header
            cols = self.horizontalHeader().count()
            col_width_to = max(col_width, int(t_width / cols))

            logger.debug(self.hcenter_before_wheeling)
            self.horizontalHeader().setDefaultSectionSize(col_width_to)
            self.col_to_center(self.hcenter_before_wheeling)
        else:
            bias = 2 if idler_forward else -2
            mySignals.schedule.emit(-1, bias, -1, MySignals.Emitter.T_WHEEL)

    def slot_ckb_follow(self, state):
        logger.debug('')
        self.b_scroll_follow = state == Qt.Checked

    def slot_cellPressed(self, qindex):
        r, c = qindex.row(), qindex.column()
        logger.debug(f'{r}, {c}, {self.model().item(r, c)}')
        if not self.model().item(r, c):
            item = QStandardItem('')
            item.setBackground(Qt.white)
            self.model().setItem(r, c, item)
        self.entry_cell_pos = (r, c)

    def slot_cellClicked(self, qindex):
        r, c = qindex.row(), qindex.column()
        logger.debug(f'{r}, {c}')
        label = self._detect_label(r, c)
        if label is None:
            self.label_clicked = None
        else:
            self.label_clicked = label
            self.select_label(label)
            mySignals.label_selected.emit(label, MySignals.Emitter.T_LABEL)

    def slot_sliderMoved(self, pos):
        logger.debug(pos)
        index = (self.model().columnCount() - 1) * pos / self.horizontalScrollBar().maximum()
        mySignals.schedule.emit(index, -1, -1, MySignals.Emitter.T_HSCROLL)
        # self.selectColumn(index)  # crash bug

    def set_column_num(self, c):
        self.model().setColumnCount(c)

    @TableDecorators.block_signals
    def slot_follow_to(self, index):
        self.current_column = index
        # if emitter == MySignals.Emitter.T_HSCROLL:
        #     return
        if self.b_scroll_follow:
            self.col_to_center(index)

    @TableDecorators.block_signals
    def slot_label_delete(self, action_labels: typing.List[ActionLabel], emitter):
        logger.debug(f'{action_labels}, {emitter}')
        self.unselect_all()
        for label in action_labels:
            self._del_label(label)

    @TableDecorators.block_signals
    def slot_label_update(self, action_labels: typing.List[ActionLabel], emitter):
        logger.debug(f'{action_labels}, {emitter}')
        self.unselect_all()
        for label in action_labels:
            self._update_label(label)

    def settle_label(self, label: ActionLabel):
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
            warn_ = 'All related rows are already occupied and new ones cannot be placed!'
            logger.warn(warn_)
            CommonUnit.status_prompt(warn_)
            return None
        label.timeline_row = t_r
        if not self._plot_label(label):
            return None
        return t_r

    def _plot_label(self, label: ActionLabel):
        # Log.debug(label)
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
        logger.debug(f'{item.toolTip()}, {item.whatsThis()}, {item.background()}')
        return ActionLabel(item.toolTip(), int(item.whatsThis()), item.background(), l, r, row)

    def select_label(self, label: ActionLabel):
        logger.debug(label)
        logger.debug(QRect(label.begin, label.timeline_row, label.end - label.begin + 1, 1))
        self.selectionModel().select(
            QItemSelection(self.model().index(label.timeline_row, label.begin),
                           self.model().index(label.timeline_row, label.end)),
            QItemSelectionModel.ClearAndSelect)

    def _update_label(self, label: ActionLabel):
        self._plot_label(label)

    def _del_label(self, label: ActionLabel):
        for c in range(label.begin, label.end + 1):
            item = self.model().item(label.timeline_row, c)
            if item is None:
                continue
            item.setBackground(Qt.white)
            item.setWhatsThis(None)
            item.setToolTip(None)

    def _del_selected_label_cells(self):
        logger.info('here')
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
        self.unselect_all()
        return label_cells

    def col_to_center(self, index):
        self.scrollTo(self.model().index(0, max(0, index - 1)), QAbstractItemView.PositionAtCenter)

    def _center_col(self):
        """only supports static case & no vertical header"""
        t_width = self.width()
        return self.columnAt(int(t_width / 2))

    Ui_Dialog, _ = uic.loadUiType("view/ui_from_creator/timelinedialog.ui")

    class TimelineDialog(QDialog, Ui_Dialog):
        def __init__(self, parent=None):
            QDialog.__init__(self, parent, flags=Qt.Dialog)
            self.setupUi(self)
            self.line_begin.setValidator(QIntValidator())
            self.line_end.setValidator(QIntValidator())

            self.cur_frame_index = None
            self.labels_unfinished = []  # type:typing.List

            self.btn_new.clicked.connect(self.slot_btn_new_clicked)

        def load(self, cur_frame_index):
            self.cur_frame_index = cur_frame_index
            self._load_new_comb()
            self._load_unfinished()

        def _load_new_comb(self):
            # created in qt creator IDE
            self.line_begin.setText(str(self.cur_frame_index))
            self.line_end.clear()
            self.combo_action_names.clear()
            self.actions = actions = CommonUnit.get_all_actions()
            if actions:
                _action_names = [a.name for a in actions]
                self.combo_action_names.addItems(_action_names)
                default: Action = next(filter(lambda action: action.default, actions))
                if default:
                    self.combo_action_names.setCurrentIndex(_action_names.index(default.name))

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

            _action_names = [a.name for a in CommonUnit.get_all_actions()]
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
            logger.debug('')
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
            logger.debug('')
            action_name = self.combo_action_names.currentText()
            if not action_name:
                logger.info('Please add action first!')
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
            logger.debug(label)
            if not label.is_valid(['action', 'action_id', 'color', 'begin', 'end']):
                return False
            if self.parent().settle_label(label) is None:
                return False
            mySignals.label_created.emit(label, MySignals.Emitter.T_LABEL)
            return True

        def exec_(self):
            # self.setFixedWidth(self.width())
            # self.setMaximumHeight(self.height())
            return super().exec_()


class TimelineTableModel(QStandardItemModel):
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(section)
        return QVariant()
