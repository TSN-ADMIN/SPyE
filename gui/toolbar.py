#!/usr/bin/python

import wx

from conf.debug import (
    DEBUG, dbg_CTXTTB,
)
from common.type import is_str
from common.util import me_, not_implemented
from const.common import TXT_NIL
from const import glb
from const.menu import NO_ICO, NO_KND, NO_UIH
from const.toolbar import TB, TBX
from data.images import catalog as PNG
import gui


#INFO, see: contrib/TestFloatBar.7z  (needs: wx.lib.floatbar)

class ToolBar(wx.ToolBar):

    __slots__ = ['CFG', 'sec', 'prt']

    def __init__(self, prt, *args, **kwargs):
        self.sec = glb.CFG['ToolBar']
        sty = wx.TB_HORIZONTAL | wx.BORDER_MASK
        super().__init__(prt, style=sty, name='ToolBar')
        self.prt = prt

#INFO, URL=https://docs.wxpython.org/wx.ToolBar.html
        wx.SystemOptions.SetOption('msw.remap', 0)

        self.ttd = self.tool_defs(self.prt)
        self.style()
        self.create()

    def tool_defs(self, tlw):
#NOTE, a TOOLBAR TOOL shares the SAME id with its corresponding MENU ITEM
#INFO, URL=http://wxpython-users.1045709.n5.nabble.com/Binding-mouse-clicks-to-toolbar-button-td2353483.html
        TTD = {
            # 'SEP': (None, None, 'Separator'),
            'NEW': ('New', tlw.file_new, 'New', 'new', NO_KND, NO_UIH, TB['NEW']),
            'OPN': ('Open', tlw.file_open, 'Open', 'open', NO_KND, NO_UIH, TB['OPN']),
            'SAV': ('Save', tlw.file_save, 'Save', 'save', NO_KND, 'Mod', TB['SAV']),
            'SAS': ('SaveAs', tlw.file_save_as, 'Save As', 'save_as', NO_KND, 'Doc', TB['SAS']),
            'CLS': ('Close', tlw.file_close, 'Close', 'close', NO_KND, 'Doc', TB['CLS']),
            'CUT': ('Cut', tlw.edit_clipboard, 'Cut', 'cut', NO_KND, 'Sel', TB['CUT']),
            'CPY': ('Copy', tlw.edit_clipboard, 'Copy', 'copy', NO_KND, 'Sel', TB['CPY']),
            'PST': ('Paste', tlw.edit_clipboard, 'Paste', 'paste', NO_KND, 'Doc', TB['PST']),
            'UDO': ('Undo', tlw.edit_undo, 'Undo', 'undo', NO_KND, 'Doc', TB['UDO']),
            'RDO': ('Redo', tlw.edit_redo, 'Redo', 'redo', NO_KND, 'Doc', TB['RDO']),
            'FND': ('Find', tlw.set_search_mode_find, 'Find', 'find', NO_KND, 'Doc', TB['FND']),
            'NXT': ('Next', tlw.search_find_next, 'Find Next', 'find_next', NO_KND, 'Sch', TB['NXT']),
            'RPL': ('Replace', tlw.set_search_mode_replace, 'Replace', 'replace', NO_KND, 'Doc', TB['RPL']),
            'PRV': ('Prev', tlw.search_find_previous, 'Find Previous', 'find_prev', NO_KND, 'Sch', TB['PRV']),
            'FXP': ('Explore', tlw.view_side_panel_tool, 'File Explorer', 'explorer', NO_KND, 'Doc', TB['FXP']),
            'SDF': ('Symbols', tlw.view_side_panel_tool, 'Symbol Defs', 'symbol_defs', NO_KND, 'Doc', TB['SDF']),
            'BRC': ('Brace', tlw.do_brace_match, 'Brace Match', 'brace_match', NO_KND, 'Doc', TB['BRC']),
            'SRT': ('Sort', tlw.edit_sort_lines, 'Sort', 'sort', NO_KND, 'Sel', TB['SRT']),
            'SUM': ('Sum', tlw.edit_calc_sum_of_text, 'Sum', 'calc_sum', NO_KND, 'Sel', TB['SUM']),
            'FUL': ('Full', tlw.toggle_fullscreen, 'Full Screen', 'fullscreen', NO_KND, NO_UIH, TB['FUL']),
            'PRF': ('Prefs', tlw.show_preferences, 'Preferences', 'prefs', NO_KND, NO_UIH, TB['PRF']),
            'SCH': ('Search', not_implemented, 'Search', NO_ICO, NO_KND, NO_UIH, TB['SCH']),
        }
        return TTD

    def style(self):
        self.SetBackgroundColour(self.sec['BackColour'])
        sty = self.WindowStyle

        # get context menu item check marks from config
        dbg_CTXTTB('B', TBX, glb.CFG)
        TBX['SHW_ICO'][1] = self.sec['ShowIcons']
        TBX['SHW_TXT'][1] = self.sec['ShowText']
        TBX['LRG_ICO'][1] = self.sec['LargeIcons']
        TBX['LRG_TXT'][1] = self.sec['LargeText']
        TBX['ALN_HOR'][1] = self.sec['AlignHorizontally']
        TBX['LOC_TOP'][1] = self.sec['Top']
        TBX['LOC_LFT'][1] = self.sec['Left']
        TBX['LOC_BOT'][1] = self.sec['Bottom']
        TBX['LOC_RIT'][1] = self.sec['Right']
        dbg_CTXTTB('A', TBX, glb.CFG)

        # prepare toolbar: style, font, bitmap size
        if not TBX['SHW_ICO'][1]:
            sty |= wx.TB_NOICONS

        if TBX['SHW_TXT'][1]:
            sty |= wx.TB_TEXT

        if TBX['LRG_ICO'][1]:
            self.SetToolBitmapSize((24, 24) if TBX['LRG_ICO'][1] else (16, 16))
            sfx = '_24' if TBX['LRG_ICO'][1] else ''  # suffix
            for key, itm in self.ttd.items():
                # search control has no dedicated icon
                if key == 'SCH':
                    continue
                __, __, __, ico, __, __, id_ = itm
                self.SetToolNormalBitmap(id_, PNG[ico + sfx].Bitmap)

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
            print('__do_search: ' + tbs.GetValue())

        tlw = glb.TLW
        tbt = {}

        # rebuild toolbar tools from config
        for key in self.sec['Tools']:
            if key == 'SEP':
                self.AddSeparator()
                continue

#TODO, process text entered in 'tbs', implement functionality in handlers above
            if key == 'SCH':
                tbs = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # ctx_lst = list(tlw.ctx['TSK'])  # tuple -> list

                # mnu_ctx = glb.MB.build_submenu(tbs, ctx_lst)
                # tbs.SetMenu(mnu_ctx)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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

            sfx = '_24' if TBX['LRG_ICO'][1] else ''  # suffix
            tbt[key] = self.AddTool(id_, ttl, PNG[ico + sfx].Bitmap, wx.NullBitmap, wx.ITEM_NORMAL, hlp, hlp)

            # add action
            if is_str(act):
                act = eval(act)  # str -> function
            self.Bind(wx.EVT_TOOL, act, tbt[key])

            # UI event handler
            if uih:
                if is_str(uih):
                    # add handler prefix
                    uih = f'tlw.updateui_{uih.lower()}'
                    uih = eval(uih)  # str -> function
                self.Bind(wx.EVT_UPDATE_UI, uih, tbt[key])

        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'TBR'))


#INFO, EXAMPLE: adding PyUserData to toolbar control
#     self.SetToolClientData(TB['PRF'], 'example of adding PyUserData to control: clientData (PyUserData)')
#     print(self.GetToolClientData(TB['PRF']))

        self.Realize()

        if DEBUG['TBR'] > 1:
            print('ToolBar Items:')
            for k, v in sorted(tbt.items()):
                print('  [%-11s] = %s' % (k, v))
            print('\n')

    def rebuild(self):
        tlw = self.prt
        self.Destroy()
        del self
        glb.TB = self = ToolBar(tlw)
        tlw.SetToolBar(self)
        tlw.SendSizeEvent()


####################################################################################################
# R&D for extra tooltip functionality (eg. colour)
####################################################################################################

    # def bla(self, evt):

    #     import commctrl
    #     import win32gui

    #     # import win32ui

    #     # from ctypes import c_void_p, POINTER, sizeof, Structure
    #     # from ctypes.wintypes import UINT, HWND, RECT, HINSTANCE, LPWSTR, LPARAM

# ##################################################

#         def print_HWND():
#             print(f'{HWND_fr = }')  # frame
#             print(f'{HWND_tb = }')  # toolbar
#             print(f'{HWND_tt = }')  # tooltip control (toolbar association)
#             print(f' {cnt_tt = }')  # # toolbar tools (buttons)

#         def print_TOOLINFO(ti):
#             print(f'\n{"="*12}')
#             print(f'        {ti = }')
#             for nam, typ in ti._fields_:
#                 print(f'{nam:>10} = {getattr(ti, nam)}')

# ##################################################

#         class TOOLINFO(Structure):
#             _fields_ = [('cbSize',     UINT),
#                         ('uFlags',     UINT),
#                         ('hwnd',       HWND),
#                         ('uId',        PUINT),
#                         ('rect',       RECT),
#                         ('hinst',      HINSTANCE),
#                         ('lpszText',   LPWSTR),
#                         ('lParam',     LPARAM),
#                         ('lpReserved', c_void_p)]

# ##################################################

#         HWND_fr = tlw = glb.TLW.Handle
#         HWND_tb = self.Handle
#         HWND_tt = win32gui.SendMessage(HWND_tb, commctrl.TB_GETTOOLTIPS, 0, 0)
#         cnt_tt = win32gui.SendMessage(HWND_tt, commctrl.TTM_GETTOOLCOUNT, 0, 0)

#         print_HWND()

#         ti = TOOLINFO()

#         ti.uId = PUINT(UINT(23))
#         ti.hwnd = 999999999999999999
#         # id = UINT(23)
#         # ti.uId = PUINT(id)

#         print_TOOLINFO(ti)

# ##################################################

#         # ti = TOOLINFO()  # test: clear struct, works

#         ti.uId = PUINT(UINT(99))

#         print_TOOLINFO(ti)

#         # txt = ''
#         # ti.cbSize = sizeof(ti)
#         # ti.uFlags = xxx
#         # ti.hwnd =
#         # ti.uId =
#         # ti.rect =
#         # ti.hinst =
#         # ti.lpszText =
#         # ti.lParam =
#         # ti.lpReserved =


#         # win32gui.SendMessage(HWND_tt, commctrl.TTM_GETTEXT, 256, ti_buffer)

# ##################################################

        # def _get_child_win(hwnd, param):
        #     print(hwnd, win32gui.GetWindowText(hwnd))
        #     return True

        # # print(win32ui.GetActiveWindow())
        # print(win32gui.EnumChildWindows(HWND_tb, _get_child_win, None))

##################################################

        # # send() definition from PythonInfo wiki FAQs
        # def send(self):
        #     return buffer(self)[:]

        # txt = ''
        # ti.cbSize = sizeof(ti)
        # ti.uFlags = xxx
        # ti.hwnd =
        # ti.uId =
        # ti.rect =
        # ti.hinst =
        # ti.lpszText =
        # ti.lParam =
        # ti.lpReserved =


        # ti = TOOLINFO()
        # ti.cbSize = sizeof(ti)
        # ti.lpszText = txt                 # buffer to store text in
        # # ti.uId = POINTER(UINT(wnd))        # wnd is the handle of the tooltip
        # # ti.hwnd = w_wnd                    # w_wnd is the handle of the window containing the tooltip
        # ti.uFlags = commctrl.TTF_IDISHWND  # specify that uId is the control handle
        # # ti_buffer = send(ti)               # convert to buffer for pywin32

        # del(ti)

        # # win32gui.SendMessage(HWND_tt, commctrl.TTM_GETTEXT, 256, ti_buffer)

        # ti = TOOLINFO()              # create new TOOLINFO() to copy result to

        # # # copy result (according to linked article from Jeremy)
        # # memmove(addressof(ti), ti_buffer, sizeof(ti))

        # if ti.lpszText:
        #     print(ti.lpszText)          # print any text recovered from the tooltip

##################################################

        # obj = evt.EventObject
        # pprint(obj.Type)
        # pprint(dir(evt))
        # print(evt.EventObject, evt.ClassInfo)
        # print(evt.Id, evt.GetClientObject())
        # import win32ui
        # print(win32ui.GetActiveWindow())
        # print(win32gui.EnumChildWindows(HWND_tb, None, None))
        # status, msg = win32gui.PeekMessage(0, 0, 0, 0)
        # # if msg[1] in TTM_messages:
        # if status != 0 and msg[1] == 275: #msg[1] not in [0, 275, 512]:
        #     print(msg)


        # def _get_child_win(hwnd, param):
        #     print(hwnd, win32gui.GetWindowText(hwnd))
        #     return True

        # win32gui.EnumChildWindows(HWND_tb, _get_child_win, None)

##################################################

# from ctypes import *
# from ctypes.wintypes import *
