#!/usr/bin/python

import wx

from common.util import is_shown
from conf.debug import DBG, DEBUG
from const.common import SASH_POS
from const import glb
from const.sidepanel import SPT
# import gui


#DONE, create one base class 'Splitter' with inheritance, code redundancy gone
class Splitter(wx.SplitterWindow):

    __slots__ = ['CFG', 'prt', 'pnl', 'tlw', 'swap']

    def __init__(self, prt, pnl, orient, gravity):
        self.sec = glb.CFG['Splitter']

        sty = wx.SP_NO_XP_THEME  # sty  = 0
        sty += wx.BORDER_STATIC  if self.sec['Border'] else wx.BORDER_NONE
        sty += wx.SP_LIVE_UPDATE if self.sec['LiveUpdate'] else 0
        super().__init__(prt, style=sty, name=pnl)

        self.prt = prt
        self.pnl = pnl
        self.orient = orient
        self.SetSashGravity(gravity)

        self.swap = False
        self.SetMinimumPaneSize(10)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO,  self.UpdateSize() -> MIGHT solve 'sidepanel' sash/panes resize flicker issue.
#                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#       CAUSES any PENDING SIZING of the SASH and CHILD PANES to take place IMMEDIATELY.
#       Such resizing normally takes place in idle time, in order to wait for layout to
#       be completed. However, this can cause unacceptable flicker as the panes are
#       resized after the window has been shown. To work around this, you can perform
#       window layout (for example by sending a size event to the parent window), and
#       then call this function, before showing the top-level window.
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


######################
# temporary code: SASH
######################
        # print(self.DefaultSashSize)
        # print(self.SashSize)
        # self.SetSashSize(25)
        # print(self.DefaultSashSize)
        # print(self.SashSize)
        # self.SetSashGravity(1.0)  # keep sash in place when resizing
######################
# temporary code: SASH
######################

        self.binds()

    def binds(self):
        if self.sec['SashDoubleClickIsClose']:
            self.Bind(wx.EVT_SPLITTER_DCLICK, lambda e: glb.TLW.toggle_panel(e, self.pnl))

        self.Bind(wx.EVT_ENTER_WINDOW, self.tooltip)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.on_sash_pos_changing)

        if not self.sec['LiveUpdate']:
            # prevent flicker when dragging sash: temporarily disable event processing
            self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_sash_pos_changed)
            self.Bind(wx.EVT_MOTION, self.on_motion)

        # self.Bind(wx.EVT_LEFT_DOWN, self._on_click)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # fnc = self._set_sidepanel_sash
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: double click sash centres sash
    # def _set_sidepanel_sash(self, evt):
    #     wid = self.Window1.Size.x + self.Window2.Size.x
    #     glb.SPL['SPN'].SetSashPosition(wid / 2)
    #     print(self.Window1.Size.x)
    #     print(self.Window2.Size.x)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def on_sash_pos_changing(self, evt):
        # besides 'search results', searchpanel/ruler sashes may NOT move...
        if self.pnl in {'SCH', 'RLR'}:
            if not (self.pnl == 'SCH' and glb.SCH.mode == 'RES'):
                evt.Veto()
                return
            glb.SPN.Update()  # update side panel
        elif self.pnl in {'CCX'}:
            if is_shown('DCM'):
                # only update a change of every 5 pixels for better response
                if evt.SashPosition % 5 == 0:
                    (ctl := glb.DOC.spt_lst[SPT.DCM.idx]).Refresh()  # force 'doc map' update
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # else:
        #     if is_shown('DCM'):
        #         print('DCM Update', evt.SashPosition)
        #         glb.SPL['SPN'].SetSashPosition(evt.SashPosition)
        #         glb.SPN.Refresh()  # update side panel
        #         glb.SPN.Update()  # update side panel
        #         # self.Refresh()
        #         # self.Update()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if DEBUG['SAS']:
            # print('on_sash_pos_changing: evt.Id=[%6d], self.Id=[%6d]' % (evt.Id, self.Id))
#FIX, works for SASH_POS['SPN'] only
            pos = self.prt.ClientSize.x - evt.SashPosition
            if pos == SASH_POS[self.pnl]: print('EQUAL')
            print(f'SashPos[{self.pnl}] = {evt.SashPosition:4}')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def on_sash_pos_changed(self, evt):
        # enable event processing when dragging ends
        for win in {'NBK', 'CCX', 'RLR', 'SCH', 'SPN', 'DOC'}:
            getattr(glb, win).SetEvtHandlerEnabled(True)

    def on_motion(self, evt):
        evt.Skip()
        # discard when not dragging
        if not (evt.Dragging() and evt.LeftIsDown()):
            return

        # disable event processing when dragging starts
        for win in {'NBK', 'CCX', 'RLR', 'SCH', 'SPN', 'DOC'}:
            getattr(glb, win).SetEvtHandlerEnabled(False)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def tooltip(self, evt):
        ttp = ''
        if self.sec['SashDoubleClickIsClose']:
            ttp += 'Double click closes panel'
        if self.pnl not in {'SCH', 'RLR'} or self.pnl == 'SCH' and glb.SCH.mode == 'RES':
            ttp += '\n' if len(ttp) else ''
            ttp += 'Drag moves sash'
        self.SetToolTip(ttp)

    # def _on_click(self, evt):
    #     if self.pnl == 'SCH':
    #         spl = glb.SPL['SCH']
    #         print(' SCH')
    #     elif self.pnl == 'SPN':
    #         spl = glb.SPL['SPN']
    #         print(' SPN')
    #     elif self.pnl == 'CCX':
    #         spl = glb.SPL['CCX']
    #         print(' CCX')
    #     elif self.pnl == 'RLR':
    #         spl = glb.SPL['RLR']
    #         print(' RLR')

    #     print(f'SashPos[{self.pnl}] = {spl.SashPosition:4}')

    #     if spl.SashPosition < 700:
    #         spl.SetSashPosition(2 if spl.swap else -2)
    #     else:
    #         spl.SetSashPosition(300 if spl.swap else -300)

    def set_windows(self, win1, win2):
        self.win1 = win1
        self.win2 = win2
        self.dft_win = win2 if self.pnl in {'SCH', 'SPN'} else win1

    def split_windows(self, sash_pos=0):
        fnc = self.SplitHorizontally if self.orient else self.SplitVertically
        fnc(self.win1, self.win2, sash_pos)

    def swap_windows(self):
        self.win1, self.win2 = self.win2, self.win1
        # self.swap = not self.swap

    def unsplit_windows(self):
        self.Unsplit(self.dft_win)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# class EditorSplitterPanel(wx.Panel):
#     """"""

#     #----------------------------------------------------------------------
#     def __init__(self, prt, dnm, fnm, fbs, ext):
#         """Constructor"""
#         wx.Panel.__init__(self, prt)

#         self.spl = gui.Splitter(self, 'EDT', False, 0.5)  # vertical (Notebook/Editor page)
#         self.spl.SetMinimumPaneSize(20)
#         self.spl.SetSashPosition(glb.NBK.Rect.Width // 2)

#         # assign editor windows to splitter
#         self.txt1 = gui.Editor(self.spl, [dnm, fnm, fbs, ext])  # main doc
#         self.txt2 = gui.Editor(self.spl, [dnm, fnm, fbs, ext])  # 2nd view of main doc

# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         self.txt1.AddRefDocument(self.txt1.DocPointer)
#         self.txt2.SetDocPointer(self.txt1.DocPointer)
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#         self.spl.set_windows(self.txt1, self.txt2)
#         self.spl.split_windows()
#         # glb.SPL['EDT'] = ##

#         bxv = wx.BoxSizer(wx.VERTICAL)
#         bxv.Add(self.spl, 1, wx.EXPAND)
#         self.SetSizer(bxv)

# #INFO, logic for returning panel and main doc moved to this (separate) method
# #INFO, URL=https://docs.quantifiedcode.com/python-anti-patterns/correctness/explicit_return_in_init.html
#     @property
#     def doc(self):
#         return self.spl.Window1
