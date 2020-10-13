import codecs
import json
import pickle
from typing import Callable

import numpy as np

from PyQt5.QtWidgets import QFileDialog, QComboBox, QLineEdit

from zdl.utils.io.log import logger


class CommonUnit:
    get_default_action: Callable
    get_all_actions: Callable
    status_prompt: Callable
    get_all_labels: Callable

    @classmethod
    def set_mw(cls, mwindow):
        logger.debug('')
        cls.mw = mwindow

        cls.get_default_action = cls.mw.table_action.get_default_action
        cls.get_all_actions = cls.mw.table_action.get_all_actions
        cls.status_prompt = cls.mw.label_note.setText
        cls.get_all_labels = cls.mw.table_labeled.get_all_labels

    @classmethod
    def get_save_name(cls, default=None):
        fd = QFileDialog()
        fd.setAcceptMode(QFileDialog.AcceptSave)
        name = fd.getSaveFileName(cls.mw, 'Save File', default)
        return name[0]

    @classmethod
    def get_open_name(cls, caption="Open File", directory="", filter_="*"):
        name = QFileDialog().getOpenFileName(cls.mw, caption, directory,
                                             filter_, options=QFileDialog.ReadOnly)
        return name[0]

    @classmethod
    def save_dict(cls, content, fname=None, default_fname='xxx.json'):
        if fname is None:
            fname = cls.get_save_name(default=default_fname)
        with codecs.getwriter("utf8")(open(fname, "wb")) as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_dict(cls) -> dict:
        file_name = cls.get_open_name(filter_="(*.json)")
        logger.debug(file_name)
        assert file_name, 'file not selected!'
        with open(file_name, 'r', encoding='utf-8') as f:
            json_content = json.load(f)
        return json_content

    @classmethod
    def save_ndarray(cls, array: np.ndarray, default_fname):
        save_as = cls.get_save_name(default=default_fname)
        if save_as:
            np.save(save_as, array)

    @classmethod
    def save_pkl(cls, pickleable, default_fname):
        save_as = cls.get_save_name(default=default_fname)
        if save_as:
            with open(save_as, 'wb') as f:
                pickle.dump(pickleable, f)

    @classmethod
    def get_value(cls, obj, type_=str):
        if type(obj) in [QComboBox]:
            text = obj.currentText()
        elif type(obj) in [QLineEdit]:
            text = obj.text()
        else:
            raise ValueError('The obj arg is wrong.')
        return type_(text)
