from functools import partial
from typing import Union

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from zdl.utils.helper.qt import TableDecorators
from zdl.utils.io.log import logger

from model.Action import Action
from presenter.CommonUnit import CommonUnit
from view.widgets.TableHelpers import TableViewExtended, EnumColsHelper, RowHelper


class ActionTableWidget(QTableWidget, TableViewExtended):
    def __init__(self, parent):
        super().__init__()

        self.RowAction = partial(self._Row, table=self)

        self.cellChanged.connect(self.slot_cellChanged)
        self.cellDoubleClicked.connect(self.slot_cellDoubleClicked)

    def __init_later__(self):
        self.Cols.to_table(self)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.blockSignals(True)
        for i in range(2):
            action = Action(self.generate_id(), f"action{i + 1}",
                            QColor('#fcba03') if i == 0 else QColor('#83bdc9'),
                            i == 0)
            self.RowAction(action)
        self.blockSignals(False)

    def slot_cellChanged(self, r, c):
        logger.debug(f'{r}, {c}')
        row_action = self.RowAction(r)
        if c == self.Cols.default.value.index:
            if row_action.default():
                self._unselect_others(except_=r)

        # mySignals.action_update.emit(MySignals.Emitter.T_TEMP)
        # global_.g_all_actions = self.get_all_actions

    def slot_cellDoubleClicked(self, r, c):
        logger.debug(f'{r}, {c}')
        if c == self.Cols.color.value.index:
            row_action = self.RowAction(r)
            color = QColorDialog().getColor(initial=QColor(row_action.color()))  # type:QColor
            if color.isValid():
                if color == Qt.white:
                    CommonUnit.status_prompt('Cannot set white color to action!')
                    logger.warn('Cannot set white color to action!')
                    return
                row_action.set_color(color)

    def slot_delete_selected(self):
        logger.debug('')
        self._delete_selected_rows()

    def get_all_actions(self):
        logger.debug('')
        actions = []
        for r in range(self.rowCount()):
            try:
                actions.append(self.RowAction(r).to_action())
            except AttributeError as e:
                pass
            except Exception as e:
                logger.error(e.__str__())
        return actions

    def get_default_action(self):
        logger.debug('')
        rows = self.rowCount()
        if rows == 0:
            QMessageBox().information(self, 'ActionLabeller',
                                      "Please add action first!",
                                      QMessageBox.Ok, QMessageBox.Ok)
            return None

        actions = self.get_all_actions()
        for action in actions:
            if action.default:
                return action
        # 2.select from dialog
        action_name, ok_pressed = QInputDialog().getItem(self, "ActionLabeller",
                                                         "Select or check as default in Action Setting:",
                                                         [a.name for a in actions], 0,
                                                         False)
        if ok_pressed and action_name:
            return list(filter(lambda a: a.name == action_name, actions))[0]

        return None

    def generate_id(self):
        actions = self.get_all_actions()
        if actions:
            return max([action.id for action in actions]) + 1
        return 0

    def slot_insert_action(self, action: Action):
        self.RowAction(action)

    def _unselect_others(self, except_):
        for r in range(self.rowCount()):
            if r == except_:
                continue
            self.RowAction(r).set_default(False)

    def slot_test(self, *arg):
        logger.debug(*arg)

    class Cols(EnumColsHelper):
        id = EnumColsHelper.Col()(0, int, 'Action Id', False, True, True, False)
        name = EnumColsHelper.Col()(1, str, 'Action Name', True, True, False, True)
        color = EnumColsHelper.Col()(2, QColor, 'Label Color', False, False, False, True)
        default = EnumColsHelper.Col()(3, bool, 'Default', False, True, False, True)
        xml_ymin = EnumColsHelper.Col()(4, int, 'Y-min', True, True, True, False)
        xml_ymax = EnumColsHelper.Col()(5, int, 'Y-max', True, True, True, False)

    class _Row(RowHelper):

        def __init__(self, row_num_or_action: Union[int, Action], table: 'ActionTableWidget'):
            self.table = table

            self.id: callable = partial(self._col_value, col=self.table.Cols.id)
            self.name: callable = partial(self._col_value, col=self.table.Cols.name)
            self.color: callable = partial(self._col_value, col=self.table.Cols.color)
            self.default: callable = partial(self._col_value, col=self.table.Cols.default)
            self.xml_ymin: callable = partial(self._col_value, col=self.table.Cols.xml_ymin)
            self.xml_ymax: callable = partial(self._col_value, col=self.table.Cols.xml_ymax)

            self.set_id: callable = partial(self._set_col_value, col=self.table.Cols.id)
            self.set_name: callable = partial(self._set_col_value, col=self.table.Cols.name)
            self.set_color: callable = partial(self._set_col_value, col=self.table.Cols.color)
            self.set_default: callable = partial(self._set_col_value, col=self.table.Cols.default)
            self.set_xml_ymin: callable = partial(self._set_col_value, col=self.table.Cols.xml_ymin)
            self.set_xml_ymax: callable = partial(self._set_col_value, col=self.table.Cols.xml_ymax)

            if isinstance(row_num_or_action, int):
                self.row_num = row_num_or_action
            elif isinstance(row_num_or_action, Action):
                self.row_num = self.table.rowCount()
                self._insert(row_num_or_action)
            else:
                raise TypeError

        @TableDecorators.dissort(table_lambda=lambda self: self.table)
        def _insert(self, action: Action):
            self.table.insertRow(self.row_num)
            self.set_id(action.id) \
                .set_name(action.name) \
                .set_color(action.color) \
                .set_default(action.default) \
                .set_xml_ymin(action.xml_ymin) \
                .set_xml_ymax(action.xml_ymax)

        def to_action(self) -> Action:
            action = Action(self.id(),
                            self.name(),
                            self.color(),
                            self.default(),
                            self.xml_ymin(),
                            self.xml_ymax())
            return action
