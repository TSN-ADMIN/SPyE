#!/usr/bin/python

import wx

from common.doc import get_doc
from common.util import is_shown
from conf.debug import DEBUG
from const.common import SASH_POS
from const import glb
from const.sidepanel import SPT


#DONE, create one base class 'Splitter' with inheritance, code redundancy gone
class Splitter(wx.SplitterWindow):

    __slots__ = ['CFG', 'prt', 'pnl', 'tlw', 'swap']

    def __init__(self, prt, pnl, orient, gravity):
        sty = wx.SP_NO_XP_THEME  # sty  = 0
        sty += wx.BORDER_STATIC  if glb.CFG['Splitter']['Border'] else wx.BORDER_NONE
        sty += wx.SP_LIVE_UPDATE if glb.CFG['Splitter']['LiveUpdate'] else 0
        super().__init__(prt, style=sty, name=pnl)

        self.prt = prt
        self.pnl = pnl
        self.orient = orient
        self.SetSashGravity(gravity)

        self.swap = False
        self.SetMinimumPaneSize(10)

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
        if glb.CFG['Splitter']['SashDoubleClickIsClose']:
            if self.pnl == 'SCH':
                fnc = lambda e: glb.TLW.toggle_panel(e, 'SCH', -1)
            elif self.pnl == 'RLR':
                fnc = lambda e: glb.TLW.toggle_panel(e, 'RLR', 1)
            elif self.pnl == 'SPN':
                fnc = lambda e: glb.TLW.toggle_panel(e, 'SPN', -1)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # fnc = self._set_sidepanel_sash
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            elif self.pnl == 'CCX':
                fnc = lambda e: glb.TLW.toggle_panel(e, 'CCX', 1)
            elif self.pnl == 'EDT':
                fnc = lambda e: glb.TLW.toggle_panel(e, 'EDT', 1)
            self.Bind(wx.EVT_SPLITTER_DCLICK, fnc)
        self.Bind(wx.EVT_ENTER_WINDOW, self.tooltip)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.on_sash_pos_changing)
        self.UpdateSize()
        # self.Bind(wx.EVT_LEFT_DOWN, self._on_click)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: double click sash centres sash
    # def _set_sidepanel_sash(self, evt):
    #     wid = self.Window1.Size[0] + self.Window2.Size[0]
    #     glb.SPL['SPN'].SetSashPosition(wid / 2)
    #     print(self.Window1.Size[0])
    #     print(self.Window2.Size[0])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def on_sash_pos_changing(self, evt):
        # besides 'search results', searchpanel/ruler sashes may NOT move...
        if self.pnl in ['SCH', 'RLR']:
            if not (self.pnl == 'SCH' and glb.SCH.mode == 'RES'):
                evt.Veto()
                return
            glb.SPN.Update()  # update side panel
        elif self.pnl in ['CCX']:
            if is_shown('DCM'):
                # only update a change of every 5 pixels for better response
                if evt.SashPosition % 5 == 0:
                    (ctl := get_doc().spt_lst[SPT.DCM.idx]).Refresh()  # force 'doc map' update
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
            pos = self.prt.ClientSize[0] - evt.SashPosition
            if pos == SASH_POS[self.pnl]: print('EQUAL')
            print(f'SashPos[{self.pnl}] = {evt.SashPosition:4}')

    def tooltip(self, evt):
        ttp = ''
        if glb.CFG['Splitter']['SashDoubleClickIsClose']:
            ttp += 'Double click closes panel'
        if self.pnl not in ['SCH', 'RLR'] or self.pnl == 'SCH' and glb.SCH.mode == 'RES':
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
        self.dft_win = win2 if self.pnl in ('SCH', 'SPN') else win1

    def swap_windows(self):
        self.win1, self.win2 = self.win2, self.win1
        # self.swap = not self.swap

    def split_windows(self, sash_pos=0):
        fnc = self.SplitHorizontally if self.orient else self.SplitVertically
        fnc(self.win1, self.win2, sash_pos)

    def unsplit_windows(self):
        self.Unsplit(self.dft_win)
