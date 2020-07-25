from PyQt5 import uic

import global_
from utils import Log
from video import Video
from widgets import *

Ui_MainWindow, QtBaseClass = uic.loadUiType("qt_gui/mainwindow.ui")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self, flags=Qt.Window)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.model = TimelineItemModel(20, 50)
        self.table_timeline.setModel(self.model)

        self.combo_speed.addItems(['0.25', '0.5', '0.75', '1', '1.25', '1.5', '1.75'])
        self.combo_speed.setCurrentIndex(2)
        self.combo_sortby.addItems(['timestamp', 'filename'])
        self.combo_sortby.setCurrentIndex(1)

        self.spin_interval.textChanged.connect(self.slot_interval_changed)
        self.combo_speed.currentTextChanged.connect(self.slot_speed_changed)
        self.input_jumpto.textChanged.connect(
            lambda text: text and global_.mySignals.schedule.emit(int(text), -1, -1, global_.Emitter.INPUT_JUMPTO))
        self.label_show.installEventFilter(self)

        def init_buttons():
            self.btn_open_video.setFocus()
            self.btn_open_video.clicked.connect(self.slot_open_file)
            self.btn_play.clicked.connect(global_.mySignals.video_pause_or_resume.emit)
            self.btn_to_head.clicked.connect(self.to_head)
            self.btn_to_tail.clicked.connect(self.to_tail)
            self.btn_eval.clicked.connect(self.slot_eval)
            self.btn_new_label_temp.clicked.connect(self.table_label_temp.slot_action_add)
            self.btn_del_label_temp.clicked.connect(self.table_label_temp.slot_del_selected_actions)

        def init_settings():
            global_.Settings.v_interval = int(self.spin_interval.text())
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
        self.table_label_temp.__init_later__()

        global_.g_status_prompt = self.label_note.setText
        global_.mySignals.follow_to.connect(self.slot_follow_to)

    def common_slot(self, *arg):
        Log.debug(f'common slot print:', arg)

    def slot_open_file(self):
        # got = QFileDialog.getOpenFileName(self, "Open Image", "/Users/zdl/Downloads/下载-视频",
        #                                   "Media Files (*.mp4 *.jpg *.bmp)", options=QFileDialog.ReadOnly)
        got = ['/Users/zdl/Downloads/下载-视频/金鞭溪-张家界.mp4']
        Log.info(got)
        fname = got[0]
        if fname:
            video = Video(fname)
            self.table_timeline.set_column_count(video.get_info()['frame_c'])
            self.label_show.set_video(video)
            global_.mySignals.timer_start(1000 / video.get_info()['fps'] / float(self.combo_speed.currentText()))
            global_.mySignals.video_start.emit()

    def to_head(self):
        pass

    def to_tail(self):
        pass

    def slot_interval_changed(self):
        global_.Settings.v_interval = int(self.spin_interval.text() or 1)

    def slot_speed_changed(self):
        Log.debug('here')
        new_speed = 1000 / self.label_show.video_obj.get_info()['fps'] / float(self.combo_speed.currentText())
        global_.mySignals.timer_video.setInterval(new_speed)

    def slot_follow_to(self, emitter, to):
        global_.g_status_prompt(f'Frame {to}')

    def eventFilter(self, source, event):
        if event.type() == 12:
            return False
        # Log.debug(f'etype {event.type()} source {source}')
        # if source is self.label_note:
        #     pass

        return super(QMainWindow, self).eventFilter(source, event)

    # def resizeEvent(self, e):
    #     pass
    #     Log.warn(self.table_timeline.width())
    #     super(MyApp, self).resizeEvent(e)

    def slot_eval(self):
        cont = self.ptext_eval_in.toPlainText()  # type:QPlainTextEdit
        Log.info(cont)
        try:
            resp = eval(cont)
        except Exception as e:
            resp = e.__str__()
        self.textb_eval_out.setText(str(resp))

    # def slot_new_label_temp(self):
    #     Log.debug('here')
    #     global_.mySignals.action_add.emit(global_.Emitter.T_TEMP)

