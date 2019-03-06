import numpy as np
from datamodel import DataModel
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import *

import pyqtgraph
from pyqtgraph import PlotWidget, PlotItem, ImageView


class InteractiveDataplot1d(PlotWidget):
    """ Allows to draw a 1d interactive Dataplot """
    def __init__(self, parent = None, model = None, video_model = None):
        super().__init__(parent)
        self.main_plot = None
        self.indicator = None
        self.video_model = video_model
        self.model = model

        #export = self.sceneObj.contextMenu
        #del export[:]#modify contextMenu

        self.getPlotItem().ctrlMenu = None#Delete "Plot Options" option from context menu as it contains bugs and crashes with float data

        if(type(self.model)==type(None)):#Create empty model if no model was given
            self.model = DataModel()

        self.print_indicator = False#As long as there is no data we don't want to print the indicator
        initial_data = self.model.get_data()
        if not isinstance(initial_data, type(None)):
            try:
                self.print_data(initial_data)
            except:#It might be that the model contains data that is not displayable e.g. 2d data
                pass

        self.plot()


    def print_data(self, data):
        """ Prints 1D-Data represented in a numpy array.
            Args:
                data: 1D Numpy Array containing values to be displayed.
        """
        self.print_indicator = True #As soon as there is data we want to print the indicator upon update
        self.plot_item = self.getPlotItem()

        C=pyqtgraph.hsvColor(1)
        pen=pyqtgraph.mkPen(color=C,width=1)

        X=np.arange(len(data))
        self.indicator_min = int(np.nanmin(data))
        self.indicator_max = int(np.nanmax(data))
        self.main_plot = self.plot_item.plot(X,data,pen=pen,clear=True)


        self.indicator = self.plot([0,0],[self.indicator_min,self.indicator_max],pen=pyqtgraph.mkPen(color=pyqtgraph.hsvColor(2),width=1))

    def update_indicator(self, pos):
        """ Updates indicator position
            Args:
                pos: Int describing the current position of the indicator
        """
        print("udate")
        if self.print_indicator and self.indicator:
            print("update indicator pos to" + str(pos))
            C=pyqtgraph.hsvColor(1)
            pen=pyqtgraph.mkPen(color=C,width=1)
            #pos = int(self.video_model.get_pos(datatype = self.model.get_datatype()))
            self.indicator.setData([pos,pos],[self.indicator_min,self.indicator_max])
