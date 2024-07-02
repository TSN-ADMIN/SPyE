#!/usr/bin/python

import wx
from wx import stc

from common.util import drop_shadow, get_char_pos
from conf.debug import dbf
from const.editor import MGN
from const import glb
import gui
import mix

def add_doc_view(doc, stc_obj=None, is_dcm=False):
    sec = glb.CFG['DocMap']
    sec_pvw = glb.CFG['CodePreview']
    sec_mgn = glb.CFG['Margin']

    # create extra view, referencing current/main editor doc
    doc.AddRefDocument(doc.DocPointer)
    stc_obj.SetDocPointer(doc.DocPointer)

    # set zoom level: for 'doc map' only
    if is_dcm:
        stc_obj.SetZoom(-10)
        stc_obj.SetExtraAscent(0)
        stc_obj.SetExtraDescent(-1)

    if not stc_obj.IsDoubleBuffered():
        stc_obj.SetDoubleBuffered(True)  # ensure smooth drawing

    stc_obj.UsePopUp(False)  # disable popup menu

    if is_dcm:
        mlh = sec['MarkerLineHighlight']  # marker line background colour
        stc_obj.SetMarginWidth(MGN['NUM'], 0)
        stc_obj.SetMarginWidth(MGN['SYM'], 0 if mlh else 1)
    else:
        mgn = sec_pvw['Margin']
        stc_obj.SetMarginWidth(MGN['NUM'], sec_mgn['LineNumberWidth'] if mgn else 0)
        stc_obj.SetMarginWidth(MGN['SYM'], sec_mgn['SymbolWidth'] if mgn else 0)
    stc_obj.SetMarginWidth(MGN['FOL'], 0)

    stc_obj.SetIndentationGuides(stc.STC_IV_NONE)

    # no scrollbars
    stc_obj.SetUseHorizontalScrollBar(False)
    stc_obj.SetUseVerticalScrollBar(False)
    stc_obj.SetScrollWidthTracking(False)

    # hide caret
    stc_obj.SetCaretWidth(0)
    stc_obj.SetReadOnly(True)
#FIX, main doc's read-only seems to be 'True', so set it 'False'
    doc.SetReadOnly(False)

    stc_obj.styling(doc.lexer, doc.lng_typ, doc.lng_nam, doc.lng_mni)
    # stc_obj.Refresh()
    # stc_obj.Update()


class DragZone:

    __slots__ = ['sec', 'bmp', 'pos']

    def __init__(self):
        self.sec = glb.CFG['DocMap']
        self.bmp = None
        self.pos = wx.Point(0, 0)

    def contains(self, pt):
        return self.get_rct().Contains(pt)

    def create(self, siz, lbl=''):
        # limit zone size
        min_siz = 3
        siz = wx.Size(max(min_siz, siz.x), max(min_siz, siz.y))

        # prepare memory bitmap for drawing
        mdc = wx.MemoryDC()
        self.bmp = wx.Bitmap(siz)
        mdc.SelectObject(self.bmp)
        mdc.Clear()

        __ = self.sec

        # zone surface
        mdc.SetPen(wx.Pen(__['ZoneRectLineColour'], __['ZoneRectLineWidth'], __['ZoneRectLineStyle']))
        clr_lst = [int(__['ZoneFillColour'][i:i + 2], 16) for i in (1, 3, 5)]  # (r, g, b)
        clr_lst.append(__['ZoneFillAlpha'])  # transparency -> (r, g, b, a)
        mdc.SetBrush(wx.Brush(clr_lst))
        if __['ZoneRectRounded']:
            mdc.DrawRoundedRectangle(0, 0, *siz, __['ZoneRectRoundedRadius'])
        else:
            mdc.DrawRectangle(0, 0, *siz)

        # calc centre point
        x, _, w, h = self.get_rct()
        mid = h // 2

        # zone line, centred
        if __['ZoneCentreLine']:
            lft = (x, mid)
            rit = (w, mid)
            clr = __['ZoneCentreLineColour']
            wid = __['ZoneCentreLineWidth']
            sty = __['ZoneCentreLineStyle']
            mdc.SetPen(wx.Pen(clr, wid, sty))
            mdc.DrawLine(lft, rit)

        # zone dot, centred
        if __['ZoneCentreDot']:
            clr = __['ZoneCentreDotColour']
            rad = __['ZoneCentreDotRadius']
            mdc.SetPen(wx.Pen(clr, 1))
            mdc.SetBrush(wx.Brush(clr, wx.BRUSHSTYLE_TRANSPARENT))
            mdc.DrawCircle(w // 2, mid, rad)

#FIX, sec['DocMap']['Edge...'], fine tuning, EdgeTextPosition etc..
        # zone text, top/bottom indicator
        if __['EdgeTextIndicator'] and lbl:
            mdc.SetBackgroundMode(wx.PENSTYLE_SOLID)  # wx.PENSTYLE_TRANSPARENT
            mdc.SetFont(wx.Font(__['EdgeTextFontSize'], wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, __['EdgeTextFont']))
            mdc.SetTextForeground(__['EdgeTextForeColour'])
            mdc.SetTextBackground(__['EdgeTextBackColour'])
            if lbl == 'top':
                txt = __['EdgeTextTop']
                y   = 5
            elif lbl == 'bot':
                txt = __['EdgeTextBottom']
                y   = siz.y - mdc.GetTextExtent(txt).y - 5
            x = siz.x - mdc.GetTextExtent(txt).x - 5
            mdc.DrawText(txt, x, y)

        mdc.SelectObject(wx.NullBitmap)

    def draw(self, dc):
        self.set_transparency(self.sec['ZoneFillAlpha'])
        dc.DrawBitmap(self.bmp, self.get_rct()[:2])

    def get_rct(self):
        return wx.Rect(self.pos, self.bmp.Size)

    def set_transparency(self, alpha=0x80):
        dbf.TIMER('setalpha')
        img = self.bmp.ConvertToImage()
        if not img.HasAlpha():
            img.InitAlpha()
            w = self.sec['ZoneRectLineWidth']
            [img.SetAlpha(x, y, alpha) for x in range(w, img.Width - w) for y in range(w, img.Height - w)]
            self.bmp = img.ConvertToBitmap()
        dbf.TIMER('setalpha', 'STOP')


########################################################################################
######              (8)         DOC MAP           (extracted from 'sidepanel.py') ######
########################################################################################

# @dbf.method_calls()
class DocMap(gui.Editor, mix.Help):

    __slots__ = ['prt', 'doc', 'zone', 'sec', 'drg_pos_map', 'drg_pos_zone' ]

    def __init__(self, prt, doc):
        self.sec = glb.CFG['DocMap']
        self.sec_pvw = glb.CFG['CodePreview']
        super().__init__(prt, [doc.dnm, doc.fnm, doc.fbs, doc.ext])
        mix.Help.__init__(self)
        self.prt = prt
        self.doc = doc  # main editor doc

        # prevent zoom event from firing
        self.Bind(stc.EVT_STC_ZOOM, None)

        self.zone = DragZone()
        self.update_zone()
        self.cod_pvw = None

        # click/drag start position relative to map and zone respectively
        self.drg_pos_map = self.drg_pos_zone = wx.Point(0, 0)

        add_doc_view(doc, self, is_dcm=True)  # init 'doc map' editor control

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, INCORRECT ZONE POSITION at startup/init (try: Ctrl+Up/Down)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#DONE, hack: known CAUSE of bind CONFLICT -> inheriting 'gui.Editor' ... OOPS!)
        self.binds_hack()  # '_hack' suffix prevents conflict w/ 'gui.Editor.binds'

    def binds_hack(self):
        self.prt.Bind(wx.EVT_SIZE, self.resize)
        self.doc.Bind(stc.EVT_STC_UPDATEUI, self.doc_pos_changed)
        self.doc.Bind(stc.EVT_STC_MODIFIED, self.doc_pos_changed)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'DCM'))
        self.Bind(stc.EVT_STC_PAINTED, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.left_down)
        self.Bind(wx.EVT_LEFT_UP, self.left_up)
        self.Bind(wx.EVT_MOTION, self.on_motion)

        # disable map text selection and mouse wheel
        self.Bind(wx.EVT_LEFT_DCLICK, lambda e: e.Skip)

        # always force focus on main editor doc
        self.Bind(wx.EVT_SET_FOCUS, lambda e: dbf.FOCUS(self.doc))

        # 'code preview' binds
        self.Bind(wx.EVT_ENTER_WINDOW, self.create_code_preview)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.destroy_code_preview)
        self.Bind(wx.EVT_SET_CURSOR, self.update_code_preview)
        self.Bind(wx.EVT_MOUSEWHEEL, self.wheel_code_preview)

    def create_code_preview(self, evt):
        if not self.sec_pvw['Enable'] or self.cod_pvw:
            return
        self.cod_pvw = CodePreview(self, self.doc)

    def destroy_code_preview(self, evt):
        if self.sec_pvw['Enable'] and self.cod_pvw:
            self.cod_pvw.destroy()
            self.cod_pvw = None

    def update_code_preview(self, evt):
        evt.Skip()
        if not self.cod_pvw:
            return
        if not self.sec_pvw['Enable']:
            self.destroy_code_preview(evt)
            return
        self.cod_pvw.update()

    def wheel_code_preview(self, evt):
        if not self.sec_pvw['Enable'] or not self.cod_pvw:
            return
        self.cod_pvw.wheel(evt)

    def calc_heights(self):
        # calculate doc/map height values (in pixels)
        doc_buf_hgh = self.LineCount * self.TextHeight(0)     # doc buffer; includes invisible lines
        self.clt_hgh = self.ClientSize.y                      # client window
        self.max_hgh = min(doc_buf_hgh, self.clt_hgh)         # zone boundary
        self.zone_hgh = self.zone.get_rct()[3]                # zone object
        self.scl_hgh = max(.1, self.max_hgh - self.zone_hgh)  # zone scroll range

    def doc_pos_changed(self, evt):
        # discard when marking matches OR styling tokens (huge speed up)
        if self.doc.mch_active or any(list(self.doc.sty_active.values())):
            return

        # copy text selection(s) to map
        cnt = self.doc.Selections
        for s in range(cnt):
            self.doc.RotateSelection()
            self.AddSelection(self.doc.GetSelectionNCaret(s), self.doc.GetSelectionNAnchor(s))

        self.calc_heights()
        top_y = self.doc.FirstVisibleLine * self.get_doc_scroll_ratio()
        top_lin = self.get_top_line(top_y) + 1
        self.sync_map(top_lin, top_y)
        evt.Skip()

    def get_doc_scroll_ratio(self):
        ratio = self.doc.LineCount - self.doc.LinesOnScreen()
        # prevent division by zero
        if ratio == 0:
            ratio = -1
        return self.scl_hgh / ratio

    def get_top_line(self, top_y):
        top_lin = top_y / self.scl_hgh * (self.LineCount - self.LinesOnScreen())
        return round(top_lin)

    def get_top_y(self, posY):
        # drag zone's top Y coordinate
        top_y = posY - self.drg_pos_zone.y
        # adjust when mouse released past top/bottom edge
        top_y = max(top_y, 0)
        top_y = min(top_y, self.scl_hgh)
        return top_y

    def left_down(self, evt):
        pos = evt.Position

        # clicked drag zone?
        if self.zone.contains(pos):
            # set map/zone start positions
            self.drg_pos_map = pos
            self.drg_pos_zone = self.drg_pos_map - self.zone.pos
            self.tooltip()
            self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

            if not self.sec['SnapCursorAtDragStart'] and not self.HasCapture():
                self.CaptureMouse()

            if self.cod_pvw:
                self.cod_pvw.Hide()  # hide when zone drag starts

            # prevent interfering with drag
            self.doc.Bind(stc.EVT_STC_UPDATEUI, None)
            return

        # centre drag zone around clicked line
        self.calc_heights()
        clk_lin = self.FirstVisibleLine - (self.zone_hgh // 2 - pos.y) // self.TextHeight(0)
        top_y = clk_lin * self.get_doc_scroll_ratio()
        top_y = min(top_y, self.scl_hgh)
        top_lin = self.get_top_line(top_y)
        self.sync_doc(top_lin, top_y)
        self.sync_map(top_lin, top_y)

    def left_up(self, evt):
        self.dcm_drg_active = False  # not used
        self.tooltip(False)
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

        if not self.sec['SnapCursorAtDragStart'] and self.HasCapture():
            self.ReleaseMouse()

        if self.cod_pvw:
            self.cod_pvw.Show()  # show when zone drag ends

        self.doc.Bind(stc.EVT_STC_UPDATEUI, self.doc_pos_changed)

    def on_motion(self, evt):
        # discard when not dragging
        if not (evt.Dragging() and evt.LeftIsDown()):
            return

        self.dcm_drg_active = True  # not used

#NOTE, force invalidate for display performance
        self.Refresh()
        self.doc.Refresh()

        self.calc_heights()
        top_y = self.get_top_y(evt.Position.y)

        # align position with drag start
        pos = (self.drg_pos_map.x, top_y + self.drg_pos_zone.y)
        top_lin = self.get_top_line(top_y)
        self.sync_doc(top_lin, top_y)
        self.SetFirstVisibleLine(top_lin)  # in doc map
        self.tooltip()

        # adjust mouse pointer position
        if self.sec['SnapCursorAtDragStart']:
            self.WarpPointer(*pos)

        self.zone.pos = (0, top_y)

#NOTE, force immediate paint for display performance
        self.Update()
        self.doc.Update()

    def on_paint(self, evt):
        dc = wx.PaintDC(self)
        self.update_zone()
        self.zone.draw(dc)

    def resize(self, evt):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#HACK, sync current doc object with doc map
        self = gui.get_spt('DCM')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.SetSize(self.prt.Size)
        self.update_zone()
        # keep zone inside map
        x, y, _, h = self.zone.get_rct()
        if y + h > self.ClientSize.y - self.TextHeight(0):
            self.SetFirstVisibleLine(self.FirstVisibleLine + 1)
            self.zone.pos = (x, y - self.TextHeight(0))
        # self.Refresh()

    def sync_doc(self, top_lin, top_y):
        if self.max_hgh < self.clt_hgh:
            top_lin = 0

        self.doc.SetFirstVisibleLine(round(top_lin + top_y // self.TextHeight(0)))

    def sync_map(self, top_lin, top_y):
#NOTE, force invalidate for display performance
        # self.Refresh()

        # adjust map top line
        if top_lin == 1:
            top_lin = 0
        self.SetFirstVisibleLine(top_lin)
        self.zone.pos = (0, round(top_y))

#NOTE, force immediate paint for display performance
        self.Update()
        # self.update_zone()

    def tooltip(self, show=True):
        # show top line number tooltip during drag
#NOTE, 'SetDelay' is global, so when used, restore it
        # wx.ToolTip.SetDelay(0)
        ttp = 'Top Line: %7d' % (self.doc.FirstVisibleLine + 1) if show else ''
        self.SetToolTip(ttp)
#NOTE, 'SetDelay' is global, so when used, restore it
        # wx.ToolTip.SetDelay(glb.CFG['ToolTip']['DelayShow'])

    def update_zone(self, evt=None):
        txt = ''
        if self.doc.FirstVisibleLine == 0:
            txt = 'top'
            # self.SetCursor(wx.Cursor(self.sec['CursorTypeHover']))
        elif self.LineCount - self.LinesOnScreen() == self.FirstVisibleLine:
            txt = 'bot'
            # self.SetCursor(wx.Cursor(self.sec['CursorTypeEdge']))
        self.zone.create(wx.Size(self.ClientSize.x, self.doc.LinesOnScreen() * self.TextHeight(0)), txt)


# @dbf.method_calls(exclude=['update'])
class CodePreview(wx.MiniFrame):

    __slots__ = ['dcm', 'doc', 'sec', 'stc_pvw', 'bxv']

    def __init__(self, prt, doc):
        self.sec = glb.CFG['CodePreview']
        wid = self.sec['Width']  # preview:editor width ratio (0.00 to 1)
        hgh = self.sec['Height']  # num preview lines (use line height in pixels)
        self.cap = self.sec['Caption']
        sty = wx.CAPTION if self.cap else 0
        super().__init__(prt, wx.ID_ANY, style=sty, name='mnfCodePreview')

        self.dcm = prt  # doc map
        self.doc = doc  # main editor doc
        self.prv_ttl = None  # title and/or tooltip text

        self.SetBackgroundColour(self.sec['BorderColour'])  # '#C6E2FF'

        if self.sec['DropShadow'] and not self.cap:
            drop_shadow(self)

        self.stc_pvw = gui.Editor(self, [doc.dnm, doc.fnm, doc.fbs, doc.ext])

        add_doc_view(doc, self.stc_pvw)  # init 'code preview' editor control

        # set initial size
        csy = self.Size.y - self.ClientSize.y  # caption height
        _w = self.doc.Size.x * wid  # preview:editor width ratio
        _h = self.stc_pvw.TextHeight(0) * hgh + csy
        self.SetSize(_w, _h)

#HACK, use sizer to simulate border (width/colour)
        self.bxv = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.bxv)

        # always force focus on main editor doc
        self.Bind(wx.EVT_SET_FOCUS, lambda e: dbf.FOCUS(self.doc))


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #     self.Bind(stc.EVT_STC_PAINTED, self.on_paint)

    # def on_paint(self, evt):
    #     dc = wx.PaintDC(self.stc_pvw)

    #     # prepare memory bitmap for drawing
    #     mdc = wx.MemoryDC()
    #     bmp = wx.Bitmap(self.stc_pvw.Size)
    #     mdc.SelectObject(bmp)
    #     mdc.Clear()

    #     __ = glb.CFG['DocMap']

    #     # calc centre point
    #     x, _, w, h = self.stc_pvw.GetRect()
    #     mid = h // 2

    #     # zone line, centred
    #     if __['ZoneCentreLine']:
    #         lft = (x, mid)
    #         rit = (w, mid)
    #         clr = __['ZoneCentreLineColour']
    #         wid = __['ZoneCentreLineWidth']
    #         sty = __['ZoneCentreLineStyle']
    #         mdc.SetPen(wx.Pen(clr, wid, sty))
    #         mdc.DrawLine(lft, rit)

    #     # zone dot, centred
    #     if __['ZoneCentreDot']:
    #         clr = __['ZoneCentreDotColour']
    #         rad = __['ZoneCentreDotRadius']
    #         mdc.SetPen(wx.Pen(clr, 1))
    #         mdc.SetBrush(wx.Brush(clr, wx.BRUSHSTYLE_TRANSPARENT))
    #         mdc.DrawCircle(w // 2, mid, rad)

    #     mdc.SelectObject(wx.NullBitmap)

    #     img = bmp.ConvertToImage()
    #     if not img.HasAlpha():
    #         img.InitAlpha()
    #         w = __['ZoneRectLineWidth']
    #         for x in range(w, img.Width - w):
    #             for y in range(w, img.Height - w):
    #                 img.SetAlpha(x, y, 0x80)
    #         bmp = img.ConvertToBitmap()

    #     dc.DrawBitmap(bmp, self.stc_pvw.GetRect()[:2])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def destroy(self):
        self.Hide()
        if self.sec['DropShadow'] and not self.cap:
            drop_shadow(self, show=False)

    def update(self):

        self.Freeze()

        # to caption or not to ..
        self.cap = self.sec['Caption']
        sty = self.WindowStyle
        sty = sty | wx.CAPTION if self.cap else sty & ~wx.CAPTION
        self.WindowStyle = sty

        # to border or not to ..
        border = self.sec['BorderWidth'] if self.sec['Border'] else 0
        self.bxv.Detach(self.stc_pvw)
        self.bxv.Add(self.stc_pvw, 1, wx.ALL|wx.EXPAND, border)
        self.Layout()

        if self.sec['DropShadow'] and not self.cap:
            drop_shadow(self)

        # pos/line under cursor, preview width/height, update caption
        _x, _y, pos = get_char_pos(self.dcm, close=False)
        _w, _h, lin = *self.Size, self.stc_pvw.LineFromPosition(pos)
        fr = self.stc_pvw.FirstVisibleLine + 1
        to = fr + self.stc_pvw.LinesOnScreen()  # - 1
        ttl = f'Line range: {fr} - {to}, {to - fr + 1} lines, centred at: {lin + 1}'

        self.SetTitle(ttl)

        # set tooltip text when changed (avoid flicker)
        if ttl != self.prv_ttl:
            self.dcm.SetToolTip(None if self.cap else ttl)

        self.prv_ttl = ttl

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # prepare for drawing
        dc = wx.WindowDC(self)

        __ = glb.CFG['DocMap']

        # calc centre point
        txh = self.doc.TextHeight(0)
        x, _, w, h = wx.Rect(self.Size)
        mid = h // 2 - txh // 2

        # zone line, centred
        if __['ZoneCentreLine']:
            lft = (x, mid+4)
            rit = (w, mid+4)
            clr = 'RED'  # __['ZoneCentreLineColour']
            wid = 1        # __['ZoneCentreLineWidth']
            sty = 101      # __['ZoneCentreLineStyle']
            dc.SetPen(wx.Pen(clr, wid, sty))
            dc.DrawLine(lft, rit)
            dc.DrawLine((lft[0], lft[1] + txh), (rit[0], rit[1] + txh))

        # # zone dot, centred
        # if __['ZoneCentreDot']:
        #     clr = __['ZoneCentreDotColour']
        #     rad = __['ZoneCentreDotRadius']
        #     dc.SetPen(wx.Pen(clr, 1))
        #     dc.SetBrush(wx.Brush(clr, wx.BRUSHSTYLE_TRANSPARENT))
        #     dc.DrawCircle(w // 2, mid, rad)
        #     # dc.DrawCircle(w // 2, mid + txh, rad)

        # # dc.SelectObject(wx.NullBitmap)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # _dx, _dy = self.doc.Size
        # self.SetTitle(f'{_x=}, {_y=}, {_w=}, {_h=}, {lin=}')
        # self.SetTitle(f'{_dx=}, {_dy=}, {_w=}, {_h=}, {lin=}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # centre line under cursor
        self.stc_pvw.GotoLine(lin)
        self.stc_pvw.VerticalCentreCaret()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, correct height to FULLY view ALL visible lines (NOT PARTIALLY)
        # pos_ = self.stc_pvw.PointFromPosition
        # print(f'{pos_(74059) = }')  # pos_(74059) = wx.Point(0, 928)
        # print(f'{pos_(74084) = }')  # pos_(74084) = wx.Point(0, 944) -> + 16
        # print(f'{pos_(74086) = }')  # pos_(74086) = wx.Point(0, 960) -> + 16
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        # calculate new position/size
        wid = self.sec['Width']
        dmh = self.dcm.Size.y  # doc map height
        ofs = self.doc.Size.x * (1 - wid)  # x offset from editor top left

        # tiny corrections to ..
        ofs = ofs + 6 if self.cap else ofs  # .. align with side panel sash
        dif = 6 if self.cap else 3  # .. stay within doc map bounds
        pos = self.doc.ClientToScreen(ofs, dif + _y * (dmh - self.Size.y) / dmh)

        self.SetPosition(pos)
        self.SetSize(self.doc.Size.x * wid, self.Size.y)

        self.Thaw()

        # cursor over drag zone?
        if self.dcm.zone.contains((_x, _y)):
            self.Show(self.sec['ShowOverZone'])
        else:
            self.Show()

    def wheel(self, evt):
        _rot = evt.WheelRotation  # is multiple of 120 (+/- delta)
        _fwd = bool(_rot > 0)

        ctrl, shift = evt.controlDown, evt.shiftDown

        # discard when no valid modifier pressed
        if not (ctrl or shift):
            return

        # preview position/size
        _x, _y, _w, _h = self.Rect

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, correct height to FULLY view ALL visible lines (NOT PARTIALLY); see bottom editor line
        # _h += self.sec['BorderWidth'] * 2
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # editor (doc) position/size
        pos, siz = self.doc.ClientToScreen(self.doc.Position), self.doc.Size

        # resize value/minimum in pixels for width or line height
        rsz = 20 if shift else 2 * self.stc_pvw.TextHeight(0)

        # resize preview by: editor width ratio (Ctrl+Shift or Shift) AND/OR line height (Ctrl)
        if ctrl and shift:
            # change width (20 pixels/step)
            if (_fwd and _w >= siz.x) or (not _fwd and _w <= rsz):
                return
            _x = _x - rsz if _fwd else _x + rsz
            _w = _w + rsz if _fwd else _w - rsz
            if _x < pos.x:
                _x = pos.x
            if _w > siz.x:
                _w = siz.x
            if _w < rsz:
                _w = rsz
            self.SetPosition((_x, _y))
            self.SetSize(_w, _h)
            self.sec['Width'] = self.Size.x / siz.x  # update config
        elif shift:
            # change width (min or max per step)
            if _fwd and _w >= siz.x:
                return
            _x = pos.x if _fwd else pos.x + siz.x - rsz
            _w = siz.x if _fwd else rsz
            self.SetPosition((_x, _y))
            self.SetSize(_w, _h)
            self.sec['Width'] = self.Size.x / siz.x  # update config
        elif ctrl:
            # change height (2 lines/step)
            if (_fwd and _h >= siz.y) or (not _fwd and _h <= rsz):
                return
            _h = _h + rsz if _fwd else _h - rsz
            if _h > siz.y:
                _h = siz.y
            if _h < 2 * rsz:
                _h = 2 * rsz
            self.SetSize(_w, _h)
            csy = self.Size.y - self.ClientSize.y  # caption height
            self.sec['Height'] = (self.Size.y - csy) // (rsz // 2)  # update config

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # print(f'{self.sec["Width"] = :0.2f}, {self.sec["Height"] = }')
        # print(f'{self.Size.y =}, {self.ClientSize.y= }')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
