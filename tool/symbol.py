#!/usr/bin/python

import glob
from pathlib import Path
import re
import sys

import wx
# from wx.lib.agw.hyperlink import HyperLinkCtrl, EVT_HYPERLINK_LEFT
from wx.adv import HyperlinkCtrl, EVT_HYPERLINK
import wx.html
from wx.lib.scrolledpanel import ScrolledPanel

import extern.fuzzysearch as FUZ
# from common.file import open_files
from common.path import resolve_path
from common.util import drop_shadow, get_closest_index, rs_, make_modal, set_font
from conf.debug import DEBUG, dbg_FOCUS, dbg_TIMER, dbg_SYMBOL_POPUP
from const.app import EXE, OPT_CTAGS, OUT_CTAGS, LBX_NAV_KEYS
from const import glb
from const.symbol import SBW_TMPFIL_NAME, SYMBOL
from tool.ctags import CtagsParser


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
        # self.create('INIT')
        pass

    def create(self):
        dbg_TIMER('index')
        if DEBUG['SIX']: print(f'* Create [Python] symbol index:')

        # reset symbol index dicts/counts
        for typ in SYMBOL:
            SYMBOL[typ][4].clear()
            SYMBOL[typ][3] = 0

        # triple quotes
        tsq = "'''"  # single
        tdq = '"""'  # double
        trq_reg = re.compile(rf'({tsq}|{tdq})')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, use all notebook tabs (open documents)
#FIX, call 'create_symbol_index' when doc(s) opened/closed

        fil_lst = glob.glob('**/*.py', recursive=True)

        # fil_lst = []
        # for __, doc in nbk.open_docs():
            # fnm = doc.pnm
            # fil_lst.append(fnm)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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
                if DEBUG['SIX'] == 1: print(f'{flc:3d}.  {pnm}')
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
                            if DEBUG['SIX'] == 3: print(lin[elc:])
                            lin = lin[:elc].rstrip()
                            stp = lin[:elc].strip()
                            if DEBUG['SIX'] == 3: print(' ', stp)

                        # skip triple quote comment
                        for __ in trq_reg.findall(lin):
                            if in_trq:
                                if DEBUG['SIX'] == 4: print(f'{pnm:24}: {lnc:4d}, [ {stp} ]')
                                in_trq = False
                            else:
                                in_trq = True

                        if in_trq:
                            if DEBUG['SIX'] == 4: print(f'{pnm:24}: {lnc:4d}, [ {stp} ]')
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

                except Exception as err:
                    print(f'{fil.name}\nUnexpected error: {sys.exc_info()[0]}\n{err}\n')
                    pass

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

                    diff = set(wrd_dct[wrd][fil]).difference(set(dfn_dct[wrd][fil]))
                    if not diff:
                        continue

                    # print(wrd_dct[wrd][fil])
                    # print(dfn_dct[wrd][fil])
                    # print('Diff', sorted(diff))
                    # print()

                    SYMBOL['REF'][3] += len(diff)  # add to total count

                    if wrd not in ref_dct:
                        ref_dct[wrd] = {fil: None}

                    ref_dct[wrd][fil] = list(diff)

                del wrd_dct[wrd]

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # remove words already existing in some other dicts
        wrd_dct = SYMBOL['WRD'][4]

        for typ in ['IMP', 'VAR', 'QTS']:
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

        if DEBUG['SIX'] >= 1:
            # summary/counts
            print(f'\n  Indexed Files: {flc}')
            print(f'\n  Symbol Type      Total   Unique')
            print(f'  {rs_(13)}   {rs_(6)}   {rs_(6)}')

            for typ in SYMBOL:
                dsc = SYMBOL[typ][0]
                tot = SYMBOL[typ][3]
                unq = len(SYMBOL[typ][4])
                # sts = 'Excluded' if not glb.CFG['SymbolIndex'][f'Include{typ}'] else 'Active'
                # print(f'  {dsc:13}   {tot:6d}    {unq:5d}   {sts}')
                print(f'  {dsc:13}   {tot:6d}    {unq:5d}')

            print()

        dbg_TIMER('index', 'STOP')

        # return list of indexes
        idx_lst = []
        for typ in SYMBOL:
            idx_lst.append(SYMBOL[typ][4])

        return idx_lst

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def parse_line(self, typ, pnm, lin, lnc):

        elm_cnt, elm_dct, elm_reg, reg_grp = SYMBOL[typ][3:]

        nam = typ.lower()

        stp = lin.strip()
        diff = len(lin) - len(stp)

        if DEBUG['SIX'] == 5:
            # control (white)space between matches
            cnt = prv_pos = 0

        for res in re.finditer(elm_reg, lin):
            elm = res.group(reg_grp)
            col = res.start(reg_grp) + 1

#FIX, needs better coding...
            # discard reference when its definition exists
            if typ == 'REF' and elm in SYMBOL['DFN'][4] and pnm in SYMBOL['DFN'][4][elm] and (lnc, col) in SYMBOL['DFN'][4][elm][pnm]:
                continue

            if typ == 'WRD':
                fnd = False
                for t in ['DFN', 'REF', 'IMP', 'VAR']:
                    if elm in SYMBOL[t][4] and pnm in SYMBOL[t][4][elm] and (lnc, col) in SYMBOL[t][4][elm][pnm]:
                        fnd = True
                        break
                if fnd:
                    continue

            elm_cnt += 1
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            lin = stp
            # print(f'[{nam}]::[{elm}]::[{pnm}]::[{diff if typ == "WRD" else ""}]')

            if DEBUG['SIX'] == 5:
                # control (white)space between matches
                cnt += 1
                pos = col - diff + 15

                if cnt == 1:
                    print(f'[{nam}]::[{elm}]::[{pnm}]')
                    print(f'  [{lnc:4d}]::[{lin=}]')
                    wsp = pos
                else:
                    wsp = pos - prv_pos

                # mark matches with '^' chars
                print(f'{" "*(wsp)}{"^"*len(elm)}', end='')
                prv_pos = pos + len(elm)

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # if typ == 'WRD' and elm in INDEX_EXCLUDE_WORDS:
            #     print('exclude', elm, lnc, pnm)
            #     continue
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # if typ == 'QTS' and elm[0] == '"':
            #     print(elm)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # strip begin/end quotes
            if typ == 'QTS':
                elm = elm[1:len(elm)-1]

            if elm not in elm_dct:
                elm_dct[elm] = dict([(pnm, [(lnc, col)])])
            elif pnm not in elm_dct[elm]:
                elm_dct[elm][pnm] = [(lnc, col)]
            else:
                elm_dct[elm][pnm].append((lnc, col))

        if DEBUG['SIX'] == 5:
            if cnt > 0:
                print()

        return elm_cnt, elm_dct
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class SymbolPopup(wx.Dialog):
# class SymbolPopup(wx.PopupTransientWindow):  # for 'PopupTransientWindow'

    __slots__ = ['CFG', 'sec', 'doc', 'tlw', 'stt_lst',
                 'max_wid', 'max_hgh', 'tmr', 'bxv', ]

    def __init__(self, doc, wrd, cwl, style):
        self.sec = glb.CFG['SymbolPopup']
        super().__init__(doc, style=wx.BORDER_SIMPLE)  # wx.DIALOG_NO_PARENT
        # super().__init__(doc, style)  # for 'PopupTransientWindow'
        self.doc = doc

        dbg_SYMBOL_POPUP(glb.TLW, wrd=wrd, total=True, verbose=False)

        if self.sec['DropShadow']:
            drop_shadow(self)

        self.doc.spu_active = True
        self.stt_lst = list()  # static text list
        # self.url_lst = list()  # symbol url list

        # maximum popup size
        self.max_wid = 0
        self.max_hgh = 0

        # monitor mouse pointer position
        self.tmr = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.mouse_timer)
        self.tmr.Start(50)  # milliseconds

#FIX,   # self.Bind(wx.EVT_KEY_DOWN, self.on_escape)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_escape)

        # add panel with labels
        scl_pnl = ScrolledPanel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)  # BORDER_RAISED
        scl_pnl.SetBackgroundColour(self.sec['PanelBackColour'])

        # populate panel/sizer
        self.bxv = wx.BoxSizer(wx.VERTICAL)

        if self.sec['ShowSymbol']:
            # word symbol
            stt_wrd = wx.StaticText(scl_pnl, label=f' {wrd} ')
            set_font(stt_wrd, face=self.sec['SymbolFont'], siz=10)  # Consolas
            self.set_popup_size(stt_wrd)
            stt_wrd.SetForegroundColour(self.sec['SymbolForeColour'])
            stt_wrd.SetBackgroundColour(self.sec['SymbolBackColour'])
            self.bxv.Add(stt_wrd, 0, wx.TOP|wx.BOTTOM, border=5)

        # add description and URL's per symbol type for word
        for typ in SYMBOL:
            self.populate_panel(scl_pnl, wrd, cwl, typ)

        scl_pnl.SetSizer(self.bxv)

        scl_pnl.SetupScrolling()

#FIX, calculate size (width), allow max. height 12 URL's
        siz = (self.max_wid + 25, 225)  # self.max_hgh
        self.SetSize(siz)
        scl_pnl.SetSize(siz)
        # print(f'{self.max_wid = }')

        # show symbol popup at cursor position
        self.SetPosition(wx.GetMousePosition())
        # self.Position(wx.GetMousePosition(), (-5, 15))  # for 'PopupTransientWindow'
        self.ShowModal()
        # self.Popup(self)  # for 'PopupTransientWindow'

    def click_url(self, evt):
#NOTE, prevent circular dependency
        from common.file import open_files

        url = evt.URL

        # get filename:line:column
        sep1 = url.find('|')
        sep2 = url.rfind('|')
        fil = url[:sep1]
        lin = int(url[sep1+1:sep2])
        col = int(url[sep2+1:])

        if DEBUG['SPU']: print(f'\nClicked URL: [{fil}]:[{lin}]:[{col}]')

        fil_lst = [[str(resolve_path(fil))]]
        print(fil_lst)
        # fil_lst = [['D:\\Dev\\D\\wx\\TSN_SPyE\\src\\_DEV\\_NOW\\Debugger\\_pdb_cmds.txt']]
        doc = open_files(fil_lst)

        if DEBUG['SPU']: print(f'  realpath = {str(resolve_path(fil))}')
        if DEBUG['SPU']: print(f'   pnm = {doc.pnm}')

        doc.GotoPos(doc.XYToPosition(col - 1, lin - 1))
        if self.sec['CentreCaret']:
            doc.VerticalCentreCaret()
        self.destroy(evt)

#NOTE, works for 'wx.Dialog', does NOT work for 'wx.PopupTransientWindow'
    def on_escape(self, evt):
        if evt.KeyCode == wx.WXK_ESCAPE:
            print('Escape SymbolPopup')
            self.destroy(evt)
#HACK: for a very short time ignore current doc's events so a new popup is not triggered
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

    def destroy(self, evt):
        if self.sec['DropShadow']:
            drop_shadow(self, show=False)
        self.Destroy()
        self.doc.spu_active = False

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
            self.set_popup_size(stt_typ)
            self.bxv.Add(stt_typ, 0, wx.TOP|wx.BOTTOM, border=5)
            if DEBUG['SPU']: print(f'\n{dsc}(s)')

        cnt = 0

        # symbol type hyperlinks for word
        for fil in sorted(idx[wrd]):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# include only refs in current file
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # print(fil)
            # print(glb.NBK.GetPage(glb.NBK.Selection).pnm)
            # if fil != glb.NBK.GetPage(glb.NBK.Selection).pnm:
            #     continue
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            for pos in sorted(idx[wrd][fil], key=lambda itm: itm[0]):
                # discard hyperlink for current symbol
                if pos == cwl:
                    continue
                cnt += 1
                url = f'{fil}|{pos[0]}|{pos[1]}'
                lbl = f'{fil}:{pos[0]}'
                hyp_url = HyperlinkCtrl(prt, label=lbl, url=url)
                hyp_url.Bind(EVT_HYPERLINK, self.click_url)
                # hyp_url.SetNormalColour('GREEN')
                # hyp_url.SetHoverColour('RED')
                set_font(hyp_url, face=self.sec['HyperlinkFont'], siz=10, bold=True)
                self.set_popup_size(hyp_url)
                self.bxv.Add(hyp_url, 0, wx.TOP|wx.BOTTOM, border=0)
                if DEBUG['SPU']: print(url)

        if self.sec['ShowSymbolType']:
            stt_typ.Label = f'{dsc}(s) [{cnt}]:'

    def set_popup_size(self, obj):
        dc = wx.ClientDC(self)
        dc.SetFont(obj.Font)
        # calculate font size in pixels
        w, h = dc.GetTextExtent(obj.Label)
        if w > self.max_wid:
            self.max_wid = w
        if h > self.max_hgh:
            self.max_hgh = h
        # print(w, h, obj.Label)


class SymbolBrowser(wx.Dialog):
    def __init__(self):
        self.sec = glb.CFG['SymbolBrowser']
        sty = wx.BORDER_SIMPLE  # wx.DIALOG_NO_PARENT
        super().__init__(glb.TLW, style=sty)
        self.WindowStyle |= wx.STAY_ON_TOP

        self.doc = glb.NBK.CurrentPage

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

        # get symbol name closest to current line
        cur = self.doc.LineFromPosition(self.doc_pos) + 1
        self.lin_lst = [e[2] for e in self.sym_lst]
        idx = get_closest_index(self.lin_lst, cur)
        self.lbx_sym.SetSelection(idx)

        # highlight/select symbol name
        self.on_select(None)
        dbg_FOCUS(self.lbx_sym)

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
        doc_wid = self.doc.ClientSize[0] // 2
        dlg_wid = self.ClientSize[0] // 2
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

#HACK: map hidden OK button to ENTER key
        self.btn_ok_ = wx.Button(self, wx.ID_OK, size=(0, 0))
        self.btn_ok_.SetDefault()

#HACK: map hidden cancel button to ESCAPE key
        self.btn_esc = wx.Button(self, wx.ID_CANCEL, size=(0, 0))
        self.SetEscapeId(wx.ID_CANCEL)

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # self.stt_hdr = wx.StaticText(self, wx.ID_ANY, 'Enter number:')
        # self.stt_hdr.SetBackgroundColour('#71B3E8')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.txc_flt = wx.TextCtrl(self, wx.ID_ANY, '', size=(330, 35))
        self.lbx_sym = wx.html.SimpleHtmlListBox(self, choices=lbx_chc_lst, size=(330, 250), style=wx.LB_OWNERDRAW)

        # colours and font
        self.SetBackgroundColour(self.sec['BackColour'])
        self.txc_flt.SetBackgroundColour(self.sec['TextCtrlBackColour'])
        self.lbx_sym.SetBackgroundColour(self.sec['ListBoxBackColour'])
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, add 'ListBoxSelBackColour' to 'SymbolBrowser'
        self.lbx_sym.SetSelectionBackground('#71B3E8')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # for idx, itm in enumerate(self.sym_lst):
            # self.lbx_sym.SetItemBackgroundColour(idx, itm[3])

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
                # fuzzy search
                res = FUZ.find_best_match(flt_txt, nam)
                if res.score >= 0:
                    # print(res.score, itm[2], FUZ.format(nam, res, '<b>', '</b>'))
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
        self.SetSize(-1, 15 + self.txc_flt.Size[1] + self.lbx_sym.Size[1])
        return

    def on_char(self, evt):
#HACK: repeat last keypress after focus switch (text control <-> listbox)
        rpt_key = wx.UIActionSimulator()
        if evt.KeyCode in LBX_NAV_KEYS and self.txc_flt.HasFocus():
            if self.lbx_sym.GetCount() > 0:
                dbg_FOCUS(self.lbx_sym)
                rpt_key.Char(evt.KeyCode)
        elif evt.KeyCode not in LBX_NAV_KEYS and self.lbx_sym.HasFocus():
            dbg_FOCUS(self.txc_flt)
            self.txc_flt.SetInsertionPointEnd()
            rpt_key.Char(evt.KeyCode)
#HACK: SHIFT key forces paint at bottom of resized listbox
        rpt_key.Char(wx.WXK_SHIFT)
        evt.Skip()
        return

    def on_select(self, evt):
        # highlight/select line with selected symbol name
        idx = self.lbx_sym.Selection
        # typ, nam, lin, __ = self.sym_lst[idx]
        lin = self.lin_lst[idx]
        self.doc.GotoLine(lin - 1)
        self.doc.LineEndExtend()
        self.doc.VerticalCentreCaret()

    def on_confirm(self, evt):
        self.cleanup()

    def on_exit(self, evt):
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
            # nam = FUZ.format(nam, fuzzy_obj, '<font color="black"><b>', '</b></font>')
            nam = FUZ.format(nam, fuzzy_obj, '<font color="black"><b><u>', '</u></b></font>')
            # nam = FUZ.format(nam, fuzzy_obj, '<font color="black"><b><u><i>', '</i></u></b></font>')
            # nam = nam.replace('<b>', '[').replace('</b>', ']')

        nam = f'<table cellspacing="1" cellpadding="1" border="0" width="99%">' \
              f'<tr><td bgcolor="{clr}" width="8%" align="center"><b>{itm[0]}</b></td><td><b>{nam}</b></td></tr></table>'

        # nam = f'<table cellspacing="1" cellpadding="1" border="0" width="99%">' \
        #       f'<tr><td bgcolor="{clr}" width="8%"><b>[{itm[0]}]</b></td><td><b>{nam}</b></td></tr></table>'

        # nam = f'<table cellspacing="0" cellpadding="0" bgcolor="#C6E2FF" border="0" width="99%">' \
        #       f'<tr bgcolor="{clr}"><td><b>{nam}</b></td></tr></table>'

        # nam = f'<b>{nam}</b>'

        # idx = self.lbx_sym.Append(nam)
        self.flt_itm_lst.append(nam)
        # self.lbx_sym.SetItemBackgroundColour(idx, clr)
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
        # file = self.doc.pnm.replace('\\', '/')

        # create/read tags file
        parser = CtagsParser()

        # auxiliary option: including regex search pattern '--excmd=pattern'
        # res = parser.parse(f'{EXE["CTAGS"]} -f "{OUT_CTAGS}" -nu --excmd=pattern --extras=-p --fields=fiKlmnsStz -R {tmp}')
        res = parser.parse(f'{EXE["CTAGS"]} -f "{OUT_CTAGS}" {OPT_CTAGS} {tmp}')

        Path(tmp).unlink()

        if not res:
            return False

        # build symbol list (type, name, line, colour)
        sym_lst = []

        for tag in parser.tags:
            kind = tag.fields['kind']

#HACK: assume that 1 indent is 4 spaces wide
            ind = tag.xcmd[2:10]
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
        self.doc_cur = glb.NBK.CurrentPage

        self.doc_lst = self.create_document_list()
        self.pag_lst = [e[1] for e in self.doc_lst]

        self.create_widgets()

        # highlight/select current file name
        self.lbx_ofl.SetSelection(glb.NBK.Selection)
        self.on_select(None)
        dbg_FOCUS(self.lbx_ofl)

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
        doc_wid = self.doc_cur.ClientSize[0] // 2
        dlg_wid = self.ClientSize[0] // 2
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

#HACK: map hidden OK button to ENTER key
        self.btn_ok_ = wx.Button(self, wx.ID_OK, size=(0, 0))
        self.btn_ok_.SetDefault()

#HACK: map hidden cancel button to ESCAPE key
        self.btn_esc = wx.Button(self, wx.ID_CANCEL, size=(0, 0))
        self.SetEscapeId(wx.ID_CANCEL)

        self.txc_flt = wx.TextCtrl(self, wx.ID_ANY, '', size=(500, 35))
        self.lbx_ofl = wx.ListBox(self, choices=lbx_chc_lst, size=(500, 250))  #, style=wx.LB_OWNERDRAW)

        # colours and font
        self.SetBackgroundColour(self.sec['BackColour'])
        self.txc_flt.SetBackgroundColour(self.sec['TextCtrlBackColour'])
        self.lbx_ofl.SetBackgroundColour(self.sec['ListBoxBackColour'])

        for wgt in (self.txc_flt, self.lbx_ofl):
            set_font(wgt, self.sec['Font'], self.sec['FontSize'], self.sec['FontBold'])

    def on_filter(self, evt):
        flt_txt = self.txc_flt.Value
        # populate listbox
        self.lbx_ofl.Clear()
        self.pag_lst = []
        for itm in self.doc_lst:
            if self.sec['FuzzySearch'] and flt_txt:
                # fuzzy search
                res = FUZ.find_best_match(flt_txt, itm[0])
                if res.score >= 0:
                    # print(res.score, itm[1], FUZ.format(itm[0], res, '<b>', '</b>'))
                    self.add_document(itm, fuzzy_obj=res)
            elif flt_txt in itm[0]:
                self.add_document(itm)

        # highlight/select first file name
        if self.lbx_ofl.Count > 0:
            self.lbx_ofl.SetSelection(0)
            self.on_select(None)

        # resize listbox
        if self.lbx_ofl.Count < 10:
            self.lbx_ofl.SetSize(500, self.lbx_ofl.Count * 26)
        else:
            self.lbx_ofl.SetSize(500, 250)
        self.SetSize(-1, 15 + self.txc_flt.Size[1] + self.lbx_ofl.Size[1])
        return

    def on_char(self, evt):
#HACK: repeat last keypress after focus switch (text control <-> listbox)
        rpt_key = wx.UIActionSimulator()
        if evt.KeyCode in LBX_NAV_KEYS and self.txc_flt.HasFocus():
            dbg_FOCUS(self.lbx_ofl)
            rpt_key.Char(evt.KeyCode)
        elif evt.KeyCode not in LBX_NAV_KEYS and self.lbx_ofl.HasFocus():
            dbg_FOCUS(self.txc_flt)
            self.txc_flt.SetInsertionPointEnd()
            rpt_key.Char(evt.KeyCode)
#HACK: SHIFT key forces paint at bottom of resized listbox
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
        dbg_FOCUS(glb.NBK.CurrentPage)

    def on_exit(self, evt):
        self.cleanup()
        # set focus on last document
        dbg_FOCUS(self.doc_cur)

    def add_document(self, itm, fuzzy_obj=None):
        if fuzzy_obj:
            nam = FUZ.format(itm[0], fuzzy_obj, '<b>', '</b>')
        else:
            nam = itm[0]
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
