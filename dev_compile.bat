pyinstaller ^
--name=LazyGIF ^
--onefile player.py ^
--icon=icon.ico ^
--add-data "icon.png;/." ^
--hidden-import=pyqt5 ^
--hidden-import=moviepy ^
--hidden-import=imageio_ffmpeg ^