from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QColor, QDoubleValidator
from PyQt5.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, \
    QHeaderView, QComboBox
from zdl.utils.io.log import logger

from presenter.ActionLabellingUnit import ActionLabellingUnit
from presenter.ApplicationUnit import ApplicationUnit
from presenter.CommonUnit import CommonUnit
from presenter.PlayingUnit import PlayingUnit
from presenter.Settings import Settings
from presenter.XmlSettingUnit import XmlSettingUnit

Ui_MainWindow, QtBaseClass = uic.loadUiType("view/ui_from_creator/mainwindow.ui")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self, flags=Qt.Window)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        double_validator = QDoubleValidator()

        self.combo_speed: QComboBox
        self.combo_speed.setEditable(True)
        self.combo_speed.lineEdit().setValidator(double_validator)
        self.combo_speed.addItems(['0.25', '0.5', '0.75', '1.0', '1.25', '1.5', '1.75'])
        self.combo_speed.setCurrentIndex(3)
        self.combo_sortby.addItems(['filename', 'timestamp'])
        self.combo_sortby.setCurrentIndex(0)
        # self.line_xml_file_parttern.setText('action_{begin index}-{end index}.xml')

        self.label_show.installEventFilter(self)

        def init_buttons():
            self.btn_open_video.setFocus()
            self.btn_eval.clicked.connect(self.slot_eval)

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
        self._holder0 = ApplicationUnit(self)
        self._holder1 = XmlSettingUnit(self)
        self._holder2 = PlayingUnit(self)
        self._holder3 = ActionLabellingUnit(self)
        # self._holder4 = PosePlottingUnit(self)

    def common_slot(self, *arg):
        logger.debug(f'common slot print:{arg}')

    def slot_interval_changed(self):
        Settings.v_interval = int(self.spin_interval.text() or 1)

    def slot_follow_to(self, to):
        CommonUnit.status_prompt(f'Frame {to}')

    def eventFilter(self, source, event):
        # if event.type() == 12:  # paint
        #     return False
        return False

    def closeEvent(self, e: QCloseEvent):
        logger.debug('')
        # TODO: uncomment this block
        # if QMessageBox.Ok != QMessageBox.information(self, 'ActionLabeller',
        #                                              "Are you sure to quit, the unsaved labels will be lost?",
        #                                              QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel):
        #     e.ignore()
        logger.debug('Main window closed.')

    # def resizeEvent(self, e):
    #     pass
    #     Log.warn(self.table_timeline.width())
    #     super(MyApp, self).resizeEvent(e)

    def slot_eval(self):
        eval_content = self.ptext_eval_in.toPlainText()
        logger.info(eval_content)
        try:
            resp = eval(eval_content)
        except Exception as e:
            resp = e.__str__()
        self.textb_eval_out.setText(str(resp))
