import numpy as np
from datamodel import DataModel

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import *

import pyqtgraph
from pyqtgraph import PlotWidget, PlotItem, ImageView
import matplotlib.pyplot as plt


class InteractiveDataplot2d(ImageView):
    """ Allows to draw 2d numpy array in an interactive plot using a colormap"""
    def __init__(self, parent=None, model = None, video_model = None, colormap = "inferno"):
        """ Sets the datamodel and optionally a videomodel that is used to print a time indicator according to its current frameself.
        Args:
            model:  DataModel wrapping either 1d or 2d data
            video_model: VideoModel wrapping a video file
            parent: Parent QtWidget
            colormap: String describing matplotlib colormap
        """
        self.view= PlotItem()
        super().__init__(view = self.view)

        self.model = model
        self.video_model = video_model
        self.print_indicator = False
        self.indicator = None

        # Get a colormap
        colormap = plt.cm.get_cmap(colormap)  # cm.get_cmap("CMRmap")nipy_spectral
        colormap._init()
        self.lut = (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0 -255 for Qt
        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()


        if(type(self.model)==type(None)):#Create empty model if no model was given
            self.model = DataModel()

        initial_data = self.model.get_data()
        if not isinstance(initial_data, type(None)):#Draw imagedata if possible
            try:
                self.print_data(initial_data)
            except:#It might be that the model contains data that is not displayable e.g. 1d
                pass

    def print_data(self, data):
        """ Prints data to dataplot
            Args:
                data: 2d float.64 numpy arrays containing values between 0 and 1
        """
        self.print_indicator = True
        self.imagedata = data
        self.setImage(self.imagedata)

        self.indicator_min = -200
        self.indicator_max = 200

        if self.video_model != None:
            pos = int(self.video_model.get_pos(datatype = "motion"))
            self.indicator = self.view.plot([pos,pos],[self.indicator_min,self.indicator_max],pen=pyqtgraph.mkPen(color=pyqtgraph.hsvColor(2),width=1))
        else:
            pos = 0
            self.indicator = self.view.plot([pos,pos],[self.indicator_min,self.indicator_max],pen=pyqtgraph.mkPen(color=pyqtgraph.hsvColor(2),width=1))


    def update_indicator(self, pos):
        """ Updates indicator position
            Args:
                pos: Int describing the current position of the indicator
        """
        if self.print_indicator and self.indicator:
            C=pyqtgraph.hsvColor(1)
            pen=pyqtgraph.mkPen(color=C,width=1)
            #pos = int(self.video_model.get_pos(datatype = self.model.get_datatype()))
            self.indicator.setData([pos,pos],[self.indicator_min,self.indicator_max])



    def updateImage(self, autoHistogramRange=True):
        """ Updates the image, setting the colormap"""
        super().updateImage(autoHistogramRange=autoHistogramRange)
        self.getImageItem().setLookupTable(self.lut)

    def setImage(self, *args, **kwargs):
        """ Sets the image and adjusts the initial view/zoom in the plot"""
        super().setImage(*args, **kwargs)
        self.view.disableAutoRange(axis = 0)
        self.view.enableAutoRange(axis = 1)
