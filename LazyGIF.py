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
    QTextEdit,
        )
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys
import os
import subprocess

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

import qdarkstyle

class InfoWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log")
        self.setFixedSize(400, 300)
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setText('')
        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        self.setLayout(layout)

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
        self.autoStartSliderButton.setEnabled(flag)
        self.autoEndSliderButton.setEnabled(flag)

    def autofillStartMarkerTime(self):
        time = self.mediaPlayer.position()
        time = time / 1000
        self.startMarkerTime.setText(str("{0:.2f}".format(time)))

    def autofillEndMarkerTime(self):
        time = self.mediaPlayer.position()
        time = time / 1000
        self.endMarkerTime.setText(str("{0:.2f}".format(time)))

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        # self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
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
        self.mediaPlayer.setMuted(True) # mute the video

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
    



        self.symmetrizeCheckbox = QCheckBox("Symmetrize")
        self.symmetrizeCheckbox.setEnabled(False)
        self.symmetrizeCheckbox.setChecked(False)

        self.exportResolutionPercentage    = QLineEdit(self)
        self.exportResolutionPercentage.setStatusTip("Export Resolution Percentage (Scaling)")
        self.exportResolutionPercentage.setEnabled(False)
        self.exportResolutionPercentage.setPlaceholderText("0.5")
        self.exportResolutionPercentage.setText("0.3")

        self.exportFrameRate    = QLineEdit(self)
        self.exportFrameRate.setStatusTip("Export Frame Rate (FPS)")
        self.exportFrameRate.setEnabled(False)
        self.exportFrameRate.setPlaceholderText("20")
        self.exportFrameRate.setText("20")

        self.exportSpeedRate    = QLineEdit(self)
        self.exportSpeedRate.setStatusTip("Export Speed Rate")
        self.exportSpeedRate.setEnabled(False)
        self.exportSpeedRate.setPlaceholderText("1")
        self.exportSpeedRate.setText("1")

        self.convertToGifButton = QPushButton("Export GIF")
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
        # menuBar = self.menuBar()
        # fileMenu = menuBar.addMenu('&Actions')
        # fileMenu.addAction(openAction)
        # fileMenu.addAction(exitAction)
        # fileMenu.addAction(devFileAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.currentPlayTimeLabel)
        controlLayout.addWidget(self.positionSlider)

        self.startMarkerTime    = QLineEdit(self)
        self.startMarkerTime.setStatusTip("Clip Start Time")
        self.startMarkerTime.setPlaceholderText("00.00")
        self.startMarkerTime.setPlaceholderText("ss.ms")
        self.startMarkerTime.setEnabled(False)

        self.endMarkerTime      = QLineEdit(self)
        self.endMarkerTime.setStatusTip("Clip End Time")
        self.endMarkerTime.setPlaceholderText("00.00")
        self.endMarkerTime.setPlaceholderText("ss.ms")
        self.endMarkerTime.setEnabled(False)

        self.autoStartSliderButton = QPushButton()
        self.autoStartSliderButton.setText("Set clip start to current frame")
        self.autoStartSliderButton.clicked.connect(self.autofillStartMarkerTime)
        self.autoStartSliderButton.setEnabled(False)

        startSliderLayout = QHBoxLayout()
        startSliderLayout.setContentsMargins(0, 0, 0, 0)
        startSliderLayout.addWidget(self.autoStartSliderButton)
        startSliderLayout.addWidget(self.startMarkerTime)

        self.autoEndSliderButton = QPushButton()
        self.autoEndSliderButton.setText("Set clip end to current frame  ")
        self.autoEndSliderButton.clicked.connect(self.autofillEndMarkerTime)
        self.autoEndSliderButton.setEnabled(False)

        endSliderLayout = QHBoxLayout()
        endSliderLayout.setContentsMargins(0, 0, 0, 0)
        endSliderLayout.addWidget(self.autoEndSliderButton)
        endSliderLayout.addWidget(self.endMarkerTime)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addLayout(startSliderLayout)
        layout.addLayout(endSliderLayout)


        layout.addWidget(self.errorLabel)
        layout.addWidget(self.symmetrizeCheckbox)
        layout.addWidget(self.exportResolutionPercentage)
        layout.addWidget(self.exportFrameRate)
        layout.addWidget(self.exportSpeedRate)
        

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
        self.positionSlider.setValue(position)
        # convert to mm:ss:ms
        time = self.mediaPlayer.position()
        time = time / 1000
        # print(self.mediaPlayer.position())
        self.currentPlayTimeLabel.setText("{0:.2f}".format(time) + "s")

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.enableAllControls(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def saveAsGif(self):
        """Export video as GIF main method"""
        self.log("EXPORTING ... PLEASE WAIT")
        if ('.gif' in self.loadedFile):
            newFilePath = os.path.splitext(self.loadedFile)[0] + "_lazyGIF.gif"
      
        else:
            newFilePath = os.path.splitext(self.loadedFile)[0] + ".gif"


        time = self.mediaPlayer.position()
        time = time / 1000
        # print(self.mediaPlayer.position())
        self.currentPlayTimeLabel.setText("{0:.2f}".format(time).replace('.', ':') + "s")
        # print("{0:.2f}".format(time).replace('.', ':') + "s")


        # Get start and end times
        exportFrameRate        = float(self.exportFrameRate.text())
        desiredFPS             = exportFrameRate if exportFrameRate >= 1 or exportFrameRate <= self.videoFPS else self.videoFPS
        desiredExportSpeedRate = 1.0 if float(self.exportSpeedRate.text()) == "" or float(self.exportSpeedRate.text()) <= 0 else float(self.exportSpeedRate.text())

        if self.startMarkerTime.text() == "":
            startTime = 0
        else:
            startTime = float(self.startMarkerTime.text())
        if self.endMarkerTime.text() == "":
            endTime = float(self.mediaPlayer.duration() / 1000)
        else:
            endTime = float(self.endMarkerTime.text())
        if (self.symmetrizeCheckbox.isChecked()):
            def time_symetrize(clip):
                return concatenate_videoclips([clip, clip.fx( time_mirror )])
            clip = (VideoFileClip(self.loadedFile, audio=False)
                    .subclip(startTime, round(endTime, 1)) # (start, end) # https://zulko.github.io/moviepy/ref/Clip.html?highlight=subclip#moviepy.Clip.Clip.subclip
                    .resize(float(self.exportResolutionPercentage.text())) # output scaling
                    .fx( time_symetrize ) # mirror clip
                    .fx( speedx, desiredExportSpeedRate)
                    )
        else:
            clip = (VideoFileClip(self.loadedFile, audio=False)
                    .subclip(startTime, endTime) # (start, end) # https://zulko.github.io/moviepy/ref/Clip.html?highlight=subclip#moviepy.Clip.Clip.subclip
                    .resize(float(self.exportResolutionPercentage.text())) # output scaling
                    .fx( speedx, desiredExportSpeedRate)
                    )      

        clip.write_gif(newFilePath, fps=desiredFPS, fuzz=0, program='ffmpeg')

        # frames = int(clip.fps * clip.duration)
        # n_frames = clip.reader.nframes # number of frames in video

        self.log("saved at " + newFilePath)
        # if self.symmetrizeCheckbox.isChecked():
        #     self.statusBar.showMessage("Symmetrizing...")

        newFilePathDirectory = os.path.dirname(newFilePath)
        # subprocess.Popen(f'explorer {newFilePathDirectory}') # TODO: currently not working: redirects to documents folder instead.

        # open folder with gif
        # newWindow = QDialog()
        # newWindow.setWindowTitle("EXPORTED GIF")

        os.startfile(newFilePathDirectory)

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
        # copyPathButton = QPushButton(newWindow)
        # copyPathButton.setText("Copy path to clipboard")
        # copyPathButton.clicked.connect(lambda: copyPathToClipboard(newFilePathDirectory))


        # descriptionLabel.setStyleSheet("font-size: 20px;")
        # descriptionLabel.setGeometry(QRect(0, 0, 400, 50))
        # newWindow.setWindowFlags(Qt.WindowStaysOnTopHint)
        # newWindow.setFixedSize(400, 200)
        # newWindow.setStyleSheet("background-color: #1a1a1a;")
        # newWindow.setWindowModality(Qt.ApplicationModal)
        # newWindow.setAttribute(Qt.WA_DeleteOnClose)
        # newWindow.exec_()

        # msgbox = QMessageBox()
        # msgbox.setWindowTitle('Done Exporting!')
        # msgbox.setText(f'Video saved at {newFilePathDirectory}')
        # msgbox.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # msgbox.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    # info = InfoWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    player.show()
    # info.show()
    sys.exit(app.exec_())