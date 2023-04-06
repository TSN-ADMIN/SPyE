#!/usr/bin/python

import wx

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TSN, #NOTE, 'extern.shortcuteditor' needs dependencies:
#TSN, #        'genericmessagedialog.py', 'hypertreelist.py'
#TSN, #      in 'extern' OR 'from wx.lib.agw import ...'
#TSN, # import extern.shortcuteditor as SCE
from wx.lib.agw import shortcuteditor as SCE
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

from ._load import _load
from common.doc import get_doc
from common.file import get_file_icon
from common.util import is_shown, me_, set_icon
from conf.debug import DEBUG, dbg_FOCUS
from conf.lang import SyntaxStyling
from const import glb
from const.app import APP
from const.common import SASH_POS
from const.menu import MI
import gui


@_load
class Layout:

    def panel_effect_choice(self, evt):
        obj = evt.EventObject

#INFO, URL=https://docs.wxpython.org/wx.ShowEffect.enumeration.html
        # use menu item 'None' as base id '0', it equals 'wx.SHOW_EFFECT_NONE'
        chc = evt.Id - int(MI['PEF_NON'])
        # menu item order syncs choice with any 'wx.SHOW_EFFECT_*' value
        glb.CFG['PanelEffect']['Choice'] = chc

    def panel_effect_duration(self, evt):
        dur = str(glb.CFG['PanelEffect']['Duration'])
        with wx.TextEntryDialog(self, 'Enter number (millis):', 'Panel effect duration', dur) as dlg:
            set_icon(dlg)
            if (res := dlg.ShowModal()) == wx.ID_OK:
                dur = int(dlg.Value)
                glb.CFG['PanelEffect']['Duration'] = dur

    def show_preferences(self, evt):
        dlg = gui.Preferences(self)
#TODO, handle buttons inside or outside 'Preferences' class?
        res = dlg.ShowModal()

    def show_menu_editor(self, evt):
        dlg = gui.MenuEditor(self)
        res = dlg.Show()

    def show_shortcut_editor(self, evt):
#FIX, search filter not working
        dlg = SCE.ShortcutEditor(self)
        dlg.FromMenuBar(self)
        if (res := dlg.ShowModal()) == wx.ID_OK:
            # changes accepted, send new shortcuts back to TLW wx.MenuBar
            dlg.ToMenuBar(self)
        dlg.Destroy()

    def show_syntax_styling(self, evt):
        if not (doc := get_doc()): return
        dlg = SyntaxStyling(doc)
        set_icon(dlg)
        res = dlg.ShowModal()

    def toggle_panel(self, evt, pnl, neg):
        print(f'{me_("F")}: {pnl}')
        spl = glb.SPL[pnl]
        pos = SASH_POS[pnl][glb.SCH.mode] if pnl == 'SCH' else SASH_POS[pnl]
        if DEBUG['SAS']: print(f'   IN: [{spl.swap = !r:>5}], [{is_shown(pnl) = !r:>5}]')
        if is_shown(pnl):
            if spl.swap:
                spl.swap_windows()
            spl.unsplit_windows()
        else:
            spl.split_windows(neg * pos)
        spl.swap = False
        if DEBUG['SAS']: print(f'  OUT: [{spl.swap = !r:>5}], [{is_shown(pnl) = !r:>5}]')

    def reset_panel(self, pnl, neg):
        print(f'{me_("F")}: {pnl}')
        [self.toggle_panel(None, pnl, neg) for __ in range(2)]  #twice ...

    def swap_panel(self, evt, pnl, neg=None):
        print(f'{me_("F")}: {pnl}')
        if not is_shown(pnl):
            return
        spl = glb.SPL[pnl]
        pos = SASH_POS[pnl][glb.SCH.mode] if pnl == 'SCH' else SASH_POS[pnl] if pnl == 'RLR' else spl.SashPosition
        if neg is None:
            if pnl in 'RLR':
                neg = 1 if spl.swap else -1
            elif pnl in 'SCH':
                neg = -1 if spl.swap else 1
        if DEBUG['SAS']: print(f'   IN: [{spl.swap = !r:>5}], [{pos = !r:>5}]')
        spl.unsplit_windows()
        spl.swap_windows()
        spl.split_windows(neg * pos)
        spl.swap = not spl.swap
        if DEBUG['SAS']: print(f'  OUT: [{spl.swap = !r:>5}], [{pos = !r:>5}]')

    def reset_side_panel(self, evt):
        if not is_shown('SPN'):
            return
        if DEBUG['GLB']: print(f' MAIN: {id(glb.DOC) = } -> {glb.DOC.fnm = }')
        self.reset_panel('SPN', -1)

    def toggle_autocomplete(self, evt):
        glb.CFG['AutoComplete']['Enable'] = evt.IsChecked()

    def toggle_calltips(self, evt):
        glb.CFG['CallTip']['Enable'] = evt.IsChecked()

    def toggle_colour_tooltip(self, evt):
        glb.CFG['ColourToolTip']['Enable'] = evt.IsChecked()

    def toggle_distraction_free(self, evt):
        if not (doc := get_doc()): return
        # enable/disable 'fullscreen'
        glb.MB.Enable(MI['LAY_FUL'], bool(self.IsFullScreen()))
        flg = wx.FULLSCREEN_ALL
        self.Freeze()
#DONE, hide/show page tabs
        if not self.IsFullScreen():
            glb.NBK.SetTabCtrlHeight(0)
        else:
            glb.NBK.SetTabCtrlHeight(-1 if glb.MB.IsChecked(MI['LAY_PTB']) else 0)
#FIX, menu and shortcuts NOT accessible, use accelerator table
        # glb.MB.Check(MI['LAY_DFM'], glb.MB.IsChecked(MI['LAY_DFM']))
        self.ShowFullScreen(not self.IsFullScreen(), flg)
        doc.SetUseHorizontalScrollBar(False if self.IsFullScreen() else glb.CFG['Editor']['HorizontalScrollBar'])
        doc.SetUseVerticalScrollBar(False if self.IsFullScreen() else glb.CFG['Editor']['VerticalScrollBar'])
        # unsplit/split side panel to force default sash position
#FIX, needs better coding...
        self.maximize(None)
        self.Thaw()

    def toggle_fullscreen(self, evt):
        # enable/disable 'distraction free mode'
        glb.MB.Enable(MI['LAY_DFM'], bool(self.IsFullScreen()))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, default: no flags = wx.FULLSCREEN_ALL
        flg = 0
#         flg |= wx.FULLSCREEN_ALL
        flg |= wx.FULLSCREEN_NOBORDER
        flg |= wx.FULLSCREEN_NOCAPTION
#         flg |= wx.FULLSCREEN_NOMENUBAR
        flg |= wx.FULLSCREEN_NOTOOLBAR
#         flg |= wx.FULLSCREEN_NOSTATUSBAR
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, fullscreen with staticbox/label: '...F11 to return'
#         if not self.IsFullScreen():
#             self.sbs = wx.StaticBoxSizer(wx.StaticBox(self, label=' Full Screen (F11 to return) '))
#             self.SetSizer(self.sbs)
#             self.Layout()
#         else:
#             del self.sbs
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.Freeze()
        glb.MB.Check(MI['LAY_FUL'], glb.MB.IsChecked(MI['LAY_FUL']))
        self.ShowFullScreen(not self.IsFullScreen(), flg)
        # unsplit/split side panel to force default sash position
#FIX, needs better coding...
        self.maximize(None)
        self.Thaw()

#FIX, review and test colour change
        if self.IsFullScreen():
            glb.SB.SetBackgroundColour(glb.CFG['StatusBar']['FullScreenBackColour'])
            glb.SB.set_text('Full Screen (F11 to return)')
        else:
            glb.SB.SetBackgroundColour(glb.CFG['StatusBar']['BackColour'])

    def toggle_caption(self, evt):
        glb.MB.Check(evt.Id, evt.IsChecked())
        sty, cap = self.WindowStyle, wx.CAPTION
        self.SetWindowStyle(sty & ~cap if sty & cap else sty | cap)

    def toggle_menu_item(self, evt):
        if (id_ := evt.Id) == MI['LAY_MIC']:
            glb.MB.ico = not glb.MB.ico
        elif id_ == MI['LAY_MIK']:
            glb.MB.icc = not glb.MB.icc
        elif id_ == MI['LAY_MHT']:
            # glb.CFG['Layout']['MenuHelpText'] = not glb.CFG['Layout']['MenuHelpText']
            glb.MB.hlp = not glb.MB.hlp
        glb.MB.rebuild_menubar(self)

    def toggle_menubar(self, evt):
        glb.MB.Check(evt.Id, evt.IsChecked())
        self.SetMenuBar(None if glb.MB.IsAttached() else glb.MB)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def toggle_infobar(self, evt):
        # glb.IB.Show(evt.IsChecked())
        # self.SendSizeEvent()
        pass
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def toggle_page_tabs(self, evt):
        glb.NBK.SetTabCtrlHeight(0 if glb.NBK.TabCtrlHeight else -1)

    def toggle_page_tab_icons(self, evt):
        for pag, doc in glb.NBK.open_docs():
            ico = get_file_icon(doc.lng_typ)
            glb.NBK.SetPageBitmap(pag, ico)

    def toggle_page_tab_theme(self, evt):
        thm = 'DEFAULT' if evt.IsChecked() else 'SIMPLE'
        glb.CFG['Notebook']['ArtProviderTheme'] = thm
        glb.NBK.set_theme(thm)

    def toggle_statusbar(self, evt):
        glb.SB.Show(evt.IsChecked())
        self.SendSizeEvent()

#INFO, URL=http://wxpython-users.1045709.n5.nabble.com/Hide-Remove-a-Toolbar-td2316942.html
    def toggle_toolbar(self, evt):
        glb.TB.Show(evt.IsChecked())
#NOTE, 2017-07-07 07:06:34, also solved for statusbar
        self.SendSizeEvent()

    def toggle_tooltips(self, evt):
        if not (doc := get_doc()): return

#TODO, process NOT just TOOLBAR tooltips, ALSO:
#TODO, 'Notebook' tabs, 'Splitter', 'StatusBar', 'DocMap', 'Toplinetooltip', 'SearchPanel'

        glb.NBK.update_page_tab(doc)

        sty = glb.TB.WindowStyle
        if sty & wx.TB_NO_TOOLTIPS:
            glb.TB.SetWindowStyle(sty & ~wx.TB_NO_TOOLTIPS)
        else:
            glb.TB.SetWindowStyle(sty | wx.TB_NO_TOOLTIPS)

        wx.ToolTip.Enable(glb.MB.IsChecked(MI['LAY_TTP']))

    def toggle_topline_tooltip(self, evt):
#FIX, does not globally enable/disable
        glb.NBK.tlt.EnableTip(bool(glb.MB.IsChecked(evt.Id)))

    def toggle_symbol_popup(self, evt):
        glb.CFG['SymbolPopup']['Enable'] = evt.IsChecked()
