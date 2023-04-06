#!/usr/bin/python

from wx import stc

from ._load import _load
from common.doc import get_doc
from common.util import is_shown
from conf.debug import DEBUG, dbg_FOCUS
from const.editor import MRK
from const import glb
from const.menu import MI
from const.sidepanel import SPT
import gui
from tool.debugger import Debugger


@_load
class Run:

    def clear_breakpoints(self, evt):
        if not (doc := get_doc()): return
        doc.clear_breakpoints()

    def debugger_start(self, evt=None):
        if not (doc := get_doc()): return
        self.debugger = Debugger(doc)

    def enable_breakpoint(self, evt, lin=None):
        if not (doc := get_doc()): return
        lin = doc.CurrentLine if lin is None else lin

        # force breakpoint list control creation
        if not gui.get_spt('BPT'):
            glb.SPN.SetSelection(SPT.BPT.idx)

        # update doc map panel/control
        # if (ctl := gui.get_spt('DCM')):
        #     ctl.Refresh()  # force 'doc map' update

        msk = doc.MarkerGet(lin)
        if DEBUG['BPT']: print(msk)

        if not (msk & MRK['BPT']['MSK']):
            return

        # find bp line number in list control
        for idx in range((ctl := gui.get_spt('BPT')).ItemCount):
            lbl = ctl.GetItem(idx, 3)  # 4th column: source line
            if int(lbl.Text) != lin + 1:
                continue
            if DEBUG['BPT']: print('Found @%d' % idx, lbl.Text)
            bpn = ctl.GetItemText(idx, 1)  # 2nd column: bp number
            ena = ctl.GetItemText(idx, 2)  # 3rd column: enabled flag

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            if ena == 'No':
                doc.MarkerDelete(lin, MRK['BPD']['NUM'])
            else:
                doc.MarkerAdd(lin, MRK['BPD']['NUM'])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # UPDATE breakpoint list control
            ctl.SetItem(idx, 2, 'No' if ena == 'Yes' else 'Yes')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            if self.debugger:
                bpt_lst = self.debugger.command(f'break').splitlines()
                for bpt in bpt_lst:
                    if 'breakpoint' in bpt and f':{lin + 1}' in bpt:
                        cmd = 'disable' if ena == 'Yes' else 'enable'
                        self.debugger.command(f'{cmd} {bpt[0]}')
                        self.debugger.command(f'break')
                        break
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            if DEBUG['BPT']: print(f'BP {bpn}: disabled' if ena == 'Yes' else f'BP {bpn}: enabled')
            break

    def goto_breakpoint(self, evt):
        if not (doc := get_doc()): return
        cur = doc.CurrentLine

        # force panel visibility
        if glb.CFG['Breakpoint']['ShowPanel']:
            if not is_shown('SPN'):
                self.toggle_panel(evt, 'SPN', -1)
            if not is_shown('BPT'):
                glb.SPN.SetSelection(SPT.BPT.idx)

        if (id_ := evt.Id) == MI['BPT_NXT']:
            if DEBUG['BPT']: print('  Next breakpoint')
            lin = doc.MarkerNext(cur + 1, MRK['BPT']['MSK'])
        elif id_ == MI['BPT_PRV']:
            if DEBUG['BPT']: print('  Previous breakpoint')
            lin = doc.MarkerPrevious(cur - 1, MRK['BPT']['MSK'])

        if lin != stc.STC_INVALID_POSITION:
            doc.GotoLine(lin)
        elif glb.CFG['Breakpoint']['SearchWrap']:
            if id_ == MI['BPT_NXT']:
                lin = doc.MarkerNext(0, MRK['BPT']['MSK'])
            elif id_ == MI['BPT_PRV']:
                lin = doc.MarkerPrevious(doc.LineCount, MRK['BPT']['MSK'])
            if lin != stc.STC_INVALID_POSITION:
                doc.GotoLine(lin)

        if lin != stc.STC_INVALID_POSITION:
            if glb.CFG['Breakpoint']['CentreCaret']:
                doc.VerticalCentreCaret()
            # breakpoint list control
            if (ctl := gui.get_spt('BPT')) and glb.CFG['Breakpoint']['SyncPanel']:
                for idx in range(ctl.ItemCount):
                    if lin == int(ctl.GetItemText(idx, 3)) - 1:  # lineno
                        ctl.Select(idx)
                        ctl.Focus(idx)

        dbg_FOCUS(doc)

    def run_module(self, evt):
        pass

    def toggle_breakpoint(self, evt, lin=None):
        if not (doc := get_doc()): return
        lin = doc.CurrentLine if lin is None else lin

        # no breakpoint at blank/comment line
        if not doc.is_valid_breakpoint(lin):
            return

        # force breakpoint list control creation
        if not (gui.get_spt('BPT') and is_shown('BPT')):
            glb.SPN.SetSelection(SPT.BPT.idx)

        # update doc map panel/control
        # if (ctl := gui.get_spt('DCM')):
        #     ctl.Refresh()  # force 'doc map' update

        msk = doc.MarkerGet(lin)
        if DEBUG['BPT']: print(msk)

        if msk & MRK['BPT']['MSK']:
            doc.MarkerDelete(lin, MRK['BPT']['NUM'])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            doc.MarkerDelete(lin, MRK['BPD']['NUM'])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            if self.debugger:
                self.debugger.command(f'clear {doc.pnm}:{lin + 1}')
                self.debugger.command(f'break')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        else:
            doc.MarkerAdd(lin, MRK['BPT']['NUM'])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            if self.debugger:
                self.debugger.command(f'break {doc.pnm}:{lin + 1}')
                self.debugger.command(f'break')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # UPDATE breakpoint list control
        (ctl := gui.get_spt('BPT')).update_list(doc)
