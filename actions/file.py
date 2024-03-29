#!/usr/bin/python

import os
from pathlib import Path

import requests
import wx
import wx.aui as aui
from wx import stc

from ._load import _load
from common.doc import get_doc
from common.file import is_open_file, open_files, split_path
from common.path import cwd
from common.util import (
    create_symbol_index, me_, msg_box, not_implemented,
    QuickOpenDialog, set_icon, zero
)
from conf.config import noit
from conf.debug import (
    DEBUG, dbg_BOOKMARK, dbg_BREAKPOINT, dbg_FILE, dbg_FILE_HISTORY,
    dbg_FOCUS, dbg_MODEVTMASK, dbg_TIMER, dbg_TRACEFUNC, dbg_whoami
)
from const.app import APP, APP_EXIT_FAST
from const.common import DELAY, TXT_NIL
from const.editor import CHARS, CR, CRLF, FOL_STYLE, LF, MGN, URI_SCHEMES
from const import glb
from const.lang import LANG, LANG_WILDCARDS
from const.menu import MI
from const.sidepanel import SPT
from const.statusbar import SBF
from data.images import catalog as PNG
import gui


@_load
class File:

#TODO, move 3 [File.*History] methods to gui.py

    def file_append_file(self, evt):
        if not (doc := get_doc()): return
        dbg_FILE('IN')

        sty = wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_PREVIEW | wx.FD_FILE_MUST_EXIST
        with wx.FileDialog(self, 'Append File', cwd(), '', LANG_WILDCARDS, sty) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                dbg_FILE(f'    Cancel:[{doc.pnm}]')
            else:
                pnm = dlg.Path
                dbg_FILE(f'        OK:[{pnm}]')
                with open(pnm, 'r') as fil:
                    txt = fil.read().replace(LF, CRLF)
                doc.DocumentEnd()
                doc.NewLine()
                doc.WriteText(txt)
                glb.SB.set_text(f'File [{pnm}] appended')

        dbg_FILE('OUT')

    def file_change_directory(self, evt):
        dbg_FILE('IN')
        sty = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR
        with wx.DirDialog(self, 'Change Directory', cwd(), sty) as dlg:
            txt = TXT_NIL if dlg.ShowModal() == wx.ID_OK else ' (unchanged)'
            txt = f'CD{txt} = [{dlg.Path}]'
            glb.SB.set_text(txt)
        dbg_FILE('OUT')

    def file_change_to_file_directory(self, evt):
        if not (doc := get_doc()): return
        dbg_FILE('IN')
        os.chdir(doc.dnm)
        txt = f'CD = [{cwd()}]'
        glb.SB.set_text(txt)
        dbg_FILE('OUT')

    def file_clear_history(self, evt):
        cnt = glb.MB.rfh_cache.Count
        for __ in range(cnt):
            glb.MB.rfh_cache.RemoveFileFromHistory(0)
        glb.SB.push_text(f'Cleared {cnt} recent file history items')

    def file_close(self, evt, pag_cls_called=False):
        if not (doc := get_doc()): return
        cur = glb.NBK.Selection

#DONE, check for macro recording
        if doc.mac_rec_active:
            msg = f'{doc.fnm}\n\nStop currently active macro recording?'
#FIX, Yes/No/Cancel dialog unclear
            if msg_box(self, 'WARN_ASK', msg) in [wx.ID_NO, wx.ID_CANCEL]:  # keep in editor
                return False
            doc.macro_stop(None)
        if doc.IsModified():
#NOTE, file_close starts 'modified' dialog
            msg = f'{doc.fnm} has been modified, save changes?'
            if not doc.dnm:
                msg = f'New file {msg}'
            if (res := msg_box(self, 'WARN_ASK', msg)) == wx.ID_YES:
                if doc.dnm:        # save (as) and close
                    self.file_save(evt)
                else:
                    self.file_save_as(evt)
            elif res == wx.ID_NO:      # discard and close
                pass
            elif res == wx.ID_CANCEL:  # keep in editor
                return False

        # destroy this document's side panel tools
        #@@@@@@@@@@@@@@@@@@@@@@@@@
        # print('\n', doc.pnm)
        # pprint(doc.spt_lst)
        #@@@@@@@@@@@@@@@@@@@@@@@@@
        for ctl in doc.spt_lst:
            #@@@@@@@@@@@
            # print(ctl)
            #@@@@@@@@@@@
            if ctl:
                ctl.Destroy()

        if not self.xit_active:
            if glb.RFH['RecentFileHistory']['Enable']:
                # skip new/unsaved file
                if doc.dnm:
                    glb.MB.rfh_cache.AddFileToHistory(doc.pnm)
                    if DEBUG['RFH']: dbg_FILE_HISTORY(glb.MB.rfh_cache)

#HACK: 'aui PAGE_CLOSE' event ONLY fires when page close button is clicked
#NOTE,        it does NOT fire when Ctrl-W shortcut is pressed, so FORCE call to page_close
        if not pag_cls_called:
            aui_evt = aui.AuiNotebookEvent(aui.wxEVT_AUINOTEBOOK_PAGE_CLOSE)
            glb.NBK.page_close(aui_evt, fil_cls_called=True)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, APP CRASH on 'Ctrl-W (close), 'use '__del__' magic method in 'Editor' ?
#NOTE, avoid error AttributeError: 'NoneType' object has no attribute 'Destroy'
        # # if doc.glc_obj:
        # #     print(doc.glc_obj.stc_pvw.fnm)
        # #     doc.glc_obj.Destroy()  # 'glance view'
        # try:
        #     if doc.glc_obj:
        #         doc.glc_obj.Destroy()  # 'glance view'
        # except AttributeError as e:
        #     print(f'obj [glance]: [{sys.exc_info()[0]}: {e}] [{doc.fnm}]')
        #     pass
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, APP CRASH on 'Ctrl-W (close), ALSO when using 'x' in page tab
#NOTE, hard to reproduce consistently
# # #   USE:
# #         wx.CallAfter(glb.NBK.RemovePage, cur)
# #         # doc.DestroyLater()
# #         wx.CallLater(5000, doc.DestroyLater)
# # #    OR:
# #         del doc
# #         glb.NBK.DeletePage(cur)

#         import traceback

#         try:
#             del doc
#             glb.NBK.DeletePage(cur)
#         except Exception(err):
#             try:
#                 raise TypeError("Again !?!")
#             except:
#                 pass

#             traceback.print_exc()

        del doc
        glb.NBK.DeletePage(cur)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        # when no document open
        if not glb.NBK.PageCount:
            if glb.CFG['General']['NewFileAtCloseLast']:
                self.file_new(None)
                # update document list control
                if (ctl := glb.SPN.sgl_lst[SPT.DOC.idx]):
                    ctl.update_list(glb.NBK.CurrentPage)
                return True
            # clear main caption and statusbar fields, close any open panels
            self.SetTitle(APP['Base'])
#             glb.CCX.ctl.SetLabel(TXT_NIL)
            for pnl in glb.SPL:
                glb.SPL[pnl].unsplit_windows()

            # discard these actions when called from 'file_exit'
            if not self.xit_active:
                for id_ in ['LAY_SCH', 'LAY_RLR', 'LAY_SPN', 'LAY_CCX']:
                    glb.MB.Check(MI[id_], False)
                for fld in SBF:
                    glb.SB.set_text(TXT_NIL, fld)

        return True

    def file_close_all(self, evt):
        dbg_TIMER('close')

        self.Freeze()

        is_chk = glb.MB.IsChecked
        res = True
        pag_cnt = 0

        # # convenient short naming (sections)
        # sec_sch = glb.CFG['SearchPanel']
        # sec_rlr = glb.CFG['Ruler']
        # sec_spn = glb.CFG['SidePanel']
        # sec_ccx = glb.CFG['CodeContext']
        # sec_pth = glb.CFG['PageTabHistory']

        # update some config before its data is lost closing all files
        glb.CFG['SearchPanel']['Enable'] = is_chk(MI['LAY_SCH'])
        if glb.CFG['SearchPanel']['Enable']:
            glb.CFG['SearchPanel']['Swap'] = glb.SPL['SCH'].swap
            glb.CFG['SearchPanel']['SashPos'] = glb.SPL['SCH'].SashPosition

        sch = glb.SCH

        glb.CFG['SearchPanel']['Mode'] = sch.mode
        focus = any(f for f in (sch.txc_fnd, sch.txc_whr, sch.txc_rpl, sch.txc_inc) if f.HasFocus())
        glb.CFG['SearchPanel']['HasFocus'] = focus
        glb.CFG['SearchPanel']['FindText'] = sch.txc_fnd.Value
        glb.CFG['SearchPanel']['WhereText'] = sch.txc_whr.Value
        glb.CFG['SearchPanel']['ReplaceText'] = sch.txc_rpl.Value
        # glb.CFG['SearchPanel']['IncrementalText'] = self.txc_inc  # [NOT IMPLEMENTED]
        glb.CFG['SearchPanel']['CaseSensitive'] = sch.cbx_cas.Value
        glb.CFG['SearchPanel']['RegularExpression'] = sch.cbx_reg.Value
        glb.CFG['SearchPanel']['WholeWord'] = sch.cbx_wrd.Value
        glb.CFG['SearchPanel']['WrapAround'] = sch.cbx_wrp.Value
        glb.CFG['SearchPanel']['InSelection'] = sch.cbx_isl.Value
        glb.CFG['SearchPanel']['HighlightMatches'] = sch.cbx_hlm.Value
        glb.CFG['SearchPanel']['PreserveCase'] = sch.cbx_pcs.Value
        glb.CFG['SearchPanel']['ShowContext'] = sch.cbx_cxt.Value
        glb.CFG['SearchPanel']['UseBuffer'] = sch.cbx_buf.Value

        glb.CFG['Ruler']['Enable'] = is_chk(MI['LAY_RLR'])
        if glb.CFG['Ruler']['Enable']:
            glb.CFG['Ruler']['Swap'] = glb.SPL['RLR'].swap
            glb.CFG['Ruler']['SashPos'] = glb.SPL['RLR'].SashPosition

        glb.CFG['SidePanel']['Enable'] = is_chk(MI['LAY_SPN'])
        # glb.CFG['SidePanel']['Choice'] = SPT.DOC.idx
        if glb.CFG['SidePanel']['Enable']:
            glb.CFG['SidePanel']['Swap'] = glb.SPL['SPN'].swap
            glb.CFG['SidePanel']['SashPos'] = glb.SPL['SPN'].SashPosition
            glb.CFG['SidePanel']['Choice'] = glb.SPN.GetSelection()

        # save side panel tool filter definitions
        for pag, doc in glb.NBK.open_docs():
            for spt in SPT.values():
                if spt.lbl in glb.CFG['Filter'].keys():
                    glb.CFG['Filter'][spt.lbl] = glb.SPN.flt_dct[spt.lbl]

        glb.CFG['CodeContext']['Enable'] = is_chk(MI['LAY_CCX'])
        if glb.CFG['CodeContext']['Enable']:
            glb.CFG['CodeContext']['Swap'] = glb.SPL['CCX'].swap
            glb.CFG['CodeContext']['SashPos'] = glb.SPL['CCX'].SashPosition

        if glb.CFG['PageTabHistory']['Enable']:
            pth_stk_lst = list(glb.NBK.pth_cache)  # current page tab history stack
            out_stk_lst = list()  # build new stack, excluding new/unsaved files

        cur = glb.NBK.CurrentPage
        glb.SSN['Session'] = {}
        glb.SSN['Session']['ActiveFile'] = cur.pnm if cur else ''

        opn_cnt = 0  # all open files
        new_cnt = 0  # new/unsaved files

#DONE, change 'i' by 'pag'?
        for pag in range(glb.NBK.PageCount):
            glb.NBK.SetSelection(pag_cnt)
            doc = glb.NBK.GetPage(pag_cnt)
            glb.CFG['Editor']['ZoomLevel'] = doc.Zoom

            # skip new/unsaved file
            if not doc.dnm:
                new_cnt += 1
            else:
                if glb.CFG['PageTabHistory']['Enable']:
                    out_stk_lst.append(pth_stk_lst[pag - new_cnt])
                pnm = doc.pnm
                vis = str(doc.FirstVisibleLine + 1)
                pos = str(doc.CurrentPos)
                lin = str(doc.CurrentLine + 1)
                col = str(doc.GetColumn(doc.CurrentPos) + 1)
                lng = doc.lng_typ
                wrp = str(doc.WrapMode)
                eol = str(1 if doc.ViewEOL else 0)
                wsp = str(doc.ViewWhiteSpace)
                tbu = str(1 if doc.UseTabs else 0)
                tbw = str(doc.TabWidth)
                ofs = str(doc.XOffset)
                sel_str = str(doc.GetSelection())  # tuple -> string
                bmk_lst = doc.get_bookmarks()
                bmk_str = str(bmk_lst)  # list -> string
                dbg_BOOKMARK('SAVE', doc, bmk_lst)
                bpt_lst = doc.get_breakpoints()
                bpt_str = str(bpt_lst)  # list -> string
                dbg_BREAKPOINT('SAVE', doc, bpt_lst)
                val = '|'.join([pnm, vis, pos, lin, col, lng, wrp, eol, wsp, tbu, tbw, ofs, sel_str, bmk_str, bpt_str])
                glb.SSN['Session']['File' + str(opn_cnt)] = val
                opn_cnt += 1

            if not self.file_close(evt):
                pag_cnt += 1  # keep in editor, next page tab
                res = False
                # break  # cancel button quits close

        if glb.CFG['PageTabHistory']['Enable']:
            # make list 0-based
            out_stk_lst = [i - min(out_stk_lst) for i in out_stk_lst]
            glb.CFG['PageTabHistory']['Stack'] = [out_stk_lst]

#TODO, update many more cfg sections/keys below!
        if glb.CFG['General']['FlushClipboard']:
            wx.TheClipboard.Flush()

#FIX, use 'update_margins' to derive 'All' value
#         self.update_margins()
#         glb.CFG['Margin']['All'] = is_chk(MI['MGN_ALL'])
        glb.CFG['Margin']['LineNumber'] = is_chk(MI['MGN_NUM'])
        glb.CFG['Margin']['Symbol'] = is_chk(MI['MGN_SYM'])
        glb.CFG['Margin']['Folding'] = is_chk(MI['MGN_FOL'])
#TODO, add fold_style to 3 docstate methods, FOR NOW it is GLOBAL
        glb.CFG['Margin']['FoldingStyle'] = FOL_STYLE

        if is_chk(MI['EDG_NON']):
            glb.CFG['Edge']['Mode'] = stc.STC_EDGE_NONE
        elif is_chk(MI['EDG_BCK']):
            glb.CFG['Edge']['Mode'] = stc.STC_EDGE_BACKGROUND
        elif is_chk(MI['EDG_LIN']):
            glb.CFG['Edge']['Mode'] = stc.STC_EDGE_LINE
        # elif is_chk(MI['EDG_MUL']):
        #     # glb.CFG['Edge']['Mode'] = stc.STC_EDGE_MULTILINE
        #     glb.CFG['Edge']['Mode'] = 3
        # glb.CFG['Edge']['Column'] = doc.EdgeColumn
        # glb.CFG['Edge']['Colour'] = doc.EdgeColour

        if is_chk(MI['IND_GDS']):
            glb.CFG['Indentation']['Guides'] = stc.STC_IV_LOOKBOTH
        else:
            glb.CFG['Indentation']['Guides'] = stc.STC_IV_NONE

        glb.CFG['Caret']['HomeEndKeysBRIEF'] = is_chk(MI['CRT_BRF'])
        glb.CFG['Caret']['LineVisible'] = is_chk(MI['CRT_LIN'])

        if is_chk(MI['CRT_STK']):
            glb.CFG['Caret']['Sticky'] = stc.STC_CARETSTICKY_ON
        else:
            glb.CFG['Caret']['Sticky'] = stc.STC_CARETSTICKY_OFF

        glb.CFG['Window']['OnTop'] = is_chk(MI['WIN_TOP'])

#         glb.CFG['Macro'][''] =

        glb.CFG['Layout']['Caption'] = is_chk(MI['LAY_CAP'])
        glb.CFG['Layout']['MenuBar'] = is_chk(MI['LAY_MBR'])
        glb.CFG['Layout']['ToolBar'] = is_chk(MI['LAY_TBR'])
        glb.CFG['Layout']['InfoBar'] = is_chk(MI['LAY_IBR'])
        glb.CFG['Layout']['StatusBar'] = is_chk(MI['LAY_SBR'])

        glb.CFG['Layout']['MenuIcons'] = glb.MB.ico
        glb.CFG['Layout']['MenuIconsCustomCheckable'] = glb.MB.icc
        glb.CFG['Layout']['MenuHelpText'] = glb.MB.hlp

        glb.CFG['Layout']['PageTabs'] = is_chk(MI['LAY_PTB'])
        glb.CFG['Layout']['PageTabTheme'] = is_chk(MI['LAY_PTT'])
        glb.CFG['Layout']['PageTabIcons'] = is_chk(MI['LAY_PTI'])

        glb.CFG['Layout']['ToolTips'] = is_chk(MI['LAY_TTP'])
        glb.CFG['AutoComplete']['Enable'] = is_chk(MI['LAY_ACP'])
        glb.CFG['CallTip']['Enable'] = is_chk(MI['LAY_CTP'])
        glb.CFG['TopLineToolTip']['Enable'] = is_chk(MI['LAY_TLT'])
        glb.CFG['ColourToolTip']['Enable'] = is_chk(MI['LAY_CTT'])
        glb.CFG['SymbolPopup']['Enable'] = is_chk(MI['LAY_SPU'])

        glb.CFG['Layout']['FullScreen'] = is_chk(MI['LAY_FUL'])
        glb.CFG['Layout']['DistractionFree'] = not glb.MB.IsEnabled(MI['LAY_FUL'])

        # glb.CFG['PanelEffect']['Enable'] =

        glb.RFH['RecentFiles'] = {}

        if glb.RFH['RecentFileHistory']['Enable']:
            for i in range(glb.MB.rfh_cache.Count):
                glb.RFH['RecentFiles']['File' + str(i)] = glb.MB.rfh_cache.GetHistoryFile(i)

        # window position, width, height
        glb.CFG['Window']['PositionX'] = self.Position[0]
        glb.CFG['Window']['PositionY'] = self.Position[1]
        glb.CFG['Window']['Width'] = self.Size[0]
        glb.CFG['Window']['Height'] = self.Size[1]

        # save config, recent file history, session
        glb.CFG.write()
        glb.RFH.write()
        glb.SSN.write()

        self.Thaw()

        dbg_TIMER('close', 'STOP')
        return res

    def file_close_left_or_right(self, evt):
        id_ = evt.Id
        if DEBUG['GEN']: print('  Left' if id_ == MI['NBK_CAL'] else '  Right')
        res = True  # not used
        cur = glb.NBK.Selection
        pag = 0 if id_ == MI['NBK_CAL'] else cur + 1
        rng_lst = list(range(cur)) if id_ == MI['NBK_CAL'] else list(range(cur + 1, glb.NBK.PageCount))
        cnt = 0

        for __ in rng_lst:
            glb.NBK.SetSelection(pag)
            if not self.file_close(evt):
                res = False  # not used
            else:
                cnt += 1

        if cnt > 0:
            glb.SB.push_text(f'Closed {cnt} documents')

        return cnt

    def file_close_other(self, evt):
        cnt = 0
        for id_ in ['NBK_CAL', 'NBK_CAR']:
            evt.SetId(MI[id_])
            cnt += self.file_close_left_or_right(evt)
        glb.SB.push_text(f'Closed {cnt} documents')

    def file_exit(self, evt):
        import sys
#FIX, trace python crash in wx versions >= 4.1
        # sys.settrace(dbg_TRACEFUNC)
        dbg_TIMER('exit')
        self.xit_active = True
        res = False
        if not APP_EXIT_FAST:
            res = self.file_close_all(evt)
        noit()
        if res or APP_EXIT_FAST:
            self.Destroy()
            if glb.CFG['General']['SystemTrayMenu']:
                glb.STM.Destroy()
        dbg_TIMER('exit', 'STOP')

    def file_insert_file(self, evt):
        if not (doc := get_doc()): return
        dbg_FILE('IN')

        sty = wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_PREVIEW | wx.FD_FILE_MUST_EXIST
        with wx.FileDialog(self, 'Insert File', cwd(), '', LANG_WILDCARDS, sty) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                dbg_FILE(f'    Cancel:[{doc.pnm}]')
            else:
                pnm = dlg.Path
                dbg_FILE(f'        OK:[{pnm}]')
                with open(pnm, 'r') as fil:
                    txt = fil.read().replace(LF, CRLF)
                doc.WriteText(txt)
                glb.SB.set_text(f'File [{pnm}] inserted')

        dbg_FILE('OUT')

    def file_new(self, evt):
        if DEBUG['STK']: print(dbg_whoami())
        dbg_FILE('IN')
        self.fil_num += 1
        dnm = ''
        pfx = glb.CFG['General']['NewFilePrefix']
        fnm = pfx + str(self.fil_num)
        fbs = ''
        ext = ''
        dbg_FILE(f'    [{fnm}]')

        self.Freeze()

        doc = gui.Editor(glb.NBK, [dnm, fnm, fbs, ext])

        # get language based on menu selection or set to plain text
        if glb.CFG['Language']['NewFile'] == 'CURRENT':
            lng_lst = [m for m in LANG if glb.MB.IsChecked(m[4])]
        else:
            lng_lst = [LANG[-1]]
        doc.update_language_styling(lng_lst)
        glb.NBK.update_page_tab(doc, newtab=True)

#         multi = sash.MultiSash(glb.NBK.CurrentPage, wx.ID_ANY, pos=(0,0), size=doc.ClientSize)
#         multi.SetDefaultChildClass(Editor)

        self.Thaw()

        glb.NBK.make_tab_visible()

        if DEBUG['SME']: dbg_MODEVTMASK(doc)
        dbg_FILE('OUT')

    def file_open(self, evt):
        dbg_FILE('IN')

        sty = wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_PREVIEW | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        with wx.FileDialog(self, 'Open', cwd(), '', LANG_WILDCARDS, sty) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                dbg_FILE('    Cancel')
                return
            dbg_TIMER('open')
            fil_lst = [[fnm] for fnm in dlg.Paths]
            open_files(fil_lst)
            dbg_TIMER('open', 'STOP')

        dbg_FILE('OUT')

    def file_open_from_history(self, evt):
        fid = evt.Id - wx.ID_FILE1
        fnm = glb.MB.rfh_cache.GetHistoryFile(fid)
        glb.MB.rfh_cache.AddFileToHistory(fnm)  # move up the list
        fil_lst = [[fnm]]
        open_files(fil_lst)
        fbs = Path(fnm).name
        glb.SB.push_text(f'Opening file [{fbs}] from recent file history')

#DONE, open file or URL at caret
#INFO, URL=https://gist.github.com/jbjornson/1186126
#INFO, URL=https://stackoverflow.com/questions/1547899/which-characters-make-a-url-invalid/1547940#1547940
#INFO, How to check if a string is a URL in Python and exists on the internet
#INFO, URL=https://www.kite.com/python/answers/how-to-check-if-a-string-is-a-url-in-python
    def file_open_at_caret(self, evt, src='EDT', dsc=None):
        if not (doc := get_doc()): return

        if dsc:
            txt = dsc  # description from task panel item
            if (idx := txt.find(Path(txt).name)) == -1:
                idx = txt.find('://')
        else:
            lin = doc.LineFromPosition(doc.CurrentPos)
            txt = doc.GetLineText(lin)
            idx = doc.CurrentPos - doc.PositionFromLine(lin)

        is_url = txt.find('://') >= 0
        sel_txt = doc.SelectedText

        if DEBUG['OAC']: print('  ------')
        if DEBUG['OAC']: print('  Select' if sel_txt else '  Parse')
        if DEBUG['OAC']: print(f'1. {src=}')

        # called from generated context menu item: editor (0)
        if src in 'EDT':
            # with selection
            if sel_txt:
                if DEBUG['OAC']: print(f'  2. with selection [{sel_txt}]')
                if CRLF in sel_txt:
                    if DEBUG['OAC']: print('  SKIP : multiple lines selected')
                    if DEBUG['OAC']: print('    3. multiple lines selected')
                    return
                if is_url:
                    if not any(sel_txt.startswith(scm) for scm in URI_SCHEMES):
                        if DEBUG['OAC']: print('    3. Not a valid URI scheme at start of selection')
                        return
                lin, pos = sel_txt, idx
            # no selection
            else:
                if DEBUG['OAC']: print(f'  2. without selection [{sel_txt}]')
                lin, pos = doc.CurLine
        # called from generated context menu item: task panel (1)
        else:
            lin, pos = txt, idx

        # remove leading/trailing whitespace
        lin = lin.strip()

        if DEBUG['OAC']: (bla1, bla2) = ('    ', 'X')
        if DEBUG['OAC']: print(f'{bla1}{bla2}. [{pos=}] [{lin=}]')

        if is_url:
            # parse line for valid URI scheme
            idx = -1
            for scm in URI_SCHEMES:
                if scm in lin:
                    idx = lin.find(scm)
                    break

            if DEBUG['OAC']: txt = scm if idx != -1 else 'NOT found'
            if DEBUG['OAC']: print(f'  URI scheme: [{txt}]')

            # scheme not found OR caret before URI scheme?
            if idx == -1 or pos < idx:
                return

        # parse filename or URL in current line
        lft = lin[:pos]
        rit = lin[pos:]

        if DEBUG['OAC']: print(f'  line : [{lin}]')
        if DEBUG['OAC']: print(f'  pos  : [{pos}]\n  idx  : [{idx}]')
        if DEBUG['OAC']: print(f'  left : [{lft}]\n  right: [{rit}]')

        # walk left until invalid OR at 1st pos of URI scheme
        txt = TXT_NIL
        for c in reversed(lft):
            if is_url:
                if DEBUG['OAC'] > 1: print(f'    txt: [{txt}]')
                # at 1st pos of URI scheme?
                if len(txt) == pos - idx:
                    if DEBUG['OAC']: print(f'  SKIP : at 1st pos of URI scheme [{scm}]')
                    break
            if (is_url and c not in CHARS['URL']) or c not in CHARS['FNM']:
                break
            txt = c + txt
        lft = txt

        # walk right until invalid
        txt = TXT_NIL
        for c in rit:
            if (is_url and c not in CHARS['URL']) or c not in CHARS['FNM']:
                break
            txt += c
        rit = txt

        # complete filename or URL
        oac = lft + rit

        if not is_url:
            fbs = Path(oac).name
            vld = Path(oac).exists()

            if DEBUG['OAC']: print(f'  fnm  : [{oac}]')
            if DEBUG['OAC']: print(f'  fbs  : [{fbs}]')
        else:
            vld = False
            try:
                requests.get(oac, timeout=1)
                vld = True
            except requests.exceptions.InvalidURL as e:
                pass
            except requests.ConnectionError as e:
                pass
            except UnicodeError as e:
                pass
            except requests.Timeout as e:
                pass

            if DEBUG['OAC']: print(f'  URL  : [{oac}]')

        if DEBUG['OAC']: print(f'  valid: [{vld}]')

        # select filename or URL
        if vld:
            lin = doc.CurrentLine
            pos = doc.PositionFromLine(lin)
            txt = doc.GetLineText(lin)
            pos = doc.FindText(pos, pos + len(txt), oac)
            spos, epos = pos, pos + len(oac)
            doc.SetSelection(spos, epos)
            print(spos, epos)

        # # called from generated context menu item: editor (0)
        # if src in 'EDT':
        #     if vld:
        #         glb.SB.push_text(f'Opening URL [{oac}] at caret')
        #         webbrowser.open(oac)
        #         glb.SB.push_text(f'Opening file [{fbs}] at caret')
        #         fil_lst = [[oac]]
        #         open_files(fil_lst)
        #     else:
        #         glb.SB.set_text(f'Invalid URL [{oac}] at caret', typ='ERROR')
        #         glb.SB.set_text(f'Invalid filename [{fbs}] at caret', typ='ERROR')
        # # called from generated context menu item: task panel (1)
        # elif vld:

        return oac if vld else None


###########################################################################
###########################################################################

    def file_quick_open(self, evt):
        print('file_quick_open')

        if not (doc := get_doc()): return

        dlg = QuickOpenDialog(self)
        set_icon(dlg)
        dlg.txc_pnm.SetValue(doc.dnm)  # cwd()
        if dlg.ShowModal() == wx.ID_OK:
            print('quick open file(s)')

###########################################################################
###########################################################################

    def file_rename(self, evt):
        if not (doc := get_doc()): return

        with wx.TextEntryDialog(self, 'New filename:', 'Rename', doc.fnm) as dlg:
            set_icon(dlg)
            # cancel
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            # unmodified
            if (fnm := dlg.Value) == doc.fnm:
                return
            # save current filename parts
            pnm = str(Path(doc.dnm, fnm))
            dnm, fnm, fbs, ext = split_path(pnm)

        try:
            Path(doc.pnm).rename(pnm)
        except FileExistsError as e:
            msg = f'File already exists.\n\n\'{pnm}\'\n\n{e}'
            msg_box(self, 'WARN', msg)
            return
        except OSError as e:
            msg = f'Filename syntax is incorrect.\n\n\'{fnm}\'\n\n{e}'
            msg_box(self, 'WARN', msg)
            return

        # apply new filename parts
        doc.dnm = dnm
        doc.fnm = fnm
        doc.fbs = fbs
        doc.ext = ext
        doc.pnm = pnm
        print(pnm)

        # get language based on file extension
        lng_lst = [e for e in LANG if ext in e[3].split('|')]
        doc.update_language_styling(lng_lst)
        glb.NBK.update_page_tab(doc)

    def file_reopen_closed_from_history(self, evt):  #, all_files=False
        cnt = glb.MB.rfh_cache.Count

        if (id_ := evt.Id) == MI['FIL_RCA'] and glb.RFH['RecentFileHistory']['ReopenConfirm']:
            msg = f'Reopen {str(cnt)} file(s) from recent file history?'
            if msg_box(self, 'WARN_ASK', msg) != wx.ID_YES:
                return

#DONE, reopen last file wiggles page tab in notebook, use 'make_tab_visible' in open_files
        # walk file history
        for fid in range(cnt):
            fnm = glb.MB.rfh_cache.GetHistoryFile(fid)
            if not is_open_file(fnm):
                fil_lst = [[fnm]]
                open_files(fil_lst)
                fbs = Path(fnm).name
                glb.SB.push_text(f'Reopening closed file [{fbs}] from recent file history')
                # quit if 1 file selected
                if id_ == MI['FIL_RCF']:
                    break
#FIX, focus is on page tab itself instead of in document
        # if not (doc := get_doc()): return
        # dbg_FOCUS(doc)

    def file_revert_to_saved(self, evt):
        if not (doc := get_doc()): return
        if glb.CFG['Editor']['RevertConfirm']:
            msg = f'Reload file {doc.fnm}?\n\nNOTE: changes will be lost.'
            if msg_box(self, 'WARN_ASK', msg) != wx.ID_YES:
                return
        # save caret position, first line and selection
        pos = doc.CurrentPos
        top = doc.FirstVisibleLine
        spos, epos = doc.GetSelection()
        # reload file (unmodified buffer)
        doc.LoadFile(doc.pnm)
        doc.SetModified(False)
        glb.NBK.update_page_tab(doc)
        # restore caret's last position and first line
        doc.GotoPos(pos)
        doc.SetFirstVisibleLine(top)
        # restore selection
        if spos != epos:
            doc.SetSelection(spos, epos)
        # clear caret position history
        doc.cph_cache_lst = [pos]
        doc.cph_idx = 0

    def file_save(self, evt):
        if not (doc := get_doc()): return
        dbg_FILE('IN')
        res = True
        if doc.IsModified():
            if doc.dnm:
                self.Freeze()
                res = doc.SaveFile(doc.pnm)
                glb.NBK.update_page_tab(doc)
                create_symbol_index(self, me_("F"))
                self.Thaw()
                glb.SB.set_text(f'Saved [{doc.pnm}]')
            else:
                msg = f'New file {doc.fnm} has been modified, save changes?'
                if (res := msg_box(self, 'WARN_ASK', msg)) == wx.ID_YES:
                    res = self.file_save_as(evt)
                    dbg_FOCUS(doc)
                    dbg_FILE(f'       Yes:[{doc.pnm}]')
                elif res == wx.ID_NO:
                    dbg_FILE(f'        No:[{doc.pnm}]')
                elif res == wx.ID_CANCEL:
                    dbg_FILE(f'    Cancel:[{doc.pnm}]')
                    res = False
        else:
            dbg_FILE(f'    NO mod:[{doc.pnm}]')

        dbg_FILE('OUT')
        return res

    def file_save_all(self, evt):
        if not (doc := get_doc()): return
        dbg_FILE('IN')
        self.Freeze()
        cur = glb.NBK.Selection     # save current page
        for pag, __ in glb.NBK.open_docs():
            glb.NBK.SetSelection(pag)
            self.file_save(evt)
        glb.NBK.SetSelection(cur)  # restore current page
        self.Thaw()

        dbg_FILE('OUT')

    def file_save_as(self, evt):
        if not (doc := get_doc()): return
        dbg_FILE('IN')

        res = True

#NOTE, file_save_as starts 'Save As' dialog
        sty = wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_PREVIEW | wx.FD_OVERWRITE_PROMPT
        with wx.FileDialog(self, 'Save As', cwd(), doc.pnm, LANG_WILDCARDS, sty) as dlg:
            idx = LANG.index([m for m in LANG if glb.MB.IsChecked(m[4])][0])
            print(idx)
            dlg.SetFilterIndex(idx + 1)  # add 1: 'All files' = 0 in 'LANG_WILDCARDS'
            if dlg.ShowModal() != wx.ID_OK:
                dbg_FILE(f'    Cancel:[{doc.pnm}]')
                res = False
            else:
                dbg_FILE(f'        OK:[{doc.pnm}]')
#FIX, test whether to use '.Path(s) AND if '.strip()' is needed
                pnm = dlg.Path
#                 pnm = dlg.Path.strip()

                self.Freeze()
                res = doc.SaveFile(pnm)
                dnm, fnm, fbs, ext = split_path(pnm)
                doc.dnm, doc.fnm, doc.fbs, doc.ext = dnm, fnm, fbs, ext
                doc.pnm = pnm
                glb.NBK.update_page_tab(doc)
                create_symbol_index(self, me_("F"))
                self.Thaw()

        dbg_FILE('OUT')

        return res

    def file_new_window(self, evt):
        txt = TXT_NIL
        if (id_ := evt.Id) == MI['FIL_NWN']:
            txt = 'New'
        elif id_ == MI['FIL_CWN']:
            txt = 'Close'
        if txt:
            txt += ' Window'
            not_implemented(None, txt)
            msg = f'{me_("F")} not implemented'
            msg_box(self, 'INFO', msg, extra=txt)

    def file_write_block_to_file(self, evt):
        if not (doc := get_doc()): return
        dbg_FILE('IN')

        sty = wx.FD_SAVE | wx.FD_CHANGE_DIR | wx.FD_PREVIEW | wx.FD_OVERWRITE_PROMPT
        with wx.FileDialog(self, 'Write Block To File', cwd(), '', LANG_WILDCARDS, sty) as dlg:
            dlg.SetFilterIndex(19)  # default: plain text
            if dlg.ShowModal() != wx.ID_OK:
                dbg_FILE(f'    Cancel:[{doc.pnm}]')
            else:
                sel_txt = doc.SelectedText
                pnm = dlg.Path
                dbg_FILE(f'        OK:[{pnm}]')
                with open(pnm, 'w') as fil:
                    fil.write(sel_txt.replace(CR, TXT_NIL))
                glb.SB.set_text(f'Block written to file [{pnm}] ')

        dbg_FILE('OUT')
