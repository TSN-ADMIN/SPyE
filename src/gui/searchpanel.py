#!/usr/bin/python

import fnmatch
import mmap
import os
from pathlib import Path
from pprint import pprint
import re

import wx
from wx import stc

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: module TESTING
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# import sys
# sys.path.insert(0, os.path.dirname('..'))

# # print(os.getcwd())
# # if __name__ == '__main__':
#     os.chdir('..')    # from const.app import LOC
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

from common.path import resolve_path
from common.type import is_btn, is_cbx, is_list, is_stb, is_stt, is_txc, is_stc
from common.util import curdoc, curdoc_class, rs_, get_char_pos, get_keypress, is_shown, msg_box, not_implemented
from conf.debug import DBG, DEBUG, dbf, me_
from const.app import CLR
from const.common import LBL_FNT_STYLES, TXT_NIL
from const import glb
from const.lang import LANG
from const.menubar import MI
from const.searchpanel import (
    SCH_FLAGS, SCH_HIS_KEYS, SCH_KEYS, SCH_MAP, SCH_TTP, WHR, PTN
)
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
        mix.Help.__init__(self)

        self.mode = 'FND'  # mode: FND/RPL/FIF/INC
        self.pos_inc = 0  # current position at start of INC mode
        self.tmr_clr = wx.Timer(self, wx.ID_ANY)
        self.tmr_pgb = wx.Timer(self, wx.ID_ANY)

        # tab traversal allowed for ALL fields OR textctrl's ONLY
        self.ttv_all = self.sec['TabTraversalAll']

        # lists for common and mode-specific widgets/icons
        self.wgt_lst = None
        self.ico_lst = None
        # self.pgb_cnt = 0  # progress bar value

        self.create_widgets()

        # search fields history
        self.txc_fnd.his_lst, self.txc_fnd.his_idx = [], 0  # 0: 1st item, -1: empty list
        self.txc_rpl.his_lst, self.txc_rpl.his_idx = [], 0
        self.txc_whr.his_lst, self.txc_whr.his_idx = [], 0

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
#NOTE, EXPERIMENTAL: CMD session to flush/force stdout/stderr to console
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
#HACK, avoid error AttributeError: 'SearchPanel' object has no
#            attribute 'FindItemById' in '_keyword_set_handler'
        # self.Bind(wx.EVT_TOOL_RANGE, lambda e: e.Skip(False))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, binds not working correctly for checkbox w/ Enter or ESC key
        self.txc_fnd.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'FNF'))  # Find field
        self.txc_rpl.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'RPF'))  # Replace field
        self.txc_whr.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'WHF'))  # Where field

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
                             self.do_find(e, glb.NBK.CurrentPage,  # .txt1
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

    def create_widgets(self):

        siz = self.sec['IconSize']

        for key in {'Case','Regex','Word','Wrap','Insel','Hilite','Prcase','Context','Buffer'}:
            SCH_TTP[f'ico_{siz}_{key}'] = SCH_TTP[f'ico{key}'].replace(f'ico{key}', f'ico_{siz}_{key}')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, move block below to 'constant.py'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # text control common arguments: value, pos, size, style
        _txc_arg = ('', wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER)  # | wx.TE_RICH)
#HACK, non-default 'txcIncremental' size aligns better when switching search mode (not optimal yet)
        _txc_arg_inc = ('', wx.DefaultPosition, (-1, 26), wx.TE_PROCESS_ENTER)

        # # widget classes
        # btn = wx.Button
        # cbx = wx.CheckBox
        # wx.Gauge = wx.Gauge
        # ico = wx.StaticBitmap
        # stc = gui.Editor  # stc.StyledTextCtrl
        # stt = wx.StaticText
        # txc = wx.TextCtrl

#NOTE, prefix of '8 space chars' in 'value' of 'stt_fnd' is needed for precise alignment when switching search mode
        pfx, siz = rs_(8, ' '), glb.CFG['SearchPanel']['IconSize']

        # search panel widget definitions
        SCH_WIDGETS = {
        #   attribute:  class            label/value/style       window name
        #   ----------  -----            ---------------------   -----------------
            'stt_fnd': (wx.StaticText,   f'{pfx}&Find:',         'sttFind'),
            'txc_fnd': (wx.TextCtrl,     _txc_arg,               'txcFind'),
            'btn_fnd': (wx.Button,       'Find',                 'btnFind'),
            'btn_fnp': (wx.Button,       'Find Prev',            'btnFindPrev'),
            'btn_fna': (wx.Button,       'Find All',             'btnFindAll'),

            'stt_whr': (wx.StaticText,   'W&here:',              'sttWhere'),
            'txc_whr': (wx.TextCtrl,     _txc_arg,               'txcWhere'),
            'btn_whr': (wx.Button,       '...',                  'btnWhere'),

            'stt_rpl': (wx.StaticText,   'R&eplace:',            'sttReplace'),
            'txc_rpl': (wx.TextCtrl,      _txc_arg,               'txcReplace'),
            'btn_rpl': (wx.Button,       'Replace',              'btnReplace'),
            'btn_rpa': (wx.Button,       'Replace All',          'btnReplaceAll'),

#HACK, non-default size
            'stt_inc': (wx.StaticText,   f'{pfx}&Incr:',         'sttIncremental'),
            'txc_inc': (wx.TextCtrl,     _txc_arg_inc,           'txcIncremental'),

            'btn_cnt': (wx.Button,       'Count',                'btnCount'),

            'cbx_cas': (wx.CheckBox,     '&Case sensitive',      'cbxCase'),
            'cbx_reg': (wx.CheckBox,     '&Regular expression',  'cbxRegex'),
            'cbx_wrd': (wx.CheckBox,     '&Whole word',          'cbxWord'),

            'cbx_wrp': (wx.CheckBox,     'Wrap around',          'cbxWrap'),
            'cbx_isl': (wx.CheckBox,     'In selection',         'cbxInsel'),
            'cbx_hlm': (wx.CheckBox,     'Highlight matches',    'cbxHilite'),
            'cbx_pcs': (wx.CheckBox,     'Preserve case',        'cbxPrcase'),

            'cbx_cxt': (wx.CheckBox,     'Show context',         'cbxContext'),
            'cbx_buf': (wx.CheckBox,     'Use buffer',           'cbxBuffer'),

            'gge_pgb': (wx.Gauge,        'Search Progress Bar',  'ggeProgressBar'),
            'btn_can': (wx.Button,       'Cancel',               'btnCancel'),

            'ico_hlp': (wx.StaticBitmap, PNG[f'help_{siz}'],     'icoHelp'),

            'ico_cas': (wx.StaticBitmap, PNG[f'sch_cas_{siz}'],  f'ico_{siz}_Case'),
            'ico_reg': (wx.StaticBitmap, PNG[f'sch_reg_{siz}'],  f'ico_{siz}_Regex'),
            'ico_wrd': (wx.StaticBitmap, PNG[f'sch_wrd_{siz}'],  f'ico_{siz}_Word'),
            'ico_wrp': (wx.StaticBitmap, PNG[f'sch_wrp_{siz}'],  f'ico_{siz}_Wrap'),
            'ico_isl': (wx.StaticBitmap, PNG[f'sch_isl_{siz}'],  f'ico_{siz}_Insel'),
            'ico_hlm': (wx.StaticBitmap, PNG[f'sch_hlm_{siz}'],  f'ico_{siz}_Hilite'),
            'ico_pcs': (wx.StaticBitmap, PNG[f'sch_pcs_{siz}'],  f'ico_{siz}_Prcase'),
            'ico_cxt': (wx.StaticBitmap, PNG[f'sch_cxt_{siz}'],  f'ico_{siz}_Context'),
            'ico_buf': (wx.StaticBitmap, PNG[f'sch_buf_{siz}'],  f'ico_{siz}_Buffer'),

            'stc_res': (gui.Editor,      'Search Results',       'stcResults'),
        }

        DBG('SCH', f'{me_("C")}: Widget definitions')

        # build widgets from definition
        for key, val in SCH_WIDGETS.items():
            cls, lvs, nam = val
            # text control
            if val[0] is wx.TextCtrl:
                setattr(self, key, cls(self, value=lvs[0], pos=lvs[1], size=lvs[2], style=lvs[3], name=nam))
            # icon
            elif val[0] is wx.StaticBitmap:
                setattr(self, key, cls(self, bitmap=lvs.Bitmap, size=(siz,siz), name=nam))
            # gauge
            elif val[0] is wx.Gauge:
                setattr(self, key, cls(self, name=nam))
            # styledtextctrl
            elif val[0] is gui.Editor:
                setattr(self, key, cls(self, ['', lvs, '', '']))
                self.stc_res.SetName(nam)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: styling of search results
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, create new lexer for styling of search results
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                lng_lst = [t for t in LANG if t[1] == 'text']
                self.stc_res.update_language_styling(lng_lst)
                # self.stc_res.StyleSetBackground(stc.STC_STYLE_DEFAULT, 'GREEN')
                # self.stc_res.StyleClearAll()
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
                print(f'  {wgt_def=}')

        DBG('SCH')

#FIX, create function 'set_font_style' in 'util.py'
        # static text widget: label font style
        for wgt in {'fnd', 'whr', 'rpl', 'inc'}:
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
            extra_wgt_lst = ('stt_whr', 'txc_whr', 'stt_rpl', 'txc_rpl', 'btn_fnd', 'btn_whr', 'btn_rpl', 'btn_cnt', 'cbx_cas', 'cbx_reg', 'cbx_wrd', 'cbx_cxt', 'cbx_buf', 'gge_pgb', 'btn_can')
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
            # if wgt in {'gge_pgb', 'btn_can'}:
            #     self.gge_pgb.Hide()
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
    @curdoc
    def dispatch(self, evt):


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
        #     # dbf.FOCUS(self)
        #     print(nav_key_evt)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        # event types handled: 'EVT_CHAR_HOOK', 'EVT_BUTTON'
        typ = evt.EventType
        obj = evt.EventObject
        nam = obj.Name
        key_, map_ = SCH_KEYS, SCH_MAP  # convenient short naming (KEYS, MAP)

        # preprocess button
        if typ == wx.EVT_BUTTON.typeId:
            # convert button label to corresponding keypress
            if nam in map_:
                if self.mode == 'FIF' and nam in {'btnFind', 'btnReplace'}:
                    nam += 'All'
                kpr_sct = map_[nam]
            elif nam == 'btnWhere':
                gui.ContextMenu(evt, 'WHR')
                return
#TODO, implement thread to keep GUI available while searching
            elif nam == 'btnCancel':
                # print('[btnCancel] pressed (not implemented)')
                self.gge_pgb.SetValue(0)
                # self.btn_can.Label = 'Cancel'
                self.fif_cancelled = True
                return
            else:
                # we should NEVER get here
                err = f'{self.__class__.__name__}: unknown widget name [{nam}]'
                raise AssertionError(err)
        # preprocess keypress
        else:
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
                    dbf.FOCUS(doc)
                return

            # convert numpad key label to corresponding 'RETURN'
            if 'NUMPAD_ENTER' in kpr_sct:
                kpr_sct = kpr_sct.replace('NUMPAD_ENTER', 'RETURN')

            DBG('SCH', f'{me_("C, F")}: >>> code: {cod:3}, name: [{kpr_sct}]')

        # search parameters
        flg = self.get_flags()
        fnd = self.txc_fnd.Value
        rpl = self.txc_rpl.Value
        whr = self.txc_whr.Value

        # catch empty 'find field'
        if not fnd and kpr_sct in map_.values():
            txt = 'No text to find'
            glb.IBR.info_msg(txt, 'INFO')
            glb.SBR.set_text(txt, typ='INFO')
            self.set_back_colour('FOREST GREEN')
            self.transfer_focus(None)
            return

        if kpr_sct in (key_['Find'], key_['FindPrev']) and self.mode not in {'FIF', 'INC'}:
            self.do_find(None, doc, fnd, flg, prv=(kpr_sct != 'RETURN'))
        elif kpr_sct == key_['Count'] and self.mode != 'INC' and self.sec['ShowCountButton']:
            self.do_count(doc, fnd, flg)
        elif kpr_sct in (key_['Find'], key_['FindAll']):
            if self.mode in {'FND', 'RPL'}:
                self.do_find_all(doc, fnd, flg)
            elif self.mode == 'FIF':

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # self.gge_pgb.Show()
                # self.btn_can.Show()
                # wx.MilliSleep(200)
                # self.Update()  # force
                # self.Layout()
                # glb.TLW.Layout()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                self.do_find_in_files(fnd, whr)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # self.gge_pgb.Hide()
                # self.btn_can.Hide()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        elif kpr_sct == key_['Replace']:
            if self.mode == 'RPL':
                self.do_replace(doc, fnd, rpl, flg)
                wx.CallAfter(dbf.FOCUS, self.txc_fnd)
        elif kpr_sct == key_['ReplaceAll']:
            if self.mode == 'RPL':
                self.do_replace_all(doc, fnd, rpl, flg)
            elif self.mode == 'FIF':
                self.do_replace_in_files(doc, fnd, rpl, whr, flg)
                wx.CallAfter(dbf.FOCUS, self.txc_fnd)
#INFO, 'Ctrl+Shift+A' also selects all in text control
        elif kpr_sct == key_['SelectAll'] and is_txc(obj):
            obj.SelectAll()

        # icon (checkbox) shortcuts (Sublime emulation)
        elif kpr_sct in (key_['Case'], key_['Regex'], key_['Word']):
            ico = self.FindWindowByName(f'ico{map_[kpr_sct]}')

            if kpr_sct in (key_['Case']):
                ico = self.ico_cas
            elif kpr_sct in (key_['Regex']):
                ico = self.ico_reg
            elif kpr_sct in (key_['Word']):
                ico = self.ico_wrd

            # inject as icon; forces checkbox mapping
            evt.Id, evt.EventObject = ico.Id, ico
            self.on_icon_or_checkbox(evt)
            return

        if kpr_sct in (map_[k] for k in map_ if 'All' in k):
            glb.TLW.toggle_panel(None, 'SCH', -1)  # hide panel
            # prevent 'transfer_focus' to kill focus on document
            wx.CallAfter(dbf.FOCUS, doc)

        # propagate unhandled keypress
        evt.Skip(kpr_sct not in map_.values())

    @curdoc
    def set_mode(self, mode='FND'):
        if not (doc := glb.DOC): return
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
#         gbs.Add(self.stt_fnd, (1, 1), *_static_text)
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
        refcol = rc_ = 5 if self.sec['ShowIcons'] or mode == 'RES' else 0

        # common grid bag sizer arguments: span, flags, border (_9C = #columns)
        _static_text   = ((1, 1), wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        _static_bitmap = ((1, 1), wx.LEFT | wx.EXPAND, border)  # wx.ALIGN_CENTRE_VERTICAL
        _single_span   = ((1, 1), wx.ALL, border)
        _multi_span_2c = ((1, 2), wx.ALL | wx.EXPAND, border + 1)  # wx.ALIGN_CENTRE_VERTICAL
        _multi_span_4c = ((1, 4), wx.ALL | wx.EXPAND, border)  # wx.ALIGN_CENTRE_VERTICAL
        _full_span     = ((0, 0), wx.ALL | wx.EXPAND, 0)  # no border for results window

        # common layout
        if self.sec['ShowCountButton'] and mode != 'RES':
            # set count button row/column to fit common layout
            row, col = (2, 8) if mode == 'FND' else (3, 7) if mode == 'RPL' else (4, 6) if mode == 'FIF' else (2, 8)
            gbs.Add(self.btn_cnt, (row, rc_ + col), *_single_span)

        # set help icon row to fit common layout
        if mode != 'RES':
            ico_hlp_row = 3 if mode in ('FND', 'INC') else 4 if mode == 'RPL' else 5 if mode == 'FIF' else 3
            gbs.Add(self.ico_hlp, (ico_hlp_row, rc_ - 5), *_static_bitmap)
            gbs.Add(self.ico_cas, (1, rc_ - 5), *_static_bitmap)
            gbs.Add(self.ico_reg, (1, rc_ - 4), *_static_bitmap)
            gbs.Add(self.ico_wrd, (1, rc_ - 3), *_static_bitmap)

        # incremental mode has no buttons
        if mode not in {'INC', 'RES'}:
            gbs.Add(self.stt_fnd, (1, rc_ + 1), *_static_text)
            gbs.Add(self.txc_fnd, (1, rc_ + 2), *_multi_span_4c)
            gbs.Add(self.btn_fnd, (1, rc_ + 6), *_single_span)

        # search mode layout: 'Find', 'Replace', 'Find in Files' or 'Incremental' or 'Results'
        if mode == 'FND':
            gbs.Add(self.ico_wrp, (1, rc_ - 2), *_static_bitmap)
            gbs.Add(self.ico_isl, (1, rc_ - 1), *_static_bitmap)
            gbs.Add(self.btn_fnp, (1, rc_ + 7), *_single_span)
            gbs.Add(self.btn_fna, (1, rc_ + 8), *_single_span)

            gbs.Add(self.ico_hlm, (2, rc_ - 1), *_static_bitmap)
            gbs.Add(self.cbx_cas, (2, rc_ + 2), *_single_span)
            gbs.Add(self.cbx_reg, (2, rc_ + 3), *_single_span)
            gbs.Add(self.cbx_wrd, (2, rc_ + 4), *_single_span)

            gbs.Add(self.cbx_wrp, (3, rc_ + 2), *_single_span)
            gbs.Add(self.cbx_isl, (3, rc_ + 3), *_single_span)
            gbs.Add(self.cbx_hlm, (3, rc_ + 4), *_single_span)
        elif mode == 'RPL':
            gbs.Add(self.ico_wrp, (1, rc_ - 2), *_static_bitmap)
            gbs.Add(self.ico_isl, (1, rc_ - 1), *_static_bitmap)
            gbs.Add(self.btn_fna, (1, rc_ + 7), *_single_span)

            gbs.Add(self.ico_pcs, (2, rc_ - 5), *_static_bitmap)
            gbs.Add(self.ico_hlm, (2, rc_ - 2), *_static_bitmap)
            gbs.Add(self.stt_rpl, (2, rc_ + 1), *_static_text)
            gbs.Add(self.txc_rpl, (2, rc_ + 2), *_multi_span_4c)
            gbs.Add(self.btn_rpl, (2, rc_ + 6), *_single_span)
            gbs.Add(self.btn_rpa, (2, rc_ + 7), *_single_span)

            gbs.Add(self.cbx_cas, (3, rc_ + 2), *_single_span)
            gbs.Add(self.cbx_reg, (3, rc_ + 3), *_single_span)
            gbs.Add(self.cbx_wrd, (3, rc_ + 4), *_single_span)

            gbs.Add(self.cbx_wrp, (4, rc_ + 2), *_single_span)
            gbs.Add(self.cbx_isl, (4, rc_ + 3), *_single_span)
            gbs.Add(self.cbx_hlm, (4, rc_ + 4), *_single_span)
            gbs.Add(self.cbx_pcs, (4, rc_ + 5), *_single_span)
        elif mode == 'FIF':
            gbs.Add(self.ico_cxt, (1, rc_ - 2), *_static_bitmap)
            gbs.Add(self.ico_buf, (1, rc_ - 1), *_static_bitmap)

            gbs.Add(self.stt_whr, (2, rc_ + 1), *_static_text)
            gbs.Add(self.txc_whr, (2, rc_ + 2), *_multi_span_4c)
            gbs.Add(self.btn_whr, (2, rc_ + 6), *_single_span)

            gbs.Add(self.stt_rpl, (3, rc_ + 1), *_static_text)
            gbs.Add(self.txc_rpl, (3, rc_ + 2), *_multi_span_4c)
            gbs.Add(self.btn_rpl, (3, rc_ + 6), *_single_span)

            gbs.Add(self.cbx_cas, (4, rc_ + 2), *_single_span)
            gbs.Add(self.cbx_reg, (4, rc_ + 3), *_single_span)
            gbs.Add(self.cbx_wrd, (4, rc_ + 4), *_single_span)
            gbs.Add(self.cbx_cxt, (5, rc_ + 2), *_single_span)
            gbs.Add(self.cbx_buf, (5, rc_ + 3), *_single_span)
            gbs.Add(self.gge_pgb, (5, rc_ + 4), *_multi_span_2c)
            # gbs.Add(self.gge_pgb, (5, rc_ + 2), *_multi_span_4c)
            gbs.Add(self.btn_can, (5, rc_ + 6), *_single_span)
            # print(f'{self.gge_pgb.Range = }, {self.gge_pgb.Value = }')
        elif mode == 'INC':
            gbs.Add(self.ico_wrp, (1, rc_ - 2), *_static_bitmap)
            gbs.Add(self.ico_isl, (1, rc_ - 1), *_static_bitmap)
            gbs.Add(self.stt_inc, (1, rc_ + 1), *_static_text)
            gbs.Add(self.txc_inc, (1, rc_ + 2), *_multi_span_4c)

            gbs.Add(self.ico_hlm, (2, rc_ - 1), *_static_bitmap)
            gbs.Add(self.cbx_cas, (2, rc_ + 2), *_single_span)
            gbs.Add(self.cbx_reg, (2, rc_ + 3), *_single_span)
            gbs.Add(self.cbx_wrd, (2, rc_ + 4), *_single_span)

            gbs.Add(self.cbx_wrp, (3, rc_ + 2), *_single_span)
            gbs.Add(self.cbx_isl, (3, rc_ + 3), *_single_span)
            gbs.Add(self.cbx_hlm, (3, rc_ + 4), *_single_span)
        elif mode == 'RES':
            # results window takes up all available space
            gbs.AddGrowableCol(0)
            gbs.AddGrowableRow(0)
            # gbs.Add(glb.IBR, (0, rc_ - 5), *_full_span)
            gbs.Add(self.stc_res, (0, rc_ - 5), *_full_span)
        else:
            # we should NEVER get here
            err = f'{self.__class__.__name__}: unknown search mode [{mode}]'
            raise AssertionError(err)

        self.hide_widgets()
        self.show_widgets(mode)

        if mode != 'RES':
            gbs.AddGrowableCol(rc_ + 5)

        # copy text selection to 'find field'
        if self.sec['SelectedTextToFind']:
            if (sel := doc.StringSelection):
                self.txc_fnd.Value = sel

        # select text control contents: Find, Where, Replace, Incremental
        for fld in (self.txc_fnd, self.txc_whr, self.txc_rpl, self.txc_inc):
            dbf.FOCUS(fld)
            fld.SelectAll()

        self.pos_inc = doc.CurrentPos

        # set focus on mode-specific text control
        fld = self.txc_fnd if self.mode != 'INC' else self.txc_inc
        wx.CallAfter(dbf.FOCUS, fld)

        self.SetBackgroundColour(self.sec[f'BackColour{mode}'])
        self.Refresh()  # force

        self.SetSizer(gbs)
        self.Layout()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: gradient background colour
    #     self.Bind(wx.EVT_PAINT, self.on_paint)

    # def on_paint(self, evt):
    #     dc = wx.PaintDC(self)
    #     x, y = self.Size

    #     # rainbow effect in 3 adjoining sections
    #     dc.GradientFillLinear((0,     0, x/3, y), 'RED',   'YELLOW') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)
    #     dc.GradientFillLinear((1*x/3, 0, x/3, y), 'YELLOW', 'GREEN') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)
    #     dc.GradientFillLinear((2*x/3, 0, x/3, y), 'GREEN',   'BLUE') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)

    #     # WHITE -> BLUE effect in 3 adjoining sections
    #     dc.GradientFillLinear((0,     0, x/3, y), 'WHITE',   '#71b3e8') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)
    #     dc.GradientFillLinear((1*x/3, 0, x/3, y), '#71b3e8', '#515cc6') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)
    #     dc.GradientFillLinear((2*x/3, 0, x/3, y), '#515cc6', '#000d84') # , wx.DIRECTION_MASK|wx.RIGHT|wx.TOP)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def textctrl_history(self, evt):
        evt.Skip()

        if (cod := evt.KeyCode) not in SCH_HIS_KEYS:
            return

        fld = evt.EventObject
        # print(fld)
        pos, max_pos = fld.InsertionPoint, fld.LastPosition
        up_, dn_, txt = (cod == wx.WXK_UP), (cod == wx.WXK_DOWN), TXT_NIL

        if up_ or dn_:
            if up_:
                txt, pos = ('Prev   [Up]'), (pos + 1 if pos != max_pos else pos)
                fld.his_idx += 1

                if fld.his_lst and fld.his_idx == len(fld.his_lst):
                    self.set_back_colour('PURPLE', fld)
                    # print('   LAST item: ', end='')
                    fld.his_idx = len(fld.his_lst) - 1
            elif dn_:
                txt, pos = ('Next [Down]'), (pos - 1 if pos != 0 else 0)
                fld.his_idx -= 1

                if fld.his_lst and fld.his_idx == -1:
                    self.set_back_colour('PURPLE', fld)
                    # print('  FIRST item: ', end='')
                    fld.his_idx = 0

            if fld.his_lst:
                fld.Value = val = fld.his_lst[fld.his_idx]
                DBG('SCH', f'{fld.his_idx:3} {val}')

            # wx.CallAfter(fld.SelectAll)
            wx.CallAfter(fld.SetInsertionPoint, fld.LastPosition)
        else:
            print(cod)
            DBG('SCH', '\n  [ENTER] pressed\n')
            # if not exist, add value to history
            if (val := fld.Value) and val not in fld.his_lst:
                fld.his_lst.insert(0, val)
                fld.his_idx = 0
            if DEBUG['SCH']: pprint(fld.his_lst, indent=4, width=10)

        if len(fld.his_lst) > int(glb.SFH['SearchFieldHistory']['MaxItems']):
            del fld.his_lst[-1]  # last item


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
        DBG('SCH', f'{me_("F")}: {txc.Name}')

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
        DBG('SCH', f'{me_("F")}: {txc.Name}')

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
            dbf.FOCUS(last_fld)
        elif id_ == last_fld.Id and _fwd:
            dbf.FOCUS(first_fld)
        else:
            evt.Skip()

    # set focus on 'Find'/'Incremental' text control when button or checkbox clicked
    def transfer_focus(self, evt):
        fld = self.txc_fnd if self.mode != 'INC' else self.txc_inc
        wx.CallAfter(dbf.FOCUS, fld)
        if evt:
            evt.Skip()

    def on_icon_or_checkbox(self, evt):
        """
        Called on icon or checkbox.

        :param      evt:  The event
        :type       evt:  { type_description }
        """
        def __create_xref_mapping(obj):
            """Create input to reference object mapping.

            Create referenced object entries for CheckBox/Icon/Keyboard input.

            Args:
                obj: a CheckBox or Icon (StaticBitmap) event object
            """
            fld_xrf_dct = {}
            pfx_fld, pfx_ref = ('cbx', 'ico') if is_cbx(obj) else ('ico', 'cbx')
            for fld in SCH_FLAGS:
                fld_id_ = getattr(self, f'{pfx_fld}_{(nam := fld.lower())}').Id
                fld_ref = getattr(self, f'{pfx_ref}_{nam}')
                fld_xrf_dct[fld_id_] = (fld, fld_ref)
            return fld_xrf_dct

        id_, obj = evt.Id, evt.EventObject
        nam = obj.Name

        DBG('SCH', f'{me_("F")}: {nam}')

        fld, wgt = __create_xref_mapping(obj)[id_]
        mni = MI[f'SCH_{fld}']

        # sync checkbox, icon and menu item references
        if is_cbx(wgt):
            wgt.Value = not wgt.Value
        self.toggle_icon(fld.lower())
        glb.MBR.Check(mni, not glb.MBR.IsChecked(mni))

        if DEBUG['SCH']:
            if is_cbx(obj):
                chk = 'ON' if obj.IsChecked() else 'off'
                print(f'  {self.__class__.__name__}: {nam:<10s} [ {chk:<3s} ] [{obj.Label}]')

    def toggle_icon(self, fld):
        self.Freeze()
        cbx = getattr(self, f'cbx_{fld}')
        ico = getattr(self, f'ico_{fld}')

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        bmp = PNG[(nam := f'sch_{fld}_24')].Bitmap
        dis_bmp = bmp.ConvertToImage().ConvertToGreyscale().ConvertToDisabled().ConvertToBitmap()

        nam = bmp if cbx.Value else dis_bmp
        ico.SetBitmap(nam)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # nam = f'sch_{fld}_24' if cbx.Value else f'sch_{fld}_unchk_24'
        # ico.SetBitmap(PNG[nam].Bitmap)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.Layout()
        self.Thaw()


# stc.STC_FIND_CXX11REGEX
# stc.STC_FIND_MATCHCASE
# stc.STC_FIND_POSIX
# stc.STC_FIND_REGEXP
# stc.STC_FIND_WHOLEWORD
# stc.STC_FIND_WORDSTART


        # if nam in {'case', 'regex', 'word', 'wrap', 'insel', 'hilite', 'prcase'}:
        #     print(nam)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: private AcceleratorTable for 'SearchPanel'    >>> >>> >>> >>> >>> >>> >>>
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#     def enter_panel(self, evt):
#         evt.Skip()

#         def __accel_handler(evt):
#             # obj = evt.EventObject

#             # sim_key = wx.UIActionSimulator()
#             DBG('SCH', evt.Id)
#             # pprint(dir(evt))
#             DBG('SCH', evt.IsChecked())
#             # for key in {'CRW'}:
#             #     if evt.KeyCode == ord(key):
#             #         print(key)

#             # if evt.KeyCode == ord('C'):
#             #     dbf.FOCUS()

#             # sim_key.KeyDown(evt.KeyCode)

#         DBG('SCH', f'{me_("C, F")}')

# # #FIX, save/set accel table on 'SearchPanel'
#         self.sav_acc_tbl = glb.MBR.acc_tbl
#         glb.TLW.SetAcceleratorTable(wx.NullAcceleratorTable)
#         glb.MBR.SetAcceleratorTable(wx.NullAcceleratorTable)

#         # # acc_ent_lst = []
#         acc_lst =  ('cas', 'reg', 'wrd')

#         for idx, key in enumerate('CRW'):
#             # # acc_ent_lst.append(wx.AcceleratorEntry())

# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#             nam = f'cbx_{acc_lst[idx]}'
# #HACK, boolean walrus logic ;-) as an alternative to:
# #INFO,    1.  obj, id_ = getattr(self, nam), getattr(self, nam).Id

# #INFO,    2.  obj = getattr(self, f'cbx_{acc_lst[idx]}')
# #INFO,        id_ = obj.Id
#             (obj := getattr(self, nam)) and (id_ := obj.Id)
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#             # # print(' ', idx, key, id_, obj.Name)
#             # # acc_ent_lst[idx].Set(wx.ACCEL_ALT, ord(key), id_)
#             obj.Bind(wx.EVT_MENU, __accel_handler, id=id_)
# #TODO, try a 2nd 'wx.Panel' in init ('self' is 1st panel)
#             # self.pnl.Bind(wx.EVT_MENU, __accel_handler, id=id_)

#             accel = wx.AcceleratorTable([(wx.ACCEL_ALT, ord(key), id_)])
#             obj.SetAcceleratorTable(accel)

#         # accel = wx.AcceleratorTable(acc_ent_lst)
#         # self.SetAcceleratorTable(accel)

#     def leave_panel(self, evt):
#         evt.Skip()

#         DBG('SCH', f'{me_("C, F")}')

#         glb.TLW.SetAcceleratorTable(self.sav_acc_tbl)
#         glb.MBR.SetAcceleratorTable(self.sav_acc_tbl)


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
    #     dbf.FOCUS(fld)
    #     evt.Skip()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL:                                               <<< <<< <<< <<< <<< <<< <<<
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def set_back_colour(self, clr=None, fld=None, typ='WARN'):
        if fld is None:
            fld = self.txc_fnd if self.mode != 'INC' else self.txc_inc
        if not clr:
            clr = 'WarningBackColour' if typ == 'WARN' else 'ErrorBackColour'
            clr = self.sec[clr]
        self.tmr_clr.StartOnce(self.sec['DelayDefaultColour'])
        fld.SetBackgroundColour(clr)
        self.Refresh()  # force

    def reset_back_colour(self, evt, clr='WHITE'):
        # discard when not our timer
        if evt.Timer.Id != self.tmr_clr.Id:
            evt.Skip()
            return

        for fld in (self.txc_fnd, self.txc_whr, self.txc_rpl, self.txc_inc):
            fld.SetBackgroundColour(clr)
        self.Refresh()  # force

    @curdoc
    def show_not_found_msg(self, doc, fnd, spos, epos):
        txt = f'Text [{fnd}] not found'
        glb.IBR.info_msg(txt, 'WARN')
        glb.SBR.set_text(txt, typ='WARN')
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

    @curdoc
    def scroll_to_centre(self, doc, fnd):
#FIX, for next/prev find: print 'found at', too
#         self._exec_found(fnd)
        lin = doc.CurrentLine
        # col = doc.GetColumn(doc.CurrentPos)
        half_screen = doc.LinesOnScreen() // 2
        doc.ScrollToLine(lin - half_screen)
        # keep caret on screen vertically:
        # - divisor '30' works fine with differing client widths
        # doc.ScrollToColumn(col - doc.ClientSize.x // 30)
        doc.EnsureCaretVisible()

    @curdoc
    def do_find(self, evt, doc, fnd, flg, prv=False):
        DBG('SCH', f'{me_("F")}: {fnd} {prv=}')
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

        # res = True

        if (fnc := doc.SearchPrev if prv else doc.SearchNext)(flg, fnd) == stc.STC_INVALID_POSITION:
            if self.cbx_wrp.Value:
                # search from top/bottom when not found
                wrp = ('BOTTOM' if prv else 'TOP') if self.cbx_wrp.Value else ''
                txt = f'    => [{fnd}] NOT found (search wrapped to {wrp})'
                DBG('SCH', txt)
                glb.IBR.info_msg(txt, 'INFO')
                glb.SBR.set_text(txt, typ='WARN')
                spos, epos = doc.GetSelection()  # save last selection
                doc.DocumentEnd() if prv else doc.DocumentStart()
                doc.SearchAnchor()
                if fnc(flg, fnd) == stc.STC_INVALID_POSITION:
                    self.show_not_found_msg(doc, fnd, spos, epos)
            else:
                self.show_not_found_msg(doc, fnd, spos, epos)

        self.scroll_to_centre(doc, fnd)

        # back to search panel when visible
        if is_shown('SCH'):
            wx.CallAfter(dbf.FOCUS, fld)

        # DBG('SCH', f'{me_("F")}: {res}')
        # return res

    @curdoc
    def do_count(self, doc, fnd, flg):
        DBG('SCH', f'{me_("F")}: {fnd}')

        cur = cnt = 0
        while (pos := doc.FindText(cur, doc.LastPosition, fnd, flg)) != stc.STC_INVALID_POSITION:
            cur = pos + len(fnd)
            cnt += 1

        txt = f'Found {cnt} occurrences of [{fnd}]'
        DBG('SCH', txt)
        glb.SBR.set_text(txt)
        msg = f'{doc.fnm}\n\n{txt}'
        msg_box(self, 'INFO', msg, extra='Search Count')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, replace 'SearchNext' with already existing 'do_find' functionality
#NOTE, and ... do 'return res' from 'do_find'
#NOTE,     ... and 'scroll_to_centre' could be discarded below
    @curdoc
    def do_replace(self, doc, fnd, rpl, flg):
        if (res := doc.SearchNext(flg, fnd)) == stc.STC_INVALID_POSITION:
            spos = epos = doc.CurrentPos
            self.show_not_found_msg(doc, fnd, spos, epos)
        else:
            doc.ReplaceSelection(rpl)
            doc.SearchAnchor()
            self.scroll_to_centre(doc, fnd)
        return res
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    @curdoc
    def do_find_all(self, doc, fnd, flg):
        DBG('SCH', f'{me_("F")}: {fnd}')

        siz = len(fnd)
        end = doc.LastPosition

        cur = pos = 0
        spos, epos = doc.GetSelection()  # save last selection
        sel_lst = []
        doc.SelectNone()
        doc.SetSelection(pos, pos)

        dbf.TIMER('FND_all')

        # find and select matches
        while (pos := doc.FindText(cur, end, fnd, flg)) != stc.STC_INVALID_POSITION:
#FIX, incorrect results with regex, e.g. '[1-2][cd]'
            anchor, caret = pos, pos + siz
            if not sel_lst:
                doc.SetSelection(anchor, caret)
            else:
                doc.AddSelection(anchor, caret)

            sel_lst.append(pos)
            cur = pos + siz

        dbf.TIMER('FND_all', 'STOP')

        cnt = len(sel_lst)

        if cnt:
            txt = f'Found {cnt} occurrences of [{fnd}]'
            DBG('SCH', txt)
            glb.SBR.set_text(txt)
            msg = f'{doc.fnm}\n\n{txt}'
            msg_box(self, 'INFO', msg, extra='Find All')
        else:
            self.show_not_found_msg(doc, fnd, spos, epos)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @curdoc
    def do_replace_all(self, doc, fnd, rpl, flg):
        DBG('SCH', f'{me_("F")}: {fnd} {rpl}')

        # save caret position and first line and selection
        pos, top = doc.CurrentPos, doc.FirstVisibleLine
        spos, epos = doc.GetSelection()

        cnt = 0  # replace all: occurrences
        doc.DocumentStart()  # replace from top
        doc.SearchAnchor()

        doc.BeginUndoAction()

        dbf.TIMER('RPL_all')

        while (res := self.do_replace(doc, fnd, rpl, flg)) != stc.STC_INVALID_POSITION:
            cnt += 1

        dbf.TIMER('RPL_all', 'STOP')

        if cnt:
            txt = f'Replaced {cnt} occurrences of [{fnd}] with [{rpl}]'
            DBG('SCH', txt)
            glb.SBR.set_text(txt)
            msg = f'{doc.fnm}\n\n{txt}'
            msg_box(self, 'INFO', msg, extra='Replace All')
        else:
            self.show_not_found_msg(doc, fnd, spos, epos)

        doc.EndUndoAction()

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # restore caret's last position and first line
        # doc.GotoPos(pos)
        # doc.SetFirstVisibleLine(top)
        doc.GotoPos(doc.CurrentPos)
        doc.VerticalCentreCaret()
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    @curdoc
    def do_find_in_files(self, fnd, whr):
        def __file_io(fnm):
            cnt = 0
            with open(fnm, 'rb') as fil_obj:
                for num, lin in enumerate(fil_obj.readlines()):
                    cnt += __matches_in_line(fnm, fnd, cnt, num, lin)
                    # keep gui responsive during search
#NOTE, 'YieldIfNeeded' slows performance > 200%
#TODO, implement thread to keep GUI available while searching
                    # wx.YieldIfNeeded()
                    if self.fif_cancelled:
                        DBG('SCH', f'{rs_(25, "*")}\n** Searching cancelled **\n{rs_(25, "*")}')
                        break
            return cnt

#INFO, Python mmap: Improved File I/O With Memory Mapping
#INFO, URL=https://realpython.com/python-mmap/
#INFO, '__mmap_io' not used
        # def __mmap_io(fnm):
        #     cnt = 0
        #     with open(fnm, mode='r', encoding='utf-8') as fil_obj:
        #         try:
        #             with mmap.mmap(fil_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
        #                 for num, lin in enumerate(iter(mmap_obj.readline, b'')):
        #                     cnt += __matches_in_line(fnm, fnd, cnt, num, lin)
        #         except ValueError as e:
        #             # print(f'\nValueError: {fnm}\n  *** {e} ***')
        #             ...
        #     return cnt

        def __matches_in_line(fnm, fnd, cnt, num, lin):
            lin = lin.decode('iso-8859-1').strip('\n')

            # count matches, discard when none found
            if not (occ := len(re.findall(fnd_reg, lin))):
                return occ

            # filename header before 1st match in file
            if not cnt:
#FIX, not used: obsolete path separator conversion?
                txt = fnm  # .replace('/', '\\')
                txt = f'\n  {txt}:'
                DBG('SCH', f'{txt}')
                self.stc_res.AddText(f'{txt}\n')

            # output 1st and possible next matches
            for n in range(occ):
                if not n:
                    txt = f'  {num + 1:5d}: {lin}'
                    DBG('SCH', f'{txt}')
                    # if self.cbx_cxt:
                    #     self.stc_res.AddText(f'  {num:5d}_ {lin}\n')
                    self.stc_res.AddText(f'{txt}\n')
                    # if self.cbx_cxt:
                    #     self.stc_res.AddText(f'  {num + 2:5d}_ {lin}\n')
                    #     self.stc_res.AddText(f'  .....\n')
                # else:
                #     DBG('SCH', f'     >>  {lin}')
                #     self.stc_res.AddText(f'     >>  {lin}\n')

            return occ


# ----- START SEARCH HERE -----

        DBG('SCH==0', f'{me_("F")}: [{fnd}]')

        dbf.TIMER('FIF_find')

        self.fif_cancelled = False  # 'finding files' not cancelled by user

        # self.tmr_pgb.Start(100)
        self.gge_pgb.SetValue(0)
        self.stt_rpl.Label = 'Filename:'
        # self.Layout()

        whr_str = whr
        DBG('SCH==0', f'\n\n1.  WHERE STRING\n  [{whr_str}]')

        whr_str = whr_str.replace(' ', '')
        DBG('SCH==0', f'\n\n2a. REMOVE spaces\n  [{whr_str}]')

        whr_str = whr_str.replace('\\', '/')
        DBG('SCH==0', f'\n\n2b. REPLACE backslash [\\] with slash [/]\n  [{whr_str}]')

        whr_lst = whr_str.split(',')

        if DEBUG['SCH'] == 0:
            print('\n\n3.  SPLIT into elements')
            for whr in whr_lst:
                print(f'  [{whr}]')

        DBG('SCH==0', '\n\n4.  BUILD where string data per element type')

        # remove last run's content
        for val in WHR.values():
            val.lst.clear()

        for whr in whr_lst:
            dsc = '<tag>'

            if PTN.WHR_TAG.reg[0].match(whr):
                WHR.OFD.lst = [whr]
            elif PTN.WHR_TAG.reg[1].match(whr):
                WHR.OFL.lst = [whr]
            elif PTN.WHR_TAG.reg[2].match(whr):
                WHR.CFL.lst = [whr]
            elif PTN.WHR_TAG.reg[3].match(whr):
#FIX, 'BIN' not used -> implement
                WHR.BIN.lst = [whr]
            elif PTN.WHR_TAG.reg[4].match(whr):
                WHR.PVW.lst = [whr]
            elif any(c in whr for c in '<>'):
                WHR.ITG.lst.append(whr)
                dsc = '_INVALID_<tag>'
            elif PTN.WHR_FLT.reg.match(whr):
                itm, pfx = ('INC', '+ In') if not whr.startswith('-') else ('EXC', '- eX')
                WHR[itm].lst.append(whr)
                dsc = f'{pfx}clude'
            elif PTN.WHR_PNM.reg.match(whr):  # and Path(whr).is_dir()
                WHR.PNM.lst.append(whr)
                dsc = 'Path'
            elif PTN.WHR_FNM.reg.match(whr):  # and Path(os.getcwd()+'\\'+whr).is_file()
                WHR.FNM.lst.append(whr)
                dsc = 'File'
            elif whr:
                WHR.DCD.lst.append(whr)
                dsc = '_DISCARD'
            else:
                continue

            # prefix spaces when 1st char not plus/minus
            dsc = f'  {dsc}' if dsc[0] not in '+-' else dsc
            DBG('SCH==0', f'  [ {dsc:16} ] = [{whr}]')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, convert each <tag> placeholder to its respective list of pathname(s)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, for TESTING: for NOW extract dirname from open files ('OFL')
        # <openfolders>
        if WHR.OFD.lst:
            WHR.OFD.lst.clear()
            for __, doc in glb.NBK.open_docs():
                dnm = doc.dnm.replace('\\', '/')
                WHR.OFD.lst.append(dnm)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # <openfiles>
        if WHR.OFL.lst:
            WHR.OFL.lst.clear()
            for __, doc in glb.NBK.open_docs():
                pnm = doc.pnm.replace('\\', '/')
                WHR.OFL.lst.append(pnm)

        # <currentfile>
        if WHR.CFL.lst:
            WHR.CFL.lst = [glb.NBK.CurrentPage.pnm.replace('\\', '/')]  # .txt1.pnm

        # # <binary>
        # if WHR.BIN.lst:
        #     pass

        # # <preview>
        # if WHR.PVW.lst:
        #     pass
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        DBG('SCH==0', '\n\n5a. FULL where string content (element types)')
        DBG('SCH==0', (dbf.SEARCH_WHERE, WHR))

        DBG('SCH==0', '\n\n5b. UNIQUE where string content (element types)')

        # strip '+'/'-' prefix from 'include/exclude' element types
        rm_pfx = lambda pfx, itm: list(e if not e.startswith(pfx) else e[1:] for e in itm)
        WHR.INC.lst = rm_pfx('+', WHR.INC.lst)
        WHR.EXC.lst = rm_pfx('-', WHR.EXC.lst)

        # deduplicate lists
        for val in WHR.values():
            val.lst = list(set(val.lst))

        # remove equal strings from include/exclude' element types
        if (equ_lst := list(set(WHR.INC.lst) & set(WHR.EXC.lst))):
            [WHR.INC.lst.remove(s) for s in equ_lst]
            [WHR.EXC.lst.remove(s) for s in equ_lst]

        DBG('SCH==0', (dbf.SEARCH_WHERE, WHR))

        DBG('SCH', '\n\n6.  VALIDATE pathnames')

        dcd_cnt = len(WHR.DCD.lst)
        for pat in WHR.PNM.lst:
            if not Path(pat).exists():
                dcd_cnt += 1
                DBG('SCH', f'    discard [{pat}]')
                # 'move' from pathnames to discard list
                WHR.PNM.lst.remove(pat)
                WHR.DCD.lst.append(pat)

        DBG('SCH', f'\n  #paths: {dcd_cnt} discarded\n')

        if dcd_cnt:
            txt = 'No valid path(s) specified in [Where:] field, reverting to default: <open files>'
            DBG('SCH', f'\n  {txt}')

#HACK, force header wrap to next line
            txt = txt.replace(',', f',{" "*6}')

            dsc = 'Check discarded item(s) for cause:'
            for idx, itm in enumerate(WHR.DCD.lst):
                dsc += f'\n    {idx + 1}. {itm}'

            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, help examples for 'Where:' field
            hlp_whr = '\n\n'
            for idx in range(10):
                hlp_whr += f'    {idx + 1}.\n'

            msg = f'{txt}\n\n{dsc}\n\n... optional help (examples) ...{hlp_whr}'
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            msg_box(self, 'WARN', msg, extra='Find in Files')
#FIX, no return when [reverting to default: <open files>']
            return

        if DEBUG['SCH']:
            for pat in WHR.PNM.lst:
                print(f'     accept [{pat}]')
            print(f'\n  #paths: {len(WHR.PNM.lst)} accepted')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, use UNIFORM NAMING CONVENTION ('dnm', 'fnm', 'fbs', 'ext') from
#FIX, 'split_path' in 'D:\Dev\D\wx\TSN_SPyE\dev\spye\src\common\file.py'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        DBG('SCH', '\n\n7.  WALK pathnames list, apply filters')
        flt_cnt = 0

        pat_fnm_lst = []  # files, present in specified paths
        sch_fnm_lst = []  # files, to search (filter criteria applied)

        WHR.PNM.lst.extend(WHR.OFD.lst)
        WHR.FNM.lst.extend(WHR.OFL.lst)
        sch_fnm_lst.extend(WHR.CFL.lst)
        # sch_fnm_lst.extend(WHR.FNM.lst)

        inc_reg = re.compile(r'|'.join([fnmatch.translate(x) for x in WHR.INC.lst]))
        exc_reg = re.compile(r'|'.join([fnmatch.translate(x) for x in WHR.EXC.lst]) or r'$.')

#NOTE, prevent circular dependency
        from common.file import is_junction

        for pat in WHR.PNM.lst:

            fnm_lst = []  # files in path, matching filter criteria

#INFO, python - Filtering os.walk() dirs and files - Stack Overflow
#INFO, URL=https://stackoverflow.com/questions/5141437/filtering-os-walk-dirs-and-files

            # pat_fnm_lst = [Path(root, fnm) for root, dirs, files in os.walk(pat) for fnm in files]

            #@@@@@@@@@@@@@@@@@@@@@@@@@@
            # tmp_cnt = 0
            #@@@@@@@@@@@@@@@@@@@@@@@@@@
            for root, __, files in os.walk(pat):

#HACK, detect/discard junction (directory reparse point)
                if resolve_path(root) != Path(root):
                    DBG('SCH', f'\n - junction: {resolve_path(root)}\n{rs_(13, " ")}{Path(root)}\n')
                    continue

                for fnm in files:
                    pat_fnm_lst.append(Path(root, fnm))

                    #@@@@@@@@ NOT USED YET @@@@@@@@@
                    # ext = Path(fnm).suffix[1]
                    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, not used: obsolete path separator conversion?
                    pnm = str(resolve_path(root, fnm)).replace('\\', '/')

                    if exc_reg.match(pnm):
                        DBG('SCH', f' -  exclude: {pnm}')
                        continue
                    elif inc_reg.match(pnm):
                        DBG('SCH', f'+   include: {pnm}')
                        flt_cnt += 1
                        sch_fnm_lst.append(pnm)
                        fnm_lst.append(Path(root, fnm))

            DBG('SCH==0', f'\n  ALL files in path [{pat}]: {len(fnm_lst)}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ FOR TESTING: RETURN EARLY @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if DEBUG['SCH']:
            print(f'\n  #files (filtered): {flt_cnt}')
            print(f'\n{WHR.PVW.lst = }\n{inc_reg = }\n{exc_reg = }\n')
            for f in pat_fnm_lst:
                print(f)
            print(f'\n  ALL files scanned: {len(pat_fnm_lst)}\n')

        # self.gge_pgb.SetValue(100)
        # self.btn_can.Label = 'Finish'
        # dbf.TIMER('FIF_find', 'STOP')

        # return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ FOR TESTING: RETURN EARLY @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # save count of files to search through for later
        sch_cnt = len(sch_fnm_lst)

        sch_fnm_lst = sorted(sch_fnm_lst)
        if DEBUG['SCH']:
            print(f'\n\n8a. File list {(txt := "(FULL, filtered, sorted)")}')
            for fil in sch_fnm_lst:
                print(f'  [{fil}]')
            print(f'\n  #files {txt}: {sch_cnt}')

        sch_fnm_lst = sorted(list(set(sch_fnm_lst)))
        if DEBUG['SCH']:
            print(f'\n\n8b. File list {(txt := "(UNIQUE, filtered, sorted)")}')
            for fil in sch_fnm_lst:
                print(f'  [{fil}]')
            print(f'\n  #files {txt}: {sch_cnt}')

        DBG('SCH', '\n\n8c. PREVIEW only')

        if WHR.PVW.lst:
            txt = ' Preview only'
            msg = f'{txt}\n\n[[[Extra Text]]]\n\n'
            msg_box(self, 'INFO', msg, extra='Find in Files')
            return

        DBG('SCH', '\n\n9.  SEARCH, apply option flags')

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

#INFO, catch regex exception
#INFO, URL=https://docs.python.org/3/library/re.html#re.error
        try:
            fnd_reg = re.compile(rf'{fnd_str}', flg_cas)
        except re.error as e:
            glb.SBR.set_text('Regex error', typ='ERROR')
            self.set_back_colour()
            dbf.FOCUS(self.txc_fnd)

            # self.txc_fnd.SetStyle(10, 11, wx.TextAttr(wx.RED, wx.YELLOW))

            msg = f'Regex error:\n\n{e.msg}\n    at position {e.pos + 1}\n    in pattern "{e.pattern}"'
            DBG('SCH', msg.replace('\n\n', ' ').replace('\n   ', ''))
            msg_box(self, 'ERROR', msg, extra='Regular Expression')
            return

        # dbf.TIMER('FIF_find', 'STOP')
        # dbf.TIMER('FIF_find')

        txt = f'Searching {sch_cnt} files for [{fnd}] {flg_dsc}'
        DBG('SCH', f'\n{txt}')
        self.stc_res.AddText(f'{txt}\n')

        # file count, total matches, progress bar value
        flc = tot = pgb_cnt = 0

        # self.txc_rpl.SetBackgroundColour('GREEN')

        for fil in sch_fnm_lst:
#FIX, current filename needs own proper field or banner message
            self.txc_rpl.Value = fil
            self.txc_rpl.Update()

            #@@@@@@@@@@@@@@@@@@@@@@@
            # if exc_reg.match(fil):
            #     print('excludes')
            #     continue
            #@@@@@@@@@@@@@@@@@@@@@@@

            # #matches in this file
            mch_cnt = __file_io(fil)  # __mmap_io(fil)

            # quit when 'Cancel' button pressed
            if self.fif_cancelled:
                break

            if mch_cnt:
                flc += 1
                tot += mch_cnt

            pgb_cnt += 1
            self.gge_pgb.SetValue(int(pgb_cnt / sch_cnt * 100))

        DBG('SCH')
        dbf.TIMER('FIF_find', 'STOP')

        # search results summary
        can_txt = ' ** CANCELLED **' if self.fif_cancelled else ''
        tot_txt = f'{tot} match ' if tot == 1 else f'{tot} matches '
        tot_txt += f'across {flc} files' if flc > 1 else TXT_NIL if not flc else 'in 1 file'
        ftr_txt = f'\nFinished searching {sch_cnt} files for [{fnd}] {flg_dsc}'
        DBG('SCH', ftr_txt)
        DBG('SCH', f'\n  {tot_txt}\n')
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

            # go to top of search results
            self.stc_res.DocumentStart()
            self.stc_res.mark_matches(ind=4, fnd=fnd)

            # self.stc_res.Thaw()

            wx.CallAfter(dbf.FOCUS, self.stc_res)
        else:
            # no results, back to 'find field'
            self.txc_fnd.SelectAll()
            wx.CallAfter(dbf.FOCUS, self.txc_fnd)

        self.gge_pgb.SetValue(0)
        self.stt_rpl.Label = 'R&eplace:'


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @curdoc
    def do_replace_in_files(self, doc, fnd, rpl, whr, flg):
        not_implemented(None, f'{me_("F")}')
        DBG('SCH', f'{me_("F")}: [{fnd}] [{rpl}] [{whr}]')

        dbf.TIMER('FIF_replace')

        dbf.TIMER('FIF_replace', 'STOP')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# ----- PROCESS RESULTS HERE -----


    def toggle_mouse_active(self, evt, enable=True):
        # disable mouse hover when keyboard active, enable when mouse moved
        self.stc_res.Bind(wx.EVT_MOTION, self.do_result_line if enable else lambda e: self.toggle_mouse_active(e, enable=False))

    def do_result_line(self, evt, kpr_sct=None):
        # hover over line in 'search results'
        def __hover():
            dbf.FOCUS(self.stc_res)

            self.stc_res.SetCaretLineVisible(True)
            self.stc_res.SetSelBackground(True, '#3399FF')
            x, y, pos = get_char_pos(self.stc_res, close=False)

            lnr = self.stc_res.LineFromPosition(pos)
            txt = self.stc_res.GetLineText(lnr)

            fnm_mch = PTN.RES_FNM.reg.search(txt)
            lin_mch = PTN.RES_LIN.reg.search(txt)

            pos = self.stc_res.PositionFromLine(lnr)

            if fnm_mch:
                end, grp = fnm_mch.end(), fnm_mch.group(0)
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
            DBG('SCH', f'{kpr_sct} detected')
            self.toggle_mouse_active(None, enable=False)

            if kpr_sct in {'F4', 'F5'}:
                to = self.stc_res.TextLength
                self.stc_res.LineEnd()
            elif kpr_sct in {'Shift+F4', 'Shift+F5'}:
                to = 0
                self.stc_res.Home()
            else:
                return

            if kpr_sct in {'F4', 'Shift+F4'}:
                self.stc_res.SetSelBackground(True, 'BLUE')
                fnd = r'^ *?[0-9]+:'
            elif kpr_sct in {'F5', 'Shift+F5'}:
                self.stc_res.SetSelBackground(True, 'ORANGE')
                fnd = r'^  [^ 0-9].*:$'

            fr, flg = self.stc_res.CurrentPos, stc.STC_FIND_REGEXP

            if (pos := self.stc_res.FindText(fr, to, fnd, flg)) == stc.STC_INVALID_POSITION:
                if kpr_sct in {'F4', 'F5'}:
                    self.stc_res.Home()
                elif kpr_sct in {'Shift+F4', 'Shift+F5'}:
                    self.stc_res.LineEnd()
                fr = self.stc_res.CurrentPos
                pos = self.stc_res.FindText(fr, to, fnd, flg)
                txt = 'No more results'
                glb.IBR.info_msg(txt, 'WARN')
                # return

            self.stc_res.Home()
            self.stc_res.SetSelection(pos + 2, pos + 8)
            # self.stc_res.VerticalCentreCaret()
            self.stc_res.EnsureCaretVisible()
            if kpr_sct in {'F5', 'Shift+F5'}:
                self.stc_res.SetSelection(pos + 2, pos + self.stc_res.GetLineLength(self.stc_res.CurrentLine))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#                           vvvvvvvvvvvvv
#TODO, add config Section: [SearchResults]
#TODO,  "     "   Options: next/previous found file/line ->  e.g. selected position in 'TOP|CENTRE|VISIBLE|...'
#TODO,  "     "      "   : e.g. add 2 (or 4) key(s) -> (Next|Prev)(File|Line)Pos
#INFO,     e.g. this sets the found file (selected position) -> TOP
#INFO,          self.stc_res.SetFirstVisibleLine(self.stc_res.CurrentLine)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # self.stc_res.GotoPos(pos)

            # # return line number or filename
            # lnr = self.stc_res.LineFromPosition(pos)
            # lnf = self.stc_res.GetLineText(lnr)[:-1]

        # double-click line in 'search results'
        def __select():
            def __reverse_find(typ):
                fr, to, flg = self.stc_res.CurrentPos, 0, stc.STC_FIND_REGEXP
                fnd = r'^ *?[0-9]+:' if typ == 'LIN' else r'^  [^ ].*:$'

                if (pos := self.stc_res.FindText(fr, to, fnd, flg)) == stc.STC_INVALID_POSITION:
                    # we should NEVER get here
                    return ''

                # return line number of filename
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
            DBG('SCH', f'Selected: [{lnr:5}]  [{fnm}]')

            doc.GotoLine(lnr - 1)
            doc.VerticalCentreCaret()

        # 'EVT_' event types handled: wx.EVT_MOTION, stc.EVT_STC_DOUBLECLICK
        try:
            typ = evt.EventType
        except AttributeError as e:
            typ = 'KEYBOARD_USED'

        self.stc_res.SetCaretLineBackground('#C6E2FF')


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


if __name__ == '__main__':

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: module TESTING
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # from const.app import LOC
    # print(LOC['CFG']['FIL'])

    # LOC['CFG']['FIL'] ='D:\\Dev\\D\\wx\\TSN_SPyE\\dev\\spye\\conf\\SPyE.cfg'
    # print(LOC['CFG']['FIL'])

    # from app.startup import startup

    # startup()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    app = wx.App(False)
    frm = wx.Frame(None, size=(850, 200))
    SearchPanel(frm)
    frm.Show()
    app.MainLoop()
