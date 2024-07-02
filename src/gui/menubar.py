#!/usr/bin/python

import collections
import re

import wx

from common.type import is_list, is_str
from common.util import (
    set_menu_item_icon, rs_, set_menu_item_label, swap_dict
)
from conf.debug import DBG, dbf, me_
from const.app import COMMON_KEYS, ACC_KEYS
from const.common import TXT_NIL
from const import glb
from const.menubar import SEP, MI
#FIX, filehistory performance with 'close many files' is 7 times slower...
# from extern.filehistory import FileHistory
import gui
import mix


class MenuBar(wx.MenuBar, mix.Help):

    __slots__ = ['CFG', 'prt', 'tlw', 'rfh_lst', 'rfh_cache', 'ico', 'icc',
                 'hlp', 'lng', 'mnu', 'ctx', 'ttd', 'acc_tbl']

    def __init__(self, prt):
        sec = glb.CFG['Layout']
        super().__init__()
        mix.Help.__init__(self)
        self.prt = prt

        self.rfh_lst = glb.CFG.rfh_lst
        self.rfh_cache = None

        # only for 1st instance (at startup)
        if not hasattr(self, 'ico'):
            self.ico = sec['MenuIcons']
            self.icc = sec['MenuIconsCustomCheckable']
            self.ics = sec['MenuIconSize']
            self.hlp = sec['MenuHelpText']

        # main menubar and context menu definitions
        # 'sub_lst' contains search, indentation, language submenus
        self.mnu, sub_lst = gui.menubar_defs(prt)
        self.ctx = gui.context_menu_defs(prt, sub_lst)

        # build menubar from main definitions
        self.build_menubar(prt, self.mnu)

        self.acc_tbl = self.build_accel_table() \
            if glb.CFG['General']['AcceleratorTable'] else wx.NullAcceleratorTable
        prt.SetAcceleratorTable(self.acc_tbl)

#INFO, D:\Dev\Python38\Lib\site-packages\wxPython-demo-4.0.1\demo\FileHistory.py
#DONE, reattach 'mni_rfh' here, see 'AppFrame.__init__'
    def attach_recent_files_history(self, tlw):
        sec = glb.RFH['RecentFileHistory']
        max_rfh = 0 if not sec['Enable'] else int(sec['MaxItems'])
        mni_rfh = self.FindItemById(MI['SUB_RFH']).SubMenu
        self.rfh_cache = wx.FileHistory(max_rfh)
        self.rfh_cache.UseMenu(mni_rfh)
        for fnm in reversed(self.rfh_lst):
            self.rfh_cache.AddFileToHistory(fnm)
        DBG('RFH', (dbf.FILE_HISTORY, self.rfh_cache))
        tlw.Bind(wx.EVT_MENU_RANGE, tlw.file_open_from_history, id=wx.ID_FILE1, id2=wx.ID_FILE1 + max_rfh - 1)

    def build_accel_table(self):
        def __set_accel_entry(lbl, id_):
            if '\t' in lbl:
                # strip ampersand, tab and font tags
                lbl, acc = lbl.replace('&', TXT_NIL).split('\t')
                acc = re.sub(r'\[\[.*\]\]', TXT_NIL, acc)

                # modifiers and keycode
                acc_lst = acc.split('+')
                mod, cod = acc_lst[0:-1], acc_lst[-1]

                # set modifier flags
                flg = wx.ACCEL_NORMAL
                for m in mod:
                    flg |= acc_keys[m]

                # lookup keycode
                if cod in keymap:
                    cod = keymap[cod]
                else:
                    if len(cod) == 1:  # avoid error for 1 item with >1 chars: 'Backspace'
                        cod = ord(cod)
                    else:
                        return

                acc_ent_lst.append(wx.AcceleratorEntry(flg, cod, id_))

                DBG('ACC', lbl, flg, cod, id_)

        # recursive menu walk
        def __walk_menu(mnu, lvl=1):
            for mni in mnu.MenuItems:
                if mni.IsSeparator():
                    continue
                if mni.Accel:
                    __set_accel_entry(mni.ItemLabel, mni.Id)
                if (sub := mni.SubMenu):
                    __walk_menu(sub, lvl=lvl + 1)

        # swap 'key:val' for easy common/accelerator key lookup
        keymap = swap_dict(COMMON_KEYS)
        acc_keys = swap_dict(ACC_KEYS)
        acc_ent_lst = []

        for mnu, __ in self.Menus:
            __walk_menu(mnu, lvl=1)

        return wx.AcceleratorTable(acc_ent_lst)

##############################################################################
##############################################################################

    def build_menubar(self, tlw, mnu):
        DBG('MNU==1', '%5s   %s\n%5s   %s' % ('id', 'Menu Item', rs_(), rs_(30)))
        for ttl, sub in mnu:
            DBG('MNU==1', '%-5s' % ttl.replace('&', TXT_NIL))
            self.Append(self.build_submenu(tlw, sub), ttl)
        # add recent file history menu
        self.attach_recent_files_history(self.prt)
        dbf.MENU(self)
        return self

    def build_submenu(self, tlw, sub):
        mnu = wx.Menu()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, 'Break' in field history menus
        # cnt, his = 0, False
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        for itm_lst in sub:
            # separator
            if not itm_lst:
                mnu.AppendSeparator()
                continue

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, 'Break' in field history menus
            # if 'History' in itm_lst[0]:
            #     his = True
            #     print(itm_lst)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # handle menu item attributes positionally
            # attr#: 1 = label        2 = shortcut   3 = action
            #        4 = help text    5 = icon       6 = kind
            #        7 = ui handler   8 = id         9 = style (not used)

            # append 'None' elements up to max_ list length
            len_, min_, max_ = len(itm_lst), 2, 9
            itm_lst = list(itm_lst) + [None] * (max_ - len_)

            if min_ <= len_ <= max_:
                ico = knd = uih = id_ = sty = None
                lbl, sct, act, hlp, ico, knd, uih, id_, sty = itm_lst
                # help text (statusbar)
                hlp = hlp if self.hlp and hlp else TXT_NIL
            else:
                err = f'{me_("F")}: menu item [{itm_lst[0]}] takes {min_} to {max_} arguments ({len_} given)'
                raise AssertionError(err)

            if sct:
                lbl = f'{lbl}\t{sct}'

            # menu item id
            if not id_:
                id_ = wx.NewIdRef()

            # check, radio or normal type
            typ = wx.ITEM_CHECK if knd == 'CHECK' else wx.ITEM_RADIO if knd == 'RADIO' else wx.ITEM_NORMAL

            # create menu item
            mni = wx.MenuItem(None, id_, lbl, hlp, kind=typ)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # print(f'{mni.GetItemLabelText()=}')

            # if '\tF' in mni.GetItemLabel():
            #     print(f'{mni.GetItemLabel()=}')
            #     print(mni.GetAccel().ToString())
            #     print(' ', mni.GetAccel().ToRawString())
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


            # label with optional font style
            set_menu_item_label(mni, lbl)
            # set_menu_item_label(mni, mni.GetLabelText(lbl))  # strip accel key

            # icon bitmap
            if self.ico and ico:
                set_menu_item_icon(mni, knd, ico, icc=self.icc, ics=self.ics)

            # menu item or submenu
            if is_list(act):
                # add submenu to menu item
                mni.SetSubMenu(self.build_submenu(tlw, act))
#INFO, see 'menuitemwithbmp' in "D:\Dev\Python38\Lib\site-packages\wxPython-demo-4.1.0\demo\Menu.py"
                # mni.SetBitmaps(PNG['copy'].Bitmap)
                # print('[%-20s] - [%s]' % (mni.ItemLabel, mni.Menu))
                if id_:
                    DBG('MNU', 'submenu/id:', lbl, id_)
            else:
                # add action to menu item
                if is_str(act):
                    act = eval(act)  # str -> function
                    # print('act: [%s]' % act)
                tlw.Bind(wx.EVT_MENU, act, id=id_)
                # if glb.CFG['General']['AcceleratorTable']:
                #     self._set_accel_entry(lbl, id_)

            # UI event handler
            if uih:
                if is_str(uih):
                    uih = eval(f'tlw.updateui_{uih.lower()}')  # str -> function
                tlw.Bind(wx.EVT_UPDATE_UI, uih, id=id_)

            mnu.Append(mni)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, 'Break' in field history menus
            # cnt += 1
            # if his and cnt % 20 == 0:
            #     mnu.Break()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # lbl = mnu.Append(mni)

            # if MNU_FNT_AUX:
            #     p, f, s, w, n = MNU_FNT_TYP
            #     lbl.SetFont(wx.Font(p, f, s, w, faceName=n))

            DBG('MNU==1', '%5d = %s' % (id_, mni.ItemLabel))
        return mnu

    def rebuild_menubar(self, tlw):
        # save menu item check state
        mni_dct = collections.OrderedDict(sorted(MI.items()))
        sav_dct = {}
        cnt = 0
        DBG('RBM', f'  BEFORE   (save state): {self.ico =!r:>6}, {self.icc =!r:>6}, {self.hlp =!r:>6}\n  {rs_(22)}')
        for i in mni_dct:
            if mni_dct[i] in [SEP, MI['CTX_TTL']]:
                continue
            if (mni := self.FindItemById(mni_dct[i])) and mni.IsCheckable():
                sav_dct[i] = mni.IsChecked()
                if sav_dct[i]:
                    DBG('RBM', f'  {i:15} = {sav_dct[i]}')
                    cnt += 1
        DBG('RBM', f'{rs_(17, " ")} [ {cnt} ]')

        # rebuild with empty menubar object
        self.__init__(tlw)
        tlw.SetMenuBar(self)
        glb.SMS('pub_kws', mnu_obj=self)

        # restore menu item check state
        rst_dct = collections.OrderedDict(sorted(sav_dct.items()))
        DBG('RBM', f'  AFTER (restore state): {self.ico =!r:>6}, {self.icc =!r:>6}, {self.hlp =!r:>6}\n  {rs_(22)}')
        cnt = 0
        for i in rst_dct:
            if rst_dct[i]:
                self.Check(MI[i], True)
                DBG('RBM', f'  {i:15} = {self.IsChecked(MI[i])}')
                cnt += 1
        DBG('RBM', f'{rs_(17, " ")} [ {cnt} ]')
