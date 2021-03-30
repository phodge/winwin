#import xdg.BaseDirectory
import json
import os
import sys
from shlex import quote
from pathlib import Path
from typing import List, Optional, Literal, Dict


def get_self_cmd(args: List[str]) -> List[str]:
    cmd = [sys.executable, '-m', 'winwin.cli']
    cmd.extend(args)
    return cmd


def get_self_cmd_str(args: List[str]) -> str:
    return ' '.join([quote(x) for x in get_self_cmd(args)])


class Config:
    def __init__(self):
        self._load()

    def _load(self):
        HOME = os.getenv('HOME')
        if not HOME:
            return

        configpath = Path(HOME) / '.config/winwin.json'
        if not configpath.exists():
            return

        self._config = json.loads(configpath.read_text())

    @property
    def force_platform(self) -> Optional[str]:
        return self._config.get('force_platform')

    @property
    def allow_remote_sessions(self) -> bool:
        return True if self._config.get('remote_sessions') else False

    @property
    def terminal_is_alacritty(self) -> bool:
        return self._config.get('terminal_app') == 'alacritty'

    @property
    def alacritty_path(self) -> str:
        return self._config.get('alacritty_path', 'alacritty')

    def get_screen_opts(self, screen_name: Literal['main', 'secondary']) -> Dict[str, str]:
        if screen_name == 'main':
            data = {
                'window.dimensions.columns': self._config.get('main_screen_columns'),
                'window.dimensions.lines': self._config.get('main_screen_lines'),
                'window.position.x': self._config.get('main_screen_x'),
                'window.position.y': self._config.get('main_screen_y'),
                # FIXME: this seems to result in a window which isn't
                # fullscreen but also doesn't have any title bar
                #'window.startup_mode': 'SimpleFullscreen' if self._config.get('main_screen_fullscreen') else None,
            }
        elif screen_name == 'secondary':
            data = {
                'window.dimensions.columns': self._config.get('main_screen_columns'),
                'window.dimensions.lines': self._config.get('main_screen_lines'),
                'window.position.x': self._config.get('main_screen_x'),
                'window.position.y': self._config.get('main_screen_y'),
                # FIXME: this seems to result in a window which isn't
                # fullscreen but also doesn't have any title bar
                #'window.startup_mode': 'SimpleFullscreen' if self._config.get('main_screen_fullscreen') else None,
            }
        else:
            # should never happen
            raise NotImplementedError()

        return {k: str(v) for k, v in data.items() if v is not None}
