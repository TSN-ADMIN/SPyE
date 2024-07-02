#!/usr/bin/python

from pathlib import Path

from extern.configobj import ConfigObj
from extern.configobj.validate import Validator

from const.common import TXT_NIL
from .debug import DBG, me_


class RecentFileHistory(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.load()

    def default(self):
        DBG('RFH', f'{me_()}\n  File = {self.filename}\n')

        self['RecentFileHistory'] = {}
        self['RecentFileHistory']['Enable'] = True
        self['RecentFileHistory']['MaxItems'] = 25
        self['RecentFileHistory']['ReopenConfirm'] = True

        self['RecentFiles'] = {}

    def create(self):
        DBG('RFH', f'{me_()}\n  File = {self.filename}\n')

        # get default recent file history configuration
        self.default()

        # add blank lines and header before all sections, except the first
        first_sec = 'RecentFileHistory'
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Comment header for %s' % sec)

        self.save()

#FIX, not used: obsolete?
    def load(self):
        DBG('RFH', f'{me_()}\n  File = {self.filename}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # for sec in self:
        #     print(sec)
        #     for key in self[sec]:
        #         print(' ', key, self[sec][key])
        #     print()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, not used: obsolete?
    def save(self):
        DBG('RFH', f'{me_()}\n  File = {self.filename}\n')

        self.write()
