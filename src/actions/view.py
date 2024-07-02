#!/usr/bin/python

import msvcrt
import subprocess as SP

import wx
from wx import stc

from ._load import _load
from common.doc import update_margins
from common.util import (
    curdoc, curdoc_class, hex_colour, is_shown, msg_box, not_implemented, set_icon
)
from conf.debug import DBG, DEBUG, me_
from const.app import EXE
from const.editor import FOL_STY_NIL, FOL_STY_SQR, MGN
from const import glb
from const.menubar import MI
from const.sidepanel import SPT, SPT_NO_LCT


@_load
@curdoc_class(curdoc)
class View:

    def view_all_margins(self, evt):
#NOTE, margins are GLOBAL now
        sec = glb.CFG['Margin']
        num, sym, fol = sec['LineNumberWidth'], sec['SymbolWidth'], sec['FoldingWidth']
        tot = num + sym + fol
        items = (MI['MGN_NUM'], MI['MGN_SYM'], MI['MGN_FOL'])
        types = {MGN['NUM']: num, MGN['SYM']: sym, MGN['FOL']: fol}

        # process all margin menu items
        chk = evt.IsChecked()
        # same margins in all documents
        for __, doc_mgn in glb.NBK.open_docs():
            for mni in items:
                glb.MBR.Check(mni, bool(chk))
            for typ, wid in types.items():
                doc_mgn.SetMarginWidth(typ, wid if chk else 0)
        DBG('ZOO', f'num {num:3d}, sym {sym:3d}, fol {fol:3d}, tot {tot:3d}  (ruler offset: all margins)')
        # update ruler alignment
        glb.RLR.set_offset((tot if chk else 0) - doc.XOffset)

    def view_auto_scroll(self, evt):
        fnc = doc.LineScrollDown
        slp = 100  # default speed (ms)

        prv_slp = prv_txt = None

        while True:
            if DEBUG['SCL']:
                txt = 'down' if fnc == doc.LineScrollDown else 'up'
                if slp != prv_slp or txt != prv_txt:
                    print(f'{me_("F")}: scroll [{txt:4}], sleep [{slp:3} ms]')
                    prv_slp, prv_txt = slp, txt

            wx.MilliSleep(slp)
            fnc()
            doc.Update()
            doc.scroll(evt)  # force top line tooltip update
            _gks = wx.GetKeyState
            if _gks(wx.WXK_DOWN):
                fnc = doc.LineScrollDown
            elif _gks(wx.WXK_UP):
                fnc = doc.LineScrollUp
            elif _gks(wx.WXK_LEFT):
                slp = slp + 25 if slp < 300 else 300  # slower
            elif _gks(wx.WXK_RIGHT):
                slp = slp - 25 if slp > 0 else 0  # faster
            elif _gks(wx.WXK_SPACE):
                slp = 100  # default
            elif _gks(wx.WXK_CONTROL) and _gks(wx.WXK_ALT) and _gks(wx.WXK_SHIFT):
                break

#INFO, Keyboard input/Flush the keyboard buffer
#INFO, URL=https://rosettacode.org/wiki/Keyboard_input/Flush_the_keyboard_buffer#Python
            # when keys are pressed continuously, flush them for performance
            while msvcrt.kbhit():
                msvcrt.getch()

    def view_caret(self, evt):
        if (id_ := evt.Id) == MI['CRT_BRF']:
            ...
        elif id_ == MI['CRT_LIN']:
            doc.SetCaretLineVisible(bool(not doc.CaretLineVisible))
        elif id_ == MI['CRT_STK']:
            doc.SetCaretSticky(stc.STC_CARETSTICKY_OFF if doc.CaretSticky else stc.STC_CARETSTICKY_ON)

    def view_console_output(self, evt, lin=None):
        not_implemented(evt)

    def view_edge(self, evt):
        if (id_ := evt.Id) == MI['EDG_NON']:
            print('STC_EDGE_NONE')
            doc.SetEdgeMode(stc.STC_EDGE_NONE)
        elif id_ == MI['EDG_BCK']:
            print('STC_EDGE_BACKGROUND')
            doc.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        elif id_ == MI['EDG_LIN']:
            print('STC_EDGE_LINE')
            doc.SetEdgeMode(stc.STC_EDGE_LINE)
        elif id_ == MI['EDG_MUL']:
            print('STC_EDGE_MULTILINE (implement in wxPython 4.1)')
        #     doc.SetEdgeMode(stc.STC_EDGE_MULTILINE)
        #     doc.MultiEdgeClearAll()
        #     doc.MultiEdgeAddLine(10, CLR['RED'])
        #     doc.MultiEdgeAddLine(20, CLR['RED'])
        #     doc.MultiEdgeAddLine(30, CLR['RED'])
        #     doc.MultiEdgeAddLine(40, CLR['RED'])
        #     doc.MultiEdgeAddLine(50, CLR['RED'])
        #     doc.MultiEdgeAddLine(60, CLR['RED'])
        elif id_ == MI['EDG_COL']:
            with wx.TextEntryDialog(self, 'Enter number:', 'Edge column', str(doc.EdgeColumn + 1)) as dlg:
                set_icon(dlg)
                if (res := dlg.ShowModal()) == wx.ID_OK:
                    col = int(dlg.Value) - 1
                    doc.SetEdgeColumn(col)
        elif id_ == MI['EDG_CLR']:
            # current edge colour
            dta = wx.ColourData()
            dta.SetColour(wx.Colour(doc.EdgeColour))
            # pass to dialog
            with wx.ColourDialog(self, dta) as dlg:
                set_icon(dlg)
                dlg.ColourData.SetChooseFull(False)
                dlg.Centre()
                if (res := dlg.ShowModal()) == wx.ID_OK:
                    # selected colour
                    dta = dlg.ColourData
                    clr = hex_colour(dta)
                    # pass to edge
                    doc.SetEdgeColour(clr)

    def view_eol_chars(self, evt):
        # glb.MBR.Check(evt.Id, evt.IsChecked())
        doc.SetViewEOL(bool(not doc.ViewEOL))

    def view_folding_style(self, evt):
        if doc.fold_style < FOL_STY_SQR:
            doc.fold_style += 1
        else:
            doc.fold_style = FOL_STY_NIL
        doc.fold_styling()

    def view_indent_guides(self, evt):
        # glb.MBR.Check(evt.Id, evt.IsChecked())
        doc.SetIndentationGuides(stc.STC_IV_NONE if doc.IndentationGuides else stc.STC_IV_LOOKBOTH)

    def view_margin(self, evt):
#NOTE, margins are GLOBAL now
        if (id_ := evt.Id) == MI['MGN_NUM']:
            mgn = MGN['NUM']
            wid = glb.CFG['Margin']['LineNumberWidth']
        elif id_ == MI['MGN_SYM']:
            mgn = MGN['SYM']
            wid = glb.CFG['Margin']['SymbolWidth']
        elif id_ == MI['MGN_FOL']:
            mgn = MGN['FOL']
            wid = glb.CFG['Margin']['FoldingWidth']
        # glb.MBR.Check(id_, evt.IsChecked())
        # same margins in all documents
        for __, doc_mgn in glb.NBK.open_docs():
            doc_mgn.SetMarginWidth(mgn, 0 if doc_mgn.GetMarginWidth(mgn) != 0 else wid)
        update_margins()

    def view_on_top(self, evt):
        self.WindowStyle ^= wx.STAY_ON_TOP

    def view_read_only(self, evt):
        doc.SetReadOnly(bool(not doc.ReadOnly))
        glb.NBK.update_page_tab(doc)

    def view_scroll_bars(self, evt):
        id_ = evt.Id

        doc.SetUseHorizontalScrollBar(bool(id_ in [MI['SCL_BTH'], MI['SCL_HOR']]))
        doc.SetUseVerticalScrollBar(bool(id_ in [MI['SCL_BTH'], MI['SCL_VER']]))
#FIX, save settings to config, per doc/GLOBAL?
        glb.CFG['Editor']['HorizontalScrollBar'] = doc.GetUseHorizontalScrollBar()
        glb.CFG['Editor']['VerticalScrollBar'] = doc.GetUseVerticalScrollBar()

    def view_side_panel_tool(self, evt):
        # show filter box for active side panel tool
        if (id_ := evt.Id) == MI['SPT_FLT']:
            if not is_shown('SPN'):
                return
            sel = glb.SPN.GetSelection()
            sgl_ctl = glb.SPN.sgl_lst[sel]
            spt_ctl = glb.DOC.spt_lst[sel]

            # access via choice id
            for key, spt in SPT.items():
                if spt.idx == sel:
                    break

            print(f'  {me_("F")} (Filter List): {key = } ({sel})')

            # discard when no list
            if key in SPT_NO_LCT:
                return

            if (ctl := sgl_ctl if sgl_ctl else spt_ctl if spt_ctl else None):
                ctl.show_list_filter_box()
            return
        elif id_ == MI['SPT_DLF']:
            glb.SPN.clear_filter()
            return

        # open side panel when closed
        if not is_shown('SPN'):
            self.toggle_panel(evt, 'SPN', -1)
        glb.SPN.SetSelection(evt.Id - int(MI['SPT_DOC']))

    def view_statistics(self, evt):
#TODO, now only handles Python source code
        if doc.lng_typ != 'python':
            not_implemented(None, f'[{doc.lng_nam}] LANGUAGE STATISTICS')
            return
#TODO, create better output dialog w/ button for 'clipboard copy'
        wx.BeginBusyCursor()
        out = SP.check_output([f'{EXE["RADON"]}', 'raw', doc.pnm])
        wx.EndBusyCursor()
#NOTE, py3: decode 'out' data type: bytes -> str prevents error:
#NOTE,     'TypeError: can only concatenate str (not "bytes") to str'
        msg = f'\'{doc.fnm}\' statistics\n\n{out.decode("utf-8")}'
        msg_box(self, 'INFO', msg)

    def view_whitespace_chars(self, evt):
        # glb.MBR.Check(evt.Id, evt.IsChecked())
        doc.SetViewWhiteSpace(bool(not doc.ViewWhiteSpace))

    def view_word_wrap(self, evt):
        # glb.MBR.Check(evt.Id, evt.IsChecked())
        doc.SetWrapMode(stc.STC_WRAP_NONE if doc.WrapMode else stc.STC_WRAP_WORD)

    def view_zoom(self, evt):
        if (id_ := evt.Id) == MI['ZOO_RST']:
            doc.SetZoom(0)
        elif id_ == MI['ZOO_IN_']:
            doc.SetZoom(doc.Zoom + 1)
        elif id_ == MI['ZOO_OUT']:
            doc.SetZoom(doc.Zoom - 1)
