import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pexpect
import cv2

import os
import pickle

from ui_processing_job_adapter import Ui_ProcessingJobAdapter

import ui_data_processor
import sip
import re

class ControllerDataProcessor(QObject):

    def __init__(self):
        super().__init__()
        self.jobs = []
        self.window = QtWidgets.QMainWindow()
        self.ui = ui_data_processor.Ui_MainWindow()

        self.vertical_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.ui.setupUi(self.window)
        self.make_connections()

    def show(self):
        self.window.show()
        #self.window.update()

    def make_connections(self):
        self.ui.new_job.clicked.connect(self.add_motion_decoding_1d)
        self.ui.remove_jobs.clicked.connect(self.remove_jobs)
        self.ui.start_processing.clicked.connect(self.start_all)

    def remove_jobs(self):
        for j in self.jobs:
            j.delete()
        self.jobs = []

    def start_all(self):
        for j in self.jobs:
            j.start_processing()

    def add_motion_decoding_1d(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        video, _ = QFileDialog.getOpenFileName(None,"Select a video for motion processing", "",
                                                  "Wmv Video (*.wmv);;Mp4 Video (*.mp4);; AVI Video (*.avi);; MOV Video files (*.mov);; MPEG Video files (*.mpeg);;",
                                                  options=options)
        if not video:
            return

        json, _ = QFileDialog.getOpenFileName(None,"Select a json specifying the motion Region of interest (ROI) for the file", "","Motion Windows/ROIs (*.json);;",options=options)
        if not json:
            return

        outfile, _ = QFileDialog.getSaveFileName(None,"Specify the output filename", "","Motion Windows/ROIs (*.mot);;",options=options)
        if not outfile:
            outfile = ""
        #motion_decoder = ControllerDataProcessor.MotionDecoderThread(self)

        self.jobs.append(ProcessingJob(self.ui.layout_for_processing_jobs,"1D motion",outfile = outfile,infile1= video,infile2 = json,outer_ui=self.ui))

        self.ui.layout_for_processing_jobs.removeItem(self.vertical_spacer)
        self.ui.layout_for_processing_jobs.addItem(self.vertical_spacer)

    def add_element(self,msg):
        """ TODO menu to choose job from then magic accordingly"""
        #self.ui.layout_for_processing_jobs.addWidget(Ui_ProcessingJobAdapter())
        self.jobs.append(ProcessingJob(self.ui.layout_for_processing_jobs))

        self.ui.layout_for_processing_jobs.removeItem(self.vertical_spacer)
        self.ui.layout_for_processing_jobs.addItem(self.vertical_spacer)

class ProcessingJob(QObject):
    def __init__(self,layout,type_name = "", outfile = "", infile1="", infile2="", outer_ui =None, parent=None):
        super().__init__(parent)
        self.type_name = type_name
        self.input1 = infile1
        self.input2 = infile2
        self.outfile = outfile
        self.layout = layout
        self.outer_ui = outer_ui
        self.init_ui()
        self.make_connections()

    def init_ui(self):
        self.ui = Ui_ProcessingJobAdapter()
        self.ui.jobname.setText(self.type_name)
        self.ui.input1.setText(self.input1)
        self.ui.input2.setText(self.input2)
        self.ui.outfilename.setText(self.outfile)
        self.layout.addWidget(self.ui)

    def delete(self):
        self.layout.removeWidget(self.ui)
        sip.delete(self.ui)
        self.ui = None


    def make_connections(self):
        self.ui.start.clicked.connect(self.start_processing)

    def start_processing(self):
        if "motion" in self.type_name:
            self.thread = ProcessingJob.MotionDecoderThread()
            self.thread.motion_decoding_progress.connect(self.ui.progressBar.setValue)
            self.thread.motion_decoding_finished.connect(lambda msg: self.post_process_motion(self.type_name, self.outfile,self.input2))

            self.thread.set_filepath(self.input1,self.outfile)
            self.thread.set_total_frames()
            self.thread.start()

    def post_process_motion(self, motion_type, tempfile, json):
        if motion_type == "1D motion":
            self.thread = ProcessingJob.Motion1dThread(tempfile,json)#Compute 1D motion and replace tempfile by it
            self.thread.file_ready.connect(lambda msg: self.outer_ui.output_files.append(str(msg)))
            self.thread.start()


    class MotionDecoderThread(QThread):
        """ Class for parallel decoding of motion information from H.264 videos"""
        motion_decoding_progress = pyqtSignal(int)
        motion_decoding_finished = pyqtSignal(bool)

        def __init__(self):
            super().__init__()
            self.infile = None
            self.outfile = None
            self.total_frames = 0

        def set_filepath(self, infile, outfile):
            self.infile = infile
            self.outfile = outfile


        def set_total_frames(self):
            self.cap = cv2.VideoCapture(self.infile)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        def run(self):
            if not self.infile or not self.outfile:
                return #just don't do anything if anything is missing

            child = pexpect.spawnu("./decode_motion " + self.infile + " "+ self.outfile, echo = False)
            while(child.isalive):

                try:
                    child.expect("progress: ")
                    try:
                        for x in range(100):
                            line = child.readline()
                            current_frame = int( re.search("([0-9]+)",line).groups()[0])
                            self.motion_decoding_progress.emit(int((current_frame/self.total_frames)*100))
                    except Exception as e:
                        pass
                except:
                    break
            self.motion_decoding_progress.emit(100)
            self.motion_decoding_finished.emit(True)

    class Motion1dThread(QThread):
        file_ready = pyqtSignal(str)
        def __init__(self, path_to_tempfile, path_to_json):
            super().__init__()
            self.path_to_tempfile = path_to_tempfile
            self.path_to_json = path_to_json

        def run(self):
            amount = None
            try:
                with open(self.path_to_json, encoding='utf-8') as fh:
                    roi = json.load(fh)
                    h264 = tables.open_file(self.path_to_tempfile, mode='r')
                    h264 = h264.root.motion_tensor
                    mothistmap = helper.weighted_histograms(h264,roi=roi)
                    mot[i] = mothistmap#append mothistmap

                    hist = ndimage.gaussian_filter(mothistmap,10)
                    amount = np.sum(hist,axis=0)#1d signal

            except Exception as e:
                print(e)

            # Delete tomparary motfile and replace it by 1d motion
            os.remove(self.path_to_tempfile)
            with open(self.path_to_tempfile, "wb") as fh:
                pickle.dump(amount, fh)
            self.file_ready.emit(self.path_to_tempfile)
