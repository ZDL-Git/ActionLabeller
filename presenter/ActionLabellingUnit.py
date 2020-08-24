import json
import os
import time

from common.utils import Log, hash_of_file
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from presenter.VideoPlayingUnit import VideoPlayingUnit


class ActionLabellingUnit:
    def __init__(self, mwindow):
        Log.debug('')
        self.mw = mwindow

        (
            mySignals.follow_to.connect(self.mw.table_timeline.slot_follow_to),
            mySignals.labeled_selected.connect(self.mw.table_timeline.slot_label_play),
            mySignals.labeled_update.connect(self.mw.table_timeline.slot_label_update),
            mySignals.labeled_delete.connect(self.mw.table_timeline.slot_label_delete),
        )
        (
            mySignals.label_created.connect(self.mw.table_labeled.slot_label_created),
            mySignals.label_selected.connect(self.mw.table_labeled.slot_label_selected),
            mySignals.label_delete.connect(self.mw.table_labeled.slot_label_delete),
            mySignals.label_cells_delete.connect(self.mw.table_labeled.slot_label_cells_delete),
            mySignals.action_update.connect(self.mw.table_labeled.slot_action_update),
        )
        (
            self.mw.btn_export_labeled.clicked.connect(self.slot_export_labeled),
            self.mw.btn_import_labeled.clicked.connect(self.slot_import_labeled),
        )

    def slot_export_labeled(self):
        Log.debug('')
        labels = self.mw.table_labeled.get_all_labels()
        video_obj = VideoPlayingUnit.only_ins.video_model
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
        save_as = CommonUnit.get_save_name(default='xxx.json')
        if save_as:
            with open(save_as, "w") as f:
                json.dump(json_content, f, indent=2, ensure_ascii=False)

    def slot_import_labeled(self):
        Log.debug('')
