from subprocess import check_call, Popen, DEVNULL


from typing import Literal, List

from winwin.config import Config

import time
import shlex



def open_alacritty_gui(
    cfg: Config,
    title: str,
    command: List[str],
    opt_group: Literal['main', 'secondary'],
) -> None:
    opts = cfg.get_screen_opts(opt_group)
    cmd = ['nohup', cfg.alacritty_path, '--title', title]
    # FIXME: remove this hack
    cmd.extend(['--working-directory', '/Users/peter/dotfiles.git/winwin.git'])

    # FIXME: also remove this hack
    cmd.extend(['-o', 'window.decorations=full'])
    for name, val in opts.items():
        if val is not None:
            cmd.extend(['-o', '{}={}'.format(name, val)])
    cmd.append('--command')
    cmd.extend(['/bin/bash', '-c', shlex.join(command) + ' || sleep 10'])
    check_call([
        '/bin/bash', '-c', shlex.join(cmd) + ' &',
    ], stdout=DEVNULL, stderr=DEVNULL)
