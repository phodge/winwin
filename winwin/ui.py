import time

import click

from winwin.config import get_self_cmd, Config
from winwin.constants import Platforms


def ui_new_session(name: str) -> None:
    cfg = Config()

    # FIXME: don't allow re-using session names

    # ask what platform name?
    if cfg.force_platform:
        platform = cfg.force_platform
    else:
        platform = click.prompt('What platform?',
                                type=click.Choice([p.value for p in Platforms]),
                                default=Platforms.TERMINAL_TMUX.value)

    # TODO: templates:
    # - if the user has created any templates, ask if they want to reuse an
    #   existing one

    # should the session be running on a remote host?
    remote_host = None
    if cfg.allow_remote_sessions and click.confirm('Start session on a remote host?', default=False):
        remote_host = click.prompt("Enter a remote host name")

        # FIXME: confirm we can connect to the host and bail out if we can't
        # get to it

    # do they want a 2nd terminal window on the second screen?
    want_2nd_terminal = click.confirm(
        'Show 2nd terminal on other screen?',
        default=None,
    )

    if platform == Platforms.TERMINAL_TMUX.value:
        begin_session_terminal_tmux(name, remote_host, want_2nd_terminal)
    else:
        raise Exception("TODO: spawn session using platform %r" % (platform, ))  # noqa


def begin_session_terminal_tmux(name, remote_host, want_2nd_terminal):
    from winwin.ubuntu import focus_window, move_window, open_terminal_gui

    # window names
    title1 = 'SESSION: {}'.format(name)
    title2 = 'SESSION: {} (2)'.format(name)

    # FIXME: what to do for a shell if running on OS X?

    # first screen
    open_terminal_gui(
        title1,
        get_self_cmd(['enter-main-session', name]),
    )

    # move the first window to the 2nd screen; maximise it
    time.sleep(1)
    move_window(title1, 1980 + 1, True)

    # 2nd screen
    if want_2nd_terminal:
        open_terminal_gui(
            title2,
            get_self_cmd(['enter-second-session', name]),
        )

        # FIXME: I sometimes get a BadWindow error from xdotool when attempting
        # to move/resize the 2nd window. I think it's a race condition so for
        # now I'm just waiting a bit before moving/resizing the 2nd window
        time.sleep(1)

        # move window to the 3rd screen, maximise it
        move_window(title2, 1980 + 1980 + 10, False)
        focus_window(title1)
