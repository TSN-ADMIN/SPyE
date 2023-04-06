#!/usr/bin/python

"""Run application

Process startup configuration and run application:
    - window position
    - multi instance
    - global hot key
    - system tray menu
    - ui event update interval
    - ui event process specified
    - widget inspection tool
    - splash screen
    - context help button
"""


import wx
from wx import aui
from wx.lib.mixins import inspection

from common.doc import get_doc
from common.util import (
    _win_under_cursor, app_filter_event, me_, msg_box,
    register_hotkey, splash, welcome, widget_inspection_tool
)
from conf.debug import dbg_funcname_app, dbg_method_calls, DEBUG
from const import glb
import gui
import mix


# @dbg_method_calls(exclude=['FilterEvent'])
class Application(wx.App, inspection.InspectionMixin, mix.Help):
    """Application"""

    __slots__ = ['focus', 'prv_evt_typ', 'frm', 'instance', 'prv_nam']

    def __init__(self, AppFrame, APP, *args, **kwargs):
        """__init__"""
        self.ready = False
        dbg_funcname_app()
        super().__init__(*args, **kwargs)

        glb.APP = self

        self.focus = True
        self.prv_evt_typ = -1
        self.base = APP['Base']

        sec = glb.CFG['Window']

#FIX, create lists: 'Position', 'Size'
        # window position, size
        x, y, w, h = sec['PositionX'], sec['PositionY'], sec['Width'], sec['Height']

        # create application top level window
        frm = self.frm = AppFrame(None, title=self.base, pos=(x, y), size=(w, h))
        frm.SetIcon(APP['Icon'])

        # frm.SetMinSize((600, 600))

        sec = glb.CFG['General']

        # application instance running?
        if not sec['MultiInstance']:
            self.instance = wx.SingleInstanceChecker(self.base)
            if self.instance.IsAnotherRunning():
                msg = (f'Another {APP["Base"]} instance is running\n\n'
                        'Set config "[General]:MultiInstance = True" to allow more than 1 instance.\n\n'
                        'Use at your own risk.')
                msg_box(frm, 'ERROR', msg, extra=self.base)
                raise SystemExit

        # set platform global hotkey
        if register_hotkey(frm, sec['GlobalHotKey']):
            frm.Bind(wx.EVT_HOTKEY, lambda e: gui.global_hot_key(frm), id=1)
        else:
            msg = ('Unable to register global hot key\n\n'
                  f'Likely cause: key [{sec["GlobalHotKey"]}] already registered.\n\n'
                   'Modify config "[General]:GlobalHotKey".')
            msg_box(frm, 'ERROR', msg, extra=self.base)

        # taskbar menu
        if sec['SystemTrayMenu']:
            glb.STM = gui.SystemTrayMenu(frm)

        # set interval for UI update events
        wx.UpdateUIEvent.SetUpdateInterval(sec['UIEventUpdateInterval'])

#INFO, minimize overhead of UI update processing, see 'SetExtraStyle(wx.WS_EX_PROCESS_UI_UPDATES)'
#INFO, URL=https://docs.wxpython.org/wx.UpdateUIEvent.html
        if sec['UIEventProcessSpecified']:
            wx.UpdateUIEvent.SetMode(wx.UPDATE_UI_PROCESS_SPECIFIED)
        else:
            wx.UpdateUIEvent.SetMode(wx.UPDATE_UI_PROCESS_ALL)

        # initialize WIT
        if glb.CFG['WidgetInspectionTool']['Enable']:
            widget_inspection_tool()

        sec = glb.CFG['Splash']

        if sec['Welcome']:
            welcome(frm)

        if sec['Enable']:
            splash(frm, timeout=sec['DelayHide'])

#TODO, style=wx.WS_EX_CONTEXTHELP
#INFO, URL=https://docs.wxpython.org/wx.Frame.html?highlight=window%20extra%20styles#extra-styles-window-extra-styles
#NOTE, MAXIMIZE/MINIMIZE_BOX are automatically turned off if this style is used
        if glb.CFG['Help']['QuestionMarkButton']:
            frm.SetExtraStyle(wx.WS_EX_CONTEXTHELP)

#         _s = wx.BoxSizer(wx.HORIZONTAL)
# #         _s.Add(frm.nbk, 1, wx.EXPAND)
#         frm.SetSizer(_s)
#         frm.SetAutoLayout(True)

        self.SetTopWindow(frm)
        frm.Show(True)
        glb.SB.push_text('Welcome to ' + APP['Full'])

#         self.Bind(wx.EVT_ENTER_WINDOW, self.got_focus)
#         self.Bind(wx.EVT_LEAVE_WINDOW, self.lost_focus)
        self.Bind(wx.EVT_SET_FOCUS, self.got_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.lost_focus)

        self.Bind(wx.EVT_HELP, self.Help)

#FIX: get window name under mouse cursor
        if DEBUG['WNM']:
            self.Bind(wx.EVT_SET_CURSOR, lambda e: _win_under_cursor(self, e))
            self.prv_nam = None

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# test: global_char_hook
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if DEBUG['KBD']:
            self.Bind(wx.EVT_CHAR_HOOK, self.global_char_hook)

    def FilterEvent(self, evt):
        """FilterEvent"""
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if (hasattr(self, 'frm') and
        #     hasattr(self.frm, 'nbk') and
        #     hasattr(self.frm.nbk, 'CurrentPage.pnm')):
        #     print(self.frm.nbk.CurrentPage.pnm)
        #     # print(get_doc().pnm)
        # if hasattr(glb.DOC, 'pnm'):
        #     print(glb.DOC.pnm)
        #     # print(get_doc().pnm)
        #     print(glb.DOC.pnm)

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if evt.EventType == wx.EVT_UPDATE_UI.typeId:
        #     # print('bla')
        #     return self.Event_Ignore
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if DEBUG['GLB']:
            if evt.EventType == aui.EVT_AUINOTEBOOK_PAGE_CHANGING.typeId:
                print('EVT_AUINOTEBOOK_PAGE_CHANGING\n')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        return app_filter_event(self, evt)

    def global_char_hook(self, evt):
        """global_char_hook"""
        if evt.KeyCode == wx.WXK_ESCAPE:
            print(f'\nGlobal ESCAPE: {me_("A")}')
            if (cur := glb.NBK.CurrentPage):
                print(f'{cur.pnm    = }')
                print(f'{cur.spu_active = }')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#HACK: avoid error AttributeError: 'SidePanel' object has no
#            attribute 'FindItemById' in '_keyword_set_handler'
#            when using 'ENTER' on 'Choicebook.ChoiceCtrl'
        elif evt.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            print(f'Global ENTER: {me_("A")}')
#FIX, when 'evt.Skip(False)', document does NOT accept 'ENTER'
        #     evt.Skip(False)
            evt.Skip()
            return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        else:
            evt.Skip()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def got_focus(self, evt):
        """got_focus"""
#DONE, hack: unresponsive Choicebook in side panel ('Skip' needed)
        evt.Skip()
        # dbg_funcname_app()
        if DEBUG['FCS']: print(f"+{self.base}  got focus")
        self.focus = True

    def lost_focus(self, evt):
        """lost_focus"""
#DONE, hack: wx.TextCtrl focus issues in search panel ('Skip' needed)
        evt.Skip()
        # dbg_funcname_app()
        if DEBUG['FCS']: print(f"-{self.base} lost focus")
        self.focus = False

    def OnInit(self):
        """OnInit"""
        dbg_funcname_app()
        return True

    def OnInitGui(self):
        """OnInitGui"""
        dbg_funcname_app()
        return True

    def OnPreInit(self):
        """OnPreInit"""
        dbg_funcname_app()
        super().OnPreInit()
        self.ready = False

    def OnRun(self):
        """OnRun"""
        dbg_funcname_app()
        super().OnRun()
        return 0

    def OnEventLoopEnter(self, loop):
        """OnEventLoopEnter"""
        dbg_funcname_app()
        self.ready = True

    def OnEventLoopExit(self, loop):
        """OnEventLoopExit"""
        dbg_funcname_app()

    def OnExit(self):
        """OnExit"""
        dbg_funcname_app()
        return True
