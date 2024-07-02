#!/usr/bin/python

from pathlib import Path

from extern.configobj import ConfigObj
from extern.configobj.validate import Validator

from const.common import TXT_NIL
from .debug import DBG, me_


class Trace(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.load()

    def default(self):
        DBG('TRC', f'{me_()}\n  File = {self.filename}\n')

        self['Files'] = {}
        self['Classes'] = {}
        self['Functions'] = {}

    def create(self):
        DBG('TRC', f'{me_()}\n  File = {self.filename}\n')

        # get default trace configuration
        self.default()

        # add blank lines and header before all sections, except the first
        first_sec = 'Files'
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Comment header for %s' % sec)

        self.save()

#FIX, not used: obsolete?
    def load(self):
        DBG('TRC', f'{me_()}\n  File = {self.filename}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # for sec in self:
        #     print(sec)
        #     for key in self[sec]:
        #         print(' ', key, self[sec][key])
        #     print()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, not used: obsolete?
    def save(self):
        DBG('TRC', f'{me_()}\n  File = {self.filename}\n')

        self.write()
