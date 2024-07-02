#!/usr/bin/python

import wx

from common.util import set_font
from const import glb
from const.menubar import MI
from data.images import catalog as PNG
import gui


class InfoBar(wx.InfoBar):

    # __slots__ = ['CFG', 'sec', 'prt', 'prv_tim', 'tmr_cfd', 'ico_psw']

    def __init__(self, prt):  #, *args, **kwargs):
        self.sec = glb.CFG['InfoBar']
        super().__init__(prt)
        self.SetName('InfoBar')
        self.prt = prt

        self.create()

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.SetShowHideEffects(wx.SHOW_EFFECT_EXPAND, wx.SHOW_EFFECT_EXPAND)
        self.SetEffectDuration(100)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # timer to dismiss infobar after a set delay
        self.tmr_ibr = wx.Timer(self, wx.ID_ANY)

        self.Bind(wx.EVT_TIMER, self.dismiss)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'IBR'))

    def on_paint(self, evt):
        dc = wx.PaintDC(self)
        dc.SetBrush(wx.Brush('BLACK', wx.BRUSHSTYLE_TRANSPARENT))
        dc.SetPen(wx.Pen('#B4CCE6', 2))
        # dc.SetPen(wx.Pen('SLATE BLUE', 3))
        dc.DrawRectangle(0, 0, *self.Size)

    def create(self):
        self.SetEffectDuration(0)
        self.SetShowHideEffects(wx.SHOW_EFFECT_NONE, wx.SHOW_EFFECT_NONE)

        # self.SetEffectDuration(200)
        # self.SetShowHideEffects(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM, wx.SHOW_EFFECT_SLIDE_TO_TOP)

        self.dismiss(None)  # reset colours

        set_font(self, self.sec['Font'], self.sec['FontSize'], self.sec['FontBold'], self.sec['FontItalic'])

        # top level window sizer
        self.prt.Sizer = wx.BoxSizer(wx.VERTICAL)
        if self.sec['Position'] == 'TOP':
            self.prt.Sizer.Add(self, 0, wx.EXPAND)
            self.prt.Sizer.Add(glb.SPL['SCH'], 1, wx.EXPAND)
        else:
            self.prt.Sizer.Add(glb.SPL['SCH'], 1, wx.EXPAND)
            self.prt.Sizer.Add(self, 0, wx.EXPAND)

#HACK, remove default close (X) button
        # if not self.sec['CloseButton']:
        #     self.FindWindow('button').Destroy()

    def dismiss(self, evt):
        self.prt.Freeze()
        self.Dismiss()
        # self.SetForegroundColour(self.sec['ForeColour'])
        # self.SetBackgroundColour(self.sec['BackColour'])
        self.prt.Thaw()

    def info_msg(self, msg, typ=None, autohide=True):
        # discard when infobar disabled
        if not glb.MBR.IsChecked(MI['LAY_IBR']):
            return

        flg = wx.ICON_NONE

        if typ == 'INFO':
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, key 'InformationBackColour' in config file
            flg = wx.ICON_INFORMATION
            self.SetForegroundColour('WHITE')
            self.SetBackgroundColour('FOREST GREEN')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        elif typ == 'WARN':
            flg = wx.ICON_WARNING
            self.SetBackgroundColour(self.sec['WarningBackColour'])
        elif typ == 'ERROR':
            flg = wx.ICON_ERROR
            self.SetBackgroundColour(self.sec['ErrorBackColour'])

        self.prt.Freeze()
#INFO, 'flg' -> wx.ICON_(NONE|INFORMATION|QUESTION|WARNING|ERROR)
        self.ShowMessage(msg, flg)

#HACK, replace/resize default icon in sizer
        if (bmp := self.FindWindow('staticBitmap')):
            bmp.SetName('icoInfoBar')
        # elif (bmp := self.FindWindow('icoInfoBar')):
        #     bmp.SetBitmap(PNG['app_16'].Bitmap)

        if (stt := self.FindWindow('staticText')):
            stt.SetName('sttInfoBar')

        self.Sizer.Layout()
        self.prt.Thaw()

        if autohide:
            self.tmr_ibr.StartOnce(self.sec['DelayHide'])

#     def info_msg(self, msg, flg, fgc=None, bgc=None, autohide=True):
#         # discard when infobar disabled
#         if not glb.MBR.IsChecked(MI['LAY_IBR']):
#             return

#         fgc = self.sec['ForeColour'] if fgc is None else fgc
#         bgc = self.sec['BackColour'] if bgc is None else bgc
#         self.SetForegroundColour(fgc)
#         self.SetBackgroundColour(bgc)

#         self.prt.Freeze()
# #INFO, 'flg' -> wx.ICON_(NONE|INFORMATION|QUESTION|WARNING|ERROR)
#         self.ShowMessage(msg, flg)

# #HACK, replace/resize default icon in sizer
#         if (bmp := self.FindWindow('staticBitmap')):
#             bmp.SetName('icoInfoBar')
#         # elif (bmp := self.FindWindow('icoInfoBar')):
#         #     bmp.SetBitmap(PNG['app_16'].Bitmap)

#         if (stt := self.FindWindow('staticText')):
#             stt.SetName('sttInfoBar')

#         self.Sizer.Layout()
#         self.prt.Thaw()

#         if autohide:
#             self.tmr_ibr.StartOnce(self.sec['DelayHide'])
