#!/usr/bin/python

# pylint: disable=W0212(protected-access) [_disabler, _core, _getframe]

import __main__  # used for cfg

from bisect import bisect_left
from pathlib import Path
import string
import sys

import win32api
import win32gui
import wx
from wx.adv import RichToolTip as RTT
from wx.lib.agw import advancedsplash as AS

from common.type import is_tlw
from const.menu import MNU_FNT_AUX, MNU_FNT_TYP, NO_ICO
from const.common import TXT_NIL, LBL_FNT_STYLES
from conf.debug import DEBUG
from const.app import (
    APP, COMMON_EVENTS, FILTER_EVENTS, COMMON_KEYS, MOD_KEYS, OPT_BORDER,
    TLT_POSITION
)
from const import glb
from const.sidepanel import SPT
from data.images import catalog as PNG
import extern.supertooltip as STT


#FIX, needs better coding...
def app_filter_event(app, evt):
    res = app.Event_Skip

    if not DEBUG['AFE']:
        return res

    verbose = False
    if DEBUG['AFE'] > 1:
        verbose = True

    typ = evt.EventType
    nam = COMMON_EVENTS.get(typ, TXT_NIL)

#INFO, catch key events globally
#INFO, URL=https://wiki.wxwidgets.org/Catching_key_events_globally
    if nam == 'EVT_CHAR_HOOK':
        kpr_sct, __, __ = get_keypress(evt)
        print(kpr_sct)

    if nam == TXT_NIL:
        # if typ == 10416:
        #     nam = 'EVT_STC_DO_DROP'
        # else:
            nam = '*** _EVT_TYPE_UNKNOWN_ ***'

    # catch selected or all events (empty FILTER_EVENTS list)
    if FILTER_EVENTS and nam not in FILTER_EVENTS:
        return res

    # strip ' object at <0xADDRESS>' and keep name only
    obj = str(evt.EventObject)
    obj = obj[:obj.find(' object at ')]
    obj = obj[obj.rfind('.') + 1:]
    # discard repeating event names
    if not verbose:
        if typ != app.prv_evt_typ:
            app.prv_evt_typ = typ
            print(f'{typ:5d}  {nam:30s}  {obj}')
    else:
        fnm = evt.EventObject.fnm if obj in 'Editor' else TXT_NIL
        print(f'{typ:5d}  {nam:30s}  {obj}  {fnm}')

    # continue processing the event normally
    return res


class CharValidator(wx.Validator):
    def __init__(self, flag):
        super().__init__()
        self.flag = flag
        # self.SuppressBellOnError(False)  # bell active
        self.Bind(wx.EVT_CHAR, self.on_char)

    def Clone(self):
        # Note that every validator must implement the Clone() method.
        return CharValidator(self.flag)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def on_char(self, evt):
        key = chr(evt.KeyCode)
        if self.flag == 'digit' and key not in string.digits and ord(key) != wx.WXK_BACK:
            tip = RTT(f'Warning', 'Numeric input required !')
            tip.SetBackgroundColour('#FFFFF0')
            tip.SetIcon(wx.ICON_WARNING)
            tip.SetTipKind(wx.adv.TipKind_BottomLeft)
            tip.SetTitleFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            tip.SetTimeout(millisecondsTimeout=2000, millisecondsDelay=5)
            tip.ShowFor(self.Window, wx.Rect(-50, -8, *self.Window.ClientRect[2:]))
            return

        evt.Skip()


#INFO, URL=https://wxpython.org/Phoenix/docs/html/MigrationGuide.html#makemodal
# used in 'list_open_files', 'splash', 'FilterBox', FindReplaceDialog'
def make_modal(window, modal=True):
    if modal and not hasattr(window, '_disabler'):
        window._disabler = wx.WindowDisabler()
    if not modal and hasattr(window, '_disabler'):
        del window._disabler


def splash(frm, timeout=0):
    bmp = PNG['splash_wide_rgba'].Bitmap
    # bmp = PNG['splash_TSN_SPYe'].Bitmap
    sty = AS.AS_TIMEOUT if timeout else AS.AS_NOTIMEOUT
    sty += AS.AS_CENTER_ON_PARENT
    avs = AS.AdvancedSplash(frm, bitmap=bmp, timeout=timeout, agwStyle=sty)
    drop_shadow(avs)

    # make_modal(avs, True)

    # avs.SetText('SPyE')
    # avs.SetTextColour('DARK GRAY')
    # avs.SetTextFont(wx.Font(wx.FontInfo(77).Bold().Italic()))
    # avs.SetTextPosition((0, 78))

    # return avs


def welcome(frm):
    tip = RTT(f'Welcome to {APP["Base"]}', TXT_NIL)
    tip.SetBackgroundColour('#71B3E8', '#FFFFF0')
    tip.SetTipKind(wx.adv.TipKind_None)
    tip.SetTitleFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName='Comic Sans MS'))
    tip.SetTimeout(millisecondsTimeout=glb.CFG['Splash']['DelayHide'], millisecondsDelay=5)
    tip.ShowFor(frm, wx.Rect(0, -360, *frm.ClientRect[2:]))


#FIX, replace 'GridSizer' sizer with 'GridBagSizer', see 'search_panel.set_mode'
class QuickOpenDialog(wx.Dialog):
    def __init__(self, prt):
        super().__init__(prt, id=wx.ID_ANY, title='Quick Open  (not implemented)',
                         size=(430, 210), style=wx.DEFAULT_DIALOG_STYLE)

        self.stt_fnm = wx.StaticText(self, wx.ID_ANY, '&Filename:')
        self.txc_fnm = wx.TextCtrl(self, wx.ID_ANY, '', size=(300, -1), style=wx.BORDER_STATIC)
        self.btn_brw = wx.Button(self, wx.ID_ANY, '&Browse...')
        self.stt_pnm = wx.StaticText(self, wx.ID_ANY, '&Path:')
        self.txc_pnm = wx.TextCtrl(self, wx.ID_ANY, '', size=(300, -1), style=wx.BORDER_STATIC | wx.TE_READONLY)
        self.cbx_opn = wx.CheckBox(self, wx.ID_ANY, 'Open all &matching files from subdirectories')
        self.btn_opn = wx.Button(self, wx.ID_OK, '&Open')
        self.btn_clo = wx.Button(self, wx.ID_CANCEL, '&Close')

        # self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        grs = wx.GridSizer(6, 2, 0, 0)
        border = 5

        # convenient short naming (sizer flags)
        CV = wx.ALIGN_CENTRE_VERTICAL
        BT = wx.ALIGN_BOTTOM
        LT = wx.ALIGN_LEFT  | wx.ALL
        RT = wx.ALIGN_RIGHT | wx.ALL
        XP = ((0, 0), 1, wx.EXPAND, border)

        grs.Add(self.stt_fnm, 0, LT | BT, border)
        grs.Add(*XP)
        grs.Add(self.txc_fnm, 0, LT)
        grs.Add(self.btn_brw, 0, RT | CV, border)
        grs.Add(self.stt_pnm, 0, LT | BT, border)
        grs.Add(*XP)
        grs.Add(self.txc_pnm, 0, LT)
        grs.Add(*XP)
        grs.Add(self.cbx_opn, 0, LT | CV, border)
        grs.Add(self.btn_opn, 0, RT | CV, border)
        grs.Add(*XP)
        grs.Add(self.btn_clo, 0, RT | CV, border)

        self.btn_clo.Bind(wx.EVT_BUTTON, self.__on_exit)
        self.Bind(wx.EVT_CLOSE, self.__on_exit)

        self.btn_opn.SetDefault()

        self.SetSizer(grs)
        self.Layout()
        self.Centre()

    def __on_exit(self, evt):
        self.Destroy()


class TopLineToolTip(STT.SuperToolTip):
    def __init__(self, prt):
        self.sec = glb.CFG['TopLineToolTip']
        super().__init__(TXT_NIL)

#FIX, realize smooth 'TopLineToolTip' attribute coordination:
#FIX,     see 'supertooltip.py': 'SetStartDelay', 'SetEndDelay', 'DoShowNow', 'DoHideNow'
#FIX,     see 'SPyE.cfg', section 'TopLineToolTip': 'UseFade', 'DropShadow', 'DelayHide'

        # self.SetStartDelay(0)
        # print('ON ', glb.NBK.tlt.GetStartDelay())
        # print('OFF', glb.NBK.tlt.GetEndDelay())

        # glb.NBK.tlt.SetStartDelay(2)
        # glb.NBK.tlt.SetEndDelay(5)

        self.SetTarget(prt)
        self.SetMessageFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD, faceName='Courier New'))

        bgc, fgc = self.sec['BackColour'], self.sec['ForeColour']
        self.SetBottomGradientColour(bgc)
        self.SetMiddleGradientColour(bgc)
        self.SetTopGradientColour(bgc)
        self.SetTextColour(fgc)

        self.SetUseFade(self.sec['UseFade'])
        self.SetDropShadow(self.sec['DropShadow'])

        # self.ApplyStyle('NASA Blue')

        # disable tooltip popup when entering notebook window
        prt.Bind(wx.EVT_ENTER_WINDOW, None)

    def update(self, evt, doc, top, col):
        if not self.IsEnabled():
            # update 'scrolling' in statusbar
            glb.SB.set_text('Top Line: %d' % (top + 1), 'AUX')
            return

        # handle both scrollbars
        # if hasattr(evt, 'Orientation') and evt.Orientation == wx.VERTICAL:
        txt = self.sec['Text']
        self.SetMessage(txt % (doc.DocLineFromVisible(top) + 1, top + 1, col))

        if not self.GetTipWindow():
            self.DoShowNow()
            self.GetTipWindow().SetWindowStyle(OPT_BORDER['SUNKEN'])

        # convert editor client rectangle to screen coordinates
        clt = doc.ClientRect
        rct = wx.Rect(doc.ClientToScreen(clt.Position), clt.Size)
        loc = TLT_POSITION['TR']  # top right
        if DEBUG['SCL']: print('  TopLineToolTip: LOC:', loc, '| RECT:', rct)

        self._superToolTip.SetPosition((rct[0] + rct[2] + loc[0], rct[1] + loc[1]))
        self.Update()


class ColourToolTip(STT.SuperToolTip):
    def __init__(self, prt):
        self.sec = glb.CFG['TopLineToolTip']
        super().__init__(TXT_NIL)

#FIX, realize smooth 'TopLineToolTip' attribute coordination:
#FIX,     see 'supertooltip.py': 'SetStartDelay', 'SetEndDelay', 'DoShowNow', 'DoHideNow'
#FIX,     see 'SPyE.cfg', section 'TopLineToolTip': 'UseFade', 'DropShadow', 'DelayHide'

        # self.SetStartDelay(0)
        # print('ON ', glb.NBK.tlt.GetStartDelay())
        # print('OFF', glb.NBK.tlt.GetEndDelay())

        # glb.NBK.tlt.SetStartDelay(2)
        # glb.NBK.tlt.SetEndDelay(5)

        self.SetTarget(prt)
        self.SetMessageFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD, faceName='Courier New'))

        self.SetUseFade(self.sec['UseFade'])
        self.SetDropShadow(self.sec['DropShadow'])

        # self.ApplyStyle('NASA Blue')

        # disable tooltip popup when entering notebook window
        prt.Bind(wx.EVT_ENTER_WINDOW, None)

    def update(self, txt, bgc, pos):
        self.SetBottomGradientColour(bgc)
        self.SetMiddleGradientColour(bgc)
        self.SetTopGradientColour(bgc)
        self.SetTextColour('WHITE' if is_dark(bgc) else 'BLACK')

        self.SetMessage(txt)

        if not self.GetTipWindow():
            self.DoShowNow()
            self.GetTipWindow().SetWindowStyle(OPT_BORDER['RAISED'])

        self._superToolTip.SetPosition(pos)
        # self._superToolTip.SetPosition((pos[0], pos[1]+30))
        self.Update()


def widget_inspection_tool(shortcut='Ctrl+Alt+Shift+I'):
    sec = glb.CFG['WidgetInspectionTool']

    sct = sec['ShortCut'].upper()

    alt = bool('ALT+' in sct)
    cmd = bool('CTRL+' in sct)
    shift = bool('SHIFT+' in sct)

    key_cod = sct.split('+')[-1][0]

    # print(f'{shortcut=}, {alt=}, {cmd=}, {shift=}, {key_cod=}')

    glb.APP.InitInspection(alt=alt,
                           cmd=cmd,
                           shift=shift,
                           keyCode=ord(key_cod))

    if sec['ShowAtStartup']:
        wx.lib.inspection.InspectionTool().Show(
            selectObj=eval(f'glb.{sec["PreSelectObject"]}'),
            refreshTree=sec['RefreshWidgetTree'])


#HACK: avoid "DeprecationWarning: an integer is required (got type WindowIDRef)."
#INFO, URL=https://discuss.wxpython.org/t/deprecation-warnings-with-python-3-8/34405
def WindowIDRef_hack():
    wx._core.WindowIDRef.__index__ = wx._core.WindowIDRef.__int__


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# temporary code: win_warmth_lookup, Freeze, Thaw.   NOT CURRENTLY USED.   NOT CURRENTLY USED.   NOT CURRENTLY USED
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
# #INFO, Thaw failure despite IsFrozen returning True
# #INFO, URL=https://groups.google.com/forum/#!topic/wxpython-users/XABAqJ7GnY0
# win_warmth = {}
#
# def win_warmth_lookup(win):
#     # Check to see if we have already frozen or
#     #   thawed this window or any of its parents
#     nam = win.Name
#     hnd = win.Handle
#     lvl = 0
#     fnd = False
#     while not fnd:
#         if win is None:
#             break
#
#         hnd = win.Handle
#         fnd = hnd in win_warmth
#         if not fnd:
#             win = win.Parent
#             lvl += 1
#     return win, nam, hnd, lvl, fnd
#
# def win_warmth_freeze(win, src):
#     __, nam, hnd, lvl, fnd = win_warmth_lookup(win)
#
#     if fnd and win_warmth[hnd][3] == 'frozen':
#         if DEBUG['FZT']: print('>> %-10s [%-8s] (at %-15s) is already frozen!' % (nam, hnd, src))
#         # print('      >> [%s]' % (win))
#         # utils.Beep('Freeze')
#     else:
#         win.Freeze()
#         win_warmth[win.Handle] = [nam, lvl, src, 'frozen']
#         # print('Freeze [%s] (%s) successful:' % (hnd, src))
#         # for itm in win_warmth.items(): print(rs_(4, ' '), itm)
#
# def win_warmth_thaw(win, src):
#     win, nam, hnd, lvl, fnd = win_warmth_lookup(win)
#
#     if fnd and win_warmth[hnd][3] == 'frozen':
#         win.Thaw()
#         win_warmth[hnd][2] = src
#         win_warmth[hnd][3] = 'thawed'
#         # print('  Thaw [%s] (%s) successful:' % (hnd, src))
#
#         # for itm in win_warmth.items(): print(rs_(4, ' '), itm)
#     else:
#         if DEBUG['FZT']: print('>> %-10s [%-8s] (at %-15s) is   NOT   frozen!' % (win.Name, win.Handle, src))
#         # utils.Beep('Thaw')
#
# # I don't know if traveling up the window tree in my win_warmth_lookup routine was
# # necessary.  I coded it that way because I thought my problems might be parent/child
# # problems, e.g., freezing a parent, then thawing one or more of its children, then
# # trying to thaw the parent.
#
# # This URL made me wonder:
# #     http://wxpython-users.1045709.n5.nabble.com/Thaw-without-matching-Freeze-td2361682.html
# # even though the bug reported there was reported as fixed ( http://trac.wxwidgets.org/ticket/4549 ).
#
# # Does anyone here know if the while loop is ever necessary?
# # The Freeze/Thaw failures I was experiencing and that motivated this code
# # did not require any child-to-parent traversals, so I still don't know.
#
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# temporary code: win_warmth_lookup, Freeze, Thaw.   NOT CURRENTLY USED.   NOT CURRENTLY USED.   NOT CURRENTLY USED
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


##################################################################################################
##################################################################################################


def create_symbol_index(tlw, mth):
    if not glb.CFG['SymbolIndex']['Enable']:
        return

#NOTE, prevent circular dependency
    from tool.symbol import SymbolIndex
    from conf.debug import dbg_SYMBOL_INDEX

    sym_idx = SymbolIndex()  # Python symbol index object
    tlw.dfn_idx, tlw.ref_idx, tlw.imp_idx, tlw.var_idx, tlw.wrd_idx, tlw.qts_idx = sym_idx.create()
    dbg_SYMBOL_INDEX(desc=False, word=False, total=False, count=False, verbose=False)


# get 2nd elem from list: ['<type ', 'datatype', '>']
def d_type(val):
    return str(type(val)).split('\'')[1]


# create/destroy drop shadow under window
def drop_shadow(win, show=True):
    if wx.Platform != '__WXMSW__':
        return

    hnd, CS_DROPSHADOW, GCL_STYLE = win.Handle, 0x00020000, -26  # constant defs, see 'winuser.h'

    sty = win32gui.GetClassLong(hnd, GCL_STYLE)
    if show:
        if sty & CS_DROPSHADOW == 0:
            win32api.SetClassLong(hnd, GCL_STYLE, sty | CS_DROPSHADOW)
    else:
        win32api.SetClassLong(hnd, GCL_STYLE, sty & ~CS_DROPSHADOW)


#FIX, reorganize dbg_callername, dbg_funcname dbg_funcname_app, me_
def funcname(lvl=1):
    return sys._getframe(lvl).f_code.co_name


def _get_cfg():
    return __main__.CFG


def _get_lng():
    return __main__.LNG


# character position under cursor
def get_char_pos(doc, close=True):
    # client cursor coordinates
    x, y = doc.ScreenToClient(wx.GetMousePosition())
    if close:
        pos = doc.CharPositionFromPointClose(x, y)
    else:
        pos = doc.CharPositionFromPoint(x, y)
    return x, y, pos


#INFO, from list of integers, get number closest to a given value
#INFO, URL=https://stackoverflow.com/questions/12141150/from-list-of-integers-get-number-closest-to-a-given-value
def get_closest_index(lst, num):
    """
    Assumes lst is sorted. Returns index of closest value to num.
    If two numbers are equally close, return index of the smallest number.
    """
    pos = bisect_left(lst, num)
    if pos == 0:
        return 0
    if pos == len(lst):
        return len(lst) - 1
    after = lst[pos]
    before = lst[pos - 1]
    if after - num < num - before:
        return pos
    return pos - 1


#NOTE, not used
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# get most used event attributes; convenience function
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# from common.util import get_evt_att
# pprint(get_evt_att(evt))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
def get_evt_att(evt):
    obj = evt.EventObject
    typ = evt.EventType
    id_ =  evt.Id
    nam = obj.Name if hasattr(obj, 'Name') else TXT_NIL
    # menu objects have 1 parameter, other objects have none
    try:
        lbl = obj.GetLabel(id_)
    except TypeError as e:
        lbl = obj.GetLabel()
    return obj, typ, id_, nam, lbl
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#INFO, Icons (Design basics) - Win32 apps Icons
#INFO, URL=https://docs.microsoft.com/en-us/windows/win32/uxguide/vis-icons Windows
#INFO, Icon Size Guide
#INFO, URL=https://www.creativefreedom.co.uk/icon-designers-blog/windows-7-icon-sizes/
# create square icon bitmap from 'PyEmbeddedImage'
def get_icon(nam='app', siz=24):
    bmp = PNG[nam].Bitmap
    ico = scale_bitmap(bmp, siz, siz)
    return ico


def get_keypress(evt):
    cod = evt.KeyCode
    nam = COMMON_KEYS.get(cod, None)  # key name

    if not nam:
        if 'unicode' in wx.PlatformInfo:
            cod = evt.UnicodeKey
            if cod <= 127:
                cod = evt.KeyCode
            nam = chr(evt.UnicodeKey)
        elif cod < 256:
            if cod == 0:
                nam = 'NUL'
            elif cod < 27:
                nam = chr(ord('A') + cod - 1)
            else:
                nam = chr(cod)
        else:
            err = f'{me_("F")}: unknown key name for keycode [{cod}]'
            raise AssertionError(err)

    modifiers = ''
    for mod, lbl in [(evt.controlDown, 'Ctrl+'),
                     (evt.altDown,     'Alt+'),
                     (evt.shiftDown,   'Shift+'),
                     (evt.metaDown,    'Meta+')]:
        if mod:
            modifiers += lbl

    kpr_sct = ''
    if nam:
        kpr_sct = modifiers + nam

    return kpr_sct, nam, cod


# convert colour to hexadecimal '#rrggbb' representation
def hex_colour(dta):
    r, g, b = dta.Colour.Get(includeAlpha=False)
    clr = f'#{r:02X}{g:02X}{b:02X}'
    return clr


# return if colour is dark or not
def is_dark(colour):
#INFO, Determine font color based on background color
#INFO, URL=https://stackoverflow.com/questions/1855884/determine-font-color-based-on-background-color
    # avg = (.299 * colour.Red() + .587 * colour.Green() + .114 * colour.Blue()) / 255
    # if avg < .5:
    avg = (colour.Red() + colour.Green() + colour.Blue()) / 3
    if avg < 127:
        return True
    return False


# return if a panel is visible
def is_shown(pnl):
    sch = glb.SPL['SCH'].IsSplit()  # search panel
    spn = glb.SPL['SPN'].IsSplit()  # side panel
    ccx = glb.SPL['CCX'].IsSplit()  # code context
    rlr = glb.SPL['RLR'].IsSplit()  # ruler

    # search panel
    if pnl in 'SCH':
        return sch
    # search panel mode
    elif pnl in ['INC', 'FND', 'RPL', 'FIF', 'RES']:
        return sch and glb.SCH.mode == pnl
    # side panel
    elif pnl in 'SPN':
        return spn
    # side panel tool
    elif pnl in SPT:
        return spn and glb.SPN.GetSelection() == SPT[pnl].idx
    # code context
    elif pnl in 'CCX':
        return ccx
    # ruler
    elif pnl in 'RLR':
        return rlr
    else:
        # we should NEVER get here
        err = f'{glb.TLW.__class__.__name__}: unknown panel name [{pnl}]'
        raise AssertionError(err)
    return False


# checks if selected text matches a word
def is_word_at(doc, pos):
    if doc.Selections == 1 and doc.SelectedText:
        if doc.SelectionStart == doc.WordStartPosition(pos, True) and \
            doc.SelectionEnd == doc.WordEndPosition(pos, True):
            return True
    return False


#FIX, reorganize dbg_callername, dbg_funcname dbg_funcname_app, me_
def me_(spec='A', lvl=1):
    # return [A]ll names if spec is default: 'A'
    spec = 'M, C, F, L' if 'A' in spec else spec
    # return [M]odule, [C]lass, [F]unction/method name(s) and/or [L]ine number plus simple formatting
    out = TXT_NIL
    for typ in spec.upper():
        # caller's frame, namespaces
        _frm = sys._getframe(lvl)
        _glb, _lcl = _frm.f_globals, _frm.f_locals
        # module
        if typ == 'M':
            pfx = 'Mod'
            mod = _glb['__name__']
            fil = Path(_glb['__file__']).name
            out += f'[{pfx}] {mod} (file: {fil})'
        # class
        elif typ == 'C':
            pfx = 'Cls'
            cls = f'{_lcl["self"].__class__.__name__}' if 'self' in _lcl else '<n/a>'
            out += f'[{pfx}] {cls}'
        # function (or method)
        elif typ == 'F':
            pfx = 'Mth' if 'self' in _lcl else 'Fnc'
            fnc = _frm.f_code.co_name
            out += f'[{pfx}] {fnc}'
        # line number
        elif typ == 'L':
            pfx = 'Lin'
            lin = _frm.f_lineno
            out += f'[{pfx}] {lin}'
        # formatting
        elif typ in ' :;,>':
            out += typ
        else:
            return f'  {me_("F")}: unknown format type: [{typ}]'

    return out  # +'\n'

##################################################################################################
##################################################################################################


# message dialog box
def msg_box(prt, typ='INFO', msg='', extra=''):
    # style and caption
    if typ == 'HELP':
        sty = wx.HELP  # | wx.ICON_NONE
        cap = APP['Base'] + ' Help'
    elif typ == 'INFO':
        sty = wx.OK | wx.OK_DEFAULT | wx.ICON_INFORMATION
        cap = 'Information'
    elif typ == 'WARN':
        sty = wx.OK | wx.OK_DEFAULT | wx.ICON_EXCLAMATION
        cap = 'Warning'
    elif typ == 'WARN_ASK':
        sty = wx.YES_NO | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_EXCLAMATION
        cap = 'Warning'
    elif typ == 'ERROR':
        sty = wx.OK | wx.OK_DEFAULT | wx.ICON_ERROR
        cap = 'Error'
    else:
        # we should NEVER get here
        err = f'{me_("F")}: unknown message dialog box type [{typ}]'
        raise AssertionError(err)
    # append text to caption
    if extra:
        cap = f'{cap} ({extra})'

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#     with wx.MessageDialog(prt, msg, cap, style=sty) as dlg:
# #FIX, icon not shown
#         set_icon(dlg)
#         res = dlg.ShowModal()

    from wx.lib.agw.genericmessagedialog import GenericMessageDialog

    with GenericMessageDialog(glb.TLW, msg, cap, agwStyle=sty) as dlg:
        # no dialog button bitmaps
        _NO_BMP = wx.Bitmap(0, 0)
        dlg.SetHelpBitmap(_NO_BMP)
        dlg.SetOKBitmap(_NO_BMP)
        # dlg.SetOKCancelBitmaps(_NO_BMP, _NO_BMP)
        dlg.SetYesNoCancelBitmaps(_NO_BMP, _NO_BMP, _NO_BMP)
#HACK: allow ESCAPE key via 'OnKeyDown' in 'wx.lib.agw.genericmessagedialog.py'
#INFO, URL=https://bit.ly/3nMlvJm
        dlg.Bind(wx.EVT_CHAR_HOOK, dlg.OnKeyDown)
        res = dlg.ShowModal()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    return res


# stub: for unimplemented functionality
def not_implemented(evt, txt=None):
    if evt:
        obj = evt.EventObject
        if is_tlw(obj):
#NOTE, weird behaviour after 'Ctrl+Shift+U' followed by 'Ctrl+Shift+I'
            return
            # txt = obj.GetLabel()
        else:  # elif isinstance(obj, wx.Menu):
            txt = obj.GetLabel(evt.Id)

    if DEBUG['NIM']: print('NOIMP: [%s]' % txt)
    txt = '[%s] -> NOT implemented' % txt.replace('\t', ': ')
    # glb.SB.set_text(txt, typ='WARN')
    glb.IB.info_msg(txt, wx.ICON_WARNING, 'WHITE', '#C30100')

    # raise NotImplementedError


# register global hotkey shortcut
def register_hotkey(tlw, hotkey):
    cmn_keys = swap_dict(COMMON_KEYS)
    mod_keys = swap_dict(MOD_KEYS)

    # split modifiers and keycode
    hot_lst = hotkey.split('+')
    mod, cod = hot_lst[0:-1], hot_lst[-1]

    # set modifier flags
    flg = wx.MOD_NONE
    for m in mod:
        flg |= mod_keys[m]

    # lookup keycode
    if cod in cmn_keys:
        cod = cmn_keys[cod]
    else:
        # if len(cod) == 1:  # avoid error for 1 item with >1 chars: 'Backspace'
            cod = ord(cod)
        # else:
        #     return

    return tlw.RegisterHotKey(1, flg, cod)


#INFO, repeat string to certain length
#INFO, URL=https://stackoverflow.com/questions/3391076/repeat-string-to-certain-length
# called without arguments results in: '-----'
def rs_(len_=5, str_='-'):
    return (len_ * str_)[:len_]


def scale_bitmap(bmp, w, h):
    qly = wx.IMAGE_QUALITY_HIGH
    bmp = bmp.ConvertToImage().Scale(w, h, qly).ConvertToBitmap()
    return bmp


def set_font(obj, face=None, siz=None, bold=False, italic=False):
    fnt = obj.Font
    if face:
        fnt.SetFaceName(face)
    if siz:
        fnt.SetPointSize(siz)
    if bold:
        fnt.MakeBold()
    if italic:
        fnt.MakeItalic()
    obj.SetFont(fnt)


# set dialog icon
def set_icon(dlg, ico=None):
    if DEBUG['GEN']: print(f'{me_()}')
    if not ico:
        ico = APP['Icon']
    dlg.SetIcon(ico)
    dlg.SetBackgroundColour(glb.CFG['General']['DialogBackColour'])


# set menu item icon bitmap
def set_menu_item_icon(mni, knd, ico, icc):
    # checkable item
    if knd in ['CHECK', 'RADIO']:
        if icc:
            try:
#NOTE, for now, ONLY 9 custom check icons implemented (see 'Search -> Option Flags' menu)
                mni.SetBitmaps(PNG[ico].Bitmap, PNG[ico].Image.ConvertToGreyscale().ConvertToDisabled().ConvertToBitmap())  # custom
                # mni.SetBitmaps(PNG[ico].Bitmap, PNG[f'{ico}_unchk'].Bitmap)  # custom
            except KeyError:
                mni.SetBitmaps(PNG[ico].Bitmap, wx.NullBitmap)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # mni.SetBitmaps(PNG[ico].Bitmap, wx.NullBitmap)  # custom: TEST (uncheck = empty)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        else:
            mni.SetBitmaps(mni.Bitmap)  # system-defined
    # normal item
    elif ico != NO_ICO:
        mni.SetBitmap(PNG[ico].Bitmap)


# set menu item label with optional font style
def set_menu_item_label(mni, lbl):
    # auxiliary font
    if MNU_FNT_AUX:
        p, f, s, w, n = MNU_FNT_TYP
        mni.SetFont(wx.Font(p, f, s, w, faceName=n))

#FIX, create function 'set_font_style' in 'util.py'
    # label font
    fnt = mni.Font
    for key, sty in LBL_FNT_STYLES.items():
        if (tag := f'[[{key}]]') in lbl:
            lbl = lbl.replace(tag, TXT_NIL)
#FIX, needs better coding...
            cmd = f'fnt.Make{sty}()'
            exec(cmd)

    mni.SetItemLabel(lbl)
    mni.SetFont(fnt)


# swap dictionary 'key:val' to 'val:key' (inverse lookup)
def swap_dict(dict_):
    return {v:k for k, v in dict_.items()}


#@@@@@@@@@@@@ OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE @@@@@@@@@@
#@@@@@@@@@@@@ OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE @@@@@@@@@@
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# # 2 convenience functions: 'create_tlw_att', 'set_tlw_att'
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# # Create/Set attributes (references) for most frequently used top level window instances
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# # Injected instance attributes in class 'obj':
# #    CFG    Config (global from __main__ namespace)
# #    app    Application (wx.App)
# #    tlw    AppFrame (wx.Frame, top level window)
# #    mb     MenuBar
# #    tb     ToolBar
# #    sb     StatusBar
# #    nbk    Notebook
# #    sch    SearchPanel
# #    spn    SidePanel
# #    rlr    Ruler
# #    ccx    CodeContext
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# # called from AppFrame.__init__', create its 'tlw' attributes
# def create_tlw_att(obj):
#     for obj_str in TLW_ATT_LST[3:]:
#         obj = eval(f'obj.{obj_str}')
#         nam = obj.__class__.__name__
#         if DEBUG['TLW']: print(f'\n    {me_("F")}:\n    * obj: {nam}')
#         set_tlw_att(obj)
#         for att_str in TLW_ATT_LST[1:]:
#             att = eval(f'obj.{obj_str}.{att_str}')
#             if DEBUG['TLW']: print(f'        {att_str:3}  [{att}]')
#     if DEBUG['TLW']: print()

# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# # called from a class (__init__) method OR function to access 'tlw' attributes
# def set_tlw_att(obj):
#     CFG = _get_cfg()
#     app = wx.GetApp()
#     tlw = app.TopWindow
#     for att_str in TLW_ATT_LST[:3]:
#         setattr(obj, att_str, eval(att_str))
#         if DEBUG['TLW']: print(f'! -> SET {att_str:3} in:  {me_("C", 2)}')
#     for att_str in TLW_ATT_LST[3:]:
#         if hasattr(tlw, att_str):
#             if DEBUG['TLW']: print(f'    {me_("F")}: {me_("C", 2)} -> {att_str}')
#             setattr(obj, att_str, getattr(tlw, att_str))
#         else:
#             if DEBUG['TLW']: print(f'! -> {att_str:3}  NOT set in:  {me_("C", 2)}')
#     if DEBUG['TLW']: print()
#@@@@@@@@@@@@ OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE @@@@@@@@@@
#@@@@@@@@@@@@ OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE @@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# as a Mixin class with an __init__
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# class TlwAtt

#     ATT_LST = ('mb', 'tb', 'sb', 'nbk', 'sch', 'spn', 'rlr', 'ccx')

#     # called from AppFrame.__init__', create
#     def __init__(self, obj):
#         if obj.__class__.__name__ == 'AppFrame':
#             self.create(obj)
#         else:
#             self.set_(obj)

#     def create(self, obj):
#         for obj_str in self.ATT_LST:
#             obj = eval(f'obj.{obj_str}')
#             nam = obj.__class__.__name__
#             if DEBUG['TLW']: print(f'\n    {me_("F")}:\n    * obj: {nam}')
#             self.set_(obj)
#             for att_str in ('app', 'tlw', *self.ATT_LST):
#                 att = eval(f'obj.{obj_str}.{att_str}')
#                 if DEBUG['TLW']: print(f'        {att_str:3}  [{att}]')
#         if DEBUG['TLW']: print()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#     # called from '__init__' whose class uses 'tlw' attributes
#     def set_(self, obj):
#         CFG = __main__.CFG
#         app = wx.GetApp()
#         tlw = app.TopWindow
#         for att_str in ('CFG', 'app', 'tlw'):
#             setattr(obj, att_str, eval(att_str))
#             if DEBUG['TLW']: print(f'! -> SET {att_str:3} in:  {me_("C", 2)}')
#         for att_str in self.ATT_LST:
#             if hasattr(tlw, att_str):
#                 if DEBUG['TLW']: print(f'    {me_("F")}: {me_("C", 2)} -> {att_str}')
#                 setattr(obj, att_str, getattr(tlw, att_str))
#             else:
#                 if DEBUG['TLW']: print(f'! -> {att_str:3}  NOT set in:  {me_("C", 2)}')
#         if DEBUG['TLW']: print()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# return list of 'count' zeroes
def zero(count=0):
    return [0 for z in range(count)]


########################################################################################################################
# SCRATCH CODE SNIPPETS FOR FUTURE USE GO HERE
########################################################################################################################


#FIX, decorator for get_doc
def cur_doc(arg):

#NOTE, prevent circular dependency
    from common.doc import get_doc

    def __decorator(fnc):
        def __wrapper(self, *args, **kwargs):
            print(f'decorator [cur_doc] for [{fnc.__name__}]')
            tlw = wx.GetApp().TopWindow
            if not (doc := get_doc()): return
            fnc(self, doc, *args, **kwargs)
        return __wrapper
    return __decorator


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#FIX: get window name under mouse cursor
def _win_under_cursor(app, evt):
    _gks = wx.GetKeyState
    ctrl, alt = _gks(wx.WXK_CONTROL), _gks(wx.WXK_ALT)
    if not (ctrl and alt):
        return
    # pos = wx.GetMouseState().Position
    # win = wx.FindWindowAtPoint(pos)
    win, pos = wx.FindWindowAtPointer()
    nam = str(win)
    end = nam.find(' object at ')
    start = nam.rfind('.') + 1
    nam = nam[start:end]
    if nam == app.prv_nam:
        return
    app.prv_nam = nam
    # print(nam)
    print(f'{nam:25} at {pos} ({win.Name})')
#     app.highlight_window(win)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# def highlight_window(self, win):
#     rct = win.Rect
#     tlw = win.TopLevelParent
#     pos = win.ClientToScreen((0,0))
#     rct.SetPosition(pos)
#     for i in range(10):
#         self.do_highlight(tlw, rct, 'RED')
#     for i in range(10):
#         self.do_highlight(tlw, rct, None, mode='Clear')
#
# def do_highlight(self, tlw, rct, colour, penWidth=2, mode=0):
#     dc = wx.ScreenDC()
#     dc.SetPen(wx.Pen(colour, penWidth))
#     dc.SetBrush(wx.TRANSPARENT_BRUSH)
#
#     drawRect = wx.Rect(*rct)
#     drawRect.Deflate(2,2)
#     if mode == 'Clear':
#         dc.SetPen(wx.TRANSPARENT_PEN)
#     dc.DrawRectangle(drawRect)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


########################################################################################################################
# SCRATCH CODE SNIPPETS FOR FUTURE USE END HERE
########################################################################################################################
