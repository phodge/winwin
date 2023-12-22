#import xdg.BaseDirectory
import json
import os
import os.path
import sys
from pathlib import Path
from shlex import quote
from subprocess import PIPE, run
from typing import Dict, List, Literal, Optional, Set, Tuple


def get_self_cmd(args: List[str]) -> List[str]:
    cmd = [sys.executable, '-m', 'winwin.cli']
    cmd.extend(args)
    return cmd


def get_self_cmd_str(args: List[str]) -> str:
    return ' '.join([quote(x) for x in get_self_cmd(args)])


class UpstreamConfig:
    def __init__(
        self,
        label: str,
        local_clone: Path,
        search_prefix: str,
        ignore_branches: list[str],
    ) -> None:
        assert len(search_prefix)

        self._label: str = label
        self._local_clone: Path = local_clone
        self._search_prefix: str = search_prefix
        self._ignore_branches: Set[str] = set(ignore_branches)

    @property
    def label(self) -> str:
        return self._label

    def get_upstream_branches(self) -> List[Tuple[str, str, str]]:
        """Returns tuples of commitsha, refname, subject"""
        branches = []
        cmd = [
            'git',
            'branch',
            '--remote',
            '--format',
            '%(objectname)|%(refname:lstrip=3)|%(contents:subject)',
        ]
        result = run(cmd, cwd=self._local_clone, check=True, stdout=PIPE, encoding='utf-8')
        for line in result.stdout.splitlines():
            parts = line.split('|', 2)
            assert len(parts) == 3
            refname = parts[1]
            if refname.startswith(self._search_prefix) and refname not in self._ignore_branches:
                branches.append((parts[0], refname, parts[2]))
        return branches


class Config:
    def __init__(self):
        self._load()

    def _load(self):
        self._config = {}

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
    def allow_multiple_screens(self) -> bool:
        return self._config.get('allow_multiple_screens', True)

    @property
    def shell_executable(self) -> str:
        return self._config.get('default_shell', '/bin/bash')

    @property
    def terminal_is_alacritty(self) -> bool:
        return self._config.get('terminal_app') == 'alacritty'

    @property
    def alacritty_path(self) -> str:
        return self._config.get('alacritty_path', 'alacritty')

    def get_alacritty_screen_opts(self, screen_name: Literal['main', 'secondary']) -> Dict[str, str]:
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

    def get_upstream_repositories(self) -> List[UpstreamConfig]:
        upstreams = []
        for entry in self._config.get('upstream_repositories', []):
            ignore_branches = entry.get('ignore_branches', [])
            upstreams.append(UpstreamConfig(
                entry.get('label', os.path.basename(entry['local_clone'])),
                Path(entry['local_clone']).expanduser(),
                entry['search_prefix'],
                ignore_branches,
            ))
        return upstreams
