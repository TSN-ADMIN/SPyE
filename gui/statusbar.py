#!/usr/bin/python

import time

import wx
from wx import stc

from common.doc import guess_eol_mode
from common.util import get_icon, is_shown, me_
from conf.debug import DEBUG, dbg_CTXTSB, dbg_TIMER
from const.common import TXT_NIL
from const import glb
from const.menu import MI
from const.statusbar import (
    SBF, SBF_CPY, SBF_TIM_SECONDS_WIDTH, SBX, SBX_EOL, SBL, SBF_NO_CLEAR_AUX
)
from extern.EnhancedStatusBar import (
    EnhancedStatusBar, ESB_EXACT_FIT, ESB_ALIGN_CENTER_VERTICAL, ESB_ALIGN_LEFT
)
import gui


class StatusBar(EnhancedStatusBar):

    __slots__ = ['CFG', 'sec', 'prt', 'prv_tim', 'tmr_cfd', 'ico_psw']

    def __init__(self, prt, *args, **kwargs):
        self.sec = glb.CFG['StatusBar']
        sty = self.style()
        super().__init__(prt, style=sty, name='StatusBar')
        self.SetExtraStyle(wx.WS_EX_PROCESS_UI_UPDATES)
        self.prt = prt

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #TODO, sliding 'MSG' field width, right/left: TEST
#         self._fwd = True
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # self.dft_fnt = self.Font

        # 2nd colon blinks every second
        self.prv_tim = '99:99:99'

        # timers to clear field after a set delay since last update
        self.tmr_cfd = {
            'MSG': wx.Timer(self, wx.NewIdRef()),
            'AUX': wx.Timer(self, wx.NewIdRef()),
        }
        self.SetBackgroundColour(self.sec['BackColour'])
        self.create()

        # use message field to display menu and toolbar help text
        self.prt.SetStatusBarPane(SBF['MSG'][0])

        # panel switcher icon (rescaled)
#FIX, create 'SMALL'  constant 'ICO_SIZE_S = (16, 16)'
#FIX, create 'MEDIUM' constant 'ICO_SIZE_M = (24, 24)'
#FIX, create 'LARGE'  constant 'ICO_SIZE_L = (32, 32)'

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #
    # Searching 34 files for "(16|24|32), (16|24|32)" (regex)
    #
    # D:\Dev\D\wx\TSN_SPyE\src\lib\editor.py:
    #   309:     self.RegisterImage(2, wx.ArtProvider.GetBitmap(wx.ART_NEW, size=(16, 16)))
    #   310:     self.RegisterImage(3, wx.ArtProvider.GetBitmap(wx.ART_COPY, size=(16, 16)))
    #
    # D:\Dev\D\wx\TSN_SPyE\src\lib\extern\shortcuteditor.py:
    #  1802:     self.imageList = wx.ImageList(16, 16)
    #  1826:         if bitmap.GetSize() != (16, 16):
    #  1827:             bitmap = bitmap.ConvertToImage().Scale(16, 16, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
    #
    # D:\Dev\D\wx\TSN_SPyE\src\lib\gui.py:
    #  1262:     glb.TB.SetToolBitmapSize((24, 24) if TBX['LRG_ICO'][1] else (16, 16))
    #
    # D:\Dev\D\wx\TSN_SPyE\src\lib\sidepanel.py:
    #    68:     img_siz = (16, 16)
    #   677:         img_siz = (16, 16)
    #
    # D:\Dev\D\wx\TSN_SPyE\src\lib\statusbar.py:
    #    49:     siz = (16, 16)
    #
    # D:\Dev\D\wx\TSN_SPyE\src\lib\toolbar.py:
    #   102: #   tb.SetToolBitmapSize((24, 24) if TBX['LRG_ICO'][1] else (16, 16))
    #
    # 12 matches across 6 files
    #
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        ico = get_icon(nam='app', siz=16)
        self.ico_psw = wx.StaticBitmap(self, bitmap=ico, name='icoPanelSwitcher')
        self.AddWidget(self.ico_psw)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #NOTE, EXPERIMENTAL CODE: 'MSG' field visibility
#         self.stt_msg = wx.StaticText(self, label='W', name='sttMsgFieldText')
#         # self.stt_msg.SetForegroundColour('RED')
#         self.AddWidget(self.stt_msg, ESB_ALIGN_LEFT, ESB_ALIGN_CENTER_VERTICAL, pos=1)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.binds()

    def binds(self):
        self.Bind(wx.EVT_UPDATE_UI, lambda e: self.update(glb.NBK.CurrentPage))

        evt = wx.EVT_LEFT_DOWN if glb.CFG['ContextMenu']['LeftClick'] else wx.EVT_CONTEXT_MENU
        # bind statusbar INCLUDING 'PanelSwitcher' icon
        for obj in (self, self.ico_psw):
            obj.Bind(evt, lambda e: gui.ContextMenu(e, 'SBR'))

        self.Bind(wx.EVT_LEFT_DOWN, self.toggle_insert)

        # self.Bind(wx.EVT_ENTER_WINDOW, self.tooltip)
#HACK: when statusbar is painted (hence updated)
        self.Bind(wx.EVT_PAINT, self.clear_field_set_delay)
        # self.Bind(wx.EVT_PAINT, self.draw_field_borders)
        self.Bind(wx.EVT_TIMER, self.clear_field)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # def draw_field_borders(self, evt):
    #     dc = wx.ClientDC(self)
    #     dc.SetPen(wx.Pen('RED', 1))
    #     for idx in range(self.GetFieldsCount()):
    #         x, y, w, h = self.GetFieldRect(idx)
    #         dc.SetBrush(wx.Brush('RED', wx.BRUSHSTYLE_TRANSPARENT))
    #         dc.DrawRectangle(x - 1, y - 1, w + 1, h + 1)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def style(self):
        sty = 0
        sty += wx.BORDER_SUNKEN if self.sec['Border'] else wx.BORDER_NONE
        sty += wx.STB_SIZEGRIP  if self.sec['SizeGrip'] else 0
        sty += wx.STB_SHOW_TIPS if self.sec['ToolTips'] else 0
        sty += wx.FULL_REPAINT_ON_RESIZE
        return sty

    def create(self):
        # field#: 0 = panel switcher    1 = msg   2 = aux   3 = Ln/Col yy    4 = INS/OVR
        #         5 = lock keys         6 = search flags    7 = file size    8 = encoding
        #         9 = end of line      10 = indentation    11 = language    12 = clock time

        # rebuild statusbar fields from config
        SBF.clear()
        for idx, (key, val) in enumerate(SBF_CPY.items()):
            if key in self.sec['Fields']:
                SBF[key] = val       # original list
                SBF[key][0] = idx    # field number (consecutive)
                SBX[key][1] = True   # checked
            else:
                SBX[key][1] = False  # unchecked

        self.fld_wid_lst = [w[1] for w in SBF.values()]
        self.fld_sty_lst = [s[2] for s in SBF.values()]
        self.fld_cnt = len(self.fld_wid_lst)

        # clock time field width/format
        if SBX['TIM'][1]:
            fld_tim_pos, fld_tim_wid = SBF['TIM'][:2]  # default width
            self.fld_wid_lst[fld_tim_pos] = SBF_TIM_SECONDS_WIDTH if self.sec['ClockTimeSeconds'] else fld_tim_wid
            self.fld_tim_fmt = '%H:%M:%S' if self.sec['ClockTimeSeconds'] else '%H:%M'

        # set field properties
        self.SetFieldsCount(self.fld_cnt)
        self.SetStatusWidths(self.fld_wid_lst)
        self.SetStatusStyles(self.fld_sty_lst)

    def rebuild(self):
        tlw = self.prt
        self.Destroy()
        del self
        glb.SB = self = StatusBar(tlw)
        tlw.SetStatusBar(self)

    def clear_field_set_delay(self, evt):
        for fld in self.tmr_cfd:
            fld_txt = self.GetField(SBF[fld][0]).Text
            if self.tmr_cfd[fld].IsRunning() or fld_txt == TXT_NIL:
                continue
            if fld == 'AUX' and any(s in fld_txt for s in SBF_NO_CLEAR_AUX):
                continue
            self.tmr_cfd[fld].StartOnce(self.sec[f'DelayClearField{fld}'])

    def clear_field(self, evt):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #NOTE, EXPERIMENTAL CODE: 'MSG' field visibility
#         self.stt_msg.SetLabel(TXT_NIL)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        for fld in self.tmr_cfd:
            if evt.Id == self.tmr_cfd[fld].Id:
                self.set_text(TXT_NIL, fld)
                self.tmr_cfd[fld].Stop()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #TODO, sliding 'MSG' field width, right/left: TEST
#                 self.prt.SetStatusBar(None)
#                 self.__init__(self.prt)
#                 print('__init__')
#                 self.prt.SetStatusBar(self)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # if fld == 'AUX' and self.Font is not self.dft_fnt:
                #     self.SetFont(self.dft_fnt)

    def pop_text(self, fld):  # (self, fld, *args, **kwargs)
        # print(f'{me_("F")}: CallLater called with {fld =}, {args =}, {kwargs =}\n')
#NOTE, workaround: 'RuntimeError: wrapped C/C++ object of type StatusBar has been deleted'
        try:
            self.PopStatusText(SBF[fld][0])
        except RuntimeError:
            pass
#NOTE, workaround: 'AttributeError: 'AppFrame' object has no attribute 'tmr_pop''
        if hasattr(self, 'tmr_pop'):
            self.tmr_pop.Stop()
            del self.tmr_pop

    def toggle_insert(self, evt):
        evt.Skip()
        # when no document open, abort
        if not glb.NBK.PageCount:
            return

        pos = self.ClientToScreen(evt.Position)
        __, clk_fld = self.get_clicked_field(pos)

        if clk_fld != 'INS':
            return

        doc = glb.NBK.CurrentPage
        doc.SetOvertype(bool(not doc.Overtype))

    def tooltip(self, evt):
        obj = evt.EventObject
        nam = obj.Name
        ttp = 'statusbar tooltip'
        obj.SetToolTip(ttp)

    def get_clicked_field(self, pos):
        # convert client rectangle to screen coordinates
        clt = self.ClientRect
        rct = wx.Rect(self.ClientToScreen(clt.Position), clt.Size)

        clk_fld = None
        sfr_lst = list()  # field rectangles

        for idx, fld in enumerate(SBF):
            sfr = self.GetFieldRect(idx)
            sfr = wx.Rect(self.ClientToScreen(sfr.Position), sfr.Size)
            sfr_lst.append(sfr)

            # clicked this field?
            if sfr.Contains(pos):
                clk_fld = list(SBF)[idx]  # key (name) by field number
                break

        if DEBUG['CTX']: dbg_CTXTSB(pos, idx, rct, sfr_lst)

        return rct, clk_fld

    def push_text(self, msg, fld='MSG'):
#FIX, needs better coding... -> if not SBX[fld][1]: return
        msg = msg if fld in ['MSG', 'AUX'] or SBX[fld][1] else TXT_NIL
        self.PushStatusText(msg, SBF[fld][0])
        self.tmr_pop = wx.CallLater(self.sec['DelayClearFieldMSG'], self.pop_text, fld)

    def set_text(self, msg, fld='MSG', typ='DEFAULT'):
#NOTE, avoid error 'wrapped C/C++ object of type StatusBar has been deleted'
#      when returned from 'CtxStatusBarMain'
        try:
            bgc = self.BackgroundColour
        except RuntimeError:
            return
        if typ == 'INFO':
#TODO, key 'InformationBackColour' in config file
            self.SetBackgroundColour('FOREST GREEN')
        elif typ == 'WARN':
            self.SetBackgroundColour(self.sec['WarningBackColour'])
        elif typ == 'ERROR':
            self.SetBackgroundColour(self.sec['ErrorBackColour'])

#FIX, needs better coding... -> if not SBX[fld][1]: return
        msg = msg if fld in ['MSG', 'AUX'] or SBX[fld][1] else TXT_NIL
        if fld == 'MSG' or SBX[fld][1]:
            self.SetStatusText(msg, SBF[fld][0])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #NOTE, EXPERIMENTAL CODE: 'MSG' field visibility
#             if fld == 'MSG':
#                 self.stt_msg.SetLabel(f'{msg}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # if fld == 'AUX':
        #     # fnt = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        #     # self.SetFont(fnt)
        #     self.SetStatusText(msg, SBF[fld][0])

        self.SetBackgroundColour(bgc)

    def update(self, doc):
        # when no document open, abort
        if not glb.NBK.PageCount:
            return

        mb = glb.MB

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #TODO, sliding 'MSG' field width, right/left: TEST
#         self.Freeze()
#         if self.tmr_cfd['MSG'].IsRunning():
#             print(self.fld_wid_lst[1])
#             self.fld_wid_lst[1] += 1 if self._fwd else -1
#             if self.fld_wid_lst[1] > 400:
#                 self._fwd = False
#
#             self.SetStatusWidths(self.fld_wid_lst)
#             # wx.MilliSleep(1)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # auxiliary field
        msg = TXT_NIL
        cnt, spos, epos = doc.Selections, *doc.GetSelection()
        if cnt > 1 or spos != epos:
            msg = 'Sel:'
            if cnt >= 2:
                msg = f'{msg} Cnt={cnt}'
            else:
                slin, elin = (doc.LineFromPosition(s) for s in (spos, epos))
                lin_txt = TXT_NIL
                if slin != elin:
                    lin_cnt = elin - slin + 1
                    lin_txt = f'Ln={lin_cnt}, '
                chr_cnt = epos - spos
                msg = f'{msg} {lin_txt}Ch={chr_cnt}'
        elif doc.mac_rec_active:
            msg = 'Recording macro'
        elif doc.mch_active:
            msg = 'Marking matches'
        elif doc.tmr_cph.IsRunning():
            msg = 'Position history'
        elif glb.NBK.pth_active:
            msg = 'Page tab history'
        elif is_shown('SCH'):  # .sch.txc_fnd.HasFocus():
            msg = f'Search mode: {glb.SCH.mode}'
        elif cnt == 1:
#NOTE, not used; keep in mind: 'cnt == 1' w/ empty selection, never returns '0'
            # msg = 'No selection'
            pass
        else:
            # we should NEVER get here
            err = f'{me_("F")}: unexpected empty AUX field message'
            raise AssertionError(err)

        self.set_text(msg, 'AUX')

        # Ln/Col
        lin = doc.CurrentLine + 1
        col = doc.GetColumn(doc.CurrentPos) + 1
        tot = doc.GetLineLength(lin - 1)
        self.set_text(SBL['LNC'] % (lin, col, tot), 'LNC')

        # ruler caret column
        glb.RLR.set_column(col)

        # insert mode
        ins = SBL['OVR'] if doc.Overtype else SBL['INS']
        if not doc.tmr_cph.IsRunning():
            doc.SetCaretStyle(stc.STC_CARETSTYLE_BLOCK if doc.Overtype else stc.STC_CARETSTYLE_LINE)
        self.set_text(f'{ins}', 'INS')

        # Caps/Num/Scroll lock status
        lck = TXT_NIL
        _gks = wx.GetKeyState
        if _gks(wx.WXK_CAPITAL): lck += SBL['CAP']
        if _gks(wx.WXK_NUMLOCK): lck += SBL['NUM']
        if _gks(wx.WXK_SCROLL):  lck += SBL['SCL']
        self.set_text(f'{lck}', 'CNS')

        # find labels, separator = '|'
        txt = SBL['SCH']
        mod = glb.SCH.mode

        if mb.IsChecked(MI['SCH_CAS']):
            txt += SBL['CAS']
#TODO, REGEX not implemented
        if mb.IsChecked(MI['SCH_REG']):
            txt += SBL['REG']
        if mb.IsChecked(MI['SCH_WRD']):
            txt += SBL['WRD']
        if mb.IsChecked(MI['SCH_WRP']) and mod != 'FIF':
            txt += SBL['WRP']
        if mb.IsChecked(MI['SCH_ISL']) and mod != 'FIF':
            txt += SBL['ISL']
        if mb.IsChecked(MI['SCH_HLM']) and mod != 'FIF':
            txt += SBL['HLM']
        if mb.IsChecked(MI['SCH_PCS']) and mod == 'RPL':
            txt += SBL['PCS']
        if mb.IsChecked(MI['SCH_CXT']) and mod == 'FIF':
            txt += SBL['CXT']
        if mb.IsChecked(MI['SCH_BUF']) and mod == 'FIF':
            txt += SBL['BUF']

        txt = txt.rstrip('|')  # strip last '|'
        self.set_text(f'{txt}', 'SCH')

        # file size
        siz = doc.Length
        self.set_text(SBL['FSZ'] % (siz), 'FSZ')

#FIX, field 'ENC' not implemented
        # file encoding
        self.set_text(f'{SBL["ENC"]}', 'ENC')

        # end of line
        for key in SBX_EOL:
            SBX_EOL[key][1] = False

        # dbg_TIMER('guess_eol')

        txt, key, flg = guess_eol_mode(doc)

        # dbg_TIMER('guess_eol', 'STOP')

        if key:
            mb.Check(MI[f'FMT_{key}'], True)
            SBX_EOL[key][1] = True
            doc.SetEOLMode(flg)
        else:
            mb.Check(MI['FMT_EMX'], True)
            SBX_EOL['EMX'][1] = True

        self.set_text(txt, 'EOL')

        # indentation
        txt = 'Spaces' if not doc.UseTabs else 'Tab size'
        num = doc.TabWidth
        self.set_text(f'{txt}:{num}', 'IND')
        mb.Check(MI['IND_IUS'], bool(not doc.UseTabs))
        mb.Check(MI[f'IND_TW{num}'], True)

        # language (in menu, too)
        nam = doc.lng_nam
        self.set_text(f'{nam}', 'LNG')
        mb.Check(doc.lng_mni, True)

        # clock time
        if SBX['TIM'][1]:
            tim = time.strftime(self.fld_tim_fmt, time.localtime(time.time()))
            # 2nd colon blinks every second
            if self.sec['ClockTimeSeconds'] and self.sec['ClockTimeColonBlink']:
                if tim[-2:] != self.prv_tim[-2:]:
                    if ':' in self.prv_tim[5]:
                        bln = tim[5].replace(':', ' ')
                    else:
                        bln = tim[5].replace(' ', ':')
                    tim = tim[:5] + bln + tim[6:]
                    self.set_text(f'{tim}', 'TIM')
                    self.prv_tim = tim
            else:
                self.set_text(f'{tim}', 'TIM')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #TODO, sliding 'MSG' field width, right/left: TEST
#         self.Thaw()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
