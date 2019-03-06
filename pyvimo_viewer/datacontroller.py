from datamodel import DataModel
from ui_dataelement_adapter import Ui_DataElementAdapter

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from filedialog import FileDialog

import sip

class DataController:
    def __init__(self, add_button, layout, videomodel, datamodels =[]):
        self.add_button = add_button#
        self.layout = layout

        self.add_button.clicked.connect(self.add_data_display)
        print("DataListController init")


        self.videomodel = videomodel
        self.datamodels = datamodels#Use self.add_data_display() tQtGui.QListWidget(self.centralwidget)o append
        self.dataviews = []

        for model in datamodels:
            self.add_data_display(model)

    def set_start_pos_adapter(self, msg, model):
        """ Converts the string entered in a lineEdit to an int if possible and sets the start position of the video relative to the EEG accordingly.
            Used in add_data_display(...) below.
        """
        try:
            pos = int(msg)
            model.set_start_pos(pos)
        except:
            pass

    def add_data_display(self, model = None):
        """ Adds datadisplay
            Args:
                model: Model to be added to centralwidget as well as to list of models
        """
        print("add_data_display")

        #Create new MODEL and append it to self.models
        if type(model) != type(DataModel()):#Via button (+) press some message (False) arrives
            model = DataModel()

        self.datamodels.append(model)

        #Create VIEW and add it (widget) to layout
        optiondisplay = Ui_DataElementAdapter()
        self.optiondisplay = optiondisplay
        self.dataviews.append(optiondisplay)
        self.layout.addWidget(optiondisplay)

        optiondisplay.close.clicked.connect(lambda msg: self.delete(optiondisplay, self.layout) )
        optiondisplay.load.clicked.connect(lambda msg: FileDialog.load(model))
        optiondisplay.close_1.clicked.connect(lambda msg: self.delete(optiondisplay, self.layout) )
        optiondisplay.load_1.clicked.connect(lambda msg: FileDialog.load(model))
        optiondisplay.lineEdit.textChanged.connect(lambda msg: self.set_start_pos_adapter(msg, model))
        optiondisplay.spinBox.valueChanged.connect(model.set_channel)
        model.channeldata.connect(optiondisplay.graphicsView.print_data)#TODO rename to dataplot and also in designer
        self.videomodel.framenumber.connect(optiondisplay.graphicsView_1.update_indicator)

        self.videomodel.framenumber.connect(model.set_pos_in_video)#triggers pos in eeg
        model.pos_in_eeg.connect(optiondisplay.graphicsView.update_indicator)
        model.mothistmap.connect(optiondisplay.graphicsView_1.print_data)

        model.datatype_signal.connect(self.set_active_page)

        self.redraw_button()

    def set_active_page(self, msg):
        if (msg == "motion"):
            print("set to motion")
            self.optiondisplay.pages.setCurrentIndex(1)
        elif(msg == "eeg"):
            self.optiondisplay.pages.setCurrentIndex(0)



    def delete(self, widget, layout):
        """ Deletes a model from the widget (by reinitializing the centralwidget) and the list of models  """

        layout.removeWidget(widget)
        sip.delete(widget)#calls c++ delete
        del self.dataviews[self.dataviews.index(widget)]


    def redraw_button(self):
        """ Adds button at end of list that may be used to add additional DataDisplays """
        self.layout.removeWidget(self.add_button)
        self.layout.addWidget(self.add_button)
