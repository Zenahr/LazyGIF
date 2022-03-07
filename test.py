# import moviepy.editor as mp
# clip = mp.VideoFileClip("slurp.mp4")
# clip_resized = clip.resize(height=1920, width=1080) # make the height 360px ( According to moviePy documenation The width is then computed so that the width/height ratio is conserved.)
# clip_resized.write_videofile("movie_resized.mp4", fps=30, bitrate="2000k", audio_bitrate="20k", preset="medium", threads=6)


# from qtpy.QtCore import Qt
# from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget

# from superqt import QDoubleRangeSlider, QDoubleSlider, QRangeSlider

# app = QApplication([])

# w = QWidget()

# sld1 = QDoubleSlider(Qt.Orientation.Horizontal)
# sld2 = QDoubleRangeSlider(Qt.Orientation.Horizontal)
# rs = QRangeSlider(Qt.Orientation.Horizontal)

# sld1.valueChanged.connect(lambda e: print("doubslider valuechanged", e))

# sld2.setMaximum(1)
# sld2.setValue((0.2, 0.8))
# sld2.valueChanged.connect(lambda e: print("valueChanged", e))
# sld2.sliderMoved.connect(lambda e: print("sliderMoved", e))
# sld2.rangeChanged.connect(lambda e, f: print("rangeChanged", (e, f)))

# w.setLayout(QVBoxLayout())
# w.layout().addWidget(sld1)
# w.layout().addWidget(sld2)
# w.layout().addWidget(rs)
# w.show()
# w.resize(500, 150)
# app.exec_()




"""
 
   _        _    ____  _____ _     _____ ____  
  | |      / \  | __ )| ____| |   | ____|  _ \ 
  | |     / _ \ |  _ \|  _| | |   |  _| | | | |
  | |___ / ___ \| |_) | |___| |___| |___| |_| |
  |_____/_/   \_\____/|_____|_____|_____|____/ 
                                               
 
"""

# from qtpy.QtCore import Qt
# from qtpy.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

# from superqt import (
#     QLabeledDoubleRangeSlider,
#     QLabeledDoubleSlider,
#     QLabeledRangeSlider,
#     QLabeledSlider,
# )

# app = QApplication([])

# ORIENTATION = Qt.Orientation.Horizontal

# w = QWidget()
# qls = QLabeledSlider(ORIENTATION)
# qls.valueChanged.connect(lambda e: print("qls valueChanged", e))
# qls.setRange(0, 500)
# qls.setValue(300)


# qlds = QLabeledDoubleSlider(ORIENTATION)
# qlds.valueChanged.connect(lambda e: print("qlds valueChanged", e))
# qlds.setRange(0, 1)
# qlds.setValue(0.5)
# qlds.setSingleStep(0.1)

# qlrs = QLabeledRangeSlider(ORIENTATION)
# qlrs.valueChanged.connect(lambda e: print("QLabeledRangeSlider valueChanged", e))
# qlrs.setValue((20, 60))

# qldrs = QLabeledDoubleRangeSlider(ORIENTATION)
# qldrs.valueChanged.connect(lambda e: print("qlrs valueChanged", e))
# qldrs.setRange(0, 1)
# qldrs.setSingleStep(0.01)
# qldrs.setValue((0.2, 0.7))


# w.setLayout(
#     QVBoxLayout() if ORIENTATION == Qt.Orientation.Horizontal else QHBoxLayout()
# )
# w.layout().addWidget(qls)
# w.layout().addWidget(qlds)
# w.layout().addWidget(qlrs)
# w.layout().addWidget(qldrs)
# w.show()
# w.resize(500, 150)
# app.exec_()


