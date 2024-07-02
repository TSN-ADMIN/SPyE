#!/usr/bin/python

import os
from pprint import pprint

# from extern.configobj import ConfigObj, Section
# from extern.configobj.validate import Validator
import wx

from common.type import is_str, is_txc
from common.util import (
    get_keypress, make_modal, scale_bitmap,
    set_font, swap_dict, WindowIDRef_hack
)
from conf.debug import DBG, dbf, me_
from conf.menu import Menu
from const.app import APP
from const.common import TXT_NIL
from const.menubar import MI
# from const.statusbar import SBL
from data.images import catalog as PNG
import gui


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
CNT = 1
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# frame title
TTL_FRM = f'{APP["Base"]} - Menu Editor'

# frame: system menu item ids
ID_FRM = {
    'RESTORE' : -3808,
    'MOVE'    : -4080,
    'RESIZE'  : -4096,
    'ICONIZE' : -4064,
    'MAXIMIZE': -4048,
    'CLOSE'   : -4000,
}

# menu events
EVT_MNU = (wx.EVT_MENU, wx.EVT_MENU_OPEN, wx.EVT_MENU_CLOSE, wx.EVT_MENU_HIGHLIGHT)

# Menu/Tree item Id mapping
MAP_MTI = {}

# editable textctrl ids
__ID = wx.NewIdRef
ID_LBL = __ID()
ID_SCT = __ID()
ID_HLP = __ID()
ID_ICO = __ID()

# (non)editable/ALL textctrl field name suffixes
TXC_NON = set(('id_', 'key', 'act', 'knd', 'uih', 'sty'))
TXC_EDT = set(('lbl', 'sct', 'hlp', 'ico'))
TXC_ALL = TXC_EDT.union(TXC_NON)

# tabbable panel/textctrl/button widgets
WGT_TAB = set(('pnl_rit',
               'txc_lbl', 'txc_sct', 'txc_hlp', 'txc_ico',
               'btn_new', 'btn_edt', 'btn_del', 'btn_prv', 'btn_nxt'))

# staticbox label
LBL_SBX = 'Menu Item Properties'


WindowIDRef_hack()


class MenuEditor(wx.Frame):
    def __init__(self, prt):
        super().__init__(prt, size=wx.Size(800, 633), name='MenuEditor')
        self.prt = prt  # app frame (parent)

        # this editor (menubar)
        self.emb = emb = gui.MenuBar(self.prt)
        self.SetMenuBar(emb)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.CreateStatusBar()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        sty = wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE | wx.SP_3D
        spl_top = wx.SplitterWindow(self, wx.ID_ANY, style=sty)
        spl_bot = wx.SplitterWindow(spl_top, wx.ID_ANY, style=sty)

        sty, clr = wx.TAB_TRAVERSAL, '#E6F2FF'
        self.pnl_top = wx.Panel(spl_top, style=sty)
        self.pnl_top.SetBackgroundColour(clr)
        self.pnl_lft = wx.Panel(spl_bot, style=sty)
        self.pnl_lft.SetBackgroundColour(clr)
        self.pnl_rit = wx.Panel(spl_bot, style=sty)
        self.pnl_rit.SetBackgroundColour(clr)

        self.mtc = MenuTreeCtrl(self.pnl_lft, None, emb, icons=False)

        spl_top.SplitHorizontally(self.pnl_top, spl_bot, 60)
        spl_bot.SplitVertically(self.pnl_lft, self.pnl_rit, 300)

        spl_top.SetMinimumPaneSize(60)
        spl_bot.SetMinimumPaneSize(300)

        # prevent moving horizontal sash
        spl_top.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, lambda e: e.Veto())
        spl_bot.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, None)

        bxh = wx.BoxSizer(wx.HORIZONTAL)
        bxh.Add(self.pnl_top, 1, wx.EXPAND)
        self.pnl_top.SetSizer(bxh)

        bxv = wx.BoxSizer(wx.VERTICAL)
        bxv.Add(spl_bot, 1, wx.EXPAND)
        spl_bot.SetSizer(bxv)

        self.SetMinSize(self.Size)
        self.SetIcon(APP['Icon'])
        make_modal(self, True)

        self.create_widgets()
        self.Centre()
        self.binds()

    def binds(self):
        # self.mtc.Bind(wx.EVT_TREE_SEL_CHANGED if self.CFG['MenuEditor']['SingleClick'] else wx.EVT_TREE_ITEM_ACTIVATED, self.populate_panel)
        self.mtc.Bind(wx.EVT_TREE_SEL_CHANGED, self.populate_panel)

        # menu events
        for evt in EVT_MNU:
            self.Bind(evt, self.select_by_menu)

        # for evt in {'MENU', 'MENU_OPEN', 'MENU_HIGHLIGHT'}:
        #     self.Bind(getattr(wx, f'EVT_{evt}'), self.select_by_menu)


#INFO, URL=https://groups.google.com/g/wxpython-users/c/Ggq3Un1dSqY/m/kOeFJzDP2PsJ
        # tabbable fields
        for fld in WGT_TAB:
            getattr(self, fld).Bind(wx.EVT_NAVIGATION_KEY, self.tab_traversal)

        # editable textctrls (tabbable)
        for sfx in TXC_EDT:
            fld = getattr(self, f'txc_{sfx}')

            # fld.Bind(wx.EVT_TEXT_ENTER, lambda e: print('EVT_TEXT_ENTER'))

            fld.Bind(wx.EVT_SET_FOCUS, self.enter_textctrl)
            fld.Bind(wx.EVT_KILL_FOCUS, self.leave_textctrl, eval(f'ID_{sfx.upper()}'))

        self.btn_prv.Bind(wx.EVT_BUTTON, self.select_prev)
        self.btn_nxt.Bind(wx.EVT_BUTTON, self.select_next)

        self.txc_sct.Bind(wx.EVT_CHAR_HOOK, self.get_keypress)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def get_keypress(self, evt):
        obj = evt.EventObject
        # if obj is self.txc_lbl:
        #     self.txc_lbl.Value =
        #     print(get_keypress(evt))
        # evt.Skip()
        print(get_keypress(evt)[0])
        obj.Value = get_keypress(evt)[0]


    def create_widgets(self):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        sbx_lft = wx.StaticBox(self.pnl_lft, wx.ID_ANY, 'Menu Tree View')
        sbs_lft = wx.StaticBoxSizer(sbx_lft, wx.VERTICAL)
        set_font(sbx_lft, bold=True)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        sbx_top = wx.StaticBox(self.pnl_top, wx.ID_ANY, 'Visual Options')
        sbs_top = wx.StaticBoxSizer(sbx_top, wx.HORIZONTAL)
        set_font(sbx_top, bold=True)
        self.cbx_aut_exp = wx.CheckBox(self.pnl_top, wx.ID_ANY, 'Auto Expand/Collapse')
        self.cbx_ctr_itm = wx.CheckBox(self.pnl_top, wx.ID_ANY, 'Centre Selected Item')
        self.cbx_shw_box = wx.CheckBox(self.pnl_top, wx.ID_ANY, 'Show Unfocused Item Box')
        self.cbx_shw_ttp = wx.CheckBox(self.pnl_top, wx.ID_ANY, 'Show Tooltips')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.sbx_rit = wx.StaticBox(self.pnl_rit, wx.ID_ANY, LBL_SBX)
        sbs_rit = wx.StaticBoxSizer(self.sbx_rit, wx.VERTICAL)
        set_font(self.sbx_rit, bold=True)

        gbs = wx.GridBagSizer(vgap=0, hgap=0)
        gbs.SetFlexibleDirection(wx.BOTH)
        gbs.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_ALL)
        gbs.SetEmptyCellSize((10, 0))
        border = 5  # border space around widgets (pixels)

        self.stt_id_ = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Id (internal):')
        self.stt_key = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Key (application tag):')
        self.stt_lbl = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Label:')
        self.stt_sct = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Shortcut Key:')
        self.stt_act = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Action (event handler):')
        self.stt_hlp = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Help Text (statusbar):')
        self.stt_ico = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Icon:')
        self.stt_knd = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Type:')
        self.stt_uih = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'UI Handler (UI event):')
        self.stt_sty = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Style:')

        self.stt_sub = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Submenu:')
        self.stt_bmp = wx.StaticText(self.pnl_rit, wx.ID_ANY, 'Icon:')

        _txc_arg = (wx.DefaultPosition, (-1, -1), wx.TE_PROCESS_ENTER | wx.TE_READONLY)
        self.txc_id_ = wx.TextCtrl(self.pnl_rit, wx.ID_ANY, '', *_txc_arg)
        self.txc_key = wx.TextCtrl(self.pnl_rit, wx.ID_ANY, '', *_txc_arg)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.txc_lbl = wx.TextCtrl(self.pnl_rit, ID_LBL,    '', *_txc_arg, name='LBL')
        self.txc_sct = wx.TextCtrl(self.pnl_rit, ID_SCT,    '', *_txc_arg, name='SCT')
        self.txc_act = wx.TextCtrl(self.pnl_rit, wx.ID_ANY, '', *_txc_arg)
        self.txc_hlp = wx.TextCtrl(self.pnl_rit, ID_HLP,    '', *_txc_arg, name='HLP')
        self.txc_ico = wx.TextCtrl(self.pnl_rit, ID_ICO,    '', *_txc_arg, name='ICO')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.txc_knd = wx.TextCtrl(self.pnl_rit, wx.ID_ANY, '', *_txc_arg)
        self.txc_uih = wx.TextCtrl(self.pnl_rit, wx.ID_ANY, '', *_txc_arg)
        self.txc_sty = wx.TextCtrl(self.pnl_rit, wx.ID_ANY, '', *_txc_arg)

        self.cbx_sub = wx.CheckBox(self.pnl_rit, wx.ID_ANY, '')

#TODO, add icon bitmap sizes
        # for siz in (16, 24, 32):
        #     setattr(self, f'bmp_ico_{siz}', wx.StaticBitmap(self.pnl_rit, size=(siz, siz), style=wx.SUNKEN_BORDER))
        lrg, mdm, sml = (32, 32), (24, 24), (16, 16)
        self.bmp_ico = wx.StaticBitmap(self.pnl_rit, size=lrg, style=wx.SUNKEN_BORDER)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO: handle edit buttons
        self.btn_new = wx.Button(self.pnl_rit, wx.ID_ANY, '&New', size=(75, -1))
        self.btn_edt = wx.Button(self.pnl_rit, wx.ID_ANY, '&Edit', size=(75, -1))
        self.btn_del = wx.Button(self.pnl_rit, wx.ID_ANY, '&Delete', size=(75, -1))
        self.btn_new.Enable(False)
        self.btn_edt.Enable(False)
        self.btn_del.Enable(False)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.btn_prv = wx.Button(self.pnl_rit, wx.ID_ANY, 'P&revious', size=(75, -1))
        self.btn_nxt = wx.Button(self.pnl_rit, wx.ID_ANY, '&Next', size=(75, -1))

        _szr_arg1 = (wx.ALIGN_CENTRE_VERTICAL, border)
        # _szr_arg1 = (wx.EXPAND | wx.ALL | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        _szr_arg2 = (wx.EXPAND | wx.ALL, border)
        _szr_arg3 = (wx.ALIGN_RIGHT, border)

        row = 1
        for fld in {'id_', 'key', 'lbl', 'sct', 'act', 'hlp', 'ico', 'knd', 'uih', 'sty', 'sub'}:
            gbs.Add(getattr(self, f'stt_{fld}'), (row, 1), (1, 3), *_szr_arg1)
            pfx = 'cbx' if fld == 'sub' else 'txc'
            gbs.Add(getattr(self, f'{pfx}_{fld}'), (row, 4), (1, 2), *_szr_arg2)
            row += 1

        # bitmap icon field spans 1 column
        gbs.Add(self.stt_bmp, (row, 1), (1, 3), *_szr_arg1)
        gbs.Add(self.bmp_ico, (row, 4), (1, 1), *_szr_arg2)

#TODO, add icon bitmap sizes
        # gbs.Add(self.bmp_ico_16, (row, 4), (1, 1), *_szr_arg2)
        # gbs.Add(self.bmp_ico_24, (row+1, 4), (1, 1), *_szr_arg2)
        # gbs.Add(self.bmp_ico_32, (row+2, 4), (1, 1), *_szr_arg2)

        gbs.AddGrowableCol(5)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        bxh_opt = wx.BoxSizer(wx.HORIZONTAL)
        sbs_top.Add(self.cbx_aut_exp, 1, *_szr_arg2)
        # sbs_top.AddSpacer(5)
        sbs_top.Add(self.cbx_ctr_itm, 1, *_szr_arg2)
        # sbs_top.AddSpacer(175)
        sbs_top.Add(self.cbx_shw_box, 1, *_szr_arg2)
        # sbs_top.AddSpacer(5)
        sbs_top.Add(self.cbx_shw_ttp, 1, *_szr_arg2)
        sbs_top.AddStretchSpacer(9)
        bxh_opt.Add(sbs_top, 0, *_szr_arg2)
        self.pnl_top.SetSizer(bxh_opt)
        self.pnl_top.Fit()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        bxv = wx.BoxSizer(wx.VERTICAL)

        sbs_lft.Add(self.mtc, 1, *_szr_arg2)
        bxv.Add(sbs_lft, 1, *_szr_arg2)

        self.pnl_lft.SetSizer(bxv)
        self.pnl_lft.Fit()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        bxv = wx.BoxSizer(wx.VERTICAL)
        bxh = wx.BoxSizer(wx.HORIZONTAL)

        sbs_rit.Add(gbs, 0, *_szr_arg2)
        bxv.Add(sbs_rit, 0, *_szr_arg2)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        bxh.Add(self.btn_new, 0, *_szr_arg2)
        bxh.Add(self.btn_edt, 0, *_szr_arg2)
        bxh.Add(self.btn_del, 0, *_szr_arg2)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        bxh.Add(self.btn_prv, 0, *_szr_arg2)
        bxh.Add(self.btn_nxt, 0, *_szr_arg2)
        bxv.Add(bxh, 0, *_szr_arg3)

        self.populate_panel(None)

        self.pnl_rit.SetSizer(bxv)
        self.pnl_rit.Fit()

    def populate_panel(self, evt):
        # prevent error when closing frame
        if not self.mtc:
            return

        def __populate_field(obj, val, clr='#FFFFFF', ena=True):
            # textctrl field name suffix string or checkbox object
            fld = getattr(self, f'txc_{obj}') if is_str(obj) else obj
            fld.SetValue(val)
            fld.SetBackgroundColour(clr)
            fld.Enable(ena)
            if is_txc(fld):
                fld.SetEditable(ena)
                if obj in TXC_EDT:
                    stt = getattr(self, f'stt_{obj}')
                    fnt = stt.Font
                    fnt.SetWeight(wx.FONTWEIGHT_BOLD if ena else wx.FONTWEIGHT_NORMAL)
                    stt.SetFont(fnt)

        itm = self.mtc.Selection
        key = self.mtc.GetItemData(itm)
        if evt and key and evt.OldItem:
            prv_itm = evt.OldItem
            prv_key = self.mtc.GetItemData(prv_itm)
        # else:
        #     prv_key = None

        # get breadcrumb for tree item and its parent(s)
        bcb, prt = self.mtc.GetItemText(itm), itm
        while evt and (prt := self.mtc.GetItemParent(prt)):
            try:
                bcb = f'{self.mtc.GetItemText(prt)} -> {bcb}'
            except AssertionError as e:
                break

        # update frame title w/ breadcrumb
        self.SetTitle(f'{TTL_FRM} - [{bcb}]')

        # centre tree item
        mid = self.mtc.ClientRect[3] // 2
        __, y, __, h = self.mtc.GetBoundingRect(itm)
        self.mtc.ScrollLines((y - mid) // (h - 1) + 1)

        # toggle buttons
        self.btn_prv.Enable(False if itm == self.mtc.first else True)
        self.btn_nxt.Enable(False if itm == self.mtc.last else True)

        # item is not editable
        if key in {'MENU', 'NORMAL', 'SEPARATOR'}:
            # textctrls
            for fld in TXC_ALL:
                val = 'n/a'
                if fld == 'lbl':
                    val = self.mtc.GetItemText(itm)
                elif fld == 'knd':
                    val = val if key is None else key
                __populate_field(fld, val, '#FFFFFF', False)
            # checkbox
            __populate_field(self.cbx_sub, False, '#C0C0C0', False)
            # icon bitmap
            self.bmp_ico.SetBitmap(wx.NullBitmap)
            return

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # # process right panel changes for both tree and menu item
        # if evt:  # and (prv_itm) and (prv_key):
        # # if evt and (prv_itm = evt.OldItem) and (prv_key := self.mtc.GetItemData(prv_itm)):
        # # print(prv_key)
        #     mni = gui.MENU_ITEM[key]
        #     # print(mni)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # create local vars from menu item list
        itm_lst = gui.MENU_ITEM[key]
        len_, max_ = len(itm_lst), 7
        itm_lst = list(itm_lst) + [None] * (max_ - len_)

        id_ = MI[key]  # id_ (not used)
        __, sct, act, hlp, ico, knd, uih = [TXT_NIL if v is None else v for v in itm_lst]
        lbl = self.mtc.GetItemText(itm)
        knd = 'NORMAL' if knd == TXT_NIL else knd
        sty = TXT_NIL  # style (not used)

        # self.mtc.EnsureVisible(itm)

        # textctrls
        for fld in TXC_ALL:
            val = str(eval(fld))
            ena = True if fld in TXC_EDT else False
            __populate_field(fld, val, '#FFFFFF', ena)

        # checkbox
        val = self.MenuBar.FindItemById(MI[key]).IsSubMenu()
        __populate_field(self.cbx_sub, val, '#5CC95C' if val else '#C0C0C0', False)

        # prepare size
        if not any(s in ico for s in ('16', '24', '32') if ico.endswith(s)):
            ico = f'{ico}_32'

        # icon bitmap
        bmp = scale_bitmap(PNG[ico].Bitmap, 32, 32) if self.txc_ico.Value else wx.NullBitmap
        self.bmp_ico.SetBitmap(bmp)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def enter_textctrl(self, evt):
        evt.Skip()
        obj = evt.EventObject
        print(f'ENTER_window: [{obj.__class__.__name__:10}] ({evt.Id:6}) = [{obj.Value:25}] -> mod = {obj.IsModified()}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.sbx_rit.Label = f'{LBL_SBX} for [ {self.mtc.GetItemText(self.mtc.Selection)} ]'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def leave_textctrl(self, evt):
        evt.Skip()
        obj = evt.EventObject
        print(f'LEAVE_window: [{obj.__class__.__name__:10}] ({evt.Id:6}) = [{obj.Value:25}] -> mod = {obj.IsModified()}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.sbx_rit.Label = LBL_SBX
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if obj.IsModified():
            print('process change')
            itm = self.mtc.Selection
            key = self.mtc.GetItemData(itm)

            # find menu id
            id_ = swap_dict(MAP_MTI)[itm]
            mni = self.MenuBar.FindItemById(id_)

            lbl = self.txc_lbl.Value  # mni.ItemLabelText
            sct = self.txc_sct.Value  # mni.Accel.ToString()
            hlp = self.txc_hlp.Value
            ico = self.txc_ico.Value

            mnu = mni.Menu
            pos = mnu.FindChildItem(id_)[1]

            # label
            if obj is self.txc_lbl:
                print(f'lbl [{lbl:30}]-> update tree/menu')
                self.mtc.SetItemText(itm, lbl)
                mni.SetItemLabel(lbl)
            # shortcut
            elif obj is self.txc_sct:
                print(f'sct [{sct:30}]-> update menu ONLY')
#TODO, shortcut
            # help text
            elif obj is self.txc_hlp:
                print(f'hlp [{hlp:30}]-> update menu ONLY')
                mni.SetHelp(hlp)
            # icon
            elif obj is self.txc_ico:
                print(f'ico [{ico:30}]-> update tree/menu & bmp_ico')
                bmp = PNG[ico].Bitmap if ico.strip() else wx.NullBitmap
                self.mtc.img_lst.Replace(self.mtc.GetItemImage(itm), bmp)
                # force tree item update
                self.mtc.Refresh()
                mni.SetBitmap(bmp)

            # force menu item update
            mnu.Insert(pos, mnu.Remove(id_))

            print()

            obj.SetModified(False)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def tab_traversal(self, evt):
        # control allowed tab fields
#NOTE, weird behaviour: 'evt.Id = 0', so use focused object Id
        obj = self.FindFocus()
        id_ = obj.Id
        _fwd = evt.Direction  # backward/forward tab keypress (0/1)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        print(f'tab_traversal from -> [{obj.__class__.__name__}] [{obj.Name}]')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # allowed tab fields range
        first_fld, last_fld = self.txc_lbl, self.btn_nxt

        # focus last/first field with back/forward tab respectively
        if id_ == first_fld.Id and not _fwd:
            dbf.FOCUS(self.mtc)
            # dbf.FOCUS(last_fld)
        elif id_ == last_fld.Id and _fwd:
            dbf.FOCUS(self.mtc)
            # dbf.FOCUS(first_fld)
        else:
            evt.Skip()

    def select_by_menu(self, evt):
        def __walk_menu(mnu, lvl=1):
            res = None
            # if lvl == 1:
            #     print('='*55)
            #     print(mnu.Title)
            #     print('='*55)
            # else:
            #     print('-'*55)
            for mni in mnu.MenuItems:
                if (sub := mni.SubMenu):
                    # print(' '*4*(lvl-1), lvl, mni.ItemLabelText)
                    if evt.Menu is sub:
                        return (res := mni.Id)
                    if (res := __walk_menu(sub, lvl=lvl + 1)):
                        return res
            return res

        # assess menu event we're dealing with...
        id_, typ = evt.Id, evt.EventType

        evt_opn = (typ == wx.EVT_MENU_OPEN.typeId)
        evt_hlt = (typ == wx.EVT_MENU_HIGHLIGHT.typeId)

        # menubar menu opened/closed
        if hasattr(evt, 'Menu') and evt.Menu and (ttl := evt.Menu.Title):
            itm_typ = 'menubar menu'
            itm_act = 'opened' if evt_opn else 'closed'
            lbl = ttl.replace('&', TXT_NIL)  # strip ampersand
            itm_act = f'{itm_act:12}         [{lbl}]'
#HACK, prevent 'up/down' tree movement (when menubar menu just closed)
            if evt_opn:
                self.mtc.SelectItem(MAP_MTI[ttl])
        # submenu opened/closed (event Id = 0)
        elif id_ == 0:
            itm_typ = 'submenu'
            itm_act = 'opened' if evt_opn else 'closed'
            # lookup menu item id for submenu
            for mnu, __ in self.emb.Menus:
                if (id_sub := __walk_menu(mnu, lvl=1)):
                    lbl = self.MenuBar.FindItemById(id_sub).ItemLabelText
                    itm_act = f'{itm_act:12}[{id_sub:6}] [{lbl}]'
#HACK, prevent 'up/down' tree movement (when submenu just closed)
                    if evt_opn:
                        self.mtc.SelectItem(MAP_MTI[id_sub])
                    break
        # frame: system menu item
        elif id_ in (id_keys := swap_dict(ID_FRM)):
            itm_typ = 'sysmenu item'
            itm_act = 'highlighted' if evt_hlt else 'selected'
            itm_act = f'{itm_act:12}[{id_:6}] -> [{id_keys[id_]}]'
        # menu item highlighted/selected (include recent file history items)
        elif id_ < wx.ID_NONE or 0 <= id_ - wx.ID_FILE1 < 25:
            itm_typ = 'menu item'
            itm_act = 'highlighted' if evt_hlt else 'selected'
            lbl = self.MenuBar.FindItemById(id_).ItemLabelText
            itm_act = f'{itm_act:12}[{id_:6}] [{lbl}]'
            self.mtc.SelectItem(MAP_MTI[id_])
        else:
            itm_typ = f'{TXT_NIL:24} [{id_:6}]'
            itm_act = '* Unhandled ID *'


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL:
        fcs_evt = wx.PyCommandEvent(wx.EVT_SET_FOCUS.typeId, wx.NewIdRef())
        wx.PostEvent(self.mtc, fcs_evt)

        fcs_evt = wx.PyCommandEvent(wx.EVT_KILL_FOCUS.typeId, wx.NewIdRef())
        wx.PostEvent(self.mtc, fcs_evt)
        # self.mtc.Refresh()
        # self.mtc.Update()
        # self.mtc.kill_focus(None)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        global CNT
        print(f'{CNT:3}. {itm_typ:12} {itm_act}')
        CNT += 1
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def _do_select(self, itm):
        self.mtc.SelectItem(itm)
        self.mtc.SetFocusedItem(itm)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        dbf.FOCUS(self.mtc)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#INFO 'select_prev'/'select_next', copied from 'wx\lib\agw\customtreectrl.py'
    def select_prev(self, evt):
        itm = self.mtc.Selection
        if (prv := self.mtc.GetPrevSibling(itm)):
            # return item's last child or itself if it has no children
            while self.mtc.GetChildrenCount(prv):
                prv = self.mtc.GetLastChild(prv)
        else:
            # item has no previous sibling, return its parent
            prv = self.mtc.GetItemParent(itm)
        self._do_select(prv)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        dbf.FOCUS(self.btn_prv)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def select_next(self, evt):
        itm = self.mtc.Selection
        nxt = None
        # first see if there are any children.
        if self.mtc.GetChildrenCount(itm):
            nxt, __ = self.mtc.GetFirstChild(itm)
        else:
            # try a sibling of this or ancestor instead
            while itm and not nxt:
                nxt = self.mtc.GetNextSibling(itm)
                itm = self.mtc.GetItemParent(itm)
        self._do_select(nxt)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        dbf.FOCUS(self.btn_nxt)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def on_close(self, evt):
        make_modal(self, False)
        self.Destroy()


class MenuTreeCtrl(wx.TreeCtrl):
#FIX, parm 'icons' (not used)
    def __init__(self, prt, style, emb, icons=False):
        # | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_NO_LINES | wx.TR_TWIST_BUTTONS
        sty = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT
        super().__init__(prt, style=sty)
        self.prt = prt
        self.emb = emb

        self.SetBackgroundColour('#E6F2FF')
        self.root = self.AddRoot('Hidden root')
        self.sep = '-'*20

        lrg, mdm, sml = (32, 32), (24, 24), (16, 16)
        img_siz = sml
        self.img_lst = wx.ImageList(*img_siz)
        self.img_cnt = 0
        self.SetImageList(self.img_lst)

        self.create_tree()

        self.first = self.GetFirstChild(self.root)[0]
        self.last = self.GetLastChild(self.GetLastChild(self.root))

        self.binds()

    def binds(self):
        self.Bind(wx.EVT_CHAR_HOOK, self.get_keypress)
        self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.set_item_tooltip)

        self.Bind(wx.EVT_SET_FOCUS, self.set_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.kill_focus)

    def get_keypress(self, evt):
        # obj = evt.EventObject
        # if obj is self.txc_lbl:
        #     print(get_keypress(evt))
        # evt.Skip()
        print(get_keypress(evt))

    def set_focus(self, evt):
        evt.Skip()
        itm = self.Selection
        # remove item box leftover(s) when focus set
        self.Refresh()
        self.Update()

    def kill_focus(self, evt):
        evt.Skip()
        itm = self.Selection
        # create item box when focus lost
        x, y, w, h = self.GetBoundingRect(itm, textOnly=True)
        dc = wx.ClientDC(self)
        dc.SetPen(wx.Pen('RED', 2))
        dc.SetBrush(wx.Brush('RED', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle(x, y, w, h)
        del dc

    def create_tree(self):
        # recursive menu walk
        def __walk_menu(mnu, prt, lvl=1):
            for mni in mnu.MenuItems:
                if mni.IsSeparator():
                    itm = self.AppendItem(prt, self.sep)
                    self.SetItemData(itm, 'SEPARATOR')
                    continue

                itm = self.AppendItem(prt, mni.ItemLabelText)
                if (bmp := mni.Bitmap):
                    self.set_item_bitmap(itm, bmp)
                self.SetItemData(itm, id_keys[mni.Id] if mni.Id in id_keys else 'NORMAL')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # if mni.Accel:
                #     print(mni.Accel.ToString())
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                MAP_MTI[mni.Id] = itm
                if (sub := mni.SubMenu):
                    self.SetItemBold(itm)
                    self.SetItemBackgroundColour(itm, 'LIGHT BLUE')
                    __walk_menu(sub, itm, lvl=lvl + 1)

        id_keys = swap_dict(MI)

        # build tree and 'MAP_MTI' from menu items
        for mnu, lbl in self.emb.Menus:
            itm = self.AppendItem(self.root, lbl)
            self.SetItemData(itm, 'MENU')
            self.set_item_bitmap(itm, PNG['tree_member_16'].Bitmap)
            self.SetItemBold(itm)
            MAP_MTI[mnu.Title] = itm
            __walk_menu(mnu, itm)

        # pprint(MAP_MTI)

        if self.Count > 1:
            self.ExpandAll()
            child, __ = self.GetFirstChild(self.root)
            self.SelectItem(child)

    def set_item_bitmap(self, itm, bmp):
        self.img_lst.Add(bmp)
        self.SetItemImage(itm, self.img_cnt)
        self.img_cnt += 1

    def set_item_tooltip(self, evt):
        if (itm := evt.GetItem()):
            key, mni, itm_txt = self.GetItemData(itm), gui.MENU_ITEM, self.GetItemText(itm)
            if key in mni:
                evt.SetToolTip(mni[key][3])
            elif self.GetItemParent(itm) == self.root:
                evt.SetToolTip(f'Top menu: {itm_txt}')
            elif self.sep in itm_txt:
                evt.SetToolTip('Separator')
