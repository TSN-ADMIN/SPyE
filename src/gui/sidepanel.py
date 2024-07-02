#!/usr/bin/python

import locale
import os
from pathlib import Path
from pprint import pprint
import shlex
from shutil import which
import subprocess as SP
import markdown as md

import wx
import wx.html2 as wv
from wx.lib.buttons import GenBitmapButton
from wx.lib.mixins.listctrl import (
    ColumnSorterMixin as ColSorter,
    ListCtrlAutoWidthMixin as AutoWidth,
    ListRowHighlighter as Alternate
)
from wx import stc

from common.path import cwd
from common.type import is_int, is_lct
from common.util import (
    curdoc, curdoc_class, d_type, is_shown, msg_box, not_implemented,
    rs_, set_font, make_modal
)
from conf.debug import DBG, DEBUG, dbf, me_
from const.app import APP, EXE, OPT_CTAGS, OUT_CTAGS, LOC, CLR
from const.common import TXT_NIL, LOREM_IPSUM
from const.editor import MRK
from const import glb
from const.lang import LANG, LANG_WILDCARDS
from const.sidepanel import SPT_TMPFIL_NAME, SPT, SPT_NO_LCT, SPT_COL_HEADERS, TSK_TAGS, SPT_DUMMY
from const.symbol import SDF_TYPE, SDF_ICO_UNKNOWN, SDF_ICO_MEMBER, SDF_ICO_FUNCTION
import gui
from data.images import catalog as PNG
import mix
from tool.ctags import CtagsParser, ctags_version
from tool.docmap import DocMap

import extern.ExtendedChoice as XCHC


# @curdoc_class(curdoc)
class Hover:

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def _bind(obj, sec):
#INFO, 'ListCtrl' flag 'LIST_HITTEST_ONITEMLABEL' ALSO allows hovering empty space to right of item label
#INFO. a welcome bonus functionality ;-)
        flg  = wx.LIST_HITTEST_ONITEMLABEL
        flg += 0 if is_lct(obj) else wx.TREE_HITTEST_ONITEMINDENT | wx.TREE_HITTEST_ONITEMICON | wx.TREE_HITTEST_ONITEMLABEL
        val = glb.CFG[sec]['HoverSelect']
        return obj.Bind(wx.EVT_MOTION, lambda e: Hover._select_item(e, obj, sec, flg) if val else None)

#DONE, created generic function for wx.ListCtrl and wx.TreeCtrl
#DONE,     with signature: _select_item(evt, obj, cfg_sec, flg)
#DONE,               e.g.: _select_item(evt, self, 'Bookmark', wx.LIST_HITTEST_ONITEMLABEL)
#DONE, ==>> in case of function implementation: replace 'self' with 'obj'
#INFO, implemented for: 'Document', 'Bookmark',    'Language', 'Symbol',
#INFO,                  'Task',     'Breakpoint',  'Config',   'Pylint',
#INFO,                  'Pyflakes', 'Pycodestyle', 'Vulture'

    def _select_item(evt, obj, cfg_sec, flg):
        evt.Skip()

        ctrl, alt, shift = evt.controlDown, evt.altDown, evt.shiftDown

        # discard when 'Ctrl' key needed/not used
        if glb.CFG[cfg_sec]['NeedCtrlKey']:
            if not ctrl or (alt or shift):
                return

        itm, hit = obj.HitTest(evt.Position)

        if is_lct(obj) and itm <= -1:
            return

        if hit & flg:

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: avoid update when 'ListCrl item (wx.ListItem)' is already selected (e.g. 'wx.LIST_STATE_SELECTED')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            if DEBUG['GEN']:
                itm_sel, itm_pos, csr_pos, itm_rct = obj.GetFirstSelected(), obj.GetItemPosition(itm), evt.Position, obj.GetItemRect(itm)
                itm_hit = itm_rct.Contains(csr_pos)

                print(f'sel=[{itm_sel:2d}] || pos=[{itm_pos!r:16}] || csr=[{csr_pos!r:18}] || rct=[{itm_rct!r:24}] || hit=[{itm_hit!r:<5}]')
                print(f'    csy=[{csr_pos.y:3d}] || rcy=[{itm_rct.y:3d}] || rch=[{itm_rct.height:3d}]')

                dif_bot, dif_top = (itm_rct.y + itm_rct.height - csr_pos.y), (csr_pos.y - itm_rct.y)

                # if (2 < dif_bot < itm_rct.height - 2) or (2 < dif_top < itm_rct.height - 2):
                #     # print(' -> RTN 1')
                #     return

                print(f'    itm=[{itm:2d}] || BOT=[{dif_bot:3d}] || TOP=[{dif_top:3d}] -> UPDATE\n')

            # sta = obj.GetItem(itm).State
            # # print(f' -> SELECTED, FOCUSED : [{sta == wx.LIST_STATE_SELECTED!r:>5}], [{sta == wx.LIST_STATE_FOCUSED!r:>5}]')

            # if sta == wx.LIST_STATE_SELECTED:
            #     print(' >>>>> sta == wx.LIST_STATE_SELECTED')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            sel_fnc = obj.Select if is_lct(obj) else obj.SelectItem
            sel_fnc(itm)

            # speed up document and list/tree item update
            glb.DOC.Update()
            obj.Update()

            if DEBUG['GEN']:
                lbl = obj.GetItemText(itm)
                if (dta := obj.GetItemData(itm)) is None:
                    print(f'** Header: {lbl}')
                    return
                print(f'*   Label: {lbl}')


# @curdoc_class(curdoc)
class ListCtrlOverrides:
    # override ColumnSorterMixin
    def GetColumnSorter(self):
        """Returns a callable object to be used for comparing column values when sorting."""
        def __column_sorter(key1, key2):
            # python 3 lacks cmp:
            def __cmp(a, b):
                return (a > b) - (a < b)

            col = self._col
            ascending = self._colSortFlag[col]
            itm1 = self.itemDataMap[key1][col]
            itm2 = self.itemDataMap[key2][col]

            #--- Internationalization of string sorting with locale module
            if isinstance(itm1, str) and isinstance(itm2, str):
                # both are unicode (py2) or str (py3)
                cmp_val = locale.strcoll(itm1, itm2)
            elif isinstance(itm1, bytes) or isinstance(itm2, bytes):
                # at least one is a str (py2) or byte (py3)
                cmp_val = locale.strcoll(str(itm1), str(itm2))
            else:
                cmp_val = __cmp(itm1, itm2)
            #---

            # If the items are equal then pick something else to make the sort value unique
            if not cmp_val:
                cmp_val = __cmp(*self.GetSecondarySortValues(col, key1, key2))
#NOTE, added numeric (integer) sort
            else:
                try:
                    itm1, itm2 = int(itm1), int(itm2)
                except ValueError:
                    pass
                else:
                    cmp_val = __cmp(itm1, itm2)

            return cmp_val if ascending else -cmp_val

        return __column_sorter

    # override ColumnSorterMixin
    def GetListCtrl(self):
        return self

    # override ColumnSorterMixin
    def GetSortImages(self):
        return (self.img_arrow_dn, self.img_arrow_up)

    # override wx.ListCtrl
    def OnGetItemColumnImage(self, itm, col):
        return -1  # no image list

    # override wx.ListCtrl
    def OnGetItemImage(self, item):
        return -1  # no image list

    # override wx.ListCtrl
    def OnGetItemText(self, itm, col):
        if not col:
            col_txt = TXT_NIL
        else:
            col_txt = self.vrt_rows[itm][col]
        return col_txt

    # def _ColumnSorterMixin__updateImages(self, oldCol):
    #     sortImages = self.GetSortImages()
    #     if self._col != -1 and sortImages[0] != -1:
    #         img = sortImages[self._colSortFlag[self._col]]
    #         list = self.GetListCtrl()
    #         if oldCol != -1:
    #             list.SetColumnImage(oldCol, self.img_alpha_0_)
    #         list.SetColumnImage(self._col, img)


# base list control
# @dbf.method_calls()
# @curdoc_class(curdoc)
class ListCtrlTool(ListCtrlOverrides, wx.ListCtrl, ColSorter, AutoWidth, Alternate, mix.Help):

    __slots__ = ['_col',           'bxv',          'flg_vrt_srt', 'img_alpha_0_',
                 'img_arrow_dn',   'img_arrow_up', 'img_lst',     'itemDataMap',
                 'rows',           'mnf_flt',      'prt',         'prv_idx',
                 'tlw',            'vrt_rows']

    def __init__(self, prt, key, doc=None, srt_col=1):

#INFO, see 'wx.LC_VIRTUAL' example in 'D:\Dev\Python38\Lib\site-packages\wx\lib\agw\ultimatelistctrl.py'
#INFO, URL=https://wiki.wxpython.org/How%20to%20create%20a%20virtual%20list%20control%20%28Phoenix%29
#INFO, URL=https://discuss.wxpython.org/t/virtual-listctrl-an-example-with-a-question/27841

        sty = wx.BORDER_SUNKEN | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES
        if glb.CFG['SidePanel']['ListCtrlIsVirtual']:
            sty |= wx.LC_VIRTUAL

        super().__init__(prt, wx.ID_ANY, style=sty)
        mix.Help.__init__(self)
        self.prt = prt
        self.key = key
        # derive config section
        self.sec = sec = SPT[key].lbl
        self.rows = {}

        lbl = sec.lower()

        self.SetBackgroundColour(glb.CFG[sec]['ListRowColour'])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # # avoid flicker when resizing 'SidePanel' (otherwise, 'ChoiceCtrl' shines through)
        # self.SetBackgroundStyle(wx.WS_EX_BLOCK_EVENTS)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # avoid flicker when creating 'ListCtrl' (ctl), see 'SidePanel.page_changed'
        self.SetSize(glb.SPN.ClientSize)

        self.flg_vrt_srt = 'up'
        self.prv_idx = -1  # most recently selected list item
        self.mnf_flt = FilterBox(self, lbl, doc)

        self._create_columns(key)
        self._populate_list(key, lbl, doc)
        self.SortListItems(srt_col)  # sort by column#

        self.binds()

    def binds(self):
        Hover._bind(self, self.sec)
        if self.IsVirtual():
            self.Bind(wx.EVT_LIST_COL_CLICK, self._virtual_sort)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED if glb.CFG[self.sec]['SingleClick'] else wx.EVT_LIST_ITEM_ACTIVATED, self.activate_item)
        self.Bind(wx.EVT_COMMAND_LEFT_CLICK, lambda e: dbf.FOCUS(glb.DOC) if glb.CFG[self.sec]['SingleClick'] else None)
        self.Bind(wx.EVT_LIST_COL_DRAGGING, self._no_column_zero_drag)

    def _no_column_zero_drag(self, evt):
        if evt.Column == 0:
            evt.Veto()

    def _create_columns(self, key):
        hdr_lst = SPT_COL_HEADERS[key]
        col_cnt = len(hdr_lst)
        ColSorter.__init__(self, col_cnt)
        AutoWidth.__init__(self)
        # Alternate.__init__(self)

        lrg, mdm, sml = (32, 32), (24, 24), (16, 16)
        img_siz = sml
        self.img_lst = wx.ImageList(*img_siz)
        [self.img_lst.Add(PNG[f'ext_{ico[1]}_16'].Bitmap) for ico in LANG]
        self.img_arrow_up = self.img_lst.Add(PNG['SmallUpArrow'].Bitmap)
        self.img_arrow_dn = self.img_lst.Add(PNG['SmallDnArrow'].Bitmap)
#HACK, use transparent PNG (= #2) to prevent column label right aligning
        self.img_alpha_0_ = self.img_lst.Add(PNG['alpha_zero_16'].Bitmap)
        self.SetImageList(self.img_lst, wx.IMAGE_LIST_SMALL)

#NOTE, ListCtrl.SetHeaderAttr: new in version 4.1/wxWidgets-3.1.1
        # self.SetHeaderAttr(wx.ItemAttr('RED', 'GREEN', self.Font))

        for col in range(col_cnt):
            hdr, fmt = hdr_lst[col]
            if fmt == 'L':
                fmt = wx.LIST_FORMAT_LEFT
            elif fmt == 'R':
                fmt = wx.LIST_FORMAT_RIGHT
            elif fmt == 'C':
                fmt = wx.LIST_FORMAT_CENTRE
            self.InsertColumn(col, hdr, format=fmt)

#HACK, hide empty column 0
        self.SetColumnWidth(0, 0)

    def _populate_list(self, key, lbl, doc):
        # populate list AND setup 'itemDataMap' for mixin

        # 'Pylint'/'Pyflakes'/'Pycodestyle'/'Vulture': skip 1st update; click 'run_{siz}' icon to 'run'
        if not hasattr(self, 'run'):
        # if key not in {'PLT', 'PFL', 'PYS', 'VLT'}:
            self.update(doc, lbl)

        self.itemDataMap = self.rows  # ColumnSorterMixin

        cnt = len(self.rows)
#FIX, only show msg when any side panel tool visible
#NOTE, NOT working correctly
        if not any([is_shown(p) for p in SPT]):
            glb.SBR.set_text(f'Found {cnt} {lbl} occurrences')

    def _do_add_item(self, row, clr, extra=None):
        # discard when filter text not found
        val = self.mnf_flt.txc_flt.Value
        if self.mnf_flt.cbx_cas.Value:
            fnd = [itm for itm in row if val in itm]
        else:
            fnd = [itm for itm in row if val.lower() in itm.lower()]
        if not fnd:
            return

        key = self.ItemCount
        for col in range(self.ColumnCount):
            if not col:
#HACK, -1 hides 'mandatory item image' in empty column 0
                idx = self.InsertItem(key, row[col], -1)
            else:
                self.SetItem(idx, col, row[col])
                # icon at left side of language 'Name'
                if self.key in 'LNG' and col == 2:
                    self.SetItemColumnImage(idx, col, key)

        idx = self.ItemCount - 1
        self.SetItemData(key, idx)  # ColumnSorterMixin

        self.rows[key] = row

        # alternate row colour
        if key % 2:
            self.SetItemBackgroundColour(key, clr)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # fnt = self.GetItemFont(idx)
        # fnt.SetPointSize(8)
        # # fnt.SetPixelSize((4,10))
        # self.SetItemFont(idx, fnt)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # used in 'DebugList', extra formatting
        if extra:
            fnt = self.GetItemFont(idx)
            fnt.MakeBold()
            self.SetItemFont(idx, fnt)
            self.SetItemTextColour(idx, 'RED')

    def add_item(self, row, clr, extra=None):
        if self.IsVirtual():
            self.vrt_rows.append(row)
        else:
            self._do_add_item(row, clr, extra)

    def delete_all_items(self):
        if self.IsVirtual():
            self.vrt_rows = list()  # virtual rows container

        self.DeleteAllItems()

    def virtual_set_item_count(self):
        if self.IsVirtual():
            self.SetItemCount(len(self.vrt_rows))

    def _virtual_sort(self, evt):
        col = evt.Column
        self.vrt_rows.sort(key=lambda x: x[col])
        self.SetColumnImage(col, 0 if self.flg_vrt_srt == 'up' else 1)

#HACK, use transparent PNG (= #2) to prevent column label right aligning
        for c in range(self.ColumnCount):
            if c != col:
                self.ClearColumnImage(c)
                self.SetColumnImage(c, 2)

        if self.flg_vrt_srt == 'up':
            self.flg_vrt_srt = 'down'
        else:
            self.vrt_rows.reverse()
            self.flg_vrt_srt = 'up'

        self.DeleteAllItems()
        self.virtual_set_item_count()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, share pre/post functionality in 'update'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def update(self, doc=None, lbl=TXT_NIL):
        if self.__pre_update(lbl):
            self._update(doc)  # call subclass method
        self.__post_update(lbl)

    def __pre_update(self, lbl):
        # print(f'{me_("F"):23}  [{lbl.title()}]')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if hasattr(self, 'out') and not self.out:
            print(self.key, self.sec)
            return False
        if self.key not in {'BPT'}:
            dbf.call_stack(f'{me_("F")}')
            self.delete_all_items()
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        return True
        ...

    def __post_update(self, lbl):
        # print(f'{me_("F"):23}  [{lbl.title()}]')
        self.virtual_set_item_count()
        ...
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, share pre/post functionality in 'activate_item'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # def activate_item(self, lbl, doc=None):
    #     self.__pre_activate_item(lbl)
    #     self._activate_item(doc)  # call subclass method
    #     self.__post_activate_item(lbl)

    # def __pre_activate_item(self, lbl):
    #     print(f'{me_("F"):23}  [{lbl.title()}]')
    #     ...

    # def __post_activate_item(self, lbl):
    #     print(f'{me_("F"):23}  [{lbl.title()}]')
    #     ...
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    @curdoc
    def activate_item(self, evt):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#DONE, share 'discard' functionality in 'activate_item'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#DONE,   e.g. speed up list item selection:
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # discard when selected list item unchanged
        if (idx := evt.Index) == self.prv_idx:
            return

        self.prv_idx = idx

#INFO, 'Bind(...)' in subclass calls (superclass) 'activate_item'
#INFO, which then calls (subclass) '_activate_item' ('_' prefixed!)
        # self._activate_item(evt, idx)
        self._activate_item(evt, idx)  # call subclass method
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def show_list_filter_box(self):
        make_modal(self.mnf_flt)
        # place 'FilterBox' relative to 'Editor' window (top right)
        doc = glb.DOC
        doc_wid = doc.ClientSize.x
        flt_wid = self.mnf_flt.ClientSize.x
        self.mnf_flt.Move(doc.ClientToScreen(doc_wid - flt_wid - 25, 20))
        self.mnf_flt.Show()
        dbf.FOCUS(self.mnf_flt.txc_flt)
        self.prv_flt_val = self.mnf_flt.txc_flt.Value


# @dbf.method_calls()
# @curdoc_class(curdoc)
class FilterBox(wx.MiniFrame, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, lbl, doc):
        self.prt = prt
        self.lbl = lbl.title()
        self.ttl = f'{self.lbl} Filter'
        self.doc = doc
        self.flt_txt = TXT_NIL  # filter text

        sty = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER
        super().__init__(prt, wx.ID_ANY, lbl, size=(350, 95), style=sty, name=self.lbl)
        mix.Help.__init__(self)

#FIX, icon not shown
        self.SetIcon(APP['Icon'])

        pnl = wx.Panel(self, name='mnfFilterBoxPanel')
        pnl.SetToolTip('Filter Keys\n\nReturn   Set\nESC        Clear')

        # self.dft = 'Type Filter Text'
        self.dft = TXT_NIL
        self.txc_flt = wx.TextCtrl(pnl, wx.ID_ANY, self.dft, name='txcFilter')
        self.txc_flt.SetToolTip(LOREM_IPSUM)

        self.cbx_cas = wx.CheckBox(pnl, wx.ID_ANY, label='&Case sensitive', name='cbxCase')
        self.cbx_cas.SetToolTip('Toggle case sensitive filter search')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # self.btn_ok_ = wx.Button(pnl, wx.ID_ANY, label='OK', name='btnOK')
        # # self.cbx_cas.SetToolTip('Toggle case sensitive filter search')

        # self.btn_can = wx.Button(pnl, wx.ID_ANY, label='Cancel', name='btnCancel')
        # # self.cbx_cas.SetToolTip('Toggle case sensitive filter search')

        # bxv = wx.BoxSizer(wx.VERTICAL)
        # bxh = wx.BoxSizer(wx.HORIZONTAL)
        # _szr_arg = (1, wx.ALL | wx.EXPAND, 5)  # proportion, flags, border
        # bxv.Add(self.txc_flt, *_szr_arg)
        # bxh.Add(self.cbx_cas, *_szr_arg)
        # bxh.Add(self.btn_ok_, *_szr_arg)
        # bxh.Add(self.btn_can, *_szr_arg)
        # bxv.Add(bxh, *_szr_arg)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        bxv = wx.BoxSizer(wx.VERTICAL)
        _szr_arg = (1, wx.ALL | wx.EXPAND, 5)  # proportion, flags, border
        bxv.Add(self.txc_flt, *_szr_arg)
        bxv.Add(self.cbx_cas, *_szr_arg)
        pnl.SetSizer(bxv)
        # pnl.Refresh()
        # pnl.Update()
        # pnl.Layout()

        self.SetBackgroundColour(glb.CFG['SidePanel']['ListFilterBackColour'])

        self._rfr_fnc = lambda e: self._refresh_list(reset=False)

        self.binds()

    def binds(self):
        self.txc_flt.Bind(wx.EVT_TEXT, self._rfr_fnc)
        self.cbx_cas.Bind(wx.EVT_CHECKBOX, self._rfr_fnc)
        self.Bind(wx.EVT_CHAR_HOOK, self._keypress)
        self.Bind(wx.EVT_SHOW, lambda e: self._refresh_title())
        self.Bind(wx.EVT_CLOSE, self._close)

    def _keypress(self, evt):
        print(f'{me_("F")}')
        if evt.KeyCode not in (wx.WXK_ESCAPE, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            evt.Skip()
            return

        # on escape, restore value at time of box entry
        if evt.KeyCode == wx.WXK_ESCAPE:
            self.txc_flt.Value = self.prt.prv_flt_val

        make_modal(self, False)
        self.Hide()

        # set filter text
        if self.txc_flt.Value:
            self.flt_txt = self.txc_flt.Value
        else:
            self.flt_txt = TXT_NIL

        glb.SPN.flt_dct[self.lbl] = self.flt_txt

        glb.SMS('pub_spn')  # force '_update_tool_icons'
        dbf.FOCUS(self.doc)

    def _refresh_list(self, reset=True):
#FIX, 'reset' always 'False'
        # if reset:
        #     # prevent text event from firing
        #     self.txc_flt.Bind(wx.EVT_TEXT, None)
        #     self.txc_flt.Value = TXT_NIL
        #     self.txc_flt.Bind(wx.EVT_TEXT, self._rfr_fnc)

        self.prt.update(self.doc)
        self._refresh_title()

    def _refresh_title(self):
        if not self.IsShown():
            return

        cnt = self.prt.ItemCount
        txt = 'items' if cnt != 1 else 'item'
        doc = glb.DOC
        self.SetTitle(f'[{doc.fnm}] {self.ttl}: {cnt:3d} {txt}')
        DBG('LFL', f'[{doc.fnm}] {self.ttl} = [{self.txc_flt.Value}]: {cnt:3d} {txt}')

    def _close(self, evt):
        make_modal(self, False)
        self.Hide()
        # restore value at time of box entry
        self.txc_flt.Value = self.prt.prv_flt_val


# @dbf.method_calls()
# @curdoc_class(curdoc)
class SidePanel(wx.Choicebook, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]


#TODO, describe side panel's layered panel/ctl widget/object tree structure
#INFO, URL=D:\Dev\D\wx\TSN_SPyE\docs\diagram\SidePanel - SPyE - widget tree structure.JPG
#
#    SIDEPANEL (spn) perspective:
#    - 1 choice book w/ 16 pages (or panels) (cbp) w/ 1 ctl/page each
#    - 1 choice control (chc)
#    - chc selects cbp
#    - cbp contains functional control widget (ctl)
#    - ctl is deepest level and the ONLY visible object for chc
#    - ctl reference registration in spn occurs ONCE at 1st ctl creation
#    - MAX. 5 singleton ctl references are registered in: 'sgl_lst' in 'sidepanel.py'
#    - 8 singleton ctl references are UNUSED and always contain: 'None'
#    ...
#
#    DOCUMENT (doc) perspective:
#    - each doc can have 16 ctl references
#    - ctl reference registration in doc occurs ONCE at 1st ctl creation
#    - MAX. 16 ctl references for 1 doc are registered in: 'spt_lst' in 'editor.py'
#    ...
#
#    SINGLETON ctl (see definition in 'SPT'):
#    - 5 ctl are singleton, i.e. each is used for ALL docs:
#        - Document
#        - Macro
#        - Debug
#        - Config
#        - Help
#    ...
#
#    OTHER ctl (see definition in 'SPT'):
#    - 8 ctl are non-singleton, i.e. each is UNIQUELY used for 1 doc:
#        - Bookmark
#        - Explorer
#        - Symbol
#        - Task
#        - Breakpoint
#        - DocMap (see separate module 'docmap.py')
#        - Pylint
#        - Pyflakes
#        - Pycodestyle
#    ...
#

    def __init__(self, prt):
        sty = wx.BORDER_SUNKEN  # | wx.CHB_BOTTOM
        super().__init__(prt, wx.ID_ANY, size=(-1, -1), style=sty, name='SidePanel')
        mix.Help.__init__(self)
        DBG('SPN', f'{me_()}')

        self.chc = self.ChoiceCtrl  # choice book's (original) choice control
        self.chc.SetName('chcSidePanel')

        self.cbp_lst = list()  # choice book page panels
        # side panel tool pointers (single[ton] control), empty
        # -> each singleton side panel tool is shared by all open docs
        self.sgl_lst = [None] * len(SPT)
        # side panel tool filter definitions, empty
        self.flt_dct = {v.lbl: None for k, v in SPT.items()}


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # ArtIDs = [ 'wx.ART_ADD_BOOKMARK', 'wx.ART_DEL_BOOKMARK', 'wx.ART_HELP_SIDE_PANEL', 'wx.ART_HELP_SETTINGS', 'wx.ART_HELP_BOOK',
        #            'wx.ART_HELP_FOLDER', 'wx.ART_HELP_PAGE', 'wx.ART_GO_BACK', 'wx.ART_GO_FORWARD', 'wx.ART_GO_UP', 'wx.ART_GO_DOWN',
        #            'wx.ART_GO_TO_PARENT', 'wx.ART_GO_HOME', 'wx.ART_FILE_OPEN', 'wx.ART_PRINT', 'wx.ART_HELP', 'wx.ART_TIP',
        #            'wx.ART_REPORT_VIEW', 'wx.ART_LIST_VIEW', 'wx.ART_NEW_DIR', 'wx.ART_HARDDISK', 'wx.ART_FLOPPY', 'wx.ART_CDROM',
        #            'wx.ART_REMOVABLE', 'wx.ART_FOLDER', 'wx.ART_FOLDER_OPEN', 'wx.ART_GO_DIR_UP', 'wx.ART_EXECUTABLE_FILE',
        #            'wx.ART_NORMAL_FILE', 'wx.ART_TICK_MARK', 'wx.ART_CROSS_MARK', 'wx.ART_ERROR', 'wx.ART_QUESTION', 'wx.ART_WARNING',
        #            'wx.ART_INFORMATION', 'wx.ART_MISSING_IMAGE',
        # ]

        # img_siz = (16, 16)
        # ico_lst = wx.ImageList(*img_siz)
        # chc_lst = []

        # # build icon/choice lists
        # for itm in ArtIDs:
        #     bmp = wx.ArtProvider.GetBitmap(eval(itm), wx.ART_TOOLBAR, img_siz)
        #     ico_lst.Add(bmp)
        #     chc_lst.append(itm[7:])

        # #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # chc_lst = list(SPT.keys())
        # #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # import extern.ExtendedChoice as XCHC

        # self.chc = XCHC.ExtendedChoice(self, -1, choices=chc_lst, icons=ico_lst, extrastyle=XCHC.EC_CHOICE, name='ExtendedChoice')
        # self.chc.ecstyle.SetAllItemsFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'Consolas'))

        # def on_choice(event):
        #     ...

        # self.chc.Bind(XCHC.EVT_EXTENDEDCHOICE, on_choice)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        # choice font
        set_font(self.chc, face='Consolas', siz=11, bold=True)

        # get choice book's native nested (vertical/horizontal box) sizers
        self.bxv = self.Sizer
        self.bxh = self.bxv.Children[0].Sizer

        # 'replace' default w/ our extended choice control
        self.ChoiceCtrl.SetSize(1, 1)
        self.bxh.Detach(self.ChoiceCtrl)
        self.bxh.Add(self.chc, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, 2)
        self.SetSizer(self.bxv)

        self._page_panels()

        self.binds()

        self.subscriptions()

        DBG('SPN', f'\nwx.Choicebook native nested sizers'
                   f'\n  {self.bxv = }\n    children: {self.bxv.Children}'
                   f'\n  {self.bxh = }\n    children: {self.bxh.Children}\n')

    def binds(self):
        # self.Bind(wx.EVT_CHOICE, lambda e: print(e.Selection, e.String))
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.page_changed)
#HACK, hide (= empty) tooltip when click on choice control, restore when control selected/unfocused
        self.chc.Bind(wx.EVT_MOUSE_CAPTURE_CHANGED, lambda e: self._tooltip(e, show=False))
        self.chc.Bind(wx.EVT_KILL_FOCUS, lambda e: self._tooltip(e, show=True))
        self.chc.Bind(wx.EVT_CHOICE, lambda e: self._tooltip(e, show=True))


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.chc.Bind(wx.EVT_KEY_UP, self._on_key_up)

    def subscriptions(self):
        glb.SUB(self.page_changed, 'pub_spn')

    def _on_key_up(self, evt):
        # cod = chr(evt.KeyCode)
        cur = self.chc.CurrentSelection
        print('wx.Choice changing to', cur, self.chc.GetString(cur))
        # self.chc.SetSelection(self.chc.CurrentSelection)
        # self.page_changed(None)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def _page_panels(self):
        self.chc.ttp = 'Side Panel Shortcuts\n\n'  # tooltip

        # choice book page panels, filter defs and tooltip
        for spt in SPT.values():
            pnl = wx.Panel(self, name=spt.lbl)
            self.InsertPage(spt.idx, pnl, spt.lbl)
            self.cbp_lst.append(pnl)
            self.chc.ttp += f'{spt.acc}\t{spt.lbl}\n'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, needs better coding...
#INFO, see also 'update_choice_labels'
            if spt.lbl in glb.CFG['Filter'].keys():
                self.flt_dct[spt.lbl] = glb.CFG['Filter'][spt.lbl]
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            DBG('SPN', f'{spt.lbl:11} filter = [{self.flt_dct[spt.lbl]}]')

        self.chc.SetToolTip(self.chc.ttp)

    def _tooltip(self, evt, show=True):
        evt.Skip()
        self.chc.ttp = 'Side Panel Info\n\n'  # tooltip
        self.chc.ttp += 'Key\tTool         \tFilter\n'
        self.chc.ttp += '-----\t-------------\t-----------\n'
        # choice control tooltip
        for key, spt in SPT.items():
            if key in SPT_NO_LCT:
                dsc = ' '
            elif (dsc := self.flt_dct[spt.lbl]):
                pass
            else:
                dsc = '{None}'
            self.chc.ttp += f'{spt.acc}\t{spt.lbl}         \t{dsc}\n'
        self.chc.SetToolTip(self.chc.ttp if show else None)

    def _update_tool_icons(self, sel, key, ctl, cls, doc, siz=16):
        def _set_btn(flg, pfx, nam, ttp):
            __ = (self, wx.ID_ANY)  # convenient short naming (__)
            btn = wgt(*__, PNG[f'{pfx}_{siz}' if flg else _no].Bitmap, style=sty(flg), name=f'ico{nam}')
            btn.SetToolTip(ttp if flg else None)
            return btn

        # destroy bitmap buttons when present
        if hasattr(self, 'btn_hlp'):
            for obj in (getattr(self, f'btn_{a}') for a in {'run', 'lfe', 'lfc', 'rfr', 'srt', 'hlp'}):
                self.bxh.Detach(obj)
                obj.Destroy()

        # tool label/filter text
        lbl = get_lbl(sel)
        flt_txt = self.flt_dct[lbl]

        # selected tool's flags
        # command panels: 'Run'
        flg_run = hasattr(cls, 'run')
        # list panels: 'FilterEdit', 'FilterClear'
        flg_lfe = key not in SPT_NO_LCT
        flg_lfc = flg_lfe and flt_txt
        # list & 'Symbol' panels: 'Refresh', 'Sort'
        flg_rfr = flg_lfe or key in {'SDF'}
        flg_srt = flg_rfr and key not in {'MDN'}
        # all panels: 'Help'
        flg_hlp = True

        DBG('LFL', f'{lbl=:11}, {flg_lfe=!r:>5}, {flg_lfc=!r:>5}, {flt_txt=}\n')

        # filter text tooltip, help event, transparent button, widget, style
        flt_txt_ttp = f'\n\n  <<{flt_txt}>>\n ' if flt_txt else TXT_NIL
        hlp_evt = wx.PyCommandEvent(wx.EVT_HELP.typeId, wx.NewIdRef())
        _no = f'alpha_zero_{siz}'
        wgt = GenBitmapButton
        sty = lambda flg: wx.BORDER_RAISED if flg else wx.BORDER_NONE

        # bitmap buttons and tooltips
        _run = self.btn_run = _set_btn(flg_run,
            'run', 'Run', f'Run [{lbl}] command')
        _lfe = self.btn_lfe = _set_btn(flg_lfe,
            'filter_edit', 'FilterEdit', f'Edit [{lbl}] list filter{flt_txt_ttp}')
        _lfc = self.btn_lfc = _set_btn(flg_lfc,
            'filter_clear', 'FilterClear', f'Clear [{lbl}] list filter{flt_txt_ttp}')
        _rfr = self.btn_rfr = _set_btn(flg_rfr,
            'refresh', 'Refresh', f'Refresh [{lbl}] panel')
        _srt = self.btn_srt = _set_btn(flg_srt,
            'sort', 'Sort', f'Restore [{lbl}] sort state')
        _hlp = self.btn_hlp = _set_btn(flg_hlp,
            'help', 'Help', f'Side Panel Tool help [{lbl}]')

        # bind handlers
        __ = wx.EVT_BUTTON  # convenient short naming (__)
        _run.Bind(__, lambda e: cls.run(ctl, doc) if flg_run else None)
        _lfe.Bind(__, lambda e: ctl.show_list_filter_box() if flg_lfe else None)
        _lfc.Bind(__, lambda e: self.clear_filter() if flg_lfc else None)
        _rfr.Bind(__, lambda e: ctl.update(doc) if flg_rfr else None)
        _srt.Bind(__, lambda e: restore_sort_state(ctl) if flg_srt else None)
        _hlp.Bind(__, lambda e: wx.PostEvent(get_spt(), hlp_evt if flg_hlp else None))

        # repopulate/refresh buttons
        for idx, obj in enumerate((_run, _lfe, _lfc, _rfr, _srt, _hlp), start=1):
            self.bxh.Insert(idx, obj, 1, wx.LEFT | wx.EXPAND, 2)  # proportion, flags, border
            obj.SetBackgroundColour(CLR['BLUE'])
            obj.SetUseFocusIndicator(False)

#HACK, resize function for 'Side Panel Tool' controls
    def _resize(self, evt, ctl, cbp):
        DBG('GEN', f'{ctl}: _resize')
        ctl.SetSize(cbp.ClientSize)

    def clear_filter(self):
        ctl, lbl = get_spt(), get_lbl()
        ctl.mnf_flt.txc_flt.Value = self.flt_dct[lbl] = TXT_NIL
        glb.SMS('pub_spn')  # force '_update_tool_icons'

    @curdoc
    def page_changed(self, evt=None):
        DBG('SPN', f'{me_()}')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        DBG('GLB', f'  SPN: {id(doc) = } -> {doc.fnm = }')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # discard expected lengthy control creation when 'file_exit' in progress
        if glb.TLW.xit_active:
            return

        # access via choice id
        sel = self.GetSelection()
        for key, spt in SPT.items():
            if spt.idx == sel:
                break

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # # discard update when selected singleton control exists, prevents little flicker
        # __ = self.sgl_lst[sel]  # convenient short naming (selected singleton control)
        # if __ and (key != 'DOC' or __.ItemCount == glb.NBK.PageCount):
        #     return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.Freeze()

        # choice book page panel (parent), control, class, argument(s), singleton
        cbp, ctl, cls, arg, sgl = self.cbp_lst[sel], doc.spt_lst[sel], SPT[key].cls, SPT[key].arg, SPT[key].sgl
        cls = eval(cls)  # str -> class (instance)
        arg = (doc,) if arg else list()  # class: 'doc' argument or empty list

        # create control for current selection
        if not ctl:
            if sgl:
                if self.sgl_lst[sel] is None:
                    self.sgl_lst[sel] = cls(self.cbp_lst[sel], *arg)
                if hasattr((ctl := self.sgl_lst[sel]), 'update'):
                    ctl.update(doc)
            else:
                ctl = doc.spt_lst[sel] = cls(cbp, *arg)

            ctl.SetName(doc.fnm)

#HACK, each 'tool class' called its own '_resize', now consolidated here
#FIX, put choice book page panel in BoxSizer
        if cls in [DocMap]:
            self._resize(None, ctl, cbp)
        else:
            ctl.Bind(wx.EVT_PAINT, lambda e: self._resize(e, ctl, cbp))

        # cycle all documents and hide their existing controls
        [spt.Hide() for __, doc_spt in glb.NBK.open_docs() for spt in doc_spt.spt_lst if spt and spt.IsShown()]

        # show only current document's control
        ctl.Show()

        update_choice_labels()
        self._update_tool_icons(sel, key, ctl, cls, doc)

        # cbp.bxv = wx.BoxSizer(wx.VERTICAL)
        # cbp.bxv.Add(ctl, 1, wx.EXPAND)
        # cbp.SetSizer(cbp.bxv)

        self.Layout()

        self.Thaw()  # re-enable window updates

        # always force focus on main editor doc
        if self.chc.HasFocus():
            dbf.FOCUS(doc)

        dbf.SIDEPANEL(self, doc)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, force task control update from document task tags
        # if sel == SPT.TSK.idx:
        #     pnl.ctl.DeleteAllItems()
        #     pnl.ctl.update(doc)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
#         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         # handle key/selection while 'wx.Choice' (ChoiceCtrl) menu list is opened
#         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#     #     # self.chc.Bind(wx.EVT_CHAR, lambda e: print('***', e.EventObject.GetString(e.EventObject.CurrentSelection)))
#     #     self.chc.Bind(wx.EVT_CHAR, self.handle_key)
#     #     # self.chc.Bind(wx.EVT_CHAR, lambda e: print('***', dir(e.EventObject)))
#
#     # def handle_key(self, evt):
#     #     print('***', evt.EventObject.GetString(evt.EventObject.CurrentSelection))
#     #     evt.Skip()
#         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
#
#         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         # self.Size = (200, 90)
#
#         # siz = 24
#         # hlp = wx.StaticBitmap(self, wx.ID_ANY, PNG[f'help_{siz}'].Bitmap, name='icoHelp')
#
#         # bxh = wx.BoxSizer(wx.HORIZONTAL)
#         # bxh.Add(self.chc, 1, wx.ALL | wx.EXPAND)  # wx.EXPAND)
#         # bxh.Add(hlp, 0, wx.RIGHT, 5)
#
#         # self.SetSizer(bxh)
#         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
#         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         # icon (help)
#         # transform left click into help event; post it with our name as 'payload'
#         # hlp_evt = wx.PyCommandEvent(wx.EVT_HELP.typeId, wx.NewIdRef())
#         # hlp_evt.SetClientData(f'{self.__class__.__name__}-{hlp.Name}')
#         # hlp.Bind(wx.EVT_LEFT_DOWN, lambda e: wx.PostEvent(hlp, hlp_evt))
#         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# ########################################################################################
# ########################################################################################
# #FIX, FIND and DELETE list item (filename)
# #TODO, 2 functions: Ins/DelItem on open/close of file
# #         print(self.ctl.itemDataMap)
# #
# #         for idx in range(self.ctl.ItemCount):
# #             itm = self.ctl.GetItem(idx, 1)  # 2nd column
# #             if itm.Text == 'CALLS':
# #                 print('Found @%d' % idx, itm.Text)
# # #         for i in range(self.ctl.ItemCount):
# # #             self.ctl.DeleteItem(i)
# #
# #         print(self.ctl.itemDataMap)
# #         self.ctl.DeleteItem(11)
# #         print(self.ctl.ItemCount)
# ########################################################################################
# ########################################################################################


# @dbf.method_calls()
# @curdoc_class(curdoc)
class DocumentList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, doc):
        super().__init__(prt, 'DOC')
        DBG('DCL', f'{me_()}')

    def _update(self, doc=None):
        for idx, (pag, doc) in enumerate(glb.NBK.open_docs()):
            fnm, dnm, lng = doc.fnm, doc.dnm, doc.lng_nam
            DBG('DCL', '    doc[%d] = [%s] [%s] [%s] [%s]' % (pag, idx, fnm, dnm, lng))

            row = ('', str(idx + 1), fnm, dnm, lng)
            self.add_item(row, glb.CFG['Document']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
#FIX, share initial functionality with superclass implementation
        # super()._activate_item(evt)

        # idx = evt.Index

        # build pathname from item selection
        fnm = self.GetItemText(idx, 2)  # filename
        dnm = self.GetItemText(idx, 3)  # dirname
        pnm = f'{dnm}{os.sep}{fnm}' if dnm else f'{fnm}'  # new/unsaved file: no dirname

        # find pathname and set focus on selected file
        for __, doc in glb.NBK.open_docs():
            if pnm == doc.pnm:
                dbf.FOCUS(doc)
                break


# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #INFO, Highlight a ListItem in a wx.ListCtrl on MouseOver
# #INFO, URL=https://stackoverflow.com/questions/8512434/highlight-a-listitem-in-a-wx-listctrl-on-mouseover
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#     #     self.ctl.Bind(wx.EVT_MOTION, self.on_mouseover)
#     #     self.prv_itm = -1

#     # def on_mouseover(self, evt):
#     #     x = evt.GetX()
#     #     y = evt.GetY()
#     #     self.itm, flags = self.ctl.HitTest((x, y))
#     #     if self.itm < 0:
#     #         self.ctl.SetToolTipString("Colour codes Red - Loaded, Yellow - In Progress, Green - Finished, Blue - Invoiced, White - User defined")
#     #         return
#     #     if self.itm != self.prv_itm:
#     #         self.old_itm = self.prv_itm
#     #         self.prv_itm = self.itm
#     #     else:
#     #         return
#     #     bg_colour = self.ctl.GetItemBackgroundColour(self.itm)
#     #     if bg_colour == wx.BLACK or bg_colour == wx.NullColour:
#     #         self.ctl.SetItemBackgroundColour(self.itm,"#3246A8")
#     #         self.ctl.SetItemBackgroundColour(self.old_itm,wx.BLACK)
#     #     elif bg_colour == "#3246A8":
#     #         self.ctl.SetItemBackgroundColour(self.itm,wx.BLACK)
#     #     self.currentItem = self.itm
#     #     rowid = self.ctl.GetItem(self.currentItem,13)
#     #     stat_test = rowid.GetText()
#     #     rowid = self.ctl.GetItem(self.currentItem,1)
#     #     file_test = rowid.GetText()
#     #     rowid = self.ctl.GetItem(self.currentItem,4)
#     #     running_test = rowid.GetText()

#     #     if stat_test == "0":
#     #         self.ctl.SetToolTipString("File currently playing\nRunning time "+running_test)
#     #     elif stat_test == "1":
#     #         self.ctl.SetToolTipString("In Progress\nRunning time "+running_test)
#     #     elif stat_test == "2":
#     #         self.ctl.SetToolTipString("Finished\nRunning time "+running_test)
#     #     elif stat_test == "3":
#     #         self.ctl.SetToolTipString("Invoiced\nRunning time "+running_test)
#     #     if file_test == self.file_playing and stat_test == "1":
#     #         self.ctl.SetToolTipString("File currently playing & In Progress\nRunning time "+running_test)
#     #     if file_test == self.file_playing and stat_test == "2":
#     #         self.ctl.SetToolTipString("File currently playing but Finished\nRunning time "+running_test)
#     #     if file_test == self.file_playing and stat_test == "3":
#     #         self.ctl.SetToolTipString("File currently playing but Invoiced\nRunning time "+running_test)
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# @curdoc_class(curdoc)
class ProjectTree(wx.TreeCtrl, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, doc):
        sty = wx.TR_DEFAULT_STYLE  # | wx.TR_HIDE_ROOT
        # | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_NO_LINES | wx.TR_TWIST_BUTTONS
        super().__init__(prt, style=sty)
        mix.Help.__init__(self)
        self.SetBackgroundColour('#FFDDDD')  # CLR['RED']
        self.prt = prt

#NOTE, workaround: no further processing, now only handles Python source code
        if not is_lang(self, doc, 'python'):
            return

        self.root = self.AddRoot('Hidden root')

        for __, doc in glb.NBK.open_docs():
            # print(doc.fnm)
            self.AppendItem(self.root, doc.fnm)

        if self.Count > 1:
            self.ExpandAll()

#HACK, though 'ProjectTree' is no list, use 'update' as core method here
#FIX, when 'Refresh' called ('ico_rfr'), DESTROY CURRENT 'ProjectTree' instance
    def _update(self, doc=None):
        self.__init__(self.prt, doc)

    def run(self, doc):
        ...


# @curdoc_class(curdoc)
class BookmarkList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, doc):
        super().__init__(prt, 'BMK', doc)
        DBG('BMK', f'{me_()}')

        # self.prt = prt

        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'BMK'))
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.delete_item)

    def _update(self, doc):
        for bmk in doc.get_bookmarks():
            DBG('BMK', '    bmk = [%s]' % str(bmk))

            row = ('', str(bmk[0]), str(bmk[1]), doc.GetLine(bmk[1] - 1).strip())
            self.add_item(row, glb.CFG['Bookmark']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
        DBG('BMK', f'{me_()}')
        # idx = evt.Index
        lin = int(self.GetItemText(idx, 2))  # lineno
        DBG('BMK', f'  [{self.GetItemText(idx, 1).rstrip()}] on line: {lin}')

        self.goto_bookmark(doc, lin)
        evt.Skip()

    # @curdoc
    def delete_item(self, evt):
        if evt.KeyCode != wx.WXK_DELETE or evt.Index < 0:
            return
        DBG('BMK', f'{me_()}')
        idx = evt.Index
        DBG('BMK', f'  delete #{idx + 1}: [{self.GetItemText(idx, 3).rstrip()}]')
        lin = int(self.GetItemText(idx, 2))  # lineno
        glb.SBR.set_text('Bookmark deleted from line %d' % (lin))

        self.goto_bookmark(doc, lin)
        glb.TLW.toggle_bookmark(evt, lin - 1)
        restore_sort_state(self)

        # select next bookmark (if any) after delete
        if self.ItemCount:
            idx = idx - 1 if idx >= self.ItemCount else idx
            self.Select(idx)

    def goto_bookmark(self, doc, lin):
        doc.GotoLine(lin - 1)
        doc.LineEndExtend()
        if glb.CFG['Bookmark']['CentreCaret']:
            doc.VerticalCentreCaret()
        dbf.FOCUS(doc)


# @curdoc_class(curdoc)
class LanguageList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):
        super().__init__(prt, 'LNG')
        DBG('SPN', f'{me_()}')

#TODO, add 'enable selected lexer' for cur doc to '_activate_item'

    def _update(self, doc=None):
        for idx, (__, typ, nam, ext, __) in enumerate(LANG):
            DBG('GEN', '    lng = [%s] [%s] [%s] [%s]' % (idx, nam, typ, ext))
            row = ('', str(idx + 1), nam, typ, ext)
            self.add_item(row, glb.CFG['Language']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
    # def post_activate_item(self, evt, idx):
        DBG('GEN', f'{me_()}')

#FIX, selecting/hovering 'Perl' takes more time to execute...
        # dbf.TIMER('__test__')

        # number (order), name, type, extension(s)
        num, nam, typ, ext = [self.GetItemText(idx, i) for i in range(1, 5)]

        DBG('GEN', f'  [{num:2}]: [{nam:12}]  [{typ:10}]  [{ext:20}]')

#NOTE, prevent circular dependency
        from common.file import get_file_icon

#FIX, consolidate language/styling process into 1 method/call:
#FIX, see 'update_language_styling', 'update_styling' and 'styling'
        # selected language
        doc.update_language_styling([[lng for lng in LANG][int(num) - 1]])
        ico = get_file_icon(doc.lng_typ)
        glb.NBK.SetPageBitmap(glb.NBK.Selection, ico)
        glb.SMS('pub_kws', mnu_obj=glb.MBR)

        dbf.FOCUS(doc)
        evt.Skip()

#FIX, selecting/hovering 'Perl' takes more time to execute...
        # dbf.TIMER('__test__', 'STOP')


# @curdoc_class(curdoc)
class ExplorerTree(wx.GenericDirCtrl, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, doc):
        sty = wx.DIRCTRL_SHOW_FILTERS  # | wx.DIRCTRL_DIR_ONLY | wx.DIRCTRL_EDIT_LABELS
        super().__init__(prt, wx.ID_ANY, style=sty, filter=LANG_WILDCARDS)
        mix.Help.__init__(self)

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # for d in ('_SRCREF-TSN-Python-Editor', '_TODO', 'archive',
        #             'build', 'contrib', 'docs', 'src'):
        #     self.ExpandPath(f'D:/Dev/D/wx/TSN_SPyE/{d}')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.ExpandPath(doc.pnm)

#FIX, set scrollbar thumb to leftmost pos
        # self.SetScrollPos(wx.HORIZONTAL, self.GetScrollRange(wx.HORIZONTAL), refresh=True)

        self.TreeCtrl.SetBackgroundColour(CLR['ORANGE'])
        self.Bind(wx.EVT_DIRCTRL_FILEACTIVATED, self._select_file)

    def _select_file(self, evt):
#NOTE, prevent circular dependency
        from common.file import open_files

        DBG('GEN', f'{me_()}\n  [{self.Path}]')

        fil_lst = [[fnm] for fnm in self.Path.splitlines()]
        open_files(fil_lst)


# @curdoc_class(curdoc)
class SymbolTree(wx.TreeCtrl, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, doc):
        sty = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT
        # | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_NO_LINES | wx.TR_TWIST_BUTTONS
        super().__init__(prt, style=sty)
        mix.Help.__init__(self)

        self.SetBackgroundColour('#FFDDDD')  # CLR['RED']
        self.prt = prt

#NOTE, workaround: no further processing, now only handles Python source code
        if not is_lang(self, doc, 'python'):
            return

        self.root = self.AddRoot('Hidden root')

        if glb.CFG['SymbolDef']['ShowIcons']:
            lrg, mdm, sml = (32, 32), (24, 24), (16, 16)
            img_siz = sml
            bmp_lst = [PNG[f'tree_{nam}_16'].Bitmap \
                for nam in ('variable', 'unknown', 'namespace', 'class', 'member', 'function')]

            self.img_lst = wx.ImageList(*img_siz)
            for bmp in bmp_lst:
                self.img_lst.Add(bmp)
            self.SetImageList(self.img_lst)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # set_font(self, face='Consolas', siz=8, bold=True, italic=True)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # validate ctags executable/version
        pnm = which(EXE['CTAGS'])
        if not pnm:
            print(f'[{EXE["CTAGS"]}] executable not found')
            stt = wx.StaticText(self, label='\n Ctags: executable not found \n')
            stt.SetBackgroundColour('RED')
            return
        dsc = 'Universal Ctags'
        if dsc not in ctags_version():
            print(f'[{dsc}] not found in version string of [{pnm}]')
            stt = wx.StaticText(self, label='\n Ctags: wrong version \n')
            stt.SetBackgroundColour(CLR['PURPLE'])
            return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # create/read tags file
        parser = CtagsParser()
        # prevent 'file open error'
        pnm = doc.pnm.replace(os.sep, '/')
        # auxiliary option: including regex search pattern '--excmd=pattern'
        # res = parser.parse(f'{EXE["CTAGS"]} -f "{OUT_CTAGS}" -nu --excmd=pattern --extras=-p --fields=fiKlmnsStz -R {pnm}')
        res = parser.parse(f'{EXE["CTAGS"]} -f "{OUT_CTAGS}" {OPT_CTAGS} "{pnm}"')

        if not res:
            return

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # D:\Dev\D\wx\TSN_SPyE\src>ctags -nu --kinds-python=+l --fields=fiKlmnsStz -R SPyE.py
    #NOTE, '--kinds-python=+l' adds 'local variables', example tag:
    #     ...
    #     max_pos SPyE.py 2265;"  kind:local  line:2265   language:Python member:AppFrame.GotoTask    file:
    #     ...
    #################################################################################################
    # D:\Dev\D\wx\TSN_SPyE\src>ctags --fields-python= --list-fields=python
    # #LETTER NAME       ENABLED LANGUAGE JSTYPE FIXED OP DESCRIPTION
    # -       decorators no      Python   s--    no    -- decorators on functions and classes
    # -       nameref    no      Python   s--    no    -- the original name for the tag
    #
    # D:\Dev\D\wx\TSN_SPyE\src>ctags --fields-python=nameref --list-fields=python
    # ctags: Warning: Wrong per language field specification: nameref
    # ctags: only long name can be used in per language field spec: 'n'
    #
    # D:\Dev\D\wx\TSN_SPyE\src>ctags --fields-python={nameref} --list-fields=python
    # #LETTER NAME       ENABLED LANGUAGE JSTYPE FIXED OP DESCRIPTION
    # -       decorators no      Python   s--    no    -- decorators on functions and classes
    # -       nameref    yes     Python   s--    no    -- the original name for the tag
    #
    # D:\Dev\D\wx\TSN_SPyE\src>ctags --fields-python={decorators} --list-fields=python
    # #LETTER NAME       ENABLED LANGUAGE JSTYPE FIXED OP DESCRIPTION
    # -       decorators yes     Python   s--    no    -- decorators on functions and classes
    # -       nameref    no      Python   s--    no    -- the original name for the tag
    #
    # D:\Dev\D\wx\TSN_SPyE\src>ctags --fields-python=* --list-fields=python
    # #LETTER NAME       ENABLED LANGUAGE JSTYPE FIXED OP DESCRIPTION
    # -       decorators yes     Python   s--    no    -- decorators on functions and classes
    # -       nameref    yes     Python   s--    no    -- the original name for the tag
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # build nodes and children per symbol type
        for idx, sym_lst in enumerate(self.populate_symbol_lists(parser.tags)):
            self.add_top_node(*SDF_TYPE[idx], sym_lst)

#TODO, config option: 'Expand/Collapse/Level_1/All'
        if self.Count > 1:
            self.ExpandAll()
            child, __ = self.GetFirstChild(self.root)
            self.SelectItem(child)

#NOTE, 'EVT_TREE_SEL_CHANGED' needs single click, EVT_TREE_ITEM_ACTIVATED needs double click
        Hover._bind(self, 'SymbolDef')
        self.Bind(wx.EVT_TREE_SEL_CHANGED if glb.CFG['SymbolDef']['SingleClick'] else wx.EVT_TREE_ITEM_ACTIVATED, self._activate_item)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'SDF'))

    def populate_symbol_lists(self, parsed_tags):
        def __get_level(fnc):
            # derive level from function list item
            lvl = 1
            if len(fnc) > 2:
                lvl = fnc[2].count('.') + 2
            return lvl

        # build tree list per symbol type
        var_lst = []
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        lcl_lst = []
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        unk_lst = []
        nsp_lst = []
        cls_lst = list()  # temp
        mbr_lst = list()  # temp
        fnc_lst = []
        cmf_lst = []
        fn2_lst = list()  # temp

        # process tags
        for tag in parsed_tags:
            kind = tag.fields['kind']
            fld_lst = [tag.name, int(tag.fields['line'])]

            # store tag item info per symbol type
            if  kind == 'variable':
                var_lst.append(['V', *fld_lst, 1])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            elif  kind == 'local':
                lcl_lst.append(['L', *fld_lst, 1])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            elif  kind == 'unknown':
                unk_lst.append(['U', *fld_lst, 1])
            elif  kind == 'namespace':
                nsp_lst.append(['N', *fld_lst, 1])
            elif  kind == 'class':
#FIX, add CLASS to cmf_lst
                # cmf_lst.append(['C', *fld_lst, 1])
                cls_lst.append(fld_lst)
            elif  kind == 'member':
#FIX, add MEMBER to cmf_lst
                # cmf_lst.append(['M', *fld_lst, 2])
                fld_lst.append(tag.fields['class'])
                mbr_lst.append(fld_lst)
            elif  kind == 'function':
#FIX, add (member) FUNCTION to cmf_lst
                # cmf_lst.append(['F', *fld_lst[:2], __get_level(fnc)])
                if 'member' in tag.fields:
                    fld_lst.append(tag.fields['member'])
                    # print(f'F  {__get_level(fld_lst):2d}  {fld_lst[0]:25}  {fld_lst[1]:4}  {fld_lst[2]}')
                elif 'function' in tag.fields:
                    fld_lst.append(tag.fields['function'])
                    # print(f'F  {__get_level(fld_lst):2d}  {fld_lst[0]:25}  {fld_lst[1]:4}  {fld_lst[2]}')
                fnc_lst.append(fld_lst)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        #     print(kind, 'class' in tag.fields, 'member' in tag.fields, 'function' in tag.fields, tag.name, tag.fields)
        # print('-'*20)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # consolidate classes/members/member functions into 'cmf' list
        # pass 1: add classes/members
        for cls in cls_lst:
            cmf_lst.append(['C', *cls[:2], 1])
            for mbr in mbr_lst:
                if cls[0] in mbr[2]:
                    cmf_lst.append(['M', *mbr[:2], 2])

        # pass 2: add member functions
        for fnc in fnc_lst:
            lin = fnc[1]
            for idx, __ in enumerate(cmf_lst):
#HACK, avoid insert of regular function (level 1) as a class
                if __get_level(fnc) == 1:
                    continue
                if cmf_lst[idx][2] > lin:
                    cmf_lst.insert(idx, ['F', *fnc[:2], __get_level(fnc)])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                    # print(__get_level(fnc))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                    break

        # pass 3: add regular functions
        for idx, fnc in enumerate(fnc_lst):
#@@@@@@@@@@@@@@@@@@@@@
            # print(fnc)
#@@@@@@@@@@@@@@@@@@@@@
            fn2_lst.insert(idx, ['F', *fnc[:2], __get_level(fnc)])

        fnc_lst = fn2_lst.copy()

        # clear temp lists
        del cls_lst
        del mbr_lst
        del fn2_lst

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        pprint(lcl_lst)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        return var_lst, unk_lst, nsp_lst, cmf_lst, fnc_lst

    def add_top_node(self, typ='V', top_lbl='Unknowns', ico=SDF_ICO_UNKNOWN, itm_lst=[], sort=False):
        # discard empty symbol list
        if not itm_lst:
            return

        # add top-level (root) node
        top_node = self.AppendItem(self.root, top_lbl)
        self.SetItemImage(top_node, ico)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # self.SetItemBold(top_node)
        # self.SetItemBackgroundColour(top_node, 'YELLOW')
        # self.SetQuickBestSize(True)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # list of level parent pointers (max 10); root node = level 0 parent
        lpp_lst = [top_node, *[None]*10]

        # add tree items (label, line, icon)
        for itm in itm_lst:
            cat, lbl, lin, lvl = itm

#FIX, not used: obsolete?
            # if typ == 'C' and cat == 'F' and lvl == 1:
            #     continue

            # skip when no parent
            if not lpp_lst[lvl-1]:
                continue

            # set label, line
            lpp_lst[lvl] = self.AppendItem(lpp_lst[lvl-1], lbl)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # self.SetItemTextColour(lpp_lst[lvl], 'BLUE')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            self.SetItemData(lpp_lst[lvl], lin)

            # set icon
            bmp = ico
            if typ == 'C':
                if lvl == 2:
                    bmp = SDF_ICO_MEMBER
                elif lvl >= 3:
                    bmp = SDF_ICO_FUNCTION

            self.SetItemImage(lpp_lst[lvl], bmp)

        # sort items
        if sort:
            self.SortChildren(top_node)
            child, cookie = self.GetFirstChild(top_node)
            while child.IsOk():
                self.SortChildren(child)
                child, cookie = self.GetNextChild(top_node, cookie)

#HACK, though 'SymbolTree' is no list, use 'update' as core method here
#FIX, when 'Refresh' called ('ico_rfr'), DESTROY CURRENT 'SymbolTree' instance
    def _update(self, doc=None):
        self.__init__(self.prt, doc)

    def _activate_item(self, evt):
#NOTE, workaround: see also 'SidePanel._resize'
#NOTE, workaround: 'RuntimeError: wrapped C/C++ object of type SymbolTree has been deleted'
        if not self:
            return

        itm = evt.Item
        dta = self.GetItemData(itm)
        if dta is None:
            evt.Skip()
            return
        lin = int(dta)
        lbl = self.GetItemText(itm)
        DBG('GEN', f'line {lin:4}: [{lbl}]')
        doc.GotoLine(lin - 1)
        doc.LineEndExtend()
        if glb.CFG['SymbolDef']['CentreCaret']:
            doc.VerticalCentreCaret()
#FIX, use 'wx.CallAfter(dbf.FOCUS, doc)' in bookmark/breakpoint/task controls, too
        wx.CallAfter(dbf.FOCUS, doc)


# @curdoc_class(curdoc)
class MacroList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):
        super().__init__(prt, 'MAC')
        DBG('SPN', f'{me_()}')

    def _update(self, doc=None):
        for nam, dsc in SPT_DUMMY['MAC'].items():
            DBG('SPN', f'    mac = [{nam}: {dsc}]')

            row = ('', nam, dsc)
            self.add_item(row, glb.CFG['Macro']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
        print(f'{me_("C, F")}: not implemented, yet ...')
        ...


# @curdoc_class(curdoc)
class TaskList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, doc):
        super().__init__(prt, 'TSK', doc, srt_col=2)
        DBG('TSK', f'{me_()}')

        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'TSK'))
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.delete_item)

    def _update(self, doc):
        flg = stc.STC_FIND_MATCHCASE | stc.STC_FIND_REGEXP

        to = doc.LastPosition
        DBG('TSK', f'  to = [{to}]')

        for tsk in TSK_TAGS:
            fr, tsk = 0, f'^{tsk}'  # match from BOL
            while (pos := doc.FindText(fr, to, tsk, flg)) != stc.STC_INVALID_POSITION:
                lin = doc.LineFromPosition(pos)
                if glb.CFG['Task']['ShowMarker']:
                    doc.MarkerAdd(lin, MRK['TSK']['NUM'])
                col = doc.GetColumn(pos) + 1
                dsc = doc.GetLine(lin).replace(tsk, TXT_NIL)
                dsc = dsc.lstrip(', ')  # strip comma/space
                DBG('TSK', f'    tsk = [{tsk:>6}] - [{lin:5d} /{col:2d}]')

                row = ('', tsk[1:], f'{lin + 1}', dsc, 'Reserved')
                self.add_item(row, glb.CFG['Task']['ListRowAltColour'])

                fr = pos + len(tsk)

    def _activate_item(self, evt, idx):
        DBG('TSK', f'{me_()}')
        # obj = evt.EventObject
        # idx = evt.Index
        lin = int(self.GetItemText(idx, 2))  # lineno
        if DEBUG['TSK']:
            txt = self.GetItemText(idx, 1).rstrip()
            print(f'  [{txt}] on line: {lin}')

        doc.GotoLine(lin - 1)
        doc.LineEndExtend()

        if glb.CFG['Task']['CentreCaret']:
            doc.VerticalCentreCaret()
        dbf.FOCUS(doc)

    # @curdoc
    def delete_item(self, evt):
        if evt.KeyCode != wx.WXK_DELETE or evt.Index < 0:
            return
        DBG('TSK', f'{me_()}')
        idx = evt.Index
        DBG('TSK', f'  delete #{idx + 1}: [{self.GetItemText(idx, 3).rstrip()}]')
        lin = int(self.GetItemText(idx, 2))  # lineno
        glb.SBR.set_text('Task deleted from line %d' % (lin))

        doc.GotoLine(lin - 1)
        doc.LineDownExtend()
        doc.Clear()
        if glb.CFG['Task']['CentreCaret']:
            doc.VerticalCentreCaret()
        dbf.FOCUS(doc)

        self.update(doc)
        restore_sort_state(self)

        # select next Task (if any) after delete
        if self.ItemCount:
            idx = idx - 1 if idx >= self.ItemCount else idx
            self.Select(idx)


# @curdoc_class(curdoc)
class BreakpointList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, doc):
        super().__init__(prt, 'BPT', doc)
        DBG('BPT', f'{me_()}')

        # self.prt = prt

        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'BPT'))
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.delete_item)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.enable_item)

    def _update(self, doc):
        # save disabled bp lines
        lin_lst = []
        for idx in range(self.ItemCount):
            ena = self.GetItemText(idx, 2)  # 3rd column: enabled flag
            if ena == 'No':
                lin = int(self.GetItemText(idx, 3))  # 4th column: source line
                lin_lst.append(lin)

        # from gui.editor import LIN_B4_MOD
        # print(f'{LIN_B4_MOD=}')

        dbf.call_stack(f'{me_("F")}')
        self.delete_all_items()

        for bpt in doc.get_breakpoints():
            DBG('BPT', '    bpt = [%s]' % str(bpt))
            # restore disabled bp lines
            bpn = bpt[0]
            ena = bpt[1]  # enabled flag
            lin = bpt[2]  # source line
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # if lin in lin_lst:  # or lin == LIN_B4_MOD:
            if lin in lin_lst:
                ena = 'No'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            row = ('', str(bpn), ena, str(lin), doc.GetLine(lin - 1).strip())
            self.add_item(row, glb.CFG['Breakpoint']['ListRowAltColour'])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, hack: used ONLY at STARTUP -> might integrate wih 'ListCtrlTool.update'
    def update_hack(self, doc, bpt_lst):
        for bpt in bpt_lst:
            DBG('BPT', '    bpt = [%s]' % str(bpt))
            bpn = bpt[0]
            ena = bpt[1]  # enabled flag
            lin = bpt[2]  # source line

            row = ('', str(bpn), ena, str(lin), doc.GetLine(lin - 1).strip())
            self.add_item(row, glb.CFG['Breakpoint']['ListRowAltColour'])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def _activate_item(self, evt, idx):
        DBG('BPT', f'{me_()}')
        # obj = evt.EventObject
        # idx = evt.Index
        lin = int(self.GetItemText(idx, 3))  # lineno
        DBG('BPT', f'  [{self.GetItemText(idx, 1).rstrip()}] on line: {lin}')

        self.goto_breakpoint(doc, lin)
        evt.Skip()

    # @curdoc
    def delete_item(self, evt):
        if evt.KeyCode != wx.WXK_DELETE or evt.Index < 0:
            evt.Skip()  # allow 'enable_item' key handler
            return
        DBG('BPT', f'{me_()}')
        idx = evt.Index
        DBG('BPT', f'  delete #{idx + 1}: [{self.GetItemText(idx, 4).rstrip()}]')
        lin = int(self.GetItemText(idx, 3))  # lineno
        glb.SBR.set_text('Breakpoint deleted from line %d' % (lin))

        self.goto_breakpoint(doc, lin)
        glb.TLW.toggle_breakpoint(evt, lin - 1)
        restore_sort_state(self)

        # select next breakpoint (if any) after delete
        if self.ItemCount:
            idx = idx - 1 if idx >= self.ItemCount else idx
            self.Select(idx)

    # @curdoc
    def enable_item(self, evt):
        if evt.KeyCode != wx.WXK_INSERT or evt.Index < 0:
            evt.Skip()  # allow 'delete_item' key handler
            return
        DBG('BPT', f'{me_()}')
        idx = evt.Index
        bpn = self.GetItemText(idx, 1)  # bp number
        ena = self.GetItemText(idx, 2)  # enabled flag
        lin = int(self.GetItemText(idx, 3))  # lineno
        src = self.GetItemText(idx, 4).rstrip()  # source
        txt = 'Dis' if ena == 'Yes' else 'En'
        print(f'  {txt:>3}able #{bpn}: [{src}]')
        glb.SBR.set_text(f'{txt}abled breakpoint {bpn} on line {lin}')

        glb.TLW.enable_breakpoint(evt, lin - 1)

    def goto_breakpoint(self, doc, lin):
        doc.GotoLine(lin - 1)
        doc.LineEndExtend()
        if glb.CFG['Breakpoint']['CentreCaret']:
            doc.VerticalCentreCaret()
        dbf.FOCUS(doc)


# @curdoc_class(curdoc)
class DebugList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):
        super().__init__(prt, 'DBG', srt_col=2)
#FIX, sort order after filter use
        # ColSorter.SortListItems(self, col=1)  # sort by debug type

    def _update(self, doc=None):
        for typ, val in DEBUG.items():
            DBG('GEN', '    dbg = [%-5s = %1d]' % (typ, val))

            row = ('', typ, 'ON' if val else 'off', '%d' % (val), '_TODO_', 'Reserved')
            self.add_item(row, glb.CFG['Debug']['ListRowAltColour'], extra=val)

    def _activate_item(self, evt, idx):
        DBG('GEN', f'{me_()}')
        # idx = evt.Index
        sty = wx.OK | wx.ICON_INFORMATION
#DONE, needs better coding..., use 'itm' as list
        itm_lst = []
        for col in range(1, self.ColumnCount):
            itm_lst.append(self.GetItemText(idx, col).rstrip())
        cap = 'Debug Property Information'
#INFO, URL=https://stackoverflow.com/questions/5299796/how-to-use-list-or-tuple-as-string-formatting-value/43882351
        msg = 'Type        = %s\nStatus      = %s\nValue       = %s\nReserved = %s\n\nDescription:\n%s' % tuple(itm_lst)
        msg_box(self, 'INFO', msg, extra='Debug Property')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, for 'class DocMap', see module 'docmap.py'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# @curdoc_class(curdoc)
class ConfigList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):
        super().__init__(prt, 'CFG')
        DBG('SPN', f'{me_()}')

        # selection colours
        self.clr_sec = glb.CFG['Config']['SectionSelBackColour']
        self.clr_key = glb.CFG['Config']['KeySelBackColour']
        self.clr_val = 'RED'  #  glb.CFG['Config']['ValSelBackColour']

    def _update(self, doc=None):
        idx = 0

        for sec in glb.CFG:
            for key in glb.CFG[sec]:
                idx += 1
                val = glb.CFG[sec][key]
                typ = d_type(val)
                DBG('SPN', f'    cfg = [{sec}], [{key}], [{typ}], [{val}], "desc"')

                row = ('', str(idx), sec, key, typ, str(val), 'desc')
                self.add_item(row, glb.CFG['Config']['ListRowAltColour'])
                # print(f'[{sec}], [{key}], [{typ}], [{val}]')

    def _activate_item(self, evt, idx):
    # def post_activate_item(self, evt, idx):

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # glb.TLW.Freeze()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # when needed, open/focus config file
        fnm = LOC['CFG']['FIL']

        if (doc := glb.DOC).pnm != fnm:
#NOTE, prevent circular dependency
            from common.file import open_files

            fil_lst = [[fnm]]
            doc = open_files(fil_lst)
            doc.SetReadOnly(True)
            glb.NBK.update_page_tab(doc)


        # doc = glb.DOC
        # if (fnm := LOC['CFG']['FIL']) != doc.fnm:  # or is_open_file(fnm):
        #     fil_lst = [[fnm]]
        #     doc = open_files(fil_lst)

        # get values from list
        sec = f'[{self.GetItemText(idx, 2)}]'  # '[section]'
        key = f'{self.GetItemText(idx, 3)}'    # 'key'
        val = f'{self.GetItemText(idx, 5)}'    # 'val'

        # init find
        res = 0
        flg = stc.STC_FIND_MATCHCASE | stc.STC_FIND_WHOLEWORD
        to = doc.LastPosition

        # find section
        fr, fnd = 0, sec
        if (pos := doc.FindText(fr, to, fnd, flg)) != stc.STC_INVALID_POSITION:
            res = 1
            lin = lin_sec = doc.LineFromPosition(pos)
            sel_sec = (pos, pos + len(fnd))
            # find key
            fr, fnd = pos + len(fnd), key
            if (pos := doc.FindText(fr, to, fnd, flg)) != stc.STC_INVALID_POSITION:
                res = 2
                lin = lin_key = doc.LineFromPosition(pos)
                sel_key = (pos, pos + len(fnd))
                # # find value
                # fr, fnd = pos + len(fnd), val
                # if (pos := doc.FindText(fr, to, fnd, flg)) != stc.STC_INVALID_POSITION:
                #     res = 3
                #     lin = lin_val = doc.LineFromPosition(pos)
                #     sel_val = (pos, pos + len(fnd))

        # when find successful (at least once)
        if res > 0:
            doc.SelectNone()
            doc.SetSelBackground(True, self.clr_sec)
            # found section only
            if res == 1:
                doc.SetSelection(*sel_sec)
                # doc.GotoLine(lin_sec)
                # doc.LineEndExtend()
                doc.SwapMainAnchorCaret()
                doc.SetFirstVisibleLine(lin)
                doc.EnsureCaretVisible()
            # found section and key
            elif res == 2:
                doc.SetAdditionalSelBackground(self.clr_key)
                for sel in range(2):
                    lin, sel_fnc = (lin_sec, doc.SetSelection) if not sel else (lin_key, doc.AddSelection)
                    # pos = doc.PositionFromLine(lin)
                    sel_cur = sel_sec if not sel else sel_key
                    sel_fnc(*sel_cur)
                    # doc.LineEndExtend()
                    doc.SwapMainAnchorCaret()
                    if not sel:
                        doc.SetFirstVisibleLine(lin)
                    doc.RotateSelection()  # ensure section is main selection
                    doc.EnsureCaretVisible()
            # # found section, key and value
            # elif res == 3:
            #     # doc.SetAdditionalSelBackground(self.clr_val)
            #     for sel in range(3):
            #         lin, sel_fnc = (lin_sec, doc.SetSelection) if not sel else (lin_val, doc.AddSelection)
            #         # pos = doc.PositionFromLine(lin)
            #         sel_cur = sel_sec if not sel else sel_key if sel == 1 else sel_val
            #         sel_fnc(*sel_cur)
            #         # doc.LineEndExtend()
            #         doc.SwapMainAnchorCaret()
            #         if not sel:
            #             doc.SetFirstVisibleLine(lin)
            #         doc.RotateSelection()  # ensure section is main selection
            #         doc.EnsureCaretVisible()

            if glb.CFG['Config']['CentreCaret']:
                doc.VerticalCentreCaret()

        dbf.FOCUS(doc)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # glb.TLW.Thaw()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if DEBUG['GEN']:
            if res == 0:
                typ, msg = 'ERROR', f'Section {sec} not found'
            elif res == 1:
                typ, msg = 'WARN',  f'Section {sec} found on line [{lin_sec + 1}].\n\nKey [{key}] not found'
            else:
                typ, msg = 'INFO',  f'Section {sec} found on line [{lin_sec + 1}].\n\nKey [{key}] found on line [{lin_key + 1}]'
#NOTE, wx.CallAfter prevents crash (cause unknown)
            wx.CallAfter(msg_box, self, typ, msg)


# @curdoc_class(curdoc)
class EnvironmentList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):
        super().__init__(prt, 'ENV')
        DBG('SPN', f'{me_()}')

    def _update(self, doc=None):
        for nam, dsc in SPT_DUMMY['ENV'].items():
            DBG('SPN', f'    env = [{nam}: {dsc}]')

            row = ('', nam, dsc)
            self.add_item(row, glb.CFG['Environment']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
        print(f'{me_("C, F")}: not implemented, yet ...')
        ...


# @curdoc_class(curdoc)
class HelpList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):
        super().__init__(prt, 'HLP')
        DBG('SPN', f'{me_()}')

    def _update(self, doc=None):
        for nam, dsc in SPT_DUMMY['HLP'].items():
            DBG('SPN', f'    hlp = [{nam}: {dsc}]')

            row = ('', nam, dsc)
            self.add_item(row, glb.CFG['Help']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
        print(f'{me_("C, F")}: not implemented, yet ...')
        ...


# @curdoc_class(curdoc)
class PylintList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, class or instance variable?
#FIX, find better var name!
    out = None
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self, prt, doc):
        super().__init__(prt, 'PLT')
        DBG('SPN', f'{me_()}')

    def _update(self, doc):
        for lin_txt in self.out:
            if lin_txt.count(':') != 6:
                continue
            lin, col, cat, id_, sym, obj, msg = lin_txt.split(':')
            DBG('SPN', f'    plt = [{lin}], [{col}], [{cat}], [{id_}], [{sym}], [{obj}], [{msg}]')

            row = ('', str(lin), str(int(col) + 1), cat, id_, sym, obj, msg)
            self.add_item(row, glb.CFG['Pylint']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
        DBG('GEN', f'{me_()}')
        # idx = evt.Index
        lin = int(self.GetItemText(idx, 1))  # lineno
        col = int(self.GetItemText(idx, 2))  # column
        DBG('GEN', f'  [{self.GetItemText(idx, 1).rstrip()}] on line: {lin}')

        doc.GotoPos(doc.PositionFromLine(lin - 1) + col - 1)
        doc.LineEndExtend()
        if glb.CFG['Pylint']['CentreCaret']:
            doc.VerticalCentreCaret()
        dbf.FOCUS(doc)
        evt.Skip()

    def run(self, doc):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, EXAMPLES:
        # cmd = 'pylint --msg-template="{path}:{line}: {category} ({msg_id}, {symbol}, {obj}) {msg}" <file>'
        # cmd = 'pylint --enable-all-extensions <file>'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        dbf.TIMER('pylint')

        opt = '--msg-template="{line}:{column}:{category}:{msg_id}:{symbol}:{obj}:{msg}"'
        fil  = doc.pnm.replace('\\', '/')
        cmd = f'{EXE["PYLINT"]} {opt} "{fil}"'

        cmd_output_to_list(self, cmd)

        dbf.TIMER('pylint', 'STOP')


# @curdoc_class(curdoc)
class PyflakesList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, class or instance variable?
#FIX, find better var name!
    out = None
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self, prt, doc):
        super().__init__(prt, 'PFL')
        DBG('SPN', f'{me_()}')

    def _update(self, doc):
#HACK, remove 'filename:' and replace 'col ' w/ 'col:' in Pyflakes output
        doc = glb.DOC
        pnm = Path(doc.pnm).as_posix()
        len_ = len(pnm) + 1  # include ':' delimiter

        for lin_txt in self.out:
            lin_txt = lin_txt[len_:].strip().replace(' ', ':', 1)
            if lin_txt.count(':') != 2:
                continue
            lin, col, msg = lin_txt.split(':')
            DBG('SPN', f'    pfl = [{lin}], [{col}], [{msg}]')

            row = ('', str(lin), str(int(col)), msg)
            self.add_item(row, glb.CFG['Pyflakes']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
        DBG('GEN', f'{me_()}')
        # idx = evt.Index
        lin = int(self.GetItemText(idx, 1))  # lineno
        col = int(self.GetItemText(idx, 2))  # column
        DBG('GEN', f'  [{self.GetItemText(idx, 1).rstrip()}] on line: {lin}')

        doc.GotoPos(doc.PositionFromLine(lin - 1) + col - 1)
        doc.LineEndExtend()
        if glb.CFG['Pyflakes']['CentreCaret']:
            doc.VerticalCentreCaret()
        dbf.FOCUS(doc)
        evt.Skip()

    def run(self, doc):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, EXAMPLES:
        # cmd = 'pyflakes --msg-template="{path}:{line}: {category} ({msg_id}, {symbol}, {obj}) {msg}" <file>'
        # cmd = 'pyflakes --enable-all-extensions <file>'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        dbf.TIMER('pyflakes')

        opt = None
        fil  = doc.pnm.replace('\\', '/')
        cmd = f'{EXE["PYFLAKES"]} "{fil}"'

        cmd_output_to_list(self, cmd)

        dbf.TIMER('pyflakes', 'STOP')


# @curdoc_class(curdoc)
class PycodestyleList(ListCtrlTool):

    # __slots__ = ['', '', '', '', '', '', '', '',]

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, class or instance variable?
#FIX, find better var name!
    out = None
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self, prt, doc):
        super().__init__(prt, 'PYS')
        DBG('SPN', f'{me_()}')

    def _update(self, doc):
        for lin_txt in self.out:
            if lin_txt.count(':') != 3:
                continue
            lin, col, id_, msg = lin_txt.split(':')
            DBG('SPN', f'    pys = [{lin}], [{col}], [{id_}], [{msg}]')

            row = ('', str(lin), str(int(col)), id_, msg)
            self.add_item(row, glb.CFG['Pycodestyle']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
        DBG('GEN', f'{me_()}')
        # idx = evt.Index
        lin = int(self.GetItemText(idx, 1))  # lineno
        col = int(self.GetItemText(idx, 2))  # column
        DBG('GEN', f'  [{self.GetItemText(idx, 1).rstrip()}] on line: {lin}')

        doc.GotoPos(doc.PositionFromLine(lin - 1) + col - 1)
        doc.LineEndExtend()
        if glb.CFG['Pycodestyle']['CentreCaret']:
            doc.VerticalCentreCaret()
        dbf.FOCUS(doc)
        evt.Skip()

    def run(self, doc):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, EXAMPLES:
        # cmd = 'pycodestyle --format="%(path)s:%(row)d:%(col)d:%(code)s:%(text)s" <file>'
        # cmd = 'pycodestyle --config=D:\Dev\D\wx\TSN_SPyE\src\.pycodestyle_BLADIBLA <file>'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        dbf.TIMER('pycodestyle')

        opt = '--format="%(row)d:%(col)d:%(code)s:%(text)s"'
        fil  = doc.pnm.replace('\\', '/')
        cmd = f'{EXE["PYCODESTYLE"]} {opt} "{fil}"'

        cmd_output_to_list(self, cmd)

        dbf.TIMER('pycodestyle', 'STOP')


# @curdoc_class(curdoc)
class VultureList(ListCtrlTool):

# SPyE.py:426: unused import 'is_shown' (90% confidence)
# SPyE.py:431: unused import 'dbf.method_calls' (90% confidence)
# SPyE.py:435: unused import 'SASH_POS' (90% confidence)

    # __slots__ = ['', '', '', '', '', '', '', '',]

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, class or instance variable?
#FIX, find better var name!
    out = None
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def __init__(self, prt, doc):
        super().__init__(prt, 'VLT')
        DBG('SPN', f'{me_()}')

    def _update(self, doc):
        for lin_txt in self.out:
            if lin_txt.count(':') != 3:
                continue
            __, __, lin, msg = lin_txt.split(':')
            DBG('SPN', f'    vlt = [{lin}], [{msg}]')

            row = ('', str(lin), msg)
            self.add_item(row, glb.CFG['Vulture']['ListRowAltColour'])

    def _activate_item(self, evt, idx):
        DBG('GEN', f'{me_()}')
        # idx = evt.Index
        lin = int(self.GetItemText(idx, 1))  # lineno
        DBG('GEN', f'  [{self.GetItemText(idx, 1).rstrip()}] on line: {lin}')

        doc.GotoLine(lin - 1)
        doc.LineEndExtend()
        if glb.CFG['Vulture']['CentreCaret']:
            doc.VerticalCentreCaret()
        dbf.FOCUS(doc)
        evt.Skip()

    def run(self, doc):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, EXAMPLES/HELP:
        # cmd = 'pycodestyle <file>'

        # usage: vulture [options] [PATH ...]

        # positional arguments:
        #   PATH                  Paths may be Python files or directories. For each directory Vulture
        #                         analyzes all contained *.py files.
        # optional arguments:
        #   -h, --help            show this help message and exit
        #   --exclude PATTERNS    Comma-separated list of paths to ignore (e.g., "*settings.py,docs/*.py").
        #                         Patterns may contain glob wildcards (*, ?, [abc], [!abc]). A PATTERN
        #                         without glob wildcards is treated as *PATTERN*.
        #   --ignore-decorators PATTERNS
        #                         Comma-separated list of decorators. Functions and classes using these
        #                         decorators are ignored (e.g., "@app.route,@require_*"). Patterns may
        #                         contain glob wildcards (*, ?, [abc], [!abc]).
        #   --ignore-names PATTERNS
        #                         Comma-separated list of names to ignore (e.g., "visit_*,do_*"). Patterns
        #                         may contain glob wildcards (*, ?, [abc], [!abc]).
        #   --make-whitelist      Report unused code in a format that can be added to a whitelist module.
        #   --min-confidence MIN_CONFIDENCE
        #                         Minimum confidence (between 0 and 100) for code to be reported as unused.
        #   --sort-by-size        Sort unused functions and classes by their lines of code.
        #   -v, --verbose
        #   --version             show program's version number and exit
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        opt = TXT_NIL
        fil  = doc.pnm.replace('\\', '/')
        cmd = f'{EXE["VULTURE"]} {opt} "{fil}"'

        cmd_output_to_list(self, cmd)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# @curdoc_class(curdoc)
class MarkdownHtml(wx.Panel, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt, doc):
        super().__init__(prt)
        mix.Help.__init__(self)
        self.prt = prt
        self.doc = doc

        DBG('SPN', f'{me_()}')

#NOTE, workaround: no further processing, now only handles markdown source code
        if not is_lang(self, doc, 'markdown'):
            return

        self.Bind(wx.EVT_TIMER, self._update)

        # self.SetBackgroundColour(glb.CFG['Markdown']['BackColour'])
        # self.Bind()

        self.tmr_mdn = wx.Timer(self)
        # self.tmr_mdn.Start(25)

        self.wv = wv.WebView.New(self, backend=wv.WebViewBackendIE)
        self.wv.SetSize(glb.SPN.ClientSize)
        self._update(doc)

#HACK, though 'MarkdownHtml' is no list, use 'update' as core method here
#FIX, when 'Refresh' called ('ico_rfr'), DESTROY CURRENT 'MarkdownHtml' instance
    def _update(self, doc=None):
        html = '<head><link rel="stylesheet" href="styles.css" type="text/css" /></head>'
        html += md.markdown(self.doc.GetText(), extensions=['codehilite'])
        # print(os.getcwd())
        # print(html)
        self.wv.SetPage(html, TXT_NIL)

    def run(self, doc):
        ...


# @curdoc_class(curdoc)
class Code2flowGraph(wx.Panel, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):  #, doc):
        super().__init__()
        mix.Help.__init__(self)
        DBG('SPN', f'{me_()}')

        # self.SetBackgroundColour(glb.CFG['Code2flow']['BackColour'])
        # self.Bind()

    def run(self, doc):
        ...


# @curdoc_class(curdoc)
class DiagramsGraph(wx.Panel, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):  #, doc):
        super().__init__()
        mix.Help.__init__(self)
        DBG('SPN', f'{me_()}')

        # self.SetBackgroundColour(glb.CFG['Diagrams']['BackColour'])
        # self.Bind()

    def run(self, doc):
        ...


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@
#TODO, use and REFACTOR SNIPPET CODE from 'D:\Dev\D\wx\TSN_SPyE\dev\docs\scintilla\utouch-master'
#@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# @curdoc_class(curdoc)
class SnippetCode(wx.Panel, mix.Help):

    # __slots__ = ['', '', '', '', '', '', '', '',]

    def __init__(self, prt):  #, doc):
        super().__init__()
        mix.Help.__init__(self)
        DBG('SPN', f'{me_()}')

        # self.SetBackgroundColour(glb.CFG['Snippet']['BackColour'])
        # self.Bind()

    def run(self, doc):
        ...


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: pycodestyle => 'PYS'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@ TESTING COMMANDS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# pycodestyle -v SPyE.py|wc
# pycodestyle -vv SPyE.py|wc
# pycodestyle -vvv SPyE.py|wc
# pycodestyle -vvvv SPyE.py|wc
# pycodestyle -vvvvv SPyE.py|wc
# pycodestyle -v SPyE.py
# pycodestyle -v SPyE.py --config=D:\Dev\D\wx\TSN_SPyE\src\.pycodestyle_BLADIBLA
# pycodestyle SPyE.py --format="%(path)s:%(row)d:%(col)d:%(code)s:%(text)s"

#@@@@@ TESTING COMMANDS: OUTPUT @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#   D:\Dev\D\wx\TSN_SPyE\src>pycodestyle -v SPyE.py|wc
#       64
#            76     695    4492

#   D:\Dev\D\wx\TSN_SPyE\src>pycodestyle -vv SPyE.py|wc
#       64
#          3894    9188   95280

#   D:\Dev\D\wx\TSN_SPyE\src>pycodestyle -vvv SPyE.py|wc
#       64
#         35036  140168  973076

#   D:\Dev\D\wx\TSN_SPyE\src>pycodestyle -vvvv SPyE.py|wc
#       64
#        153330  259117 4335859

#   D:\Dev\D\wx\TSN_SPyE\src>pycodestyle -vvvvv SPyE.py|wc
#       64
#        153330  259117 4335859

#   D:\Dev\D\wx\TSN_SPyE\src>pycodestyle -v SPyE.py --config=D:\Dev\D\wx\TSN_SPyE\src\.pycodestyle_BLADIBLA
#       user configuration: C:\Users\Thom\.pycodestyle
#       cli configuration: D:\Dev\D\wx\TSN_SPyE\src\.pycodestyle_BLADIBLA
#       checking SPyE.py
#       SPyE.py:258:8: E221 multiple spaces before operator
#       SPyE.py:261:11: E221 multiple spaces before operator
#       SPyE.py:263:11: E221 multiple spaces before operator
#       SPyE.py:296:1: E402 module level import not at top of file
#       SPyE.py:388:1: E402 module level import not at top of file
#       SPyE.py:777:151: E501 line too long (172 > 150 characters)
#       SPyE.py:806:5: E301 expected 1 blank line, found 0
#       SPyE.py:826:5: E301 expected 1 blank line, found 0
#       SPyE.py:826:50: E262 inline comment should start with '# '
#       SPyE.py:1436:13: E722 do not use bare 'except'
#       SPyE.py:4364:49: E272 multiple spaces before keyword
#       SPyE.py:4431:22: E222 multiple spaces after operator
#       SPyE.py:4441:18: E222 multiple spaces after operator
#       SPyE.py:4572:1: E302 expected 2 blank lines, found 0
#       SPyE.py:4574:1: E302 expected 2 blank lines, found 0
#       SPyE.py:4576:5: E306 expected 1 blank line before a nested definition, found 0
#       SPyE.py:4578:9: E306 expected 1 blank line before a nested definition, found 0
#       SPyE.py:4592:37: E306 expected 1 blank line before a nested definition, found 0
#       3       E221 multiple spaces before operator
#       2       E222 multiple spaces after operator
#       1       E262 inline comment should start with '# '
#       4       E272 multiple spaces before keyword
#       2       E301 expected 1 blank line, found 0
#       2       E302 expected 2 blank lines, found 0
#       9       E306 expected 1 blank line before a nested definition, found 0
#       39      E402 module level import not at top of file
#       1       E501 line too long (172 > 150 characters)
#       1       E722 do not use bare 'except'
#       64

#   D:\Dev\D\wx\TSN_SPyE\src>pycodestyle SPyE.py --format="%(path)s:%(row)d:%(col)d:%(code)s:%(text)s"
#       SPyE.py:258:8:E221:multiple spaces before operator
#       SPyE.py:261:11:E221:multiple spaces before operator
#       SPyE.py:263:11:E221:multiple spaces before operator
#       SPyE.py:388:1:E402:module level import not at top of file
#       SPyE.py:777:151:E501:line too long (172 > 150 characters)
#       SPyE.py:806:5:E301:expected 1 blank line, found 0
#       SPyE.py:826:5:E301:expected 1 blank line, found 0
#       SPyE.py:826:50:E262:inline comment should start with '# '
#       SPyE.py:1436:13:E722:do not use bare 'except'
#       SPyE.py:4441:18:E222:multiple spaces after operator
#       SPyE.py:4572:1:E302:expected 2 blank lines, found 0
#       SPyE.py:4574:1:E302:expected 2 blank lines, found 0
#       SPyE.py:4576:5:E306:expected 1 blank line before a nested definition, found 0
#       SPyE.py:4578:9:E306:expected 1 blank line before a nested definition, found 0
#       SPyE.py:4580:13:E306:expected 1 blank line before a nested definition, found 0
#       SPyE.py:4592:37:E306:expected 1 blank line before a nested definition, found 0
#       3       E221 multiple spaces before operator
#       2       E222 multiple spaces after operator
#       1       E262 inline comment should start with '# '
#       4       E272 multiple spaces before keyword
#       2       E301 expected 1 blank line, found 0
#       2       E302 expected 2 blank lines, found 0
#       9       E306 expected 1 blank line before a nested definition, found 0
#       39      E402 module level import not at top of file
#       1       E501 line too long (172 > 150 characters)
#       1       E722 do not use bare 'except'
#       64
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# populate list with external command output
def cmd_output_to_list(ctl, cmd):
    args = shlex.split(cmd)

    print(cmd)
    print(f' *    [ {cwd() = } ]\n *           [ {args = } ]\n * [ {which(args[0]) = } ]\n')

    with open(SPT_TMPFIL_NAME, 'w') as output:
        res = SP.run(args, stdout=output, stderr=output)

    with open(SPT_TMPFIL_NAME, encoding='utf-8') as input_:
        ctl.out = input_.readlines()

    Path(SPT_TMPFIL_NAME).unlink()
    ctl.update(None)
    restore_sort_state(ctl)


# return selected side panel tool label
def get_lbl(sel=None):
    if sel is None:
        sel = glb.SPN.GetSelection()
    for spt in SPT.values():
        if spt.idx == sel:
            break
    return spt.lbl


# return selected side panel tool object
def get_spt(key=None):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    doc = glb.DOC
    if key in SPT:
        idx = SPT[key].idx
    else:
        sel = glb.SPN.GetSelection()
        for key, spt in SPT.items():
            if spt.idx == sel:
                idx = spt.idx
                break
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    spt = glb.SPN.sgl_lst[idx] if SPT[key].sgl else doc.spt_lst[idx] if doc else None
    return spt


#NOTE, workaround: no further processing, now only handles markdown source code
def is_lang(obj, doc, typ=None):
    if typ != doc.lng_typ:
        stt = wx.StaticText(obj, label=f'\n WORKAROUND: lng_typ not {typ.title()}! \n')
        stt.SetBackgroundColour(CLR['YELLOW2'])
        return False
    return True


#FIX, not yet sorting ...
#FIX, for 'SDF' ('Symbol'): 'AttributeError: 'SymbolTree' object has no attribute '_col''
def restore_sort_state(ctl):
    print(f'{me_("F")}, {ctl}')

    sort_state = ColSorter.GetSortState(ctl)
    ColSorter.SortListItems(ctl, *sort_state)


def update_choice_labels():
    doc = glb.DOC
    spn = glb.SPN

    DBG('LFL', f'*      File = [{doc.fnm}]')

#@@@@@@@@@
#FIX, ==>> possibly ONLY current item needed, NOT all item labels! <<==
#@@@@@@@@@
    # cycle item labels
    for key, spt in SPT.items():
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, needs better coding...
        # discard when no 'ListCtrl'
        if key in SPT_NO_LCT:
            DBG('LFL', f'{spt.idx:2}', '=> skip', key)
            continue
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        flt_txt = spn.flt_dct[spt.lbl]

        if (ctl := get_spt(key)):
            # update 'FilterBox'
            ctl.mnf_flt.txc_flt.Value = flt_txt
            if DEBUG['LFL']:
                if flt_txt:
                    print(f'* Choice {spt.idx:2d} = [{flt_txt}]')

        DBG('LFL', f'{spt.idx:2}', spt)

        # format filter text
        if flt_txt:
            flt_txt = '*'  # {{{flt_txt}}}'

        # update item label
        lbl = f'{spt.lbl}{rs_(12 - len(spt.lbl), " ")}{flt_txt}'
        spn.chc.SetString(spt.idx, lbl.strip())

    spn.Layout()  # force choice control resize

    DBG('LFL')
