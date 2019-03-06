from PyQt5 import QtCore, QtGui, QtWidgets
import sys

from ui_data_processor import Ui_MainWindow
from controller_data_processor import *

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    #window = QtWidgets.QMainWindow()
    #ui = Ui_MainWindow()
    #ui.setupUi(window)

    c = ControllerDataProcessor()
    c.show()

    #window.show()
    #window.update()

    sys.exit(app.exec_())
