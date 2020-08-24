from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QColor
from PyQt5.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, \
    QHeaderView

from common.utils import Log
from presenter import MySignals
from presenter.ActionLabellingUnit import ActionLabellingUnit
from presenter.CommonUnit import CommonUnit
from presenter.MySignals import mySignals
from presenter.Settings import Settings
from presenter.VideoPlayingUnit import VideoPlayingUnit
from presenter.XmlSettingUnit import XmlSettingUnit

Ui_MainWindow, QtBaseClass = uic.loadUiType("view/ui_from_creator/mainwindow.ui")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self, flags=Qt.Window)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.combo_speed.addItems(['0.25', '0.5', '0.75', '1', '1.25', '1.5', '1.75'])
        self.combo_speed.setCurrentIndex(3)
        self.combo_sortby.addItems(['timestamp', 'filename'])
        self.combo_sortby.setCurrentIndex(1)
        # self.line_xml_file_parttern.setText('action_{begin index}-{end index}.xml')

        self.label_show.installEventFilter(self)

        def init_buttons():
            self.btn_open_video.setFocus()
            self.btn_play.clicked.connect(mySignals.video_pause_or_resume.emit)
            self.btn_eval.clicked.connect(self.slot_eval)
            self.btn_new_action.clicked.connect(self.table_action.slot_action_add)
            self.btn_del_action.clicked.connect(self.table_action.slot_del_selected_actions)

        def init_settings():
            Settings.v_interval = int(self.spin_interval.text())
            # global_.Settings.v_speed = float(self.combo_speed.currentText())

        def prettify():
            shadowEffect = QGraphicsDropShadowEffect()
            shadowEffect.setColor(QColor(0, 0, 0, 255 * 0.9))
            shadowEffect.setOffset(0)
            shadowEffect.setBlurRadius(8)
            self.label_show.setGraphicsEffect(shadowEffect)
            self.label_note.setGraphicsEffect(shadowEffect)

            vheader = self.table_timeline.verticalHeader()
            vheader.setDefaultSectionSize(5)
            vheader.sectionResizeMode(QHeaderView.Fixed)

        init_buttons()
        init_settings()
        prettify()

        self.table_timeline.__init_later__()
        self.table_labeled.__init_later__()
        self.table_action.__init_later__()
        self.table_xml_setting.__init_later__(self.table_action.model())

        CommonUnit.set_mw(self)
        # Hold to avoid being destroyed
        self._holder1 = XmlSettingUnit(self)
        self._holder2 = VideoPlayingUnit(self)
        self._holder3 = ActionLabellingUnit(self)

    def common_slot(self, *arg):
        Log.debug(f'common slot print:', arg)

    def slot_interval_changed(self):
        Settings.v_interval = int(self.spin_interval.text() or 1)

    def slot_speed_changed(self):
        Log.debug('')
        new_speed = 1000 / self.label_show.video_model.get_info()['fps'] / float(self.combo_speed.currentText())
        mySignals.timer_video.setInterval(new_speed)

    def slot_input_jumpto_changed(self, text):
        try:
            jumpto = int(text)
            mySignals.schedule.emit(jumpto, -1, -1, MySignals.Emitter.INPUT_JUMPTO)
        except Exception:
            Log.warn('Only int number supported!')

    def slot_follow_to(self, emitter, to):
        CommonUnit.status_prompt(f'Frame {to}')

    def eventFilter(self, source, event):
        # if event.type() == 12:  # paint
        #     return False
        return False

    def closeEvent(self, e: QCloseEvent):
        Log.debug('')
        # TODO: uncomment this block
        # if QMessageBox.Ok != QMessageBox.information(self, 'ActionLabel',
        #                                              "Are you sure to quit, the unsaved labels will be lost?",
        #                                              QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel):
        #     e.ignore()
        Log.debug('Main window closed.')

    # def resizeEvent(self, e):
    #     pass
    #     Log.warn(self.table_timeline.width())
    #     super(MyApp, self).resizeEvent(e)

    def slot_eval(self):
        eval_content = self.ptext_eval_in.toPlainText()
        Log.info(eval_content)
        try:
            resp = eval(eval_content)
        except Exception as e:
            resp = e.__str__()
        self.textb_eval_out.setText(str(resp))
