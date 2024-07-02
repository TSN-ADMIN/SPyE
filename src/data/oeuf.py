#!/usr/bin/python

# try:
#     from data.images import catalog as PNG
# except ImportError as e:
#     from data.images import catalog as PNG

import wx

from .images import catalog as PNG


class Oeuf(wx.Frame):
    def __init__(self, prt):
        sty = wx.FRAME_SHAPED | wx.BORDER_SIMPLE | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP
        super().__init__(prt, wx.ID_ANY, "Oeuf", style=sty)

        self.Bind(wx.EVT_LEFT_UP,  self.on_exit)
        self.Bind(wx.EVT_RIGHT_UP, self.on_exit)
        self.Bind(wx.EVT_KEY_UP,   self.on_exit)
        self.Bind(wx.EVT_PAINT,    self.on_paint)

        self.bmp = PNG['OEUF'].Bitmap
        w, h = self.bmp.Width, self.bmp.Height
        self.SetClientSize((w, h))
        self.Centre()
        self.Show()

    def on_paint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)

    def on_exit(self, evt):
        self.Close()

#---------------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.App(redirect=False, filename=None)
    win = Oeuf(None)
    win.Show()
    app.MainLoop()
