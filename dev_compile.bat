pyinstaller ^
LazyCUT.py ^
--name=LazyCUT ^
--onefile ^
--icon=icon.ico ^
--add-data "icon-dark.png;." ^
--hidden-import=pyqt5 ^
--hidden-import=moviepy ^
--hidden-import=imageio_ffmpeg ^