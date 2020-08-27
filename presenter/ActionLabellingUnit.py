import json
import os
import time

from PyQt5.QtCore import QRandomGenerator
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox

from common.Log import Log
from common.utils import hash_of_file
from model.Action import Action
from model.ActionLabel import ActionLabel
from presenter import MySignals
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from presenter.PlayingUnit import PlayingUnit


class ActionLabellingUnit:
    def __init__(self, mwindow):
        Log.debug('')
        self.mw = mwindow
        (
            self.mw.table_action.cellChanged.connect(self.mw.table_labeled.slot_action_update),
        )

        (
            mySignals.follow_to.connect(self.mw.table_timeline.slot_follow_to),
            # mySignals.labeled_selected.connect(self.mw.table_timeline.slot_label_play),
            mySignals.labeled_update.connect(self.mw.table_timeline.slot_label_update),
            mySignals.labeled_delete.connect(self.mw.table_timeline.slot_label_delete),
        )
        (
            mySignals.label_created.connect(self.mw.table_labeled.slot_label_created),
            mySignals.label_selected.connect(self.mw.table_labeled.slot_label_selected),
            mySignals.label_delete.connect(self.mw.table_labeled.slot_label_delete),
            mySignals.label_cells_delete.connect(self.mw.table_labeled.slot_label_cells_delete),
            # mySignals.action_update.connect(self.mw.table_labeled.slot_action_update),
        )
        (
            self.mw.btn_new_action.clicked.connect(self.slot_action_add),
            self.mw.btn_del_action.clicked.connect(self.slot_del_selected_actions),
            self.mw.btn_export_labeled.clicked.connect(self.slot_export_labeled),
            self.mw.btn_import_labeled.clicked.connect(self.slot_import_labeled),
        )

    def slot_export_labeled(self):
        Log.debug('')
        labels = self.mw.table_labeled.get_all_labels()
        video_obj = PlayingUnit.only_ins.media_model
        video_info = video_obj and video_obj.get_info()
        video_uri = video_info and video_info['fname']
        video_name = video_uri and os.path.basename(video_uri)
        md5 = video_uri and hash_of_file(video_uri)
        h = video_info and video_info['height']
        w = video_info and video_info['width']
        json_content = {
            'video_info': {
                'name': video_name,
                'url': video_uri,
                'hash_md5': md5,
                'h': h,
                'w': w,
            },
            'timestamp': time.ctime(),
            'labels': dict()
        }
        for i, label in enumerate(labels):
            json_content['labels'][i] = {'action': label.action,
                                         'begin': label.begin,
                                         'end': label.end, }
        save_as = CommonUnit.get_save_name(default=f'{video_name}.json')
        if save_as:
            with open(save_as, "w") as f:
                json.dump(json_content, f, indent=2, ensure_ascii=False)

    def slot_import_labeled(self):
        Log.debug('')
        file_name = CommonUnit.get_open_name(filter_="(*.json)")
        Log.debug(file_name)
        if file_name == '':
            return
        with open(file_name, 'r') as f:
            json_content = json.load(f)

        all_actions = {}
        for i in json_content['labels']:
            action_name = json_content['labels'][i]['action']
            begin = json_content['labels'][i]['begin']
            end = json_content['labels'][i]['end']
            if action_name not in all_actions:
                action = Action(self.mw.table_action.generate_id(), action_name,
                                QColor(QRandomGenerator().global_().generate()), False)
                self.mw.table_action.insert_action(action)
                all_actions[action_name] = action
            else:
                action = all_actions[action_name]
            action_label = ActionLabel(action.name, action.id, action.color, begin, end, None)
            self.mw.table_timeline.settle_label(action_label)
            self.mw.table_labeled.add_label(action_label)

    def slot_action_add(self, checked):  # if use decorator, must receive checked param of button clicked event
        Log.debug('')
        action = Action(self.mw.table_action.generate_id(), '', QColor(QRandomGenerator().global_().generate()), False)
        self.mw.table_action.insert_action(action)
        self.mw.table_action.editItem(self.mw.table_action.item(self.mw.table_action.rowCount() - 1, 0))

    def slot_del_selected_actions(self,
                                  checked):  # if use decorator, must receive checked param of button clicked event
        Log.debug('')
        if not self.mw.table_action.selectedIndexes():
            QMessageBox().information(self.mw, 'ActionLabel Warning',
                                      "Select action first!",
                                      QMessageBox.Ok, QMessageBox.Ok)
            return
        if self.mw.table_labeled.rowCount():
            if QMessageBox.Cancel == QMessageBox().warning(self.mw, 'ActionLabel Warning',
                                                           "All you sure to delete action template?"
                                                           " All the related action labels will be deleted!",
                                                           QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel):
                return
        rows = set()
        for index in self.mw.table_action.selectedIndexes():
            rows.add(index.row())
        for r in sorted(rows, reverse=True):
            self.mw.table_action.removeRow(r)
        mySignals.action_update.emit(MySignals.Emitter.T_TEMP)
