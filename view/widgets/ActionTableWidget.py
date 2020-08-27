from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from common.Log import Log
from model.Action import Action
from presenter.CommonUnit import CommonUnit
from view.widgets.TableViewCommon import TableViewCommon


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

        self.blockSignals(True)
        for i in range(2):
            action = Action(self.generate_id(), f"action{i + 1}",
                            QColor('#fe8a71') if i == 0 else QColor('#0e9aa7'),
                            i == 0)
            self.insert_action(action)
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

        # mySignals.action_update.emit(MySignals.Emitter.T_TEMP)
        # global_.g_all_actions = self.get_all_actions

    def slot_cellDoubleClicked(self, r, c):
        Log.debug(r, c)
        if c == 1:
            item = self.item(r, c)
            color = QColorDialog().getColor(initial=item.background().color())  # type:QColor
            if color.isValid():
                if color == Qt.white:
                    CommonUnit.status_prompt('Cannot set white color to action!')
                    Log.warn('Cannot set white color to action!')
                    return
                item.setBackground(color)

    def get_all_actions(self):
        Log.debug('')
        actions = []
        for r in range(self.rowCount()):
            try:
                actions.append(self._row_to_action(r))
            except AttributeError as e:
                pass
            except Exception as e:
                Log.error(e.__str__())
        return actions

    def get_default_action(self):
        Log.debug('')
        rows = self.rowCount()
        if rows == 0:
            QMessageBox().information(self, 'ActionLabel',
                                      "Please add action first!",
                                      QMessageBox.Ok, QMessageBox.Ok)
            return None

        actions = self.get_all_actions()
        for action in actions:
            if action.default:
                if not action.name:
                    QMessageBox().information(self, 'ActionLabel',
                                              "Please complete action name first!",
                                              QMessageBox.Ok, QMessageBox.Ok)
                    return None
                # 1.return default
                return action
        # 2.select from dialog
        action_name, ok_pressed = QInputDialog().getItem(self, "ActionLabel",
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
        Log.debug(*arg)
