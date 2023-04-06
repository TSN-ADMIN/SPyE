#!/usr/bin/python

from pprint import pprint
import re

import wx
import wx.lib.agw.floatspin as FS
from wx.lib.busy import BusyInfo
import wx.lib.scrolledpanel as SCL

from common.type import (
    is_cbb, is_cbx, is_cpc, is_fpc, is_fsp,
    is_lbx, is_spc, is_stt, is_txc
)
from common.util import set_font
from conf.debug import dbg_TIMER
from const import glb
from const.app import APP
from const.common import TXT_NIL
import gui


# frame title
TTL_FRM = f'{APP["Base"]} - Preferences'

# widgets with a '1 column' span (width)
ONE_COL_SPAN_WIDGETS = (
    wx.ColourPickerCtrl,
    wx.FontPickerCtrl,
    FS.FloatSpin,
    wx.SpinCtrl
)


class Preferences(wx.Dialog):
    def __init__(self, prt):
        super().__init__(prt, id=wx.ID_ANY, title=TTL_FRM, size=wx.Size(690, 633), style=wx.DEFAULT_DIALOG_STYLE)
        self.SetIcon(APP['Icon'])
        self.SetBackgroundColour(CLR['BLUE'])
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.configspec = glb.CFG.configspec

        dbg_TIMER('preferences')

        dlg = BusyInfo('\n\nLoading Preferences ...\n\n', glb.TLW, CLR['BLUE2'], 'BLUE')

        self.init_dialog()
        self.sizers()
        self.binds()
        self.show_panel()
        self.Centre()

        dbg_TIMER('preferences', 'STOP')

    def binds(self):
        self.Bind(wx.EVT_TIMER, lambda e: self.ibr.Dismiss())
        self.txc_flt.Bind(wx.EVT_TEXT, self.filter_search)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.show_panel)
        self.Bind(wx.EVT_BUTTON, self.on_button)
        self.Bind(wx.EVT_CLOSE, self.on_exit)

    def init_dialog(self):
        # infobar
        self.ibr = wx.InfoBar(self)
        self.ibr.SetBackgroundColour(CLR['BLUE'])
        # timer to dismiss infobar after a set delay
        self.tmr_ibr = wx.Timer(self, wx.ID_ANY)

#HACK: remove default close (X) button
        self.ibr.FindWindow('button').Destroy()

        # search filter box
        self.txc_flt = wx.SearchCtrl(self, wx.ID_ANY, pos=(5, 15), size=(175, 25))
        self.txc_flt.SetBackgroundColour(CLR['BLUE2'])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # # indent specific choices
        # chc_lst, spc = [], ' ' * 8
        # for c in PRF_CHC:
        #     chc_lst.append(f'{spc}{c}' if c.startswith(' ')  else c)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # section list
        sty = wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER  # | wx.LC_HRULES | wx.LC_VRULES
        self.lct_sec = wx.ListCtrl(self, wx.ID_ANY, (-1, -1), (175, -1), style=sty)
        self.lct_sec.SetBackgroundColour(CLR['BLUE2'])
        self.lct_sec.InsertColumn(0, TXT_NIL)
        self.lct_sec.SetColumnWidth(0, 155)

        # walk sections/fields
        self.lct_sec.Select(0)   # first list item
        self.sec_pnl_lst = []    # panel objects
        self.flt_sec_dct = {}    # filtered/shown sections
        self.prv_pnl_idx = 0     # last panel index
        self.flg_ini_cmt = True  # force initial_comment (1st section only)
        self.flt_idx = 0

        for sec in self.configspec.sections:
            self.add_section(sec)

        # buttons
        siz = (85, 25)
        self.btn_ok_ = wx.Button(self, wx.ID_OK, '&OK', size=siz)
        self.btn_can = wx.Button(self, wx.ID_CANCEL, '&Cancel', size=siz)
        self.btn_apl = wx.Button(self, wx.ID_APPLY, 'Apply', size=siz)

    def sizers(self):
        bxv1 = wx.BoxSizer(wx.VERTICAL)    # main sizer
        bxv2 = wx.BoxSizer(wx.VERTICAL)    # search filter, section list
        bxh1 = wx.BoxSizer(wx.HORIZONTAL)  # bxv2, section panel
        bxh2 = wx.BoxSizer(wx.HORIZONTAL)  # ok/cancel buttons
        border = 5  # space around widgets (pixels)

        bxv1.Add(self.ibr, 1, wx.EXPAND, border)

        bxv2.Add(self.txc_flt, wx.ID_ANY, wx.LEFT | wx.ALL | wx.ALIGN_BOTTOM, border)
        bxv2.Add(self.lct_sec, 10, wx.ALL, border)

        bxh1.Add(bxv2, 3, wx.EXPAND, border)
        for pnl in self.sec_pnl_lst:
            bxh1.Add(pnl, 8, wx.EXPAND | wx.ALL, border)

        bxv1.Add(bxh1, 15, wx.EXPAND, border)

        for btn in (self.btn_ok_, self.btn_can, self.btn_apl):
            bxh2.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, border)

        bxv1.Add(bxh2, 1, wx.EXPAND, border)

        self.SetSizer(bxv1)
        self.Layout()

    def show_panel(self, evt=None):
        idx = 0 if not evt else self.lct_sec.GetItemData(evt.Index)

        self.Freeze()
        prv_pnl = self.sec_pnl_lst[self.prv_pnl_idx]
        prv_pnl.Hide()
        sel_pnl = self.sec_pnl_lst[idx]
        sel_pnl.Show()
        self.Layout()
        self.Thaw()

        # minimize flicker
        for obj in (self, self.txc_flt, self.lct_sec, sel_pnl):
            obj.Refresh()
            obj.Update()

        self.prv_pnl_idx = idx

    def add_section(self, sec):
        if self.flg_ini_cmt:
            self.flg_ini_cmt = False
            cmt_lst = self.configspec.initial_comment
        else:
            cmt_lst = self.configspec.comments[sec]

        # section label/tooltip: section name OR text in comment's {lbl}/{tip} tag
        sec_lbl, sec_tip, __ = parse_comments(cmt_lst, sec)
        # discard hidden (aka internal) section
        if (sec_lbl, sec_tip) == (None, None):
            return

        # add to filtered/shown sections
        self.flt_sec_dct[self.flt_idx] = [sec, True]
        self.flt_idx += 1

        # add section to list
        idx = self.lct_sec.InsertItem(self.lct_sec.ItemCount, sec)
        self.lct_sec.SetItem(idx, 0, sec)
        self.lct_sec.SetItemData(idx, idx)

        # setup panel
        pnl = SCL.ScrolledPanel(self, style=wx.BORDER_SIMPLE)
        pnl.SetupScrolling()
        pnl.Hide()
        pnl.SetBackgroundColour(CLR['BLUE2'])
        self.sec_pnl_lst.append(pnl)

        # section header
        pnl.stt_hdr = wx.StaticText(pnl, label=sec_lbl)
        set_font(pnl.stt_hdr, siz=12, bold=True)
        pnl.stt_hdr.SetToolTip(sec_tip)
        pnl.stl_hdr = wx.StaticLine(pnl)

        # section fields
        for key, spec in self.configspec[sec].items():
            self.add_field(sec, pnl, key, spec)

        # load section panel
        SectionPanel(sec, pnl)
        # eval(f'Prf{sec}')(sec, pnl)

    def add_field(self, sec, pnl, key, spec):
        # parse field datatype
        typ = spec.split('(')[0]
        wgt, pfx = get_widget_name(typ)
        if not wgt:
            return

        cmt_lst = self.configspec[sec].comments[key]

        # field label/tooltip: key name OR text in comment's {lbl}/{tip} tag
        lbl, tip, props = parse_comments(cmt_lst, key)
        if props:
            print(sec, key, f'{props = }')
        # discard hidden (aka internal) field
        if (lbl, tip) == (None, None):
            return

        lbl = wx.StaticText(pnl, label=f'{lbl:>24}:')
        set_font(lbl, face='Consolas')
        lbl.SetToolTip(tip)

        # construct input field (window name used in 'save_preferences')
        fld = f'{pfx}.{wgt}(pnl, name="{sec}.{key}", size=(-1, 21)'
        val = glb.CFG[sec][key]

        # populate input field
        if wgt in 'ListBox':
            fld = eval(f'{fld}, choices={val})')
        elif wgt in 'ComboBox':
            # parse choices from 'option()' spec
            chc_lst = eval(f'[{spec.split("(")[1].split(")")[0]}]')
            fld = eval(f'{fld}, choices={chc_lst}, style=wx.CB_READONLY)')
        else:
            fld = eval(f'{fld})')

        if wgt in ('CheckBox', 'ComboBox', 'FloatSpin', 'TextCtrl'):
            fld.SetValue(val)
        elif wgt in 'SpinCtrl':
            fld.SetMax(10000)
            fld.SetValue(val)
        elif wgt in 'ColourPickerCtrl':
            fld.SetColour(val)
        elif wgt in 'FontPickerCtrl':
            fnt = fld.Font
            fnt.SetFaceName(val)
            fld.SetSelectedFont(fnt)
            if (btn := fld.PickerCtrl) is not None:
                btn.SetLabel(val)

    def filter_search(self, evt):
        def __found_in(lbl):
            txt = evt.String
            return txt and len(txt) >= 2 and txt.lower() in lbl.lower()

        def __insert_item(idx, sec):
            itm = self.lct_sec.InsertItem(self.lct_sec.ItemCount, sec)
            self.lct_sec.SetItem(itm, 0, sec)
            self.lct_sec.SetItemData(itm, idx)
            return itm

        sec_cnt = key_cnt = 0

        for idx, pnl in enumerate(self.sec_pnl_lst):
            fnd = False
            for wgt in pnl.Children:
                if not is_stt(wgt):
                    continue
                if __found_in(wgt.Label):
                    fnd = True
                    wgt.SetBackgroundColour('#FFFFC1')
                    key_cnt += 1
                else:
                    wgt.SetBackgroundColour(wx.NullColour)

            if fnd or __found_in(self.flt_sec_dct[idx][0]):
                self.flt_sec_dct[idx][1] = True
                sec_cnt += 1
            else:
                self.flt_sec_dct[idx][1] = False

        self.lct_sec.DeleteAllItems()
        if len(evt.String) >= 2:
            for idx, (sec, show) in self.flt_sec_dct.items():
                if not show:
                    continue
                itm = __insert_item(idx, sec)
                self.lct_sec.SetItemBackgroundColour(itm, '#FFFFC1')
        else:
            for idx, (sec, __) in self.flt_sec_dct.items():
                __insert_item(idx, sec)
                self.flt_sec_dct[idx][1] = True

        txt = f'  Filter: {sec_cnt} section(s), {key_cnt} key(s)'
        self.ibr.ShowMessage(txt, wx.ICON_NONE)
        self.tmr_ibr.StartOnce(2500)

        self.lct_sec.Select(0, on=1)  # show 1st section's panel (if exist)
        self.lct_sec.Select(0, on=0)  # item highlight off

        # hide last panel when nothing found
        if not self.lct_sec.ItemCount:
            self.sec_pnl_lst[self.prv_pnl_idx].Hide()

        self.Refresh()
        self.Update()

    def on_button(self, evt):
        def __do_save():
            for idx, pnl in zip(self.flt_sec_dct, self.sec_pnl_lst):
                sec = self.flt_sec_dct[idx][0]
                print(sec, pnl)
                save_preferences(sec, pnl)

        if evt.Id == wx.ID_OK:
            txt = 'OK'
            __do_save()
            self.on_exit()
        elif evt.Id == wx.ID_CANCEL:
            txt = 'Cancel'
            self.on_exit()
        else:
            txt = 'Apply'
            __do_save()
        print(f'Preferences: [{txt}]')

    def on_exit(self, evt=None):
        # when filtering, ignore ESCAPE key/Cancel button
        if self.txc_flt.Value:
            # clear filter instead
            self.txc_flt.Value = TXT_NIL
            txt = f'  Filter Cleared: displaying all sections'
            self.ibr.ShowMessage(txt, wx.ICON_NONE)
            # wx.Bell()
            self.tmr_ibr.StartOnce(2500)
            return

        self.Destroy()


def parse_comments(cmt_lst, val):
    lbl = tip = val  # default
    props = TXT_NIL
    for cmt in cmt_lst:
        if any(t in cmt for t in ('{hidden}', '{internal}')):
            lbl = tip = None
            break
        if  '{disable}' in cmt:
            props += 'disable'
        if  '{readonly}' in cmt:
            props += 'readonly'
        if (txt := parse_tag('lbl', cmt)):
            lbl = txt
        if (txt := parse_tag('tip', cmt)):
            tip = '\n'.join(txt.split('|')).replace('^', '\t')
    return lbl, tip, props


def parse_tag(tag, cmt):
    pat = r'{tag}(.*?){tag}'
    txt = re.findall(re.compile(pat.replace('tag', tag)), cmt)
    # if txt:
    #     print(txt)
    return TXT_NIL if not len(txt) else txt[0]


def get_widget_name(typ):
    # get widget name from section key spec (datatype)
    wgt, pfx = None, 'wx'
    if typ in 'boolean':
        wgt = 'CheckBox'
    elif typ in 'colour':
        wgt = 'ColourPickerCtrl'
    elif typ in 'float':
        pfx = 'FS'
        wgt = 'FloatSpin'
    elif typ in 'font':
        wgt = 'FontPickerCtrl'
    elif typ in 'integer':
        wgt = 'SpinCtrl'
    elif typ in 'list':
        wgt = 'ListBox'
    elif typ in 'option':
        wgt = 'ComboBox'
    elif typ in 'string':
        wgt = 'TextCtrl'
    return wgt, pfx


def save_preferences(sec, pnl):
    # section dict on entry
    before = glb.CFG[sec]

    # walk section panel widgets
    for wgt in pnl.Children:
        # discard non-input/empty fields
        if not wgt.Name.startswith(sec) or (new_val := get_widget_value(wgt)) is None:
            continue
        # store key value when changed
        __, key = wgt.Name.split('.')
        if (old_val := before[key]) != new_val:
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            to, ov, tn, nv = str(type(old_val)), old_val, str(type(new_val)), new_val
            print(f'{sec:>20}.{key:<24} {to} = [{ov}]\n{tn:>{len(tn) + 46}} = [{nv}]\n')
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            glb.CFG[sec][key] = new_val


def get_widget_value(wgt):
    # use widget's 'get' method/property
    if any(fnc(wgt) for fnc in (is_cbb, is_cbx, is_spc, is_txc)):
        val = wgt.Value
    elif is_cpc(wgt):
        val = wgt.Colour
    elif is_fpc(wgt):
        # print(wgt.SelectedFont.FaceName)
        val = wgt.SelectedFont.FaceName
    elif is_fsp(wgt):
        val = wgt.GetValue()
    elif is_lbx(wgt):
        # print(wgt.Name)
        val = None if (idx := wgt.Selection) == wx.NOT_FOUND else wgt.GetString(idx)
    else:
        err = f'{__name__}: unsupported widget [{wgt}]: name[{wgt.Name}]'
        raise AssertionError(err)

    return val


class SectionPanel:
    def __init__(self, sec, pnl):
        self.gbs = wx.GridBagSizer(vgap=0, hgap=0)
        self.gbs.SetFlexibleDirection(wx.BOTH)
        self.gbs.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_ALL)
        self.gbs.SetEmptyCellSize((10, 0))

        self.gbs.SetCols(5)
        self.gbs.AddGrowableCol(4)

        border = 5  # space around widgets (pixels)
        _SZR_ARG = (wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, border)

        # add widgets (header)
        row = col = 1
        for wgt in list(pnl.Children)[:2]:
            self.gbs.Add(wgt, (row, col), (1, 5), *_SZR_ARG)
            row += 1

        # add widgets (labels and input fields)
        for idx, wgt in enumerate(list(pnl.Children)[2:]):
            if not idx % 2:
                self.gbs.Add(wgt, (row, col), (1, 1), wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, border)
            else:
                span = 1 if isinstance(wgt, ONE_COL_SPAN_WIDGETS) else 4
                self.gbs.Add(wgt, (row, col + 1), (1, span), *_SZR_ARG)
                row += 1

        pnl.SetSizer(self.gbs)
        pnl.Layout()


# class PrfGeneral(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSplash(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfWidgetInspectionTool(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfWindow(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfContextMenu(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfBackup(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfToolBar(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfStatusBar(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfInfoBar(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfIndentation(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfLanguage(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSplitter(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfNotebook(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfPageTabHistory(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfEditor(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfMultiEdit(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfCaret(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfCaretPositionHistory(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfMargin(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfEdge(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfDebugger(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfAutoComplete(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfBrace(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfIndicator(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfCallTip(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfHotspot(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfKeyBinding(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfMultiView(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfToolTip(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfGotoAnything(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSymbolBrowser(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSymbolIndex(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSymbolPopup(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfColourToolTip(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfTopLineToolTip(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfFindHistory(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfWhereHistory(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfReplaceHistory(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfLayout(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfPanelEffect(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfRuler(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSidePanel(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSidePanelTool(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfFilter(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfDocument(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfProject(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfBookmark(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfExplorer(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSymbolDef(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfMacro(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfTask(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfBreakpoint(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfDebug(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfConfig(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfHelp(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfPylint(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfPyflakes(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfPycodestyle(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfMarkdown(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfCode2flow(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSnippet(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfCodeContext(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfSearchPanel(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfDocMap(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfCodePreview(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


# class PrfRecentFileHistory(SectionPanel):
#     def __init__(self, sec, pnl):
#         super().__init__(sec, pnl)


if __name__ == '__main__':
    from data.images import catalog as PNG
    CLR = {}
    CLR['BLUE'] = '#E6F2FF'
    CLR['BLUE2'] = '#C6E2FF'
    APP = {}
    APP['Icon'] = PNG['app']

    app = wx.App(False)
    Preferences(None)
    app.MainLoop()
else:
    from const.app import APP, CLR
    from data.images import catalog as PNG
