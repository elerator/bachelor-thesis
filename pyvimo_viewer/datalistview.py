from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

import pyqtgraph
from pyqtgraph import PlotWidget, PlotItem, ImageView

class DataListView(QScrollArea):
    """ Scroll area that contains several DataViews. Scrolling is disabled"""
    def __init__(self, parent = None):
        """ Initializes the DataListView
        """
        pyqtgraph.setConfigOption('background', 'w') #White background

        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

    def wheelEvent(self, ev):
        """ Handles the wheel event and turns mouse wheel control off for the Scroll area"""
        if ev.type() == QEvent.Wheel:
            ev.ignore()
