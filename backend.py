from moviepy.editor import *


# https://zulko.github.io/blog/2014/01/23/making-animated-gifs-from-video-files-with-python/


# # CONVERT VIDEO TO GIF
# clip = (VideoFileClip("frozen_trailer.mp4")
#         .subclip((1,22.65),(1,23.2)) # (start, end)
#         .resize(0.3)) # resize to 30% of its original size
# clip.write_gif("use_your_head.gif")




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


# # LOOP VIA FADING
# castle = (VideoFileClip("frozen_trailer.mp4", audio=False)
#           .subclip(22.8,23.2)
#           .speedx(0.2)
#           .resize(.4))

# d = castle.duration
# castle = castle.crossfadein(d/2)

# composition = (CompositeVideoClip([castle,
#                                    castle.set_start(d/2),
#                                    castle.set_start(d)])
#                .subclip(d/2, 3*d/2))

# composition.write_gif('castle.gif', fps=5,fuzz=5)



# # LOOP VIA FADING AND FIX VIA TAKING A FREEZE SHOT
"""
The next clip (from the movie Charade) was almost loopable: you can see Carry Grant smiling, then making a funny face, then coming back to normal. The problem is that at the end of the excerpt Cary is not exactly in the same position, and he is not smiling as he was at the beginning. To correct this, we take a snapshot of the first frame and we make it appear progressively at the end. This seems to do the trick.
"""
carry = (VideoFileClip("charade.mp4", audio=False)
         .subclip((1,51,18.3),(1,51,20.6))
         .crop(x1=102, y1=2, x2=297, y2=202))

d = carry.duration
snapshot = (carry.to_ImageClip()
            .set_duration(d/6)
            .crossfadein(d/6)
            .set_start(5*d/6))

composition = CompositeVideoClip([carry, snapshot])
composition.write_gif('carry.gif', fps=carry.fps, fuzz=3)