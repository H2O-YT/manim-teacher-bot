from manim import *


config.frame_width = config.frame_height
config.pixel_height = 1000
config.pixel_width = 1000
config.background_color = WHITE


class ProfilePicture(Scene):

    def construct(self):
        banner = ManimBanner(dark_theme=False)
        self.add(banner)