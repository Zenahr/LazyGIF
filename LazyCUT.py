#!/usr/bin/env python

# GET THE SLIDER TO WORK ON MOUSE CLICK ANYWHERE: https://stackoverflow.com/questions/52689047/moving-qslider-to-mouse-click-position




"""ROADMAP

hotkeys
----------------------------------------------------------------------------------------------------
arrow   keys        : seek 10   frames  forward or backward
arrow   keys + shift: seek 100  frames  forward or backward
arrow   keys + ctrl : seek 1    frame   forward or backward
ctrl + e : export as gif to source folder


export functionality
----------------------------------------------------------------------------------------------------
export resolution percentage
export frame rate

target filesize: use this textfield to make sure file can be exported to Discord, etc. (will try to keep the highest quality and frame rate possible)
regarding that, have a radio button group to choose between:
    - prioritize resolution
    - prioritize frame rate
"""


"""
InnoSetup: e process of adding custom verbs to a file's shortcut menu is described in the Extending Shortcut Menus and Verbs and File Associations topics. If you prefer a simpler way, you can also just put a shortcut to your EXE in the SendTo folder.
"""

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QVideoEncoderSettings
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QCheckBox,
    QStatusBar,
    QMessageBox,
    QDialog,
        )
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys
import os
import subprocess
from uuid import uuid1
from random import randint

import moviepy.config as mpy_conf

# mpy_conf.FFMPEG_BINARY = r'path\to\ffmpeg.exe'
# mpy_conf.FFMPEG_BINARY = r'C:\ffmpeg\bin\ffmpeg.exe'
# mpy_conf.FFMPEG_BINARY = r'ffmeg\bin\ffmpeg.exe' # Remove the need to manually set the path to ffmpeg.exe for end users.

# We got to import all modules manually for PyInstaller to work. Use AUTOPYTOEXE in case the imports have changed since the date of writing this.
# See: https://github.com/Zulko/moviepy/issues/591#issuecomment-965203931

from importhelper import *


# Windows app icon fix (taskbar and taskbar manager)
import ctypes
myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

from __info__ import *

class VideoWindow(QMainWindow):

    def log(self, msg):
        self.statusBar.showMessage(msg)

    def enableAllControls(self, flag=True):
        self.startMarkerTime.setEnabled(flag)
        self.endMarkerTime.setEnabled(flag)
        self.symmetrizeCheckbox.setEnabled(flag)
        self.playButton.setEnabled(flag)
        self.convertToGifButton.setEnabled(flag)
        self.exportResolutionPercentage.setEnabled(flag)
        self.exportFrameRate.setEnabled(flag)
        self.exportSpeedRate.setEnabled(flag)
        self.startSlider.setEnabled(flag)
        self.endSlider.setEnabled(flag)

    def updateStartSlider(self):
        if self.startSlider.value() > self.endSlider.value():
            self.endSlider.setValue(self.startSlider.value())
        self.setPosition(self.startSlider.value())
        self.mediaPlayer.play()
            
    def updateEndSlider(self):
        if self.endSlider.value() < self.startSlider.value():
            self.startSlider.setValue(self.endSlider.value())
        if self.mediaPlayer.position() > self.endSlider.value():
            self.mediaPlayer.setPosition(self.endSlider.value())
            self.positionSlider.setValue(self.endSlider.value())
        self.mediaPlayer.play()

    def updateVolume(self):
        self.mediaPlayer.setVolume(self.volumeSlider.value())

    def mouseReleaseEvent(self, event):
        print("Mouse Release Event")
        # if element was startSlider, do something
        if self.startSlider.underMouse():
            self.setPosition(self.startSlider.value())

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setWindowTitle(APP_TITLE) 
        self.setWindowIcon(QIcon("icon-dark.png"))
        # self.setWindowFlags(Qt.WindowStaysOnTopHint) # dev only
        self.setMinimumSize(640, 280)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface) # https://doc.qt.io/qtforpython-5/PySide2/QtMultimedia/QMediaPlayer.html#qmediaplayer
        self.mediaPlayer.setNotifyInterval(30) # XYms refresh rate (needed for notifs)
        self.mediaPlayer.setMuted(False) # mute the video
        self.mediaPlayer.setVolume(50) # set volume to 50%


        # add label for volume slider
        self.volumeLabel = QLabel()
        self.volumeLabel.setText("Volume")
        self.volumeLabel.setAlignment(Qt.AlignCenter)

        # add slider for audio volume
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setTickPosition(QSlider.TicksBothSides)
        self.volumeSlider.setTickInterval(10)
        self.volumeSlider.setSingleStep(1)


        self.volumeSlider.valueChanged.connect(self.updateVolume)

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        self.currentPlayTimeLabel = QLabel()
        self.currentPlayTimeLabel.setText("00:00")
    

        # Other stuff
        self.startMarkerTime    = QLineEdit(self)
        self.startMarkerTime.setStatusTip("Clip Start Time")
        self.startMarkerTime.setEnabled(False)
        self.startMarkerTime.setPlaceholderText("ss:ms")

        self.endMarkerTime      = QLineEdit(self)
        self.endMarkerTime.setStatusTip("Clip End Time")
        self.endMarkerTime.setEnabled(False)
        self.endMarkerTime.setPlaceholderText("ss:ms")

        self.symmetrizeCheckbox = QCheckBox("Symmetrize")
        self.symmetrizeCheckbox.setEnabled(False)
        self.symmetrizeCheckbox.setChecked(False)

        self.exportResolutionPercentage    = QLineEdit(self)
        self.exportResolutionPercentage.setStatusTip("Export Resolution Percentage (Scaling)")
        self.exportResolutionPercentage.setEnabled(False)
        self.exportResolutionPercentage.setPlaceholderText("1")
        self.exportResolutionPercentage.setText("1")

        self.exportFrameRate    = QLineEdit(self)
        self.exportFrameRate.setStatusTip("Export Frame Rate (FPS)")
        self.exportFrameRate.setEnabled(False)
        self.exportFrameRate.setPlaceholderText("60")
        self.exportFrameRate.setText("60")

        self.exportSpeedRate    = QLineEdit(self)
        self.exportSpeedRate.setStatusTip("Export Speed Rate")
        self.exportSpeedRate.setEnabled(False)
        self.exportSpeedRate.setPlaceholderText("1")
        self.exportSpeedRate.setText("1")

        self.convertToGifButton = QPushButton("Export As GIF")
        self.convertToGifButton.setStatusTip('Export video as GIF')
        self.convertToGifButton.clicked.connect(self.saveAsGif)

        self.appVersionLabel = QLabel()
        self.appVersionLabel.setText(APP_VERSION)
        self.appVersionLabel.setAlignment(Qt.AlignCenter)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Import Video', self)        
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('')
        openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('')
        exitAction.triggered.connect(self.exitCall)

        # dev tool button
        devFileAction = QAction(QIcon('open.png'), '&Devtest', self)        
        devFileAction.setShortcut('R')
        devFileAction.setStatusTip('')
        devFileAction.triggered.connect(self.openTestFile)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&Actions')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        # fileMenu.addAction(devFileAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        self.startSlider = QSlider(Qt.Horizontal, self)
        self.startSlider.setRange(0, 100)
        self.startSlider.setFocusPolicy(Qt.NoFocus)
        self.startSlider.setPageStep(5)

        self.endSlider = QSlider(Qt.Horizontal, self)
        self.endSlider.setRange(0, 100)
        self.endSlider.setValue(100)
        self.endSlider.setFocusPolicy(Qt.NoFocus)
        self.endSlider.setPageStep(5)



        self.startSlider.valueChanged.connect(self.updateStartSlider)
        self.endSlider.valueChanged.connect(self.updateEndSlider)


        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.currentPlayTimeLabel)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.startSlider)
        layout.addWidget(self.endSlider)
        layout.addWidget(self.errorLabel)
        layout.addWidget(self.exportResolutionPercentage)
        layout.addWidget(self.exportFrameRate)

        # add volume slider
        volumeSliderLayout = QHBoxLayout()
        volumeSliderLayout.addWidget(self.volumeLabel)
        volumeSliderLayout.addWidget(self.volumeSlider)

        layout.addLayout(volumeSliderLayout)

        layout.addWidget(self.convertToGifButton)

        # layout.addWidget(self.appVersionLabel)

        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        self.enableAllControls(False) # Disable all controls on startup.


        self.videoFPS = 0

    def dragEnterEvent(self, event):
            event.accept()

    def dragMoveEvent(self, event):
            event.accept()

    def dropEvent(self, event):
        # get the file path of event
        filePath = event.mimeData().urls()[0].toLocalFile()
        print(filePath)


        # check if file is a video
        if filePath.endswith(('.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.wmv', '.flv', '.3gp', '.3g2')):
            # set the video path
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filePath)))
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(filePath)))
            self.enableAllControls()
            self.mediaPlayer.play()
            self.loadedFile = filePath # TODO: replace with simple call of currently loaded file on onMediaLoaded
            self.videoFPS   = VideoFileClip(self.loadedFile).fps
        event.accept()

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Import Video",
                QDir.homePath() + "/Videos",
                )

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.enableAllControls()
            self.mediaPlayer.play()
            self.loadedFile = fileName # TODO: replace with simple call of currently loaded file on onMediaLoaded
            self.videoFPS   = VideoFileClip(self.loadedFile).fps
            # self.exportFrameRate.setText(str(self.videoFPS)) # initially set the export frame rate to the source video fps

    def openTestFile(self):
        # NOTE: dev only
        self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile("D:\\VIDEOS\APEX LEGENDS\\CHEATER FOOTAGE\\2.mp4")))
        self.enableAllControls()
        self.mediaPlayer.play()
        self.loadedFile = "D:\\VIDEOS\APEX LEGENDS\\CHEATER FOOTAGE\\2.mp4" # TODO: replace with simple call of currently loaded file on onMediaLoaded
        print(self.loadedFile)

    def exitCall(self):
        sys.exit(app.exec_())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
            event.accept()
        elif event.key() == Qt.Key_Enter and event.modifiers() & Qt.Key_Alt:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        if event.key() == Qt.Key_Space:
            self.play()
            event.accept()
        event.accept()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
        
    def mouseDoubleClickEvent(self, event):
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        if position > self.endSlider.value():
            self.positionSlider.setValue(self.endSlider.value())
            self.mediaPlayer.setPosition(self.endSlider.value())
            
            # seek to startSlider and play video
            self.mediaPlayer.setPosition(self.startSlider.value())
            self.mediaPlayer.play()

        elif position < self.startSlider.value():
            self.positionSlider.setValue(self.startSlider.value())
            self.mediaPlayer.setPosition(self.startSlider.value())
            self.mediaPlayer.pause()
        else:
            self.positionSlider.setValue(position)

        # restart when reaching end.
        if position == self.endSlider.value():
            self.mediaPlayer.setPosition(self.startSlider.value())
            self.positionSlider.setValue(self.startSlider.value())
            self.mediaPlayer.play()

        
        # check endofvideo has been reached. If so, restart playback.
        if position == self.mediaPlayer.duration():
            self.mediaPlayer.setPosition(0)
            self.positionSlider.setValue(0)
            self.mediaPlayer.play()
        

        
        # convert to mm:ss:ms
        time = self.mediaPlayer.position()
        time = time / 1000
        # print(self.mediaPlayer.position())
        self.currentPlayTimeLabel.setText("{0:.2f}".format(time) + "s")

    def durationChanged(self, duration):
        def initializeSliders():
            # Initialize sliders
            self.totalFrames = VideoFileClip(self.loadedFile).reader.nframes

            self.positionSlider.setRange(0, duration)
            self.startSlider.setRange(0, duration)
            self.endSlider.setRange(0, duration)
            self.startSlider.setValue(0)
            self.endSlider.setValue(duration)
        initializeSliders()
        # set the export frame rate to the source video fps
        self.exportFrameRate.setText(str(self.videoFPS))

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.enableAllControls(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def saveAsGif(self):
        """Export video as GIF main method"""
        self.log("EXPORTING ... PLEASE WAIT")
        if ('.gif' in self.loadedFile):
            newFilePath = os.path.splitext(self.loadedFile)[0] + "_LazyCUT.mp4"
      
        else:
            newFilePath = os.path.splitext(self.loadedFile)[0] + "-CUT-" + str(randint(111111, 999999)) + ".mp4"
        time = self.mediaPlayer.position()
        time = time / 1000
        # print(self.mediaPlayer.position())
        self.currentPlayTimeLabel.setText("{0:.2f}".format(time).replace('.', ':') + "s")
        # print("{0:.2f}".format(time).replace('.', ':') + "s")
        # Get start and end times
        exportFrameRate        = float(self.exportFrameRate.text())
        desiredFPS             = exportFrameRate if exportFrameRate >= 1 or exportFrameRate <= self.videoFPS else self.videoFPS
        desiredExportSpeedRate = 1.0 if float(self.exportSpeedRate.text()) == "" or float(self.exportSpeedRate.text()) <= 0 else float(self.exportSpeedRate.text())

        startTime = self.startSlider.value() / 1000
        endTime = self.endSlider.value() / 1000
        clip = (VideoFileClip(self.loadedFile, audio=True)
                .subclip(startTime, endTime) # (start, end) # https://zulko.github.io/moviepy/ref/Clip.html?highlight=subclip#moviepy.Clip.Clip.subclip
                .resize(float(self.exportResolutionPercentage.text())) # output scaling
                .fx( speedx, desiredExportSpeedRate)
                )      
        clip.write_videofile(newFilePath, fps=desiredFPS, preset='medium', remove_temp=True)

        # frames = int(clip.fps * clip.duration)
        # n_frames = clip.reader.nframes # number of frames in video

        self.log("saved at " + newFilePath)
        # if self.symmetrizeCheckbox.isChecked():
        #     self.statusBar.showMessage("Symmetrizing...")

        newFilePathDirectory = os.path.dirname(newFilePath)
        # subprocess.Popen(f'explorer {newFilePathDirectory}') # TODO: currently not working: redirects to documents folder instead.

        newWindow = QDialog()
        newWindow.setWindowTitle("EXPORTED GIF")

        # add description label
        # descriptionLabel = QLabel(newWindow)
        # descriptionLabel.setText(f'Video saved at {newFilePathDirectory}')
        # descriptionLabel.setAlignment(Qt.AlignCenter)
        # make label selectable
        # descriptionLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        def copyPathToClipboard(path):
            cb = QApplication.instance().clipboard()
            cb.clear(mode=cb.Clipboard )
            cb.setText(path, mode=cb.Clipboard)

        # add button to copy path to clipboard
        copyPathButton = QPushButton(newWindow)
        copyPathButton.setText("Copy path to clipboard")
        copyPathButton.clicked.connect(lambda: copyPathToClipboard(newFilePathDirectory))


        # descriptionLabel.setStyleSheet("font-size: 20px;")
        # descriptionLabel.setGeometry(QRect(0, 0, 400, 50))
        # newWindow.setWindowFlags(Qt.WindowStaysOnTopHint)
        newWindow.setFixedSize(400, 200)
        # newWindow.setStyleSheet("background-color: #1a1a1a;")
        newWindow.setWindowModality(Qt.ApplicationModal)
        # newWindow.setAttribute(Qt.WA_DeleteOnClose)
        newWindow.exec_()

        # msgbox = QMessageBox()
        # msgbox.setWindowTitle('Done Exporting!')
        # msgbox.setText(f'Video saved at {newFilePathDirectory}')
        # msgbox.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # msgbox.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())