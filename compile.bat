pyinstaller ^
LazyGIF.py ^
--name=LazyGIF ^
--hidden-import=pyqt5 ^
--icon=icon.ico ^
--noconsole ^
--add-data "icon.png;/." ^
--hidden-import=moviepy ^
--clean ^