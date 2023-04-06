#!/usr/bin/python

import beeprint

import wx
from wx import stc

from ._load import _load
from common.doc import get_doc
from common.util import (
    CharValidator, is_shown, make_modal, me_, not_implemented, set_icon
)
from conf.debug import (
    DEBUG, dbg_EVENT, dbg_FILE, dbg_FOCUS, dbg_POSITION_HISTORY
)
from const.common import TXT_NIL
from const.editor import MRK
from const import glb
from const.menu import MI
from const.sidepanel import SPT
import gui
from tool.symbol import GotoAnything, SymbolBrowser


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#               REFACTOR METHOD NAMES
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CURRENT               FUTURE
# ----------------      ----------------------------
# do_brace_match    ->  do_brace_match
# GotoAnything      ->  GotoAnything
# GotoBookmark      ->  GotoBookmark
# goto_caret_pos    ->  goto_caret_pos
# GotoLine          ->  GotoLine
# GotoTask          ->  GotoTask
# jump_to_bookmark  ->  jump_to_bookmark
# list_open_files   ->  list_open_files
# symbol_browser    ->  symbol_browser
# toggle_bookmark   ->  toggle_bookmark
# toggle_task       ->  toggle_task [not_implemented]
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


@_load
class Goto:

    def clear_all_markers(self, evt):
        if not (doc := get_doc()): return
        doc.clear_bookmarks()
        doc.clear_breakpoints()
        doc.clear_task_markers()

    def clear_bookmarks(self, evt):
        if not (doc := get_doc()): return
        doc.clear_bookmarks()

    def clear_task_markers(self, evt):
        if not (doc := get_doc()): return
        doc.clear_task_markers()

    def do_brace_match(self, evt):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, braces: 3 functions:
#  1. highlight             caret/mouse cursor movement
#  2. match (inner/outer)   Ctrl-M
#  3. select (inner/outer)  Ctrl-Shift-M
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        def __highlight_both():
            pass

        def __jump_to_match():
            pass

        def __select_to_match():
            pass


        evt.Skip()
        if DEBUG['BRC']: print(f'{me_()}')
        if DEBUG['BRC'] > 1: dbg_EVENT(evt)
        if not (doc := get_doc()): return

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        doc.BraceHighlight(-1, -1)  # turn OFF

        doc.MarkerDeleteAll(MRK['BRL']['NUM'])
        doc.MarkerDeleteAll(MRK['BRR']['NUM'])
        # # test: markers used for braces
        # lin = doc.LineFromPosition(doc.CurrentPos)
        # doc.MarkerAdd(lin, MRK['BAB']['NUM'])
        # doc.MarkerAdd(lin+1, MRK['BAL']['NUM'])
        # doc.MarkerAdd(lin+2, MRK['BAR']['NUM'])

        # doc.MarkerAdd(lin+4, MRK['BCB']['NUM'])
        # doc.MarkerAdd(lin+5, MRK['BCL']['NUM'])
        # doc.MarkerAdd(lin+6, MRK['BCR']['NUM'])

        # doc.MarkerAdd(lin+8, MRK['BRB']['NUM'])
        # doc.MarkerAdd(lin+9, MRK['BRL']['NUM'])
        # doc.MarkerAdd(lin+10, MRK['BRR']['NUM'])

        # doc.MarkerAdd(lin+12, MRK['BSB']['NUM'])
        # doc.MarkerAdd(lin+13, MRK['BSL']['NUM'])
        # doc.MarkerAdd(lin+14, MRK['BSR']['NUM'])

        # doc.MarkerDeleteAll(MRK['BCB']['NUM'])
        # doc.MarkerDeleteAll(MRK['BCL']['NUM'])
        # doc.MarkerDeleteAll(MRK['BCR']['NUM'])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        res = False
        cur = doc.CurrentPos
        prs = glb.CFG['Brace']['Pairs']
        mid = len(prs) // 2  # distance between open/close brace

        # get char at left/right of current position
        rit = chr(doc.GetCharAt(cur))
        lft = chr(doc.GetCharAt(cur - 1)) if cur > 0 else rit

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # left/right outer/inner flags
        lto = lti = rto = rti = False

        if chr(doc.GetCharAt(cur - 1)) in prs[:mid]:
            lti = True
        elif chr(doc.GetCharAt(cur - 1)) in prs[mid:]:
            rto = True
        elif chr(doc.GetCharAt(cur)) in prs[:mid]:
            lto = True
        elif chr(doc.GetCharAt(cur)) in prs[mid:]:
            rti = True

        # print(f'{lto = !r:>5}  {lti = !r:>5}  {rti = !r:>5}  {rto = !r:>5}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # brace at left/right of current position?
        if cur > 0 and lft in prs:
            cur -= 1
        elif rit not in prs:
            cur = -1

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        sav = cur

        if cur < 0:
            pos = doc.FindText(doc.CurrentPos, 0, f'[{prs[:mid-2]}]', stc.STC_FIND_REGEXP)
            # print(pos)
            if pos == stc.STC_INVALID_POSITION:
                return
            # doc.GotoPos(pos)

            if (brc := doc.BraceMatch(pos)) != stc.STC_INVALID_POSITION:
                # print(chr(doc.GetCharAt(pos)), chr(doc.GetCharAt(brc)))
                # doc.SetSelection(pos, brc)
                doc.MarkerAdd(doc.LineFromPosition(pos), MRK['BRL']['NUM'])
                doc.MarkerAdd(doc.LineFromPosition(brc), MRK['BRR']['NUM'])

            cur = sav
            # return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # check for matching brace
        if cur >= 0:
            if (brc := doc.BraceMatch(cur)) != stc.STC_INVALID_POSITION:
#FIX, needs better coding...
                res = True
                tlb = 'ToolBar' in str(evt.EventObject)
                if evt.Id == MI['MCH_BRC'] or tlb:  # called from menu/Ctrl+M or toolbar
                    if rit in prs:
                        brc += 1                    # adjust for inner/outer match
                    doc.GotoPos(brc)                # ...jump to matching brace
                elif evt.Id == MI['SEL_BRC']:       # called from menu/Ctrl+Shift+M
                    if cur > brc:                   # ...create selection between braces
                        cur, brc = brc, cur
                    # if (cur + 1, brc) != doc.GetSelection():
                    doc.SetSelection(cur + 1, brc)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, expand brace selection with every Ctrl+Shift+M
                    # else:
                        # doc.SetSelection(cur, brc + 1)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # if lto: brc -= 1
                # if rti: brc -= 1
                doc.BraceHighlight(cur, brc)  # turn ON
                doc.SetHighlightGuide(doc.GetColumn(cur))
            else:
                doc.BraceBadLight(cur)
                glb.SB.push_text(f'No matching brace for [{doc.GetRange(cur, cur + 1)}]')
        else:
            doc.BraceHighlight(-1, -1)  # turn OFF
        return res

    def goto_anything(self, evt):
        if not (doc := get_doc()): return
        GotoAnything()

    def goto_bookmark(self, evt):
        if not (doc := get_doc()): return
        cur = doc.CurrentLine

        # force panel visibility
        if glb.CFG['Bookmark']['ShowPanel']:
            if not is_shown('SPN'):
                self.toggle_panel(evt, 'SPN', -1)
            if not is_shown('BMK'):
                glb.SPN.SetSelection(SPT.BMK.idx)

        if (id_ := evt.Id) == MI['BMK_NXT']:
            if DEBUG['BMK']: print('  Next bookmark')
            lin = doc.MarkerNext(cur + 1, MRK['BMK']['MSK'])
        elif id_ == MI['BMK_PRV']:
            if DEBUG['BMK']: print('  Previous bookmark')
            lin = doc.MarkerPrevious(cur - 1, MRK['BMK']['MSK'])

        if lin != stc.STC_INVALID_POSITION:
            doc.GotoLine(lin)
        elif glb.CFG['Bookmark']['SearchWrap']:
            if id_ == MI['BMK_NXT']:
                lin = doc.MarkerNext(0, MRK['BMK']['MSK'])
            elif id_ == MI['BMK_PRV']:
                lin = doc.MarkerPrevious(doc.LineCount, MRK['BMK']['MSK'])
            if lin != stc.STC_INVALID_POSITION:
                doc.GotoLine(lin)

        if lin != stc.STC_INVALID_POSITION:
            if glb.CFG['Bookmark']['CentreCaret']:
                doc.VerticalCentreCaret()
            # bookmark list control
            if (ctl := gui.get_spt('BMK')) and glb.CFG['Bookmark']['SyncPanel']:
                for idx in range(ctl.ItemCount):
                    if lin == int(ctl.GetItemText(idx, 2)) - 1:  # lineno
                        ctl.Select(idx)
                        ctl.Focus(idx)

        dbg_FOCUS(doc)

    def goto_caret_pos(self, evt):
        if not (doc := get_doc()): return
        # list of differing actions for prev/next functionality
        if (id_ := evt.Id) == MI['JMP_BCK']:
            dif = (doc.cph_idx > 0,                          -1, 'Prev', 'earliest')
        elif id_ == MI['JMP_FWD']:
            dif = (doc.cph_idx < len(doc.cph_cache_lst) - 1,  1, 'Next', 'newest')
        else:
            return

        doc.set_caret_style()
        if dif[0]:
            doc.cph_idx += dif[1]
            if DEBUG['CPH']: dbg_POSITION_HISTORY(doc)
            doc.GotoPos(doc.cph_cache_lst[doc.cph_idx])
            # doc.GotoPos(doc.cph_cache_lst[doc.cph_idx][0])
            # s, e = doc.cph_cache_lst[doc.cph_idx][1]
            # print(s, e)
            # if s != e:
            #     doc.SetSelection(s, e)
            doc.VerticalCentreCaret()
            glb.SB.set_text(f'{dif[2]} history index {doc.cph_idx + 1}')
        else:
            glb.SB.set_text(f'Already at {dif[3]} position ({doc.cph_idx})')

    def goto_line(self, evt):
        def __set_line():
            # set/select current line as default value
            lin = str(doc.LineFromPosition(pos) + 1)
            dlg.txc_lin.Value = lin
            dlg.txc_lin.SelectAll()

        def __on_char(evt):
            evt.Skip()
            # get line string
            if len(val := dlg.txc_lin.Value) > 10:
                dlg.txc_lin.Value = val[:10]
                dlg.txc_lin.SetInsertionPointEnd()
            elif val:
                # jump to line in background
                lin = int(val) - 1
                doc.GotoLine(lin)
            else:
                # restore caret position
                doc.GotoPos(pos)
                __set_line()
            doc.VerticalCentreCaret()

        def __on_confirm(evt):
            __on_exit(None)

        def __on_exit(evt):
            make_modal(dlg, False)
            dlg.Destroy()
            if evt:
                # restore caret position and selection
                doc.GotoPos(pos)
                doc.SetFirstVisibleLine(top)
                if spos != epos:
                    doc.SetSelection(spos, epos)
                # doc.VerticalCentreCaret()

        if not (doc := get_doc()): return

        sty = wx.CAPTION | wx.CLOSE_BOX
        dlg = wx.Dialog(self, title='Go to line', style=sty)
        set_icon(dlg)
        make_modal(dlg, True)

        dlg.stt_lin = wx.StaticText(dlg, wx.ID_ANY, 'Enter number:')
        dlg.txc_lin = wx.TextCtrl(dlg, wx.ID_ANY, TXT_NIL, size=(165, 25), validator=CharValidator('digit'))
        dlg.btn_ok_ = wx.Button(dlg, wx.ID_OK, '&OK', size=(75, 25))
        dlg.btn_can = wx.Button(dlg, wx.ID_CANCEL, '&Cancel', size=(75, 25))

        gbs = wx.GridBagSizer(vgap=5, hgap=5)
        border = 5
        gbs.Add(dlg.stt_lin, (0, 0), (1, 1), wx.ALIGN_CENTRE_VERTICAL | wx.ALL, border)
        gbs.Add(dlg.txc_lin, (0, 1), (1, 2), wx.ALIGN_CENTRE_VERTICAL | wx.ALL, border)
        gbs.Add(dlg.btn_ok_, (1, 1), (1, 1), wx.ALIGN_CENTRE_VERTICAL | wx.ALL, border)
        gbs.Add(dlg.btn_can, (1, 2), (1, 1), wx.ALIGN_CENTRE_VERTICAL | wx.ALL, border)

        dlg.txc_lin.Bind(wx.EVT_KEY_UP, __on_char)
        dlg.btn_ok_.Bind(wx.EVT_BUTTON, __on_confirm)
        dlg.btn_can.Bind(wx.EVT_BUTTON, __on_exit)
        dlg.Bind(wx.EVT_CLOSE, __on_exit)

        dlg.btn_ok_.SetDefault()
        dbg_FOCUS(dlg.txc_lin)

        # save caret position, first line and selection
        pos = doc.CurrentPos
        top = doc.FirstVisibleLine
        spos, epos = doc.GetSelection()

        __set_line()

        dlg.Sizer = gbs
        dlg.Sizer.Fit(dlg)
        dlg.Centre()
        dlg.Show()

    def goto_task(self, evt):
        if not (doc := get_doc()): return
        cur = doc.CurrentPos

        # force panel visibility
        if glb.CFG['Task']['ShowPanel']:
            if not is_shown('SPN'):
                self.toggle_panel(evt, 'SPN', -1)
            if not is_shown('TSK'):
                glb.SPN.SetSelection(SPT.TSK.idx)

#FIX, Scintilla REGEXP not efficient -> use 're.compile'
#INFO, URL=https://pythex.org
#INFO, URL=https://docs.python.org/library/re.html
#INFO, URL="D:\Dev\D\wx\TSN_SPyE\contrib\demo\demo_SearchSTC.py"
#NOTE, workaround: (TEMPORARY), for now using Scintilla REGEXP syntax

        # tsk = '^#(INFO|NOTE|TODO|FIX|DONE|HACK)'  # '|'.join(TSK_TAGS)
        # flg = stc.STC_FIND_MATCHCASE | stc.STC_FIND_REGEXP | stc.STC_FIND_CXX11REGEX

        tsk = '^#[INTDFH][NOOOIA][FTDNXC][OEOEK,]'  # '|'.join(TSK_TAGS)
        flg = stc.STC_FIND_MATCHCASE | stc.STC_FIND_REGEXP

        if (id_ := evt.Id) == MI['TSK_NXT']:
            if DEBUG['TSK']: print('  next')
            cur += 1
            max_pos = doc.LastPosition
        elif id_ == MI['TSK_PRV']:
            if DEBUG['TSK']: print('  previous')
            cur -= 1
            max_pos = 0

        pos = doc.FindText(cur, max_pos, tsk, flg)
        if pos == stc.STC_INVALID_POSITION:
            if glb.CFG['Task']['SearchWrap']:
                if id_ == MI['TSK_NXT']:
                    cur = 0
                    max_pos = doc.LastPosition
                    txt = 'TOP'
                elif id_ == MI['TSK_PRV']:
                    cur = doc.LastPosition
                    max_pos = 0
                    txt = 'BOTTOM'
                pos = doc.FindText(cur, max_pos, tsk, flg)
                if pos == stc.STC_INVALID_POSITION:
                    return
                else:
                    if DEBUG['TSK']: print(f'  wrapped to {txt}')
            else:
                if DEBUG['TSK']: print('  not found')
                return

        doc.GotoPos(pos)
        doc.SetSelection(pos, pos + 5)  # task tag search length: 5
        if glb.CFG['Task']['CentreCaret']:
            doc.VerticalCentreCaret()

        # task list control
        if (ctl := gui.get_spt('TSK')) and glb.CFG['Task']['SyncPanel']:
            lin = doc.CurrentLine
            for idx in range(ctl.ItemCount):
                if lin == int(ctl.GetItemText(idx, 3)) - 1:  # lineno
                    ctl.Select(idx)
                    ctl.Focus(idx)
        dbg_FOCUS(doc)

    def jump_to_bookmark(self, evt):
        if not (doc := get_doc()): return
        bmn = evt.Id - int(MI['BMK_JB1']) + 1

        # 10 'jump keys' supported
        if bmn not in range(1, 11):
            return

        bmk_lst = doc.get_bookmarks()

        # bookmark number not found
        if bmn > len(bmk_lst):
            return

        bmn = 9 if not bmn else bmn - 1  # 0-based list index
        lin = bmk_lst[bmn][1] - 1  # 0-based line number
        doc.GotoLine(lin)

        if DEBUG['BMK']: print(f'jump_to_bookmark: [{bmn:2d}]')

#INFO, URL=https://stackoverflow.com/questions/33783727/how-can-i-update-a-wxpython-listbox-based-on-some-search-string
    def list_open_files(self, evt):
        def __on_char(evt):
            evt.Skip()
            # get filter string
            val = dlg.txc_flt.Value
            # populate listbox
            dlg.lbx_ofl.Clear()
            for item in doc_lst:
                if val in item:
                    dlg.lbx_ofl.Append(item)
            dlg.SetTitle(f'Open File List - Filter: [{dlg.lbx_ofl.Count}]')

#TODO, implement fuzzy search
#INFO, see file 'symbol.py'
#INFO, see file 'D:\Dev\D\wx\TSN_SPyE\_SRCREF-TSN-Python-Editor\editor\fuzzy-py-master.zip'
        def __on_fuzzy(evt):
            dlg.fuzzy = bool(dlg.cbx_fuz.IsChecked())

        def __on_confirm(evt):
            dbg_FILE(f'key OK = [{wx.ID_OK}], ID = [{evt.Id}]')
            dbg_FILE(f'select item [{evt.Selection + 1}] = [{evt.String}]:')

            # get selected filename index
            if dlg.lbx_ofl.Selection != -1:
                # enter pressed or mouse double clicked
                if evt.Id == wx.ID_OK:
                    idx = doc_lst.index(dlg.lbx_ofl.GetString(dlg.lbx_ofl.Selection))
                else:
                    idx = doc_lst.index(evt.String)

                # select corresponding page tab
                glb.NBK.SetSelection(pag_lst[idx])

            __on_exit(None)

        def __on_exit(evt):
            make_modal(dlg, False)
            dlg.Destroy()
            # focus on selected or current document
            if not (doc := get_doc()): return
            dbg_FOCUS(doc)

        doc_lst = list()  # open documents
        pag_lst = list()  # page tab indices
        for pag, doc in glb.NBK.open_docs():
            fnm = doc.pnm
            doc_lst.append(fnm)
            pag_lst.append(pag)

        if glb.CFG['General']['OpenFileListSort']:
            doc_lst.sort()

        dbg_FILE(f'\nFile List (tab order):') ; beeprint.pp(list(enumerate(doc_lst, start=1)))
        dbg_FILE(f'\nFile List (name sort):') ; beeprint.pp(list(enumerate(sorted(doc_lst), start=1)))

        sty = wx.CAPTION | wx.CLOSE_BOX
        dlg = wx.Dialog(self, title='Open File List', style=sty)
        set_icon(dlg)
        make_modal(dlg, True)

        dlg.btn_ok_ = wx.Button(dlg, wx.ID_OK, '&OK', size=(75, 25))
        dlg.btn_can = wx.Button(dlg, wx.ID_CANCEL, '&Cancel', size=(75, 25))
        dlg.txc_flt = wx.TextCtrl(dlg, wx.ID_ANY, TXT_NIL, size=(250, 25))
        dlg.cbx_fuz = wx.CheckBox(dlg, wx.ID_ANY, '&Fuzzy Search', size=(250, 25))
        dlg.lbx_ofl = wx.ListBox(dlg, choices=doc_lst, size=(330, 250))

        gbs = wx.GridBagSizer(vgap=5, hgap=5)
        border = 10
        gbs.Add(dlg.btn_ok_, (0, 1), (1, 1), wx.TOP | wx.RIGHT, border)
        gbs.Add(dlg.btn_can, (1, 1), (1, 1), wx.RIGHT, border)
        gbs.Add(dlg.txc_flt, (0, 0), (1, 1), wx.TOP | wx.LEFT, border)
        gbs.Add(dlg.cbx_fuz, (1, 0), (1, 1), wx.LEFT, border)
        gbs.Add(dlg.lbx_ofl, (2, 0), (1, 2), wx.LEFT | wx.BOTTOM, border)

        dlg.btn_ok_.Bind(wx.EVT_BUTTON, __on_confirm)
        dlg.btn_can.Bind(wx.EVT_BUTTON, __on_exit)
        dlg.txc_flt.Bind(wx.EVT_KEY_UP, __on_char)
        dlg.cbx_fuz.Bind(wx.EVT_CHECKBOX, __on_fuzzy)
        dlg.lbx_ofl.Bind(wx.EVT_LISTBOX_DCLICK, __on_confirm)
        dlg.Bind(wx.EVT_CLOSE, __on_exit)

        dlg.btn_ok_.SetDefault()
        dbg_FOCUS(dlg.txc_flt)

        dlg.Sizer = gbs
        dlg.Sizer.Fit(dlg)
        dlg.Centre()
        dlg.Show()

    def symbol_browser(self, evt):
        if not (doc := get_doc()): return
        SymbolBrowser()

    def toggle_bookmark(self, evt, lin=None):
        if not (doc := get_doc()): return
        lin = doc.CurrentLine if lin is None else lin

        # force bookmark list control creation
        if not (gui.get_spt('BMK') and is_shown('BMK')):
            glb.SPN.SetSelection(SPT.BMK.idx)

        # update doc map panel/control
        # if (ctl := gui.get_spt('DCM')):
        #     ctl.Refresh()  # force 'doc map' update

        msk = doc.MarkerGet(lin)
        if DEBUG['BMK']: print(msk)

        if msk & MRK['BMK']['MSK']:
            doc.MarkerDelete(lin, MRK['BMK']['NUM'])
        else:
            doc.MarkerAdd(lin, MRK['BMK']['NUM'])

        # UPDATE bookmark list control
        (ctl := gui.get_spt('BMK')).update_list(doc)

    def toggle_task(self, evt, lin=None):
        not_implemented(evt)
