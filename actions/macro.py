#!/usr/bin/python

import wx

from ._load import _load
from common.doc import get_doc
from common.util import set_icon
from const import glb
from const.menu import MI


@_load
class Macro:


    def macro_edit(self, evt):
        if not (doc := get_doc()): return
        print(doc.macro_to_source())


    def macro_play(self, evt):
        if not (doc := get_doc()): return
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
        # doc.EndUndoAction()
        wx.EndBusyCursor()

        if cnt > 1:
            glb.SB.push_text(f'Macro executed {cnt} times')


    def macro_start(self, evt):
        if not (doc := get_doc()): return
        doc.macro_start(evt)
        # label: rec -> stop
        self.mac_rec_lbl = glb.MB.GetLabel(MI['MAC_REC'])
        glb.MB.SetLabel(MI['MAC_REC'], glb.MB.GetLabel(MI['MAC_STP']))


    def macro_stop(self, evt):
        if not (doc := get_doc()): return
        doc.macro_stop(evt)
        # label: stop -> rec
        glb.MB.SetLabel(MI['MAC_REC'], self.mac_rec_lbl)
        del self.mac_rec_lbl


    def macro_TEST(self, evt):
        if not (doc := get_doc()): return
        doc.macro_TEST(evt)
