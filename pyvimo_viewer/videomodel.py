import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import *

import cv2

from PyQt5.QtCore import pyqtSignal, QThread, QObject
import imageio
import time

import warnings


class VideoModel(QObject):
    """ Wrapper for a video file
        Allows to read frames, set the current frame number, read the start position from the database etc.
    """
    frame = pyqtSignal(np.ndarray)
    framenumber = pyqtSignal(int)
    sliderpos = pyqtSignal(int)

    title_signal = pyqtSignal(str)


    def __init__(self):
        """ Initializes the Video model
            call load manually after connecting slots and signals
        """
        super().__init__()

        self.total_frames = 1
        self.cap = None
        self.filepath = ""
        self.accept_external_control = False

        self.use_opencv = False#To read a frame
        self.title = ""
        self.current_frame = 0

        self.fps = 25.0

        self.video_loader_thread = VideoModel.ImageIOReaderThread(self)
        self.playback_thread = VideoModel.PlaybackThread(self)

        self.ignore_sliders_message = False

    def init_video(self):
        """ Initializes the video. Sets total_framenumber, creates video_reader etc.. """
        self.cap = cv2.VideoCapture(self.filepath)
        self.video_reader = imageio.get_reader(self.filepath)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.keep_playing = True # Finished flag
        self.accept_external_control = True #False during play

    def load(self, filepath):
        """ Changes the videofile that is administered by this VideoModel
            Args:
                dyad: Dyad that specifies the video together with the number of camera
                camera: Number of camera that specifies the video id together with dyad
        """
        self.filepath = filepath
        self.video_loader_thread.start()
        return True

    class ImageIOReaderThread(QThread):
        """ Class for parallel initializing of the VideoModel"""
        signal_done = pyqtSignal(bool)
        def __init__(self, outer_instance):
            super().__init__()
            self.outer_instance = outer_instance

        def run(self):
            self.outer_instance.init_video()
            self.outer_instance.get_frame(True)
            self.outer_instance.set_title()

    class PlaybackThread(QThread):
        def __init__(self, outer_instance):
            super().__init__()
            self.fps = outer_instance.fps
            self.outer_instance = outer_instance

        def run(self):
            self.outer_instance.accept_external_control = False #It is essential to set this here after thread is started!!!
            playback_start = time.time()
            pvrs = 0
            while(self.outer_instance.keep_playing):
                elapsed = time.time() - playback_start
                framenumber = self.outer_instance.playback_start_frame + int((elapsed/(1.0/self.fps)))#Why 600 not 1000?
                if(framenumber > pvrs):
                    self.outer_instance._set_framenumber(framenumber)
                pvrs = framenumber
                #QtCore.QCoreApplication.processEvents()
            self.outer_instance.accept_external_control = True #It is essential to set this here after thread is started!!!


    def start_play(self):
        #self.accept_external_control = False #does not work here has to be in thread
        self.playback_start_frame = self.get_framenumber()
        self.keep_playing = True
        self.playback_thread.start()# Start playback thread
        #self.accept_external_control = True

    def stop_play(self):
        self.keep_playing = False

    def get_camera(self):
        return self.camera

    def get_filepath(self):
        ret = None
        try:
            ret = self.database.dictionary[str(self.dyad)]['video'][str(self.camera)]['path']
        except:
            raise FileNotFoundError("Filepath not found in database")
        return ret


    def set_title(self):
        self.title = "TODO"
        self.title_signal.emit(self.title)

    def get_frame(self, via_emit = False):
        frame = None
        if(self.use_opencv):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,self.current_frame)
            ret, frame = self.cap.read()
            if(ret == False):
                raise FileNotFoundError("OpenCV couldnt retrive frames")
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            try:
                frame = self.video_reader.get_data(self.current_frame)
            except:
                pass
            if type(frame) == type(None):
                warnings.warn("No frame retrieved")

        if(via_emit):
            if(type(frame) != type(None)):
                self.frame.emit(frame)
        return frame

    def set_framenumber(self, x, inform_slider = True):
        if(self.accept_external_control):
            #print(str(x) + " at set_framenumber")
            self._set_framenumber(x, inform_slider)

    def _set_framenumber(self, x, inform_slider = True):
        if(x > self.total_frames):
            self.current_frame = self.total_frames-1
            warnings.warn("x > self.total_frames")
        elif(x<0):
            warnings.warn("x < 0")
        else:
            self.current_frame = x

        self.framenumber.emit(x)
        if inform_slider:
            self.sliderpos.emit(x)

        try:
            self.video_reader.get_data(self.current_frame)
            self.frame.emit(self.get_frame())
        except Exception as e:
            self.keep_playing = False
            print("couldnt retrieve frame")
            print(e)
        #self.frame.emit(self.video_reader.get_data(self.current_frame))

    def set_framenumber_via_slider(self,n):
        if not self.ignore_sliders_message:#If framenumber was set manually before dont update otherwise do.
            self.set_framenumber(n, False)
        self.ignore_sliders_message = False

    def get_framenumber(self):
        return self.current_frame

    def frame_forward(self):
        self.ignore_sliders_message = True #slider will inform about new pos but inaccurately
        self.set_framenumber(self.get_framenumber()+1)

    def frame_back(self):
        self.ignore_sliders_message = True #slider will inform about new pos but inaccurately
        self.set_framenumber(self.get_framenumber()-1)

    def frames_back(self, n, inform_slider = True):
        self.ignore_sliders_message = True #slider will inform about new pos but inaccurately
        self.set_framenumber(self.get_framenumber()-n)

    def frames_forward(self, n, inform_slider = True):
        self.ignore_sliders_message = True #slider will inform about new pos but inaccurately
        curr = self.get_framenumber()
        self.set_framenumber(curr+n)

    def get_amount_of_frames(self):
        return self.total_frames
