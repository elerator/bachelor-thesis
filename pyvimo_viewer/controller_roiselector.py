from ui_roiselector import Ui_ROISelector
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import *

from selectboxoverlay import *

import json

class ControllerROISelector(QObject):
    def __init__(self, parent = None):
        super().__init__()
        self.window = QMainWindow()

        self.ui = Ui_ROISelector()
        self.ui.setupUi(self.window)
        self.window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)#Trying to remove maximizability

        self.box = SelectBoxOverlay(self.ui.frame)#frame must be parent of overlay
        #self.ui.frame.installEventFilter(self.box)

        self.skip_thismany = 10

        self.top = None
        self.left = None
        self.bottom = None
        self.right = None

        self.preliminary_coordinates = {}
        self.window.installEventFilter(self)

    def show(self):
        self.window.show()

    def set_video_display_size(self, y, x):
        """ TODO connect to video emit for changed video resolution"""
        self.ui.frame.setMinimumSize(QtCore.QSize(y, x))
        self.ui.frame.setMaximumSize(QtCore.QSize(y, x))

    def eventFilter(self, qobject, qevent):
        qtype = qevent.type()
        if(qtype == QEvent.Close):
            if(self.close_and_discard()== QMessageBox.Ok):
                self.preliminary_coordinates = {}#Delete preliminary_coordinates
                return False
            else:
                qevent.ignore()#The combination of ignore and true does the job of not closing
                return True
            # parents event handler for all other events
        return super().eventFilter(qobject, qevent)

    def close_and_discard(self):
       msg = QMessageBox()
       msg.setIcon(QMessageBox.Information)

       msg.setText("If you close unsaved changes will be discarded. Close either way?")
       msg.setWindowTitle("Discard changes?")
       msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

       return  msg.exec_()

    def make_connections(self, video, model):
        self.video = video
        self.model = model
        video.frame.connect(self.ui.frame.update)#video changes position -> show new frame

        self.box.coordinates.connect(self.update_coordinates)#display currently selected coordina
        video.framenumber.connect(lambda msg: self.ui.current_frame.setText(str(msg)))
        self.ui.frame_forward.released.connect(video.frame_forward)
        self.ui.frame_back.released.connect(video.frame_back)
        self.ui.frames_forward.released.connect(lambda:video.frames_forward(self.skip_thismany))
        self.ui.frames_back.released.connect(lambda: video.frames_back(self.skip_thismany))
        self.ui.save_current_selection.clicked.connect(self.save_current_coordinates)
        self.ui.save_roi_as.clicked.connect(self.save_roi_to_file)


        self.ui.skip_thismany.textChanged.connect(self.set_skip_thismany)

    def set_skip_thismany(self, n):
        try:
            self.skip_thismany = int(n)
        except:
            pass #invalid literal for int() entered in lineedit

    def save_current_coordinates(self):
        frame = self.video.get_framenumber()
        info = {}
        info["y1"] = self.top
        info["y2"] = self.bottom
        info["x1"] = self.left
        info["x2"] = self.right
        info["exclude"] = False

        self.preliminary_coordinates[frame]=info

        #print(self.preliminary_coordinates)


    def save_roi_to_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(None,"QFileDialog.getSaveFileName()", "",
                                                  " Region of Interest (*.json);;",
                                                  options=options)
        #print(filename)
        #print(_)
        try:
            with open(filename, 'w') as outfile:
                json.dump(self.preliminary_coordinates, outfile)
        except:
            pass


    def update_coordinates(self, coordinates):
        self.top = coordinates.top()*2
        self.left = coordinates.left()*2
        self.bottom = coordinates.bottom()*2
        self.right = coordinates.right()*2

        if self.top > self.bottom:
            tmp = self.bottom
            self.bottom = self.top
            self.top = tmp

        if self.left > self.right:
            tmp = self.right
            self.right = self.left
            self.left = tmp

        self.ui.coordinates1.setText(str(self.top))
        self.ui.coordinates2.setText(str(self.left))
        self.ui.coordinates3.setText(str(self.bottom))
        self.ui.coordinates4.setText(str(self.right))
