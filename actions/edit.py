#!/usr/bin/python

from pathlib import Path

from wx import stc

from ._load import _load
from common.doc import get_doc
from common.util import cur_doc, me_, not_implemented
from conf.debug import DEBUG, dbg_FOCUS
from const.app import APP
from const.common import TXT_NIL
from const.editor import CHARS, CRLF, MGN, MRK, NEWLINE, URI_SCHEMES
from const import glb
from const.menu import MI
from const.toolbar import TB


@_load
class Edit:

    def edit_autocomplete(self, evt):
        if not (doc := get_doc()): return
        doc.auto_complete(evt)

    def edit_calc_sum_of_text(self, evt):
        if not (doc := get_doc()): return
        if (sel_txt := doc.SelectedText):
#FIX, use '.splitlines()'
            txt_lst = sel_txt.split(doc.newline)
            tot = 0.0
            for lin in txt_lst:
                if lin:
                    try:
                        val = float(lin)
                    except ValueError:
                        pass
                    else:
                        tot += val
            doc.CopyText(len(str(tot)), str(tot))
            glb.SB.set_text(f'Sum of selection: [{tot:.1f}] -> copied to clipboard')

    def edit_calltip(self, evt):
        if not (doc := get_doc()): return
        doc.calltip_start(evt)

    def edit_clipboard(self, evt):
        if not (doc := get_doc()): return

        id_ = evt.Id

#TODO: create and init dict/list 'cnt' for 'cnt' and 'cut/cpy/pst_cnt' ?
#         cnt = {'sel': 0, 'cut': 0, 'cpy': 0, 'pst': 0, }
        cnt = doc.Selections

        if glb.CFG['MultiEdit']['Clipboard'] and cnt >= 2:
            if id_ in [MI['EDT_CUT'], MI['EDT_CPY']]:
                self.multi_clp_lst = []
            elif id_ in [MI['EDT_PST']]:
                if not self.multi_clp_lst:
                    glb.SB.push_text('Multi clipboard empty, unable to paste')
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
                if DEBUG['MCB']: print(f'{sel}: {sel_lst[sel][:2]} - ')
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
                if DEBUG['MCB']: print(f'{sel_lst[sel][:2]}')
            # restore selections
            for sel in range(cnt):
                anchor, caret, txt = sel_lst[sel]
                if sel == doc.MainSelection:
                    doc.SetSelection(anchor, caret)
                else:
                    doc.AddSelection(caret, anchor)
            # doc.SetSelection(anchor, caret)
            doc.EndUndoAction()
            glb.SB.push_text(f'Multi clipboard: cut={cut_cnt}, copy={cpy_cnt}, paste={pst_cnt}')
            if DEBUG['MCB']: print(f'Multi clipboard[{len(self.multi_clp_lst)}]: {self.multi_clp_lst}')
        else:
            if id_ == MI['EDT_CUT']:
                doc.Cut()
            elif id_ == MI['EDT_CPY']:
                doc.Copy()
            elif id_ == MI['EDT_PST']:
                doc.Paste()

    def edit_copy_filename(self, evt):
        if not (doc := get_doc()): return
        fnm = doc.pnm  # fully qualified
        doc.CopyText(len(fnm), fnm)
# DONE, add list of (dnm, fnm, bas_nam, ext) to Editor class (doc object)
        glb.SB.set_text(f'Filename [{fnm}] -> copied to clipboard')

    def edit_delete(self, evt):
        if not (doc := get_doc()): return
        if doc.SelectedText:
            doc.Clear()

    def edit_duplicate_line(self, evt):
        if not (doc := get_doc()): return
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
        if not (doc := get_doc()): return
        spos, epos = doc.GetSelection()
        start, end = doc.LineFromPosition(spos), doc.LineFromPosition(epos)
        # get 1st visible line above selection
        vis = start - 1
        while not doc.GetLineVisible(vis) and vis > 0:
            vis -= 1
            # if vis < 0:
            #     vis = 0
        # mark hidden range
        doc.MarkerAdd(vis, MRK['HLS']['NUM'])      # start
        doc.MarkerAdd(vis, MRK['HLU']['NUM'])      # underline
        doc.MarkerAdd(end + 1, MRK['HLE']['NUM'])  # end
        doc.SelectNone()
        doc.HideLines(start, end)
        doc.GotoLine(start - 1)  # caret above hidden range

    def edit_mark_matches(self, evt):
        if not (doc := get_doc()): return
        for ind in range(1, 6):
            if evt.Id == MI[f'EDT_MS{ind}']:
                break
        else:
            ind = 0
        doc.mark_matches(evt, ind)

    def edit_mark_matches_clear(self, evt):
        if not (doc := get_doc()): return
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
        if not (doc := get_doc()): return
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
            if DEBUG['SCL']: print(f'  {txt}')
            glb.SB.push_text('Moved caret to ' + txt)

    def edit_move_selected_lines(self, evt):
        if not (doc := get_doc()): return
        txt = TXT_NIL
        if (id_ := evt.Id) == MI['LIN_SLD']:
            txt = 'down'
            doc.MoveSelectedLinesDown()
        elif id_ == MI['LIN_SLU']:
            txt = 'up'
            doc.MoveSelectedLinesUp()
        if txt:
            if DEBUG['SCL']: print(f'  {txt}')
            glb.SB.push_text('Moved selected line(s) ' + txt)
        # doc.SwapMainAnchorCaret()

    @cur_doc(2)
    def edit_redo(self, doc, evt):
    # def edit_redo(self, evt):
        if not (doc := get_doc()): return
        if doc.CanRedo():
            doc.Redo()
        else:
#FIX, message never shows, see updateui_doc
            glb.SB.set_text('End of redo history buffer')

    def edit_scroll_line_to(self, evt):
        if not (doc := get_doc()): return
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
            if DEBUG['SCL']: print(f'  {txt}')
            glb.SB.push_text('Scrolled current line to ' + txt)

    def edit_sort_lines(self, evt):
        if not (doc := get_doc()): return

        # force line-based selection
        txt, slin, elin, spos, epos = doc.selection_to_line()
        # more than 1 line selected?
        if slin != elin:
            doc.BeginUndoAction()
            txt_lst = txt.split(doc.newline)
            if (id_ := evt.Id) in [MI['SRT_LIN'], TB['SRT']]:
                txt_lst.sort()
            elif id_ == MI['SRT_REV']:
                txt_lst.sort(reverse=True)
            elif id_ == MI['SRT_UNQ']:
                txt_lst = sorted(set(txt_lst))
            txt = str(doc.newline.join(txt_lst))
            doc.ReplaceSelection(txt)
            # reselect after sort
            epos = spos + len(txt_lst)
            doc.SetSelection(spos, epos)
            doc.EndUndoAction()

    def edit_split_text(self, evt):
        if not (doc := get_doc()): return
        start, stop = doc.GetSelection()
        len_ = stop - start
        if DEBUG['GEN']: print('  Selection (start, stop, len_) = [%5d, %5d, %5d]' % (start, stop, len_))

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
        if not (doc := get_doc()): return
        start, stop = doc.GetSelection()
        len_ = stop - start
        if DEBUG['GEN']: print('  Selection (start, stop, len_) = [%5d, %5d, %5d]' % (start, stop, len_))

        if len_:
            sel_txt = doc.SelectedText
            doc.BeginUndoAction()
            doc.ReplaceSelection(TXT_NIL)
            doc.AddText(sel_txt.replace(NEWLINE, ' '))
            doc.EndUndoAction()

    def edit_goto_paragraph(self, evt):
        if not (doc := get_doc()): return
        if (id_ := evt.Id) == MI['PAR_NXT']:
            if DEBUG['GEN']: print('  Next')
            doc.ParaDown()
        elif id_ == MI['PAR_PRV']:
            if DEBUG['GEN']: print('  Previous')
            doc.ParaUp()

    def edit_transpose_line(self, evt):
        if not (doc := get_doc()): return
        doc.LineTranspose()

    @cur_doc(1)
    def edit_undo(self, doc, evt):
    # def edit_undo(self, evt):
        if not (doc := get_doc()): return
        if doc.CanUndo():
            doc.Undo()
        else:
#FIX, message never shows, see updateui_doc
            glb.SB.set_text('End of undo history buffer')
