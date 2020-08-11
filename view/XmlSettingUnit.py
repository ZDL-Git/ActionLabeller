from typing import List, Dict

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QGridLayout, QTextBrowser, QDialog

import global_
from action import Action, ActionLabel
from utils.utils import Log


class XmlSettingUnit:
    def __init__(self, mwindow):
        Log.debug('')
        self.mw = mwindow
        # Log.debug(self.parent())
        self.mw.btn_export_xml.clicked.connect(self.slot_export_xml)
        self.mw.btn_xml_template.clicked.connect(self.slot_xml_template)

    def slot_export_xml(self):
        Log.debug('')
        labels = global_.g_all_labels()  # type:List[ActionLabel]
        labels.sort(key=lambda l: l.begin)
        actions = global_.g_all_actions()  # type:List[Action]
        id_action_dict = {a.id: a for a in actions}  # type:Dict[int,Action]
        framespan = int(self.mw.line_framespan.text())
        overlap = int(self.mw.line_overlap.text())
        Log.debug(framespan, overlap, labels)

        anno = xml_.AnnotationXml()
        file_num = 0
        abandoned = []
        while labels:
            trans = overlap * (0 if file_num == 0 else -1)
            range_ = (file_num * framespan + trans + 1, (file_num + 1) * framespan + trans)
            anno.new_file(f'runtime/xmldemo_{range_}.xml')
            anno.set_tag('folder', 'runtime')
            anno.set_tag('filename', f'runtime/xmldemo_{range_}.png')
            anno.set_tag('width', framespan)
            anno.set_tag('height', 200)
            anno.set_tag('depth', 100)
            cursor = 0
            while labels:
                if labels[cursor].begin >= range_[0] and labels[cursor].end <= range_[1]:
                    label = labels.pop(cursor)
                    action = id_action_dict[label.action_id]
                    anno.append_action(label.action, label.begin, label.end, action.xml_ymin, action.xml_ymax)
                elif labels[cursor].begin < range_[0]:
                    abandoned.append(labels.pop(cursor))
                elif labels[cursor].begin > range_[1]:
                    break
                else:
                    cursor += 1
            anno.dump()
            file_num += 1
        Log.info('labels abandoned:', abandoned)

    def slot_xml_template(self):
        Log.debug('')
        layout = QGridLayout()
        layout.addWidget(QTextBrowser())
        layout.setContentsMargins(2, 2, 2, 2)
        dialog = QDialog(self.mw, flags=Qt.Dialog)
        dialog.setFixedSize(QSize(400, 300))
        dialog.setLayout(layout)
        dialog.setContentsMargins(2, 2, 2, 2)
        dialog.exec_()
