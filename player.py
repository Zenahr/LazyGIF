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
    vfx,
    concatenate
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
        self.exportResolutionPercentage.setEnabled(flag)

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("InstaGif - Instantly Create GIFs") 
        # self.setWindowIcon(QIcon("icon.png"))
        self.setWindowFlags(Qt.WindowStaysOnTopHint) # dev only
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
        self.exportResolutionPercentage.setPlaceholderText("0.5")
        self.exportResolutionPercentage.setText("0.5")


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
        layout.addWidget(self.exportResolutionPercentage)
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
        newFilePath = os.path.splitext(self.loadedFile)[0] + ".gif"


        time = self.mediaPlayer.position()
        time = time / 1000
        # print(self.mediaPlayer.position())
        self.currentPlayTimeLabel.setText("{0:.2f}".format(time).replace('.', ':') + "s")
        # print("{0:.2f}".format(time).replace('.', ':') + "s")


        # Get start and end times
        if self.startMarkerTime.text() == "":
            startTime = 0
        else:
            startTime = int(self.startMarkerTime.text())
        if self.endMarkerTime.text() == "":
            endTime = self.mediaPlayer.duration() / 1000
        else:
            endTime = int(self.endMarkerTime.text())
        print(startTime, endTime)
        if (self.symmetrizeCheckbox.isChecked()):
            def time_symetrize(clip):
                return concatenate([clip, clip.fx( vfx.time_mirror )])
            clip = (VideoFileClip(self.loadedFile)
                    .subclip(startTime, endTime) # (start, end) # https://zulko.github.io/moviepy/ref/Clip.html?highlight=subclip#moviepy.Clip.Clip.subclip
                    .resize(float(self.exportResolutionPercentage.text())) # output scaling
                    .fx( time_symetrize ) # mirror clip
                    )
        else:
            clip = (VideoFileClip(self.loadedFile)
                    .subclip(startTime, endTime) # (start, end) # https://zulko.github.io/moviepy/ref/Clip.html?highlight=subclip#moviepy.Clip.Clip.subclip
                    .resize(float(self.exportResolutionPercentage.text())) # output scaling
                    )      

        clip.write_gif(newFilePath, fps=20, fuzz=0, program='ffmpeg')

        # frames = int(clip.fps * clip.duration)
        # n_frames = clip.reader.nframes # number of frames in video

        self.log("saved at " + newFilePath)
        # if self.symmetrizeCheckbox.isChecked():
        #     self.statusBar.showMessage("Symmetrizing...")

        newFilePathDirectory = os.path.dirname(newFilePath)
        subprocess.Popen(f'explorer {newFilePathDirectory}')
 

# # SYMMETRICE GIF
# def time_symetrize(clip):
#     """ Returns the clip played forwards then backwards. In case
#     you are wondering, vfx (short for Video FX) is loaded by
#     >>> from moviepy.editor import * """
#     return concatenate([clip, clip.fx( vfx.time_mirror )])

# clip = (VideoFileClip("frozen_trailer.mp4", audio=False)
#         .subclip(36.5,36.9)
#         .resize(0.5)
#         .crop(x1=189, x2=433)
#         .fx( time_symetrize ))

# clip.write_gif('sven.gif', fps=15, fuzz=2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())