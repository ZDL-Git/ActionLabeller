import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from zdl.utils.io import log

log.theme(log.Theme.LIGHT)
from view.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('resources/app_icon2.png'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
