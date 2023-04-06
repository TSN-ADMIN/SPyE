#!/usr/bin/python

#INFO, copied from Gedit Source Code Browser, (modified) module 'ctags.py'
#INFO, URL=https://github.com/MicahCarrick/gedit-source-code-browser

from pathlib import Path
import shlex
import subprocess as SP

from const.app import EXE, OUT_CTAGS


def ctags_version(executable=None):
    """
    Return the text output from the --version option to ctags or None if ctags
    executable cannot be found. Use executable for custom ctags builds and/or
    path.
    """
    args = shlex.split(f'{EXE["CTAGS"]} --version')
    try:
        res = SP.Popen(args, 0, shell=False, stdout=SP.PIPE, executable=executable)
        version = res.communicate()[0].decode('utf-8')  # bytes -> str
    except:
        version = '* not found *'
    return version


class CtagsTag:
    """
    Represents a ctags "tag" found in some source code.
    """
    def __init__(self, name):
        self.name = name
        self.file = None
        self.xcmd = None
        self.kind = None
        self.fields = {}


class CtagsKind:
    """
    Represents a ctags "kind" found in some source code such as "member" or
    "class".
    """
    def __init__(self, name):
        self.name = name
        self.lang = None


class CtagsParser:
    """
    Ctags Parser

    Parses the output of a ctags command into a list of tags and a dictionary
    of kinds.
    """
    def __init__(self):
        self.tags = []
        self.kinds = {}
        self.tree = {}  # not used

    def parse(self, command, executable=None):
        """
        Parse ctags tags from the output of a ctags command. For example:
        ctags -n --fields=fiKmnsStz -f - some_file.ext
        """
        args = shlex.split(command)
        res = SP.run(args, capture_output=True)
        if res.returncode != 0 or res.stderr:
            print(f'retcode=[{res.returncode}]\n stderr=[{res.stderr}]')
            return False

        with open(OUT_CTAGS, encoding='utf-8') as fil:
            text = fil.read()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@
        Path(OUT_CTAGS).unlink()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.parse_ctags(text)

        return True

    def parse_ctags(self, text):
        """
        Parses ctags text which may have come from a TAG file or from raw output
        from a ctags command.
        """
        for lin in text.splitlines():
            name = None
            file = None
            xcmd = None
            kind = None
            for idx, fld in enumerate(lin.split('\t')):
                if idx == 0:
                    tag = CtagsTag(fld)
                elif idx == 1:
                    tag.file = fld
                elif idx == 2:
                    tag.xcmd = fld
                elif idx > 2:
                    if ':' in fld:
                        key, val = fld.split(':')[0:2]
                        tag.fields[key] = val
                        if key == 'kind':
                            kind = CtagsKind(val)
                            if kind not in self.kinds:
                                self.kinds[val] = kind

            if kind is not None:
                if 'language' in tag.fields:
                    kind.lang = tag.fields['language']
                tag.kind = kind

            self.tags.append(tag)

        return True
