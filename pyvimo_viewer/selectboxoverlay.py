from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import sip


class SelectBoxOverlay(QWidget):
    coordinates = pyqtSignal(QRect)

    def __init__(self, w, parent = None):
        QWidget.__init__(self, w)
        self.w = w

        self.begin = QtCore.QPoint(0,0)
        self.end = QtCore.QPoint(0,0)

        self.box_begin = QtCore.QPoint(0,0)#For the final selection
        self.box_end = QtCore.QPoint(0,0)
        self.parent = parent

        self.setGeometry(w.geometry())

        self.data_has_changed = True

        origin = QtCore.QPoint(0,0)
        self.update()

    def get_box_coordinates(self):
        """ returns the coordinates of the current selection"""
        return QRect(self.box_begin,self.box_end)

    def resizeEvent(self,e):
        self.origin = self.w.geometry().topLeft()

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(100, 100, 100, 100))
        qp.setBrush(br)
        qp.drawRect(QRect(  QtCore.QPoint(self.begin.x()-10,self.begin.y()-10),
                            QtCore.QPoint(self.end.x()-10,self.end.y()-10)))

    def mousePressEvent(self, event):
        """ Resets coordinates of the select box. Sets beginning point to mouse pos.
            Args:
                event: GUI event
        """
        self.begin =  event.pos()+ self.origin
        self.end =  event.pos()+ self.origin
        self.update()

    def mouseMoveEvent(self, event):
        """ Sets end point to mouse pos. Updates the select_box overlay.
            Args:
                event: GUI event
        """
        self.end = event.pos()+self.origin
        self.update()

    def mouseReleaseEvent(self, event):
        """ Copies the current coordinates to respective attributes.
            If permanent_show is set to false, deletes select_box view.
            Args:
                event: GUI event
        """
        self.box_begin = self.begin
        self.box_end = event.pos()+self.origin
        self.begin = self.begin
        self.end = event.pos()+self.origin

        self.coordinates.emit(QRect(self.get_box_coordinates().topLeft()-self.origin,self.get_box_coordinates().bottomRight()-self.origin))
        self.update()
