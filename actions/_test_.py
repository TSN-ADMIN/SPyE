#!/usr/bin/python

# pylint: disable=W0212(protected-access) [_colourSchemes]

import wx

from ._load import _load
from common.doc import get_doc
from common.util import make_modal, set_icon
from const.editor import MRK
from const import glb
from const.lang import LANG
import extern.supertooltip as STT
import gui

@_load
class Test____:


    def CtxTEST1(self, evt):
        if not (doc := get_doc()): return

        for lin in range(10):
            doc.MarkerAdd(lin, MRK['BMK']['NUM'])  # (lin, lin)
        for lin in range(10):
            print(doc.GetMarkerSymbolDefined(lin))
        if (ctl := gui.get_spt('BMK')):
            ctl.update_list(doc)


    def CtxTEST2(self, evt):
        if not (doc := get_doc()): return

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         for i in range(10):
#             doc.MarkerDefineBitmap(i, PNG['bmark' + str(i)].Bitmap)
#             doc.MarkerDefine(i, stc.STC_MARK_CHARACTER+48+i) #, foreground,background)
# #             doc.MarkerDelete(i, i)
# #         doc.MarkerDeleteAll(-1)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        pos = cur = doc.CurrentPos
        prs = glb.CFG['Brace']['Pairs']
        mid = len(prs) // 2  # distance between open/close brace
        brc_open, brc_close = prs[:mid], prs[mid:]

        brc = 0
        while pos >= 0 and cur - 2000000 <= pos <= cur:
            pos -= 1

            # print(pos, chr(doc.GetCharAt(pos)))
            ch = chr(doc.GetCharAt(pos))
            if ch in brc_close:
                brc += 1
            elif ch in brc_open:
                if brc == 0:
                    break
                brc -= 1
            print(pos, ch, brc)

        print(pos, ch, brc)

        if pos == -1:
            print(f'NOT found (within limit)')
        elif brc == 0:
            print(f'open brace "{ch}" found at {pos}')
        elif brc > 0:
            print(f'NOT found (mismatch)')


#INFO, copied from wxPyWiki, 'Customized frame (Phoenix)', 'sample_seven.py'
#INFO, URL=https://wiki.wxpython.org/Customized%20frame%20%28Phoenix%29
    def CtxTEST3(self, evt):
        sty = wx.CAPTION | wx.CLOSE_BOX
        dlg = wx.Dialog(self, title='Editor Background Colour', style=sty)
        set_icon(dlg)
        make_modal(dlg, True)

        #------------------------------------------------------------------------------------------

        # colours used in SPyE
        SPYE_COLOURS = [
            '#000000',
            '#0000FF',
            '#006400',
            '#00FF00',
            '#3399FF',
            '#71B3E8',
            '#A9A9A9',
            '#C0C0C0',
            '#C6E2FF',
            '#CCFFCC',
            '#D7FFD7',
            '#E6F2FF',
            '#EAD5FF',
            '#ECFFEC',
            '#F0F0F0',
            '#FF0000',
            '#FF6060',
            '#FF8000',
            '#FFBBAA',
            '#FFD5AA',
            '#FFDDDD',
            '#FFE7CE',
            '#FFFFD0',
            '#FFFFF0',
            '#FFFFFF',
        ]

        #------------------------------------------------------------------------------------------

        # predefined named colours from colourdb
        COLOURDB_PREDEFINED_COLOURS = [
            'BLACK',
            'BLUE',
            'SLATE BLUE',
            'GREEN',
            'SPRING GREEN',
            'CYAN',
            'NAVY',
            'STEEL BLUE',
            'FOREST GREEN',
            'SEA GREEN',
            'DARK GREY',
            'MIDNIGHT BLUE',
            'DARK GREEN',
            'DARK SLATE GREY',
            'MEDIUM BLUE',
            'SKY BLUE',
            'LIME GREEN',
            'MEDIUM AQUAMARINE',
            'CORNFLOWER BLUE',
            'MEDIUM SEA GREEN',
            'INDIAN RED',
            'VIOLET',
            'DARK OLIVE GREEN',
            'DIM GREY',
            'CADET BLUE',
            'MEDIUM GREY',
            'DARK SLATE BLUE',
            'MEDIUM FOREST GREEN',
            'SALMON',
            'DARK TURQUOISE',
            'AQUAMARINE',
            'MEDIUM TURQUOISE',
            'MEDIUM SLATE BLUE',
            'MEDIUM SPRING GREEN',
            'GREY',
            'FIREBRICK',
            'MAROON',
            'SIENNA',
            'LIGHT STEEL BLUE',
            'PALE GREEN',
            'MEDIUM ORCHID',
            'GREEN YELLOW',
            'DARK ORCHID',
            'YELLOW GREEN',
            'BLUE VIOLET',
            'KHAKI',
            'BROWN',
            'TURQUOISE',
            'PURPLE',
            'LIGHT BLUE',
            'LIGHT GREY',
            'ORANGE',
            'VIOLET RED',
            'GOLD',
            'THISTLE',
            'WHEAT',
            'MEDIUM VIOLET RED',
            'ORCHID',
            'TAN',
            'GOLDENROD',
            'PLUM',
            'MEDIUM GOLDENROD',
            'RED',
            'ORANGE RED',
            'MAGENTA',
            'LIGHT MAGENTA',
            'CORAL',
            'PINK',
            'YELLOW',
            'WHITE',
        ]

        # SPYE_COLOURS.extend(COLOURDB_PREDEFINED_COLOURS)

        #------------------------------------------------------------------------------------------

        # all colours from colourdb
        COLOURDB_ALL_COLOURS = wx.lib.colourdb.getColourList()

        # SPYE_COLOURS.extend(COLOURDB_ALL_COLOURS)

        #------------------------------------------------------------------------------------------

        # colours defined by system
        SYSTEM_COLOURS = []
        pfx = 'SYS_COLOUR_'
        for nam in dir(wx):
            if nam.startswith(pfx):
                cod = getattr(wx, nam)
                SYSTEM_COLOURS.append(wx.SystemSettings.GetColour(cod).GetAsString())
        del cod, nam

        # SPYE_COLOURS.extend(SYSTEM_COLOURS)

        #------------------------------------------------------------------------------------------

        # colour scheme colours from STT
        # import extern.supertooltip as STT
        SUPERTOOLTIP_COLOURS = []
        for clr_lst in STT._colourSchemes.values():
            for clr in clr_lst:
                clr = wx.Colour(clr.GetRGBA()).GetAsString(flags=wx.C2S_CSS_SYNTAX)
                SUPERTOOLTIP_COLOURS.append(clr)

        # SPYE_COLOURS.extend(SUPERTOOLTIP_COLOURS)

        #------------------------------------------------------------------------------------------

        def __on_choice(evt, chc):
            # selection label text
            bgc = chc.StringSelection
            glb.CFG['Editor']['DefaultBackColour'] = bgc

            # same background colour in all documents
            for __, doc in glb.NBK.open_docs():
                # get language based on file extension
                lng_lst = [e for e in LANG if doc.ext in e[3].split('|')]
                doc.update_language_styling(lng_lst)

            # glb.TB.SetBackgroundColour(bgc)
            # glb.TB.Realize()

        def __on_exit(evt):
            make_modal(dlg, False)
            dlg.Destroy()

        #------------------------------------------------------------------------------------------

        chc = wx.Choice(dlg,
                        -1,
                        pos=(-1, -1),
                        size=(200, -1),
                        choices=SPYE_COLOURS,
                        # choices=COLOURDB_PREDEFINED_COLOURS,
                        # choices=COLOURDB_ALL_COLOURS,
                        # choices=SYSTEM_COLOURS,
                        # choices=SUPERTOOLTIP_COLOURS,
                        style=wx.CB_SORT)

        chc.SetSelection(141)
        chc.Bind(wx.EVT_CHOICE, lambda e: __on_choice(e, chc))
        dlg.Bind(wx.EVT_CLOSE, __on_exit)

        bxh = wx.BoxSizer(wx.HORIZONTAL)
        bxh.Add(chc, 1, wx.ALIGN_CENTRE_HORIZONTAL)
        dlg.SetSizer(bxh)
        dlg.Sizer.Fit(dlg)
        dlg.Centre()
        dlg.Show()


    def CtxTEST4(self, evt):
        import __main__
        THM = __main__.THM

        sty = wx.CAPTION | wx.CLOSE_BOX
        dlg = wx.Dialog(self, title='Application Theme Selector', style=sty)
        set_icon(dlg)
        make_modal(dlg, True)

        #------------------------------------------------------------------------------------------

        def __on_choice(evt, chc):
            def __set_cfg_in_open_docs():
#FIX, APP CRASH after selecting them colour
                # same config value in all open documents
                for __, doc in glb.NBK.open_docs():
                    # get language based on file extension
                    lng_lst = [e for e in LANG if doc.ext in e[3].split('|')]
                    doc.update_language_styling(lng_lst)

            # selection label text
            lbl = chc.StringSelection
            glb.CFG['General']['Theme'] = lbl
            sec = THM[lbl]

            for key in sec:
                obj, itm = key.split('|')
                val = sec[key]
                print(obj, itm, val)

                if obj == 'ToolBar':
                    glb.CFG[obj]['BackColour'] = val
                    glb.TB.SetBackgroundColour(val)
                elif obj == 'StatusBar':
                    #@@@@@@@@@@@@@@@@@@@@@@@@@
                    # update statusbar
                    glb.SB.Destroy()
                    del glb.SB
                    glb.SB = gui.StatusBar(self)
                    self.SetStatusBar(glb.SB)
                    #@@@@@@@@@@@@@@@@@@@@@@@@@
                    glb.CFG[obj]['BackColour'] = val
                    glb.SB.SetBackgroundColour(val)
                elif obj == 'Editor':
                    glb.CFG[obj]['DefaultBackColour'] = val
                    __set_cfg_in_open_docs()
                elif obj == 'Margin':
                    glb.CFG[obj][itm] = val
                    __set_cfg_in_open_docs()
                elif obj == 'SearchPanel':
                    glb.CFG[obj][itm] = val
                    glb.SCH.SetBackgroundColour(val)

            # breakpoint()

        def __on_exit(evt):
            make_modal(dlg, False)
            dlg.Destroy()

        #------------------------------------------------------------------------------------------

        chc = wx.Choice(dlg,
                        -1,
                        pos=(-1, -1),
                        size=(200, -1),
                        choices=list(THM),
                        # style=wx.CB_SORT)
                        )

        chc.SetSelection(0)

        chc.Bind(wx.EVT_CHOICE, lambda e: __on_choice(e, chc))
        dlg.Bind(wx.EVT_CLOSE, __on_exit)

#HACK: map hidden OK button to ENTER key
        btn_ok_ = wx.Button(dlg, wx.ID_OK, size=(0, 0))
        btn_ok_.SetDefault()
        btn_ok_.Bind(wx.EVT_BUTTON, __on_exit)

#HACK: map hidden cancel button to ESCAPE key
        btn_esc = wx.Button(dlg, wx.ID_CANCEL, size=(0, 0))
        dlg.SetEscapeId(wx.ID_CANCEL)
        btn_esc.Bind(wx.EVT_BUTTON, __on_exit)

        bxh = wx.BoxSizer(wx.HORIZONTAL)
        bxh.Add(chc, 1, wx.ALIGN_CENTRE_HORIZONTAL)
        dlg.SetSizer(bxh)
        dlg.Sizer.Fit(dlg)
        dlg.Centre()
        dlg.Show()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# temporary code: top level menu
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def TESTMETHOD(self, evt):
        # if not (doc := get_doc()): return

        mb = glb.MB

        mb.EnableTop(mb.FindMenu('{{TEST1}}'), False)
        mb.EnableTop(mb.FindMenu('{{TEST2}}'), False)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# temporary code: top level menu
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE: test nested level tree in 'SymbolTree'
def lvl11():
    pass
def lvl12():
    pass
def lvl13():
    pass
    def __bla():
        pass
        def __bla():
            pass
            def __bla():
                pass
                def __bla():
                    pass
                    def __bla():
                        pass
                        def __bla():
                            pass
                            def __bla():
                                pass
                                def __bla():
                                    pass
                                    def __bla():
                                        pass
                                        # def __bla():
                                        #     pass
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
