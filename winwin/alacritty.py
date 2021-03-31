import shlex
import time
from subprocess import check_call, Popen, DEVNULL
from typing import Literal, List

from winwin.config import Config


def open_alacritty_gui(
    cfg: Config,
    title: str,
    command: List[str],
    opt_group: Literal['main', 'secondary'],
) -> None:
    opts = cfg.get_screen_opts(opt_group)
    cmd = ['nohup', cfg.alacritty_path, '--title', title]

    # FIXME: also remove this hack
    cmd.extend(['-o', 'window.decorations=full'])
    for name, val in opts.items():
        if val is not None:
            cmd.extend(['-o', '{}={}'.format(name, val)])
    cmd.append('--command')
    # This is just here to try and keep the window open for a bit if the
    # command crashes
    cmd.extend(['/bin/bash', '-c', shlex.join(command) + ' || sleep 10'])
    check_call([
        '/bin/bash', '-i', '-c', shlex.join(cmd) + ' &',
    ], stdout=DEVNULL, stderr=DEVNULL)
