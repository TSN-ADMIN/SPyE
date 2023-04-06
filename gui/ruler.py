#!/usr/bin/python

# copied from UliPad, (modified) module RulerCtrl.py
#INFO, URL=https://github.com/limodou/ulipad/tree/master/plugins/ruler

#       Programmer:     limodou
#       E-mail:         limodou@gmail.com
#
#       Copyleft 2006 limodou
#
#       Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#       $Id$
#   Update by Claudio Grondi 2006/08/14 :
#     - changed the design and added column numbers each tenth column
#     - improved synchronization of the column indicator with the cursor
#     - partially fixed the problem with wrong ruler positioning - now it
#   appears where it should,
#       but when margin width changes it still gets out of sync (re-sync by
#   switching it off/on)
#     - Alt+R switches now the ruler on/off
#     still ToDo:
#       - implementing of repainting the ruler on changes of margin width
#       - perfect full synchronization of column indicator with the cursor
#       - implementing resizing of the ruler on font and font size changes
#           (currently it works properly only with 'Courier New - 12')

import wx

from common.util import set_font
from conf.debug import DEBUG
from const import glb
import gui


class Ruler(wx.Panel):
    def __init__(self, prt, size=(-1, 10), offset=0, font=None):
        self.sec = glb.CFG['Ruler']
        super().__init__(prt, wx.ID_ANY, size=size, name='Ruler')

        self.col = -1
        self.size = size
        self.offset = offset
        self.set_font(wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False) if not font else font)

        self.clr_bgd = self.sec['BackColour']
        self.max_tkh = self.sec['TickMaxHeight']
        self.clr_tkl = self.sec['TickLargeColour']
        self.clr_tkm = self.sec['TickMediumColour']
        self.clr_tks = self.sec['TickSmallColour']
        self.fnt_siz = self.sec['TextFontSize']
        self.clr_txt = self.sec['TextColour']
        self.clr_crt = self.sec['CaretColour']
        self.typ_crt = self.sec['CaretType']

        self.binds()

    def binds(self):
        self.Bind(wx.EVT_LEFT_DOWN, self.goto_column)
        self.Bind(wx.EVT_MOTION, self.move_column_indicator)
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self.Refresh())
        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'RLR'))
        self.Bind(wx.EVT_PAINT, self.draw)

    def draw(self, evt):
        self.prv_x = None  # erase last indicator

        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(self.clr_bgd))
        dc.Clear()

        mdc = wx.MemoryDC()
        mdc.SelectObject(wx.Bitmap(*self.Size))

        # adjust ruler offset for all zoom levels (doc char width)
        offset = self.offset - self.chr_wid + 5

        pnl_wid, pnl_hgh = self.Size
        pos_y = pnl_hgh - 1  # draw ruler close to sash

        # horizontal base line
        if self.sec['LineBottom']:
            dc.SetPen(wx.Pen(self.sec['LineColour']))
            dc.DrawLine(offset, pos_y, pnl_wid, pos_y)

        # draw ticks and text labels (from offset to panel width, step char width)
        for idx, pos_x in enumerate(range(offset, pnl_wid, self.chr_wid)):
            # LEFT tick
            if idx == 0:
                dc.SetPen(wx.Pen(self.sec['TickLeftColour']))
                for i in range(self.sec['TickLeftHeight']):
                    dc.DrawLine(pos_x, pos_y - i, pos_x + 3, pos_y - i)
            # LARGE tick
            elif idx % 10 == 0:
                dc.SetPen(wx.Pen(self.clr_tkl))
                dc.DrawLine(pos_x, pos_y, pos_x, pos_y - (self.max_tkh))

                # text label, adjust position to font size
                if self.fnt_siz:
                    siz = self.fnt_siz
                    txt_x = pos_x - siz + 3
                    txt_y = pos_y - siz - 3
                    dc.SetFont(wx.Font(siz, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
                    dc.SetTextForeground(self.clr_txt)
                    dc.DrawText(f'{idx}', txt_x, txt_y)
            # MEDIUM tick
            elif idx % 5 == 0:
                dc.SetPen(wx.Pen(self.clr_tkm))
                dc.DrawLine(pos_x, pos_y, pos_x, pos_y - (self.max_tkh - (self.max_tkh // 3)))
            # SMALL tick
            else:
                dc.SetPen(wx.Pen(self.clr_tks))
                dc.DrawLine(pos_x, pos_y, pos_x, pos_y - (self.max_tkh // 3))

        mdc.SelectObject(wx.NullBitmap)

        self.set_column(self.col)

    def goto_column(self, evt):
        x = evt.Position[0]
        col = (x - self.offset + self.chr_wid - 5) // (self.chr_wid)

        # clicked beyond left tick?
        if col < 1:
            col = 1

        # set caret in current document
        doc = glb.NBK.CurrentPage
        lin = doc.CurrentLine

        # clicked beyond line length?
        if col > doc.GetLineLength(lin):
            doc.LineEnd()
        else:
            doc.GotoPos(doc.PositionFromLine(lin) + col - 1)

        # remove clutter when caret overlaps indicator
        self.Refresh()

        if DEBUG['RLR']: print(f'goto_column: {x = }, {col = }')

    def move_column_indicator(self, evt):
        dc = wx.ClientDC(self)
        x = evt.Position[0]
        y = self.Size[1]
        col = (x - self.offset + self.chr_wid - 5) // (self.chr_wid)

        # move beyond left tick?
        if col < 1:
            col = 1

        # get doc line
        doc = glb.NBK.CurrentPage
        lin = doc.CurrentLine

        # move beyond line length?
        if col > doc.GetLineLength(lin):
           col = doc.GetLineLength(lin) + 1

        # draw tiny indicator
        dc.SetPen(wx.Pen('#00FFFF', 3))  # use inverse of 'RED' with XOR
        dc.SetLogicalFunction(wx.XOR)

        # erase last indicator
        if self.prv_x:
            dc.DrawLine(self.prv_x, 0, self.prv_x, y)
            # self.draw_on_parent(self.prv_x)

        dc.DrawLine(x, 0, x, y)

        self.SetToolTip(f'Click for column {col}')

        self.prv_x = x

        # self.draw_on_parent(x)

    def set_column(self, col):
        def __draw_caret(x, y, siz, typ, clr):
            dc = wx.ClientDC(self)
            dc.SetPen(wx.Pen(clr))

            if typ.endswith('_SMALL'):
                y -= 6  # decrease caret height

            if DEBUG['RLR'] > 1: print(f'ruler (caret type): [{typ}]')

            if 'TRIANGLE' in typ:
                for i in range(siz):
                    if DEBUG['RLR'] > 1: print(f'  [{x - i:3}, {y - i:2}] -> [{x + i:3}, {y - i:2}]')
                    dc.DrawLine(x - i, y - i, x + i, y - i)
            elif 'BLOCK' in typ:
                for i in range(siz):
                    dc.DrawLine(x, y - i, x + 8, y - i)
            elif 'LINE' in typ:
                for i in range(siz):
                    dc.DrawLine(x - 1, y - i, x + 2, y - i)
            else:
#############################
# temporary code: CARET = '!'
#############################
                dc.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Courier New'))
                dc.SetTextForeground('RED')
                dc.DrawText('!', x, y - siz)
#############################
# temporary code: CARET = '!'
#############################

        def __get_col_xy(col):
            __, y = self.Size
            # adjust caret offset for all zoom levels (doc char width)
            x = self.offset + (col * self.chr_wid) - self.chr_wid + 5
            y -= 12  # draw caret close to sash
            return x, y

        # clear caret at old column
        x, y = __get_col_xy(self.col)
        __draw_caret(x, y, 15, self.typ_crt, self.clr_bgd)

        # draw caret at new column
        self.col = col
        x, y = __get_col_xy(self.col)
        __draw_caret(x, y, 15, self.typ_crt, self.clr_crt)

    def set_offset(self, offset):
        if self.offset != offset:
            if DEBUG['RLR']: print(f'  ruler (delta offset): {self.offset - offset:+5}')
            self.offset = offset
            self.Refresh()

#FIX: function of this code
    def set_font(self, fnt, wid=8):
        # siz = wx.Size((wid, wid))
        # siz.Scale(1.0945, 1.0945)
        # fnt.SetPixelSize(siz)
        fnt.SetPointSize(wid)
        self.SetFont(fnt)
        # self.chr_wid = self.CharWidth - 1

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#INFO, copied 'draw_on_parent' from "Python\Lib\site-packages\wx\lib\agw\rulerctrl.py"

    # def draw_on_parent(self, x):
    #     """
    #     Actually draws the thin line over the drawing parent window.

    #     :param `indicator`: the current indicator, an instance of :class:`Indicator`.

    #     :note: This method is currently not available on wxMac as it uses :class:`ScreenDC`.
    #     """

    #     if not (doc := get_doc()): return

    #     prt_rct = doc.GetClientRect()

    #     dc = wx.ScreenDC()
    #     dc.SetLogicalFunction(wx.INVERT)
    #     dc.SetPen(wx.Pen('RED', 1))
    #     dc.SetBrush(wx.TRANSPARENT_BRUSH)

    #     y1 = prt_rct.y
    #     x1 = x2 = x
    #     y2 = prt_rct.height
    #     x1, y1 = doc.ClientToScreen((x1, y1))
    #     x2, y2 = doc.ClientToScreen((x2, y2))

    #     dc.DrawLine(x1, y1, x2, y2)
    #     dc.SetLogicalFunction(wx.COPY)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
