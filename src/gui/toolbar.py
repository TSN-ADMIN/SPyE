#!/usr/bin/python

import wx

from conf.debug import DBG, DEBUG, dbf, me_
from common.type import is_str
from common.util import not_implemented
from const.common import TXT_NIL
from const import glb
from const.menubar import NO_ICO, NO_KND, NO_UIH
from const.toolbar import TBR, TBX
from data.images import catalog as PNG
import gui
import mix


#INFO, see: contrib/TestFloatBar.7z  (needs: wx.lib.floatbar)

class ToolBar(wx.ToolBar, mix.Help):

    __slots__ = ['CFG', 'sec', 'prt']

    def __init__(self, prt, *args, **kwargs):
        self.sec = glb.CFG['ToolBar']
        sty = wx.TB_HORIZONTAL | wx.BORDER_MASK
        super().__init__(prt, style=sty, name='ToolBar')
        mix.Help.__init__(self)
        self.prt = prt

#INFO, URL=https://docs.wxpython.org/wx.ToolBar.html
        wx.SystemOptions.SetOption('msw.remap', 0)

        self.ttd = gui.toolbar_defs.TTD
        self.style()
        self.tbt = self.create()

    def style(self):
        self.SetBackgroundColour(self.sec['BackColour'])
        sty = self.WindowStyle

        # get context menu item check marks from config
        DBG('CTX', (dbf.CTX_TBR, 'B', TBX, glb.CFG))
        TBX['SHW_ICO'][1] = self.sec['ShowIcons']
        TBX['SHW_TXT'][1] = self.sec['ShowText']
        TBX['LRG_ICO'][1] = self.sec['LargeIcons']
        TBX['LRG_TXT'][1] = self.sec['LargeText']
        TBX['ALN_HOR'][1] = self.sec['AlignHorizontally']
        TBX['LOC_TOP'][1] = self.sec['Top']
        TBX['LOC_LFT'][1] = self.sec['Left']
        TBX['LOC_BOT'][1] = self.sec['Bottom']
        TBX['LOC_RIT'][1] = self.sec['Right']
        DBG('CTX', (dbf.CTX_TBR, 'A', TBX, glb.CFG))

        # prepare toolbar: style, font, bitmap size
        if not TBX['SHW_ICO'][1]:
            sty |= wx.TB_NOICONS

        if TBX['SHW_TXT'][1]:
            sty |= wx.TB_TEXT

        if TBX['LRG_ICO'][1]:
            lrg, mdm, sml = (32, 32), (24, 24), (16, 16)
            self.SetToolBitmapSize(mdm if TBX['LRG_ICO'][1] else sml)
            sfx = '24' if TBX['LRG_ICO'][1] else '16'  # suffix
            for key, itm in self.ttd.items():
                # search control has no dedicated icon
                if key == 'SCH':
                    continue
                __, __, __, ico, __, __, id_ = itm
                ico += f'_{sfx}'

                try:
                    # prepare size
                    if not any(s in ico for s in ('16', '24') if ico.endswith(s)):
                        ico += f'_{sfx}'
                    bmp = PNG[ico].Bitmap
                    self.SetToolNormalBitmap(id_, bmp)
                    self.SetToolDisabledBitmap(id_, bmp)
                except KeyError as e:
                    DBG('MNU==0', f'{me_("C, F")}: icon not found: [{e.args[0]}]')
                    img_siz = (int(sfx), int(sfx))
                    bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, size=img_siz)

        siz = self.sec['LargeTextFontSize'] if TBX['LRG_TXT'][1] else self.sec['TextFontSize']
        self.SetOwnFont(wx.Font(wx.FontInfo(siz)))

        if TBX['ALN_HOR'][1]:
            sty |= wx.TB_HORZ_LAYOUT

        # clear all 'location' flags (must be mutually exclusive)
        for flg in [wx.TB_HORIZONTAL, wx.TB_VERTICAL, wx.TB_BOTTOM, wx.TB_RIGHT]:
            sty &= ~flg

        # set ONLY 1 'location' flag
        if TBX['LOC_TOP'][1]:
            sty |= wx.TB_HORIZONTAL
        elif TBX['LOC_LFT'][1]:
            sty |= wx.TB_VERTICAL
        elif TBX['LOC_BOT'][1]:
            sty |= wx.TB_BOTTOM
        elif TBX['LOC_RIT'][1]:
            sty |= wx.TB_RIGHT

        self.SetWindowStyle(sty)

#TODO, experiment with width of tooltip (see wx demo: -1/0)
        # wx.ToolTip.SetMaxWidth(-1)

#########################################################################################

    def create(self):
        def __search(evt):
            print('__search')

        def __cancel(evt):
            print('__cancel')

        def __do_search(evt):
            print(f'__do_search: {tbs.GetValue()}')

        tlw = glb.TLW
        tbt = {}

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL:
#         # self.SetToolBitmapSize((1, 19))
#         bmp = PNG['alpha_zero_1x100'].Image.Scale(1,19).ConvertToBitmap()
#         bmp = PNG['alpha_zero_1x100'].Image.Size((1,19), (0,0)).ConvertToBitmap()
#         self.AddTool(id_ := wx.NewIdRef(), '', bmp, bmp, wx.ITEM_NORMAL)
#         # self.SetToolDisabledBitmap(id_, bmp)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # rebuild toolbar tools from config
        for key in self.sec['Tools']:
            if key == 'SEP':
                self.AddSeparator()
                continue

#TODO, process text entered in 'tbs', implement functionality in handlers above
            if key == 'SCH':

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, use 'ToolBar' 'SearchCtrl' (for temp test in 'key_pressed')
                tbs = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER, size=(250, 25 if TBX['LRG_ICO'][1] else  23))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # tbs.SetBackgroundColour('YELLOW')
                #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # ctx_lst = list(tlw.ctx['TSK'])  # tuple -> list
                # mnu_ctx = glb.MBR.build_submenu(tbs, ctx_lst)
                # tbs.SetMenu(mnu_ctx)
                #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                tbs.ShowSearchButton(True)
                tbs.ShowCancelButton(True)
                tbt['SCH'] = self.AddControl(tbs)
                tbt['SCH'].Enable(False)
                self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, __search)
                self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, __cancel)
                self.Bind(wx.EVT_TEXT_ENTER, __do_search)
                continue

            # handle tool item attributes positionally
            # title, action, help text, icon, type, ui handler, id
            hlp = TXT_NIL
            uih = None
            itm = self.ttd[key]
            if len(itm) == 7:
                ttl, act, hlp, ico, typ, uih, id_ = itm
            else:
                err = f'{me_("F")}: tool item [{itm[0]}] takes 7 arguments ({len(itm)} given)'
                raise AssertionError(err)

            try:
                sfx = '24' if TBX['LRG_ICO'][1] else '16'  # suffix
                # prepare size
                if not any(s in ico for s in ('16', '24') if ico.endswith(s)):
                    ico += f'_{sfx}'
                bmp, img = PNG[ico].Bitmap, PNG[ico].Image
            except KeyError as e:
                DBG('MNU==0', f'{me_("C, F")}: icon not found: [{e.args[0]}]')
                img_siz = (int(sfx), int(sfx))
                bmp = wx.ArtProvider.GetBitmap(wx.ART_ERROR, size=img_siz)
                img = bmp.ConvertToImage()

#HACK, correct transparency (in rare [disabled] cases, e.g. 'calc_sum', 'save')
            img = img.AdjustChannels(.2, .2, .2, 2.1).ConvertToGreyscale(1.5, 1.5, 1.5)
            dis_bmp = img.ConvertToBitmap().ConvertToDisabled()
            tbt[key] = self.AddTool(id_, ttl, bmp, dis_bmp, wx.ITEM_NORMAL, hlp, hlp)

            # add action
            if is_str(act):
                act = eval(act)  # str -> function
            self.Bind(wx.EVT_TOOL, act, tbt[key])

            # UI event handler
            if uih:
                if is_str(uih):
                    uih = eval(f'tlw.updateui_{uih.lower()}')  # str -> function
                self.Bind(wx.EVT_UPDATE_UI, uih, tbt[key])

        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'TBR'))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#HACK, tweak toolbar height only
        self.SetToolBitmapSize((0, 32 if TBX['LRG_ICO'][1] else 20))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, EXAMPLE: adding PyUserData to toolbar control
#     self.SetToolClientData(TBR['PRF'], 'example of adding PyUserData to control: clientData (PyUserData)')
#     print(self.GetToolClientData(TBR['PRF']))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.Realize()

        if DEBUG['TBR'] > 1:
            print('ToolBar Items:')
            for k, v in sorted(tbt.items()):
                print('  [%-11s] = %s' % (k, v))
            print('\n')

        return tbt

    def rebuild(self):
        tlw = self.prt
        self.Destroy()
        self.__init__(tlw)
        glb.TBR = self
        tlw.SetToolBar(self)
        tlw.SendSizeEvent()
        return self
