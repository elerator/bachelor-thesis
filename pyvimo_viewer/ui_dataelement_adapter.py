from ui_dataelement import Ui_DataElement
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Ui_DataElementAdapter(QWidget, Ui_DataElement):
    """Adapter Class to turn Ui_DataElement created by QtDesigner into a QWidget"""
    def __init__(self, parent = None):
        super(QWidget,self).__init__(parent)
        self.setupUi(self)
