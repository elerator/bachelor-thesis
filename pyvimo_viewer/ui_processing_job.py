# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_processing_job.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ProcessingJob(object):
    def setupUi(self, ProcessingJob):
        ProcessingJob.setObjectName("ProcessingJob")
        ProcessingJob.resize(790, 300)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ProcessingJob)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.jobname = QtWidgets.QLabel(ProcessingJob)
        self.jobname.setObjectName("jobname")
        self.horizontalLayout.addWidget(self.jobname)
        self.input1 = QtWidgets.QLineEdit(ProcessingJob)
        self.input1.setObjectName("input1")
        self.horizontalLayout.addWidget(self.input1)
        self.input2 = QtWidgets.QLineEdit(ProcessingJob)
        self.input2.setObjectName("input2")
        self.horizontalLayout.addWidget(self.input2)
        self.outfilename = QtWidgets.QLineEdit(ProcessingJob)
        self.outfilename.setObjectName("outfilename")
        self.horizontalLayout.addWidget(self.outfilename)
        self.progressBar = QtWidgets.QProgressBar(ProcessingJob)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout.addWidget(self.progressBar)
        self.start = QtWidgets.QPushButton(ProcessingJob)
        self.start.setObjectName("start")
        self.horizontalLayout.addWidget(self.start)

        self.retranslateUi(ProcessingJob)
        QtCore.QMetaObject.connectSlotsByName(ProcessingJob)

    def retranslateUi(self, ProcessingJob):
        _translate = QtCore.QCoreApplication.translate
        ProcessingJob.setWindowTitle(_translate("ProcessingJob", "Form"))
        self.jobname.setText(_translate("ProcessingJob", "New Processing Job"))
        self.start.setText(_translate("ProcessingJob", "Start processing"))

