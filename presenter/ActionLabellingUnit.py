import json
import os
import time

from PyQt5.QtCore import QRandomGenerator
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
from zdl.utils.io.file import hashOfFile
from zdl.utils.io.log import logger

from model.Action import Action
from model.ActionLabel import ActionLabel
from presenter import MySignals
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from presenter.PlayingUnit import PlayingUnit


class ActionLabellingUnit:
    def __init__(self, mwindow):
        logger.debug('')
        self.mw = mwindow
        (
            self.mw.table_action.cellChanged.connect(self.slot_action_update),
            self.mw.table_timeline.doubleClicked.connect(self.table_timeline_cell_double_clicked),
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
        logger.debug('')
        labels = self.mw.table_labeled.get_all_labels()
        video_obj = PlayingUnit.only_ins.media_model
        video_info = video_obj and video_obj.get_info()
        video_uri = video_info and video_info['fname']
        video_name = video_uri and os.path.basename(video_uri)
        md5 = video_uri and hashOfFile(video_uri)
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
                                         'end': label.end,
                                         'pose_index': label.pose_index, }
        logger.debug(json_content['video_info'])
        CommonUnit.save_dict(json_content, default_fname=f'{video_name}.json')

    def slot_import_labeled(self):
        logger.debug('')
        json_content = CommonUnit.load_dict()
        all_actions = {}
        for i in json_content['labels']:
            action_name = json_content['labels'][i]['action']
            begin = json_content['labels'][i]['begin']
            end = json_content['labels'][i]['end']
            pose_index = json_content['labels'][i].get('pose_index', -1)
            if action_name not in all_actions:
                action = Action(self.mw.table_action.generate_id(), action_name,
                                QColor(QRandomGenerator().global_().generate()), False)
                self.mw.table_action.insert_action(action)
                all_actions[action_name] = action
            else:
                action = all_actions[action_name]
            action_label = ActionLabel(action.name, action.id, action.color, begin, end, None, pose_index)
            logger.debug(action_label)
            self.mw.table_timeline.settle_label(action_label)
            self.mw.table_labeled.add_label(action_label)

    def slot_action_add(self, checked):  # if use decorator, must receive checked param of button clicked event
        logger.debug('')
        action = Action(self.mw.table_action.generate_id(), '', QColor(QRandomGenerator().global_().generate()), False)
        self.mw.table_action.insert_action(action)
        self.mw.table_action.editItem(self.mw.table_action.item(self.mw.table_action.rowCount() - 1, 0))

    def slot_action_update(self, r, c):
        logger.debug('')
        labels_updated = self.mw.table_labeled.action_update()
        if labels_updated:
            self.mw.table_timeline.slot_label_update(labels_updated, MySignals.Emitter.T_LABELED)

    def slot_del_selected_actions(self,
                                  checked):  # if use decorator, must receive checked param of button clicked event
        logger.debug('')
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

    def table_timeline_cell_double_clicked(self, qindex):
        logger.debug('')
        r, c = qindex.row(), qindex.column()
        label = self.mw.table_timeline._detect_label(r, c)  # type:ActionLabel
        if not label:
            self.mw.table_timeline.col_to_center(self.mw.table_timeline.current_column)
            CommonUnit.status_prompt(str(f'Current Frame {self.mw.table_timeline.current_column}'))
            self.mw.table_timeline.label_create_dialog.load(self.mw.table_timeline.current_column)
            self.mw.table_timeline.label_create_dialog.exec_()
