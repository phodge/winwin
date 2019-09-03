import re
import subprocess
from typing import List


def open_terminal_gui(
    title: str,
    cmd: List[str],
    *,
    w: int = 80, h: int = 24,
    zoom: float = 1.0,
) -> None:
    subprocess.check_call([
        'gnome-terminal',
        '--title=' + title,
        '--zoom={}'.format(zoom),
        '--hide-menubar',
        #'--full-screen',
        # make the geometry a reasonable size in case the screen is resized
        # down
        '--geometry={}x{}'.format(w, h),
        '--',
    ] + cmd)


def focus_window(title):
    subprocess.check_call([
        'xdotool',
        # FIXME: using re.escape() isn't ideal here as the exact special
        # characters may differ from the regex engine used by xdotool
        'search', '--name', '^' + re.escape(title) + '$',
        'windowfocus',
    ])


def move_window(title, x, fullscreen):
    # escape special characters in window title

    cmd = [
        'xdotool',
        # FIXME: using re.escape() isn't ideal here as the exact special
        # characters may differ from the regex engine used by xdotool
        'search', '--name', '^' + re.escape(title) + '$',
        'windowmove', str(x), '0',
        'windowfocus',
    ]

    if fullscreen:
        cmd.extend(['key', 'F11'])
    else:
        cmd.extend(['windowsize', '50%', '100%'])
    subprocess.check_call(cmd)
