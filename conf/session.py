#!/usr/bin/python

from pathlib import Path

from extern.configobj import ConfigObj
from extern.configobj.validate import Validator

from const.common import TXT_NIL
from common.util import me_
from conf.debug import DEBUG


class Session(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.read()

    def default(self):
        if DEBUG['SSN']: print(f'{me_()}\n  File = {self.filename}\n')

        self['Session'] = {}
        self['Session']['ActiveFile'] = TXT_NIL

    def create(self):
        if DEBUG['SSN']: print(f'{me_()}\n  File = {self.filename}\n')

        # get default session configuration
        self.default()

        # add blank lines and header before all sections, except the first
        first_sec = 'Session'
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Comment header for %s' % sec)

        self.commit()

#FIX, not used: obsolete?
    def read(self):
        if DEBUG['SSN']: print(f'{me_()}\n  File = {self.filename}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # for sec in self:
        #     print(sec)
        #     for key in self[sec]:
        #         print(' ', key, self[sec][key])
        #     print()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, not used: obsolete?
    def commit(self):
        if DEBUG['SSN']: print(f'{me_()}\n  File = {self.filename}\n')

        self.write()
