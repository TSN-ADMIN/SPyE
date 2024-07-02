#!/usr/bin/python

# pylint: disable=W0212(protected-access) [_disabler, _core, _getframe]

import __main__  # used for cfg

from bisect import bisect_left
import fnmatch
import functools
import inspect
import os
from pathlib import Path
from pprint import pprint
import string
import sys

import win32api
import win32gui
import wx
from wx.adv import RichToolTip as RTT
from wx.lib.agw import advancedsplash as AS

from .path import cwd
from .type import is_tlw
from const.common import TXT_NIL, LBL_FNT_STYLES
from const.lang import LANG_WILDCARDS
from const.menubar import MNU_FNT_AUX, MNU_FNT_TYP, NO_ICO
from conf.debug import DBG
from const.app import APP, COMMON_KEYS, MOD_KEYS, OPT_BORDER, TLT_POSITION
from const import glb
from const.sidepanel import SPT
from data.images import catalog as PNG
import extern.supertooltip as STT


class CharValidator(wx.Validator):
    def __init__(self, flag):
        super().__init__()
        self.flag = flag
        # self.SuppressBellOnError(False)  # bell active
        self.Bind(wx.EVT_CHAR, self.on_char)

    def Clone(self):
        # Note that every validator must implement the Clone() method.
        return CharValidator(self.flag)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def on_char(self, evt):
        cod = chr(evt.KeyCode)
        if self.flag == 'digit' and cod not in string.digits and ord(cod) != wx.WXK_BACK:
            tip = RTT(f'Warning', 'Numeric input required !')
            tip.SetBackgroundColour('#FFFFF0')
            tip.SetIcon(wx.ICON_WARNING)
            tip.SetTipKind(wx.adv.TipKind_BottomLeft)
            tip.SetTitleFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            tip.SetTimeout(millisecondsTimeout=1000, millisecondsDelay=5)
            tip.ShowFor(self.Window, wx.Rect(-50, -8, *self.Window.ClientRect[2:]))
            return

        evt.Skip()


class ColourToolTip(STT.SuperToolTip):
    def __init__(self, prt):
        self.sec = glb.CFG['TopLineToolTip']
        super().__init__(TXT_NIL)

#FIX, realize smooth 'TopLineToolTip' attribute coordination:
#FIX,     see 'supertooltip.py': 'SetStartDelay', 'SetEndDelay', 'DoShowNow', 'DoHideNow'
#FIX,     see 'SPyE.cfg', section 'TopLineToolTip': 'UseFade', 'DropShadow', 'DelayHide'

        # self.SetStartDelay(0)
        # print('ON ', glb.NBK.tlt.GetStartDelay())
        # print('OFF', glb.NBK.tlt.GetEndDelay())

        # glb.NBK.tlt.SetStartDelay(2)
        # glb.NBK.tlt.SetEndDelay(5)

        self.SetTarget(prt)
        self.SetMessageFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD, faceName='Courier New'))

        self.SetUseFade(self.sec['UseFade'])
        self.SetDropShadow(self.sec['DropShadow'])

        # self.ApplyStyle('NASA Blue')

        # disable tooltip popup when entering notebook window
        prt.Bind(wx.EVT_ENTER_WINDOW, None)

    def update(self, txt, bgc, pos):
        self.SetBottomGradientColour(bgc)
        self.SetMiddleGradientColour(bgc)
        self.SetTopGradientColour(bgc)
        self.SetTextColour('WHITE' if is_dark(bgc) else 'BLACK')

        self.SetMessage(txt)

        if not self.GetTipWindow():
            self.DoShowNow()
            self.GetTipWindow().SetWindowStyle(OPT_BORDER['SUNKEN'])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: some fun 'SuperToolTip' methods
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         self._superToolTip.MakeWindowTransparent(200)
#         # see '_colourSchemes' in 'extern\supertooltip.py'
#         self.ApplyStyle("Pretty Pink")
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self._superToolTip.SetPosition(pos)
        # self._superToolTip.SetPosition((pos[0], pos[1]+30))

        self.Update()


#INFO, inspired by Notepad++
#INFO, URL=https://github.com/notepad-plus-plus/notepad-plus-plus/blob/master/PowerEditor/src/ScintillaComponent/columnEditor.cpp#L168
#INFO, parts copied/translated from 'ColumnEditorDlg::run_dlgProc' in 'columnEditor.cpp'
class ColumnEditorDialog(wx.Dialog):
    def __init__(self, prt):
        super().__init__(prt, wx.ID_ANY, 'Column / Multi-Selection Editor', size=(410,310))

        self.SetBackgroundColour('#E6F2FF')

        gbs = wx.GridBagSizer(0, 0)
        gbs.SetFlexibleDirection(wx.BOTH)
        gbs.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_ALL)

        self.rdo_txt = wx.RadioButton(self, wx.ID_ANY, '&Text to Insert', style=wx.RB_GROUP)
        self.txc_txt = wx.TextCtrl(self, wx.ID_ANY, '', size=(200,-1))

        self.rdo_num = wx.RadioButton(self, wx.ID_ANY, '&Number to Insert')
        self.stt_ini = wx.StaticText(self, wx.ID_ANY, '&Initial Number:')
        self.txc_ini = wx.TextCtrl(self, wx.ID_ANY, '', validator=CharValidator('digit'))

        self.stt_inc = wx.StaticText(self, wx.ID_ANY, 'Increase b&y:')
        self.txc_inc = wx.TextCtrl(self, wx.ID_ANY, '', validator=CharValidator('digit'))

        self.stt_rpt = wx.StaticText(self, wx.ID_ANY, '&Repeat:')
        self.txc_rpt = wx.TextCtrl(self, wx.ID_ANY, '', validator=CharValidator('digit'))

        self.cbx_ldz = wx.CheckBox(self, wx.ID_ANY, 'Leading &zeros')

        self.rdo_dec = wx.RadioButton(self, wx.ID_ANY, '&Dec', style=wx.RB_GROUP)
        self.rdo_hex = wx.RadioButton(self, wx.ID_ANY, '&Hex')
        self.rdo_oct = wx.RadioButton(self, wx.ID_ANY, '&Oct')
        self.rdo_bin = wx.RadioButton(self, wx.ID_ANY, '&Bin')

#HACK, map OK button to ENTER key
        self.btn_ok_ = wx.Button(self, wx.ID_OK, 'OK')
        self.btn_ok_.SetDefault()

#HACK, map Cancel button to ESCAPE key
        self.btn_esc = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        self.SetEscapeId(wx.ID_CANCEL)

        # replace by 'set_font' in 'util.py' -> set_font(self.rdo_txt, bold=True)
        fnt = self.rdo_txt.Font
        fnt.MakeBold()
        self.rdo_txt.SetFont(fnt)
        # replace by 'set_font' in 'util.py' -> set_font(self.rdo_num, bold=True)
        fnt = self.rdo_num.Font
        fnt.MakeBold()
        self.rdo_num.SetFont(fnt)

        _all = wx.ALL
        _alr = wx.ALIGN_RIGHT
        _acv = wx.ALIGN_CENTER_VERTICAL

        gbs.Add(self.rdo_txt, (0, 0), (1, 1), _all, 5)
        gbs.Add(self.txc_txt, (1, 0), (1, 2), _all|_alr, 5)
        gbs.Add(self.btn_ok_, (1, 2), (1, 1), _all, 5)
        gbs.Add(self.btn_esc, (2, 2), (1, 1), _all, 5)
        gbs.Add(self.rdo_num, (3, 0), (1, 1), _all, 5)
        gbs.Add(self.stt_ini, (4, 0), (1, 1), _all|_acv|_alr, 5)
        gbs.Add(self.txc_ini, (4, 1), (1, 1), _all, 5)
        gbs.Add(self.stt_inc, (5, 0), (1, 1), _all|_acv|_alr, 5)
        gbs.Add(self.txc_inc, (5, 1), (1, 1), _all, 5)
        gbs.Add(self.stt_rpt, (6, 0), (1, 1), _all|_acv|_alr, 5)
        gbs.Add(self.txc_rpt, (6, 1), (1, 1), _all, 5)
        gbs.Add(self.cbx_ldz, (6, 2), (1, 1), _all|_acv, 5)
        gbs.Add(self.rdo_dec, (7, 1), (1, 1), _all, 5)
        gbs.Add(self.rdo_hex, (7, 2), (1, 1), _all, 5)
        gbs.Add(self.rdo_oct, (8, 1), (1, 1), _all, 5)
        gbs.Add(self.rdo_bin, (8, 2), (1, 1), _all, 5)

        gbs.AddGrowableCol(2)
        gbs.AddGrowableRow(6)

        self.binds()
        self.__on_radio(None)

        self.SetSizer(gbs)
        self.Layout()
        self.Centre(wx.BOTH)

    def binds(self):
        self.btn_ok_.Bind(wx.EVT_BUTTON, self.__on_confirm)
        # self.btn_ok_.Bind(wx.EVT_BUTTON, lambda e: self.__on_confirm(e))
        self.btn_esc.Bind(wx.EVT_BUTTON, self.__on_exit)
        self.rdo_txt.Bind(wx.EVT_RADIOBUTTON, self.__on_radio)
        self.rdo_num.Bind(wx.EVT_RADIOBUTTON, self.__on_radio)
        self.rdo_dec.Bind(wx.EVT_RADIOBUTTON, self.__on_radio)
        self.rdo_hex.Bind(wx.EVT_RADIOBUTTON, self.__on_radio)
        self.rdo_oct.Bind(wx.EVT_RADIOBUTTON, self.__on_radio)
        self.rdo_bin.Bind(wx.EVT_RADIOBUTTON, self.__on_radio)

    def __on_radio(self, evt):
        getattr(self, 'txc_txt').Enable(True if self.rdo_txt.Value else False)
        for wgt in ('stt_ini', 'txc_ini', 'stt_inc', 'txc_inc', 'stt_rpt', 'txc_rpt',
                    'cbx_ldz', 'rdo_dec', 'rdo_hex', 'rdo_oct', 'rdo_bin'):
            getattr(self, wgt).Enable(False if self.rdo_txt.Value else True)

        print(self.rdo_txt.Value)
        print(self.rdo_num.Value)
        print(self.rdo_dec.Value)
        print(self.rdo_hex.Value)
        print(self.rdo_oct.Value)
        print(self.rdo_bin.Value)
        print()

    def __on_confirm(self, evt):
        """
        ColumnModeInfos ScintillaEditView::getColumnModeSelectInfo()
        {
            ColumnModeInfos columnModeInfos
            # Multi-Selection or Column mode
            if (cnt := doc.Selections) > 1:
                for sel in range(cnt):
                    sel_spos = doc.GetSelectionNAnchor(sel)
                    sel_epos = doc.GetSelectionNCaret(sel)
                    anchor_vrt_spc = doc.GetSelectionNAnchorVirtualSpace(sel)
                    caret_vrt_spc = doc.GetSelectionNCaretVirtualSpace(sel)

                    if sel_spos == sel_epos and doc.SelectionIsRectangle():
                        bool dir = anchor_vrt_spc<caret_vrt_spc?L2R:R2L
                        columnModeInfos.push_back(ColumnModeInfo(sel_spos, sel_epos, sel, dir, anchor_vrt_spc, caret_vrt_spc))
                    elif sel_spos > sel_epos:
                        columnModeInfos.push_back(ColumnModeInfo(sel_epos, sel_spos, sel, R2L, anchor_vrt_spc, caret_vrt_spc))
                    else:
                        columnModeInfos.push_back(ColumnModeInfo(sel_spos, sel_epos, sel, L2R, anchor_vrt_spc, caret_vrt_spc))
            return columnModeInfos
        }
        """
        """
            if doc.SelectionIsRectangle() or doc.Selections > 1:
                ColumnModeInfos colInfos = getColumnModeSelectInfo()
                std::sort(colInfos.begin(), colInfos.end(), SortInPositionOrder())
                columnReplace(colInfos, str)
                std::sort(colInfos.begin(), colInfos.end(), SortInSelectOrder())
                setMultiSelections(colInfos)
            else:
        """

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        def getColumnModeSelectInfo():
            columnModeInfos = []
            # Multi-Selection or Column mode
            if (cnt := doc.Selections) > 1:
                for sel in range(cnt):
                    sel_spos = doc.GetSelectionNAnchor(sel)
                    sel_epos = doc.GetSelectionNCaret(sel)
                    anchor_vrt_spc = doc.GetSelectionNAnchorVirtualSpace(sel)
                    caret_vrt_spc = doc.GetSelectionNCaretVirtualSpace(sel)

                    lin = doc.LineFromPosition(sel_spos)
                    print(f'{lin=}, {sel=}, {sel_spos=}, {sel_epos=}, {anchor_vrt_spc=}, {caret_vrt_spc=}')

                    txt = self.txc_txt.Value

                    pfx = (caret_vrt_spc) * ' '
                    txt = f'{pfx}{txt}'

                    doc.InsertText(sel_spos, txt)

                    # if sel_spos == sel_epos and doc.SelectionIsRectangle():
                    #     bool dir = anchor_vrt_spc<caret_vrt_spc?L2R:R2L
                    #     columnModeInfos.push_back(ColumnModeInfo(sel_spos, sel_epos, sel, dir, anchor_vrt_spc, caret_vrt_spc))
                    # elif sel_spos > sel_epos:
                    #     columnModeInfos.push_back(ColumnModeInfo(sel_epos, sel_spos, sel, R2L, anchor_vrt_spc, caret_vrt_spc))
                    # else:
                    #     columnModeInfos.push_back(ColumnModeInfo(sel_spos, sel_epos, sel, L2R, anchor_vrt_spc, caret_vrt_spc))
            # return columnModeInfos
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        doc = glb.NBK.CurrentPage  # .txt1

        doc.BeginUndoAction()

        if self.rdo_txt.Value:
            if doc.SelectionIsRectangle() or doc.Selections > 1:
                getColumnModeSelectInfo()
                # ColumnModeInfos colInfos = getColumnModeSelectInfo()
                # std::sort(colInfos.begin(), colInfos.end(), SortInPositionOrder())
                # columnReplace(colInfos, str)
                # std::sort(colInfos.begin(), colInfos.end(), SortInSelectOrder())
                # setMultiSelections(colInfos)
            else:
                spos = doc.CurrentPos
                scol = doc.GetColumn(spos)
                slin = doc.LineFromPosition(spos)
                epos = doc.TextLength
                elin = doc.LineFromPosition(epos)

                # print(f'{spos=}, {scol=}, {slin=}, {epos=}, {elin=}')

                for lin in range(slin, elin + 1):
                    lin_spos = doc.PositionFromLine(lin)
                    lin_epos = doc.GetLineEndPosition(lin)

                    lin_ecol = doc.GetColumn(lin_epos)
                    lin_len = lin_epos - lin_spos + 1

                    # print(f'{lin=}, {lin_spos=}, {lin_epos=}, {lin_ecol=}, {lin_len=}')

                    txt = self.txc_txt.Value

                    if (lin_ecol <= scol):
                        # prefix spaces
                        pfx = (scol - lin_ecol) * ' '
                        txt = f'{pfx}{txt}'
                        doc.InsertText(lin_epos, txt)
                    else:
                        ins_pos = doc.FindColumn(lin, scol)
                        print(f'{lin=}, {ins_pos=}')
                        doc.InsertText(ins_pos, txt)
        else:
            ini = 0 if not self.txc_ini.Value else int(self.txc_ini.Value)
            inc = 0 if not self.txc_inc.Value else int(self.txc_inc.Value)
            rpt = 0 if not self.txc_rpt.Value else int(self.txc_rpt.Value)
            ldz = self.cbx_ldz.Value

            if self.rdo_dec.Value:
                fmt = 'd'
            elif self.rdo_hex.Value:
                fmt = 'x'
            elif self.rdo_oct.Value:
                fmt = 'o'
            elif self.rdo_bin.Value:
                fmt = 'b'

            print(ini, inc, rpt, ldz)
            print(f'{ini:{fmt}}')
            # print(f'{self.txc_ini.Value:{fmt}}')

        doc.EndUndoAction()

        self.__on_exit(None)

    def __on_exit(self, evt):
        self.Destroy()


#FIX, replace 'GridSizer' sizer with 'GridBagSizer', see 'search_panel.set_mode'
class QuickOpenDialog(wx.Dialog):
    def __init__(self, prt):
        super().__init__(prt, id=wx.ID_ANY, title='Quick Open',
                         size=(430, 210), style=wx.DEFAULT_DIALOG_STYLE)

        self.fnm_len = self.prv_fnm_len = 0

        self.stt_fnm = wx.StaticText(self, wx.ID_ANY, '&Filename (or wildcard pattern):')
        self.txc_fnm = wx.TextCtrl(self, wx.ID_ANY, '', size=(300, -1))
        self.btn_brw = wx.Button(self, wx.ID_ANY, '&Browse...')
        self.stt_pnm = wx.StaticText(self, wx.ID_ANY, '&Path:')
        self.txc_pnm = wx.TextCtrl(self, wx.ID_ANY, '', size=(300, -1), style=wx.TE_READONLY)
        self.cbx_opn = wx.CheckBox(self, wx.ID_ANY, 'Open all &matching files from subdirectories')
        self.btn_opn = wx.Button(self, wx.ID_OK, '&Open')
        self.btn_clo = wx.Button(self, wx.ID_CANCEL, '&Close')

        grs = wx.GridSizer(6, 2, 0, 0)
        border = 5

        # convenient short naming (sizer flags)
        CV = wx.ALIGN_CENTRE_VERTICAL
        BT = wx.ALIGN_BOTTOM
        LT = wx.LEFT
        RT = wx.ALIGN_RIGHT | wx.ALL
        XP = ((0, 0), 1, wx.EXPAND, border)

        grs.Add(self.stt_fnm, 0, LT | BT, border)
        grs.Add(*XP)
        grs.Add(self.txc_fnm, 0, LT | CV, border)
        grs.Add(self.btn_brw, 0, RT | CV, border)
        grs.Add(self.stt_pnm, 0, LT | BT, border)
        grs.Add(*XP)
        grs.Add(self.txc_pnm, 0, LT,      border)
        grs.Add(*XP)
        grs.Add(self.cbx_opn, 0, LT | CV, border)
        grs.Add(self.btn_opn, 0, RT | CV, border)
        grs.Add(*XP)
        grs.Add(self.btn_clo, 0, RT | CV, border)

        self.binds()

        self.btn_opn.SetDefault()

        self.update_file_list()

        self.SetSizer(grs)
        self.Layout()
        self.Centre()

    def binds(self):
        self.txc_fnm.Bind(wx.EVT_CHAR, self.on_char)
        self.cbx_opn.Bind(wx.EVT_CHECKBOX, self.__on_match_subdirs)
        self.btn_brw.Bind(wx.EVT_BUTTON, self.__on_browse)
        self.btn_opn.Bind(wx.EVT_BUTTON, self.__on_open)
        self.btn_clo.Bind(wx.EVT_BUTTON, self.__on_exit)
        self.Bind(wx.EVT_CLOSE, self.__on_exit)

    def update_file_list(self, force=False):
        self.fil_lst = []

#HACK, every char typed into 'Filename' field is seen here
        # update file list only if it was a readable char
        # check current vs. previous field lengths
        self.fnm_len = len(self.txc_fnm.Value)
        if force or self.prv_fnm_len != self.fnm_len:
            self.prv_fnm_len = self.fnm_len

            fnm = self.txc_fnm.Value  # may contain glob pattern
            pnm = self.txc_pnm.Value  # directory to walk
            # get matching files ...
            if self.cbx_opn.Value:
                # ... in current dir and subdirs
                for root, __, files in os.walk(pnm):
                    for nam in files:
                        pat = os.path.join(root, nam)
                        if fnmatch.fnmatch(nam, fnm):
                            self.fil_lst.append([pat])
            # get matching files ...
            else:
                # ... in current dir only
                for nam in os.listdir(pnm):
                    pat = os.path.join(pnm, nam)
                    if os.path.isfile(pat) and fnmatch.fnmatch(nam, fnm):
                        self.fil_lst.append([pat])

        # tooltip, title
        txt = f'Quick Open - Matching Files: [{len(self.fil_lst)}]'
        self.ttp = f'{txt}\n\n'
        for pnm in self.fil_lst:
            pat = pnm[0].replace("\\\\", "\\")
            self.ttp += f'{pat}\n'
        self.SetToolTip(self.ttp)
        self.SetTitle(f'{txt}')

    def on_char(self, evt):
#HACK, catch every char typed into 'Filename' field
        evt.Skip()
        wx.CallAfter(self.update_file_list)

    def __on_match_subdirs(self, evt):
        self.update_file_list(force=True)

    def __on_browse(self, evt):
#NOTE, prevent circular dependency
        from .file import split_path

        sty = wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_PREVIEW | wx.FD_FILE_MUST_EXIST
        with wx.FileDialog(self, 'Select File', cwd(), '', LANG_WILDCARDS, sty) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                # pnm = dlg.Path
                dnm, fnm, __, __ = split_path(dlg.Path)
                if not self.txc_fnm.Value:
                    self.txc_fnm.Value = fnm
                self.txc_pnm.Value = dnm
                self.update_file_list(force=True)

    def __on_open(self, evt):
#NOTE, prevent circular dependency
        from .file import open_files

        pprint(self.fil_lst)

        if self.fil_lst:
            open_files(self.fil_lst)
        else:
            fnm = self.txc_fnm.Value
            pnm = self.txc_pnm.Value
            msg = f'NO files matching\n    [{fnm}]\nin subdirectory\n    [{pnm}]'
            self.Hide()
            msg_box(self, 'INFO', msg, extra='Quick Open')
            self.Show()
            return

        self.__on_exit(None)

    def __on_exit(self, evt):
        self.Destroy()


class TopLineToolTip(STT.SuperToolTip):
    def __init__(self, prt):
        self.sec = glb.CFG['TopLineToolTip']
        super().__init__(TXT_NIL)

#FIX, realize smooth 'TopLineToolTip' attribute coordination:
#FIX,     see 'supertooltip.py': 'SetStartDelay', 'SetEndDelay', 'DoShowNow', 'DoHideNow'
#FIX,     see 'SPyE.cfg', section 'TopLineToolTip': 'UseFade', 'DropShadow', 'DelayHide'

        # self.SetStartDelay(0)
        # print('ON ', glb.NBK.tlt.GetStartDelay())
        # print('OFF', glb.NBK.tlt.GetEndDelay())

        # glb.NBK.tlt.SetStartDelay(2)
        # glb.NBK.tlt.SetEndDelay(5)

        self.SetTarget(prt)
        self.SetMessageFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD, faceName='Courier New'))

        bgc, fgc = self.sec['BackColour'], self.sec['ForeColour']
        self.SetBottomGradientColour(bgc)
        self.SetMiddleGradientColour(bgc)
        self.SetTopGradientColour(bgc)
        self.SetTextColour(fgc)

        self.SetUseFade(self.sec['UseFade'])
        self.SetDropShadow(self.sec['DropShadow'])

        # self.ApplyStyle('NASA Blue')

        # disable tooltip popup when entering notebook window
        prt.Bind(wx.EVT_ENTER_WINDOW, None)

    def update(self, evt, doc, top, col):
        if not self.IsEnabled():
            # update only statusbar
            glb.SBR.set_text('Top Line: %d' % (top + 1), 'AUX')
            return

        # handle both scrollbars
        # if hasattr(evt, 'Orientation') and evt.Orientation == wx.VERTICAL:
        txt = self.sec['Text']
        self.SetMessage(txt % (doc.DocLineFromVisible(top) + 1, top + 1, col))

        if not self.GetTipWindow():
            self.DoShowNow()
            self.GetTipWindow().SetWindowStyle(OPT_BORDER['SUNKEN'])

        # convert editor client rectangle to screen coordinates
        clt = doc.ClientRect
        rct = wx.Rect(doc.ClientToScreen(clt.Position), clt.Size)
        loc = TLT_POSITION['TR']  # top right
        DBG('SCL', '  TopLineToolTip: LOC:', loc, '| RECT:', rct)

        self._superToolTip.SetPosition((rct[0] + rct[2] + loc[0], rct[1] + loc[1]))
        self.Update()


#HACK, avoid "DeprecationWarning: an integer is required (got type WindowIDRef)."
#INFO, URL=https://discuss.wxpython.org/t/deprecation-warnings-with-python-3-8/34405
def WindowIDRef_hack():
    wx._core.WindowIDRef.__index__ = wx._core.WindowIDRef.__int__


def create_symbol_index():
    if not glb.CFG['SymbolIndex']['Enable']:
        return

#NOTE, prevent circular dependency
    from tool.symbol import SymbolIndex
    from conf.debug import dbf

    sym_idx = SymbolIndex()  # Python symbol index object
    app = glb.APP
    app.dfn_idx, app.ref_idx, app.imp_idx, app.var_idx, app.wrd_idx, app.qts_idx = sym_idx.create()
    dbf.SYMBOL_INDEX_COUNTS(desc=False, word=False, total=False, count=False, verbose=False)


# get object data type as string
def d_type(val):
    return type(val).__name__


# create/destroy drop shadow under window
def drop_shadow(win, show=True):
    if wx.Platform != '__WXMSW__':
        return

    hnd, CS_DROPSHADOW, GCL_STYLE = win.Handle, 0x00020000, -26  # constant defs, see 'winuser.h'

    sty = win32gui.GetClassLong(hnd, GCL_STYLE)
    if show:
        if sty & CS_DROPSHADOW == 0:
            win32api.SetClassLong(hnd, GCL_STYLE, sty | CS_DROPSHADOW)
    else:
        win32api.SetClassLong(hnd, GCL_STYLE, sty & ~CS_DROPSHADOW)


#@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, not used
#@@@@@@@@@@@@@@@@@@@@@@@@
# def _get_cfg():
#     return __main__.CFG


# def _get_lng():
#     return __main__.LNG
#@@@@@@@@@@@@@@@@@@@@@@@@


# character position under cursor
def get_char_pos(doc, close=True):
    # client cursor coordinates
    fnc = doc.CharPositionFromPointClose if close else doc.CharPositionFromPoint
    x, y = doc.ScreenToClient(wx.GetMousePosition())
    pos = fnc(x, y)
    return x, y, pos


#INFO, from list of integers, get number closest to a given value
#INFO, URL=https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
def get_closest_index(lst, num):
    """
    Assumes lst is sorted. Returns index of closest value to num.
    If two numbers are equally close, return index of the smallest number.
    """
    if not (pos := bisect_left(lst, num)):
        return pos
    if pos == len(lst):
        return pos - 1
    before, after = lst[pos - 1:pos + 1]
    return pos if num - before > after - num else pos - 1


#INFO, Icons (Design basics) - Win32 apps Icons
#INFO, URL=https://docs.microsoft.com/en-us/windows/win32/uxguide/vis-icons Windows
#INFO, Icon Size Guide
#INFO, URL=https://www.creativefreedom.co.uk/icon-designers-blog/windows-7-icon-sizes/
# create square icon bitmap from 'PyEmbeddedImage'
def get_icon(nam='app', siz=24):
    return scale_bitmap(PNG[nam].Bitmap, siz, siz)


def get_keypress(evt):
#NOTE, prevent circular dependency
    from conf.debug import me_

    cod = evt.KeyCode
    nam = COMMON_KEYS.get(cod, None)  # key name

    if not nam:
        if 'unicode' in wx.PlatformInfo:
            cod = evt.UnicodeKey
            if cod <= 127:
                cod = evt.KeyCode
            nam = chr(evt.UnicodeKey)
        elif cod < 256:
            if cod == 0:
                nam = 'NUL'
            elif cod < 27:
                nam = chr(ord('A') + cod - 1)
            else:
                nam = chr(cod)
        else:
            err = f'{me_("F")}: unknown key name for keycode [{cod}]'
            raise AssertionError(err)

    modifiers = ''
    for mod, lbl in {(evt.controlDown, 'Ctrl+'),
                     (evt.altDown,     'Alt+'),
                     (evt.shiftDown,   'Shift+'),
                     (evt.metaDown,    'Meta+')}:
        if mod:
            modifiers += lbl

    kpr_sct = ''
    if nam:
        kpr_sct = modifiers + nam

    return kpr_sct, nam, cod


# convert colour to hexadecimal '#rrggbb' representation
def hex_colour(dta):
    r, g, b = dta.Colour.Get(includeAlpha=False)
    return f'#{r:02X}{g:02X}{b:02X}'


# return if colour is dark or not
def is_dark(colour):
#INFO, Determine font color based on background color
#INFO, URL=https://stackoverflow.com/questions/1855884/determine-font-color-based-on-background-color
    # avg = (.299 * colour.Red() + .587 * colour.Green() + .114 * colour.Blue()) / 255
    # if avg < .5:
    avg = (colour.Red() + colour.Green() + colour.Blue()) / 3
    if avg < 127:
        return True
    return False


# return panel if visible
def is_shown(pnl):

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: see 'Application.FilterEvent'
#INFO, GOAL: to HIDE 'InfoBar' on ANY 1st KEYPRESS
    # if not glb.IBR:
    #     return False
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    sch = glb.SPL['SCH'].IsSplit()  # search panel
    spn = glb.SPL['SPN'].IsSplit()  # side panel
    ccx = glb.SPL['CCX'].IsSplit()  # code context
    rlr = glb.SPL['RLR'].IsSplit()  # ruler

    # search panel
    if pnl in 'SCH':
        return sch
    # search panel mode
    elif pnl in {'INC', 'FND', 'RPL', 'FIF', 'RES'}:
        return sch and glb.SCH.mode == pnl
    # side panel
    elif pnl in 'SPN':
        return spn
    # side panel tool
    elif pnl in SPT:
        return spn and glb.SPN.GetSelection() == SPT[pnl].idx
    # code context
    elif pnl in 'CCX':
        return ccx
    # ruler
    elif pnl in 'RLR':
        return rlr
    # infobar
    elif pnl in 'IBR':
        return glb.IBR.IsShown()
    else:
        # we should NEVER get here
        err = f'{glb.TLW.__class__.__name__}: unknown panel name [{pnl}]'
        raise AssertionError(err)
    return False


# checks if selected text matches a word
def is_word_at(doc, pos):
    if doc.Selections == 1 and doc.SelectedText:
        if doc.SelectionStart == doc.WordStartPosition(pos, True) and \
            doc.SelectionEnd == doc.WordEndPosition(pos, True):
            return True
    return False


#INFO, URL=https://wxpython.org/Phoenix/docs/html/MigrationGuide.html#makemodal
# used in 'list_open_files', 'splash', 'FilterBox', FindReplaceDialog'
def make_modal(window, modal=True):
    if modal and not hasattr(window, '_disabler'):
        window._disabler = wx.WindowDisabler()
    if not modal and hasattr(window, '_disabler'):
        del window._disabler


# message dialog box
def msg_box(prt, typ='INFO', msg='', extra=''):
#NOTE, prevent circular dependency
    from conf.debug import me_

    # style and caption
    if typ == 'HELP':
        sty = wx.HELP  # | wx.ICON_NONE
        cap = APP['Base'] + ' Help'
    elif typ == 'INFO':
        sty = wx.OK | wx.OK_DEFAULT | wx.ICON_INFORMATION
        cap = 'Information'
    elif typ == 'WARN':
        sty = wx.OK | wx.OK_DEFAULT | wx.ICON_EXCLAMATION
        cap = 'Warning'
    elif typ == 'WARN_ASK':
        sty = wx.YES_NO | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_EXCLAMATION
        cap = 'Warning'
    elif typ == 'ERROR':
        sty = wx.OK | wx.OK_DEFAULT | wx.ICON_ERROR
        cap = 'Error'
    else:
        # we should NEVER get here
        err = f'{me_("F")}: unknown message dialog box type [{typ}]'
        raise AssertionError(err)
    # append text to caption
    if extra:
        cap = f'{cap} ({extra})'

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    with wx.MessageDialog(prt, msg, cap, style=sty) as dlg:
#FIX, icon not shown
        set_icon(dlg)
        res = dlg.ShowModal()

#     from wx.lib.agw.genericmessagedialog import GenericMessageDialog

#     with GenericMessageDialog(glb.TLW, msg, cap, agwStyle=sty) as dlg:
#         # no dialog button bitmaps
#         _NO_BMP = wx.Bitmap(0, 0)
#         dlg.SetHelpBitmap(_NO_BMP)
#         dlg.SetOKBitmap(_NO_BMP)
#         # dlg.SetOKCancelBitmaps(_NO_BMP, _NO_BMP)
#         dlg.SetYesNoCancelBitmaps(_NO_BMP, _NO_BMP, _NO_BMP)
# #HACK, allow ESCAPE key via 'OnKeyDown' in 'wx.lib.agw.genericmessagedialog.py'
# #INFO, URL=https://bit.ly/3nMlvJm
#         dlg.Bind(wx.EVT_CHAR_HOOK, dlg.OnKeyDown)
#         res = dlg.ShowModal()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    return res


# stub: for unimplemented functionality
def not_implemented(evt, txt=None):
    if evt:
        obj = evt.EventObject
        if is_tlw(obj):
#NOTE, weird behaviour after 'Ctrl+Shift+U' followed by 'Ctrl+Shift+I'
            return
            # txt = obj.GetLabel()
        else:  # elif isinstance(obj, wx.Menu):
            txt = obj.GetLabel(evt.Id)

    DBG('NIM', 'NOIMP: [%s]' % txt)
    txt = '[%s] -> NOT implemented' % txt.replace('\t', ': ')
    # glb.SBR.set_text(txt, typ='WARN')
    glb.IBR.info_msg(txt, 'WARN')


# register global hotkey shortcut
def register_hotkey(tlw, hotkey):
    cmn_keys = swap_dict(COMMON_KEYS)
    mod_keys = swap_dict(MOD_KEYS)

    # split modifiers and keycode
    hot_lst = hotkey.split('+')
    mod, cod = hot_lst[0:-1], hot_lst[-1]

    # set modifier flags
    flg = wx.MOD_NONE
    for m in mod:
        flg |= mod_keys[m]

    # lookup keycode
    if cod in cmn_keys:
        cod = cmn_keys[cod]
    else:
        # if len(cod) == 1:  # avoid error for 1 item with >1 chars: 'Backspace'
            cod = ord(cod)
        # else:
        #     return

    return tlw.RegisterHotKey(1, flg, cod)


#INFO, repeat string to certain length
#INFO, URL=https://stackoverflow.com/questions/3391076/repeat-string-to-certain-length
# called without arguments results in: '-----'
def rs_(len_=5, str_='-'):
    return (len_ * str_)[:len_]


def scale_bitmap(bmp, w, h):
    qly = wx.IMAGE_QUALITY_HIGH
    return bmp.ConvertToImage().Scale(w, h, qly).ConvertToBitmap()


def set_font(obj, face=None, siz=None, bold=False, italic=False):
    fnt = obj.Font
    if face:
        fnt.SetFaceName(face)
    if siz:
        fnt.SetPointSize(siz)
    if bold:
        fnt.MakeBold()
    if italic:
        fnt.MakeItalic()
    obj.SetFont(fnt)


# set dialog icon
def set_icon(dlg, ico=None):
#NOTE, prevent circular dependency
    from conf.debug import me_

    DBG('GEN', f'{me_()}')
    if not ico:
        ico = APP['Icon']
    dlg.SetIcon(ico)
    dlg.SetBackgroundColour(glb.CFG['General']['DialogBackColour'])


# set menu item icon bitmap
def set_menu_item_icon(mni, knd, ico, icc, ics):
    try:
        # prepare size
        if not any(s in ico for s in ('16', '24', '32') if ico.endswith(s)):
            ico = f'{ico}_{ics}'
            bmp, img = PNG[ico].Bitmap, PNG[ico].Image
            bmp = img.Rescale(ics, ics, wx.IMAGE_QUALITY_BICUBIC).ConvertToBitmap()
        else:
            bmp, img = PNG[ico].Bitmap, PNG[ico].Image
        # checkable item
        if knd in {'CHECK', 'RADIO'}:
            # custom checkable item
            if icc:
                try:
                    dis_bmp = img.ConvertToGreyscale().ConvertToDisabled().ConvertToBitmap()
                except KeyError as e:
                    dis_bmp = wx.NullBitmap
                mni.SetBitmaps(bmp, dis_bmp)
            # system-defined
            else:
                mni.SetBitmaps(mni.Bitmap)
        # normal item
        elif ico != NO_ICO:
            mni.SetBitmap(bmp)
    except KeyError as e:
#NOTE, prevent circular dependency
        from conf.debug import me_
        DBG('MNU==0', f'{me_("M, F")}: not found: [{e.args[0]}]')
        img_siz = (ics, ics)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, size=img_siz)
        mni.SetBitmap(bmp)

# set menu item label with optional font style
def set_menu_item_label(mni, lbl):
    # auxiliary font
    if MNU_FNT_AUX:
        p, f, s, w, n = MNU_FNT_TYP
        mni.SetFont(wx.Font(p, f, s, w, faceName=n))

#FIX, create function 'set_font_style' in 'util.py'
    # label font
    fnt = mni.Font
    for key, sty in LBL_FNT_STYLES.items():
        if (tag := f'[[{key}]]') in lbl:
            lbl = lbl.replace(tag, TXT_NIL)
#FIX, needs better coding...
            cmd = f'fnt.Make{sty}()'
            try:
                exec(cmd)
            except AssertionError as e:
#NOTE, prevent circular dependency
                from conf.debug import me_
                print(err := f'{me_("F")}: no [{key}] font support for label [{lbl}]\n\t{e}')

    mni.SetItemLabel(lbl)
    mni.SetFont(fnt)


def splash(frm, timeout=0):
    bmp = PNG['splash_wide_rgba'].Bitmap

    sty = AS.AS_TIMEOUT if timeout else AS.AS_NOTIMEOUT
    sty += AS.AS_CENTER_ON_PARENT
    avs = AS.AdvancedSplash(frm, bitmap=bmp, timeout=timeout, agwStyle=sty)
    drop_shadow(avs)

    # make_modal(avs, True)

    # avs.SetText('SPyE')
    # avs.SetTextColour('DARK GRAY')
    # avs.SetTextFont(wx.Font(wx.FontInfo(77).Bold().Italic()))
    # avs.SetTextPosition((0, 78))

    # return avs


# swap dictionary 'key:val' to 'val:key' (inverse lookup)
def swap_dict(dict_):
    return {v:k for k, v in dict_.items()}


def welcome(frm):
    tip = RTT(f'Welcome to {APP["Base"]}', TXT_NIL)
    tip.SetBackgroundColour('#71B3E8', '#FFFFF0')
    tip.SetTipKind(wx.adv.TipKind_None)
    tip.SetTitleFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName='Comic Sans MS'))
    # tip.SetTimeout(millisecondsTimeout=glb.CFG['Splash']['DelayHide'] - 1750, millisecondsDelay=1250)
    tip.SetTimeout(millisecondsTimeout=glb.CFG['Splash']['DelayHide'], millisecondsDelay=5)
    tip.ShowFor(frm, wx.Rect(0, -360, *frm.ClientRect[2:]))


def widget_inspection_tool(shortcut='Ctrl+Alt+Shift+I'):
    sec = glb.CFG['WidgetInspectionTool']

    sct = sec['ShortCut'].upper()

    alt = bool('ALT+' in sct)
    cmd = bool('CTRL+' in sct)
    shift = bool('SHIFT+' in sct)

    cod = sct.split('+')[-1][0]

    # print(f'{shortcut=}, {alt=}, {cmd=}, {shift=}, {cod=}')

    glb.APP.InitInspection(alt=alt,
                           cmd=cmd,
                           shift=shift,
                           keyCode=ord(cod))

    if sec['ShowAtStartup']:
        wx.lib.inspection.InspectionTool().Show(
            selectObj=eval(f'glb.{sec["PreSelectObject"]}'),
            refreshTree=sec['RefreshWidgetTree'])


# return list of 'count' zeroes
def zero(count=0):
    return [0 for z in range(count)]


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: 'current doc' decorators START HERE
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def curdoc(fnc):
    """ Pass 'glb.DOC' (current document) as 'doc' into namespace of decorated class/function. """

    @functools.wraps(fnc)
    def decorator(*args, **kwargs):
        if not (doc := glb.DOC): return
        (_glb := fnc.__globals__).update(doc=doc)
        DBG('DEC==2', f'deco (1): {_glb["doc"]}')
        res = fnc(*args, **kwargs)
        DBG('DEC==2', f'deco (3): {_glb["doc"]}\n^^^^^^^^')
        return res

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    if 'doc' in inspect.signature(fnc).parameters:
        # print(f'  [curdoc] -> arg [doc] already defined in function signature: [ {fnc.__name__} ]')
        DBG('DEC==1', f'  [curdoc] -> arg [doc] already defined in function signature: [ {fnc.__name__} ]')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # raise TypeError('[doc] argument already defined', fnc.__name__)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    return decorator


def curdoc_class(decorator, exclude=None):
    """Iterate through all methods in a class and apply decorator."""

    if exclude is None:
        exclude = []

    def decorate(cls):
        for att in cls.__dict__:
            if callable(val := getattr(cls, att)) and att not in exclude:
                setattr(cls, att, decorator(val))
        return cls

    return decorate


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: 'current doc' decorators END HERE
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
