#!/usr/bin/python

import wx

from ._load import _load
from common.doc import get_doc
from common.file import get_file_icon
from conf.debug import DEBUG
from const import glb
from const.lang import LANG, LANG_KWRD
from const.menu import ALL_KWS_ID, MI, NON_KWS_ID
from const.common import TXT_NIL


@_load
class Language:

    #DONE, build submenu of keyword sets per language
    def update_keyword_sets_menu(self, evt, mnu_obj):
        def __build_menu(mnu_kwd):
            glb.MB.Freeze()

            # delete menu items, if any
            for mni in mnu_kwd.MenuItems:
                mnu_kwd.Delete(mni)

            # build menu items per keyword set in active document's language
            for idx, kws in enumerate(doc.DescribeKeyWordSets().splitlines()):
                hlp = f'Select {doc.lng_nam} keywords: [{kws}]' if glb.MB.hlp else TXT_NIL
                mni_kwd = wx.MenuItem(None, idx, kws, hlp)
                mnu_kwd.Append(mni_kwd)
                self.Bind(wx.EVT_MENU, __menu_handler, id=mni_kwd.Id)

            # add menu items 'Select All' and 'Select None' when appropriate
            if mnu_kwd.MenuItemCount > 1:
                for hlp, lbl, id_ in (('all', 'All', ALL_KWS_ID), (('NO', 'None', NON_KWS_ID))):
                    hlp = f'Select {hlp} {doc.lng_nam} keyword sets' if glb.MB.hlp else TXT_NIL
                    mni_kwd = wx.MenuItem(None, id_, f'Select {lbl}', hlp)
                    self.Bind(wx.EVT_MENU, __menu_handler, id=mni_kwd.Id)
                    mnu_kwd.Insert(0, mni_kwd)

                mnu_kwd.InsertSeparator(2)

            glb.MB.Thaw()

        def __menu_handler(evt):
            obj = evt.EventObject
            itm = obj.FindItemById(evt.Id)

            for lbl, kws, lst in LANG_KWRD[doc.lexer]:
                if kws == itm.Id or itm.Id == ALL_KWS_ID:
                    if DEBUG['LNG']: print('All or 1 [add]:', lbl)
                    doc.SetKeyWords(kws, lst)
                else:
                    if DEBUG['LNG']: print('  1   [remove]:', lbl)
#NOTE, using empty string (TXT_NIL) still enables keyword styling for this set
#HACK: use underscore (_) as a non-existing keyword
                    doc.SetKeyWords(kws, '_')

        sec, pfx = glb.CFG['Language'], 'KeywordSets'

        # find keyword set menu item (should be present)
        mni_kwd_itm = mnu_obj.FindItemById(MI['SUB_KWS'])

        if not sec[f'{pfx}AsSubMenu']:
            mni_kwd_itm.Enable(False)
            if not sec[f'{pfx}InMenuBar']:
                return

#NOTE, avoid error 'wx._core.wxAssertionError: C++ assertion "IsAttached()" failed' on 'EnableTop'
#INFO, PREREQ: menubar attached,        'Language' has submenu      document exists
        if not (glb.MB.IsAttached() and mni_kwd_itm.IsSubMenu() and (doc := get_doc())):
            return

        if sec[f'{pfx}AsSubMenu']:
            # create menu from menu item's submenu (the one in 'Language')
            mnu_kwd = mni_kwd_itm.SubMenu
            __build_menu(mnu_kwd)
            mni_kwd_itm.Enable(bool(mnu_kwd.MenuItemCount))

        if sec[f'{pfx}InMenuBar']:
            # find keyword set menubar menu (might be present)
            mnu_kwd_pos = glb.MB.FindMenu('Language') + 1
            mnu_kwd = glb.MB.GetMenu(mnu_kwd_pos)
            __build_menu(mnu_kwd)
            glb.MB.EnableTop(mnu_kwd_pos, bool(mnu_kwd.MenuItemCount))

#FIX, consolidate language/styling process into 1 method/call:
#FIX, see 'update_language_styling', 'update_styling' and 'styling'
    def update_styling(self, evt):
        if not (doc := get_doc()): return
        # get language based on menu selection
        lng_lst = [m for m in LANG if evt.Id == m[4]]
        doc.update_language_styling(lng_lst)
        ico = get_file_icon(doc.lng_typ)
        glb.NBK.SetPageBitmap(glb.NBK.Selection, ico)
        self.update_keyword_sets_menu(None, glb.MB)
