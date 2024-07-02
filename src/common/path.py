#!/usr/bin/python

from pathlib import Path

# from conf.debug import DBG, DEBUG, me_


def resolve_path(*path):
    # DBG('GEN', f'{me_()}')
    return Path(*path).resolve()


def cwd():
    return str(Path.cwd())
