#!/usr/bin/python

import beeprint

from pathlib import Path

from extern.configobj import ConfigObj
from extern.configobj.validate import Validator

from .debug import DBG, DEBUG, dbf, me_
from const.common import TXT_NIL
from const.lang import LANG, LANG_STYL


class Language(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.load()

    def default(self):
        DBG('LNG', f'{me_()}\n  File = {self.filename}\n')
        # sort on lng_nam
        for lst in sorted(LANG, key=lambda itm: itm[2]):
            lexer, lng_typ, lng_nam = lst[:3]
            sec = '|'.join((lng_nam, lng_typ, str(lexer)))
            if LANG_STYL[lexer]:
                DBG('LNG', ' ', sec)
                self[sec] = {}
                for lbl, tok, sty in LANG_STYL[lexer]:
                    key = '|'.join((lbl, str(tok)))
                    DBG('LNG', '    %-30s %s' % (key, sty))
                    self[sec][key] = sty

    def create(self):
        DBG('LNG', f'{me_()}\n  File = {self.filename}\n')

        # get default language configuration
        self.default()

        # add blank lines and header before all sections, except the first
        # first_sec = sorted(LANG, key=lambda itm: itm[2])[0][2]  # lng_nam
        first_sec = list(self)[0]  # lng_nam
        DBG('LNG', 'first lng_nam: [%s]' % first_sec)
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Styling for %s' % sec.split('|')[0])

        self.save()

#FIX, not used: obsolete?
    def load(self):
        DBG('LNG', f'{me_()}\n  File = {self.filename}\n')
        dbf.LANG(self)

#FIX, not used: obsolete?
    def save(self):
        DBG('LNG', f'{me_()}\n  File = {self.filename}\n')
        if DEBUG['LNG'] > 1: beeprint.pp(self, sort_keys=False)
        self.write()
