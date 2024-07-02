#!/usr/bin/python

import wx

from ._load import _load
from common.util import curdoc, curdoc_class, set_icon
from const import glb
from const.menubar import MI


@_load
@curdoc_class(curdoc)
class Macro:


    def macro_edit(self, evt):
        print(doc.macro_to_source())


    def macro_play(self, evt):
        # at least play once
        cnt = 1
#DONE, Play Multiple Times Dialog
        if evt.Id == MI['MAC_PLM']:
            with wx.TextEntryDialog(self, 'Enter count:', 'Play macro multiple times', '1') as dlg:
                set_icon(dlg)
                if (res := dlg.ShowModal()) == wx.ID_CANCEL:
                    return
                cnt = int(dlg.Value)

        wx.BeginBusyCursor()
        # doc.BeginUndoAction()
        for __ in range(cnt):
            doc.macro_play(evt)
            # doc.Update()
        # doc.EndUndoAction()
        wx.EndBusyCursor()

        if cnt > 1:
            glb.SBR.push_text(f'Macro executed {cnt} times')


    def macro_start(self, evt):
        doc.macro_start(evt)
        # label: rec -> stop
        self.mac_rec_lbl = glb.MBR.GetLabel(MI['MAC_REC'])
        glb.MBR.SetLabel(MI['MAC_REC'], glb.MBR.GetLabel(MI['MAC_STP']))


    def macro_stop(self, evt):
        doc.macro_stop(evt)
        # label: stop -> rec
        glb.MBR.SetLabel(MI['MAC_REC'], self.mac_rec_lbl)
        del self.mac_rec_lbl


    def macro_TEST(self, evt):
        doc.macro_TEST(evt)
