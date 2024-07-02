#!/usr/bin/python

from ctypes import addressof, c_char_p, create_string_buffer
from io import StringIO
from pathlib import Path
from pprint import pprint
import re
import sys

import wx
# import wx.lib.gizmos as gizmos
from wx import stc
from wx.lib.busy import BusyInfo

# from common.file import get_file_status
from common.type import is_str
from common.util import (
    get_char_pos, get_keypress, is_shown, is_word_at, msg_box
)
from conf.debug import DBG, DEBUG, dbf, me_
from conf.lang import Language
from const.app import COMMON_EVENTS, LOC, CLR
from const.common import TXT_NIL
from const.editor import (
    CRLF, NEWLINE, MSL_KEYS, PDB_KEYS, BRF_KEYS, CHARS, DOC_STYLE_HOTSPOT,
    FOL_STYLE, FOLD_MARKER_NUMS, FOLD_MARKER_SYMBOLS, MGN, MRK
)
from const import glb
from const.lang import FACES, LANG, LANG_KWRD, LANG_PROP, LANG_STYL
from const.macro import MAC_CMDS
from const.menubar import MI
from const.sidepanel import SPT
from data.images import catalog as PNG
import gui
import mix
from tool.symbol import SymbolPopup


################################################################
#INFO, copied from wxPython demo file 'DynamicSashWindow.py'
################################################################
# class Editor(gizmos.DynamicSashWindow):
#     def __init__(self, prt, pat_dta=[TXT_NIL * 4]):
#         super().__init__(prt, wx.ID_ANY,
#                          style=0
#                          |gizmos.DS_DRAG_CORNER
#                                     )
#         self = EditorWithDynamicSash(self, pat_dta)
#
#############
#
# def Editor(prt, pat_dta):
#     dyn = gizmos.DynamicSashWindow(prt, wx.ID_ANY, style=0
#                               #| gizmos.DS_MANAGE_SCROLLBARS
#                               | gizmos.DS_DRAG_CORNER
#                               )
#     view = EditorWithDynamicSash(dyn, pat_dta)
#     return dyn, view
################################################################
#INFO, copied from wxPython demo file 'DynamicSashWindow.py'
################################################################


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
WX_VER = float(wx.version()[:3])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# class EditorWithDynamicSash(stc.StyledTextCtrl, mix.Help):
# @dbf.method_calls()
class Editor(stc.StyledTextCtrl, mix.Help):
    """TEST: Help text for Editor"""
    # doc_ptr = None

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # Scintilla 'direct access' class attributes
    edt_fnc = edt_ptr = None
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, OVERRIDE for 'wx.stc.StyledTextCtrl.FindText', see wx docs for:
#NOTE,   ver >= 4.1: 'Return type tuple, Returns (int, findEnd)'
#NOTE,   ver <  4.1: 'Return type int'
    def FindText(self, *args, **kwargs):
        pos = super().FindText(*args, **kwargs)
        return pos[0] if WX_VER >= 4.1 else pos
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # __slots__ = ['CFG',            'cph_active',     'cph_cache_lst',
    #              'cph_idx',        'cph_sbw_active', 'cph_scl_active',
    #              'ctt_active',     'edt_ctx_active', 'cur_sel_wrd',
    #              'dat_acc',        'dat_cre',        'dat_mod',
    #              'chg_detected',   'del_detected',   'dnm',
    #              'dyn_sash',       'fbs',            'ext',
    #              'fnm',        '    fil_szb',        'fil_szk',
    #              'fold_style',     'glance',         'ind_active',
    #              'kwd_lst',        'lexer',          'lng_mni',
    #              'lng_nam',        'lng_typ',        'mac_lst',
    #              'tlw',            'mch_active',     'nbk',
    #              'new_XOffset',    'old_XOffset',    'prt',
    #              'pnm',            'prv_lparam',     'prv_wrd_pos',
    #              'mac_rec_active', 'selected_text',  'spt_lst',
    #              'spu_active',     'state',          'sty_active',
    #              'tmr_cph',        'tmr_ctt',]

    def __init__(self, prt, pat_dta=[TXT_NIL * 4]):
        pnm = str(Path(*pat_dta[0:2]))
        super().__init__(prt, size=wx.DefaultSize, style=wx.BORDER_SUNKEN, name=pnm)
        mix.Help.__init__(self)
        self.SetExtraStyle(wx.WS_EX_PROCESS_UI_UPDATES)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # assign class attributes ONLY once
        if WX_VER >= 4.1 and not (self.edt_fnc and self.edt_ptr):
            # print('Assign')
            Editor.edt_fnc = self.GetDirectFunction()
            Editor.edt_ptr = self.GetDirectPointer()
        # print(self.edt_fnc, self.edt_ptr)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # self.CmdKeyAssign(stc.STC_KEY_TAB, 0, stc.STC_CMD_HOME)

################################################################
#INFO, copied from wxPython demo file 'DynamicSashWindow.py'
################################################################
        # self.dyn_sash = prt
        # self.SetupScrollBars()

        # self.Bind(gizmos.EVT_DYNAMIC_SASH_SPLIT, self.OnSplit)
        # self.Bind(gizmos.EVT_DYNAMIC_SASH_UNIFY, self.OnUnify)
        # #self.SetScrollWidth(500)
################################################################
#INFO, copied from wxPython demo file 'DynamicSashWindow.py'
################################################################

#DONE, 2017-07-04 22:56:21, add list of pat_dta to Editor class (doc object)
        self.dnm, self.fnm, self.fbs, self.ext, self.pnm = *pat_dta, pnm

        self.newline = NEWLINE

        self.prv_kpr_sct = None

        # line number margin clicked to start dragging
        self.mgn_num_active = False

        # last line number in margin while dragging
        self.prv_mgn_drg = -1

#FIX, not used: obsolete?
        # timestamps/size for existing file (having a dnm)
        if self.dnm:
#NOTE, prevent circular dependency
            from common.file import get_file_status
            __, self.dat_mod, __, __, __ = get_file_status(self.pnm)

        # used in 'def AutoInsertXxx'
        self.selected_text = TXT_NIL

        # detect disk file change/delete
        self.chg_detected = False
        self.del_detected = False

        # reference to this doc's 'glance view' (when hovering its page tab)
        self.glc_obj = None

        # side panel tool pointers (multi doc control), empty at doc creation
        # -> each side panel tool is unique for every doc
        self.spt_lst = [None] * len(SPT)

        # caret position history / index / timer / active
        self.cph_cache_lst = []

        self.cph_idx = -1  # cache index
        # self.cph_cache_lst = []
        # self.cph_idx = -1  # cache index
        # timer resets caret style after delay since last activity
        self.tmr_cph = wx.Timer(self, wx.ID_ANY)
        self.cph_active = False  # jumping through history
        self.cph_scl_active = False  # scrolling with scrollbar
        self.cph_sbw_active = False  # symbol browsing in dialog

        # mark matches using style 0 ('True' when double-clicked word)
        self.mch_active = False

        # mark/style tokens using style 1 to 5 ('True' when style selected)
        self.sty_active = {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
        }

        # properties: default state
        self.state = self.dft_docstate()

        # convert indentation active
        self.ind_active = False

        # context menu active
        self.edt_ctx_active = False

        # mouse cursor hover timers (colour tooltip and symbol popup)
        self.tmr_ctt = wx.Timer(self, wx.ID_ANY)
        self.tmr_spu = wx.Timer(self, wx.ID_ANY)
        self.ctt_active = False  # colour tooltip active  # not used
        self.spu_active = False  # symbol popup active

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: _hover_scroll_lines
        # self.prv_hvr_xy = wx.Point(-1, -1)  # last coordinates (_hover_scroll_lines)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.prv_wrd_pos = 0  # last word position (colour tooltip)

        self.cur_sel_wrd = None     # currently selected word

#FIX, global macro recording? set self.mac_lst/recording/lparam globally?
        self.mac_lst = []
        self.mac_rec_active = False
#HACK, prevent double '\n' when recording Enter key
        self.prv_lparam = None

#TODO, add fold_style to 3 docstate methods, FOR NOW it is GLOBAL
        self.fold_style = FOL_STYLE

        # horizontal document scroll offset (for ruler alignment)
        self.old_XOffset = self.new_XOffset = self.XOffset

#         if self.doc_ptr:
#             self.SetDocPointer(self.doc_ptr)
#         else:
#             Editor.doc_ptr = self.DocPointer

#         # default: plain text
#         self.lexer, self.lng_typ, self.lng_nam, __, self.lng_mni = LANG[-1]

#NOTE, for NOW, instead of 'default: plain text'
        # get language based on menu selection
        lng_lst = [m for m in LANG if glb.MBR.IsChecked(m[4])]
        self.update_language_styling(lng_lst)

        self.settings()
        self.binds()

################################################################
#INFO, copied from wxPython demo file 'DynamicSashWindow.py'
################################################################
    # def SetupScrollBars(self):
    #     # hook the scrollbars provided by the wxDynamicSashWindow
    #     # to this view
    #     hsb = self.dyn_sash.GetHScrollBar(self)
    #     vsb = self.dyn_sash.GetVScrollBar(self)
    #     hsb.Bind(wx.EVT_SCROLL, self.OnSBScroll)
    #     vsb.Bind(wx.EVT_SCROLL, self.OnSBScroll)
    #     hsb.Bind(wx.EVT_SET_FOCUS, self.OnSBFocus)
    #     vsb.Bind(wx.EVT_SET_FOCUS, self.OnSBFocus)

    #     # And set the wxStyledText to use these scrollbars instead
    #     # of its built-in ones.
    #     self.SetHScrollBar(hsb)
    #     self.SetVScrollBar(vsb)

    # def OnSplit(self, evt):
    #     newview = EditorWithDynamicSash(self.dyn_sash, pat_dta)
    #     newview.SetDocPointer(self.DocPointer)     # use the same document
    #     self.SetupScrollBars()

    # def OnUnify(self, evt):
    #     self.SetupScrollBars()

    # def OnSBScroll(self, evt):
    #     # redirect the scroll events from the dyn_sash's scrollbars to the STC
    #     self.EventHandler.ProcessEvent(evt)

    # def OnSBFocus(self, evt):
    #     # when the scrollbar gets the focus move it back to the STC
    #     dbf.FOCUS(self)
################################################################
#INFO, END copied from wxPython demo file 'DynamicSashWindow.py'
################################################################

    def settings(self):

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # self.SetXCaretPolicy(stc.STC_CARET_EVEN|stc.STC_CARET_STRICT, 50)
        # self.SetYCaretPolicy(stc.STC_CARET_EVEN|stc.STC_CARET_STRICT, 50)
        # # stc.STC_CARET_EVEN
        # # stc.STC_CARET_JUMPS
        # # stc.STC_CARET_SLOP
        # # stc.STC_CARET_STRICT
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        sec = glb.CFG['Editor']
        self.SetSelEOLFilled(sec['SelectionEOLFilled'])
        self.SetEOLMode(sec['EOLMode'])
#NOTE, either BufferedDraw or Technology cause flicker when False
        self.SetBufferedDraw(sec['BufferedDraw'])
        self.SetTechnology(sec['Technology'])
        self.SetVirtualSpaceOptions(sec['VirtualSpaceOptions'])
        self.SetUseHorizontalScrollBar(sec['HorizontalScrollBar'])
        self.SetUseVerticalScrollBar(sec['VerticalScrollBar'])
        self.SetScrollWidthTracking(sec['ScrollWidthTracking'])
        self.SetEndAtLastLine(sec['EndAtLastLine'])
        self.SetWhitespaceSize(sec['WhitespaceSize'])

        sec = glb.CFG['MultiEdit']
        self.SetMultipleSelection(sec['Selection'])
        self.SetAdditionalSelectionTyping(sec['Typing'])
        # self.SetMultiPaste(sec['MultiPaste'])
        self.SetSelForeground(True, sec['SelForeColour'])
        self.SetSelBackground(True, sec['SelBackColour'])
        self.SetSelAlpha(sec['SelAlpha'])
        self.SetAdditionalSelForeground(sec['ExtraSelForeColour'])
        self.SetAdditionalSelBackground(sec['ExtraSelBackColour'])
        self.SetAdditionalSelAlpha(sec['ExtraSelAlpha'])
        self.SetAdditionalCaretForeground(sec['ExtraCaretForeColour'])
        self.SetAdditionalCaretsBlink(sec['ExtraCaretsBlink'])
        self.SetAdditionalCaretsVisible(sec['ExtraCaretsVisible'])

        sec = glb.CFG['Caret']
        self.SetCaretForeground(sec['ForeColour'])
        self.SetCaretLineVisible(sec['LineVisible'])
        self.SetCaretLineBackground(sec['LineBackColour'])
        self.SetCaretLineBackAlpha(sec['LineBackAlpha'])
        self.SetCaretSticky(sec['Sticky'])
        self.SetCaretPeriod(sec['Period'])
        self.SetCaretStyle(sec['Style'])
        self.SetCaretWidth(sec['Width'])

        self.SetMouseDwellTime(glb.CFG['CallTip']['DelayShow'])

        sec = glb.CFG['Indentation']
        wid = sec['TabWidth']
        self.SetUseTabs(sec['UseTabs'])
        self.SetTabWidth(wid)
        self.SetIndent(wid)  # sec['Size']
        self.SetIndentationGuides(sec['Guides'])
        self.SetHighlightGuide(wid)

        # menu reference, make sure global margin setting is used
        mbr = glb.MBR

        # 5 margins: 0 to 4, width in pixels
        sec = glb.CFG['Margin']
        self.SetMarginType(MGN['NUM'], stc.STC_MARGIN_NUMBER)  # 0: LINE numbers
        self.SetMarginSensitive(MGN['NUM'], True)              # to mouse clicks
        self.SetMarginWidth(MGN['NUM'], sec['LineNumberWidth'] if mbr.IsChecked(MI['MGN_NUM']) else 0)

        self.SetMarginType(MGN['SYM'], stc.STC_MARGIN_SYMBOL)  # 1: BOOKMARKS
        self.SetMarginMask(MGN['SYM'], ~stc.STC_MASK_FOLDERS)  # NO folding bits
        self.SetMarginSensitive(MGN['SYM'], True)              # to mouse clicks
        self.SetMarginWidth(MGN['SYM'], sec['SymbolWidth'] if mbr.IsChecked(MI['MGN_SYM']) else 0)

        self.SetMarginType(MGN['FOL'], stc.STC_MARGIN_SYMBOL)  # 2: FOLDERS
        self.SetMarginMask(MGN['FOL'], stc.STC_MASK_FOLDERS)   # ALL folding bits
        self.SetMarginSensitive(MGN['FOL'], True)              # to mouse clicks
        self.SetMarginWidth(MGN['FOL'], sec['FoldingWidth'] if mbr.IsChecked(MI['MGN_FOL']) else 0)

        self.SetMarginType(MGN['TXT'], stc.STC_MARGIN_TEXT)    # 3: LEFT
        self.SetMarginLeft(sec['LeftWidth'])

        self.SetMarginType(MGN['RTX'], stc.STC_MARGIN_RTEXT)   # 4: RIGHT
        self.SetMarginRight(sec['RightWidth'])

        self.IndicatorSetForeground(1, 'RED')     # 'tab.timmy' uses indicator 1 with INDIC_TT
        # self.IndicatorSetStyle(1, stc.STC_INDIC_TT)

        self.SetFoldMarginColour(True, sec['FoldingColour'])      # STYLE_LINENUMBER back colour
        self.SetFoldMarginHiColour(True, sec['FoldingHiColour'])  # same colour: no chequerboard
        self.MarkerEnableHighlight(sec['FoldingHighlight'])

        sec = glb.CFG['Bookmark']
        fgc, bgc = sec['OuterColour'], sec['InnerColour']
        self.MarkerDefine(MRK['BMK']['NUM'], MRK['BMK']['SYM'], fgc, bgc)

        sec = glb.CFG['Task']
        fgc, bgc = sec['OuterColour'], sec['InnerColour']
        self.MarkerDefine(MRK['TSK']['NUM'], MRK['TSK']['SYM'], fgc, bgc)

        sec = glb.CFG['Breakpoint']
        fgc, bgc = sec['OuterColour'], sec['InnerColour']
        self.MarkerDefine(MRK['BPT']['NUM'], MRK['BPT']['SYM'], fgc, bgc)

        # breakpoint (disabled)
        fgc, bgc = 'BLACK', 'BLACK'
        self.MarkerDefine(MRK['BPD']['NUM'], MRK['BPD']['SYM'], fgc, bgc)

        # matches
        fgc, bgc = 'PURPLE', 'PURPLE'
        self.MarkerDefine(MRK['MCH']['NUM'], MRK['MCH']['SYM'], fgc, bgc)

        # hide lines
        fgc, bgc = 'FOREST GREEN', 'FOREST GREEN'
        self.MarkerDefineBitmap(MRK['HLS']['NUM'], PNG['hidelines_start_16'].Bitmap)
        self.MarkerDefine(MRK['HLU']['NUM'], MRK['HLU']['SYM'], fgc, bgc)
        self.MarkerDefineBitmap(MRK['HLE']['NUM'], PNG['hidelines_end_16'].Bitmap)

        # debugger
        fgc, bgc = 'PURPLE', 'PURPLE'
        self.MarkerDefine(MRK['DBC']['NUM'], MRK['DBC']['SYM'], fgc, bgc)
        fgc, bgc = 'RED', 'RED'
        self.MarkerDefine(MRK['DBE']['NUM'], MRK['DBE']['SYM'], fgc, bgc)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # test: brackets
        for typ, nam in {('BAB', 'angle_both'),  ('BAL', 'angle_left'),  ('BAR', 'angle_right'),
                         ('BCB', 'curly_both'),  ('BCL', 'curly_left'),  ('BCR', 'curly_right'),
                         ('BRB', 'round_both'),  ('BRL', 'round_left'),  ('BRR', 'round_right'),
                         ('BSB', 'square_both'), ('BSL', 'square_left'), ('BSR', 'square_right')}:
            self.MarkerDefineBitmap(MRK[typ]['NUM'], PNG[f'brace_{nam}_16'].Bitmap)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.SetWrapMode(stc.STC_WRAP_NONE)                     # _NONE/_WORD/_CHAR/_WHITESPACE
        self.SetWrapIndentMode(stc.STC_WRAPINDENT_SAME)        # _FIXED/_SAME/_INDENT
        self.SetWrapStartIndent(2)                              # 0/2/4/6/8/...
        self.SetWrapVisualFlags(stc.STC_WRAPVISUALFLAG_MARGIN)  # _NONE/_END/_START/_MARGIN
                                                                # _DEFAULT/_END_BY_TEXT/_START_BY_TEXT
        self.SetWrapVisualFlagsLocation(stc.STC_WRAPVISUALFLAGLOC_DEFAULT)

        # autocomplete: register 'data.images'
        lrg, mdm, sml = (32, 32), (24, 24), (16, 16)
        img_siz = sml
        self.RegisterImage(1, PNG['open_16'].Bitmap)
        self.RegisterImage(2, wx.ArtProvider.GetBitmap(wx.ART_NEW, size=img_siz))
        self.RegisterImage(3, wx.ArtProvider.GetBitmap(wx.ART_COPY, size=img_siz))

        # autocomplete: maxsize
        sec = glb.CFG['AutoComplete']
        self.AutoCompSetMaxHeight(sec['MaxHeight'])
        self.AutoCompSetMaxWidth(sec['MaxWidth'])

        self.UsePopUp(False)  # disable Scintilla context menu handler, use wx 'PopupMenu'

#         self.CmdKeyClearAll()  # drop all default Scintilla key mappings

        # set which document modification events are sent to the container
        self.SetModEventMask(stc.STC_MOD_INSERTTEXT |
                             stc.STC_MOD_DELETETEXT |
                             stc.STC_MOD_BEFOREINSERT |
                             stc.STC_PERFORMED_USER |
                             stc.STC_PERFORMED_UNDO |
                             stc.STC_PERFORMED_REDO |
                             stc.STC_STARTACTION)

###################################################################################################
###################################################################################################
#NOTE, some extra editor options
#         self.AutoCompSetDropRestOfWord(True)
#         self.SetExtraAscent(2)
#         self.SetExtraDescent(2)
#         self.SetPunctuationChars('~}|{`^][@?>=<;:.-,+*)(&%$#')
#         self.SetSelectionMode(stc.STC_SEL_LINES)
#         self.SetWordChars('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
#
#         self.SetEdgeMode(stc.STC_EDGE_LINE)
#         self.SetEdgeColumn(78)

#INFO, URL=http://www.theasciicode.com.ar/extended-ascii-code/paragraph-sign-pilcrow-end-paragraph-mark-ascii-code-244.html
#         self.SetControlCharSymbol(244)  # [char = paragraph mark]
#INFO, URL=https://unicode-table.com/en/2761/
#INFO,     Curved Stem Paragraph Sign Ornament U+2761
#INFO,     Pilcrow Sign U+00B6
###################################################################################################
###################################################################################################

    def binds(self):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, 'EVT_KEY_UP' outputs 1 keypress occurrence, 'EVT_KEY_DOWN' repeats until released
#NOTE, was 'EVT_KEY_DOWN'; now works better with 'ESCAPE' key in 'SearchPanel'
#FIX, EVT_KEY_UP used for 'UseAltKeyAsToggle' -> conflicts with other keys in 'key_pressed'
        # self.Bind(wx.EVT_KEY_UP, self.key_pressed)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.Bind(wx.EVT_CHAR_HOOK, self.key_pressed)

        self.Bind(stc.EVT_STC_CHARADDED, self.auto_complete)
        self.Bind(stc.EVT_STC_CHARADDED, self.auto_insert_braces if glb.CFG['Brace']['AutoInsert'] else None)

        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'EDT'))

        self.Bind(stc.EVT_STC_DOUBLECLICK, self.mark_matches if glb.CFG['Indicator']['Enable'] else None)

        self.Bind(wx.EVT_LEFT_DOWN, self.mark_matches_clear)

#FIX, calltip with dwell NOT WORKING, yet
        self.Bind(stc.EVT_STC_DWELLSTART, self.calltip_start)
        self.Bind(stc.EVT_STC_DWELLEND, self.calltip_end)

        self.Bind(stc.EVT_STC_MACRORECORD, self.macro_record)

        self.Bind(stc.EVT_STC_MARGINCLICK, self.margin_click_line_number)
        self.Bind(wx.EVT_LEFT_UP, self.margin_click_line_number)
        self.Bind(wx.EVT_MOTION, self.margin_click_line_number)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.margin_click_symbol)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.margin_click_folding)

        self.Bind(stc.EVT_STC_MODIFIED, self.auto_insert_get_selection if glb.CFG['Brace']['AutoInsert'] else None)
        # self.Bind(stc.EVT_STC_CHARADDED, self.text_modified)
        self.Bind(stc.EVT_STC_MODIFIED, self.text_modified)

        # override Scintilla default 'Ctrl+wheel zoom'
        self.Bind(wx.EVT_MOUSEWHEEL, self.mouse_wheel)

        self.Bind(stc.EVT_STC_ROMODIFYATTEMPT, self.readonly_changed if glb.CFG['General']['DetectFileReadOnly'] else None)

        self.Bind(stc.EVT_STC_SAVEPOINTLEFT, self.savepoint)
        self.Bind(stc.EVT_STC_SAVEPOINTREACHED, self.savepoint)

        self.Bind(wx.EVT_SCROLLWIN_LINEDOWN, self.scroll)
        self.Bind(wx.EVT_SCROLLWIN_LINEUP, self.scroll)
        self.Bind(wx.EVT_SCROLLWIN_PAGEDOWN, self.scroll)
        self.Bind(wx.EVT_SCROLLWIN_PAGEUP, self.scroll)
        self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.scroll)
        self.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, self.scroll_release)
        self.Bind(wx.EVT_MOUSE_CAPTURE_CHANGED, self.scroll_release)

        self.Bind(wx.EVT_SET_CURSOR, self.colour_tooltip_set_delay)
        self.Bind(wx.EVT_SET_CURSOR, self.symbol_popup_set_delay)

#FIX, hotspot not working
        # self.Bind(stc.EVT_STC_STYLENEEDED, self.StyleHotspot)

        self.Bind(wx.EVT_TIMER, self.reset_caret_style)
        self.Bind(wx.EVT_TIMER, self.show_colour_tooltip)
        self.Bind(wx.EVT_TIMER, self.show_symbol_popup)

        self.Bind(stc.EVT_STC_UPDATEUI, glb.TLW.do_brace_match if glb.CFG['Brace']['Enable'] else None)
        self.Bind(stc.EVT_STC_UPDATEUI, self.pos_changed if glb.CFG['CaretPositionHistory']['Enable'] else None)
        self.Bind(stc.EVT_STC_UPDATEUI, self.set_x_scroll_offset)

        self.Bind(stc.EVT_STC_ZOOM, self.zoom_changed)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: _hover_scroll_lines
#NOTE, EXPERIMENTAL: *** DISABLED ***
        # self.Bind(wx.EVT_MOTION, self._hover_scroll_lines)

    # def _hover_scroll_lines(self, evt):
    #     evt.Skip()
    #     DBG('SCL', f'{me_("F")}')

    #     _gks = wx.GetKeyState
    #     ctrl = _gks(wx.WXK_CONTROL)

    #     if not ctrl:
    #         return

    #     x, y = wx.Point(evt.X, evt.Y)

    #     if wx.Point(x, y) == self.prv_hvr_xy:
    #         return

    #     _fwd = evt.Y > self.prv_hvr_xy.y
    #     cnt = 0
    #     dif = abs(evt.Y - self.prv_hvr_xy.y)

    #     cnt = 1 if dif < 7 else 3 if dif < 14 else 25 if dif < 100 else 1

    #     DBG('SCL', cnt)

    #     self.prv_hvr_xy = wx.Point(x, y)

    #     # print(x, y, self.ClientSize)

    #     # ctrl = _gks(wx.WXK_CONTROL)
    #     # # alt = _gks(wx.WXK_ALT)
    #     # # shift = _gks(wx.WXK_SHIFT)

    #     # if not ctrl:
    #     #     return

    #     # _fwd =  evt.Y > self.ClientSize.y // 2

    #     self.Freeze()
    #     self.ScrollLines(cnt if _fwd else -cnt)
    #     self.Thaw()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, consolidate language/styling process into 1 method/call:
#FIX, see 'update_language_styling', 'update_styling' and 'styling'
    def styling(self, lexer, lng_typ, lng_nam, lng_mni):
        self.lexer    = lexer
        self.lng_typ = lng_typ
        self.lng_nam = lng_nam
        self.lng_mni = lng_mni

        self.SetLexer(self.lexer)

        self.fold_styling()

        # global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 'face:%(helv)s,size:%(size)d' % FACES)
        self.StyleSetBackground(stc.STC_STYLE_DEFAULT, glb.CFG['Editor']['DefaultBackColour'])
        self.StyleClearAll()  # reset all styles to default

        FACES['fore'] = glb.CFG['Margin']['LineNumberForeColour']
        FACES['back'] = glb.CFG['Margin']['LineNumberBackColour']
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, 'fore:%(fore)s,back:%(back)s,face:%(helv)s,size:%(size2)d' % FACES)

        FACES['fore'] = glb.CFG['Brace']['LightForeColour']
        FACES['back'] = glb.CFG['Brace']['LightBackColour']
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, 'fore:%(fore)s,back:%(back)s,bold' % FACES)

        FACES['fore'] = glb.CFG['Brace']['BadForeColour']
        FACES['back'] = glb.CFG['Brace']['BadBackColour']
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, 'fore:%(fore)s,back:%(back)s,bold' % FACES)

        FACES['fore'] = glb.CFG['Indentation']['GuidesForeColour']
        FACES['back'] = glb.CFG['Indentation']['GuidesBackColour']
        self.StyleSetSpec(stc.STC_STYLE_INDENTGUIDE, 'fore:%(fore)s,back:%(back)s,bold' % FACES)

        FACES['fore'] = glb.CFG['CallTip']['ForeColour']
        FACES['back'] = glb.CFG['CallTip']['BackColour']
        self.StyleSetSpec(stc.STC_STYLE_CALLTIP, 'fore:%(fore)s,back:%(back)s,size:%(size3)d' % FACES)
        self.CallTipUseStyle(stc.STC_STYLE_CALLTIP)

        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, 'face:%(other)s' % FACES)

#NOTE, NOT supported in wxPython -> AttributeError
#         self.StyleSetSpec(stc.STC_STYLE_FOLDDISPLAYTEXT, 'fore:RED,back:WHITE,bold')
#         self.StyleSetSpec(39, 'fore:GREEN,back:WHITE,bold')

#FIX, hotspot not working
        # sec = glb.CFG['Hotspot']
        # FACES['fore'] = sec['ForeColour']
        # FACES['back'] = sec['BackColour']
        # self.StyleSetSpec(DOC_STYLE_HOTSPOT, 'fore:%(fore)s,back:%(back)s,bold' % FACES)
        # self.StyleSetHotSpot(DOC_STYLE_HOTSPOT, True)

        # self.SetHotspotActiveBackground(True, sec['ForeColour'])
        # self.SetHotspotActiveForeground(True, sec['BackColour'])
        # self.SetHotspotActiveUnderline(sec['Underline'] )
        # self.SetHotspotSingleLine(sec['SingleLine'])

#TODO, styling per lexer BEGIN

        # lexer keywords for 'auto_complete'
        self.kwd_lst = []
        for lbl, kws, lst in LANG_KWRD[self.lexer]:
            self.SetKeyWords(kws, lst)
            self.kwd_lst += lst.split()
        self.kwd_lst.sort()

        # read styles from 'file.lng'
        lng = Language(LOC['LNG']['FIL'])

        # current language
        cur = [[n[2], n[1], n[0]] for n in LANG if self.lexer == n[0]][0]
        cur = '|'.join(map(str, cur))

        # style code elements for current language
        if cur in lng:
            for elm in lng[cur]:
                __, tok = elm.split('|')
                sty = lng[cur][elm]
                self.StyleSetSpec(int(tok), sty)

#INFO, Scintilla property documentation:
#INFO, URL=http://www.scintilla.org/SciTEDoc.html
        # lexer properties
        for nam, val in LANG_PROP[self.lexer]:
            self.SetProperty(nam, val)
        # print(self.PropertyNames())

#FIX, hotspot not working
        # # find URLs and style as hotspot
        # url_str = """(http|https|ftp|ftps|file)://[-_.()a-zA-Z0-9/:~?#\[\]@!$&*+,;='"%]+"""
        # url_reg = re.compile(url_str)

        # for m in url_reg.finditer(self.Text):
        #     start, end = m.span()
        #     len_ = end - start
        #     txt = self.GetTextRange(start, end)
        #     # self.StartStyling(start, 0x1f)
        #     # self.SetStyling(len_, DOC_STYLE_HOTSPOT)
        #     # print(txt)

#FIX, hotspot not working
    # def StyleHotspot(self, evt):
    #     self.StyleSetSpec(DOC_STYLE_HOTSPOT, 'fore:BLACK,back:RED,bold' % FACES)
    #     self.StyleSetHotSpot(DOC_STYLE_HOTSPOT, True)

    #     self.SetHotspotActiveBackground(True, 'GREEN')
    #     self.SetHotspotActiveForeground(True, 'RED')
    #     self.SetHotspotActiveUnderline(True)
    #     self.SetHotspotSingleLine(True)

    #     # find URLs and style as hotspot
    #     url_str = """(http|https|ftp|ftps|file)://[-_.()a-zA-Z0-9/:~?#\[\]@!$&*+,;='"%]+"""
    #     url_reg = re.compile(url_str)

    #     for m in url_reg.finditer(self.Text):
    #         start, end = m.span()
    #         len_ = end - start
    #         txt = self.GetTextRange(start, end)
    #         self.StartStyling(start, 0x1f)
    #         self.SetStyling(len_, DOC_STYLE_HOTSPOT)
    #         print(txt)

#TODO, styling per lexer END

###################################################################################
# START:copied from \internal D:\Dev\D\wx\TSN_SPyE\contrib\demo\StyledTextCtrl_2.py
###################################################################################

    def fold_all(self):
        cnt = self.LineCount
        expanding = True

        # find out if we are folding or unfolding
        for lin in range(cnt):
            if self.GetFoldLevel(lin) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lin)
                break

        for lin in range(cnt):
            lvl = self.GetFoldLevel(lin)
            if (lvl & stc.STC_FOLDLEVELHEADERFLAG) and \
                    (lvl & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:
                last_child = self.GetLastChild(lin, -1)
                if expanding:
                    self.SetFoldExpanded(lin, True)
                    lin = self.fold_expand(lin, True)
                    lin = last_child
                else:
                    self.SetFoldExpanded(lin, False)
                    if last_child > lin:
                        self.HideLines(lin + 1, last_child)

    def fold_expand(self, lin, expand, force=False, vis_lvl=0, lvl=-1):
        last_child = self.GetLastChild(lin, lvl)
        lin += 1

        while lin <= last_child:
            if force:
                if vis_lvl > 0:
                    self.ShowLines(lin, lin)
                else:
                    self.HideLines(lin, lin)
            else:
                if expand:
                    self.ShowLines(lin, lin)
            if lvl == -1:
                lvl = self.GetFoldLevel(lin)
            if lvl & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if vis_lvl > 1:
                        self.SetFoldExpanded(lin, True)
                    else:
                        self.SetFoldExpanded(lin, False)

                    lin = self.fold_expand(lin, expand, force, vis_lvl - 1)
                else:
                    if expand and self.GetFoldExpanded(lin):
                        lin = self.fold_expand(lin, True, force, vis_lvl - 1)
                    else:
                        lin = self.fold_expand(lin, False, force, vis_lvl - 1)
            else:
                lin += 1

        return lin

    def fold_styling(self):
        lbl = FOLD_MARKER_SYMBOLS[self.fold_style][0]

#TODO, needs better coding... -> fold_style/_marker data in 1 dict
        for idx, num in enumerate(FOLD_MARKER_NUMS, start=1):
            mrk, clr_fg, clr_bg = FOLD_MARKER_SYMBOLS[self.fold_style][idx]
            self.MarkerDeleteAll(num)
            self.MarkerDefine(num, mrk, clr_fg, clr_bg)

#TODO, do not show msg at app startup, create flag for that
        # glb.SBR.set_text('Folding style set to [%s]' % lbl)

        glb.SBR.push_text('Folding style set to [%s]' % lbl)

###################################################################################
# END:  copied from \example  D:\Dev\D\wx\TSN_SPyE\contrib\demo\StyledTextCtrl_2.py
###################################################################################

    def home_end_keys_BRIEF(self, nam, kpr_sct):
        # print(BRF_KEYS)
        txt = '  BRIEF [%-4s] key: %d'
        if kpr_sct in BRF_KEYS:

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, check if at specific pos; e.g. if Home and BOL, goto BOS
            # pos = self.CurrentPos
            # # get Begin/End Of File/Screen/Line positions
            # bol = self.PositionFromLine(self.CurrentLine)
            # eol = bol + self.GetLineLength(self.CurrentLine)
            # bos = self.PositionFromLine(self.FirstVisibleLine)
            # eos = self.PositionFromLine(self.FirstVisibleLine + self.LinesOnScreen() - 1) \
            #       + self.GetLineLength(self.CurrentLine)
            # bof = 0
            # eof = self.LastPosition
            # # print('BOL = %6d    EOL = %6d' % (bol, eol))
            # # print('BOS = %6d    EOS = %6d' % (bos, eos))
            # # print('BOF = %6d    EOF = %6d' % (bof, eof))
            # # print(rs_(28))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, SHORT version => VALIDATE
            # if kpr_sct == 'HOME':
            #     new = bol if pos != bol else bos if pos != bos else bof
            # else:
            #     new = eol if pos != eol else eos if pos != eos else eof
            # self.GotoPos(new)
            # # if new in (bol, bos, bof):
            # #     self.VCHome()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, LONG version => VALIDATE
            # if kpr_sct == 'HOME':
            #     if pos == bol:
            #         if pos != bos:
            #             new = bos
            #         else:
            #             new = bof
            #     else:
            #         new = bol
            # else:
            #     print(kpr_sct, pos, eol, eos, eof)
            #     if pos == eol:
            #         if pos != eos:
            #             new = eos
            #         else:
            #             new = eof
            #     else:
            #         new = eol
            # self.GotoPos(new)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            BRF_KEYS[nam] += 1
            if BRF_KEYS[nam] == 1:
                if kpr_sct == 'HOME':
                    self.Home()
                else:
                    self.LineEnd()
            elif BRF_KEYS[nam] == 2:
                lin = self.FirstVisibleLine
                if kpr_sct == 'END':
                    lin += self.LinesOnScreen() - 1
                self.GotoLine(lin)
            elif BRF_KEYS[nam] == 3:
                if kpr_sct == 'HOME':
                    self.DocumentStart()
                else:
                    self.DocumentEnd()
            if BRF_KEYS[nam] > 3:
                BRF_KEYS[nam] = 1
            if kpr_sct == 'HOME':
                BRF_KEYS['END'] = 0
            else:
                BRF_KEYS['HOME'] = 0
            txt = txt % (nam, BRF_KEYS[nam])
            DBG('KBD', txt)
            glb.SBR.set_text(txt, 'AUX')
        else:
            for nam in BRF_KEYS:
                BRF_KEYS[nam] = 0
                DBG('KBD', txt % (nam, BRF_KEYS[nam]))

#NOTE, copied from PyPE, GetKeyPress
    def key_pressed(self, evt):
#@@@----@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL:
        # move splitter 'spl' sash in direction 'dir_' limited by 'min_' w/ step 'pxl'
        def __move_sash(obj, spl, dir_, min_, pxl=50):
            obj.Freeze()
            if 10 < (pos := spl.SashPosition) < min_:
                pos += (min_ - pos)
            spl.SetSashPosition(pos - pxl if dir_ in kpr_sct else pos + pxl)
            # update 'editor' and 'side panel' (smoother with 'code preview' visible)
            self.Update()
            glb.SPN.Update()
            # sch.Update()
            obj.Thaw()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, revise DEBUG['KBD']
        # DBG('KBD', f'{me_()}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        DBG('KBD>2', (dbf.EVENT, evt))

        evt.Skip()  # let Scintilla process key

        kpr_sct, nam, __ = get_keypress(evt)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, revise DEBUG['KBD']
        # DBG('KBD', f'{me_("F")}: [{nam:>3}] {kpr_sct}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if not kpr_sct:
            return

        # convenience: use locals from GLOBALS
        tlw, cfg, spl, mbr, ibr, sbr, nbk, spn, sch = \
            glb.TLW, glb.CFG, glb.SPL, glb.MBR, glb.IBR, glb.SBR, glb.NBK, glb.SPN, glb.SCH

#@@@----@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL:
        # toggle menubar with single 'Alt' keypress
        if cfg['MenuBar']['UseAltKeyAsToggle'] and evt.EventType == wx.EVT_KEY_UP.typeId:
            # print(f'[{kpr_sct}], [{self.prv_kpr_sct}]')
            # for c in self.prv_kpr_sct:
            #     print(ord(c), end=' ')
            if nam == chr(0) and self.prv_kpr_sct.startswith('Alt+'):
                (dsc, _mb) = ('show', mbr) if not mbr.IsAttached() else ('hide', None)
                DBG('KBD', f'{me_("F")}: {dsc} menubar')
                tlw.toggle_menubar(None)
                evt.Skip(False)  # NO Scintilla key processing
                return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if kpr_sct != self.prv_kpr_sct:
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, revise DEBUG['KBD']
            DBG('KBD', f'{me_("F")}: [{nam:>3}] {kpr_sct}')
#NOTE, use 'ToolBar' 'SearchCtrl' (for TEMP TEST in 'key_pressed')
            glb.TBR.tbt['SCH'].Control.Value = kpr_sct
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            self.prv_kpr_sct = kpr_sct

#TODO, use for snippet mode to jump between fields
        # SNP_KEYS = ('TAB', 'Shift+TAB')
        # if snippet_mode and kpr_sct in SNP_KEYS:
        # ...
        #     return

#@@@----@@@@@
        # handle Python debugger processing
        if kpr_sct in PDB_KEYS:
            cmd = PDB_KEYS[kpr_sct]
            dsc = f'Python debugger command = [{cmd.upper()}]'
            if not tlw.debugger:
                if cmd == 'start':
                    tlw.start_debugger()
            elif cmd == 'quit':
                tlw.stop_debugger()
            # elif cmd not in {'start', 'quit'}:
            #     tlw.debugger.command(cmd)
            DBG('PDB', dsc)

#@@@----@@@@@
#NOTE, workaround: NO native multi caret movement support for Scintilla < 3.6 (wx < 4.1)
        if WX_VER < 4.1:
            # multiple selection/caret movement
            if cfg['MultiEdit']['Selection'] and self.Selections > 1 and kpr_sct in MSL_KEYS:
                self.move_multiselect_carets(kpr_sct)
                evt.Skip(False)  # NO Scintilla key processing
                return

#@@@----@@@@@
        # remove all selections, marks and search panel
        if kpr_sct == 'ESCAPE':
            if self.AutoCompActive():
                self.AutoCompCancel()
                return
            if not tlw.sch_esc_active:
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # set multiple selections to just 1 OR (if <= 1) to none at all
                if self.Selections > 1:
                    anchor, caret = self.GetSelectionNAnchor(0), self.GetSelectionNCaret(0)
                else:
                    anchor = caret = self.GetSelectionNAnchor(0)
                self.SelectNone()
                self.SetSelection(anchor, caret)
                self.VerticalCentreCaret()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                self.mark_matches_clear(evt)
                ibr.dismiss(None)
            if not is_shown('SCH'):
                return
            # switch from 'RES' to 'FIF' search mode
            if tlw.sch_res_active:
                tlw.sch_res_active = False
                sch.Freeze()
                sch.set_mode('FIF')
                # unsplit/split to force default 'FIF' sash position
                tlw.reset_panel('SCH', -1)
                sch.Thaw()
                evt.Skip(False)  # NO Scintilla key processing
                return
            # hide search panel
            tlw.sch_esc_active = False
            tlw.toggle_panel(None, 'SCH', -1)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, 'slide into view' effect (hide), see 'def set_search_mode'
            sec = cfg['PanelEffect']
            chc, dur = sec['Choice'], sec['Duration']
            sch.HideWithEffect(chc if spl['SCH'].swap else chc, dur)
            # tlw.Freeze()
            # nbk.Freeze()
            # sch.Hide()
            # tlw.Thaw()
            # nbk.Thaw()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@----@@@@@
        # BRIEF editor multi-stroke keys
        if mbr.IsChecked(MI['CRT_BRF']):
            self.home_end_keys_BRIEF(nam, kpr_sct)

#@@@----@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL:
        # move 'side panel' OR 'search results' sash w/ keyboard
        if any(c in kpr_sct for c in ('Alt+LEFT', 'Alt+RIGHT')):
            pxl = 400 if 'Ctrl' in kpr_sct else 50
            __move_sash(spn, spl['SPN'], 'LEFT', 100, pxl=pxl)

        if is_shown('RES'):
            if any(c in kpr_sct for c in ('Alt+UP', 'Alt+DOWN')):
                pxl = 200 if 'Ctrl' in kpr_sct else 50
                __move_sash(sch, spl['SCH'], 'UP', 275, pxl=pxl)
            # go to next/previous line/file in 'search results'
            elif kpr_sct in {'F4', 'Shift+F4', 'F5', 'Shift+F5'}:
                sch.do_result_line(None, kpr_sct)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@----@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if kpr_sct == 'ESCAPE':
        #     sbr.set_text(TXT_NIL)
        # if kpr_sct in 'PAGEUP':
        #     self.StutteredPageUp() ; self.PageDown()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def macro_record(self, evt):
        # discard when not recording
        if not self.mac_rec_active:
            return

        msg, wparam, lparam = evt.Message, evt.WParam, evt.LParam
        cvt = False  # ctypes char pointer -> string?

        if msg == 2170:
            pos = self.CurrentPos
            lparam = self.GetTextRange(pos - 1, pos)
        else:
            if msg in [2001, 2003, 2282, 2367, 2368]:
                lparam = c_char_p(lparam).value
                cvt = True

#HACK, prevent double '\n' when recording Enter key
        if lparam == '\n' and lparam == self.prv_lparam:
            self.prv_lparam = None
            return

        mac = (msg, wparam, lparam, cvt)
        self.mac_lst.append(mac)

        print(f'[{len(self.mac_lst):>3}]: {mac} -> {MAC_CMDS[msg]}')

        glb.SBR.set_text(f'Recording step {len(self.mac_lst)}')
        self.prv_lparam = lparam

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: click line number margin ('goto_line')
#DONE, enable click/drag to select lines (Sublime emulation)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def margin_click_line_number(self, evt):
        evt.Skip()
        DBG('GEN', f'{me_()}')
        DBG('EVT>1', (dbf.EVENT, evt))

        if evt.EventType == stc.EVT_STC_MARGINCLICK.typeId:
            if evt.Margin != MGN['NUM']:
                self.mgn_num_active = False
                return

            self.mgn_num_active = True
            if not self.HasCapture():
                self.CaptureMouse()

            DBG('GEN', 'Line Number margin clicked')

            lin = self.LineFromPosition(evt.Position)
            pos = self.PositionFromLine(lin)
            self.GotoPos(pos)
            # eol = 2 if CRLF in self.GetLine(lin) else 1
            # self.SetSelection(pos, pos + self.GetLineLength(lin) + eol)
        elif evt.EventType == wx.EVT_LEFT_UP.typeId:
            if self.HasCapture():
                self.ReleaseMouse()
            return
        # EVT_MOTION
        else:
            # discard when not dragging
            if not (evt.Dragging() and evt.LeftIsDown() and self.mgn_num_active):
                return

            DBG('GEN', '  dragging')

            lin = self.LineFromPosition(self.PositionFromPoint(evt.Position))
            if lin != self.prv_mgn_drg:
                _fwd = True if lin > self.prv_mgn_drg else False
                glb.TLW.select_line(_fwd=_fwd)

        self.prv_mgn_drg = lin
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def margin_click_symbol(self, evt):
        evt.Skip()
        DBG('BMK', f'{me_()}')
        DBG('EVT>1', (dbf.EVENT, evt))

        if evt.Margin != MGN['SYM']:
            return

        lin = self.LineFromPosition(evt.Position)
        msk = self.MarkerGet(lin)
        if DEBUG['BMK'] or DEBUG['BPT']:
            print(f'  Ctrl Alt Shift = {evt.Control} {evt.Alt} {evt.Shift}')
            print(f'  Pos Line       = {evt.Position} {lin + 1}')
            print(f'  bitmask        = {msk}')

        # show lines when hidden lines marker clicked
        if msk & MRK['HLS']['MSK'] or msk & MRK['HLE']['MSK']:
            if msk & MRK['HLS']['MSK']:
                nxt = self.MarkerNext(lin, MRK['HLE']['MSK'])
                self.MarkerDelete(lin, MRK['HLS']['NUM'])
                self.MarkerDelete(lin, MRK['HLU']['NUM'])
                self.MarkerDelete(nxt, MRK['HLE']['NUM'])
                self.ShowLines(lin, nxt)
            else:
                prv = self.MarkerPrevious(lin, MRK['HLS']['MSK'])
                self.MarkerDelete(prv, MRK['HLS']['NUM'])
                self.MarkerDelete(prv, MRK['HLU']['NUM'])
                self.MarkerDelete(lin, MRK['HLE']['NUM'])
                self.ShowLines(prv, lin)
            return

        # set marker type
        typ, dsc = ('BPT', 'Breakpoint') if evt.Control else ('BMK', 'Bookmark')

        # no breakpoint at blank/comment line
        if typ == 'BPT' and not self.is_valid_breakpoint(lin):
            return

#TODO, integrate with 'toggle_bookmark'/'toggle_breakpoint'
        # force bookmark/breakpoint list control creation
        glb.SPN.SetSelection(SPT[typ].idx)

        # marker = 1

        if msk & MRK[typ]['MSK']:

            # for i in range(10):
            #     if 2**i == msk:
            #         marker = i
            #         break
            # self.MarkerDelete(lin, marker)

            self.MarkerDelete(lin, MRK[typ]['NUM'])
            glb.SBR.set_text(f'{dsc} deleted from {lin + 1}')
        else:
            self.MarkerAdd(lin, MRK[typ]['NUM'])
            glb.SBR.set_text(f'{dsc} added to {lin + 1}')

            # self.MarginSetStyleOffset(2)
            # self.MarginSetStyle(lin, stc.STC_STYLE_LINENUMBER)
            # print('[%s]' % self.MarginGetText(lin))
            # self.MarginSetText(lin, 'XYZ')
            # print('[%s]' % self.MarginGetText(lin))

#TODO, integrate with 'toggle_bookmark'/'toggle_breakpoint'
        # update bookmark/breakpoint list control
        gui.get_spt(typ).update(self)

        # DBG('BMK', '  %14s = %s' % ('MARK', marker))

    def margin_click_folding(self, evt):
        evt.Skip()
        DBG('GEN', f'{me_()}')
        DBG('EVT>1', (dbf.EVENT, evt))

        if evt.Margin != MGN['FOL']:
            return

        # fold and unfold as needed
        if evt.Shift and evt.Control:
            self.fold_all()
        else:
            clk_lin = self.LineFromPosition(evt.Position)  # clicked line
            if self.GetFoldLevel(clk_lin) & stc.STC_FOLDLEVELHEADERFLAG:
                if evt.Shift:
                    self.SetFoldExpanded(clk_lin, True)
                    self.fold_expand(clk_lin, True, True, 1)
                elif evt.Control:
                    if self.GetFoldExpanded(clk_lin):
                        self.SetFoldExpanded(clk_lin, False)
                        self.fold_expand(clk_lin, False, True, 0)
                    else:
                        self.SetFoldExpanded(clk_lin, True)
                        self.fold_expand(clk_lin, True, True, 100)
                else:
                    self.ToggleFold(clk_lin)

    def mouse_wheel(self, evt):
#HACK, temporarily disable top line tooltip when 'wheeling'
        glb.NBK.tlt.EnableTip(False)
        wx.CallAfter(glb.NBK.tlt.EnableTip, bool(glb.MBR.IsChecked(MI['LAY_TLT'])))

        # discard when this is search results
        if self.Name == 'stcResults':
            return

        _rot = evt.WheelRotation  # is multiple of 120 (+/- delta)
        _fwd = bool(_rot < 0)
        _dir = 'forward' if _fwd else 'backward'
        _arg = (f'Scrolling {_dir}', self, CLR['BLUE2'], 'BLUE')

        ctrl, alt, shift = evt.controlDown, evt.altDown, evt.shiftDown

        # zoom in/out
        if ctrl and alt:
            self.SetZoom(self.Zoom - 1 if _fwd else self.Zoom + 1)
            dlg = show_busy(None, *_arg)
            wx.CallLater(250, del_busy, dlg)
            return

        # scroll horizontally: left/right
        if ctrl and shift:
            self.LineScroll(4 if _fwd else -4, 0)
            return

        self.Freeze()

        # scroll vertically: forward/backward
        if ctrl:
            dlg = show_busy('half page', *_arg)
            hpg = self.LinesOnScreen() // 2
            self.ScrollLines(hpg if _fwd else -hpg)
        elif alt:
            dlg = show_busy('10 lines', *_arg)
            self.ScrollLines(10 if _fwd else -10)
        elif shift:
            dlg = show_busy('1 page', *_arg)
            self.ScrollPages(1 if _fwd else -1)
        else:
            dlg = show_busy('3 lines', *_arg)
            self.ScrollLines(3 if _fwd else -3)


        self.Thaw()

        wx.YieldIfNeeded()
        wx.CallLater(250, del_busy, dlg)
        wx.CallLater(glb.CFG['TopLineToolTip']['DelayHide'], glb.NBK.tlt.DoHideNow)

    def pos_changed(self, evt):
        evt.Skip()
        DBG('GEN', f'{me_()}')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, use Begin/EndUndoAction during selection creation (for cph_cache_lst)
#INFO, Updated = 2: 'Selection may have been changed'
#INFO, URL=https://www.scintilla.org/ScintillaDoc.html#SCN_UPDATEUI
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         spos, epos = self.GetSelection()
#         if spos != epos:
#             print(f'{self.GetSelection()}: {evt.Updated}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # discard when jumping, scrolling, symbol browsing, symbol popup
        if any(getattr(self, a) for a in {'cph_active', 'cph_scl_active', 'cph_sbw_active', 'spu_active'}):
            return

        # update caret position history
        pos = self.CurrentPos
        self.cph_idx += 1

        self.cph_cache_lst.insert(self.cph_idx, self.GetSelection())
        DBG('CPH', (dbf.POSITION_HISTORY, self, 'pos_changed'))

        if self.cph_idx < len(self.cph_cache_lst) - 1:
            self.cph_cache_lst = self.cph_cache_lst[:self.cph_idx + 1]
            DBG('CPH', (dbf.POSITION_HISTORY, self, '    Cut MID'))

        mxi = glb.CFG['CaretPositionHistory']['MaxItems']
        if len(self.cph_cache_lst) > mxi:
            self.cph_cache_lst = self.cph_cache_lst[-mxi:]
            DBG('CPH', (dbf.POSITION_HISTORY, self, '    Cut MAX'))
            self.cph_idx -= 1

#FIX, speed up searching with 'search_find_previous/Next'
        # when selection is (not) a word, mark (or clear) all matches
        if glb.CFG['Indicator']['MatchSelection']:
            # caret used, NOT double-clicked word
            if not self.mch_active:
                if is_word_at(self, pos):
                    self.mark_matches(evt)
                else:
                    self.mark_matches_clear(evt)

    def readonly_changed(self, evt):
        DBG('GEN', f'{me_()}')
        msg = f'{self.fnm} is Read-only'
        msg_box(self, 'WARN', msg)

#FIX, not used: obsolete?
    def savepoint(self, evt):
        ...
        # if evt.EventType == stc.EVT_STC_SAVEPOINTLEFT.typeId:
        #     print(evt.EventType, 'Savepoint left')
        # else:
        #     print(evt.EventType, 'Savepoint reached')

    def scroll(self, evt):
        evt.Skip()

        # discard when this is search results
        if self.Name == 'stcResults':
            return

        DBG('GEN', f'{me_()}')
        DBG('GEN>1', (dbf.EVENT, evt))

        self.cph_scl_active = True

        top = self.FirstVisibleLine
        los = self.LinesOnScreen()
        lct = self.LineCount
        typ = evt.EventType

        # adjust top line per scroll event type
        if typ == wx.EVT_SCROLLWIN_LINEDOWN.typeId:
            if top < lct - los:
                top += 1
        elif typ == wx.EVT_SCROLLWIN_LINEUP.typeId:
            if top > 0:
                top -= 1
        elif typ == wx.EVT_SCROLLWIN_PAGEDOWN.typeId:
            top += los - 1
            if top + 1 > lct - los:
                top = lct - los
        elif typ == wx.EVT_SCROLLWIN_PAGEUP.typeId:
            top -= los - 1
            if top < 0:
                top = 0
        elif typ == wx.EVT_SCROLLWIN_THUMBTRACK.typeId:
            # use vertical scrollbar thumb track position
            if evt.Orientation == wx.VERTICAL:
                top = evt.Position

        # get document's visible left column
        col = int(self.XOffset / self.TextWidth(stc.STC_STYLE_DEFAULT, 'X') + 1)

        # update ruler alignment
        self.set_x_scroll_offset()

        # update top line tooltip
        glb.NBK.tlt.update(evt, self, top, col)

    def scroll_release(self, evt):
#FIX, 'auto_insert_get_selection' and 'text_modified' impact each other
#FIX, both use event 'stc.EVT_STC_MODIFIED'
        evt.Skip()
        DBG('GEN', f'{me_()}')
        DBG('GEN>1', (dbf.EVENT, evt))
        # update ruler alignment
        self.set_x_scroll_offset()
        self.cph_scl_active = False
        wx.CallLater(glb.CFG['TopLineToolTip']['DelayHide'], glb.NBK.tlt.DoHideNow)

    def text_modified(self, evt):
        evt.Skip()
        DBG('GEN', f'{me_()}')

#HACK, regain focus when 'STC_MOD_CHANGE' condition below is True
        dbf.FOCUS(self)

        # discard STC change notification (modification event) when:
        # -> style changed OR indicator added/removed (e.g. 'mark_matches')
        if (mod := evt.ModificationType) & (stc.STC_MOD_CHANGESTYLE | stc.STC_MOD_CHANGEINDICATOR):
            return

        # discard when search results active or converting indentation
        if glb.TLW.sch_res_active or self.ind_active:
            return

        glb.NBK.update_page_tab(self)

        DBG('SME', (dbf.MOD_TYPE, evt, self))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # self.BeginUndoAction()
        # self.AddUndoAction(self.LineFromPosition(evt.Position), stc.STC_UNDO_MAY_COALESCE)
        # self.EndUndoAction()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # mod = evt.ModificationType

        # if mod & stc.STC_MOD_BEFOREINSERT or mod & stc.STC_MOD_BEFOREDELETE:
        #     print(self.LineFromPosition(evt.Position))
        # if mod & stc.STC_MOD_INSERTTEXT or mod & stc.STC_MOD_DELETETEXT:
        #     print(self.LineFromPosition(evt.Position + evt.Length))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # mod = evt.ModificationType
        # if mod & stc.STC_MOD_BEFOREINSERT or mod & stc.STC_MOD_BEFOREDELETE:
        #     lin = self.LineFromPosition(evt.Position + evt.Length)
        #     print(lin)
        #     global LIN_B4_MOD
        #     LIN_B4_MOD = lin
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # update bookmark/breakpoint list controls
        for typ in 'BMK', 'BPT':
            if (ctl := gui.get_spt(typ)):
                ctl.update(self)

        # # update doc map panel/control
        # if (ctl := gui.get_spt('DCM')):
        #     ctl.Refresh()  # force 'doc map' update

    def zoom_changed(self, evt):
        if DEBUG['ZOO']:
            z, x, w, h = self.Zoom, self.XOffset, self.TextWidth(stc.STC_STYLE_DEFAULT, 'X'), self.TextHeight(0)
            print('z=%3d, x=%3d, w=%2d, h=%2d  (%s)' % (z, x, w, h, self.fnm))

        rlr = glb.RLR

        # update ruler font size
        # rlr.fnt_siz = 10 + self.Zoom
        # rlr.fnt_siz = self.TextWidth(stc.STC_STYLE_DEFAULT, 'X')

        # update ruler character width
        rlr.chr_wid = self.TextWidth(stc.STC_STYLE_DEFAULT, 'X')
        rlr.Refresh()

        # print(self.TextWidth(stc.STC_STYLE_DEFAULT, 'X'))

        # same zoom level in all documents
        self.Bind(stc.EVT_STC_ZOOM, None)
        for __, doc in glb.NBK.open_docs():
            doc.Zoom = self.Zoom
#NOTE, CallAfter prevents infinite zoom handler loop
        wx.CallAfter(self.Bind, stc.EVT_STC_ZOOM, self.zoom_changed)

        # update doc map (zone)
        if (ctl := gui.get_spt('DCM')):
            ctl.Refresh()

    def auto_complete(self, evt):
        evt.Skip()
        if not glb.CFG['AutoComplete']['Enable']:
            return

        DBG('ACP', f'{me_()}')
        DBG('ACP>1', (dbf.EVENT, evt))
        # find word start
        cur = self.CurrentPos
        start = self.WordStartPosition(cur, True)
        len_ = cur - start
        if not len_:
            return
        # filter on typed chars
        typed_chars = self.GetTextRange(start, cur)
        DBG('ACP', 'Typed chars:', typed_chars)
#TODO, styling per lexer keywords
        acp_lst = []
        for kwd in self.kwd_lst:
            if kwd.startswith(typed_chars):
#NOTE, '?2' is RegisterImage img#
                acp_lst.append(kwd + '?2')
        acp_lst = ' '.join(acp_lst)
        # show filtered autocompletion list
        self.AutoCompShow(len_, acp_lst)

    def auto_insert_get_selection(self, evt):
#FIX, skip event DEGRADES 'double-click word' 'mark_matches' performance
#FIX, but without skip 'text_modified' does NOT execute
        evt.Skip()
        DBG('GEN', f'{me_()}')
#HACK, this modification type indicates text was selected, so grab it before deletion
        mod = stc.STC_STARTACTION | stc.STC_MOD_DELETETEXT | stc.STC_PERFORMED_USER
        if evt.ModificationType == mod:
            self.selected_text = evt.Text

    def auto_insert_braces(self, evt):
        evt.Skip()
#INFO, URL=https://github.com/jacobslusser/ScintillaNET/wiki/Character-Autocompletion
        DBG('AIB', f'{me_()}')
        DBG('AIB>1', (dbf.EVENT, evt))

        # get opening brace
        cur = self.CurrentPos
        opc = chr(self.GetCharAt(cur - 1))
        prs = glb.CFG['Brace']['Pairs']
        mid = len(prs) // 2  # distance between open/close brace

        # typed opening brace?
        if opc in prs[:mid]:
            # get closing brace
            clc = prs[prs.index(opc) + mid]
            # prepend selection
            txt = self.selected_text
            if (len_ := len(txt)):
                clc = txt + clc
            # insert closing brace
            self.InsertText(cur, clc)
            # restore selection
            if len_:
                self.SetSelection(cur, cur + len_)

        self.selected_text = TXT_NIL

#FIX, calltip with dwell not working
    def calltip_start(self, evt):
#@@@@@@@@@@@@@@@@@@@
        # evt.Skip()
#@@@@@@@@@@@@@@@@@@@
        if not glb.CFG['CallTip']['Enable']:
            return

        # discard calltip when symbol popup or context menu active
        if self.spu_active or self.edt_ctx_active:
            return

        try:
            pos = evt.Position
        except AttributeError as e:
            pos = self.CurrentPos

        lin = self.LineFromPosition(pos)
        wrd = self.get_word_under_cursor(pos)[0]

        DBG('CTP', f'{me_()}  [{pos=}]  [{self.fnm=}]')
        DBG('CTP>1', (dbf.EVENT, evt))
        DBG('CTP', f' ***[{lin=}]  [{wrd=}]\n')

        if not wrd:
            return

        # print(f'{self.pnm                = }')
        # print(f'{glb.NBK.CurrentPage.pnm = }')
        # print(f'{self.CallTipActive()        = }')

#HACK, current document only
                                    # .txt1
        if self != glb.NBK.CurrentPage or self.CallTipActive() or pos == stc.STC_INVALID_POSITION:
            return

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, Python: Assign print output to a variable
#INFO, URL=https://stackoverflow.com/questions/5884517/python-assign-print-output-to-a-variable
        # get calltip text, now only handles Python source code
        old_stdout = sys.stdout
        sys.stdout = res = StringIO()
        help(wrd)
        txt = res.getvalue()
        sys.stdout = old_stdout

        if 'No Python documentation found' in txt:
            return

        txt = f'\x011 of 5\x02{txt}'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # self.CallTipSetForeground('RED')
        # self.CallTipSetForegroundHighlight('RED')
        self.CallTipSetHighlight(0, 10)
        self.CallTipShow(pos, txt)

#FIX, calltip with dwell not working
    def calltip_end(self, evt):
        pos = evt.Position

        DBG('CTP', f'{me_()}    [{pos=}]  [{self.fnm=}]')
        DBG('CTP>1', (dbf.EVENT, evt))

#HACK, current document only
                                    # .txt1
        if self != glb.NBK.CurrentPage or self.CallTipActive() or pos == stc.STC_INVALID_POSITION:
            return

        # print(f'{self.pnm                = }')
        # print(f'{glb.NBK.CurrentPage.pnm = }')
        # print(f'{self.CallTipActive()        = }')

        self.CallTipCancel()

    def mark_matches(self, evt=None, ind=0, fnd=''):
        # discard when symbol popup active
        if self.spu_active:
            return

        # if evt:
        #     evt.Skip()
        DBG('IND', f'{me_()}')

        if not is_shown('RES'):
            # discard when search panel active
            if is_shown('SCH'):
                return
            # discard when no selection
            if not (sel_txt := self.SelectedText):
                return
        elif fnd:
            sel_txt = fnd
        else:
            return

        sch = glb.SCH

        if ind == 0 and not is_shown('RES'):
            if COMMON_EVENTS[evt.EventType] == 'STC_DOUBLECLICK':  # 10231
                self.mch_active = True
        else:
            self.sty_active[ind] = True

        dbf.TIMER('mark_mch')

        self.SetIndicatorCurrent(ind)
        self.IndicatorSetForeground(ind, glb.CFG['Indicator'][f'BackColour{ind}'])

        sel_siz = len(sel_txt)
        sel_start = self.SelectionStart
        max_pos = self.LastPosition

        DBG('IND', f'  [{sel_txt   = }]\n  [{sel_siz   = }]\n  [{sel_start = }]\n  [{max_pos   = }]')

#NOTE, new in version 4.1
#         self.IndicatorSetHoverForeground(ind, 'PURPLE')
        self.IndicatorSetOutlineAlpha(ind, glb.CFG['Indicator']['OutlineAlpha'])
        self.IndicatorSetAlpha(ind, glb.CFG['Indicator']['Alpha'])
        self.IndicatorSetStyle(ind, glb.CFG['Indicator']['Style'])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, add 'TokenStyle' to config (stc.STC_INDIC_ROUNDBOX)
        if ind > 0 and not is_shown('RES'):
            self.IndicatorSetStyle(ind, glb.CFG['Indicator']['Style'] + 2)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.IndicatorSetUnder(ind, glb.CFG['Indicator']['DrawUnder'])
        self.IndicatorClearRange(0, max_pos)

        cnt = cur = pos = 0
        flg = sch.get_flags()
        lct = self.LineCount
        fil_reg = re.compile(r'^  [^ ].*:$')  # filename pattern in 'search results'
        sel_lst = []
        # find and mark matches
        while (pos := self.FindText(cur, max_pos, sel_txt, flg)) != stc.STC_INVALID_POSITION:
            DBG('IND', f'        [{pos = }]')

            lin = self.LineFromPosition(pos)

            # no indicator in 'search results'
            if is_shown('RES'):
                # in header/footer
                if lin < 3 or lin > lct - 3:
                    cur = self.PositionFromLine(lin) + self.GetLineLength(lin)
                    continue
                # in left margin (where 'filename:'/'line number:' starts)
                elif 0 <= pos - self.PositionFromLine(lin) < 9:
                    cur = self.PositionFromLine(lin) + 9
                    continue
                # in 'filename:' string
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, a binary file seems to loop forever, think: CRLF?
                elif fil_reg.search(self.GetLineText(lin)):
                    print(f'[{lin}, {fil_reg.search(self.GetLineText(lin)).span()!r:15}], {self.GetLineText(lin)}')
                    cur = self.PositionFromLine(lin) + self.GetLineLength(lin)
                    continue
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            # skip double-clicked word
            if ind == 0 and pos == sel_start:
                cur = pos + sel_siz
                cnt += 1
                continue

            self.IndicatorFillRange(pos, sel_siz)
            sel_lst.append(pos)
            cur = pos + sel_siz

            # no marker in 'search results'
            if not is_shown('RES'):
                # test: add match marker
                self.MarkerAdd(lin, MRK['MCH']['NUM'])

        cnt += len(sel_lst)

        DBG('IND', f'  [{cnt       = }]\n  [{sel_lst   = }]')

        dbf.TIMER('mark_mch', 'STOP')

        glb.SBR.set_text(f'Found {cnt} occurrences of [{sel_txt}]')
        sch.txc_fnd.Value = sel_txt  # save last find string

    def mark_matches_clear(self, evt, ind=0):
        if evt:
            evt.Skip()
        DBG('IND', f'{me_()}')

        if ind == 0:
            self.mch_active = False
        else:
            self.sty_active[ind] = False

        max_pos = self.LastPosition
        self.SetIndicatorCurrent(ind)
        self.IndicatorClearRange(0, max_pos)

        # test: delete match markers
        self.MarkerDeleteAll(MRK['MCH']['NUM'])

        glb.NBK.tlt.DoHideNow()

        self.cur_sel_wrd = None

#         wx.Shell(command='dir /b')
#         wx.Execute(command='dir', flags=wx.EXEC_SYNC, callback=wx.Process(), env=None)

###########################################################################################
#TODO, maybe change stc native recording by pynput => real editable keystroke names ##
###########################################################################################
# class Macro
#     def __init__(self, prt):
#         self.mac_lst = []
#         self.mac_rec_active = False

    def macro_start(self, evt):
        self.mac_rec_active = True
        self.StartRecord()

        self.mac_lst = []
        txt = 'Recording macro'
        DBG('MAC', txt)

    def macro_stop(self, evt):
        self.mac_rec_active = False
        self.StopRecord()

        DBG('MAC', 'Stop recording (%s steps)' % len(self.mac_lst))

#FIX, global macro recording? if not stop record at page change
        if evt:
            cnt = len(self.mac_lst)
            if not cnt:
                glb.SBR.set_text('Empty recording', typ='ERROR')
            else:
                glb.SBR.set_text('Recorded %s macro steps' % cnt, typ='WARN')

        if DEBUG['MAC']:
            if self.mac_lst:
                pprint(self.macro_build_function_source_code())

    def macro_TEST(self, evt):
        DBG('MAC', 'TEST macro message table...')

#INFO, Scintilla command messages that need param(s)
# self.AddText('AddText')                    # (string text)
# self.AddTextRaw('AddTextRaw', 20)          # (string text, int length)
# self.InsertText(40, 'InsertText')          # (position pos, string text)
# self.GotoLine(33)                          # (int line)
# self.GotoPos(333)                          # (position caret)
# self.ReplaceSelection('ReplaceSelection')  # (string text)
# self.AppendText('AppendText')              # (string text)
# self.AppendTextRaw('AppendTextRaw', 20)    # (string text, int length)
# self.SearchAnchor()
# self.SearchNext(1, 'SearchNext')           # (int searchFlags, string text)
# self.SearchPrev(1, 'SearchPrev')           # (int searchFlags, string text)
# self.SetSelectionMode(3)                   # (int selectionMode)

        # import collections
        # mcm = collections.OrderedDict(sorted(MAC_CMDS.items()))

        # for cmd in mcm:
        #     if mcm[cmd] in {'SearchNext', 'SearchPrev'}: continue  # skip: missing WParam, LParam here
        #     print('%d: %s' % (cmd, mcm[cmd]))
        #     self.SendMsg(cmd, wp=0, lp=0)

        DBG('MAC', self.macro_to_source(), '\nEnd TEST')

    def macro_play(self, evt):
        DBG('MAC', 'Playing macro...')
        self.BeginUndoAction()

        print(self.macro_to_source())
        # exec(self.macro_to_source())
#TODO??
        for cmd in self.mac_lst:
            msg, wparam, lparam, cvt = cmd
            if msg == 2170:
                self.ReplaceSelection(lparam)
            else:
                # string -> ctypes char pointer (memory address)
                if cvt:
                    lparam = addressof(create_string_buffer(lparam))
                self.SendMsg(msg, wparam, lparam)
            DBG('MAC', '  [{}] [{}] [{}]'.format(msg, wparam, lparam if not '\n' else '\\n'))

        self.EndUndoAction()
        DBG('MAC', self.macro_to_source(), '\nEnd play')

    def macro_build_function_source_code(self):
        if not self.mac_lst:
            return

        # get STC command identifiers
        cmd_lst = []
        pfx = 'STC_CMD_'
        for cmd in dir(stc):
            if cmd.startswith(pfx):
                cmd_lst.append(cmd.replace(pfx, TXT_NIL))
#         print(cmd_lst)
        # cmd_lst = [c.replace('STC_CMD_', TXT_NIL) for c in cmd_lst]

        # get STC command values from command identifiers
        val_lst = [getattr(stc, f'{pfx}{c}') for c in cmd_lst]
#         print(val_lst)

        # get STC command names from command values used in macro
        nam_lst = []
        for mac in self.mac_lst:
            if mac[0] in val_lst:
                nam_lst.append(cmd_lst[val_lst.index(mac[0])])
#         print(nam_lst)

        # get STC function names from command names for which attribute exists
        fnc_lst = []
        stc_dct = stc.StyledTextCtrl.__dict__
        for nam in nam_lst:
            for att in stc_dct:
                if nam == att.upper():
                    fnc_lst.append(att)
                    break
#         print(fnc_lst)

################################################################
################################################################

        # build source code (macro function) from function names
        src_lst = []
        pfx = 'doc'  # editor doc object
        for fnc in fnc_lst:
            src_lst.append(f'    {pfx}.{fnc}()\n')
        src_lst.append('    print("Executed")')    #TEST
        src_lst.insert(0, f'def macro({pfx}):\n')

        # src_txt = ''
        # for f in fnc_lst:
            # src_txt += '    ctrl.%s()\n' % f
        # src_txt += '    print(\'Executed\')'    #TEST
        # src_txt = f'def macro(ctrl):\n{src_txt}'

        return src_lst

#         glb.NBK.CurrentPage.SetText(src_txt)
#         glb.NBK.CurrentPage.FindLexer('py')
#         code = compile(src_txt, self.__module__, 'exec')
#         exec code in self.__dict__ # Inject new code into this namespace

################################################################
################################################################

#NOTE, copied from PyPE. translate msg to cmd name
    def macro_to_source(self):
        mcm = MAC_CMDS
        # z = ['def macro(self):']
        src_lst = []
        for cmd in self.mac_lst:
            msg, wparam, lparam, cvt = cmd
            if cvt:
                lparam = c_char_p(lparam)
            if msg in mcm:
                if msg in [2001, 2003, 2282, 2367, 2368]:
                    src_lst.append(f'doc.{mcm[msg]}({wparam!r}, {lparam!r})')
                else:
                    src_lst.append('doc.%s()' % mcm[msg])
            elif not msg:
                src_lst.append(f'    self.{lparam}({wparam})')
            elif is_str(msg):
                if not lparam:
                    src_lst.append('    self.root.keyboardShortcut(%r)' % msg)
                else:
                    src_lst.append(f'    #the following shouldn\'t happen: {cmd!r}')
                    src_lst.append('    root.Dent(None, %d)' % lparam)
            elif msg == 2170:
                if is_str(lparam):
                    src_lst.append('    self.ReplaceSelection(%r)' % lparam)
                else:
                    src_lst.append(f'    #this event shouldn\'t happen: {cmd!r}')
            else:
                src_lst.append(f'    #this event shouldn\'t happen: {cmd!r}')
        return '\n'.join(src_lst)

#FIX, consolidate language/styling process into 1 method/call:
#FIX, see 'update_language_styling', 'update_styling' and 'styling'
    def update_language_styling(self, lng_lst=None):
        # print('caller:', sys._getframe(1).f_code.co_name)
        # print('      :', lng_lst, '\n')

        DBG('GEN', f'{me_()}')
#TODO, styling BEGIN
        self.lexer   = lng_lst[0][0]
        self.lng_typ = lng_lst[0][1]
        self.lng_nam = lng_lst[0][2]
        self.lng_mni = lng_lst[0][4]
        self.styling(self.lexer, self.lng_typ, self.lng_nam, self.lng_mni)
        dbf.FILE(f'      {lng_lst  = }')

        # style doc map / code preview
        if (ctl := gui.get_spt('DCM')):
            ctl.styling(self.lexer, self.lng_typ, self.lng_nam, self.lng_mni)
            if ctl.cod_pvw:
                ctl.cod_pvw.stc_pvw.styling(self.lexer, self.lng_typ, self.lng_nam, self.lng_mni)
#TODO, styling END

#FIX, add 'Indentation Guides', 'Caret Line' to 'docstate' or GLOBAL?
#FIX, review other options per doc/GLOBAL
#TODO, add fold_style to 3 docstate methods, FOR NOW it is GLOBAL
#NOTE, margins are GLOBAL now (commented)
    def dft_docstate(self):
        mbr = glb.MBR
        sec = glb.CFG['Margin']

        num = sec['LineNumber']
        sym = sec['Symbol']
        fol = sec['Folding']
        docstate = {
            MI['DOC_WRP']: self.WrapMode,
            MI['DOC_EOL']: self.ViewEOL,
            MI['DOC_WSP']: self.ViewWhiteSpace,
            MI['DOC_LCK']: self.ReadOnly,
            # MI['MGN_ALL']: all([num, sym, fol]),
            # MI['MGN_NUM']: num,
            # MI['MGN_SYM']: sym,
            # MI['MGN_FOL']: fol,
            MI['EDG_NON']: mbr.IsChecked(MI['EDG_NON']),
            MI['EDG_BCK']: mbr.IsChecked(MI['EDG_BCK']),
            MI['EDG_LIN']: mbr.IsChecked(MI['EDG_LIN']),
            # MI['IND_IUS']: mbr.IsChecked(MI['IND_IUS']),
            # MI['IND_TW1']: mbr.IsChecked(MI['IND_TW1']),
            # MI['IND_TW2']: mbr.IsChecked(MI['IND_TW2']),
            # MI['IND_TW3']: mbr.IsChecked(MI['IND_TW3']),
            # MI['IND_TW4']: mbr.IsChecked(MI['IND_TW4']),
            # MI['IND_TW5']: mbr.IsChecked(MI['IND_TW5']),
            # MI['IND_TW6']: mbr.IsChecked(MI['IND_TW6']),
            # MI['IND_TW7']: mbr.IsChecked(MI['IND_TW7']),
            # MI['IND_TW8']: mbr.IsChecked(MI['IND_TW8']),
        }
        dbf.DOCSTATE(self.fnm, docstate)
        return docstate

    def get_docstate(self):
        mbr = glb.MBR

        num = mbr.IsChecked(MI['MGN_NUM'])
        sym = mbr.IsChecked(MI['MGN_SYM'])
        fol = mbr.IsChecked(MI['MGN_FOL'])
        docstate = {
            MI['DOC_WRP']: mbr.IsChecked(MI['DOC_WRP']),
            MI['DOC_EOL']: mbr.IsChecked(MI['DOC_EOL']),
            MI['DOC_WSP']: mbr.IsChecked(MI['DOC_WSP']),
            MI['DOC_LCK']: mbr.IsChecked(MI['DOC_LCK']),
            # MI['MGN_ALL']: all([num, sym, fol]),
            # MI['MGN_NUM']: num,
            # MI['MGN_SYM']: sym,
            # MI['MGN_FOL']: fol,
            MI['EDG_NON']: mbr.IsChecked(MI['EDG_NON']),
            MI['EDG_BCK']: mbr.IsChecked(MI['EDG_BCK']),
            MI['EDG_LIN']: mbr.IsChecked(MI['EDG_LIN']),
            # MI['IND_IUS']: mbr.IsChecked(MI['IND_IUS']),
            # MI['IND_TW1']: mbr.IsChecked(MI['IND_TW1']),
            # MI['IND_TW2']: mbr.IsChecked(MI['IND_TW2']),
            # MI['IND_TW3']: mbr.IsChecked(MI['IND_TW3']),
            # MI['IND_TW4']: mbr.IsChecked(MI['IND_TW4']),
            # MI['IND_TW5']: mbr.IsChecked(MI['IND_TW5']),
            # MI['IND_TW6']: mbr.IsChecked(MI['IND_TW6']),
            # MI['IND_TW7']: mbr.IsChecked(MI['IND_TW7']),
            # MI['IND_TW8']: mbr.IsChecked(MI['IND_TW8']),
        }
        dbf.DOCSTATE(self.fnm, docstate)
        return docstate

    def set_docstate(self):
        mbr = glb.MBR

        mbr.Check(MI['DOC_WRP'], self.state[MI['DOC_WRP']])
        mbr.Check(MI['DOC_EOL'], self.state[MI['DOC_EOL']])
        mbr.Check(MI['DOC_WSP'], self.state[MI['DOC_WSP']])
        mbr.Check(MI['DOC_LCK'], self.state[MI['DOC_LCK']])
        # mbr.Check(MI['MGN_ALL'], self.state[MI['MGN_ALL']])
        # mbr.Check(MI['MGN_NUM'], self.state[MI['MGN_NUM']])
        # mbr.Check(MI['MGN_SYM'], self.state[MI['MGN_SYM']])
        # mbr.Check(MI['MGN_FOL'], self.state[MI['MGN_FOL']])
        mbr.Check(MI['EDG_NON'], self.state[MI['EDG_NON']])
        mbr.Check(MI['EDG_BCK'], self.state[MI['EDG_BCK']])
        mbr.Check(MI['EDG_LIN'], self.state[MI['EDG_LIN']])
        # mbr.Check(MI['IND_IUS'], self.state[MI['IND_IUS']])
        # mbr.Check(MI['IND_TW1'], self.state[MI['IND_TW1']])
        # mbr.Check(MI['IND_TW2'], self.state[MI['IND_TW2']])
        # mbr.Check(MI['IND_TW3'], self.state[MI['IND_TW3']])
        # mbr.Check(MI['IND_TW4'], self.state[MI['IND_TW4']])
        # mbr.Check(MI['IND_TW5'], self.state[MI['IND_TW5']])
        # mbr.Check(MI['IND_TW6'], self.state[MI['IND_TW6']])
        # mbr.Check(MI['IND_TW7'], self.state[MI['IND_TW7']])
        # mbr.Check(MI['IND_TW8'], self.state[MI['IND_TW8']])
        docstate = self.state
        dbf.DOCSTATE(self.fnm, docstate)
        return docstate

    def get_bookmarks(self):
        DBG('STK', (dbf.whoami))
        bmk_lst = []
        bmn = 1
        lin = 0

        while lin != stc.STC_INVALID_POSITION:
            lin = self.MarkerNext(lin, MRK['BMK']['MSK'])
            if lin != stc.STC_INVALID_POSITION:
#TODO, bookmark column, source
                bmk_lst.append((bmn, lin + 1))
                bmn += 1
                lin += 1

#         bmk_lst = list(enumerate(bmk_lst, start=1))
        DBG('BMK', '*** Get:', bmk_lst)
        return bmk_lst

    def set_bookmarks(self, bmk_lst=None):
        DBG('STK', (dbf.whoami))

        for bmk in bmk_lst:
            bmn = bmk[0]  # not used
            lin = bmk[1]
#TODO, bookmark column, source
            src = self.GetLine(lin - 1).strip()
#             bco = bmk[2]
#             src = bmk[3]
            self.MarkerAdd(lin - 1, MRK['BMK']['NUM'])

        if (ctl := gui.get_spt('BMK')):
            ctl.update(self)

        DBG('BMK', '*** Set:', bmk_lst)
        return bmk_lst

    def delete_all_bookmarks(self):
        DBG('STK', (dbf.whoami))
        self.MarkerDeleteAll(MRK['BMK']['NUM'])
        if (ctl := gui.get_spt('BMK')):
            ctl.DeleteAllItems()

    def get_breakpoints(self):
        DBG('STK', (dbf.whoami))

#DONE, enabled: always 'Yes', find way to store its value when disabled ('No')
        # save disabled bp lines
        lin_lst = []
        if (ctl := gui.get_spt('BPT')):
            for idx in range(ctl.ItemCount):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                if (ena := ctl.GetItemText(idx, 2)) == 'No':  # 3rd column: enabled flag
                    lin = int(ctl.GetItemText(idx, 3))        # 4th column: source line
                    lin_lst.append(lin)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        bpt_lst = []
        bpn = 1
        lin = 0

        while lin != stc.STC_INVALID_POSITION:
            lin = self.MarkerNext(lin, MRK['BPT']['MSK'])
            if lin != stc.STC_INVALID_POSITION:
                ena = 'Yes'  # enabled (default)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                if lin + 1 in lin_lst:
                # if bpn in lin_lst:
                    ena = 'No'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                bpt_lst.append((bpn, ena, lin + 1))
                bpn += 1
                lin += 1

#         bpt_lst = list(enumerate(bpt_lst, start=1))
        DBG('BPT', '*** Get:', bpt_lst)
        return bpt_lst

    def set_breakpoints(self, bpt_lst=None):
        DBG('STK', (dbf.whoami))

        for bpt in bpt_lst:
            bpn = bpt[0]  # not used
            ena = bpt[1]
            lin = bpt[2]
            self.MarkerAdd(lin - 1, MRK['BPT']['NUM'])
            if ena == 'No':
                self.MarkerAdd(lin - 1, MRK['BPD']['NUM'])

        if (ctl := gui.get_spt('BPT')):
#FIX, hack: used ONLY AT STARTUP, might integrate with 'update'
            # (ctl := gui.get_spt('BPT')).update(self)
            ctl.update_hack(self, bpt_lst)

        DBG('BPT', '*** Set:', bpt_lst)
        return

    def delete_all_breakpoints(self):
        DBG('STK', (dbf.whoami))
        self.MarkerDeleteAll(MRK['BPT']['NUM'])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.MarkerDeleteAll(MRK['BPD']['NUM'])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if (ctl := gui.get_spt('BPT')):
            ctl.DeleteAllItems()


    def is_valid_breakpoint(self, lin):
        src = self.GetLine(lin).strip()
        if not src or src[0] == '#' or src[:3] in ['"""', "'''"]:
            txt = 'Invalid breakpoint: blank or comment line'
            glb.IBR.info_msg(txt, 'WARN')
            glb.SBR.set_text(txt, typ='WARN')
            return False
        return True

    def get_task_markers(self):
        DBG('STK', (dbf.whoami))
        tsk_lst = []
        tsk = 1
        lin = 0

        while lin != stc.STC_INVALID_POSITION:
            lin = self.MarkerNext(lin, MRK['TSK']['MSK'])
            if lin != stc.STC_INVALID_POSITION:
#TODO, bookmark column, source
                tsk_lst.append((tsk, lin + 1))
                tsk += 1
                lin += 1

#         tsk_lst = list(enumerate(tsk_lst, start=1))
        DBG('TSK', '*** Get:', tsk_lst)
        return tsk_lst

    def delete_all_task_markers(self):
        DBG('STK', (dbf.whoami))
        self.MarkerDeleteAll(MRK['TSK']['NUM'])

    def show_colour_tooltip(self, evt):
        # discard when not our timer
        if evt.Timer.Id != self.tmr_ctt.Id:
            evt.Skip()
            return

        sec = glb.CFG['ColourToolTip']

        if not sec['Enable']:
            return

        x, y, pos = get_char_pos(self)

        # use chars for hex colour word and reset to default
        self.SetWordChars(CHARS['HEX'])
        wrd, start, end = self.get_word_under_cursor(pos)
        self.SetCharsDefault()

        if start == self.prv_wrd_pos:
            return

        self.prv_wrd_pos = start

        glb.NBK.ctt.DoHideNow()

#NOTE, maybe change to regex = "^(#[A-Fa-f0-9]{6})$"
        # hex word format must be '#RRGGBB'
        if not (len(wrd) == 7 and wrd.startswith('#')):
            # now try and find colour by name
            # use chars for colour name and reset to default
            self.SetWordChars(CHARS['CLR'])
            wrd, start, end = self.get_word_under_cursor(pos)
            nam = wrd.lstrip()
            # add leading space count to word start
            pfx_spc = len(wrd) - len(nam)
            start += pfx_spc
            nam = nam.rstrip()
            self.SetCharsDefault()

            # find colour code by name
            clrdb = wx.ColourDatabase()
            clr = clrdb.Find(nam)

            if not clr.IsOk():
                return

            # convert colour components: list -> int (discard transparency)
            r, g, b, __ = clr
            # prepare for hex display
            wrd = f'#{r:02X}{g:02X}{b:02X}'
        else:
            # convert colour components: hex -> int
            r, g, b = (int(f'0x{wrd[i:i + 2]}', 16) for i in (1, 3, 5))

            # find colour name by code
            clrdb = wx.ColourDatabase()
            nam = clrdb.FindName((r, g, b))
            if not nam:
                nam = '<Unknown>'

        self.ctt_active = True


        # use colour under cursor
#         dc = wx.ClientDC(self)
#         dc.SetPen(wx.Pen(sec['RectLineColour'], sec['RectLineWidth']))
#         dc.SetBrush(wx.Brush(wx.Colour(r, g, b)))

#         # adjust popup position at client edge
#         w, h, cw, ch = sec['Width'], sec['Height'], *self.ClientSize
#         if x + w >= cw:
#             x -= w
#         if y + h >= ch:
#             y -= h

#         # draw popup rectangle at cursor position
#         rct = wx.Rect(x, y, w, h)
#         if sec['RectRounded']:
#             dc.DrawRoundedRectangle(rct, sec['RectRoundedRadius'])
#         else:
#             dc.DrawRectangle(rct)


        # RGB colour: hex (#RRGGBB), name and dec (RRR/GGG/BBB)
        hex_ = wrd if sec['ShowHex'] else TXT_NIL
        nam = nam if sec['ShowName'] else TXT_NIL
        dec = f'{r}/{g}/{b}' if sec['ShowDec'] else TXT_NIL

        txt = f'\n{hex_:^20}\n\n{nam:^20}\n\n{dec:^20}\n'
        bgc = wx.Colour(r, g, b)
        pos = self.ClientToScreen(self.PointFromPosition(start))
        pos[1] += 20  # position tooltip under colour

        # update colour tooltip
        glb.NBK.ctt.update(txt, bgc, pos)

        self.ctt_active = False

    def show_symbol_popup(self, evt):
        # discard when not our timer
        if evt.Timer.Id != self.tmr_spu.Id:
            evt.Skip()
            return

        # discard when symbol index or popup disabled
        if not (glb.CFG['SymbolIndex']['Enable'] and glb.CFG['SymbolPopup']['Enable']):
            return

        _gks = wx.GetKeyState
        ctrl, alt, shift = _gks(wx.WXK_CONTROL), _gks(wx.WXK_ALT), _gks(wx.WXK_SHIFT)

        # discard when 'Ctrl' key needed...
        if glb.CFG['SymbolPopup']['NeedCtrlKey']:
            if not ctrl:  # and NOT pressed
                return
            elif alt or shift:  # AND pressed, WITH 'Alt' and/or 'Shift' key(s)
                return

        # discard when symbol popup or context menu active
        if self.spu_active or self.edt_ctx_active:
            return

        __, __, pos = get_char_pos(self)

        # discard when in comment for this lexer
        for elm in LANG_STYL[self.lexer]:
            if any(e in elm[0].lower() for e in {'comment', 'triple'}) and elm[1] == self.GetStyleAt(pos):
                return

        wrd, start, end = self.get_word_under_cursor(pos)

        # discard when not a word
        if not wrd:
            return

        # # discard when no index
        # if not glb.CFG['SymbolIndex']['Enable']:
        #     return

        # discard when word not in any index
        app = glb.APP
        if not any(wrd in w for w in [app.dfn_idx, app.ref_idx, app.imp_idx, app.var_idx, app.wrd_idx, app.qts_idx]):
            return

        # does word have a '(' suffixed, i.e. is it a callable object (class, function)
        if glb.CFG['SymbolPopup']['CallablesOnly']:
            wrd_sfx = chr(self.GetCharAt(end))
            if wrd_sfx not in '(':
                return

        # current word location (lin, col)
        cwl = (self.LineFromPosition(start) + 1, self.GetColumn(start) + 1)

        SymbolPopup(self, wrd, cwl, wx.POPUP_WINDOW)

    def get_word_under_cursor(self, pos):
        start = self.WordStartPosition(pos, True)
        end = self.WordEndPosition(pos, True)
        wrd = self.GetTextRange(start, end)
        return (wrd, start, end)

    def colour_tooltip_set_delay(self, evt):
        evt.Skip()
        self.tmr_ctt.StartOnce(glb.CFG['ColourToolTip']['DelayShow'])

    def symbol_popup_set_delay(self, evt):
        evt.Skip()
        self.tmr_spu.StartOnce(glb.CFG['SymbolPopup']['DelayShow'])

    def selection_to_line(self):
        # used for sorting, start/end line/position
        sel_txt = slin = elin = spos = epos = None
        sel = self.GetSelection()
        if sel:
            slin = self.LineFromPosition(sel[0])
            elin = self.LineFromPosition(sel[1])
            spos = self.PositionFromLine(slin)
            epos = self.GetLineEndPosition(elin)
            self.SetSelection(spos, epos)
            sel_txt = self.SelectedText
        return sel_txt, slin, elin, spos, epos

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def move_multiselect_carets(self, key):
        cnt = self.Selections
        # print('#selections:', cnt, 'MAIN:', self.MainSelection)

#@@@@@@@@@@@@@@@@@@@@@@
        self.Freeze()
#@@@@@@@@@@@@@@@@@@@@@@

#TODO, extend line based multiple selection
        # if key in {'UP', 'Shift+UP'}:
        #     fnc = self.LineUpExtend
        # elif key in {'DOWN', 'Shift+DOWN'}:
        #     fnc = self.LineDownExtend
        # elif key in {'LEFT', 'Shift+LEFT'}:

        if key in {'LEFT', 'Shift+LEFT'}:
            fnc = self.CharLeftExtend
        elif key in {'RIGHT', 'Shift+RIGHT'}:
            fnc = self.CharRightExtend
        elif key in {'HOME', 'Shift+HOME'}:
            fnc = self.VCHomeExtend
        elif key in {'END', 'Shift+END'}:
            fnc = self.LineEndExtend
        elif key in {'Ctrl+LEFT', 'Ctrl+Shift+LEFT'}:
            fnc = self.WordLeftExtend
        elif key in {'Ctrl+RIGHT', 'Ctrl+Shift+RIGHT'}:
            fnc = self.WordRightExtend
        elif key in {'UP'}:
            fnc = self.LineUpExtend
        elif key in {'DOWN'}:
            fnc = self.LineDownExtend
        elif key in {'PAGEUP'}:
            fnc = self.PageUpExtend
        elif key in {'PAGEDOWN'}:
            fnc = self.PageDownExtend

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        sty = wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE  # | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME
        dlg = wx.ProgressDialog(f'Processing {cnt} selections', f'Keystroke: {key}', cnt, self, sty)
        cancel = False
        pgd_cnt = 0
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        dbf.TIMER('multisel')
        self.BeginUndoAction()

        for s in range(cnt):
#@@@@@@@@@@@@@@@@@@@@@@@@@
            pgd_cnt += 1
#@@@@@@@@@@@@@@@@@@@@@@@@@
            self.RotateSelection()
            fnc()
            # remove highlighted selections: anchor equals caret
            if 'Shift' not in key:
                self.SetSelectionNAnchor(s, self.GetSelectionNCaret(s))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            (cancel, _) = dlg.Update(pgd_cnt)
            if not cancel or pgd_cnt >= cnt:
                break
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.EndUndoAction()
        dbf.TIMER('multisel', 'STOP')

#@@@@@@@@@@@@@@@@@@@@@@
        self.Thaw()
        dlg.Destroy()
#@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#     def move_multiselect_carets(self, key):
# #INFO, How do you split a list into evenly sized chunks?
# #INFO, URL=https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
#         def chunks(lst, n):
#             """Yield successive n-sized chunks from lst."""
#             for i in range(0, len(lst), n):
#                 yield lst[i:i + n]

#         def thread_function(rng):
#             print(str(rng))
#             for s in rng:
#                 self.RotateSelection()
#                 if key in {'LEFT', 'Shift+LEFT'}:
#                     self.CharLeftExtend()
#                 elif key in {'RIGHT', 'Shift+RIGHT'}:
#                     self.CharRightExtend()
#                 elif key in {'HOME', 'Shift+HOME'}:
#                     self.VCHomeExtend()
#                 elif key in {'END', 'Shift+END'}:
#                     self.LineEndExtend()
#                 elif key in {'Ctrl+LEFT', 'Ctrl+Shift+LEFT'}:
#                     self.WordLeftExtend()
#                 elif key in {'Ctrl+RIGHT', 'Ctrl+Shift+RIGHT'}:
#                     self.WordRightExtend()
#                 elif key in {'UP'}:
#                     self.LineUpExtend()
#                 elif key in {'DOWN'}:
#                     self.LineDownExtend()
#                 elif key in {'PAGEUP'}:
#                     self.PageUpExtend()
#                 elif key in {'PAGEDOWN'}:
#                     self.PageDownExtend()
#                 # remove highlighted selections: anchor equals caret
#                 if 'Shift' not in key:
#                     self.SetSelectionNAnchor(s, self.GetSelectionNCaret(s))

#         cnt = self.Selections

#         # print('#selections:', cnt, 'MAIN:', self.MainSelection)
#         # self.Freeze()
#         dbf.TIMER('multisel')
#         # self.BeginUndoAction()

#         import threading

#         thread_lst = []
#         for idx, chunk in enumerate(chunks(range(1, cnt), 2)):
#             print(f'Main    : create and start thread {idx}.')
#             thread = threading.Thread(target=thread_function, args=(chunk,), daemon=True)
#             thread_lst.append(thread)
#             thread.start()

#         for idx, thread in enumerate(thread_lst):
#             print(f'Main    : before joining thread {idx}.')
#             thread.join()
#             print(f'Main    : thread {idx} done')

#         # self.EndUndoAction()
#         dbf.TIMER('multisel', 'STOP')
#         # self.Thaw()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def select_next_word(self):
        find_next = True
        cur = self.CurrentPos

        if not self.cur_sel_wrd:
            # get selection or select word under caret
            if self.SelectedText:
                # process selection left to right
                if cur < self.Anchor:
                    anchor, cur = cur, self.Anchor
                    # self.SelectNone()
                    self.SetSelection(anchor, cur)
            else:
                start = self.WordStartPosition(cur, True)
                end = self.WordEndPosition(cur, True)
                self.SetSelection(start, end)
                find_next = False

            # self.cur_sel_wrd = self.SelectedText
            self.cur_sel_wrd = self.GetTextRange(*self.GetSelection())

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # print(self.SelectedText)
        # print(self.cur_sel_wrd)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # find and add next occurrence to selection
        if find_next:
            flg = glb.SCH.get_flags()
            if (pos := self.FindText(cur, self.LastPosition, self.cur_sel_wrd, flg)) == stc.STC_INVALID_POSITION:
                # if glb.SCH.cbx_wrp.Value:
                #     print('WRAP TO TOP')
                #     self.SetCurrentPos(0)
                #     pos = self.FindText(0, self.LastPosition, self.cur_sel_wrd, flg)
                #     print(pos)
                # else:
                    glb.SBR.set_text('Unable to find [%s]' % self.cur_sel_wrd)
            else:
                self.AddSelection(pos + len(self.cur_sel_wrd), pos)
                self.EnsureCaretVisible()

    def set_x_scroll_offset(self, evt=None):
        if evt:
            evt.Skip()

        rlr = glb.RLR

        self.new_XOffset = self.XOffset
        if self.old_XOffset != self.new_XOffset:
            delta = self.old_XOffset - self.new_XOffset
            # update ruler alignment
            rlr.set_offset(rlr.offset + delta)
            self.old_XOffset = self.new_XOffset

    def set_caret_style(self, clr='GREEN'):
        self.tmr_cph.StartOnce(glb.CFG['CaretPositionHistory']['DelayDefaultStyle'])
        self.cph_active = True

        self.SetCaretForeground(glb.CFG['CaretPositionHistory']['ForeColour'])
        self.SetCaretPeriod(glb.CFG['CaretPositionHistory']['Period'])
        self.SetCaretStyle(glb.CFG['CaretPositionHistory']['Style'])
        self.SetCaretWidth(glb.CFG['CaretPositionHistory']['Width'])

    def reset_caret_style(self, evt):
        evt.Skip()
        self.cph_active = False

        self.SetCaretForeground(glb.CFG['Caret']['ForeColour'])
        self.SetCaretPeriod(glb.CFG['Caret']['Period'])
        self.SetCaretStyle(glb.CFG['Caret']['Style'])
        self.SetCaretWidth(glb.CFG['Caret']['Width'])

###########################################################################
#NOTE, EXPERIMENTAL: convert_indentation, create_indentation
###########################################################################

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#NOTE, copied/translated from 'ConvertIndentation' in 'SciTEBase.cxx'

    def convert_indentation(self, tab_siz, use_tab):
        self.ind_active = True
        self.BeginUndoAction()
        for lin in range(self.LineCount):
            print(lin)
            lin_pos = self.PositionFromLine(lin)
            ind_len = self.GetLineIndentation(lin)
            ind_pos = self.GetLineIndentPosition(lin)
            ind_max = 1000
            if ind_len < ind_max:
                ind_cur = self.GetTextRange(lin_pos, ind_pos)
                ind_new = self.create_indentation(ind_len, tab_siz, use_tab)
                if ind_cur != ind_new:
                    self.SetTargetStart(lin_pos)
                    self.SetTargetEnd(ind_pos)
                    self.ReplaceTarget(ind_new)
        self.EndUndoAction()
        self.ind_active = False
        glb.NBK.update_page_tab(self)

#NOTE, copied/translated from 'CreateIndentation' in 'SciTEBase.cxx'

    def create_indentation(self, ind_len, tab_siz, use_tab):
        ind_new = TXT_NIL
        if use_tab:
            while ind_len >= tab_siz:
                ind_new += '\t'
                ind_len -= tab_siz
        while ind_len > 0:
            ind_new += ' '
            ind_len -= 1
        return ind_new

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def show_busy(msg, pfx, prt, bgc, fgc):
    if not msg:
        pfx = ''
        msg = f'Zoom Level: {prt.Zoom}'
    # return glb.IBR.info_msg(f'{pfx} {msg} ...', 'INFO')
    return BusyInfo(f'{pfx} {msg} ...', prt, bgc, fgc)

def del_busy(dlg):
    del dlg
