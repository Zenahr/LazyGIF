pyinstaller ^
LazyCUT.py ^
--name=LazyCUT ^
--hidden-import=pyqt5 ^
--icon=icon.ico ^
--noconsole ^
--add-data "icon-dark.png;." ^
--hidden-import=moviepy ^
--clean ^
--noconfirm ^