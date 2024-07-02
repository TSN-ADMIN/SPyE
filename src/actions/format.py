#!/usr/bin/python

from datetime import datetime as dtm

import wx
from wx import stc

from ._load import _load
from common.util import curdoc, curdoc_class
from conf.debug import DBG, dbf
from const.editor import CRLF, LF
from const import glb
from const.menubar import MI
from const.statusbar import SBX_EOL


@_load
@curdoc_class(curdoc)
class Format:

    def format_case(self, evt):
        if (sel_txt := doc.SelectedText):
            top = doc.FirstVisibleLine
            spos, epos = doc.GetSelection()
            new = None
            if (id_ := evt.Id) == MI['FMT_TTL']:
#INFO, URL=https://docs.python.org/library/stdtypes.html#str.title
                new = sel_txt.title()
            elif id_ == MI['FMT_UPR']:
                doc.UpperCase()
            elif id_ == MI['FMT_LWR']:
                doc.LowerCase()
            elif id_ == MI['FMT_INV']:
                new = ''.join(c.lower() if c.isupper() else c.upper() for c in sel_txt)
            if new:
                doc.ReplaceSelection(new)
#FIX, check caret positioning for ease of use
            doc.SetFirstVisibleLine(top)
            doc.SetSelection(spos, epos)

    def format_comment(self, evt):

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# copied from 'toggle_comment' in 'TextEditor-master\control.py'
        # comment = '#'
        # if not comment:
        #     return
        # doc.BeginUndoAction()
        # spos, epos = doc.GetSelection()
        # slin, elin = doc.LineFromPosition(slin), doc.LineFromPosition(elin)
        # if doc.PositionFromLine(elin) == elin:
        #     elin -= 1
        # for lin in range(slin, elin + 1):
        #     text = doc.GetLine(lin)
        #     if text.startswith(comment):
        #         text = text[len(comment):]
        #     else:
        #         text = comment + text
        #     slin, elin = doc.PositionFromLine(lin), doc.PositionFromLine(lin + 1)
        #     doc.SetSelection(slin, elin)
        #     doc.ReplaceSelection(text)
        # slin, elin = doc.PositionFromLine(slin), doc.PositionFromLine(elin + 1)
        # doc.SetSelection(slin, elin)
        # doc.EndUndoAction()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        cmt = True
        cur = doc.CurrentPos
        lin = doc.CurrentLine
        fnd = '^[ \t]*#'  # regex (Pyhon ONLY for now)
        flg = stc.STC_FIND_REGEXP

        # handle selection
        lin_cnt, cnt, spos, epos = 1, doc.Selections, *doc.GetSelection()
        if cnt > 1 or spos != epos:
            slin, elin = [doc.LineFromPosition(s) for s in (spos, epos)]
            if slin != elin:
                lin_cnt = elin - slin + 1

        # set 'for loop' range
        if lin_cnt > 1:
            fr, to = slin, elin
        else:
            fr, to = lin, lin + 1

        doc.BeginUndoAction()
        for lin in range(fr, to):
            start = doc.PositionFromLine(lin)
            end = start + doc.GetLineLength(lin)

            pos = doc.FindText(start, end, fnd, flg)
            if pos == stc.STC_INVALID_POSITION:
                cmt = False

            if cmt:
                txt = 'Uncommented line'
                doc.DeleteRange(pos, 2)
            else:
                txt = 'Commented line'
                doc.InsertText(start, '# ')

        if cnt > 1 or spos != epos:
            doc.SetSelection(spos, epos)
        doc.EndUndoAction()

        glb.SBR.set_text(txt)

    def convert_eol(self, evt):

        if (id_ := evt.Id) in [MI['FMT_ECL'], SBX_EOL.ECL.id]:
            glb.MBR.Check(MI['FMT_ECL'], True)
            flg = stc.STC_EOL_CRLF
        elif id_ in [MI['FMT_ELF'], SBX_EOL.ELF.id]:
            glb.MBR.Check(MI['FMT_ELF'], True)
            flg = stc.STC_EOL_LF
        elif id_ in [MI['FMT_ECR'], SBX_EOL.ECR.id]:
            glb.MBR.Check(MI['FMT_ECR'], True)
            flg = stc.STC_EOL_CR

#HACK, for a very short time ignore current doc's events for speed boost
        doc.SetEvtHandlerEnabled(False)
        doc.BeginUndoAction()
        doc.ConvertEOLs(flg)
        doc.SetEOLMode(flg)
        doc.EndUndoAction()
        doc.SetEvtHandlerEnabled(True)

    def insert_timestamp(self, evt):

        tim = dtm.now()
        doc.AddText(tim.strftime(glb.CFG['Editor']['TimestampFormat']))
        glb.SBR.push_text('Timestamp inserted')

    # copied from Editra, ed_stc.py
    def remove_trailing_whitespace(self, evt):
        cpos = doc.CurrentPos
        clin = doc.CurrentLine
        clin_len = len(doc.GetLine(clin))
        epos = clin_len - (doc.GetLineEndPosition(clin) - cpos)
        dbf.RMTWS('BEFORE:', cpos, clin, clin_len, epos, doc)

        # start removing trailing whitespace
        cnt = 0
        wx.BeginBusyCursor()
        doc.BeginUndoAction()

        for lnr in range(doc.LineCount):
            eol = ''
            lin = doc.GetLine(lnr)

            # Scintilla stores text in utf-8 internally so we need to
            # encode to utf-8 to get the correct length of the text.
            tlen = len(lin.encode('utf-8'))
            if not tlen:
                continue

            # set end of line
            if CRLF in lin:
                eol = CRLF
            elif LF in lin:
                eol = LF
            else:
                eol = lin[-1]

            # no traling space
            if not eol.isspace():
                continue

            if eol in ' \t':
                eol = ''

            # strip whitespace from line
            end = doc.GetLineEndPosition(lnr) + len(eol)
            start = max(end - tlen, 0)
            doc.SetTargetStart(start)
            doc.SetTargetEnd(end)

            rlin = lin.rstrip() + eol
            if rlin != doc.GetTextRange(start, end):
                doc.ReplaceTarget(rlin)
                cnt += 1
                DBG('TWS', f'    {lnr + 1}:[{lin.__repr__()}]')
                DBG('TWS', f'    {lnr + 1}:[{rlin.__repr__()}]\n')

        doc.EndUndoAction()
        wx.EndBusyCursor()

        txt = f'Removed {cnt} trailing space occurrences' if cnt else 'No trailing space found'
        glb.SBR.push_text(txt)

        # restore caret position
        clin_len = len(doc.GetLine(clin))
        end = doc.GetLineEndPosition(clin)

        if epos >= clin_len:
            epos = end
        else:
            start = max(end - clin_len, 0)
            DBG('TWS', ' ', end, clin_len, start)
            epos += start

        dbf.RMTWS(' AFTER:', cpos, clin, clin_len, epos, doc)
        if epos != cpos and clin > 0:
            doc.GotoPos(epos)
