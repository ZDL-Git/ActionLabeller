import os
import time

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from zdl.utils.helper.python import ZDict
from zdl.utils.helper.qt import TableDecorators
from zdl.utils.io.file import FileHelper
from zdl.utils.io.log import logger

from model.ActionLabel import ActionLabel
from model.JsonFileLabels import JsonFileLabels
from presenter import MySignals
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from presenter.PlayingUnit import PlayingUnit


class ActionLabellingUnit:
    def __init__(self, mwindow):
        logger.debug('')
        self.mw = mwindow
        (
            self.mw.table_action.cellChanged.connect(self.slot_sync_action_update),
            self.mw.table_timeline.doubleClicked.connect(self.table_timeline_cell_double_clicked),
        )

        (
            mySignals.labeled_delete.connect(self.mw.table_timeline.slot_label_delete),
        )
        (
            mySignals.label_created.connect(self.mw.table_labeled.slot_label_created),
            mySignals.label_selected.connect(self.mw.table_labeled.slot_label_select),
            mySignals.label_cells_delete.connect(self.mw.table_labeled.slot_label_cells_delete),
        )
        (
            self.mw.btn_new_action.clicked.connect(self.mw.table_action.slot_insert_action),
            self.mw.btn_del_action.clicked.connect(self.slot_del_selected_actions),
            self.mw.btn_export_labeled.clicked.connect(self.slot_export_labeled),
            self.mw.btn_import_labeled.clicked.connect(self.slot_import_labeled, Qt.QueuedConnection),
            self.mw.btn_export_npy_and_label.clicked.connect(self.slot_export_npy_and_label),
        )

        self.mw.table_timeline.get_all_actions = self.mw.table_action.get_all_actions
        self.mw.table_timeline.get_default_action = self.mw.table_action.get_default_action
        self.mw.table_timeline.status_prompt = CommonUnit.status_prompt
        self.mw.table_action.status_prompt = CommonUnit.status_prompt

    def slot_export_labeled(self):
        logger.debug('')
        video_obj = PlayingUnit.only_ins.video_model
        video_info = video_obj and video_obj.get_info()
        video_uri = video_info and video_info['fname']
        video_name = video_uri and os.path.basename(video_uri)
        save_as = CommonUnit.get_save_name(f'{video_name}.json')
        if not save_as:
            return
        pose_obj = PlayingUnit.only_ins.pose_model
        pose_file_uri = pose_obj and pose_obj.file.uri
        pose_file_md5 = pose_file_uri and FileHelper.hashOfFile(pose_file_uri)
        json_file_labels = JsonFileLabels()
        json_file_labels['video_info.uri'] = video_uri
        json_file_labels['video_info.hash_md5'] = video_uri and FileHelper.hashOfFile(video_uri)
        json_file_labels['video_info.w'] = video_info and video_info['width']
        json_file_labels['video_info.h'] = video_info and video_info['height']
        json_file_labels['pose_info.uri'] = pose_file_uri
        json_file_labels['pose_info.hash_md5'] = pose_file_md5
        json_file_labels['labels'] = {i + 1: {'action': label.action,
                                              'begin': label.begin,
                                              'end': label.end,
                                              'pose_index': label.pose_index, }
                                      for i, label in enumerate(self.mw.table_labeled.get_all_labels())}
        json_file_labels.dump(save_as)

    def slot_import_labeled(self):
        logger.debug('')
        json_file_labels = JsonFileLabels.load(CommonUnit.get_open_name())
        existed_actions = {action.name: action for action in self.mw.table_action.get_all_actions()}
        for i, label in json_file_labels['labels'].items():
            action_name, begin, end, pose_index = ZDict(label)['action', 'begin', 'end', ('pose_index', -1)]
            if action_name not in existed_actions:
                action = self.mw.table_action.slot_insert_action(action_name)
                existed_actions[action_name] = action
            else:
                action = existed_actions[action_name]
            action_label = ActionLabel(action.name, action.id, action.color, begin, end, None, pose_index)
            logger.debug(action_label)
            self.mw.table_timeline.settle_label(action_label)
            self.mw.table_labeled.add_label(action_label)

    def slot_export_npy_and_label(self):
        poses = PlayingUnit.only_ins.pose_model._fdata
        logger.debug(list(poses.keys()))
        labels = self.mw.table_labeled.get_all_labels()
        labels = [l for l in labels if l.pose_index != -1]
        logger.debug(len(labels))
        npy = []
        label_len_max = 0
        for label in labels:
            one_action_pose = []
            label_len_max = max(label_len_max, label.end - label.begin + 1)
            for frame_index in range(label.begin, label.end + 1):
                one_action_pose.append(np.asarray(poses[str(frame_index)][int(label.pose_index)]))
            npy.append(np.asarray(one_action_pose))
        logger.debug([len(o_a_p) for o_a_p in npy])
        logger.debug(label_len_max)
        for one_action_pose in npy:
            one_action_pose.resize((label_len_max, *one_action_pose.shape[1:]), refcheck=False)
        npy = np.asarray(npy)
        npy = np.expand_dims(npy, axis=1)
        npy = np.repeat(npy, 3, axis=1)
        logger.info(npy.shape)
        time_stamp = int(time.time())
        CommonUnit.save_ndarray(npy, f'train_data_{time_stamp}.npy')
        CommonUnit.save_pkl(([f'name{i}' for i in range(len(npy))], [l.action_id for l in labels]),
                            f'train_label_{time_stamp}.pkl')

    @TableDecorators.dissort(table_lambda=lambda self: self.mw.table_labeled)
    @TableDecorators.dissort(table_lambda=lambda self: self.mw.table_timeline, resume_sortable=False)
    def slot_sync_action_update(self, r=None, c=None):
        logger.debug(f'{r} {c}')
        action_dict = {a.id: a for a in self.mw.table_action.get_all_actions()}
        table_labeled, table_timeline = self.mw.table_labeled, self.mw.table_timeline
        for r in reversed(range(table_labeled.rowCount())):
            label = table_labeled.label_at(r)
            id_ = label.action_id
            if id_ in action_dict:
                # update label
                action = action_dict[id_]
                label.action = action.name
                label.color = action.color
                table_labeled.slot_label_action_info_update_by_row(r, action, MySignals.Emitter.T_ACTION)
                table_timeline.slot_label_update([label], MySignals.Emitter.T_ACTION)
            else:
                # delete label
                table_labeled.slot_label_delete(label, MySignals.Emitter.T_ACTION)
                table_timeline.slot_label_delete([label], MySignals.Emitter.T_ACTION)

    # if use decorator, must receive checked param of button clicked event
    def slot_del_selected_actions(self, checked):
        logger.debug('')
        if not self.mw.table_action.selectedIndexes():
            QMessageBox().information(self.mw, 'ActionLabeller Warning',
                                      "Select action first!",
                                      QMessageBox.Ok, QMessageBox.Ok)
            return
        if self.mw.table_labeled.rowCount():
            if QMessageBox.Cancel == QMessageBox().warning(self.mw, 'ActionLabeller Warning',
                                                           "All you sure to delete action template?"
                                                           " All the related action labels will be deleted!",
                                                           QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel):
                return
        self.mw.table_action.slot_delete_selected()
        self.slot_sync_action_update()

    def table_timeline_cell_double_clicked(self, qindex):
        logger.debug('')
        r, c = qindex.row(), qindex.column()
        label = self.mw.table_timeline.detect_label(r, c)  # type:ActionLabel
        if not label:
            self.mw.table_timeline.col_to_center(self.mw.table_timeline.current_column)
            CommonUnit.status_prompt(str(f'Current Frame {self.mw.table_timeline.current_column}'))
            self.mw.table_timeline.label_create_dialog.load(self.mw.table_timeline.current_column)
            self.mw.table_timeline.label_create_dialog.exec_()
