#!/usr/bin/python

from pathlib import Path

# from common.util import me_
# from conf.debug import DEBUG


def resolve_path(*path):
    # if DEBUG['GEN']: print(f'{me_()}')
    return Path(*path).resolve()


def cwd():
    return str(Path.cwd())
