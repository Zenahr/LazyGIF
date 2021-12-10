pyinstaller ^
LazyGIF.py ^
--name=LazyGIF ^
--onefile ^
--icon=icon.ico ^
--add-data "icon.png;/." ^
--hidden-import=pyqt5 ^
--hidden-import=moviepy ^
--hidden-import=imageio_ffmpeg ^