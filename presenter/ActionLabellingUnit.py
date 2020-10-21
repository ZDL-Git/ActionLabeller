import os
import time

import numpy as np
from PyQt5.QtCore import QRandomGenerator, Qt
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
            self.mw.table_action.cellChanged.connect(self.slot_sync_action_update),
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
            mySignals.label_selected.connect(self.mw.table_labeled.slot_label_select),
            mySignals.label_delete.connect(self.mw.table_labeled.slot_label_delete),
            mySignals.label_cells_delete.connect(self.mw.table_labeled.slot_label_cells_delete),
            # mySignals.action_update.connect(self.mw.table_labeled.slot_action_update),
        )
        (
            self.mw.btn_new_action.clicked.connect(self.mw.table_action.slot_insert_action),
            self.mw.btn_del_action.clicked.connect(self.slot_del_selected_actions),
            self.mw.btn_export_labeled.clicked.connect(self.slot_export_labeled),
            self.mw.btn_import_labeled.clicked.connect(self.slot_import_labeled, Qt.QueuedConnection),
            self.mw.btn_export_npy_and_label.clicked.connect(self.slot_export_npy_and_label),
        )

    def slot_export_labeled(self):
        logger.debug('')
        video_obj = PlayingUnit.only_ins.video_model
        video_info = video_obj and video_obj.get_info()
        video_uri = video_info and video_info['fname']
        video_name = video_uri and os.path.basename(video_uri)
        save_as = CommonUnit.get_save_name(f'{video_name}.json')
        if not save_as:
            return
        md5 = video_uri and hashOfFile(video_uri)
        h = video_info and video_info['height']
        w = video_info and video_info['width']
        json_content = {
            'video_info': {
                'name': video_name,
                'uri': video_uri,
                'hash_md5': md5,
                'h': h,
                'w': w,
            },
            'timestamp': time.ctime(),
            'labels': dict()
        }
        labels = self.mw.table_labeled.get_all_labels()
        for i, label in enumerate(labels):
            json_content['labels'][i] = {'action': label.action,
                                         'begin': label.begin,
                                         'end': label.end,
                                         'pose_index': label.pose_index, }
        logger.debug(json_content)
        CommonUnit.save_dict(json_content, fname=save_as)

    def slot_import_labeled(self):
        logger.debug('')
        CommonUnit.status_prompt('Importing labels...')
        json_content = CommonUnit.load_dict()
        all_actions = {action.name: action for action in CommonUnit.get_all_actions()}
        for i in json_content['labels']:
            action_name = json_content['labels'][i]['action']
            begin = json_content['labels'][i]['begin']
            end = json_content['labels'][i]['end']
            pose_index = json_content['labels'][i].get('pose_index', -1)
            if action_name not in all_actions:
                action = Action(self.mw.table_action.generate_id(), action_name,
                                QColor(QRandomGenerator().global_().generate()), False)
                self.mw.table_action.slot_insert_action(action)
                all_actions[action_name] = action
            else:
                action = all_actions[action_name]
            action_label = ActionLabel(action.name, action.id, action.color, begin, end, None, pose_index)
            logger.debug(action_label)
            self.mw.table_timeline.settle_label(action_label)
            self.mw.table_labeled.add_label(action_label)
        CommonUnit.status_prompt('Importing finished.')

    def slot_export_npy_and_label(self):
        poses = PlayingUnit.only_ins.pose_model._fdata
        logger.debug(list(poses.keys()))
        labels = self.mw.table_labeled.get_all_labels()
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
        CommonUnit.save_pkl(([f'name{i}' for i in range(len(npy))], [l.action for l in labels]),
                            f'train_label_{time_stamp}.pkl')

    def slot_sync_action_update(self):
        logger.debug('')
        actions = CommonUnit.get_all_actions()
        action_dict = {a.id: a for a in actions}
        table_labeled = self.mw.table_labeled
        table_timeline = self.mw.table_timeline
        table_labeled.setSortingEnabled(False)
        table_timeline.setSortingEnabled(False)
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
        table_labeled.setSortingEnabled(True)
        table_timeline.setSortingEnabled(True)

    def slot_del_selected_actions(self,
                                  checked):  # if use decorator, must receive checked param of button clicked event
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
        # mySignals.action_update.emit(MySignals.Emitter.T_TEMP)

    def table_timeline_cell_double_clicked(self, qindex):
        logger.debug('')
        r, c = qindex.row(), qindex.column()
        label = self.mw.table_timeline._detect_label(r, c)  # type:ActionLabel
        if not label:
            self.mw.table_timeline.col_to_center(self.mw.table_timeline.current_column)
            CommonUnit.status_prompt(str(f'Current Frame {self.mw.table_timeline.current_column}'))
            self.mw.table_timeline.label_create_dialog.load(self.mw.table_timeline.current_column)
            self.mw.table_timeline.label_create_dialog.exec_()
