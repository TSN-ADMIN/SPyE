#!/usr/bin/python

import fnmatch
import os
from pathlib import Path
from pprint import pprint
import re

import wx
from wx import stc

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: module TESTING
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# import sys
# sys.path.insert(0, os.path.dirname('..'))

# # print(os.getcwd())
# # if __name__ == '__main__':
#     os.chdir('..')    # from const.app import LOC
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

from common.doc import get_doc
from common.path import resolve_path
from common.type import is_btn, is_cbx, is_list, is_stb, is_stt, is_txc, is_stc
from common.util import rs_, me_, get_char_pos, get_keypress, is_shown, msg_box
from conf.debug import (
    DEBUG, dbg_FOCUS, dbg_TIMER
)
from const.app import CLR
from const.common import LBL_FNT_STYLES, TXT_NIL
from const import glb
from const.lang import LANG
from const.menu import MI
from const.searchpanel import SCH_KEYS, SCH_HIS_KEYS, SCH_MAP, SCH_TTP
from data.images import catalog as PNG
import gui
import mix


class SearchPanel(wx.Panel, mix.Help):

    __slots__ = ['CFG', 'sec', 'tlw', 'mode', 'pos_inc', 'tmr_clr',
                 'ttv_all', 'wgt_lst', 'ico_lst', ]

    def __init__(self, *args, **kwargs):
        self.sec = glb.CFG['SearchPanel']

        sty = wx.BORDER_SUNKEN if self.sec['Border'] else wx.BORDER_NONE
        super().__init__(*args, style=sty | wx.TAB_TRAVERSAL, name='SearchPanel', **kwargs)

        self.mode = 'FND'  # mode: FND/RPL/FIF/INC
        self.pos_inc = 0  # current position at start of INC mode
        self.tmr_clr = wx.Timer(self, wx.ID_ANY)
        self.tmr_spb = wx.Timer(self, wx.ID_ANY)

        # tab traversal allowed for ALL fields OR textctrl's ONLY
        self.ttv_all = self.sec['TabTraversalAll']

        # list containers for common and mode-specific widgets/icons
        self.wgt_lst = None
        self.ico_lst = None
        self.spb_cnt = 0  # progress bar value

        self.create_widgets()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, 'create_widgets' MUST run before this ...
        # search fields history: Find, Where, Replace
        # self.txc_fnd.his_lst, self.txc_fnd.his_idx = [], 0  # 0: 1st item, -1: empty list

#NOTE, EXPERIMENTAL CODE: history TEST DATA >>>>>>>>>>>>
        self.txc_fnd.his_lst, self.txc_fnd.his_idx = [
            'AAAAA','BBBBB','CCCCC','DDDDD','EEEEE','FFFFF','GGGGG','HHHHH','IIIII','JJJJJ',
            'KKKKK','LLLLL','MMMMM','NNNNN','OOOOO','PPPPP','QQQQQ','RRRRR','SSSSS','TTTTT',
            'UUUUU','VVVVV','WWWWW','XXXXX','YYYYY','ZZZZZ',
            'AAAAA','BBBBB','CCCCC','DDDDD','EEEEE','FFFFF','GGGGG','HHHHH','IIIII','JJJJJ',
            'KKKKK','LLLLL','MMMMM','NNNNN','OOOOO','PPPPP','QQQQQ','RRRRR','SSSSS','TTTTT',
            'UUUUU','VVVVV','WWWWW','XXXXX','YYYYY','ZZZZZ',
            'AAAAA','BBBBB','CCCCC','DDDDD','EEEEE','FFFFF','GGGGG','HHHHH','IIIII','JJJJJ',
            'KKKKK','LLLLL','MMMMM','NNNNN','OOOOO','PPPPP','QQQQQ','RRRRR','SSSSS','TTTTT',
            'UUUUU','VVVVV','WWWWW','XXXXX','YYYYY','ZZZZZ',
            'AAAAA','BBBBB','CCCCC','DDDDD','EEEEE','FFFFF','GGGGG','HHHHH','IIIII','JJJJJ',
            'KKKKK','LLLLL','MMMMM','NNNNN','OOOOO','PPPPP','QQQQQ','RRRRR','SSSSS','TTTTT',
            'UUUUU','VVVVV','WWWWW','XXXXX','YYYYY','ZZZZZ'
        ], 0  # 0: 1st item, -1: empty list

        self.txc_rpl.his_lst, self.txc_rpl.his_idx = [
            'AAAAA','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR',
            'RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','RRRRR',
            'RRRRR','RRRRR','RRRRR','RRRRR','RRRRR','ZZZZZ'
        ], 0

        self.txc_whr.his_lst, self.txc_whr.his_idx = [
            'AAAAA','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW',
            'WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','WWWWW',
            'WWWWW','WWWWW','WWWWW','WWWWW','WWWWW','ZZZZZ'
        ], 0
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if DEBUG['SCH']:
            print(f'{me_()}')
            for wgt in self.Children:
                print(wgt.Name)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.set_mode(self.mode)
        self.binds()

    def binds(self):

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: CMD session to flush/force stdout/stderr to console
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# D:\Dev\D\wx\TSN_SPyE\dev\spye\src>set PYTHONUNBUFFERED=1
#
# D:\Dev\D\wx\TSN_SPyE\dev\spye\src>SPyE.py | egrep "(btn|cbx|gge|ico|stc|stt|txc)"
# sttFind
# txcFind
# ...
# ...
# ico_24_Buffer
# stcResults
#
# D:\Dev\D\wx\TSN_SPyE\dev\spye\src>python -u SPyE.py
# ...
# REM option '-u' is equivalent
# ...
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# os.system('cls')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#HACK: avoid error AttributeError: 'SearchPanel' object has no
#            attribute 'FindItemById' in '_keyword_set_handler'
        # self.Bind(wx.EVT_TOOL_RANGE, lambda e: e.Skip(False))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, binds not working correctly for checkbox w/ Enter or ESC key
        self.txc_fnd.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'FNF'))  # Find field
        self.txc_rpl.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'RPF'))  # Where field
        self.txc_whr.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'WHF'))  # Replace field

        # self.Bind(wx.EVT_CHILD_FOCUS, self.enter_panel)
        self.Bind(wx.EVT_CHAR_HOOK, self.dispatch)

        for wgt in self.Children:
            # wgt.Bind(wx.EVT_KILL_FOCUS, self.leave_panel)
            # button: Find, FindPrev, FindAll, Where, Replace, ReplaceAll
            if is_btn(wgt):
                wgt.Bind(wx.EVT_BUTTON, self.dispatch)
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # icon (help)
            elif wgt == self.ico_hlp:
                # transform left click into help event; post it with our name as 'payload'
                hlp_evt = wx.PyCommandEvent(wx.EVT_HELP.typeId, wx.NewIdRef())
                hlp_evt.SetClientData(f'{self.__class__.__name__}-{wgt.Name}')
                wgt.Bind(wx.EVT_LEFT_DOWN, lambda e: wx.PostEvent(wgt, hlp_evt))
            # text control: Find, Where, Replace, Incr
            elif is_txc(wgt):
                wgt.Bind(wx.EVT_SET_FOCUS, self.enter_textctrl)
                wgt.Bind(wx.EVT_KILL_FOCUS, self.leave_textctrl)
                if wgt == self.txc_inc:
                    wgt.Bind(wx.EVT_TEXT, lambda e:
                             self.do_find(e, glb.NBK.CurrentPage,
                                       self.txc_inc.Value,
                                       self.get_flags()))
                else:
                    wgt.Bind(wx.EVT_CHAR_HOOK, self.textctrl_history)  # wx.WANTS_CHARS
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # icon (bitmap): checkbox alternative
            elif is_stb(wgt):
                wgt.Bind(wx.EVT_LEFT_DOWN, self.on_icon_or_checkbox)
            # checkbox: case, regex, word, wrap, insel, hilite, prcase, context, buffer
            elif is_cbx(wgt):
                wgt.Bind(wx.EVT_CHECKBOX, self.on_icon_or_checkbox)
            # styledtextctrl: 'search results'
            elif is_stc(wgt):
                wgt.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'RES'))
                wgt.Bind(stc.EVT_STC_DOUBLECLICK, self.do_result_line)
                wgt.Bind(wx.EVT_MOTION, self.toggle_mouse_active)
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # static text: Find, Where, Replace, Incr
            # elif is_stt(wgt):
            #     wgt.Bind(wx.EVT_LEFT_DOWN, self.on_statictext)
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # set focus on 'Find'/'Incremental' text control when button or checkbox clicked
            if not (is_txc(wgt) or is_stc(wgt)):
                wgt.Bind(wx.EVT_LEFT_UP, self.transfer_focus)

        # control allowed tab fields per mode
        self.Bind(wx.EVT_NAVIGATION_KEY, self.tab_traversal)
        # reset default background colour after warning/error
        self.Bind(wx.EVT_TIMER, self.reset_back_colour)

        # self.Bind(wx.EVT_TIMER, self._update_progress_bar)

        self.Bind(wx.EVT_HELP, self.Help)

    def create_widgets(self):

        siz = self.sec['IconSize']

        for key in ('Case','Regex','Word','Wrap','Insel','Hilite','Prcase','Context','Buffer'):
            SCH_TTP[f'ico_{siz}_{key}'] = SCH_TTP[f'ico{key}'].replace(f'ico{key}', f'ico_{siz}_{key}')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, move block below to 'constant.py'
        # text control common arguments: value, pos, size, style
        _TXC_ARG = ('', wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER)  # | wx.TE_RICH)
#HACK: non-default 'txcIncremental' size aligns better when switching search mode (not optimal yet)
        _TXC_ARG_INC = ('', wx.DefaultPosition, (-1, 26), wx.TE_PROCESS_ENTER)

        # widget class
        STT = wx.StaticText
        TXC = wx.TextCtrl
        BTN = wx.Button
        CBX = wx.CheckBox
        GGE = wx.Gauge
        ICO = wx.StaticBitmap
        STC = gui.Editor  # stc.StyledTextCtrl

        # id_ = wx.ID_ANY

#NOTE, prefix of '8 space chars' in 'value' of 'stt_fnd' is needed for precise alignment when switching search mode
        pfx = rs_(8, ' ')
        siz = self.sec['IconSize']

        # search panel widget definitions
        SCH_WIDGETS = {
        #   attribute:  class  label/value/style       window name
        #   ----------  -----  ---------------------   -----------------
            'stt_fnd': (STT,   f'{pfx}&Find:',         'sttFind'),
            'txc_fnd': (TXC,   _TXC_ARG,               'txcFind'),
            'btn_fnd': (BTN,   'Find',                 'btnFind'),
            'btn_fnp': (BTN,   'Find Prev',            'btnFindPrev'),
            'btn_fna': (BTN,   'Find All',             'btnFindAll'),

            'stt_whr': (STT,   'W&here:',              'sttWhere'),
            'txc_whr': (TXC,   _TXC_ARG,               'txcWhere'),
            'btn_whr': (BTN,   '...',                  'btnWhere'),

            'stt_rpl': (STT,   'R&eplace:',            'sttReplace'),
            'txc_rpl': (TXC,   _TXC_ARG,               'txcReplace'),
            'btn_rpl': (BTN,   'Replace',              'btnReplace'),
            'btn_rpa': (BTN,   'Replace All',          'btnReplaceAll'),

            'stt_inc': (STT,   f'{pfx}&Incr:',         'sttIncremental'),
#HACK: non-default size
            'txc_inc': (TXC,   _TXC_ARG_INC,           'txcIncremental'),

            'btn_cnt': (BTN,   'Count',                'btnCount'),

            'cbx_cas': (CBX,   '&Case sensitive',      'cbxCase'),
            'cbx_reg': (CBX,   '&Regular expression',  'cbxRegex'),
            'cbx_wrd': (CBX,   '&Whole word',          'cbxWord'),

            'cbx_wrp': (CBX,   'Wrap around',          'cbxWrap'),
            'cbx_isl': (CBX,   'In selection',         'cbxInsel'),
            'cbx_hlm': (CBX,   'Highlight matches',    'cbxHilite'),
            'cbx_pcs': (CBX,   'Preserve case',        'cbxPrcase'),

            'cbx_cxt': (CBX,   'Show context',         'cbxContext'),
            'cbx_buf': (CBX,   'Use buffer',           'cbxBuffer'),

            'gge_spb': (GGE,   'Search Progress Bar',  'ggeProgressBar'),
            'btn_can': (BTN,   'Cancel',               'btnCancel'),

            'ico_hlp': (ICO,   PNG[f'help_{siz}'],     'icoHelp'),

            'ico_cas': (ICO,   PNG[f'sch_cas_{siz}'],  f'ico_{siz}_Case'),
            'ico_reg': (ICO,   PNG[f'sch_reg_{siz}'],  f'ico_{siz}_Regex'),
            'ico_wrd': (ICO,   PNG[f'sch_wrd_{siz}'],  f'ico_{siz}_Word'),
            'ico_wrp': (ICO,   PNG[f'sch_wrp_{siz}'],  f'ico_{siz}_Wrap'),
            'ico_isl': (ICO,   PNG[f'sch_isl_{siz}'],  f'ico_{siz}_Insel'),
            'ico_hlm': (ICO,   PNG[f'sch_hlm_{siz}'],  f'ico_{siz}_Hilite'),
            'ico_pcs': (ICO,   PNG[f'sch_pcs_{siz}'],  f'ico_{siz}_Prcase'),
            'ico_cxt': (ICO,   PNG[f'sch_cxt_{siz}'],  f'ico_{siz}_Context'),
            'ico_buf': (ICO,   PNG[f'sch_buf_{siz}'],  f'ico_{siz}_Buffer'),

            'stc_res': (STC,   'Search Results',       'stcResults'),
        }

        # build widgets from definition
        for key, val in SCH_WIDGETS.items():
            cls, lvs, nam = val
            # text control
            if val[0] is TXC:
                setattr(self, key, cls(self, value=lvs[0], pos=lvs[1], size=lvs[2], style=lvs[3], name=nam))
            # icon
            elif val[0] is ICO:
                setattr(self, key, cls(self, bitmap=lvs.Bitmap, size=(siz,siz), name=nam))
            # gauge
            elif val[0] is GGE:
                setattr(self, key, cls(self, name=nam))
            # styledtextctrl
            elif val[0] is STC:
                setattr(self, key, cls(self, ['', lvs, '', '']))
                self.stc_res.SetName(nam)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: styling of search results
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, create new lexer for styling of search results
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                bla_tmp = getattr(self, key)
                # print(f'*** Test: {bla_tmp is self.stc_res = }')
                lng_lst = [t for t in LANG if t[1] == 'text']
                bla_tmp.update_language_styling(lng_lst)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#                 # bla_tmp.AddText(lvs)
#                 # bla_tmp.AddText(nam)

#                 bla_tmp.AddText("""
# def goto_task(self, evt):
#    if not (doc := get_doc()): return
#    cur = doc.CurrentPos

#    # force panel visibility
#    if CFG['Task']['ShowPanel']:
#        if not is_shown('SPN'):
#            self.toggle_panel(evt, 'SPN', -1)
#        if not glb.SPN.GetSelection() == SPT.TSK.idx:
#            glb.SPN.SetSelection(SPT.TSK.idx)
# """)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


            # other widget: statictext, button, checkbox
            else:
                setattr(self, key, cls(self, label=lvs, name=nam))

            # tooltip for just created widget
            wgt = getattr(self, key)
            ttp = SCH_TTP[nam]
            wgt.SetToolTip(ttp)

            if DEBUG['SCH']:
                wgt_def = key, cls, lvs, nam
                print(f'{is_list(wgt_def)}, {wgt_def=}')

#FIX, create function 'set_font_style' in 'util.py'
        # static text widget: label font style
        for wgt in ('fnd', 'whr', 'rpl', 'inc'):
            att = getattr(self, f'stt_{wgt}')
            fnt = att.Font
            for key, sty in LBL_FNT_STYLES.items():
                if key in self.sec['LabelFontStyle']:
#FIX, needs better coding...
                    cmd = f'fnt.Make{sty}()'
                    exec(cmd)
            att.SetFont(fnt)

    def show_widgets(self, mode='FND'):
        # common widgets
        if mode == 'INC':
            # incremental mode has its own label/text control
            self.wgt_lst = ['stt_inc', 'txc_inc']
        elif mode == 'RES':
            self.wgt_lst = []
        else:
            self.wgt_lst = ['stt_fnd', 'txc_fnd']

        # common icons
        if mode == 'RES':
            self.ico_lst = []
        else:
            self.ico_lst = ['ico_hlp', 'ico_cas', 'ico_reg', 'ico_wrd']

        # mode-specific widgets (tab traversal order) and icons (NOT included in tab traversal)
        if mode == 'FND':
            extra_wgt_lst = ('btn_fnd', 'btn_fnp', 'btn_fna', 'btn_cnt', 'cbx_cas', 'cbx_reg', 'cbx_wrd', 'cbx_wrp', 'cbx_isl', 'cbx_hlm')
            extra_ico_lst = ('ico_wrp', 'ico_isl', 'ico_hlm')
        elif mode == 'RPL':
            extra_wgt_lst = ('stt_rpl', 'txc_rpl', 'btn_fnd', 'btn_rpl', 'btn_fna', 'btn_rpa', 'btn_cnt', 'cbx_cas', 'cbx_reg', 'cbx_wrd', 'cbx_wrp', 'cbx_isl', 'cbx_hlm', 'cbx_pcs')
            extra_ico_lst = ('ico_wrp', 'ico_isl', 'ico_pcs', 'ico_hlm')
        elif mode == 'FIF':
            extra_wgt_lst = ('stt_whr', 'txc_whr', 'stt_rpl', 'txc_rpl', 'btn_fnd', 'btn_whr', 'btn_rpl', 'btn_cnt', 'cbx_cas', 'cbx_reg', 'cbx_wrd', 'cbx_cxt', 'cbx_buf', 'gge_spb', 'btn_can')
            extra_ico_lst = ('ico_cxt', 'ico_buf')
        elif mode == 'INC':
            extra_wgt_lst = ('stt_inc', 'txc_inc', 'cbx_cas', 'cbx_reg', 'cbx_wrd', 'cbx_wrp', 'cbx_isl', 'cbx_hlm')
            extra_ico_lst = ('ico_wrp', 'ico_isl', 'ico_hlm')
        elif mode == 'RES':
            extra_wgt_lst = ('stc_res',)
            extra_ico_lst = ()

        # add extra widget and icons to common lists
        self.wgt_lst.extend(extra_wgt_lst)
        self.ico_lst.extend(extra_ico_lst)

#INFO, wxPyWiki, 'How to get tabs to work'
#INFO, URL=https://wiki.wxpython.org/Getting%20Started#How_to_get_tabs_to_work
        # set mode-specific widget tab order, as specified above
        for idx, wgt in enumerate(self.wgt_lst[:-1]):
            prv = getattr(self, self.wgt_lst[idx])
            nxt = getattr(self, self.wgt_lst[idx+1])
            nxt.MoveAfterInTabOrder(prv)

        # show widgets
        for wgt in self.wgt_lst:
            if wgt.startswith('cbx') and not self.sec['ShowCheckboxes']:
                continue
            if wgt == 'btn_cnt' and not self.sec['ShowCountButton']:
                continue
            getattr(self, wgt).Show()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # if wgt in ('gge_spb', 'btn_can'):
            #     self.gge_spb.Hide()
            #     self.btn_can.Hide()
            #     self.Update()  # force
            #     self.Layout()
            #     glb.TLW.Layout()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # show icons
        for ico in self.ico_lst:
            if ico.startswith('ico') and not self.sec['ShowIcons']:
                continue
            getattr(self, ico).Show()
            if ico != 'ico_hlp':
                self.toggle_icon(ico[4:])

    def hide_widgets(self):
        for wgt in self.Children:
            wgt.Hide()

#FIX, needs better coding... -> set 'fnc' var (source of event) and call 'dispatch'
    def dispatch(self, evt):
        if not (doc := get_doc()): return


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# # handle button event type: now set to 'dispatch' (was: 'confirm')
#
#         print(evt.EventType, hasattr(evt.EventObject, 'Label'),
#                              hasattr(evt.EventObject, 'Name'))
#         print(evt.EventType, f'[{evt.EventObject.Label}] [{evt.EventObject.Name}]')
#
#         if typ == wx.EVT_CHAR_HOOK.typeId:
#             print('EVT_CHAR_HOOK')
#         elif typ == wx.EVT_KEY_DOWN.typeId:
#             print('EVT_KEY_DOWN')
#         elif typ == wx.EVT_BUTTON.typeId:
#             print('EVT_BUTTON')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# BUTTON ACTION MATRIX #                                        #
########################                                        #
#                                                               #
#                 FND        RPL          FIF                   #
# -------------   --------   ----------   --------------------- #
# btnFind         Find       Find         FindAllInDocuments    #
# btnFindPrev     Previous   -            -                     #
# btnFindAll      FindAll    FindAll      -                     #
# btnWhere        -          -            Where Filter          #
# btnReplace      -          Replace      ReplaceAllInDocuments #
# btnReplaceAll   -          ReplaceAll   -                     #
# btnCount        Count      Count        Count All             #
#                                                               #
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# CURRENT ACTIONS IN 'dispatch', WAS: 'confirm'           #     #
###########################################################     #
#                                                               #
# btnFind      : self.do_find(None, doc, fnd, flg)              #
# btnFindPrev  : self.do_find(None, doc, fnd, flg, prv=True)    #
# btnCount     : self.do_count(doc, fnd)                        #
# btnFindAll   : self.do_find_all(doc, fnd)                     #
# btnReplace   : self.do_replace(doc, fnd, rpl, flg)            #
# btnReplaceAll: self.do_replace_all(doc, fnd, rpl)             #
# btnWhere     : gui.ContextMenu(evt, 'WHR')                    #
#                                                               #
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, allow notebook navigation when focus on search panel
        # _gks = wx.GetKeyState
        # _tab = _gks(wx.WXK_TAB)
        # ctrl = _gks(wx.WXK_CONTROL)
        # shift = _gks(wx.WXK_SHIFT)

        # # Tab key pressed, plus 1 or 2 modifier keys
        # if _tab and (ctrl or shift):
        #     nav_key_evt = wx.NavigationKeyEvent()
        #     wx.PostEvent(glb.NBK, nav_key_evt)
        #     # wx.PostEvent(self, wx.FocusEvent)
        #     # dbg_FOCUS(self)
        #     print(nav_key_evt)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        # event types handled: 'EVT_CHAR_HOOK', 'EVT_BUTTON'
        typ = evt.EventType
        obj = evt.EventObject
        nam = obj.Name
        key_, map_ = SCH_KEYS, SCH_MAP  # convenient short naming (KEYS, MAP)

        # preprocess keypress
        if typ != wx.EVT_BUTTON.typeId:
            kpr_sct, nam, cod = get_keypress(evt)
            # print(f'[{kpr_sct}]')

            # discard when only modifier(s) pressed
            if nam == chr(0):
                return

#FIX, handle ESCAPE centrally; app level?
            if kpr_sct == key_['Exit']:
                if self.mode == 'RES':
                    # self.Freeze()
                    # self.set_mode('FIF')
                    # self.Thaw()
                    return
                else:
                    glb.TLW.sch_esc_active = True
                    wx.PostEvent(doc, evt)
                    dbg_FOCUS(doc)
                return

            # convert numpad key label to corresponding 'RETURN'
            if 'NUMPAD_ENTER' in kpr_sct:
                kpr_sct = kpr_sct.replace('NUMPAD_ENTER', 'RETURN')

            if DEBUG['SCH']: print(f'{me_("C, F")}: >>> code: {cod:3}, name: [{kpr_sct}]')
        # preprocess button
        else:
            # convert button label to corresponding keypress
            if nam in map_:
                if self.mode == 'FIF' and nam in ('btnFind', 'btnReplace'):
                    nam += 'All'
                kpr_sct = map_[nam]
            elif nam == 'btnWhere':
                gui.ContextMenu(evt, 'WHR')
                return
#TODO, implement functionality, use thread to keep GUI available while searching?
            elif nam == 'btnCancel':
                # print('[btnCancel] pressed (not implemented)')
                self.gge_spb.SetValue(0)
                # self.btn_can.Label = 'Cancel'
                self.fif_cancelled = True
                return
            else:
                # we should NEVER get here
                err = f'{self.__class__.__name__}: unknown widget name [{nam}]'
                raise AssertionError(err)

        # search parameters
        flg = self.get_flags()
        fnd = self.txc_fnd.Value
        rpl = self.txc_rpl.Value
        whr = self.txc_whr.Value

        # catch empty 'find field'
        if not fnd and kpr_sct in map_.values():
            txt = 'No text to find'
            glb.IB.info_msg(txt, wx.ICON_WARNING, 'WHITE', 'FOREST GREEN')
            glb.SB.set_text(txt, typ='INFO')
            self.set_back_colour('FOREST GREEN')
            self.transfer_focus(None)
            return

        if kpr_sct in (key_['Find'], key_['FindPrev']) and self.mode not in ('FIF', 'INC'):
            self.do_find(None, doc, fnd, flg, prv=(kpr_sct != 'RETURN'))
        elif kpr_sct == key_['Count'] and self.mode != 'INC' and self.sec['ShowCountButton']:
            self.do_count(doc, fnd, flg)
        elif kpr_sct in (key_['Find'], key_['FindAll']):
            if self.mode in ('FND', 'RPL'):
                self.do_find_all(doc, fnd, flg)
            elif self.mode == 'FIF':

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # self.gge_spb.Show()
                # self.btn_can.Show()
                # wx.MilliSleep(200)
                # self.Update()  # force
                # self.Layout()
                # glb.TLW.Layout()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                self.do_find_in_files(doc, fnd, whr, flg)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # self.gge_spb.Hide()
                # self.btn_can.Hide()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        elif kpr_sct == key_['Replace']:
            if self.mode == 'RPL':
                self.do_replace(doc, fnd, rpl, flg)
                wx.CallAfter(dbg_FOCUS, self.txc_fnd)
        elif kpr_sct == key_['ReplaceAll']:
            if self.mode == 'RPL':
                self.do_replace_all(doc, fnd, rpl, flg)
            elif self.mode == 'FIF':
                self.do_replace_in_files(doc, fnd, rpl, whr, flg)
                wx.CallAfter(dbg_FOCUS, self.txc_fnd)
#INFO, 'Ctrl+Shift+A' also selects all in text control
        elif kpr_sct == key_['SelectAll'] and is_txc(obj):
            obj.SelectAll()

        if kpr_sct in (map_[k] for k in map_ if 'All' in k):
            glb.TLW.toggle_panel(None, 'SCH', -1)  # hide panel
            # prevent 'transfer_focus' to kill focus on document
            wx.CallAfter(dbg_FOCUS, doc)

        # propagate unhandled keypress
        evt.Skip(kpr_sct not in map_.values())

    def set_mode(self, mode='FND'):
        self.mode = mode

        #######################################################################################################
        # SearchPanel GridBagSizer: Widget Layout by Search Mode                   (inspired by Sublime Text) #
        #-----------------------------------------------------------------------------------------------------#
        # Legend: [ R0-5 and C0-8: Rows/Columns ]    [ wx.TextCtrl  : ________| ]    [ wx.CheckBox: x label ] #
        #         [ wx.Button    : < label >    ]    [ wx.StaticText: remaining ]                             #
        #-----------------------------------------------------------------------------------------------------#
        #   NOTE: < Column range LEFT of C0 (columns -5 to -1) is used for icons; see 'refcol' (C0=5) below > #
        #######################################################################################################
        #   C0 C1       C2          C3           C4          C5         C6          C7          C8            #
        # R0                                                                                                  #
        # R1      Find: ______________________________________________| <  Find   > <Find Prev> < Find All  > #
        # R2            x Case      x Regular    x Whole                                                      #
        #                 sensitive   expression   word                                                       #
        # R3            x Wrap      x In         x Highlight                                           ########
        #                 around      selection    matches                                             # Find #
        #######################################################################################################
        #   C0 C1       C2          C3           C4          C5         C6          C7                        #
        # R0                                                                                                  #
        # R1      Find: ______________________________________________| <  Find   > < Find All  >             #
        # R2   Replace: ______________________________________________| < Replace > <Replace All>             #
        # R3            x Case      x Regular    x Whole                                                      #
        #                 sensitive   expression   word                                                       #
        # R4            x Wrap      x In         x Highlight x Preserve                             ###########
        #                 around      selection    matches     case                                 # Replace #
        #######################################################################################################
        #   C0 C1       C2          C3           C4          C5         C6                                    #
        # R0                                                                                                  #
        # R1      Find: ______________________________________________| <  Find   >                           #
        # R2     Where: ______________________________________________| <   ...   >                           #
        # R3   Replace: ______________________________________________| < Replace >                           #
        # R4            x Case      x Regular    x Whole                                                      #
        #                 sensitive   expression   word                                                       #
        # R5            x Show      x Use                                                     #################
        #                 context     buffer                                                  # Find in Files #
        #######################################################################################################
        #   C0 C1       C2          C3           C4          C5         C6          C7          C8            #
        # R0                                                                                                  #
        # R1      Find: ____________________________________________________________________________________| #
        # R2            x Case      x Regular    x Whole                                                      #
        #                 sensitive   expression   word                                                       #
        # R3            x Wrap      x In         x Highlight        ###########################################
        #                 around      selection    matches          # Incremental (like Find, but NO buttons) #
        #######################################################################################################

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, use this in version 4.1: WX_VER
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if self.Sizer:
            self.Sizer.Clear()
######################
#NOTE, to avoid error:
############################################################################################
#       File 'D:\Dev\D\wx\TSN_SPyE\src\lib\searchpanel.py', line 253, in set_mode
#         gbs.Add(self.stt_fnd, (1, 1), *_STATIC_TEXT)
#     wx._core.wxAssertionError: C++ assertion '!m_containingSizer'
#         failed at ..\..\src\common\wincmn.cpp(2490) in wxWindowBase::SetContainingSizer():
#             Adding a window already in a sizer, detach it first!
############################################################################################

        gbs = wx.GridBagSizer(vgap=0, hgap=0)
        gbs.SetFlexibleDirection(wx.BOTH)
        gbs.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_ALL)
        gbs.SetEmptyCellSize((10, 0))
        border = 5  # space around widgets (pixels)

        # grid reference column:
        #     left side (columns 0-4) used for icons
        #    right side (columns 5-n) used for other widgets
        refcol = 5 if self.sec['ShowIcons'] or mode == 'RES' else 0

        # common grid bag sizer arguments: span, flags, border (_9C = #columns)
        _STATIC_TEXT   = ((1, 1), wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        _STATIC_BITMAP = ((1, 1), wx.LEFT | wx.EXPAND, border)  # wx.ALIGN_CENTRE_VERTICAL
        _SINGLE_SPAN   = ((1, 1), wx.ALL, border)
        _MULTI_SPAN_2C = ((1, 2), wx.ALL | wx.EXPAND, border + 1)  # wx.ALIGN_CENTRE_VERTICAL
        _MULTI_SPAN_4C = ((1, 4), wx.ALL | wx.EXPAND, border)  # wx.ALIGN_CENTRE_VERTICAL
        _FULL_SPAN     = ((0, 0), wx.ALL | wx.EXPAND, 0)  # no border for results window

        # common layout
        if self.sec['ShowCountButton'] and mode != 'RES':
            # set count button row/column to fit common layout
            btn_cnt_row = 2 if mode == 'FND' else 3 if mode == 'RPL' else 4 if mode == 'FIF' else 2
            btn_cnt_col = 8 if mode == 'FND' else 7 if mode == 'RPL' else 6 if mode == 'FIF' else 8
            gbs.Add(self.btn_cnt, (btn_cnt_row, refcol+btn_cnt_col), *_SINGLE_SPAN)

        # set help icon row to fit common layout
        if mode != 'RES':
            ico_hlp_row = 3 if mode in ('FND', 'INC') else 4 if mode == 'RPL' else 5 if mode == 'FIF' else 3
            gbs.Add(self.ico_hlp, (ico_hlp_row, refcol-5), *_STATIC_BITMAP)
            gbs.Add(self.ico_cas, (1, refcol-5), *_STATIC_BITMAP)
            gbs.Add(self.ico_reg, (1, refcol-4), *_STATIC_BITMAP)
            gbs.Add(self.ico_wrd, (1, refcol-3), *_STATIC_BITMAP)

        # incremental mode has no buttons
        if mode not in ('INC', 'RES'):
            gbs.Add(self.stt_fnd, (1, refcol+1), *_STATIC_TEXT)
            gbs.Add(self.txc_fnd, (1, refcol+2), *_MULTI_SPAN_4C)
            gbs.Add(self.btn_fnd, (1, refcol+6), *_SINGLE_SPAN)

        # search mode layout: 'Find', 'Replace', 'Find in Files' or 'Incremental' or 'Results'
        if mode == 'FND':
            gbs.Add(self.ico_wrp, (1, refcol-2), *_STATIC_BITMAP)
            gbs.Add(self.ico_isl, (1, refcol-1), *_STATIC_BITMAP)
            gbs.Add(self.btn_fnp, (1, refcol+7), *_SINGLE_SPAN)
            gbs.Add(self.btn_fna, (1, refcol+8), *_SINGLE_SPAN)

            gbs.Add(self.ico_hlm, (2, refcol-1), *_STATIC_BITMAP)
            gbs.Add(self.cbx_cas, (2, refcol+2), *_SINGLE_SPAN)
            gbs.Add(self.cbx_reg, (2, refcol+3), *_SINGLE_SPAN)
            gbs.Add(self.cbx_wrd, (2, refcol+4), *_SINGLE_SPAN)

            gbs.Add(self.cbx_wrp, (3, refcol+2), *_SINGLE_SPAN)
            gbs.Add(self.cbx_isl, (3, refcol+3), *_SINGLE_SPAN)
            gbs.Add(self.cbx_hlm, (3, refcol+4), *_SINGLE_SPAN)
        elif mode == 'RPL':
            gbs.Add(self.ico_wrp, (1, refcol-2), *_STATIC_BITMAP)
            gbs.Add(self.ico_isl, (1, refcol-1), *_STATIC_BITMAP)
            gbs.Add(self.btn_fna, (1, refcol+7), *_SINGLE_SPAN)

            gbs.Add(self.ico_pcs, (2, refcol-5), *_STATIC_BITMAP)
            gbs.Add(self.ico_hlm, (2, refcol-2), *_STATIC_BITMAP)
            gbs.Add(self.stt_rpl, (2, refcol+1), *_STATIC_TEXT)
            gbs.Add(self.txc_rpl, (2, refcol+2), *_MULTI_SPAN_4C)
            gbs.Add(self.btn_rpl, (2, refcol+6), *_SINGLE_SPAN)
            gbs.Add(self.btn_rpa, (2, refcol+7), *_SINGLE_SPAN)

            gbs.Add(self.cbx_cas, (3, refcol+2), *_SINGLE_SPAN)
            gbs.Add(self.cbx_reg, (3, refcol+3), *_SINGLE_SPAN)
            gbs.Add(self.cbx_wrd, (3, refcol+4), *_SINGLE_SPAN)

            gbs.Add(self.cbx_wrp, (4, refcol+2), *_SINGLE_SPAN)
            gbs.Add(self.cbx_isl, (4, refcol+3), *_SINGLE_SPAN)
            gbs.Add(self.cbx_hlm, (4, refcol+4), *_SINGLE_SPAN)
            gbs.Add(self.cbx_pcs, (4, refcol+5), *_SINGLE_SPAN)
        elif mode == 'FIF':
            gbs.Add(self.ico_cxt, (1, refcol-2), *_STATIC_BITMAP)
            gbs.Add(self.ico_buf, (1, refcol-1), *_STATIC_BITMAP)

            gbs.Add(self.stt_whr, (2, refcol+1), *_STATIC_TEXT)
            gbs.Add(self.txc_whr, (2, refcol+2), *_MULTI_SPAN_4C)
            gbs.Add(self.btn_whr, (2, refcol+6), *_SINGLE_SPAN)

            gbs.Add(self.stt_rpl, (3, refcol+1), *_STATIC_TEXT)
            gbs.Add(self.txc_rpl, (3, refcol+2), *_MULTI_SPAN_4C)
            gbs.Add(self.btn_rpl, (3, refcol+6), *_SINGLE_SPAN)

            gbs.Add(self.cbx_cas, (4, refcol+2), *_SINGLE_SPAN)
            gbs.Add(self.cbx_reg, (4, refcol+3), *_SINGLE_SPAN)
            gbs.Add(self.cbx_wrd, (4, refcol+4), *_SINGLE_SPAN)
            gbs.Add(self.cbx_cxt, (5, refcol+2), *_SINGLE_SPAN)
            gbs.Add(self.cbx_buf, (5, refcol+3), *_SINGLE_SPAN)
            gbs.Add(self.gge_spb, (5, refcol+4), *_MULTI_SPAN_2C)
            # gbs.Add(self.gge_spb, (5, refcol+2), *_MULTI_SPAN_4C)
            gbs.Add(self.btn_can, (5, refcol+6), *_SINGLE_SPAN)
            # print(f'{self.gge_spb.Range = }, {self.gge_spb.Value = }')
        elif mode == 'INC':
            gbs.Add(self.ico_wrp, (1, refcol-2), *_STATIC_BITMAP)
            gbs.Add(self.ico_isl, (1, refcol-1), *_STATIC_BITMAP)
            gbs.Add(self.stt_inc, (1, refcol+1), *_STATIC_TEXT)
            gbs.Add(self.txc_inc, (1, refcol+2), *_MULTI_SPAN_4C)

            gbs.Add(self.ico_hlm, (2, refcol-1), *_STATIC_BITMAP)
            gbs.Add(self.cbx_cas, (2, refcol+2), *_SINGLE_SPAN)
            gbs.Add(self.cbx_reg, (2, refcol+3), *_SINGLE_SPAN)
            gbs.Add(self.cbx_wrd, (2, refcol+4), *_SINGLE_SPAN)

            gbs.Add(self.cbx_wrp, (3, refcol+2), *_SINGLE_SPAN)
            gbs.Add(self.cbx_isl, (3, refcol+3), *_SINGLE_SPAN)
            gbs.Add(self.cbx_hlm, (3, refcol+4), *_SINGLE_SPAN)
        elif mode == 'RES':
            # results window takes up all available space
            gbs.AddGrowableCol(0)
            gbs.AddGrowableRow(0)
            # gbs.Add(glb.IB, (0, refcol-5), *_FULL_SPAN)
            gbs.Add(self.stc_res, (0, refcol-5), *_FULL_SPAN)
        else:
            # we should NEVER get here
            err = f'{self.__class__.__name__}: unknown search mode [{mode}]'
            raise AssertionError(err)

        self.hide_widgets()
        self.show_widgets(mode)

        if mode != 'RES':
            gbs.AddGrowableCol(refcol+5)

        if not (doc := get_doc()): return

        # copy text selection to 'find field'
        if self.sec['SelectedTextToFind']:
            if (sel := doc.StringSelection):
                self.txc_fnd.Value = sel

        # select text control contents: Find, Where, Replace, Incremental
        for fld in (self.txc_fnd, self.txc_whr, self.txc_rpl, self.txc_inc):
            dbg_FOCUS(fld)
            fld.SelectAll()

        self.pos_inc = doc.CurrentPos

        # set focus on mode-specific text control
        fld = self.txc_fnd if self.mode != 'INC' else self.txc_inc
        wx.CallAfter(dbg_FOCUS, fld)

        self.SetBackgroundColour(self.sec['BackColour' + mode])
        self.Refresh()  # force

        self.SetSizer(gbs)
        self.Layout()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: gradient background colour
    #     self.Bind(wx.EVT_PAINT, self.on_paint)

    # def on_paint(self, evt):
    #     dc = wx.PaintDC(self)
    #     x, y = self.Size
    #     # rainbow effect in 3 adjoining sections
    #     dc.GradientFillLinear((0,     0, x/3, y), 'RED',   'YELLOW') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)
    #     dc.GradientFillLinear((1*x/3, 0, x/3, y), 'YELLOW', 'GREEN') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)
    #     dc.GradientFillLinear((2*x/3, 0, x/3, y), 'GREEN',   'BLUE') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: private AcceleratorTable for 'SearchPanel'    >>> >>> >>> >>> >>> >>> >>>
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: private AcceleratorTable for 'SearchPanel'
    def enter_panel(self, evt):
        evt.Skip()

        def __accel_handler(evt):
            # obj = evt.EventObject

            # sim_key = wx.UIActionSimulator()
            print(evt.Id)
            # pprint(dir(evt))
            print(evt.IsChecked())
            # for key in ('CRW'):
            #     if evt.KeyCode == ord(key):
            #         print(key)

            # if evt.KeyCode == ord('C'):
            #     dbg_FOCUS()

            # sim_key.KeyDown(evt.KeyCode)

        if DEBUG['SCH']: print(f'{me_("C, F")}')

# #FIX, save/set accel table on 'SearchPanel'
        self.sav_acc_tbl = glb.MB.acc_tbl
        glb.TLW.SetAcceleratorTable(wx.NullAcceleratorTable)
        glb.MB.SetAcceleratorTable(wx.NullAcceleratorTable)

        # # acc_ent_lst = []
        acc_lst =  ('cas', 'reg', 'wrd')

        for idx, key in enumerate('CRW'):
            # # acc_ent_lst.append(wx.AcceleratorEntry())

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            nam = f'cbx_{acc_lst[idx]}'
#HACK: boolean walrus logic ;-) as an alternative to:
#INFO,    1.  obj, id_ = getattr(self, nam), getattr(self, nam).Id

#INFO,    2.  obj = getattr(self, f'cbx_{acc_lst[idx]}')
#INFO,        id_ = obj.Id
            (obj := getattr(self, nam)) and (id_ := obj.Id)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # # print(' ', idx, key, id_, obj.Name)
            # # acc_ent_lst[idx].Set(wx.ACCEL_ALT, ord(key), id_)
            obj.Bind(wx.EVT_MENU, __accel_handler, id=id_)
#TODO, try a 2nd 'wx.Panel' in init ('self' is 1st panel)
            # self.pnl.Bind(wx.EVT_MENU, __accel_handler, id=id_)

            accel = wx.AcceleratorTable([(wx.ACCEL_ALT, ord(key), id_)])
            obj.SetAcceleratorTable(accel)

        # accel = wx.AcceleratorTable(acc_ent_lst)
        # self.SetAcceleratorTable(accel)

    def leave_panel(self, evt):
        evt.Skip()

        if DEBUG['SCH']: print(f'{me_("C, F")}')

        glb.TLW.SetAcceleratorTable(self.sav_acc_tbl)
        glb.MB.SetAcceleratorTable(self.sav_acc_tbl)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: private AcceleratorTable for 'SearchPanel'    <<< <<< <<< <<< <<< <<< <<<
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#TODO, implement 'MaxItems'

    def textctrl_history(self, evt):
        evt.Skip()

        if (cod := evt.KeyCode) not in SCH_HIS_KEYS:
            return

        id_, fld = evt.Id, evt.EventObject
        # print(fld)
        pos, max_pos = fld.InsertionPoint, fld.LastPosition
        up_, dn_, txt = (cod == wx.WXK_UP), (cod == wx.WXK_DOWN), TXT_NIL

        if up_ or dn_:
            if up_:
                txt, pos = ('Prev   [Up]'), (pos + 1 if pos != max_pos else pos)
                fld.his_idx += 1

                if fld.his_lst and fld.his_idx == len(fld.his_lst):
                    # print('   LAST item: ', end='')
                    fld.his_idx = len(fld.his_lst) - 1
            elif dn_:
                txt, pos = ('Next [Down]'), (pos - 1 if pos != 0 else 0)
                fld.his_idx -= 1

                if fld.his_lst and fld.his_idx == -1:
                    # print('  FIRST item: ', end='')
                    fld.his_idx = 0

            if fld.his_lst:
                fld.Value = val = fld.his_lst[fld.his_idx]
                print(f'{fld.his_idx:3} {val}')

            # wx.CallAfter(fld.SelectAll)
            wx.CallAfter(fld.SetInsertionPoint, fld.LastPosition)
        else:
            print('\n  [ENTER] pressed\n')
            # if not exist, add value to history
            if (val := fld.Value) and val not in fld.his_lst:
                fld.his_lst.insert(0, val)
                fld.his_idx = 0
            pprint(fld.his_lst, indent=4, width=10)

        # print()

        # fld.SetInsertionPoint(pos)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # print(f'{me_("F")}: {txt} -> OldPos: [{fld.InsertionPoint:2}], '
        #                            f'NewPos: [{pos:2}], '
        #                            f'Field: {fld.Name}]')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def enter_textctrl(self, evt):
        evt.Skip()

        txc = evt.EventObject
        if DEBUG['SCH']: print(f'{me_("F")}: {txc.Name}')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, 'TXC_STYLE' not working
        # sty = self.TXC_STYLE[txc]
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        txc.SelectNone()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, 'TXC_STYLE
        # # restore text control style
        # txc.SetStyle(0, len(txc.Value), wx.TextAttr(*sty[:2]))
        # txc.SetStyle(*sty[6:8], wx.TextAttr(*sty[2:4]))
        # txc.SetSelection(*sty[6:8])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def leave_textctrl(self, evt):
        evt.Skip()

        txc = evt.EventObject
        if DEBUG['SCH']: print(f'{me_("F")}: {txc.Name}')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, 'TXC_STYLE' not working
        # sty = self.TXC_STYLE[txc]

        # # save text control style
        # sty[6:8] = txc.GetSelection()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        txc.SelectNone()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, 'TXC_STYLE' not working; use values from config
#NOTE, this dict definition was temporarily moved from end of 'def create_widgets'
#         # text control fields: fore/background colours and positions
#         self.TXC_STYLE = {
#             #              >>> PLAIN TEXT <<<   >>>>>>>>>>>>>>>>>>>>>> SELECTED TEXT <<<<<<<<<<<<<<<<<<<<<   Caret
#             #      field:  Fore      Back       Fore/Back (active)      Fore/Back (inactive)    Start  End     Pos
#             #      ------  --------  --------   ----------------------  ----------------------  -----  ---   -----
#             self.txc_fnd: ['BLACK',  'WHITE',   'WHITE', CLR['BLUE5'],  'WHITE', CLR['BLUE4'],      0,   0,      0,],
#             self.txc_whr: ['BLACK',  'WHITE',   'WHITE', CLR['BLUE5'],  'WHITE', CLR['BLUE4'],      0,   0,      0,],
#             self.txc_rpl: ['BLACK',  'WHITE',   'WHITE', CLR['BLUE5'],  'WHITE', CLR['BLUE4'],      0,   0,      0,],
#             self.txc_inc: ['BLACK',  'WHITE',   'WHITE', CLR['BLUE5'],  'WHITE', CLR['BLUE4'],      0,   0,      0,],
#             # self.txc_fnd: ['BLACK',  'WHITE',   'WHITE', 'GREEN',       'WHITE', 'RED',             0,   0,      0,],
#             # self.txc_whr: ['BLACK',  'WHITE',   'WHITE', 'GREEN',       'WHITE', 'RED',             0,   0,      0,],
#             # self.txc_rpl: ['BLACK',  'WHITE',   'WHITE', 'GREEN',       'WHITE', 'RED',             0,   0,      0,],
#             # self.txc_inc: ['BLACK',  'WHITE',   'WHITE', 'GREEN',       'WHITE', 'RED',             0,   0,      0,],
#         }
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         wx.CallAfter(self.set_field_style, evt, cur)
#
#     def set_field_style(self, evt, cur):
# #              ### Plain Text ###   ################### Selected Text ###################   Caret
# #      field:  fore      back       fore/back (active)   fore/back (inactive)  start  end     pos
# #      ------  --------  --------   -------------------  --------------------  -----  ---   -----
# #                 0         1          2    3               4    5               6     7       8
#
#         for fld in (self.txc_fnd, self.txc_rpl):
#             pos = fld.InsertionPoint  # self.TXC_STYLE[fld][8]
#             sel = fld.GetSelection()  # self.TXC_STYLE[fld][6:8]
#             txt = fld.StringSelection
#             # print(f'{cur.Name:<13}: {pos=:2},  {sel[0]=:2} / {sel[1]=:2},  {txt=}')
#
#             sty = self.TXC_STYLE[fld]
#             fld.SetDefaultStyle(wx.TextAttr(*sty[:2]))
#             fld.SetDefaultStyle(wx.TextCtrl().DefaultStyle)
#
#             if cur == fld:
#                 fld.SetInsertionPoint(sty[8])
#                 fld.SetStyle(0, len(fld.Value), wx.TextAttr(*sty[:2]))
#                 fld.SetStyle(*sty[6:8], wx.TextAttr(*sty[2:4]))
#                 fld.SetSelection(*sty[6:8])
#                 fld.Refresh()
#             else:
#                 sty[8] = fld.InsertionPoint
#                 sty[6:8] = fld.GetSelection()
#                 fld.SetStyle(0, len(fld.Value), wx.TextAttr(*sty[:2]))
#                 fld.SetStyle(*sty[6:8], wx.TextAttr(*sty[4:6]))
#                 fld.SetSelection(*sty[6:8])
#                 fld.Refresh()
#
#                 # fld.SetStyle(*fld.GetSelection(), wx.TextAttr(*self.TXC_STYLE[fld][2:4]))
#             # fld.SetDefaultStyle(wx.TextAttr('BLACK', 'WHITE'))
#
#     def key_pressed(self, evt):
#         print('key_pressed:', evt.EventObject.Name)
#         fld = evt.EventObject
#         sty = self.TXC_STYLE[fld]
#         if not evt.shiftDown and evt.KeyCode in (wx.WXK_LEFT, wx.WXK_RIGHT):
#             fld.SetStyle(0, len(fld.Value), wx.TextAttr(*sty[:2]))
#         evt.Skip()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#INFO, URL=https://groups.google.com/g/wxpython-users/c/Ggq3Un1dSqY/m/kOeFJzDP2PsJ
    def tab_traversal(self, evt):
#NOTE, weird behaviour: 'evt.Id = 0', so use focused object Id
        obj = self.FindFocus()
        id_ = obj.Id
        _fwd = evt.Direction  # backward/forward tab keypress (0/1)

        # allowed tab field range for selected mode
        first_fld = self.txc_fnd if self.mode != 'INC' else self.txc_inc

        if self.mode == 'FND':
            last_fld = self.cbx_hlm if self.ttv_all else self.txc_fnd
        elif self.mode == 'RPL':
            last_fld = self.cbx_pcs if self.ttv_all else self.txc_rpl
        elif self.mode == 'FIF':
            last_fld = self.cbx_buf if self.ttv_all else self.txc_rpl
        elif self.mode == 'INC':
            last_fld = self.cbx_hlm if self.ttv_all else self.txc_inc
        elif self.mode == 'RES':
            last_fld = self.stc_res

        if DEBUG['SCH']:
            nam, first, last = obj.Name, (id_ == first_fld.Id), (id_ == last_fld.Id)
            print(f'{nam= :13}  {_fwd= !r:5}  {id_= }  {first= !r:5}  {last= !r:5}')

        # focus last/first field with back/forward tab respectively
        if id_ == first_fld.Id and not _fwd:
            dbg_FOCUS(last_fld)
        elif id_ == last_fld.Id and _fwd:
            dbg_FOCUS(first_fld)
        else:
            evt.Skip()

    # set focus on 'Find'/'Incremental' text control when button or checkbox clicked
    def transfer_focus(self, evt):
        fld = self.txc_fnd if self.mode != 'INC' else self.txc_inc
        wx.CallAfter(dbg_FOCUS, fld)
        if evt:
            evt.Skip()

    def on_icon_or_checkbox(self, evt):
        def __update_ico_cbx_xref_mapping(obj):
            self.fld_xrf_dct = {}
            pfx_fld = 'cbx' if is_cbx(obj) else 'ico'
            pfx_ref = 'ico' if is_cbx(obj) else 'cbx'
            for fld in ('CAS', 'REG', 'WRD', 'WRP', 'ISL', 'HLM', 'PCS', 'CXT', 'BUF'):
                fld_id_ = getattr(self, f'{pfx_fld}_{(nam := fld.lower())}').Id
                fld_ref = getattr(self, f'{pfx_ref}_{nam}')
                self.fld_xrf_dct[fld_id_] = (fld, fld_ref)

        id_ = evt.Id
        obj = evt.EventObject
        nam = obj.Name

        if DEBUG['SCH']: print(f'{me_("F")}: {nam}')

        __update_ico_cbx_xref_mapping(obj)

        fld, wgt = self.fld_xrf_dct[id_]
        mnu_id = MI[f'SCH_{fld}']

        # sync corresponding checkbox, menu item and icon
        if not is_cbx(obj):
            wgt.Value = not wgt.Value
        glb.MB.Check(mnu_id, not glb.MB.IsChecked(mnu_id))
        self.toggle_icon(fld.lower())

        if DEBUG['SCH']:
            if is_cbx(obj):
                chk = 'ON' if obj.IsChecked() else 'off'
                print(f'  {self.__class__.__name__}: {nam:<10s} [ {chk:<3s} ] [{obj.Label}]')

    def toggle_icon(self, fld):
        self.Freeze()
        cbx = getattr(self, f'cbx_{fld}')
        ico = getattr(self, f'ico_{fld}')
        nam = f'sch_{fld}_24' if cbx.Value else f'sch_{fld}_unchk_24'
        ico.SetBitmap(PNG[nam].Bitmap)
        self.Layout()
        self.Thaw()


# stc.STC_FIND_CXX11REGEX
# stc.STC_FIND_MATCHCASE
# stc.STC_FIND_POSIX
# stc.STC_FIND_REGEXP
# stc.STC_FIND_WHOLEWORD
# stc.STC_FIND_WORDSTART


        # if nam in ('case', 'regex', 'word', 'wrap', 'insel', 'hilite', 'prcase'):
        #     print(nam)

    # def on_statictext(self, evt):
    #     obj = evt.EventObject
    #     nam = obj.Name

    #     print('on_statictext:', nam)

    #     # which static text
    #     if (id_ := evt.Id) == self.stt_fnd.Id:
    #         fld = self.txc_fnd
    #     elif id_ == self.stt_whr.Id:
    #         fld = self.txc_whr
    #     elif id_ == self.stt_rpl.Id:
    #         fld = self.txc_rpl

    #     # print(f'  {self.__class__.__name__}: {nam:<10s} [ {chk:<3s} ] [{obj.Label}]')

    #     # focus corresponding text control
    #     dbg_FOCUS(fld)
    #     evt.Skip()

    def set_back_colour(self, clr=None, typ='WARN'):
        if not clr:
            clr = 'WarningBackColour' if typ == 'WARN' else 'ErrorBackColour'
            clr = self.sec[clr]
        self.tmr_clr.StartOnce(self.sec['DelayDefaultColour'])
        fld = self.txc_fnd if self.mode != 'INC' else self.txc_inc
        fld.SetBackgroundColour(clr)
        self.Refresh()  # force

    def reset_back_colour(self, evt, clr='WHITE'):
        # discard when not our timer
        if evt.Timer.Id != self.tmr_clr.Id:
            evt.Skip()
            return

        for fld in (self.txc_fnd, self.txc_inc):
            fld.SetBackgroundColour(clr)
        self.Refresh()  # force

    def show_not_found_msg(self, doc, spos, epos):
        txt = 'Text not found'
        glb.IB.info_msg(txt, wx.ICON_ERROR, 'WHITE', CLR['RED3'])
        glb.SB.set_text(txt, typ='ERROR')
        self.set_back_colour()
        doc.SetSelection(spos, epos)
        doc.SwapMainAnchorCaret()
        return False

    def get_flags(self):
        flg = 0
#NOTE, 3 'stc.STC_FIND_*' flags are not used
        # flg += stc.STC_FIND_CXX11REGEX if self.???.Value else 0
        flg += stc.STC_FIND_MATCHCASE if self.cbx_cas.Value else 0
        # flg += stc.STC_FIND_POSIX      if self.???.Value else 0
        flg += stc.STC_FIND_REGEXP    if self.cbx_reg.Value else 0
        flg += stc.STC_FIND_WHOLEWORD if self.cbx_wrd.Value else 0
        # flg += stc.STC_FIND_WORDSTART  if self.???.Value else 0

        if DEBUG['SCH']:
            cas = bool(flg & stc.STC_FIND_MATCHCASE)
            reg = bool(flg & stc.STC_FIND_REGEXP)
            wrd = bool(flg & stc.STC_FIND_WHOLEWORD)
            print(f'[{cas = !r}] [{reg = !r}] [{wrd = !r}]')

        return flg

    def scroll_to_centre(self, doc, fnd):
#FIX, for next/prev find: print 'found at', too
#         self._exec_found(fnd)
        lin = doc.CurrentLine
        # col = doc.GetColumn(doc.CurrentPos)
        half_screen = doc.LinesOnScreen() // 2
        doc.ScrollToLine(lin - half_screen)
        # keep caret on screen vertically:
        # - divisor '30' works fine with differing client widths
        # doc.ScrollToColumn(col - doc.ClientSize[0] // 30)
        doc.EnsureCaretVisible()

    def do_find(self, evt, doc, fnd, flg, prv=False):
        print(f'{me_("F")}: {fnd} {prv=}')
        """ Handle both regular as well as incremental search.

            Arguments:
                evt: 'None', required as INC search is called from bind
                doc: current document
                fnd: text to search for
                flg: search flags, see 'get_flags'
                prv: search direction; 'True'=previous, 'False'=next
        """
        if self.mode !='INC':
            fld = self.txc_fnd
            pos = doc.SelectionStart if prv else doc.SelectionEnd
        else:
            fld = self.txc_inc
            pos = self.pos_inc

        spos, epos = doc.GetSelection()  # save last selection
        doc.SetCurrentPos(pos)
        doc.SearchAnchor()

        res = True

        if (fnc := doc.SearchPrev if prv else doc.SearchNext)(flg, fnd) == stc.STC_INVALID_POSITION:
            if self.cbx_wrp.Value:
                # search from top/bottom when not found
                wrp = ('BOTTOM' if prv else 'TOP') if self.cbx_wrp.Value else ''
                txt = f'    => [{fnd}] NOT found (search wrapped to {wrp})'
                if DEBUG['SCH']: print(txt)
                glb.IB.info_msg(txt, wx.ICON_INFORMATION, 'WHITE', 'FOREST GREEN')
                glb.SB.set_text(txt, typ='WARN')
                spos, epos = doc.GetSelection()  # save last selection
                doc.DocumentEnd() if prv else doc.DocumentStart()
                doc.SearchAnchor()
                if fnc(flg, fnd) == stc.STC_INVALID_POSITION:
                    res = self.show_not_found_msg(doc, spos, epos)
            else:
                res = self.show_not_found_msg(doc, spos, epos)

        self.scroll_to_centre(doc, fnd)

        # back to search panel when visible
        if is_shown('SCH'):
            wx.CallAfter(dbg_FOCUS, fld)

        print(f'{me_("F")}: {res}')
        return res

    def do_count(self, doc, fnd, flg):
        print(f'{me_("F")}: {fnd}')

        cur = 0
        cnt = 0
        while True:
            if (pos := doc.FindText(cur, doc.LastPosition, fnd, flg)) == stc.STC_INVALID_POSITION:
                break
            cur = pos + len(fnd)
            cnt += 1

        txt = f'Found {cnt} occurrences of [{fnd}]'
        if DEBUG['SCH']: print(txt)
        glb.SB.set_text(txt)
        msg = f'{doc.fnm}\n\n{txt}'
        msg_box(self, 'INFO', msg, extra='Search Count')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # def do_replace(self, doc, fnd, rpl, flg):
    #     print(f'{me_("F")}: {fnd} {rpl}')

    #     spos, epos = doc.GetSelection()  # save last selection
    #     doc.SearchAnchor()
    #     if (res := doc.SearchNext(flg, fnd)) != stc.STC_INVALID_POSITION:
    #         self.do_replace(doc, fnd, rpl, flg)
    #     else:
    #         res = self.show_not_found_msg(doc, spos, epos)

    #     self.scroll_to_centre(doc, fnd)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, replace 'SearchNext' with already existing 'do_find' functionality
#NOTE, and ... do 'return res' from 'do_find'
#NOTE,     ... and 'scroll_to_centre' could be discarded below
    def do_replace(self, doc, fnd, rpl, flg):
        if (res := doc.SearchNext(flg, fnd)) == stc.STC_INVALID_POSITION:
            spos = epos = doc.CurrentPos
            res = self.show_not_found_msg(doc, spos, epos)
        else:
            doc.ReplaceSelection(rpl)
            doc.SearchAnchor()
            self.scroll_to_centre(doc, fnd)
        return res
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@




    def do_find_all(self, doc, fnd, flg):
        print(f'{me_("F")}: {fnd}')

        siz = len(fnd)
        end = doc.LastPosition

        pos = 0
        cur = 0
        spos, epos = doc.GetSelection()  # save last selection
        sel_lst = []
        doc.SelectNone()
        doc.SetSelection(pos, pos)

        # find and select matches
        while True:
            if (pos := doc.FindText(cur, end, fnd, flg)) == stc.STC_INVALID_POSITION:
                break

#FIX, incorrect results with regex, e.g. '[1-2][cd]'
            anchor, caret = pos, pos + siz
            if not sel_lst:
                doc.SetSelection(anchor, caret)
            else:
                doc.AddSelection(caret, anchor)

            sel_lst.append(pos)
            cur = pos + siz

        cnt = len(sel_lst)

        if cnt:
            txt = f'Found {cnt} occurrences of [{fnd}]'
            if DEBUG['SCH']: print(txt)
            glb.SB.set_text(txt)
            msg = f'{doc.fnm}\n\n{txt}'
            msg_box(self, 'INFO', msg, extra='Find All')
        else:
            res = self.show_not_found_msg(doc, spos, epos)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def do_replace_all(self, doc, fnd, rpl, flg):
        print(f'{me_("F")}: {fnd} {rpl}')

        # save caret position and first line and selection
        pos = doc.CurrentPos
        top = doc.FirstVisibleLine
        spos, epos = doc.GetSelection()

        cnt = 0  # replace all: occurrences
        doc.DocumentStart()  # replace from top
        doc.SearchAnchor()

        doc.BeginUndoAction()

        res = doc.SearchNext(flg, fnd)
        while res != stc.STC_INVALID_POSITION:
            cnt += 1
            res = self.do_replace(doc, fnd, rpl, flg)
        if cnt:
            txt = f'Replaced {cnt} occurrences of [{fnd}] with [{rpl}]'
            if DEBUG['SCH']: print(txt)
            glb.SB.set_text(txt)
            msg = f'{doc.fnm}\n\n{txt}'
            msg_box(self, 'INFO', msg, extra='Replace All')
        else:
            res = self.show_not_found_msg(doc, spos, epos)

        doc.EndUndoAction()

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # restore caret's last position and first line
        # doc.GotoPos(pos)
        # doc.SetFirstVisibleLine(top)
        doc.GotoPos(doc.CurrentPos)
        doc.VerticalCentreCaret()
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def do_find_in_files(self, doc, fnd, whr, flg):
        print(f'{me_("F")}: [{fnd}]')

        dbg_TIMER('search')

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # gbs = self.Sizer
        # gbs.Detach(self.cbx_cxt)
        # gbs.Detach(self.cbx_buf)
        # gbs.Detach(self.gge_spb)
        # gbs.Add(self.gge_spb, (5, 5+2), (1, 4), wx.ALL | wx.EXPAND, 5)
        # self.Layout()
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.fif_cancelled = False  # 'finding files' not cancelled by user

        # self.tmr_spb.Start(100)
        self.gge_spb.SetValue(0)
        self.stt_rpl.Label = 'Filename:'
        # self.Layout()

        def __file_io(fnm):
            cnt = 0
            with open(fnm, 'rb') as fil_obj:
                for num, lin in enumerate(fil_obj.readlines()):
                    cnt += __matches_in_line(fnm, fnd, cnt, num, lin)
                    # keep gui responsive during search
                    wx.YieldIfNeeded()
                    if self.fif_cancelled:
                        print(f'{rs_(25, "*")}\n** Searching cancelled **\n{rs_(25, "*")}')
                        break
            return cnt

#INFO, Python mmap: Improved File I/O With Memory Mapping
#INFO, URL=https://realpython.com/python-mmap/
#INFO, '__mmap_io' not used
        import mmap
        def __mmap_io(fnm):
            cnt = 0
            with open(fnm, mode='r', encoding='utf-8') as fil_obj:
                try:
                    with mmap.mmap(fil_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
                        for num, lin in enumerate(iter(mmap_obj.readline, b'')):
                            cnt += __matches_in_line(fnm, fnd, cnt, num, lin)
                except ValueError as e:
                    # print(f'\nValueError: {fnm}\n  *** {e} ***')
                    pass
            return cnt

        def __matches_in_line(fnm, fnd, cnt, num, lin):
            lin = lin.decode('iso-8859-1').strip('\n')

            # count matches, discard when none found
            if not (occ := len(re.findall(fnd_reg, lin))):
                return occ

            # filename header before 1st match in file
            if not cnt:
                txt = f'\n  {fnm}:'
                if DEBUG['SCH']: print(f'{txt}')
                self.stc_res.AddText(f'{txt}\n')

            # output 1st and possible next matches
            for n in range(occ):
                if not n:
                    txt = f'  {num + 1:5d}: {lin}'
                    if DEBUG['SCH']: print(f'{txt}')
                    # if self.cbx_cxt:
                    #     self.stc_res.AddText(f'  {num:5d}_ {lin}\n')
                    self.stc_res.AddText(f'{txt}\n')
                    # if self.cbx_cxt:
                    #     self.stc_res.AddText(f'  {num + 2:5d}_ {lin}\n')
                    #     self.stc_res.AddText(f'  .....\n')
                # else:
                #     if DEBUG['SCH']: print(f'     >>  {lin}')
                #     self.stc_res.AddText(f'     >>  {lin}\n')

            return occ

        def __view_container_content():
            if not DEBUG['SCH']:
                return
            for lst in WHR_TYP:
                print(f'  [   {WHR_DSC[lst]:14} ] = {WHR_TYP[lst]}')

#@@@----@@@@@
        if DEBUG['SCH']: print('1.  WHERE STRING')
        whr_str = whr
        # whr_str = r'<open folders>, <open files>, <current file>, <preview>, D:\Dev\D\wx\TSN_SPyE\src, -*.py, *.cfg, *.cfg_spec, *.dbg, -*/_DEV/*, -*/zz_TODO/*, -*/extern/*'
        if DEBUG['SCH']: print(f'  [{whr_str}]')

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n2a. REMOVE spaces')
        whr_str = whr_str.replace(' ', '')
        if DEBUG['SCH']: print(f'  [{whr_str}]')

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n2b. REPLACE backslash [\\] with slash [/]')
        whr_str = whr_str.replace('\\', '/')
        if DEBUG['SCH']: print(f'  [{whr_str}]')

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n3.  SPLIT into elements')
        whr_lst = whr_str.split(',')
        for whr in whr_lst:
            if DEBUG['SCH']: print(f'  [{whr}]')

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n4.  BUILD data containers per element type')

        #FIX, needs better coding...
        WHR_DSC = {
            'OFD': '<tag>', 'OFL': '<tag>', 'CFL': '<tag>', 'BIN': '<tag>', 'PVW': '<tag>',
            'DSC': '_DISCARD', 'ITG': '_INVALID_<tag>',
            'INC': 'Include', 'EXC': 'eXclude',
            'PAT': 'Path', 'FIL': 'File',
        }

        # where string: element types (tag type: max items = 1)
        WHR_TYP = {
            'OFD': [],  # tag: open folders
            'OFL': [],  #  " : open files
            'CFL': [],  #  " : current file
            'BIN': [],  #  " : allow binary content
            'PVW': [],  #  " : preview (dry run)
            'ITG': [],  #  " : INVALID
            'INC': [],  # includes
            'EXC': [],  # excludes
            'PAT': [],  # pathnames
            'FIL': [],  # filenames
            'DSC': [],  # DISCARD
        }

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, use regex below wherever possible

        # regex filters
        # tag patterns
        tag_reg = []
        for reg in ('openfolders', 'openfiles', 'currentfile', 'binary', 'preview'):
            tag_reg.append(re.compile(rf'^<{reg}>$', re.IGNORECASE))
        # in/exclude with subdir/extension pattern
        flt_reg = re.compile(r'[+-]{0,1}\*\.{0,1}[a-zA-Z0-9_\-.()/:\\]*\*{0,1}')
        # pathname pattern
        pat_reg = re.compile(r'^[a-zA-Z]{0,1}[:]{0,1}[/\\]{0,1}[a-zA-Z0-9_\-.()/\\]+')
        # filename pattern
        fil_reg = re.compile(r'^[a-zA-Z0-9_\-.()]+')  # \*{0,1}
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        for whr in whr_lst:
            if tag_reg[0].match(whr):
                WHR_TYP['OFD'] = [whr]
                dsc = '<tag>'
            elif tag_reg[1].match(whr):
                WHR_TYP['OFL'] = [whr]
                dsc = '<tag>'
            elif tag_reg[2].match(whr):
                WHR_TYP['CFL'] = [whr]
                dsc = '<tag>'
            elif tag_reg[3].match(whr):
                WHR_TYP['BIN'] = [whr]
                dsc = '<tag>'
            elif tag_reg[4].match(whr):
                WHR_TYP['PVW'] = [whr]
                dsc = '<tag>'
            elif any(c in whr for c in '<>'):
                WHR_TYP['ITG'].append(whr)
                dsc = '_INVALID_<tag>'
            elif flt_reg.match(whr):
                lst, pfx = ('INC', '+ In') if not whr.startswith('-') else ('EXC', '- eX')
                WHR_TYP[lst].append(whr)
                dsc = f'{pfx}clude'
            # elif Path(whr).is_dir():
            elif pat_reg.match(whr):
                WHR_TYP['PAT'].append(whr)
                dsc = 'Path'
            # elif Path(whr).is_file():
            elif fil_reg.match(whr):
                WHR_TYP['FIL'].append(whr)
                dsc = 'File'
            elif whr:
                WHR_TYP['DSC'].append(whr)
                dsc = '_DISCARD'
            else:
                continue

            # prefix spaces when 1st char not plus/minus
            dsc =  '  ' + dsc if dsc[0] not in '+-' else dsc
            if DEBUG['SCH']: print(f'  [ {dsc:16} ] = [{whr}]')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, convert '<openfolders>', '<openfiles>', '<currentfile>' tags to list of pathnames
        # if WHR_TYP['OFD']:
        #     pass

        # if WHR_TYP['OFL']:
        #     for __, doc in glb.NBK.open_docs():
        #         print(doc.pnm)
        #         pnm = doc.pnm.replace('\\', '/')
        #         WHR_TYP['PAT'].append(pnm)

        # if WHR_TYP['CFL']:
        #     pass

        # if WHR_TYP['PVW']:
        #     pass
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n5a. FULL container content')
        __view_container_content()

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n5b. UNIQUE container content')
        rm_pfx = lambda pfx, lst: list(e if not e.startswith(pfx) else e[1:] for e in lst)

        # strip '+'/'-' prefix from include/exclude container elements
        WHR_TYP['INC'] = rm_pfx('+', WHR_TYP['INC'])
        WHR_TYP['EXC'] = rm_pfx('-', WHR_TYP['EXC'])

        # deduplicate lists
        for lst in WHR_TYP:
            WHR_TYP[lst] = list(set(WHR_TYP[lst]))

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        inc_reg = re.compile(r'|'.join([fnmatch.translate(x) for x in WHR_TYP['INC']]))
        exc_reg = re.compile(r'|'.join([fnmatch.translate(x) for x in WHR_TYP['EXC']]) or r'$.')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        __view_container_content()

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n6.  VALIDATE pathnames')
        pat_lst = [p for p in WHR_TYP['PAT']]

        pat_cnt = 0
        for pat in pat_lst:
            if not Path(pat).exists():
                pat_cnt += 1
                if DEBUG['SCH']: print(f'    discard [{pat}]')
                # delete from pathnames list
                WHR_TYP['PAT'].remove(pat)
                # add to discard list
                WHR_TYP['DSC'].append(pat)

        if DEBUG['SCH']: print(f'\n  #paths: {pat_cnt} discarded\n')

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if pat_cnt == len(pat_lst):
            txt = 'No valid path specified in [Where:] field, reverting to default: <open files>'
            if DEBUG['SCH']: print(f'\n  {txt}')

#HACK: force header wrap to next line
            txt = txt.replace(',', ', '+' '*5)

            dsc = f'Check discarded item(s) for cause:'
            for idx, itm in enumerate(WHR_TYP['DSC']):
                dsc += f'\n    {idx + 1}. {itm}'

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, help examples for 'Where:' field
            hlp_whr = '\n\n'
            for idx in range(10):
                hlp_whr += f'    {idx + 1}.\n'

            msg = f'{txt}\n\n{dsc}\n\n... optional help (examples) ...' + hlp_whr
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            msg_box(self, 'WARN', msg, extra='Find in Files')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        for pat in WHR_TYP['PAT']:
            if DEBUG['SCH']: print(f'     accept [{pat}]')
        if DEBUG['SCH']: print(f'\n  #paths: {len(WHR_TYP["PAT"])} accepted')

        del pat_lst

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n7.  WALK pathnames list, apply filters')
        flt_cnt = 0

        all_fil_lst = []  # files to match with filter criteria ('Where' field)
        fif_fil_lst = []  # files to search through (matching filter criteria)

#NOTE, prevent circular dependency
        from common.file import is_junction

        for pat in WHR_TYP['PAT']:

            pat_fil_lst = []  # files in path that match filter criteria

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # for fil in WHR_TYP['FIL']:
            #     print(f'fil = [{fil}]')
            #     pnm = Path(pat, '**/', fil)
            #     glb_lst = glob.glob(pnm, recursive=True)
            #     # glob returns list of 0 or more matches
            #     if not glb_lst:
            #         print(f'   -- skip: [{fil}]\n')
            #         continue
            #     # pprint(f'glb_lst = {glb_lst}', indent=7, width=99)
            #     for glb in glb_lst:
            #         pnm = str(resolve_path(glb)).replace('\\', '/')
            #         # print(f'++ include: {pnm}')
            #         # print(f'  {Path(pnm).exists()}')
            #         # print(f'  {fnmatch.fnmatch(pnm, "*")}', '\n')
            #     print()
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#INFO, python - Filtering os.walk() dirs and files - Stack Overflow
#INFO, URL=https://stackoverflow.com/questions/5141437/filtering-os-walk-dirs-and-files

            # all_fil_lst = [Path(root, fnm) for root, dirs, files in os.walk(pat) for fnm in files]

            #@@@@@@@@@@@@@@@@@@@@@@@@@@
            # tmp_cnt = 0
            #@@@@@@@@@@@@@@@@@@@@@@@@@@
            for root, dirs, files in os.walk(pat):

#HACK: detect/discard junction (directory reparse point)
                if resolve_path(root) != Path(root):
                    print(f'{resolve_path(root)}\n{Path(root)}\n')
                    continue

                for fnm in files:

                    #@@@@@@@@@@@@@@@@@@@@@@@@@@
                    # if tmp_cnt % 300 == 0:
                    #     self.tmr_spb.Notify()
                    #@@@@@@@@@@@@@@@@@@@@@@@@@@

                    #@@@@@@@@@@@@@@@@@@@@@@@@@@
                    # tmp_cnt += 1
                    #@@@@@@@@@@@@@@@@@@@@@@@@@@
                    all_fil_lst.append(Path(root, fnm))

                    #@@@@@@@@ NOT USED YET @@@@@@@@@
                    # ext = Path(fnm).suffix[1]
                    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                    pnm = str(resolve_path(root, fnm)).replace('\\', '/')

                    if exc_reg.match(pnm):
                        # print(f' - exclude: {pnm}')
                        continue
                    elif inc_reg.match(pnm):
                        if DEBUG['SCH']: print(f'+  include: {pnm}')
                        flt_cnt += 1
                        fif_fil_lst.append(pnm)
                        pat_fil_lst.append(Path(root, fnm))

            if DEBUG['SCH']: print(f'\n  ALL files in {pat}: {len(pat_fil_lst)}\n')


        if DEBUG['SCH']: print(f'\n  #files (filtered): {flt_cnt}')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ FOR TESTING: RETURN EARLY @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if DEBUG['SCH']: print(f'{WHR_TYP["PVW"] = }')
        if DEBUG['SCH']: print(f'{inc_reg = }')
        if DEBUG['SCH']: print(f'{exc_reg = }')

        # for f in all_fil_lst:
        #     print(f)

        if DEBUG['SCH']: print(f'\n  ALL files scanned: {len(all_fil_lst)}\n')

        # self.gge_spb.SetValue(100)
        # self.btn_can.Label = 'Finish'
        # dbg_TIMER('search', 'STOP')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, replace 'fif_fil_lst' with 'all_fil_lst'?
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ FOR TESTING: RETURN EARLY @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n8a. FULL file list')
        srt_cnt = 0
        for fil in sorted(fif_fil_lst):
            srt_cnt += 1
            # print(f'  [{fil}]')

        if DEBUG['SCH']: print(f'\n  #files (FULL, filtered, sorted): {srt_cnt}')

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n8b. UNIQUE file list')
        fif_fil_lst = sorted(list(set(fif_fil_lst)))

        unq_cnt = 0
        for fil in fif_fil_lst:
            unq_cnt += 1
            # print(f'  [{fil}]')

        if DEBUG['SCH']: print(f'\n  #files (UNIQUE, filtered, sorted)): {unq_cnt}\n')
        # save count of files to search through for later
        sch_cnt = unq_cnt


#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n8c. PREVIEW only')

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if WHR_TYP['PVW']:
            txt = ' Preview only'
            msg = f'{txt}\n\n[[[Extra Text]]]\n\n'
            msg_box(self, 'INFO', msg, extra='Find in Files')
            return
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@----@@@@@
        if DEBUG['SCH']: print('\n\n9.  SEARCH, apply option flags')

        # clear search results
        glb.TLW.sch_res_active = True
        self.stc_res.ClearAll()

        # set search flags and description
        flg_cas = flg_reg = flg_wrd = False
        flg_dsc = TXT_NIL

        if self.cbx_cas.Value:
            flg_cas = True
            flg_dsc += 'case sensitive, '
        if self.cbx_reg.Value:
            flg_reg = True
            flg_dsc += 'regex, '
        if self.cbx_wrd.Value:
            flg_wrd = True
            flg_dsc += 'whole word'

        # surround with parens, strip last ', '
        if flg_dsc:
            flg_dsc = f'({flg_dsc.rstrip(", ")})'

        # both normal and regex search use compiled regex
        fnd_str = fnd
        flg_cas = 0 if flg_cas else re.IGNORECASE                 # case?
        fnd_str = re.escape(fnd_str) if not flg_reg else fnd_str  # regex?
        fnd_str = rf'\b{fnd_str}\b' if flg_wrd else fnd_str       # word?

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # import warnings
        # warnings.filterwarnings('ignore')
        # warnings.warn('catch regex exception')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#INFO, catch regex exception
#INFO, URL=https://docs.python.org/3/library/re.html#re.error
        try:
            fnd_reg = re.compile(rf'{fnd_str}', flg_cas)
        except re.error as e:
            glb.SB.set_text('Regex error', typ='ERROR')
            self.set_back_colour()
            dbg_FOCUS(self.txc_fnd)

            # self.txc_fnd.SetStyle(10, 11, wx.TextAttr(wx.RED, wx.YELLOW))

            msg = f'Regex error:\n\n{e.msg}\n    at position {e.pos + 1}\n    in pattern "{e.pattern}"'
            if DEBUG['SCH']: print(msg.replace('\n\n', ' ').replace('\n   ', ''))
            msg_box(self, 'ERROR', msg, extra='Regular Expression')
            return

        # dbg_TIMER('search', 'STOP')
        # dbg_TIMER('search')

        txt = f'Searching {sch_cnt} files for [{fnd}] {flg_dsc}'
        if DEBUG['SCH']: print(f'\n{txt}')
        self.stc_res.AddText(f'{txt}\n')

        tot = 0      # total matches
        flc = 0      # file count
        spb_cnt = 0  # progress bar value

        # self.txc_rpl.SetBackgroundColour('GREEN')

        for fil in fif_fil_lst:
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, current filename needs own proper field or banner message
            self.txc_rpl.Value = fil
            self.txc_rpl.Update()
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            #@@@@@@@@@@@@@@@@@@@@@@@
            # if exc_reg.match(fil):
            #     print('excludes')
            #     continue
            #@@@@@@@@@@@@@@@@@@@@@@@

            # #matches in this file
            mch_cnt = __file_io(fil)
            # mch_cnt = __mmap_io(fil)

            # quit when 'Cancel' button pressed
            if self.fif_cancelled:
                break

            if mch_cnt:
                flc += 1
                tot += mch_cnt

            spb_cnt += 1
            self.gge_spb.SetValue(spb_cnt / len(fif_fil_lst) * 100)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        if DEBUG['SCH']: print()
        dbg_TIMER('search', 'STOP')

        # search results summary
        can_txt = ' ** CANCELLED **' if self.fif_cancelled else ''
        tot_txt = f'{tot} match ' if tot == 1 else f'{tot} matches '
        tot_txt += f'across {flc} files' if flc > 1 else f'' if not flc else f'in 1 file'
        ftr_txt = f'\nFinished searching {sch_cnt} files for [{fnd}] {flg_dsc}'
        print(ftr_txt)
        print(f'\n  {tot_txt}\n')
        self.stc_res.AddText(f'\n  {tot_txt}')
        self.stc_res.AddText(ftr_txt)
        pos = self.stc_res.PositionFromLine(1)
        self.stc_res.InsertText(pos, f'  {tot_txt}\n')

        msg = f'Find in Files{can_txt}\n\nSearched {sch_cnt} files for [{fnd}]: {flg_dsc}\n\n{tot_txt}'
        msg_box(self, 'INFO', msg, extra='Search Results')

        if not self.fif_cancelled and tot:

            # self.stc_res.Freeze()

            self.set_mode('RES')
            glb.SPL['SCH'].SetSashPosition(-700)

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # for idx in range(35):
            #     # wx.MilliSleep(5)
            #     glb.SPL['SCH'].SetSashPosition(-idx*21)
            #     glb.SPL['SCH'].Update()
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # from const.lang import FACES
            # self.stc_res.StyleSetSpec(stc.STC_STYLE_DEFAULT, 'face:%(helv)s,size:%(size)d' % FACES)
            # self.stc_res.StyleSetBackground(stc.STC_STYLE_DEFAULT, glb.CFG['Editor']['DefaultBackColour'])
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # self.stc_res.StyleSetBackground(stc.STC_STYLE_DEFAULT, 'BLUE')
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # go to top of search results
            self.stc_res.DocumentStart()
            self.stc_res.mark_matches(ind=4, fnd=fnd)

            # self.stc_res.Thaw()

            wx.CallAfter(dbg_FOCUS, self.stc_res)
        else:
            # no results, back to 'find field'
            self.txc_fnd.SelectAll()
            wx.CallAfter(dbg_FOCUS, self.txc_fnd)


        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.gge_spb.SetValue(0)
        self.stt_rpl.Label = 'R&eplace:'
    #     wx.CallLater(5000, self._resize_progress_bar)

    # def _resize_progress_bar(self):
    #     gbs = self.Sizer
    #     gbs.Detach(self.gge_spb)
    #     # gbs.Add(self.cbx_cxt, (5, 5+2), (1, 1), wx.ALL, 5)
    #     # gbs.Add(self.cbx_buf, (5, 5+3), (1, 1), wx.ALL, 5)
    #     # gbs.Add(self.gge_spb, (5, 5+4), (1, 2), wx.ALL | wx.EXPAND, 5)
    #     # self.Layout()
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def do_replace_in_files(self, doc, fnd, rpl, whr, flg):
        print(f'{me_("F")}: [{fnd}] [{rpl}] [{whr}]')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# PROCESS RESULTS
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def toggle_mouse_active(self, evt, enable=True):
        # disable mouse hover when keyboard active, enable when mouse moved
        self.stc_res.Bind(wx.EVT_MOTION, self.do_result_line if enable else lambda e: self.toggle_mouse_active(e, enable=False))

    def do_result_line(self, evt, kpr_sct=None):
        # hover over line in 'search results'
        def __hover():
            dbg_FOCUS(self.stc_res)

            self.stc_res.SetCaretLineVisible(True)
            self.stc_res.SetSelBackground(True, '#3399FF')
            # 'get_char_pos' uses 'CharPositionFromPointClose'
            x, y, pos = get_char_pos(self.stc_res)
            # so when hovering over virtual space, we need to adjust
            if pos < 0:
                pos = self.stc_res.CharPositionFromPoint(x, y)

            lnr = self.stc_res.LineFromPosition(pos)
            txt = self.stc_res.GetLineText(lnr)

            fil_reg = re.compile(rf'^  [^ ].*:$')  # filename pattern
            fil_mch = fil_reg.search(txt)
            lin_reg = re.compile(rf'^ *?[0-9]+:')  # line number pattern
            lin_mch = lin_reg.search(txt)

            pos = self.stc_res.PositionFromLine(lnr)

            if fil_mch:
                end, grp = fil_mch.end(), fil_mch.group(0)
                self.stc_res.SetSelBackground(True, 'ORANGE')
                self.stc_res.SetSelection(pos, pos + end)
                ttp = self.stc_res.SelectedText
                self.stc_res.SetToolTip(ttp)
            elif lin_mch:
                end, grp = lin_mch.end(), lin_mch.group(0)
                self.stc_res.SetSelBackground(True, 'BLUE')
                self.stc_res.SetSelection(pos + 2, pos + end)
            elif txt.startswith('     >>'):
                self.stc_res.SetSelBackground(True, 'GREEN')
                self.stc_res.SetSelection(pos + 2, pos + 8)
            else:
                self.stc_res.SetCaretLineVisible(False)
                self.stc_res.SelectNone()
                self.stc_res.GotoPos(pos)

        # go to next/previous 'search result' with keypress
        def __next_prev():
            print(f'{kpr_sct} detected')
            self.toggle_mouse_active(None, enable=False)

            if kpr_sct in ('F4', 'F5'):
                to = self.stc_res.TextLength
                self.stc_res.LineEnd()
            elif kpr_sct in ('Shift+F4', 'Shift+F5'):
                to = 0
                self.stc_res.Home()
            else:
                return

            if kpr_sct in ('F4', 'Shift+F4'):
                self.stc_res.SetSelBackground(True, 'BLUE')
                fnd = rf'^ *?[0-9]+:'
            elif kpr_sct in ('F5', 'Shift+F5'):
                self.stc_res.SetSelBackground(True, 'ORANGE')
                fnd = rf'^  [^ ].*:$'

            fr, flg = self.stc_res.CurrentPos, stc.STC_FIND_REGEXP

            if (pos := self.stc_res.FindText(fr, to, fnd, flg)) == stc.STC_INVALID_POSITION:
                if kpr_sct in ('F4', 'F5'):
                    self.stc_res.Home()
                elif kpr_sct in ('Shift+F4', 'Shift+F5'):
                    self.stc_res.LineEnd()
                fr = self.stc_res.CurrentPos
                pos = self.stc_res.FindText(fr, to, fnd, flg)
                # return

            self.stc_res.Home()
            self.stc_res.SetSelection(pos + 2, pos + 8)
            # self.stc_res.VerticalCentreCaret()
            self.stc_res.EnsureCaretVisible()
            if kpr_sct in ('F5', 'Shift+F5'):
                self.stc_res.SetSelection(pos + 2, pos + self.stc_res.GetLineLength(self.stc_res.CurrentLine))

            # self.stc_res.GotoPos(pos)

            # # return line number or filename
            # lnr = self.stc_res.LineFromPosition(pos)
            # lnf = self.stc_res.GetLineText(lnr)[:-1]

        # double-click line in 'search results'
        def __select():
            def __reverse_find(typ):
                fr, to, flg = self.stc_res.CurrentPos, 0, stc.STC_FIND_REGEXP
                fnd = rf'^ *?[0-9]+:' if typ == 'LIN' else rf'^  [^ ].*:$'

                if (pos := self.stc_res.FindText(fr, to, fnd, flg)) == stc.STC_INVALID_POSITION:
                    # we should NEVER get here
                    return ''

                # return line number or filename
                lnr = self.stc_res.LineFromPosition(pos)
                lnf = self.stc_res.GetLineText(lnr)[:-1]
                return lnf

            # clear selections, get line content
            self.stc_res.SelectNone()
            lnr = evt.Line
            self.stc_res.GotoLine(lnr)
            self.stc_res.LineEnd()

            # find line number for current line
            lnr = self.stc_res.GetLineText(lnr)
            if  lnr.startswith('     >>'):
                lnr = __reverse_find('LIN')
            elif not lnr:
                return

            # find filename for current line number
            fnm = __reverse_find('FNM').strip()
            if not fnm:
                return

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, prevent circular dependency
            from common.file import open_files

            fil_lst = [[fnm.replace('/', '\\')]]
            doc = open_files(fil_lst)

            try:
                lnr = int(lnr[2:7])
            except ValueError as e:
                # double-clicked filename
                lnr = doc.CurrentLine + 1

            self.stc_res.Home()
            print(f'Selected: [{lnr:5}]  [{fnm}]')

            # if not (doc := get_doc()): return

            doc.GotoLine(lnr - 1)
            doc.VerticalCentreCaret()
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # 'EVT_' event types handled: wx.EVT_MOTION, stc.EVT_STC_DOUBLECLICK
        try:
            typ = evt.EventType
        except AttributeError as e:
            typ = 'KEYBOARD_USED'

        self.stc_res.SetCaretLineBackground('#C6E2FF')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, switch from keyboard to mouse activity or vice versa
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # disable mouse hover when keyboard active, enable when mouse moved
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # self.stc_res.prv_res_xy = (-1, -1)  # last coordinates (search results)

        # x, y, pos = get_char_pos(self.stc_res)

        # if (x, y) == self.stc_res.prv_res_xy:
        #     return

        # self.stc_res.prv_res_xy = (x, y)

        # # wait until mouse cursor moves
        # while self.stc_res.prv_res_xy == get_char_pos(self.stc_res)[:2]:
        #     pass
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        if typ == wx.EVT_MOTION.typeId:
            __hover()
        elif typ == stc.EVT_STC_DOUBLECLICK.typeId:
            __select()
        elif typ == 'KEYBOARD_USED':
            __next_prev()
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    # def _update_progress_bar(self, evt):
    #     # discard when not our timer
    #     if evt.Timer.Id != self.tmr_spb.Id:
    #         evt.Skip()
    #         return

    #     self.spb_cnt += 10
    #     if self.spb_cnt >= 1000:
    #         self.spb_cnt = 0
    #         self.tmr_spb.Stop()
    #     self.gge_spb.SetValue(self.spb_cnt)

###############################################################
# OBSOLETE code -> issue SOLVED in 'lost_focus' in 'SPyE.py'
###############################################################
#DONE, SOLVED to debug wx.TextCtrl 'find entry' for occasional: missing caret, beep sound, focus issues
    #     # for att in dir(self.txc_fnd):
    #     #     typ = type(getattr(self.txc_fnd, att))
    #     #     if 'builtin_function_or_method' in str(typ):
    #     #         print(att, typ)

    #     # for wgt in ('txc_fnd', 'txc_rpl', 'txc_whr'):
    #     #     getattr(self, wgt).Bind(wx.EVT_ENTER_WINDOW, self.set_focus)
    #     #     getattr(self, wgt).Bind(wx.EVT_CHILD_FOCUS, self.set_child_focus)

    # def set_focus(self, evt):
    #     obj = evt.EventObject
    #     print(f'     set_focus: {obj} [{obj.__class__.__name__}]')
    #     # obj.Enable()
    #     # dbg_FOCUS(self)
    #     # dbg_FOCUS(obj)
    #     # obj.ShowNativeCaret()
    #     # obj.Caret.Show()
    #     evt.Skip()

    # def set_child_focus(self, evt):
    #     obj = evt.EventObject
    #     print(f'set_child_focus: {obj} [{obj.__class__.__name__}]')
    #     # dbg_FOCUS(obj)
    #     # obj.Refresh()
    #     # obj.Layout()
    #     # obj.Update()
    #     evt.Skip()
###############################################################
# OBSOLETE code: END
###############################################################

#INFO, URL=https://www.blog.pythonlibrary.org/2013/01/11/how-to-get-a-list-of-class-attributes/
        # # show class variable names
        # for wgt in self.__dict__:
        #     if not wgt == 'cls_var_nam':
        #         att = getattr(self, wgt)
        #         att.Hide()


if __name__ == '__main__':

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: module TESTING
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # from const.app import LOC
    # print(LOC['CFG']['FIL'])

    # LOC['CFG']['FIL'] ='D:\\Dev\\D\\wx\\TSN_SPyE\\dev\\spye\\conf\\SPyE.cfg'
    # print(LOC['CFG']['FIL'])

    # from app.startup import startup

    # DBG, CFG, LNG, MNU, PLG, THM = startup()  # DBG, PLG not used
    # glb.CFG = CFG
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    app = wx.App(False)
    frm = wx.Frame(None, size=(850, 200))
    SearchPanel(frm)
    frm.Show()
    app.MainLoop()
