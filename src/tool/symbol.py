#!/usr/bin/python

import glob
from pathlib import Path
import re
import sys

import wx
from wx import stc
# from wx.lib.agw.hyperlink import HyperLinkCtrl, EVT_HYPERLINK_LEFT
from wx.adv import HyperlinkCtrl, EVT_HYPERLINK
import wx.html
from wx.lib.scrolledpanel import ScrolledPanel

import extern.fuzzysearch as FUZ
# from common.file import open_files
# from common.file import split_path
from common.path import resolve_path
from common.util import drop_shadow, get_closest_index, rs_, make_modal, set_font
from conf.debug import DBG, DEBUG, dbf
from const.app import EXE, OPT_CTAGS, OUT_CTAGS, LBX_NAV_KEYS
from const.editor import MGN
from const import glb
from const.symbol import SBW_TMPFIL_NAME, SYMBOL
from .ctags import CtagsParser
import gui


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
INDEX_EXCLUDE_FIL_SUBSTRINGS = ['data\\images', 'extern', 'DEV']
INDEX_EXCLUDE_WORDS = ['self', 'DEBUG', 'print', 'doc', '__init__']
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#####
#
#  XXXXXX                  XX                                XXX   XX  XXX XXXXX   XXX XXX
#   X    X           X      X                               X   X   X   X    X      X   X
#   X    X           X      X                              X     X  XX  X    X      X   X
#   X    X XXX XXX  XXXX    X XX    XXXXX  XX XX           X     X  XX  X    X       X X
#   XXXXX   X   X    X      XX  X  X     X  XX  X          X     X  X X X    X       X X
#   X       X   X    X      X   X  X     X  X   X          X     X  X  XX    X        X
#   X        X X     X      X   X  X     X  X   X          X     X  X  XX    X        X
#   X        X X     X  X   X   X  X     X  X   X           X   X   X   X    X   X    X
#  XXXX       X       XX   XXX XXX  XXXXX  XXX XXX           XXX   XXX  X  XXXXXXX   XXX
#            X
#          XX
#
#####


class SymbolIndex:

    # __slots__ = [...]

    def __init__(self):
        ...
        # self.create('INIT')

    def create(self):
        dbf.TIMER('index')
        DBG('SIX', f'* Create [Python] symbol index:')

        # reset symbol index dicts/counts
        for typ in SYMBOL:
            SYMBOL[typ][4].clear()
            SYMBOL[typ][3] = 0

        # triple quotes
        tsq = "'''"  # single
        tdq = '"""'  # double
        trq_reg = re.compile(rf'({tsq}|{tdq})')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, use all notebook tabs (open documents)
#FIX, call 'create_symbol_index' when doc(s) opened/closed

        # fil_lst = glob.glob('**/*.py', recursive=True)

        fil_lst = [doc.pnm for __, doc in glb.NBK.open_docs()]
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        flc = 0  # file count

        # walk the (open) file list
        for fil in fil_lst:
            # exclude filename substrings
            if any(d in fil for d in INDEX_EXCLUDE_FIL_SUBSTRINGS):
                continue

            # process file
            with open(fil) as fil:
                flc += 1
                lnc = 0  # line count
                pnm = str(resolve_path(fil.name))  # pathname
                DBG('SIX==1', f'{flc:3d}.  {pnm}')
                in_trq = False

                try:
                    # process line
                    for lin in fil:
                        lnc += 1
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                        lin = lin.rstrip()
                        stp = lin.strip()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                        # skip empty line or single line comment
                        if not stp or stp[0] == '#':
                            continue

                        # skip/strip end of line comment
                        elc = lin.find('#')
                        if elc > 0:
                            DBG('SIX==3', lin[elc:])
                            lin = lin[:elc].rstrip()
                            stp = lin[:elc].strip()
                            DBG('SIX==3', ' ', stp)

                        # skip triple quote comment
                        for __ in trq_reg.findall(lin):
                            if in_trq:
                                DBG('SIX==4', f'{pnm:24}: {lnc:4d}, [ {stp} ]')
                                in_trq = False
                            else:
                                in_trq = True

                        if in_trq:
                            DBG('SIX==4', f'{pnm:24}: {lnc:4d}, [ {stp} ]')
                            continue

                        # update symbol index
                        for typ in SYMBOL:
                            # index this symbol type?
                            if not glb.CFG['SymbolIndex'][f'Include{typ}']:
                                continue
                            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                            # build reference index later
                            # if typ == 'REF':
                            #     continue
                            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                            SYMBOL[typ][3:5] = self.parse_line(typ, pnm, lin, lnc)

                except Exception as e:
                    print(f'{fil.name}\nUnexpected error: {sys.exc_info()[0]}\n{e}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if glb.CFG['SymbolIndex'][f'IncludeREF']:
            dfn_dct, ref_dct, wrd_dct = SYMBOL['DFN'][4], SYMBOL['REF'][4], SYMBOL['WRD'][4]

            # build references from definitions/words dicts
            for wrd in dfn_dct:
                if wrd not in wrd_dct:
                    continue
                for fil in dfn_dct[wrd]:
                    if fil not in wrd_dct[wrd]:
                        continue

                    dif = set(wrd_dct[wrd][fil]).difference(set(dfn_dct[wrd][fil]))
                    if not dif:
                        continue

                    # print(wrd_dct[wrd][fil])
                    # print(dfn_dct[wrd][fil])
                    # print('Diff', sorted(dif))
                    # print()

                    SYMBOL['REF'][3] += len(dif)  # add to total count

                    # ref_dct.setdefault(wrd, {fil: None})
                    if wrd not in ref_dct:
                        ref_dct[wrd] = {fil: None}

                    ref_dct[wrd][fil] = list(dif)

                del wrd_dct[wrd]

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # remove words already existing in some other dicts
        wrd_dct = SYMBOL['WRD'][4]

        for typ in {'IMP', 'VAR', 'QTS'}:
            for wrd in SYMBOL[typ][4]:
                if wrd in wrd_dct:
                    del wrd_dct[wrd]

#FIX, subtract deleted count per type above from 'SYMBOL['WRD'][3]''
        cnt = 0
        for wrd in wrd_dct:
            for fil in wrd_dct[wrd]:
                cnt += len(wrd_dct[wrd][fil])

        SYMBOL['WRD'][3] = cnt  # set total count

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        DBG('SIX', (dbf.SYMBOL_INDEX_SUMMARY, flc))

        dbf.TIMER('index', 'STOP')

        # return list of indexes
        del typ
        return [SYMBOL[typ][4] for typ in SYMBOL]

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def parse_line(self, typ, pnm, lin, lnc):

        sym_cnt, sym_dct, sym_reg, reg_grp = SYMBOL[typ][3:]
        nam, stp = typ.lower(), lin.strip()
        dif = len(lin) - len(stp)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if DEBUG['SIX'] == 5:
            # control (white)space between matches
        #@@@@@@@@@@@@@@@@@@
        # cnt = prv_pos = 0
        #@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        for res in re.finditer(sym_reg, lin):
            sym, col = res.group(reg_grp), res.start(reg_grp) + 1

#FIX, needs better coding...
            # discard reference when its definition exists
            if typ == 'REF' and sym in SYMBOL['DFN'][4] and pnm in SYMBOL['DFN'][4][sym] and (lnc, col) in SYMBOL['DFN'][4][sym][pnm]:
                continue

            if typ == 'WRD':
                fnd = False
                for t in {'DFN', 'REF', 'IMP', 'VAR'}:
                    if sym in SYMBOL[t][4] and pnm in SYMBOL[t][4][sym] and (lnc, col) in SYMBOL[t][4][sym][pnm]:
                        fnd = True
                        break
                if fnd:
                    continue

            sym_cnt += 1
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            lin = stp
            # print(f'[{nam}]::[{sym}]::[{pnm}]::[{dif if typ == "WRD" else ""}]')

            #@@@@@@@@@@@@@@@@@@
            # DBG('SIX==5', (dbf.SYMBOL_INDEX_MATCHES, pnm, lin, lnc, nam, dif, cnt, prv_pos, sym, col), end='')
            #@@@@@@@@@@@@@@@@@@
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # if typ == 'WRD' and sym in INDEX_EXCLUDE_WORDS:
            #     print('exclude', sym, lnc, pnm)
            #     continue
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # if typ == 'QTS' and sym[0] == '"':
            #     print(sym)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # strip begin/end quotes
            if typ == 'QTS':
                sym = sym[1:len(sym)-1]

            if sym not in sym_dct:
                sym_dct[sym] = dict([(pnm, [(lnc, col)])])
            elif pnm not in sym_dct[sym]:
                sym_dct[sym][pnm] = [(lnc, col)]
            else:
                sym_dct[sym][pnm].append((lnc, col))

        #@@@@@@@@@@@@@@@@@@
        # DBG('SIX==5', '\n' if cnt else '', end='')
        #@@@@@@@@@@@@@@@@@@

        return sym_cnt, sym_dct
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class SymbolPopup(wx.Dialog):

    __slots__ = ['CFG', 'sec', 'doc', 'tlw', 'max_wid', 'max_hgh', 'tmr_pos', 'bxv', ]

    def __init__(self, doc, wrd, cwl, style):
        self.sec = glb.CFG['SymbolPopup']
        super().__init__(doc, style=wx.BORDER_SIMPLE)  # wx.DIALOG_NO_PARENT
        self.doc = doc
        self.sym_pvw = None

        dbf.SYMBOL_POPUP(glb.TLW, wrd=wrd, total=True, verbose=False)

        if self.sec['DropShadow']:
            drop_shadow(self)

        self.doc.spu_active = True

        # number of URLs and popup size
        self.url_cnt = self.max_wid = self.cur_hgh = 0
        self.max_hgh = 255

        # monitor mouse pointer position
        self.tmr_pos = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.mouse_timer)
        self.tmr_pos.Start(50)  # milliseconds

        # add panel with labels
        scl_pnl = ScrolledPanel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)  # BORDER_RAISED
        scl_pnl.SetBackgroundColour(self.sec['PanelBackColour'])

        # populate panel/sizer
        self.bxv = wx.BoxSizer(wx.VERTICAL)

        if self.sec['ShowSymbol']:
            # word symbol
            stt_wrd = wx.StaticText(scl_pnl, label=f' {wrd} ')
            stt_wrd.SetForegroundColour(self.sec['SymbolForeColour'])
            stt_wrd.SetBackgroundColour(self.sec['SymbolBackColour'])
            set_font(stt_wrd, face=self.sec['SymbolFont'], siz=10)  # Consolas
            self.add_to_popup_size(stt_wrd)
            self.bxv.Add(stt_wrd, 0, wx.TOP|wx.BOTTOM|wx.LEFT, border=5)

        # add description and URL's per symbol type for word
        for typ in SYMBOL:
            self.populate_panel(scl_pnl, wrd, cwl, typ)

        # discard popup when no URLs
        if not self.url_cnt:
            return

        scl_pnl.SetSizer(self.bxv)
        scl_pnl.SetupScrolling()

        self.Bind(wx.EVT_CHAR_HOOK, self.on_escape)

#FIX, calculate size (width), allow max. height 12 URL's
        if self.url_cnt < 12:
            self.cur_hgh += 2 * 15  # correction: add size of 2 URLs
        siz = (self.max_wid + 35, self.cur_hgh)
        self.SetSize(siz)

        # show symbol popup at cursor position
        pos = wx.GetMousePosition()
        # pos[1] += doc.TextHeight(0)  # keep 'popup line' visible

        # adjust popup position at client edge
        dw, dh = wx.DisplaySize()
        x, y, cw, ch = *pos, *self.ClientSize
        if x + cw >= dw:
            x -= cw
        if y + ch >= dh:
            y -= ch + 10

        self.SetPosition(wx.Point(x, y))
        self.ShowModal()

    def add_to_popup_size(self, obj):
        dc = wx.ClientDC(self)
        dc.SetFont(obj.Font)
        # calculate font size in pixels
        w, h = dc.GetTextExtent(obj.Label)
        if w > self.max_wid:
            self.max_wid = w
        if self.cur_hgh + h < self.max_hgh:
            self.cur_hgh += h
        # print(w, h, obj.Label)

    def populate_panel(self, prt, wrd, cwl, typ):
        # symbol type index
        idx = SYMBOL[typ][4]

        if wrd not in idx:
            return

        # symbol type description
        if self.sec['ShowSymbolType']:
            dsc = SYMBOL[typ][0]  # convenient short naming (dsc)
            stt_typ = wx.StaticText(prt, label=f'{dsc}(s):')
            stt_typ.SetForegroundColour(self.sec['SymbolTypeForeColour'])
            set_font(stt_typ, face=self.sec['SymbolTypeFont'], siz=10)  # Consolas
            self.add_to_popup_size(stt_typ)
            self.bxv.Add(stt_typ, 0, wx.TOP|wx.BOTTOM|wx.LEFT, border=5)
            DBG('SPU', f'\n{dsc}(s)')

#NOTE, prevent circular dependency
        from common.file import split_path

        pvw = True if glb.CFG['SymbolPreview']['Enable'] else False

        # symbol type hyperlinks for word
        for fil in sorted(idx[wrd]):
            for pos in sorted(idx[wrd][fil], key=lambda itm: itm[0]):
                # discard hyperlink for current symbol
                if pos == cwl:
                    continue
                self.url_cnt += 1
                lin, col = pos
                url = f'{fil}|{lin}|{col}'
                __, fnm, __, __ = split_path(fil)
                lbl = f'{fil}:{lin}'
                hyp_url = HyperlinkCtrl(prt, label=lbl, name='HyperlinkCtrl', url=url)
                hyp_url.Bind(wx.EVT_ENTER_WINDOW, self.hover_url_enter if pvw else None)
                hyp_url.Bind(wx.EVT_LEAVE_WINDOW, self.hover_url_leave if pvw else None)
                hyp_url.Bind(EVT_HYPERLINK, self.click_url)
                # hyp_url.SetNormalColour('GREEN')
                # hyp_url.SetHoverColour('RED')
                # hyp_url.SetToolTip(fil)
                set_font(hyp_url, face=self.sec['HyperlinkFont'], siz=10, bold=True)
                self.add_to_popup_size(hyp_url)
                self.bxv.Add(hyp_url, 0, wx.LEFT, border=5)
                DBG('SPU', url)

        if self.sec['ShowSymbolType']:
            stt_typ.Label = f'{dsc}(s) [{self.url_cnt}]:'

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, create context preview of hovered symbol URL
    def hover_url_enter(self, evt):
        obj = evt.EventObject
        url = obj.URL
        obj.SetBackgroundColour('#E6F2FF')
        obj.Refresh()

        # get filename|line|column
        sep1 = url.find('|')
        sep2 = url.rfind('|')
        fil = url[:sep1]
        lin = int(url[sep1+1:sep2])
        col = int(url[sep2+1:])

        if not self.sym_pvw:
            self.sym_pvw = SymbolPreview(self, fil, lin, col)

        self.sym_pvw.show_file(fil, lin, col)

    def hover_url_leave(self, evt):
        obj = evt.EventObject
        obj.SetBackgroundColour(self.sec['PanelBackColour'])
        obj.Refresh()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def click_url(self, evt):
#NOTE, prevent circular dependency
        from common.file import open_files

        url = evt.URL

        # get filename|line|column
        sep1 = url.find('|')
        sep2 = url.rfind('|')
        fil = url[:sep1]
        lin = int(url[sep1+1:sep2])
        col = int(url[sep2+1:])

        DBG('SPU', f'\nClicked URL: [{fil}]:[{lin}]:[{col}]')

        fil_lst = [[str(resolve_path(fil))]]
        doc = open_files(fil_lst)

        DBG('SPU', f'  realpath = {str(resolve_path(fil))}')
        DBG('SPU', f'   pnm = {doc.pnm}')

        doc.GotoPos(doc.XYToPosition(col - 1, lin - 1))
        if self.sec['CentreCaret']:
            doc.VerticalCentreCaret()
        self.destroy(evt, doc)

#NOTE, works for 'wx.Dialog', does NOT work for 'wx.PopupTransientWindow'
    def on_escape(self, evt):
        if evt.KeyCode == wx.WXK_ESCAPE:
            print('Escape SymbolPopup')
            self.destroy(evt)
#HACK, for a very short time ignore current doc's events so a new popup is not triggered
            self.doc.SetEvtHandlerEnabled(False)
            wx.CallLater(25, self.doc.SetEvtHandlerEnabled, True)
        # evt.Skip()  # for 'PopupTransientWindow'

    def mouse_timer(self, evt):
        z = 20  # extra space outside client rectangle for mouse movement
        rct = wx.Rect(self.Position - (z, z), self.Size + (2*z, 2*z))
        pos = wx.GetMousePosition()
        # print(f'mouse: {pos} ** rect: {rct}')
        if not rct.Contains(pos):
            self.destroy(evt)

    def destroy(self, evt, doc=None):
        if self.sec['DropShadow']:
            drop_shadow(self, show=False)
        self.Destroy()
        self.doc.spu_active = False
        wx.CallLater(50, dbf.FOCUS, self.doc if doc is None else doc)


class SymbolPreview(wx.MiniFrame):

    # __slots__ = ['dcm', 'doc', 'sec', 'stc_pvw', 'bxv']

    def __init__(self, prt, pnm, lin, col):
        self.sec = glb.CFG['SymbolPreview']
        wid = self.sec['Width']  # num cols (col width in pixels)
        hgh = self.sec['Height']  # num lines (line height in pixels)
        self.cap = self.sec['Caption']
        sty = wx.CAPTION if self.cap else 0
        super().__init__(prt, wx.ID_ANY, style=sty, name='mnfSymbolPreview')

        self.SetBackgroundColour(self.sec['BorderColour'])  # '#C6E2FF'

        if self.sec['DropShadow'] and not self.cap:
            drop_shadow(self)

#NOTE, prevent circular dependency
        from common.file import split_path

        dnm, fnm, fbs, ext = split_path(pnm)
        pvw = self.stc_pvw = gui.Editor(self, [dnm, fnm, fbs, ext])

        pvw.SetUseHorizontalScrollBar(False)
        pvw.SetUseVerticalScrollBar(False)

        # disable preview margins
        [pvw.SetMarginWidth(MGN[m], 0) for m in {'NUM', 'SYM', 'FOL'} if not self.sec['Margin']]

        pvw.spu_active = True  # disable 'mark_matches'

        # pvw.Bind(stc.EVT_STC_ZOOM, None)
        # pvw.SetZoom(pvw.Zoom - 2)
        # pvw.SetCaretLineBackground('GREEN')

        self.SetSize(wid * pvw.TextWidth(stc.STC_STYLE_DEFAULT, 'X'),
                50 + hgh * pvw.TextHeight(0))

        # adjust preview position at client edge
        dw, dh = wx.DisplaySize()
        px, py, pw, ph = prt.Rect  # parent popup pos/size
        x, y, w, h = px, py + ph, *self.ClientSize  # preview pos/size

        x = dw - w if x + w > dw else x
        y = py - h if y + h > dh else y

        self.SetPosition(wx.Point(x, y))

#HACK, use sizer to simulate border (width/colour)
        # to border or not to ..
        self.bxv = wx.BoxSizer(wx.VERTICAL)
        border = self.sec['BorderWidth'] if self.sec['Border'] else 0
        self.bxv.Detach(pvw)
        self.bxv.Add(pvw, 1, wx.ALL|wx.EXPAND, border)
        self.Layout()

        self.SetSizer(self.bxv)
        self.Show()

    def show_file(self, pnm, lin, col):
        pvw = self.stc_pvw  # convenient short naming (pvw)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, needs better coding...
#NOTE, prevent circular dependency
        from const.lang import LANG
        from common.file import split_path
        __, __, __, ext = split_path(pnm)
        lng_lst = [e for e in LANG if ext in e[3].split('|')]
        pvw.update_language_styling(lng_lst)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.SetTitle(f'SymbolPreview: {pnm} [{lin=}][{col=}]')
        pvw.ClearAll()
        pvw.LoadFile(pnm)
        pvw.Home()  # ensures 1st column visible
        pvw.GotoPos(pvw.XYToPosition(col - 1, lin - 1))
        pvw.WordRightExtend()
        if self.sec['CentreCaret']:
            pvw.VerticalCentreCaret()
        else:
            pvw.SetFirstVisibleLine(pvw.CurrentLine)
        dbf.FOCUS(pvw)


class SymbolBrowser(wx.Dialog):
    def __init__(self):
        self.sec = glb.CFG['SymbolBrowser']
        sty = wx.BORDER_SIMPLE  # wx.DIALOG_NO_PARENT
        super().__init__(glb.TLW, style=sty)
        self.WindowStyle |= wx.STAY_ON_TOP

        self.doc = glb.NBK.CurrentPage  # .txt1

        # discard caret position history when symbol browsing
        self.doc.cph_sbw_active = True

        # save caret position, first line and selection
        self.doc_pos = self.doc.CurrentPos
        self.doc_top = self.doc.FirstVisibleLine
        self.doc_spos, self.doc_epos = self.doc.GetSelection()

        self.sym_lst = self.create_tags()

        # quit when no symbols
        if not self.sym_lst:
            return

        self.create_widgets()

        self.on_filter(None)

#HACK, force resized listbox when needed
#FIX, 'WXK_BACK' corrupts 'lbx_sym.SetSelection(idx)' below
        # wx.UIActionSimulator().Char(wx.WXK_BACK)

        # get symbol name closest to current line
        cur = self.doc.LineFromPosition(self.doc_pos) + 1
        self.lin_lst = [e[2] for e in self.sym_lst]
        idx = get_closest_index(self.lin_lst, cur)
        self.lbx_sym.SetSelection(idx)

        # highlight/select symbol name
        self.on_select(None)
        dbf.FOCUS(self.lbx_sym)

        gbs = wx.GridBagSizer(vgap=0, hgap=0)
        border = self.sec['BorderWidth']

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # fnt = self.stt_hdr.Font
        # fnt.MakeBold()
        # fnt.SetPointSize(14)
        # self.stt_hdr.SetFont(fnt)

        # gbs.Add(self.stt_hdr, (0, 0), (0, 0), wx.ALL, border)
        # gbs.Add(self.txc_flt, (1, 0), (1, 0), wx.ALL, border)
        # gbs.Add(self.lbx_sym, (2, 0), (2, 0), wx.ALL, border)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        gbs.Add(self.txc_flt, (0, 0), (0, 0), wx.ALL, border)
        gbs.Add(self.lbx_sym, (1, 0), (1, 0), wx.ALL, border)

        self.Sizer = gbs
        self.Sizer.Fit(self)

        make_modal(self, True)
        if self.sec['DropShadow']:
            drop_shadow(self)

        # centre dialog horizontally at top of document
        doc_wid = self.doc.ClientSize.x // 2
        dlg_wid = self.ClientSize.x // 2
        x, y = doc_wid - dlg_wid, self.sec['PositionY']
        self.SetPosition(self.doc.ClientToScreen(x, y))
        self.Show()
        self.binds()

    def binds(self):
        self.btn_ok_.Bind(wx.EVT_BUTTON, self.on_confirm)
        self.btn_esc.Bind(wx.EVT_BUTTON, self.on_exit)
        self.txc_flt.Bind(wx.EVT_KEY_UP, self.on_filter)
        self.txc_flt.Bind(wx.EVT_CHAR, self.on_char)
        self.lbx_sym.Bind(wx.EVT_CHAR, self.on_char)
        self.lbx_sym.Bind(wx.EVT_LISTBOX, self.on_select)
        # self.lbx_sym.Bind(wx.EVT_LEFT_UP, self.on_confirm)
        self.lbx_sym.Bind(wx.EVT_LISTBOX_DCLICK, self.on_confirm)

    def create_widgets(self):
        # symbol names for listbox
        lbx_chc_lst = [e[1] for e in self.sym_lst]

#HACK, map hidden OK button to ENTER key
        self.btn_ok_ = wx.Button(self, wx.ID_OK, size=(0, 0))
        self.btn_ok_.SetDefault()

#HACK, map hidden cancel button to ESCAPE key
        self.btn_esc = wx.Button(self, wx.ID_CANCEL, size=(0, 0))
        self.SetEscapeId(wx.ID_CANCEL)

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # self.stt_hdr = wx.StaticText(self, wx.ID_ANY, 'Enter number:')
        # self.stt_hdr.SetBackgroundColour('#71B3E8')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.txc_flt = wx.TextCtrl(self, wx.ID_ANY, '', size=(330, 35))
        self.lbx_sym = wx.html.SimpleHtmlListBox(self, choices=lbx_chc_lst, size=(330, 250))  #, style=wx.LB_OWNERDRAW)

        # colours and font
        self.SetBackgroundColour(self.sec['BackColour'])
        self.txc_flt.SetBackgroundColour(self.sec['TextCtrlBackColour'])
        self.lbx_sym.SetBackgroundColour(self.sec['ListBoxBackColour'])
        self.lbx_sym.SetSelectionBackground(self.sec['ListBoxSelBackColour'])

        for wgt in (self.txc_flt, self.lbx_sym):
            set_font(wgt, self.sec['Font'], self.sec['FontSize'], self.sec['FontBold'])

    def on_filter(self, evt):
        flt_txt = self.txc_flt.Value

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if flt_txt:
        #     mode = flt_txt[0]
        #     print(mode)
        #     if mode == '@':
        #         self.stt_hdr.Label = 'Symbol Browser'
        #     elif mode == '#':
        #         self.stt_hdr.Label = 'Search Term'
        #     elif mode == ':':
        #         self.stt_hdr.Label = 'Goto Line'
        #     else:
        #         self.stt_hdr.Label = 'NO MODE'
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # populate listbox
        self.lbx_sym.Clear()
        self.lbx_sym.SetItemCount(0)
        self.lin_lst = []
        self.flt_itm_lst = []
        for itm in self.sym_lst:
            nam = itm[1]
            if self.sec['FuzzySearch'] and flt_txt:
                if (res := FUZ.find_best_match(flt_txt, nam)).score >= 0:
                    self.add_symbol(itm, fuzzy_obj=res)
            elif flt_txt in nam:
                self.add_symbol(itm)

        self.lbx_sym.Set(self.flt_itm_lst)
        self.lbx_sym.SetItemCount(len(self.flt_itm_lst))
        # highlight/select symbol name
        if self.lbx_sym.GetCount() > 0:
            self.lbx_sym.SetSelection(0)
            self.on_select(None)

        # resize listbox
        if self.lbx_sym.GetCount() < 10:
            self.lbx_sym.SetSize(330, self.lbx_sym.GetCount() * 26)
        else:
            self.lbx_sym.SetSize(330, 250)
        self.SetSize(-1, 10 + self.txc_flt.Size.y + self.lbx_sym.Size.y)
        return

    def on_char(self, evt):
#HACK, repeat last keypress after focus switch (text control <-> listbox)
        rpt_key = wx.UIActionSimulator()
        if evt.KeyCode in LBX_NAV_KEYS and self.txc_flt.HasFocus():
            if self.lbx_sym.GetCount() > 0:
                dbf.FOCUS(self.lbx_sym)
                rpt_key.Char(evt.KeyCode)
        elif evt.KeyCode not in LBX_NAV_KEYS and self.lbx_sym.HasFocus():
            dbf.FOCUS(self.txc_flt)
            self.txc_flt.SetInsertionPointEnd()
            rpt_key.Char(evt.KeyCode)
#HACK, SHIFT key forces paint at bottom of resized listbox
        rpt_key.Char(wx.WXK_SHIFT)
        evt.Skip()
        return

    def on_select(self, evt):
        # highlight/select line with selected symbol name
        idx = self.lbx_sym.Selection
        lin = self.lin_lst[idx]
        self.doc.GotoLine(lin - 1)
        self.doc.LineEndExtend()
        self.doc.VerticalCentreCaret()

    def on_confirm(self, evt):
        self.cleanup()

    def on_exit(self, evt):
        # ESCAPE clears filter?
        if evt.Id == wx.ID_CANCEL and self.txc_flt.Value:
            self.txc_flt.Value = ''
            dbf.FOCUS(self.txc_flt)
            return
        # restore caret's last position and first line
        self.doc.GotoPos(self.doc_pos)
        self.doc.SetFirstVisibleLine(self.doc_top)
        # restore selection
        if self.doc_spos != self.doc_epos:
            self.doc.SetSelection(self.doc_spos, self.doc_epos)
        self.cleanup()

    def add_symbol(self, itm, fuzzy_obj=None):
        nam, lin, clr = itm[1:]
        if fuzzy_obj:
            nam = FUZ.format(nam, fuzzy_obj, '<font color="black"><b><u>', '</u></b></font>')

        nam = f'<table cellspacing="1" cellpadding="1" border="0" width="99%">' \
              f'<tr><td bgcolor="{clr}" width="8%" align="center"><b>{itm[0]}</b></td>' \
              f'<td><b>{nam}</b></td></tr></table>'

        self.flt_itm_lst.append(nam)
        self.lin_lst.append(lin)

    def cleanup(self):
        self.doc.cph_sbw_active = False
        make_modal(self, False)
        if self.sec['DropShadow']:
            drop_shadow(self, show=False)
        self.Destroy()

    def create_tags(self):
        # save current doc as tmp file
        tmp = f'{SBW_TMPFIL_NAME}.{self.doc.ext}'
        print(tmp)
        res = self.doc.SaveFile(tmp)

        # create/read tags file
        parser = CtagsParser()

        # auxiliary option: including regex search pattern '--excmd=pattern'
        res = parser.parse(f'{EXE["CTAGS"]} -f "{OUT_CTAGS}" {OPT_CTAGS} {tmp}')

        Path(tmp).unlink()

        if not res:
            return False

        # build symbol list (type, name, line, colour)
        sym_lst = []

        for tag in parser.tags:
            kind = tag.fields['kind']

#HACK, assume that 1 indent is 4 spaces wide
            ind = tag.xcmd[2:10]
            # print(f'{tag.xcmd = }')
            if ind.startswith(' '*8):
                lvl = 3
            elif ind.startswith(' '*4):
                lvl = 2
            elif ind.startswith(' '*0):
                lvl = 1
            nam = ' '*2*(lvl - 1) + tag.name

            fld_lst = [nam, int(tag.fields['line'])]
            if  kind == 'class':
                sym_lst.append(['C', *fld_lst, self.sec['ClassBackColour']])
            elif  kind == 'member':
                sym_lst.append(['M', *fld_lst, self.sec['MemberBackColour']])
            elif  kind == 'function':
                sym_lst.append(['F', *fld_lst, self.sec['FunctionBackColour']])

        return sym_lst


class GotoAnything(wx.Dialog):
    def __init__(self):
        self.sec = glb.CFG['GotoAnything']
        sty = wx.BORDER_SIMPLE  # wx.DIALOG_NO_PARENT
        super().__init__(glb.TLW, style=sty)
        self.WindowStyle |= wx.STAY_ON_TOP

        # save current document (page tab)
        self.doc_cur = glb.NBK.CurrentPage  # .txt1

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, refactor 'doc_lst', 'pag_lst'to 'doc_dct'
#INFO, see 'doc_dct = ' in 'list_open_files'
        self.doc_lst = self.create_document_list()
        self.pag_lst = [e[1] for e in self.doc_lst]
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.create_widgets()

        self.on_filter(None)

#HACK, force resized listbox when needed
        wx.UIActionSimulator().Char(wx.WXK_BACK)

        # highlight/select current file name
        self.lbx_ofl.SetSelection(glb.NBK.Selection)
        self.on_select(None)
        dbf.FOCUS(self.lbx_ofl)

        gbs = wx.GridBagSizer(vgap=0, hgap=0)
        border = self.sec['BorderWidth']
        gbs.Add(self.txc_flt, (0, 0), (0, 0), wx.ALL, border)
        gbs.Add(self.lbx_ofl, (1, 0), (1, 0), wx.ALL, border)

        self.Sizer = gbs
        self.Sizer.Fit(self)

        make_modal(self, True)
        if self.sec['DropShadow']:
            drop_shadow(self)

        # centre dialog horizontally at top of document
        doc_wid = self.doc_cur.ClientSize.x // 2
        dlg_wid = self.ClientSize.x // 2
        x, y = doc_wid - dlg_wid, self.sec['PositionY']
        self.SetPosition(self.doc_cur.ClientToScreen(x, y))
        self.Show()

        self.binds()

    def binds(self):
        self.btn_ok_.Bind(wx.EVT_BUTTON, self.on_confirm)
        self.btn_esc.Bind(wx.EVT_BUTTON, self.on_exit)
        self.txc_flt.Bind(wx.EVT_KEY_UP, self.on_filter)
        self.txc_flt.Bind(wx.EVT_CHAR, self.on_char)
        self.lbx_ofl.Bind(wx.EVT_CHAR, self.on_char)
        self.lbx_ofl.Bind(wx.EVT_LISTBOX, self.on_select)
        # self.lbx_ofl.Bind(wx.EVT_LEFT_UP, self.on_confirm)
        self.lbx_ofl.Bind(wx.EVT_LISTBOX_DCLICK, self.on_confirm)

    def create_widgets(self):
        # file names for listbox
        lbx_chc_lst = [e[0] for e in self.doc_lst]

#HACK, map hidden OK button to ENTER key
        self.btn_ok_ = wx.Button(self, wx.ID_OK, size=(0, 0))
        self.btn_ok_.SetDefault()

#HACK, map hidden cancel button to ESCAPE key
        self.btn_esc = wx.Button(self, wx.ID_CANCEL, size=(0, 0))
        self.SetEscapeId(wx.ID_CANCEL)

        self.txc_flt = wx.TextCtrl(self, wx.ID_ANY, '', size=(500, 35))
        self.lbx_ofl = wx.html.SimpleHtmlListBox(self, choices=lbx_chc_lst, size=(500, 250))  #, style=wx.LB_OWNERDRAW)

        # colours and font
        self.SetBackgroundColour(self.sec['BackColour'])
        self.txc_flt.SetBackgroundColour(self.sec['TextCtrlBackColour'])
        self.lbx_ofl.SetBackgroundColour(self.sec['ListBoxBackColour'])
        self.lbx_ofl.SetSelectionBackground(self.sec['ListBoxSelBackColour'])

    def on_filter(self, evt):
        flt_txt = self.txc_flt.Value
        # populate listbox
        self.lbx_ofl.Clear()
        self.lbx_ofl.SetItemCount(0)
        self.pag_lst = []
        self.flt_itm_lst = []
        for itm in self.doc_lst:
            if self.sec['FuzzySearch'] and flt_txt:
                if (res := FUZ.find_best_match(flt_txt, itm[0])).score >= 0:
                    self.add_document(itm, fuzzy_obj=res)
            elif flt_txt in itm[0]:
                self.add_document(itm)

        self.lbx_ofl.Set(self.flt_itm_lst)
        self.lbx_ofl.SetItemCount(len(self.flt_itm_lst))
        # highlight/select first file name
        if self.lbx_ofl.GetCount() > 0:
            self.lbx_ofl.SetSelection(0)
            self.on_select(None)

        # resize listbox
        if self.lbx_ofl.GetCount() < 10:
            self.lbx_ofl.SetSize(500, self.lbx_ofl.GetCount() * 26)
        else:
            self.lbx_ofl.SetSize(500, 250)
        self.SetSize(-1, 10 + self.txc_flt.Size.y + self.lbx_ofl.Size.y)
        return

    def on_char(self, evt):
#HACK, repeat last keypress after focus switch (text control <-> listbox)
        rpt_key = wx.UIActionSimulator()
        if evt.KeyCode in LBX_NAV_KEYS and self.txc_flt.HasFocus():
            if self.lbx_ofl.GetCount() > 0:
                dbf.FOCUS(self.lbx_ofl)
                rpt_key.Char(evt.KeyCode)
        elif evt.KeyCode not in LBX_NAV_KEYS and self.lbx_ofl.HasFocus():
            dbf.FOCUS(self.txc_flt)
            self.txc_flt.SetInsertionPointEnd()
            rpt_key.Char(evt.KeyCode)
#HACK, SHIFT key forces paint at bottom of resized listbox
        rpt_key.Char(wx.WXK_SHIFT)
        evt.Skip()
        return

    def on_select(self, evt):
        # set focus on selected document (page tab)
        idx = self.lbx_ofl.Selection
        pag = self.pag_lst[idx]
        glb.NBK.SetSelection(pag)

    def on_confirm(self, evt):
        self.cleanup()
        # set focus on selected document
        dbf.FOCUS(glb.NBK.CurrentPage)  # .txt1)

    def on_exit(self, evt):
        # ESCAPE clears filter?
        if evt.Id == wx.ID_CANCEL and self.txc_flt.Value:
            self.txc_flt.Value = ''
            dbf.FOCUS(self.txc_flt)
            return
        self.cleanup()
        # set focus on last document
        dbf.FOCUS(self.doc_cur)

    def add_document(self, itm, fuzzy_obj=None):
        if fuzzy_obj:
            # nam = FUZ.format(itm[0], fuzzy_obj, '<b>', '</b>')
            nam = FUZ.format(itm[0], fuzzy_obj, '<font color="black"><b><u>', '</u></b></font>')
        else:
            nam = itm[0]

        nam = f'<table cellspacing="1" cellpadding="1" border="0" width="99%">' \
              f'<tr><td><b>{nam}</b></td></tr></table>'

        self.flt_itm_lst.append(nam)
        self.lbx_ofl.Append(nam)
        self.pag_lst.append(itm[1])

    def cleanup(self):
        make_modal(self, False)
        if self.sec['DropShadow']:
            drop_shadow(self, show=False)
        self.Destroy()

    def create_document_list(self):
        # build list of open documents and page tab indices
        doc_lst = []
        for pag, doc in glb.NBK.open_docs():
            fnm = doc.pnm
            doc_lst.append([fnm, pag])

        return doc_lst
