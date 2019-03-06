from ui_processing_job import Ui_ProcessingJob
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Ui_ProcessingJobAdapter(QWidget, Ui_ProcessingJob):
    """Adapter Class to turn Ui_ProcessingJob created by QtDesigner into a QWidget"""
    def __init__(self, parent = None):
        super(QWidget,self).__init__(parent)
        self.setupUi(self)
