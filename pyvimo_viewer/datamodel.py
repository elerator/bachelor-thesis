import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import *

import numpy as np
import os

import tables
import re

class DataModel(QObject):
    channeldata = pyqtSignal(np.ndarray)#1d data
    channel_signal = pyqtSignal(int)
    mothistmap = pyqtSignal(np.ndarray)#2d data
    datatype_signal = pyqtSignal(str)#Datatype changed? -> Stacked widget toggles
    pos_in_eeg = pyqtSignal(int)#indicator
    title_signal = pyqtSignal(str)

    def __init__(self):
        """load() must be called by user after signals and slots are connected
            set_filepath() must be called after signals and slots are connected"""

        super().__init__()

        self.data = None
        self.vmrk_path = None
        self.title = ""
        self.channel = None
        self.datatype = None
        self.video_start_in_eeg = None
        self.filepath = None
        self.val_pos_in_eeg = None


    def load(self, filepath = None):
        """ Loads motion or eeg data depending on self.datatype
            emits data (mothistmap or channeldata) and channel in the case of eeg data"""
        if(not self.datatype or not self.filepath):
            if(filepath):
                self.set_filepath(filepath)
            else:
                raise ValueError("Set filepath first or provide it as argument")

        if self.datatype == "eeg":
            self.load_eeg_file()
        elif self.datatype == "motion":
            self.load_motion()
        else:
            raise ValueError("Datatype " + str(self.datatype) + " is not supported")


    def set_filepath(self,filepath):
        """ Sets filepath, datatype and title if path is valid. It is valid if it points to an existant i.e. readable file,
            if it is possible to set the datatype according to the file extension
            and if a vmrk file exists in the case of .eeg files. Throws exceptions otherwise"""

        try:
            with open(filepath) as file:
                pass
        except:
            raise FileNotFoundError("File '" + filepath + "' was not readable/existant")

        if(".eeg" in filepath):
            self.set_datatype("eeg")
        elif(".mot" in filepath):
            self.set_datatype("motion")
        elif(".h5" in filepath or ".hdf5" in filepath):
            self.set_datatype("motion")
        else:
            raise ValueError("Specify a filepath to a .mot .h5 or .hdf5 or a .eeg file");


        if self.datatype == "eeg": # set title and set vmrk metainfo-file-path. Error when it doesn't exist
            try:
                dir_path = re.match("(.*)/", filepath).group(0)
                filename = re.match(dir_path + "(.*)" + "\..*", filepath).groups()[0]
                vmrk_path = dir_path + filename + ".vmrk"

                self.set_title(filename + "(eeg)")
            except:
                raise NameError("Error occured during parsing of filenames")
            try:
                with open(vmrk_path) as file:
                    pass #open and close to check if file exists
                self.vmrk_path = vmrk_path
            except FileNotFoundError:
                raise FileNotFoundError("Make sure to place the .vmrk file that has the same name as the .eeg file in the same folder\n"
                                        +"file " + vmrk_path + " was not found")


        if self.datatype == "motion":#set title for motion files
            try:
                dir_path = re.match("(.*)/", filepath).group(0)
                print(dir_path)
                filename = re.match(dir_path + "(.*)" + "\..*", filepath).groups()[0]

                self.set_title(filename + "(mot)")
            except:
                raise NameError("Error occured during parsing of filenames")

        self.filepath = filepath

    def set_pos_in_video(self, frame):
        """ Convert position in frames to position in eeg samplepoints. Add offset between start of EEG recording and start of video. """
        if(type(self.video_start_in_eeg) == type(None)):#has to be compared to None if primitive value is stored
            self.set_start_pos()

        pos = 0

        if self.datatype == "eeg":
            pos = self.video_start_in_eeg + (frame/25)*500
        elif self.datatype == "motion":
                pos = frame
        elif type(self.datatype) == type(None):
            #raise ValueError("No datatype specified")
            pass
        else:
            raise NotImplementedError("Datatype not supported")

        self.val_pos_in_eeg = pos
        self.pos_in_eeg.emit(pos)

    def get_pos_in_eeg():
        if self.val_pos_in_eeg:
            return self.val_pos_in_eeg
        else:
            return 0

    def get_datatype(self):
        return self.datatype

    def set_datatype(self, datatype):
        self.datatype = datatype
        self.datatype_signal.emit(datatype)

    def get_channel(self):
        return self.channel

    def set_channel(self, channel):
        self.channel = channel
        self.load()#load emits data
        self.channel_signal.emit(channel)

    def set_title(self, title):
        self.title = title
        self.title_signal.emit(title)

    def get_title(self):
        return self.title

    def get_data(self):
        return self.data

    def deleted(self):
        return self.is_deleted

    def change_channel(self, channel):
        self.channel = channel
        self.load()

    def load_motion(self):
        try:
            f = tables.open_file(self.filepath, mode='r')
            #weighted_hist = np.array(list(f.root)[0], dtype=np.float64)#f.root.motion_tensors or f.root.data
            if "/motion_tensor" in f:
                weighted_hist = np.array(f.root.motion_tensor, dtype=np.float64)
            else:
                raise Exception("File doesn't contain node 'motion_tensor'")

            weighted_hist = (weighted_hist - np.min(weighted_hist))
            weighted_hist = weighted_hist + 1
            weighted_hist = np.log(weighted_hist)

            #transform to be between 0 and 1
            if((np.max(weighted_hist) - np.min(weighted_hist))!=0.0):
                weighted_hist = (weighted_hist - np.min(weighted_hist)) / (np.max(weighted_hist) - np.min(weighted_hist))

            self.data = weighted_hist
            self.mothistmap.emit(self.data)
        except Exception as e:
            print(e)
        finally:
            f.close()
        return self.data


    def load_eeg_file(self):
        """ Loads eeg file, emits channeldata and channel_signal"""
        if(self.filepath==None):
            print("No filepath set")
            return None

        if(not self.get_channel()):
            self.channel = 0#dont tell anyone yet (see emit below)

        n_channels = 64
        bytes_per_sample = 2 #Because int16

        my_type = np.dtype([("channel"+str(x),np.int16) for x in range(0,n_channels)])
        byte_size = os.path.getsize(self.filepath)

        nFrames =  byte_size // (bytes_per_sample * n_channels);
        data = np.array(np.fromfile(self.filepath,dtype=my_type))["channel"+str(self.get_channel())]

        data = np.array(data, dtype= np.float32)
        data[data==32767] = np.nan
        data[data==-32768] = np.nan
        data[data==-32767] = np.nan

        self.data = data

        self.channeldata.emit(data)
        self.channel_signal.emit(self.get_channel())

    def set_start_pos(self, start_pos_in_datapoints = None):
        """ Computes the beginning of the video measured in datapoints after the start of the eeg-recordings. Saves value in
            self.video_start_in_eeg. If no vmrk_path was set start_pos is set to 0. If start_pos_in_datapoints is provided
            self.video_start_in_eeg is set to 0"""

        print("set start_pos in datatpoints to " + str(start_pos_in_datapoints))

        if(not type(start_pos_in_datapoints)==type(None)):
            self.video_start_in_eeg = start_pos_in_datapoints
            #self.set_pos_in_video(self.get_framenumber()) # Communicate changes via emit in set_pos_in_video
        else:
            if not self.vmrk_path:
                self.video_start_in_eeg = 0
                return
            data = self.parse_vmrk(self.vmrk_path)
            #assuming earliest meaningful event is start of video
            pos = 10000000000000000
            try:
                for key, value in pair[str(dyad)]['eeg']['metainfo']['description'].items():#Search for R128
                    if(value == 'R128'):
                        newpos = int(pair[str(dyad)]['eeg']['metainfo']['position'][key])
                        if(newpos < pos):#find smallest R128 value
                            pos = newpos
            except:
                pass

            if(pos == 10000000000000000):
                pos = 0

            self.video_start_in_eeg = int(pos)


        #assert self.video_start_in_eeg

    def parse_vmrk(self, path):
        """ Parses vmrk file and returns a dictionary containing the information.
            The keys denote the kind of data whereas the values are a dictionary
        """

        with open(path) as f:
            content = f.readlines()

        data = {'marker number':[], 'type':[], 'description':[], 'time':[], 'size':[], 'channel':[]}

        entry = 0
        for line in content:
            match = re.match("Mk", line)
            if(match != None):
                markers = re.search("[0-9][0-9]?", line)
                data["marker number"].append(int(markers.group(0)))
                line = line[markers.end():]#use rest of line only next

                markers = re.match("(.*?),",line)
                data["type"].append(markers.group(1)[1:])#Group 1 is exclusive , while group 0 is inclusive ,
                line = line[markers.end():]

                markers = re.search("(.*?),",line)
                data["description"].append(markers.group(1))
                line = line[markers.end():]

                markers = re.search("(.*?),",line)
                data["time"].append('0' + markers.group(1))# '0' + is necessary as some fields are empty
                line = line[markers.end():]

                markers = re.search("(.*?),",line)
                data["size"].append(int('0' + markers.group(1)))
                line = line[markers.end():]

                try:#In the first line there is an additional value we dont want to parse
                    data["channel"].append(int('0' + line))
                except:
                    data["channel"].append(0)
        return data
