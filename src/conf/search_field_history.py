#!/usr/bin/python

from pathlib import Path

from extern.configobj import ConfigObj
from extern.configobj.validate import Validator

from const.common import TXT_NIL
from const import glb
from .debug import DBG, me_


class SearchFieldHistory(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.load()

    def default(self):
        DBG('SFH', f'{me_()}\n  File = {self.filename}\n')

        self['SearchFieldHistory'] = {}
        self['SearchFieldHistory']['Enable'] = True
        self['SearchFieldHistory']['MaxItems'] = 25

        self['FindHistory'] = {}
        self['ReplaceHistory'] = {}
        self['WhereHistory'] = {}

    def create(self):
        DBG('SFH', f'{me_()}\n  File = {self.filename}\n')

        # get default search field history configuration
        self.default()

        # add blank lines and header before all sections, except the first
        first_sec = 'SearchFieldHistory'
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Comment header for %s' % sec)

        self.save()

#FIX, not used: obsolete?
    def load(self):
        DBG('SFH', f'{me_()}\n  File = {self.filename}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # for sec in self:
        #     print(sec)
        #     for key in self[sec]:
        #         print(' ', key, self[sec][key])
        #     print()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, not used: obsolete?
    def save(self):
        DBG('SFH', f'{me_()}\n  File = {self.filename}\n')


        # save lists of search field history
        if not glb.SFH['SearchFieldHistory']['Enable']:
            return

        for pfx, fld in (('Find', 'fnd'), ('Replace', 'rpl'), ('Where', 'whr')):
            sfh_lst = getattr(glb.SCH, f'txc_{fld}').his_lst
            sec = f'{pfx}History'
            self[sec] = {}
            for cnt in range(len(sfh_lst)):
                self[sec][str(cnt)] = sfh_lst[cnt]

            DBG('CFG', '\n  sfh_lst = %s\n' % sfh_lst)

        self.write()

    def apply(self):
        # create lists of search field history
        if not glb.SFH['SearchFieldHistory']['Enable']:
            return

        for pfx, fld in (('Find', 'fnd'), ('Replace', 'rpl'), ('Where', 'whr')):
            sfh_lst = getattr(glb.SCH, f'txc_{fld}').his_lst
            sec = f'{pfx}History'
            # cnt = 0
            # while True:
            #     key = str(cnt)
            #     if key in glb.SFH[sec]:
            for key in self[sec]:
                    val = self[sec][key]
                    sfh_lst.append(val)
                # else:
                #     break
                # cnt += 1
            DBG('CFG', '\n  sfh_lst = %s\n' % sfh_lst)
