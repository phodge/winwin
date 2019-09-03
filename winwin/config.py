#import xdg.BaseDirectory
import sys
from shlex import quote
from typing import List

CONFIG_NAME = 'winwin'


def get_self_cmd(args: List[str]) -> List[str]:
    cmd = [sys.executable, '-m', 'winwin.cli']
    cmd.extend(args)
    return cmd


def get_self_cmd_str(args: List[str]) -> str:
    return ' '.join([quote(x) for x in get_self_cmd(args)])
