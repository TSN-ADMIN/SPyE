#!/usr/bin/python

from wx import stc

from ._load import _load
from common.util import curdoc, curdoc_class, is_shown, not_implemented
from conf.debug import DBG, dbf
from const.editor import MRK
from const import glb
from const.menubar import MI
from const.sidepanel import SPT
import gui
from tool.debugger import Debugger


# from extern.ide2py_POC.debugger import DebuggerProxy, EVT_DEBUG_ID, EVT_EXCEPTION_ID, \
#                      EnvironmentPanel, StackListCtrl, SessionListCtrl


@_load
@curdoc_class(curdoc)
class Run:

    # def OnDebugCommand(self, event):
    #     event_id = event.GetId()

    #     # start debugger (if not running):
    #     if self.debugger:
    #         self.debugger = DebuggerProxy(self)
    #         print("*** Execute!!!!")
    #         self.debugger.init(False)
    #         self.OnExecute(event)
    #         # clean running indication
    #         # self.GotoFileLine()
    #     elif event_id == ID_STEPIN:
    #         self.debugger.current.Step()
    #     elif event_id == ID_STEPNEXT:
    #         self.debugger.current.Next()
    #     elif event_id == ID_STEPRETURN:
    #         self.debugger.current.StepReturn()
    #     elif event_id == ID_CONTINUE:
    #         self.GotoFileLine()
    #         self.debugger.current.Continue()
    #     elif event_id == ID_QUIT:
    #         self.debugger.current.Quit()
    #     elif event_id == ID_INTERRUPT:
    #         self.debugger.current.Interrupt()
    #     elif event_id == ID_EVAL and self.active_child:
    #         # Eval selected text (expression) in debugger running context
    #         arg = self.active_child.GetSelectedText()
    #         val = self.debugger.current.Eval(arg)
    #         dlg = wx.MessageDialog(self, "Expression: %s\nValue: %s" % (arg, val), 
    #                                "Debugger Quick Eval",
    #                                wx.ICON_INFORMATION | wx.OK )
    #         dlg.ShowModal()
    #         dlg.Destroy()
    #     elif event_id == ID_JUMP and self.debugging_child:
    #         # change actual line number (if possible)
    #         lineno = self.debugging_child.GetCurrentLine()
    #         if self.debugger.current.Jump(lineno) is not False:
    #             self.debugging_child.SynchCurrentLine(lineno)
    #         else:
    #             print("Fail!")
    #     elif event_id == ID_CONTINUETO and self.debugging_child:
    #         # Continue execution until we reach selected line (temp breakpoint)
    #         lineno = self.debugging_child.GetCurrentLine()
    #         filename = self.debugging_child.GetFilename()
    #         self.debugger.current.Continue(filename=filename, lineno=lineno)


    def delete_all_breakpoints(self, evt):
        doc.delete_all_breakpoints()

    def start_debugger(self, evt=None):
        self.debugger = Debugger(doc)
        glb.MBR.rebuild_menubar(self)
        self.debugger.start()

    def stop_debugger(self, evt=None):
        # if self.debugger:
        self.debugger.quit()
        glb.MBR.rebuild_menubar(self)
        self.debugger = None

    def enable_breakpoint(self, evt, lin=None):
        lin = doc.CurrentLine if lin is None else lin

        # force breakpoint list control creation
        glb.SPN.SetSelection(SPT.BPT.idx)

        # update doc map panel/control
        # if (ctl := gui.get_spt('DCM')):
        #     ctl.Refresh()  # force 'doc map' update

        msk = doc.MarkerGet(lin)
        DBG('BPT', msk)

        if not (msk & MRK['BPT']['MSK']):
            return

        # find bp line number in list control
        for idx in range((ctl := gui.get_spt('BPT')).ItemCount):
            lbl = ctl.GetItem(idx, 3)  # 4th column: source line
            if int(lbl.Text) != lin + 1:
                continue
            DBG('BPT', 'Found @%d' % idx, lbl.Text)
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

            DBG('BPT', f'BP {bpn}: disabled' if ena == 'Yes' else f'BP {bpn}: enabled')
            break

    def goto_breakpoint(self, evt):
        cur = doc.CurrentLine

        # force panel visibility
        if glb.CFG['Breakpoint']['ShowPanel']:
            if not is_shown('SPN'):
                self.toggle_panel(evt, 'SPN', -1)
            if not is_shown('BPT'):
                glb.SPN.SetSelection(SPT.BPT.idx)

        if (id_ := evt.Id) == MI['BPT_NXT']:
            DBG('BPT', '  Next breakpoint')
            lin = doc.MarkerNext(cur + 1, MRK['BPT']['MSK'])
        elif id_ == MI['BPT_PRV']:
            DBG('BPT', '  Previous breakpoint')
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

        dbf.FOCUS(doc)

    def run_module(self, evt):
        not_implemented(evt)

    def toggle_breakpoint(self, evt, lin=None):
        lin = doc.CurrentLine if lin is None else lin

        # no breakpoint at blank/comment line
        if not doc.is_valid_breakpoint(lin):
            return

        # force breakpoint list control creation
        glb.SPN.SetSelection(SPT.BPT.idx)

        # update doc map panel/control
        # if (ctl := gui.get_spt('DCM')):
        #     ctl.Refresh()  # force 'doc map' update

        msk = doc.MarkerGet(lin)
        DBG('BPT', msk)

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
        (ctl := gui.get_spt('BPT')).update(doc)
