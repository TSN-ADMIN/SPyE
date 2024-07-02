#!/usr/bin/python


from wx import stc

from ._load import _load
from common.util import curdoc, curdoc_class
from conf.debug import DBG, me_
from const import glb
from const.menubar import MI


@_load
@curdoc_class(curdoc)
class Select:

    def select_add_line(self, evt):
        if (id_ := evt.Id) == MI['SEL_APL']:
            doc.LineUpRectExtend()
        elif id_ == MI['SEL_ANL']:
            doc.LineDownRectExtend()
#FIX, weird delete behaviour using Backspace
        doc.SetSelectionMode(stc.STC_SEL_THIN)

    def select_all(self, evt):
        doc.SelectAll()

    def select_braces(self, evt):

        # check for brace in immediate vicinity and select
        res = self.do_brace_match(evt)

        # check for brace farther away?
        if not res:
            cur = doc.CurrentPos
            prs = glb.CFG['Brace']['Pairs']
            # create backslashed regex
            bs = '\\'
            fnd = f'[{bs}{bs.join(prs)}]'
            flg = stc.STC_FIND_REGEXP

            # search backward for unbalanced opening brace
            cnt_lst = [0, 0, 0, 0]
            open_pos = stc.STC_INVALID_POSITION
            pos = cur
            while True:
                pos = doc.FindText(pos, 0, fnd, flg)
                if pos == stc.STC_INVALID_POSITION:
                    break
                brc = chr(doc.GetCharAt(pos))
                idx = prs.index(brc)
                cnt_lst[idx % 4] -= 1 if idx < 4 else -1
                chk = len([c for c in cnt_lst[:3] if c < 0])  # discard '<'
                if chk:
                    open_pos = pos
                    open_brc = brc
                    # print(chk, pos)
                    break

            # search forward for unbalanced closing brace
            cnt_lst = [0, 0, 0, 0]
            close_pos = stc.STC_INVALID_POSITION
            pos = cur
            while True:
                pos = doc.FindText(pos, doc.LastPosition, fnd, flg)
                if pos == stc.STC_INVALID_POSITION:
                    break
                brc = chr(doc.GetCharAt(pos))
                idx = prs.index(brc)
                cnt_lst[idx % 4] -= 1 if idx >= 4 else -1
                chk = len([c for c in cnt_lst[:3] if c < 0])  # discard '>'
                if chk:
                    close_pos = pos
                    close_brc = brc
                    # print(chk, pos)
                    break
#HACK, prevents loop forever
                pos += 1

            # brace pair found?
            DBG('BRC', f'{me_()}')
            if stc.STC_INVALID_POSITION not in [open_pos, close_pos]:
                # corresponding braces?
                if prs.index(open_brc) + 4 == prs.index(close_brc):
                    doc.SetSelection(open_pos + 1, close_pos)
                    DBG('BRC', '    found:', open_pos, close_pos, open_brc, close_brc)
            else:
                DBG('BRC', '    NOT found')

            DBG('BRC', f'    count: {cnt_lst}, total: {sum(cnt_lst)}')

    def select_line(self, evt=None, _fwd=True):
        spos, epos = doc.GetSelection()
        slin, elin = doc.LineFromPosition(spos), doc.LineFromPosition(epos)
        if spos != doc.PositionFromLine(slin) or epos != doc.PositionFromLine(elin):
            spos = doc.PositionFromLine(slin)
            epos = doc.PositionFromLine(elin)
            doc.Home()  # caret sticks to 1st column
            doc.SetSelection(spos, epos)
        if _fwd:
            doc.LineDownExtend()
        else:
            doc.LineUpExtend()

    def select_indentation(self, evt):

        # get indentation for current line
        pos = doc.CurrentPos
        cur = doc.LineFromPosition(pos)
        ind = doc.GetLineIndentation(cur)
        print(f'indent: {ind}')

        if ind > 0:
            # get 1st line above with smaller indentation
            lin = cur
            while True:
                lin -= 1
                if doc.GetLineIndentation(lin) < ind:
                    # discard whitespace only line
                    if not doc.GetLine(lin).strip():
                        continue
                    break
            start = lin + 1
            # get last line below with smaller indentation
            lin = cur
            while True:
                lin += 1
                if doc.GetLineIndentation(lin) < ind:
                    # discard whitespace only line
                    if not doc.GetLine(lin).strip():
                        continue
                    break
            end = lin
            # create selection
            start = doc.PositionFromLine(start)
            end = doc.PositionFromLine(end)
            doc.SetSelection(start, end)

    def select_paragraph(self, evt):
        doc.ParaDown()
        doc.Home()  # caret sticks to 1st column
        doc.LineUp()
        doc.ParaUpExtend()
        doc.SwapMainAnchorCaret()

    #TODO, integrate with selection_to_line()
    def select_split_into_lines(self, evt):
        spos, epos = doc.GetSelection()
        slin, elin = doc.LineFromPosition(spos), doc.LineFromPosition(epos)
        cnt = elin - slin + 1
        # more than 1 line selected?
        if cnt >= 2:
            # remove single selection
            doc.SelectNone()
            doc.SetSelection(spos, spos)
            # split single into multiple selection per line
            for s in range(cnt):
                anchor = spos if s == 0 else doc.PositionFromLine(slin + s)
                caret = epos if s == cnt - 1 else doc.GetLineEndPosition(slin + s)
                if s == doc.MainSelection:
                    doc.SetSelection(anchor, caret)
                else:
                    doc.AddSelection(caret, anchor)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, 'Ctrl+Shift+L' -> for TEST and better performance use threading/FastPython info
#INFO, test with file 'D:\Dev\W\data\worldcitiespop.txt'
                # if s % 10000 == 0:
                #     print(s)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # else:
        #     glb.SBR.push_text('Need at least 2 selected lines to split')

    def select_anchor_caret_swap(self, evt):
        cnt = doc.Selections
        # swap selection(s)
        for s in range(cnt):
            anchor = doc.GetSelectionNAnchor(s)
            caret = doc.GetSelectionNCaret(s)
            doc.SetSelectionNAnchor(s, caret)
            doc.SetSelectionNCaret(s, anchor)
        doc.EnsureCaretVisible()
        glb.SBR.push_text(f'Swapped {cnt} anchor/caret selection pairs')

    def select_word(self, evt):
        doc.select_next_word()
