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
symmetrize
target filesize: use this textfield to make sure file can be exported to Discord, etc. (will try to keep the highest quality and frame rate possible)
regarding that, have a radio button group to choose between:
    - prioritize resolution
    - prioritize frame rate
"""


"""
InnoSetup: e process of adding custom verbs to a file's shortcut menu is described in the Extending Shortcut Menus and Verbs and File Associations topics. If you prefer a simpler way, you can also just put a shortcut to your EXE in the SendTo folder.
"""

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
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
        )
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys
import os
import subprocess

from moviepy.editor import (
    VideoFileClip,
)

class VideoWindow(QMainWindow):

    def log(self, msg):
        self.statusBar.showMessage(msg)

    def enableAllControls(self, flag=True):
        self.startMarkerTime.setEnabled(flag)
        self.endMarkerTime.setEnabled(flag)
        self.symmetrizeCheckbox.setEnabled(flag)
        self.playButton.setEnabled(flag)
        self.convertToGifButton.setEnabled(flag)

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("InstaGif - Instantly Create GIFs") 
       
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
    

        # Other stuff
        self.startMarkerTime    = QLineEdit(self)
        self.startMarkerTime.setStatusTip("Start Marker Time")
        self.startMarkerTime.setEnabled(False)
        self.startMarkerTime.setPlaceholderText("mm:ss:ms")

        self.endMarkerTime      = QLineEdit(self)
        self.endMarkerTime.setStatusTip("End Marker Time")
        self.endMarkerTime.setEnabled(False)
        self.endMarkerTime.setPlaceholderText("mm:ss:ms")

        self.symmetrizeCheckbox = QCheckBox("Symmetrize")
        self.symmetrizeCheckbox.setEnabled(False)
        self.symmetrizeCheckbox.setChecked(False)

        self.convertToGifButton = QPushButton("Export As GIF")
        self.convertToGifButton.setStatusTip('Export video as GIF')
        self.convertToGifButton.clicked.connect(self.saveAsGif)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open Video', self)        
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
        fileMenu.addAction(devFileAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.currentPlayTimeLabel)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)
        layout.addWidget(self.startMarkerTime)
        layout.addWidget(self.endMarkerTime)
        layout.addWidget(self.symmetrizeCheckbox)
        layout.addWidget(self.convertToGifButton)


        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

        self.enableAllControls(False) # Disable all controls on startup.
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

    def openTestFile(self):
        # NOTE: dev only
        self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile("C:\\Users\\STUDIUM\\Videos\\Apex Legends\\CHEATER FOOTAGE\\2.mp4")))
        self.enableAllControls()
        self.mediaPlayer.play()
        self.loadedFile = "C:\\Users\\STUDIUM\\Videos\\Apex Legends\\CHEATER FOOTAGE\\2.mp4" # TODO: replace with simple call of currently loaded file on onMediaLoaded
        print(self.loadedFile)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        print(self.mediaPlayer.position())
        self.currentPlayTimeLabel.setText(str(position))

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
        newFilePath = os.path.splitext(self.loadedFile)[0] + ".gif"

        # Get start and end times
        # startTime = self.startMarkerTime.text()
        # endTime = self.endMarkerTime.text()

        clip = (VideoFileClip(self.loadedFile)
                .subclip((0)) # (start, end)
                .resize(1.0) # output scaling
                )
        clip.write_gif(newFilePath, fps=20, fuzz=0, program='ffmpeg')


        self.log("saved at " + newFilePath)
        # if self.symmetrizeCheckbox.isChecked():
        #     self.statusBar.showMessage("Symmetrizing...")

        newFilePathDirectory = os.path.dirname(newFilePath)
        subprocess.Popen(f'explorer {newFilePathDirectory}')
 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())