from collections import namedtuple
from enum import Enum
from functools import partial
from typing import Union

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from zdl.utils.helper.python import except_as_None
from zdl.utils.helper.qt import TableDecorators
from zdl.utils.io.log import logger

from model.Action import Action
from presenter.CommonUnit import CommonUnit
from view.widgets.TableHelpers import TableViewExtended, EnumColsHelper, RowHelper


class ActionTableWidget(QTableWidget, TableViewExtended):
    def __init__(self, parent):
        super().__init__()
        # TODO
        self.header_labels = {''}

        self.cellChanged.connect(self.slot_cellChanged)
        self.cellDoubleClicked.connect(self.slot_cellDoubleClicked)

    def __init_later__(self):
        self._Cols.to_table(self)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.blockSignals(True)
        for i in range(2):
            action = Action(self.generate_id(), f"action{i + 1}",
                            QColor('#fcba03') if i == 0 else QColor('#83bdc9'),
                            i == 0)
            self.insert_action(action)
        self.blockSignals(False)

    def slot_cellChanged(self, r, c):
        logger.debug(f'{r}, {c}')
        if c == 2:
            if self.item(r, c).checkState() == Qt.Checked:
                self._unselect_others(except_=r)
            elif self.item(r, c).checkState() == Qt.Unchecked:
                pass
        elif c == 0:
            pass

        # mySignals.action_update.emit(MySignals.Emitter.T_TEMP)
        # global_.g_all_actions = self.get_all_actions

    def slot_cellDoubleClicked(self, r, c):
        logger.debug(f'{r}, {c}')
        if c == 1:
            item = self.item(r, c)
            color = QColorDialog().getColor(initial=item.background().color())  # type:QColor
            if color.isValid():
                if color == Qt.white:
                    CommonUnit.status_prompt('Cannot set white color to action!')
                    logger.warn('Cannot set white color to action!')
                    return
                item.setBackground(color)

    def slot_delete_selected(self):
        logger.debug('')
        self._delete_selected_rows()

    def get_all_actions(self):
        logger.debug('')
        actions = []
        for r in range(self.rowCount()):
            try:
                actions.append(self._row_to_action(r))
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

    def insert_action(self, action: Action):
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

    def del_action(self, id):
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
        logger.debug(*arg)

    class _Cols(EnumColsHelper):
        id = EnumColsHelper.Col()(0, int, 'Action Id', False, False, False)
        name = EnumColsHelper.Col()(1, str, 'Action Name', False, True, True)
        color = EnumColsHelper.Col()(2, QColor, 'Label Color', False, True, True)
        default = EnumColsHelper.Col()(3, bool, 'Default', False, True, True)
        xml_ymin = EnumColsHelper.Col()(4, int, 'Y-min', False, False, False)
        xml_ymax = EnumColsHelper.Col()(5, int, 'Y-max', True, True, False)

    class _Row(RowHelper):

        def __init__(self, row_num_or_actionlabel: Union[int, Action], table: 'ActionTableWidget'):
            super().__init__(table)

            self.id: callable = partial(self._col_value, col=self.table._Cols.id)
            self.name: callable = partial(self._col_value, col=self.table._Cols.name)
            self.color: callable = partial(self._col_value, col=self.table._Cols.color)
            self.default: callable = partial(self._col_value, col=self.table._Cols.default)
            self.xml_ymin: callable = partial(self._col_value, col=self.table._Cols.xml_ymin)
            self.xml_ymax: callable = partial(self._col_value, col=self.table._Cols.xml_ymax)

            self.set_id: callable = partial(self._set_col_value, col=self.table._Cols.id)
            self.set_name: callable = partial(self._set_col_value, col=self.table._Cols.name)
            self.set_color: callable = partial(self._set_col_value, col=self.table._Cols.color)
            self.set_default: callable = partial(self._set_col_value, col=self.table._Cols.default)
            self.set_xml_ymin: callable = partial(self._set_col_value, col=self.table._Cols.xml_ymin)
            self.set_xml_ymax: callable = partial(self._set_col_value, col=self.table._Cols.xml_ymax)

            if isinstance(row_num_or_actionlabel, int):
                self.row_num = row_num_or_actionlabel
            elif isinstance(row_num_or_actionlabel, Action):
                self.row_num = self.table.rowCount()
                self._insert(row_num_or_actionlabel)
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
            label = Action(self.id(),
                           self.name(),
                           self.color(),
                           self.default(),
                           self.xml_ymin(),
                           self.xml_ymax())
            return label
