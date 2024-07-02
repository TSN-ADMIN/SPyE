#!/usr/bin/python

from pathlib import Path

import wx
from wx import stc

from ._load import _load
from common.util import curdoc, curdoc_class, not_implemented, set_icon, ColumnEditorDialog
from conf.debug import DBG, me_
from const.app import APP
from const.common import TXT_NIL
from const.editor import CHARS, CRLF, MGN, MRK, NEWLINE, URI_SCHEMES
from const import glb
from const.menubar import MI
from const.toolbar import TBR


@_load
#FIX, replace ALL 21 '@curdoc()' below with JUST 1 '@curdoc_class()' (MUST be possible)
#NOTE, this 'Edit' class is mixed in as 'act.Edit' in 'class AppFrame'
#NOTE, UNKNOWN why at 'frame load time' the '@curdoc_class()' does NOT properly decorate
#NOTE, NOW gives this ERROR when FIX is done
#INFO,   Traceback (most recent call last):
#INFO,     File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\actions\edit.py", line 254, in edit_scroll_line_to
#INFO,       doc.VerticalCentreCaret()
#INFO,   NameError: name 'doc' is not defined
@curdoc_class(curdoc)
class Edit:
    def edit_autocomplete(self, evt):
        doc.auto_complete(evt)

    def edit_calc_sum_of_text(self, evt):
        if (sel_txt := doc.SelectedText):
#FIX, use '.splitlines()'
            txt_lst = sel_txt.split(doc.newline)
            tot = 0.0
            for lin in txt_lst:
                if lin:
                    try:
                        val = float(lin)
                    except ValueError as e:
                        pass
                    else:
                        tot += val
            doc.CopyText(len(str(tot)), str(tot))
            glb.SBR.set_text(f'Sum of selection: [{tot:.1f}] -> copied to clipboard')

    def edit_column_editor(self, evt):
        print('edit_column_editor')

        dlg = ColumnEditorDialog(self)
        set_icon(dlg)
        if dlg.ShowModal() == wx.ID_OK:
            print('insert column text')

    def edit_calltip(self, evt):
        doc.calltip_start(evt)

    def edit_clipboard(self, evt):

        id_ = evt.Id

#TODO: create and init dict/list 'cnt' for 'cnt' and 'cut/cpy/pst_cnt' ?
#         cnt = {'sel': 0, 'cut': 0, 'cpy': 0, 'pst': 0, }
        cnt = doc.Selections

        if glb.CFG['MultiEdit']['Clipboard'] and cnt >= 2:
            if id_ in [MI['EDT_CUT'], MI['EDT_CPY']]:
                self.multi_clp_lst = []
            elif id_ in [MI['EDT_PST']]:
                if not self.multi_clp_lst:
                    glb.SBR.push_text('Multi clipboard empty, unable to paste')
                    return
            # set stream selection, rectangular does not work here
            doc.SetSelectionMode(stc.STC_SEL_STREAM)
            doc.BeginUndoAction()
            # save selections
            sel_lst = []
            pos = doc.CurrentPos
            for sel in range(cnt):
                anchor = doc.GetSelectionNAnchor(sel)
                caret = doc.GetSelectionNCaret(sel)
                # process selection left to right
                if anchor > caret:
                    anchor, caret = caret, anchor
                txt = doc.GetTextRange(anchor, caret)
                sel_lst.append([anchor, caret, txt])
            # process selections top to bottom
            sel_lst.sort()
            # remove selections
            doc.SelectNone()
            doc.SetSelection(pos, pos)
            # clipboard action per selection
            cut_cnt = cpy_cnt = pst_cnt = 0
            for sel in range(cnt):
                DBG('MCB', f'{sel}: {sel_lst[sel][:2]} - ')
                anchor, caret, txt = sel_lst[sel]
                if id_ in [MI['EDT_CUT']]:
                    anchor -= cut_cnt
                    caret = anchor
                    doc.DeleteRange(anchor, len(txt))
                    self.multi_clp_lst.append(txt)
                    cut_cnt += len(txt)
                elif id_ in [MI['EDT_CPY']]:
                    self.multi_clp_lst.append(txt)
                    cpy_cnt += len(txt)
                elif id_ in [MI['EDT_PST']]:
                    anchor -= cut_cnt
                    anchor += pst_cnt
                    caret = anchor  # + len(self.multi_clp_lst[sel])
                    doc.DeleteRange(anchor, len(txt))
                    cut_cnt += len(txt)
                    # paste if clipboard length permits
                    if sel < len(self.multi_clp_lst):
                        doc.InsertText(anchor, self.multi_clp_lst[sel])
                        pst_cnt += len(self.multi_clp_lst[sel])
                sel_lst[sel] = [anchor, caret, txt]
                DBG('MCB', f'{sel_lst[sel][:2]}')
            # restore selections
            for sel in range(cnt):
                anchor, caret, txt = sel_lst[sel]
                if sel == doc.MainSelection:
                    doc.SetSelection(anchor, caret)
                else:
                    doc.AddSelection(caret, anchor)
            # doc.SetSelection(anchor, caret)
            doc.EndUndoAction()
            glb.SBR.push_text(f'Multi clipboard: cut={cut_cnt}, copy={cpy_cnt}, paste={pst_cnt}')
            DBG('MCB', f'Multi clipboard[{len(self.multi_clp_lst)}]: {self.multi_clp_lst}')
        else:
            if id_ == MI['EDT_CUT']:
                doc.Cut()
            elif id_ == MI['EDT_CPY']:
                doc.Copy()
            elif id_ == MI['EDT_PST']:
                doc.Paste()

    def edit_copy_filename(self, evt):
        fnm = doc.pnm  # fully qualified
        doc.CopyText(len(fnm), fnm)
# DONE, add list of (dnm, fnm, bas_nam, ext) to Editor class (doc object)
        glb.SBR.set_text(f'Filename [{fnm}] -> copied to clipboard')

    def edit_delete(self, evt):
        if doc.SelectedText:
            doc.Clear()

    def edit_duplicate_line(self, evt):
        spos, epos = doc.GetSelection()
        if not (len_ := epos - spos):
            # no selection, duplicate line
            doc.LineDuplicate()
        else:
            # duplicate selected text
            txt = doc.SelectedText
            doc.CharRight()
            doc.InsertText(spos + len_, txt)
            # reselect inserted text
            doc.SetSelection(spos + len_, epos + len_)

    def edit_hide_lines(self, evt):
        spos, epos = doc.GetSelection()
        slin, elin = doc.LineFromPosition(spos), doc.LineFromPosition(epos)
        # get 1st visible line above selection
        vis = slin - 1
        while not doc.GetLineVisible(vis) and vis > 0:
            vis -= 1
            # if vis < 0:
            #     vis = 0
        # mark hidden range
        doc.MarkerAdd(vis, MRK['HLS']['NUM'])      # start
        doc.MarkerAdd(vis, MRK['HLU']['NUM'])      # underline
        doc.MarkerAdd(elin + 1, MRK['HLE']['NUM'])  # end
        doc.SelectNone()
        doc.HideLines(slin, elin)
        doc.GotoLine(slin - 1)  # caret above hidden range

    def edit_mark_matches(self, evt):
        for ind in range(1, 6):
            if evt.Id == MI[f'EDT_MS{ind}']:
                break
        else:
            ind = 0
        doc.mark_matches(evt, ind)

    def edit_mark_matches_clear(self, evt):
        if (id_ := evt.Id) == MI['EDT_CSA']:
            for ind in range(1, 6):
                doc.mark_matches_clear(evt, ind)
            return

        for ind in range(1, 6):
            if id_ == MI[f'EDT_CS{ind}']:
                break
        else:
            ind = 0
        doc.mark_matches_clear(evt, ind)

    def edit_move_caret_to(self, evt):
        top = doc.FirstVisibleLine
        los = doc.LinesOnScreen()
        txt = TXT_NIL
        if (id_ := evt.Id) == MI['CRT_TOP']:
            txt = 'top'
            doc.GotoLine(top)
        elif id_ == MI['CRT_CTR']:
            txt = 'centre'
            doc.GotoLine(top + (los // 2))
        elif id_ == MI['CRT_BOT']:
            txt = 'bottom'
            doc.GotoLine(top + los - 1)
        if txt:
            DBG('SCL', f'  {txt}')
            glb.SBR.push_text(f'Moved caret to {txt}')

    def edit_move_selected_lines(self, evt):
        txt = TXT_NIL
        if (id_ := evt.Id) == MI['LIN_SLD']:
            txt = 'down'
            doc.MoveSelectedLinesDown()
        elif id_ == MI['LIN_SLU']:
            txt = 'up'
            doc.MoveSelectedLinesUp()
        if txt:
            DBG('SCL', f'  {txt}')
            glb.SBR.push_text(f'Moved selected line(s) {txt}')
        # doc.SwapMainAnchorCaret()

    def edit_redo(self, evt):
        if (doc := glb.DOC).CanRedo():
            doc.Redo()
        else:
#FIX, message never shows, see updateui_doc
            glb.SBR.set_text('End of redo history buffer')

    def edit_scroll_line_to(self, evt):
        txt = TXT_NIL
        if (id_ := evt.Id) == MI['LIN_TOP']:
            txt = 'top'
            doc.SetFirstVisibleLine(doc.CurrentLine)
        elif id_ == MI['LIN_CTR']:
            txt = 'centre'
            doc.VerticalCentreCaret()
        elif id_ == MI['LIN_BOT']:
            txt = 'bottom'
            doc.ScrollToLine(doc.CurrentLine - doc.LinesOnScreen() + 1)
        if txt:
            DBG('SCL', f'  {txt}')
            glb.SBR.push_text(f'Scrolled current line to {txt}')

    def edit_sort_lines(self, evt):

        # force line-based selection
        txt, slin, elin, spos, epos = doc.selection_to_line()
        # more than 1 line selected?
        if slin != elin:
            doc.BeginUndoAction()
            txt_lst = txt.split(doc.newline)
            if (id_ := evt.Id) in [MI['SRT_LIN'], TBR['SRT']]:
                txt_lst.sort()
            elif id_ == MI['SRT_REV']:
                txt_lst.sort(reverse=True)
            elif id_ == MI['SRT_UNQ']:
                txt_lst = sorted(set(txt_lst))
            txt = str(doc.newline.join(txt_lst))
            doc.ReplaceSelection(txt)
            # reselect after sort
            epos = spos + len(txt_lst)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            pfl_fnc = doc.PositionFromLine
            doc.SetSelection(pfl_fnc(slin), pfl_fnc(elin) + 1)
            doc.LineEndExtend()
            # doc.SetSelection(spos, epos)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            doc.EndUndoAction()

    def edit_split_text(self, evt):
        start, stop = doc.GetSelection()
        len_ = stop - start
        DBG('GEN', f'  Selection: [{start=:5d}], [{stop=:5d}], [{len_=:5d}]')

        if len_:
            sel_txt = doc.SelectedText
            doc.BeginUndoAction()
            doc.ReplaceSelection(TXT_NIL)

            wrd_lst = sel_txt.split(';')
            for wrd in wrd_lst:
                doc.AddText(wrd)
                doc.NewLine()
            doc.DeleteBack()  # delete last newline

            doc.EndUndoAction()

    def edit_join_text(self, evt):
        start, stop = doc.GetSelection()
        len_ = stop - start
        DBG('GEN', f'  Selection: [{start=:5d}], [{stop=:5d}], [{len_=:5d}]')

        if len_:
            sel_txt = doc.SelectedText
            doc.BeginUndoAction()
            doc.ReplaceSelection(TXT_NIL)

            doc.AddText(sel_txt.replace(NEWLINE, ' '))

            doc.EndUndoAction()

    def edit_goto_paragraph(self, evt):
        if (id_ := evt.Id) == MI['PAR_NXT']:
            DBG('GEN', '  Next')
            doc.ParaDown()
        elif id_ == MI['PAR_PRV']:
            DBG('GEN', '  Previous')
            doc.ParaUp()

    def edit_transpose_line(self, evt):
        doc.LineTranspose()

    def edit_undo(self, evt):
        if (doc := glb.DOC).CanUndo():
            doc.Undo()
        else:
#FIX, message never shows, see updateui_doc
            glb.SBR.set_text('End of undo history buffer')
