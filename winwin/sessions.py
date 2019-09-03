import logging
import re
from pathlib import Path
from typing import List

import libtmux

from winwin.constants import Platforms


class SessionNotFound(Exception):
    pass


class TmuxPaneInfo:
    def __init__(self, cwd: Path, command: str):
        self._cwd = cwd
        self._command = command

    @classmethod
    def loadFromLibtmuxPane(class_, pane: libtmux.Pane) -> "TmuxPaneInfo":
        # TODO: handle tmux panes running things other than bash

        # NOTE: you can use pane.pane_current_command to get the current
        # command name, but it's not very comprehensive

        # TODO:
        # - for each child process, we need to ...
        #   - nvim: tell the nvim process to :mkession to a specific file
        #   - ssh: ???
        #   - tail: make note of the args so that we can restart the thing
        #   - complex pipelines: ask the user if they want to restart the
        #     thing?

        __expr = pane  # TODO: remove this debug
        print('pane = %s:' % type(__expr))
        for _ in dir(__expr):
            if not hasattr(__expr, _):
                print('  .%s = <not set>' % _)
            elif callable(getattr(__expr, _)):
                print('  .%s()' % _)
            else:
                print('  .%s = %r' % (_, getattr(__expr, _)))
        print('}')
        del __expr  # TODO: remove this debug
        print('pane.items() = {')  # TODO
        for _ in pane.items():
            print('  '+repr(_[0])+': '+repr(_[1])+',')
        print('}')

        pane_pid = pane.get('pane_pid')

        # TODO: what was running in the pane?

        # what programs are running in this pane?

        import pprint
        print('pane_pid = ' + pprint.pformat(pane_pid))  # noqa TODO

        # get a comprehensive list of what's running in each pane

        raise Exception("TODO: get a pane")  # noqa
        instance = class_(
        )
        return instance


class TmuxWindowInfo:
    _index: str
    _title: str
    _panes: List[TmuxPaneInfo]

    @classmethod
    def loadFromLibtmuxWindow(
        class_,
        window: libtmux.Window,
    ) -> "TmuxWindowInfo":
        instance = class_(
            index=window.get('window_index'),
            title=window.get('window_name'),
        )

        # TODO: save the window layout if there's more than 1 pane
        # - window.get('window_layout')

        # TODO: capture/restore these also:
        # - window.get('window_flags')
        # - window.get('window_active')
        # - window.get('window_activity_flag')
        # - window.get('window_silence_flag')

        # add the panes
        for pane in window.list_panes():
            instance.addPane(TmuxPaneInfo.loadFromLibtmuxPane(pane))

        return instance

    def __init__(self, *, index: str, title: str):
        self._index = index
        self._title = title

    def addPane(self, info: TmuxPaneInfo) -> None:
        self._panes.append(info)


class TmuxSessionInfo:
    _name: str
    _windows: List[TmuxWindowInfo] = []

    @classmethod
    def loadFromLibtmuxSession(
        class_,
        session: libtmux.Session
    ) -> "TmuxSessionInfo":
        # FIXME: we need to save option values so they can be restored
        # opts = session.show_options()
        #
        # FIXME: we need a way to retrieve the sessions working-directory
        # (normally set with 'new-session -c DIR')

        # use list-panes to get info about all the windows+panes in our session
        instance = class_(session.get('session-name'))

        for window in session.list_windows():
            instance._windows.append(
                TmuxWindowInfo.loadFromLibtmuxWindow(window))

        return instance

    def __init__(self, name: str):
        self._name = name

        # TODO: get these as well
        self._windows = []

    def exportv1(self) -> any:
        return {
            "name": self._name,
            "windows": self._windows,
        }


class SessionInfo:
    _name: str
    _platform = Platforms

    # onlyu when _platform == Platforms.TERMINAL_TMUX
    _primary: TmuxSessionInfo = None
    _other: List[TmuxSessionInfo] = []

    """All the information needed to restart a session"""
    def __init__(self, name: str, platform: Platforms):
        self._name = name
        self._platform = platform

    def setPrimaryTmuxSession(self, session: TmuxSessionInfo) -> None:
        assert self._platform is Platforms.TERMINAL_TMUX
        assert self._primary is None
        self._primary = session

    def addOtherSession(self, session: TmuxSessionInfo) -> None:
        assert self._platform is Platforms.TERMINAL_TMUX
        assert self._primary and session is not self._primary
        self._other.append(session)

    def exportv1(self) -> any:
        info = {
            '__version__': 1,
            'session_name': self._name,
            'platform': self._platform.value,
        }
        if self._platform is Platforms.TERMINAL_TMUX:
            info['tmux_primary'] = self._primary.exportv1()
            info['tmux_other'] = [other.exportv1() for other in self._other]
        return info


def get_tmux_session_info(session_name: str) -> TmuxSessionInfo:
    tmux = libtmux.Server()

    name2_regex = re.compile(r'^%s-\d+$' % re.escape(session_name))

    # find the primary/secondary sessions by name
    sess1: libtmux.Session = None
    sess2: libtmux.Session = None
    for sess in tmux.list_sessions():
        if sess.get('session_name') == session_name:
            if sess1 is not None:
                raise Exception('Multiple tmux sessions with name {!r}'.format(
                    session_name))
            sess1 = sess
        elif name2_regex.match(sess.get('session_name')):
            if sess2 is not None:
                logging.warn('Found multiple secondary tmux sessions')
            else:
                sess2 = sess

    if not sess1:
        raise SessionNotFound("Couldn't find session %r" % name_re)  # noqa

    info = SessionInfo(session_name, Platforms.TERMINAL_TMUX)
    info.setPrimaryTmuxSession(TmuxSessionInfo.loadFromLibtmuxSession(sess1))
    info.addOtherSession(TmuxSessionInfo.loadFromLibtmuxSession(sess2))
    return info
