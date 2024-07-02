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

from common.util import (
    get_keypress, is_shown, msg_box, register_hotkey, splash, welcome, widget_inspection_tool
)
from conf.debug import dbf, DBG, DEBUG, me_
from app.frame import AppFrame
from const.app import APP
from const import glb
import gui
import mix



# @dbf.method_calls(exclude=['FilterEvent'])
class Application(wx.App, inspection.InspectionMixin, mix.Help):
    """Application"""

    __slots__ = ['focus', 'prv_evt_typ', 'frm', 'instance', 'prv_win_nam']

    def __init__(self, *args, **kwargs):
        """__init__"""
        super().__init__(*args, **kwargs)
        mix.Help.__init__(self)

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

#INFO, minimize overhead of UI idle processing, see 'SetExtraStyle(wx.WS_EX_PROCESS_IDLE)'
#INFO, URL=https://docs.wxpython.org/wx.IdleEvent.html
        if sec['IdleEventProcessSpecified']:
            wx.IdleEvent.SetMode(wx.IDLE_PROCESS_SPECIFIED)
        else:
            wx.IdleEvent.SetMode(wx.IDLE_PROCESS_ALL)

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
        glb.SBR.push_text(f'Welcome to {APP["Info"]}')

#         self.Bind(wx.EVT_ENTER_WINDOW, self.got_focus)
#         self.Bind(wx.EVT_LEAVE_WINDOW, self.lost_focus)
        self.Bind(wx.EVT_SET_FOCUS, self.got_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.lost_focus)

#FIX: get window name under mouse cursor
        DBG('WNM==0', (self.Bind, wx.EVT_SET_CURSOR, lambda e: dbf.WIN_UNDER_CURSOR(self, e)))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: 'key_pressed' based on window that has focus
        # self.Bind(wx.EVT_CHAR_HOOK, self.key_pressed)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        DBG('KBD', (self.Bind, wx.EVT_CHAR_HOOK, self.global_char_hook))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def FilterEvent(self, evt):

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: see 'common.util.is_shown'
#INFO, GOAL: to HIDE 'InfoBar' on ANY 1st KEYPRESS
        # print(is_shown('IBR'))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        """FilterEvent"""
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if (hasattr(self, 'frm') and
        #     hasattr(self.frm, 'nbk') and
        #     hasattr(self.frm.nbk, 'CurrentPage.pnm')):
        #     print(self.frm.nbk.CurrentPage.pnm)
        # if hasattr(glb.DOC, 'pnm'):
        #     print(glb.DOC.pnm)
        #     print(glb.DOC.pnm)

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if evt.EventType == wx.EVT_UPDATE_UI.typeId:
        #     # print('bla')
        #     return self.Event_Ignore
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if self.ready:
        #     print(glb.TLW.FindFocus().Name)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # glb.DOC = None if glb.NBK and not glb.NBK.PageCount else glb.DOC
        # from const.app import COMMON_EVENTS
        # # print(self.ready, glb.DOC, COMMON_EVENTS.get(evt.EventType, ''), evt.EventObject)
        # print(glb.DOC, evt.EventObject)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if DEBUG['GLB']:
            if evt.EventType == aui.EVT_AUINOTEBOOK_PAGE_CHANGING.typeId:
                print('EVT_AUINOTEBOOK_PAGE_CHANGING\n')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        return dbf.APP_FILTER_EVENT(self, evt)

    @staticmethod
    def _DBG(ready):
        DBG('APP==2', f'APP: {ready = !r:<5} {me_("F")} -> {me_("F", lvl=2)}')

    def OnPreInit(self):
        """OnPreInit"""
        super().OnPreInit()
        self.ready = False
        self._DBG(self.ready)

    def OnInit(self):
        """OnInit"""
        self.ready = True
        self._DBG(self.ready)
        return True

    def OnEventLoopEnter(self, loop):
        """OnEventLoopEnter"""
        if self.ready:
            self.frm.Show(True)
        self._DBG(self.ready)

    def OnEventLoopExit(self, loop):
        """OnEventLoopExit"""
        self.ready = False
        self._DBG(self.ready)

    def OnExit(self):
        """OnExit"""
        self._DBG(self.ready)
        return True

    def OnInitGui(self):
        """OnInitGui"""
        return True

    def OnRun(self):
        """OnRun"""
        super().OnRun()
        return 0

    def global_char_hook(self, evt):
        """global char hook to catch e.g. ESCAPE and ENTER keys"""
        evt.Skip()
        cod = evt.KeyCode
        # print(cod, glb.TLW.FindFocus(), glb.TLW.FindFocus().Name)
        if cod == wx.WXK_ESCAPE:
            print(f'\nGlobal ESCAPE: {me_("A")}')
            if (cur := glb.NBK.CurrentPage):  # .txt1):
                print(f'{cur.pnm        = }')
                print(f'{cur.spu_active = }')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#HACK, avoid error AttributeError: 'SidePanel' object has no
#            attribute 'FindItemById' in '_keyword_set_handler'
#            when using 'ENTER' on 'Choicebook.ChoiceCtrl'
        elif cod in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            print(f'Global ENTER: {me_("A")}')
#DONE, with 'evt.Skip(False)', document does NOT accept 'ENTER'
            # evt.Skip()
            return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # else:
        #     evt.Skip()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def got_focus(self, evt):
        """got_focus"""
#DONE, hack: unresponsive Choicebook in side panel ('Skip' needed)
        evt.Skip()
        DBG('FCS', f'+{self.base}  got focus')
        self.focus = True

    def lost_focus(self, evt):
        """lost_focus"""
#DONE, hack: wx.TextCtrl focus issues in search panel ('Skip' needed)
        evt.Skip()
        DBG('FCS', f'-{self.base} lost focus')
        self.focus = False

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: 'key_pressed' based on window that has the focus
    def key_pressed(self, evt):

        evt.Skip()  # let Scintilla process key

        kpr_sct, nam, __ = get_keypress(evt)

        print(f'{me_()}: [{nam:>3}] {kpr_sct} -> Focus on: {self.frm.FindFocus().Name}')

        if not kpr_sct:
            return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
