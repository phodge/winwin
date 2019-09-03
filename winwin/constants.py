import enum
#import os
#from pathlib import Path


# types of platforms
@enum.unique
class Platforms(enum.Enum):
    TERMINAL_TMUX = 'terminal/tmux'
    KITTY = 'kitty'
    NVIMUX = 'nvimux'
    ONI = 'oni'
