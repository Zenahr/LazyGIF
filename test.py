from moviepy.editor import (
    VideoFileClip,
)

clip = (VideoFileClip('D:\\VIDEOS\APEX LEGENDS\\CHEATER FOOTAGE\\2.mp4')
        .subclip((0)) # (start, end) # https://zulko.github.io/moviepy/ref/Clip.html?highlight=subclip#moviepy.Clip.Clip.subclip
        .resize(1.0) # output scaling
        )

duration = clip.duration
print(duration) # seconds.milliseconds
framecount = clip.reader.nframes
print(framecount) # number of frames

# clip.write_gif(newFilePath, fps=20, fuzz=0, program='ffmpeg')