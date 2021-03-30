#import xdg.BaseDirectory
import json
import os
import sys
from shlex import quote
from pathlib import Path
from typing import List


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
