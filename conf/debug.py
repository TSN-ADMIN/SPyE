#!/usr/bin/python

# pylint: disable=W0212(protected-access) [_getframe]

####################################################################################
# custom exception hook: show Python version before traceback
# def custom_excepthook(exctype, value, traceback):
#         print('Python v{0}'.format(sys.version))
#         sys.__excepthook__(exctype, value, traceback)
# sys.excepthook = custom_excepthook
####################################################################################

import argparse
from datetime import datetime as dtm
import functools
from inspect import getouterframes, currentframe, stack
import os
from pprint import pprint
import sys

from extern.configobj import ConfigObj, __version__ as co_version
from extern.configobj.validate import Validator, __version__ as cv_version
from pathlib import Path
from pubsub import __version__ as pub_version
import pycodestyle
import pyflakes
import pylint
import radon
import vulture
import wx
from wx import stc

from common.date import TIM_FMT, now_
from common.path import cwd
from common.type import is_stc, is_txc
from const import glb
from const.menu import MI
from const.app import APP, EXE
from const.common import TXT_NIL
from const.sidepanel import SPT
from const.statusbar import SBF
from const.symbol import SYMBOL
from tool.ctags import ctags_version


class Debug(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.read()

    def default(self):
        # if DEBUG['_DBG_']: print(f'{me_()}\n  File = {self.filename}\n')
        self['DEBUG'] = {}
        # self['DEBUG']['_DBG_'] = 0  # 1: Experimental, DeBuG debug...

        # create debug keys w/ zero value
        for key in ('ACC', 'ACP', 'AFE', 'AIB', 'APP', 'BMK', 'BPT', 'BRC',
                    'CDB', 'CFG', 'CPH', 'CTP', 'CTX', 'DCL', 'DCM', 'DEC',
                    'DFC', 'DOC', 'EVT', 'FCS', 'FIL', 'FNM', 'FZT', 'GEN',
                    'GLB', 'IDL', 'IND', 'INF', 'KBD', 'LFL', 'LNG', 'MAC',
                    'MCB', 'MDC', 'MNU', 'NBK', 'NIM', 'OAC', 'PDB', 'PTH',
                    'RBM', 'RFH', 'RLR', 'SAS', 'SBR', 'SCC', 'SCH', 'SCL',
                    'SFH', 'SIX', 'SME', 'SPN', 'SPU', 'SSN', 'STK', 'SYS',
                    'TBR', 'THM', 'TLW', 'TMR', 'TSK', 'TWS', 'UPD', 'WNM',
                    'ZOO',):
            self['DEBUG'][key] = 0

        ##################################################################################
        # Example ConfigObj comments: regular and inline, note .append vs .insert!
        ##################################################################################
        #
        # self['DEBUG'].comments['_KEY_'].append('REGULAR: description of _KEY_')
        # self['DEBUG'].inline_comments['_KEY_'] = 'INLINE: description of _KEY_'
        #
        #    OR like this:
        #
        # cmt_txt = '%s : description of _KEY_'
        # self['DEBUG'].comments['_KEY_'].insert(0, cmt_txt % 'REGULAR')
        # self['DEBUG'].inline_comments['_KEY_'] = cmt_txt % 'INLINE'
        #
        ##################################################################################

        # add comments to debug keys
        __ = self['DEBUG'].inline_comments  # convenient short naming (__)

        __['ACC'] = ' 1: ACCELerator table'
        __['ACP'] = ' 1: AutoComPlete                 2: ++ event info'
        __['AFE'] = ' 1: Application Filter Events    2: ++ all events (verbose)'
        __['AIB'] = ' 1: AUtoInsert Braces            2: ++ event info'
        __['APP'] = ' 1: APPlication/help functions   2: ++ current doc'
        __['BMK'] = ' 1: BooMarK                      2: ++ Get/Set/Update'
        __['BPT'] = ' 1: BreakPoinT                   2: ++ Get/Set/Update'
        __['BRC'] = ' 1: BRaCe match                  2: ++ event info'
        __['CDB'] = ' 1: ColourDataBase               2: ++ all (red,green,blue)=>colournames in database'
        __['CFG'] = ' 1: ConFiG                       2: ++ file.cfg content, beeprint'
        __['CPH'] = ' 1: Caret Position History'
        __['CTP'] = ' 1: CallTiP                      2: ++ event info'
        __['CTX'] = ' 1: ConTeXt menu'
        __['DCL'] = ' 1: DoCument List'
        __['DCM'] = ' 1: DoCument Map                 2: ++ lines on editor screen; view zone area'
        __['DEC'] = ' 1: DECorator'
        __['DFC'] = ' 1: Detect File Change           2: ++ interval and resave/reload dialog info'
        __['DOC'] = ' 1: DOCument state'
        __['EVT'] = ' 1: most EVenTs                  2: ++ AuiNotebook/Fold/Margin/ContextMenu events'
        __['FCS'] = ' 1: window FoCuS'
        __['FIL'] = ' 1: FILe action                  2: ++ file info'
        __['FNM'] = ' 1: Function NAMe                2: ++ _function_name;  3: ++ frequent calls, i.e. get_doc'
        __['FZT'] = ' 1: FreeZe/Thaw, e.g. \'_avoid_flicker\''
        __['GEN'] = ' 1: GENeric (general)            2: ++ idle/updateui/refresh/get_doc/scrolling events'
        __['GLB'] = ' 1: GLoBal doc ptr (TEST)'
        __['IDL'] = ' 1: IDLe event                   2: ++ event info'
        __['IND'] = ' 1: INDicator: mark matches'
        __['INF'] = ' 1: app start / stop INFo        2: ++ timestamp/PID/versions (verbose)'
        __['KBD'] = ' 1: KeyBoarD: key presses        2: ++ BRIEF keys;      3: ++ event info'
        __['LFL'] = ' 1: List FiLter'
        __['LNG'] = ' 1: language (syntax styling)    2: ++ file.lng content, code element: stylespec field details'
        __['MAC'] = ' 1: MACro'
        __['MCB'] = ' 1: Multi ClipBoard'
        __['MDC'] = ' 1: document Map memory DC (TEST Device Context)'
        __['MNU'] = ' 1: MeNU                         2: ++ all items with accelerator keys'
        __['NBK'] = ' 1: NoteBooK: active tab         2: ++ pages/tab controls'
        __['NIM'] = ' 1: Not IMplemented'
        __['OAC'] = ' 1: Open At Caret (file/URL)'
        __['PDB'] = ' 1: Python DeBugger commands     2: ++ breakpoints      3: ++ stdin          4: ++ stdout                 5: ++ stderr'
        __['PTH'] = ' 1: Page Tab History             2: ++ stage details    3: ++ cache info'
        __['RBM'] = ' 1: ReBuild Menu                 2: ++ menu check item save/restore state'
        __['RFH'] = ' 1: Recent File History          2: ++ file.rfh content'
        __['RLR'] = ' 1: RuLeR                        2: ++ drawing coordinate details'
        __['SAS'] = ' 1: SASh: splitter window'
        __['SBR'] = ' 1: StatusBaR'
        __['SCC'] = ' 1: Scintilla Command Codes      2: ++ sort by name (instead of code)'
        __['SCH'] = ' 1: SearCH panel                 2: ++ search flags'
        __['SCL'] = ' 1: SCroLling'
        __['SFH'] = ' 1: Search Field History         2: ++ file.sfh content'
        __['SIX'] = ' 1: Symbol IndeX (files)         2: summary/counts      3: ++ line comments  4: ++ triple quote comments  5: ++ details'
        __['SME'] = ' 1: Scintilla ModEventmask'
        __['SPN'] = ' 1: Side PaNel                   2: ++ side panel tools IsShown status'
        __['SPU'] = ' 1: Symbol PopUp (word)'
        __['SSN'] = ' 1: SeSsioN                      2: ++ file.ssn content'
        __['STK'] = ' 1: call STacK: [lvl]whoami      2: ++ caller(1);       3: ++ caller(2);     4: ++ caller(3)'
        __['SYS'] = ' 1: SYStem trace func'
        __['TBR'] = ' 1: TooLBaR                      2: ++ all items'
        __['THM'] = ' 1: THeME colours                2: ++ file.thm content'
        __['TLW'] = ' 1: Top Level Window attributes (references)'
        __['TMR'] = ' 1: TiMeR: startup/open/close    2: ++ session;         3: ++ DragZone.set_transparency'
        __['TSK'] = ' 1: TaSKs (code comment tags)'
        __['TWS'] = ' 1: Trailing WhiteSpace'
        __['UPD'] = ' 1: UPDateui events              2: ++ event info'
        __['WNM'] = ' 1: set Window NaMe, used in WIT'
        __['ZOO'] = ' 1: editor ZOOm/offset'

    def create(self):
        # if DEBUG['_DBG_']: print(f'{me_()}\n  File = {self.filename}\n')

        # get default configuration
        self.default()
        self.commit()

    def read(self):
        # if DEBUG['_DBG_']: print(f'{me_()}\n  File = {self.filename}\n')

#HACK: copy our 'self['DEBUG']' to the global 'DEBUG' dict (used for import)
        for sec in self:
            for key in self[sec]:
                # convert data type: string -> int
                val = int(self[sec][key])  # use 'val' for readability
                DEBUG[key] = val
                # if DEBUG['_DBG_']: print(sec, key, val)

        # DEBUG = collections.OrderedDict(sorted(DEBUG.items()))
        # print(DEBUG['FNM'])
        # print(self['DEBUG']['FNAME'])

#FIX, not used: obsolete?
    def commit(self):
        # if DEBUG['_DBG_']: print(f'{me_()}\n  File = {self.filename}\n')
        self.write()


#FIX, refactor (also check 'from conf.debug import DEBUG')
# global 'DEBUG' dict (used for import)
DEBUG = {}


#TODO, refactor ALL 'dbg_' functions to 'class Debug'
######################################################
# class Debug
#     def __init__(...)
#     def info():
#     def event(evt):
#     def ...
######################################################


#NOTE, prevent circular dependency
from common.util import d_type, me_, rs_


# used in '__main__'
# application start / stop info
def dbg_APP_INFO(mode='START', version=True, verbose=True):
    if DEBUG['INF'] < 2 and not DEBUG['SYS']:
        return

    wsp = rs_(1, ' ')
    ver_pyt = sys.version.split()[0]
    ver_wxp = wx.version()
    ver_stc = stc.StyledTextCtrl.GetLibraryVersionInfo().VersionString.split()[1]
    ver_arg = f'{argparse.__version__}'
    ver_cfo = f'{co_version}'
    ver_vld = f'{cv_version} (Validate)'
    ver_pub = f'{pub_version}'
    ver_pys = f'{pycodestyle.__version__}'
    ver_pfl = f'{pyflakes.__version__}'
    ver_plt = f'{pylint.__version__}'
    ver_lru = f'1.2.0'
    ver_rad = f'{radon.__version__}'
    ver_vlt = f'{vulture.version.__version__}'
    ver_ctg = ctags_version().split('(')[0]
    ver_os_ = wx.GetOsDescription()

    print(f'* [{wx.Now()}]: {mode.title()} {APP["Base"]}')
    print(f'{wsp}  PythonExec [{EXE["PYTHON"]}]')
    print(f'{wsp}  PythonPath [{EXE["PYPATH"]}]')
    print(f'{wsp}     AppPath [{APP["Path"]}]')
    print(f'{wsp}         PID [{os.getpid()}]')

    if version:
        print(f'{wsp} -----------')
        print(f'{wsp}      Python [{ver_pyt}]')
        print(f'{wsp}    wxPython [{ver_wxp}]')
        print(f'{wsp}   Scintilla [{ver_stc}]')
        print(f'{wsp}    ArgParse [{ver_arg}]')
        print(f'{wsp}   ConfigObj [{ver_cfo}]')
        print(f'{wsp}       "     [{ver_vld}]')
        print(f'{wsp}    PyPubSub [{ver_pub}]')
        print(f'{wsp} Pycodestyle [{ver_pys}]')
        print(f'{wsp}    Pyflakes [{ver_pfl}]')
        print(f'{wsp}      Pylint [{ver_plt}]')
        print(f'{wsp}       PyLRU [{ver_lru}]')
        print(f'{wsp}       Radon [{ver_rad}]')
        print(f'{wsp}     Vulture [{ver_vlt}]')
        print(f'{wsp}       Ctags [{ver_ctg}]')
        print(f'{wsp} -----------')
        print(f'{wsp} OS Platform [{ver_os_}]')

    if verbose:
        cnt = 0
        # print(f'{rs_(21)}\nParse debug variables\n{rs_(21)}')
        print(f'\n* Parse debug variables:')
        # print(rs_(17))
#NOTE, use main scope (possible DEBUG dict update in 'startup.py')
        for cat, val in DEBUG.items():
            if val:
                if not cnt:
                    print('  DEBUG:')
                print('    %-5s = %-3s' % (cat, 'ON  [%i]' % val if val else 'off'))
                cnt += 1
        if not cnt:
            print('  DEBUG: not active')
        # print(f'{rs_(17)}\n')
        print()

    # only run these at startup (and when enabled)
    if mode == 'START':
        # ColourDatabase
        dbg_CLRDB()

        # Scintilla commands
        dbg_SCINTILLA_CMDS()

        # system trace function
        if DEBUG['SYS']: sys.settrace(dbg_TRACEFUNC)


# used in 'open_files' and 'file_close_all'
def dbg_BOOKMARK(when, doc, bmk_lst):
    if DEBUG['BMK']:
        if not bmk_lst:
            return
        cnt = len(bmk_lst)
        if cnt:
            print('\n  %s: Bookmarks (%d) in [%s]:' % (when, cnt, doc.pnm))
            print('    %2s  %5s  %s  %s' % ('Nr', ' Line', '  Col', 'Source'))
            print('    %2s  %5s  %s  %s' % ('--', '-----', '-----', rs_(50)))
        for bmk in bmk_lst:
            bmn = bmk[0]
            lin = bmk[1]
#TODO, bookmark column, source
#         bco = bmk[2]
            src = doc.GetLine(lin - 1).strip()
            print('    %2d  %5d  %s  %s' % (bmn, lin, '    ?', src))


# used in 'open_files' and 'file_close_all'
def dbg_BREAKPOINT(when, doc, bpt_lst):
    if DEBUG['BPT']:
        if not bpt_lst:
            return
        cnt = len(bpt_lst)
        if cnt:
            print('\n  %s: Breakpoints (%d) in [%s]:' % (when, cnt, doc.pnm))
            print('    %2s  %s  %5s  %s' % ('Nr', 'Enabled', ' Line', 'Source'))
            print('    %2s  %s  %5s  %s' % ('--', '-------', '-----', rs_(50)))
        for bpt in bpt_lst:
            bpn = bpt[0]
            ena = bpt[1]
            lin = bpt[2]
#TODO, breakpoint column, source
#         bco = bpt[2]
            src = doc.GetLine(lin - 1).strip()
            print('    %2d  %7s  %5d  %s' % (bpn, ena, lin, src))


# used in '__main__'
def dbg_CLRDB():
    if not DEBUG['CDB']:
        return

#NOTE, avoid error 'wx._core.PyNoAppError: The wx.App object must be created first!'
    app = wx.App()  # app must be created first
    print('  ColourDatabase:')
    print('  %s' % (rs_(15)))
    clrdb = wx.ColourDatabase()
    print('  Example Find(\'blue\')      =', clrdb.Find('blue'))
    print('    \'\'    FindName((0,0,0)) =', clrdb.FindName((0, 0, 0)))
    print()

#NOTE, this takes a LONG time: 255 * 255 * 255 iterations!
#FIX, for better performance use:
    # import wx.lib.colourdb
    # clr_lst = wx.lib.colourdb.getColourList()
    if DEBUG['CDB'] > 1:
        print('  Colours Found:')
        print('  %s' % (rs_(14)))
        for red in range(256):
            for green in range(256):
                for blue in range(256):
                    clr = clrdb.FindName((red, green, blue))
                    if clr:
                        print('  (%3d, %3d, %3d) = %s' % (red, green, blue, clr))
    raise SystemExit


# used in '__main__'
def dbg_CONFIG(cfg):
    if DEBUG['CFG'] > 1:
        # convert option data type: string -> list/boolean/int/float
        print('%2s%s' % ('', rs_(30, '*')))
        print('%2s*****   Config Options   *****' % '')
        print('%2s%s' % ('', rs_(30, '*')))
        for sec in cfg:
            print('\n%2s%s (%d)' % ('', sec, len(list(cfg[sec]))))
            print('%2s%s' % ('', rs_(30)))
            for key in cfg[sec]:
                val = cfg[sec][key]
                typ = d_type(val)
                print('%2s%-30s = <%-5s> %s' % ('', key, typ, val))
        raise SystemExit


# used in 'ContextMenu'
def dbg_CTXTSB(pos, fld_num, rct, sfr_lst):
    nam = '???'
    for key in SBF:
        if SBF[key][0] == fld_num:
            nam = key
    print('  RT click@: %s -> FIELD: [%s] (%d)' % (pos, nam, fld_num))
    print('  StatusBar: %s' % rct)
    print('    Fld MSG: %s' % sfr_lst[SBF['MSG'][0]])
    for key in SBF:
        if key == 'MSG':
            continue
        print(f'        {key}: {sfr_lst[SBF[key][0]]}')

# used in 'BuildToolBar', 'Config.apply', 'CtxToolBar'
def dbg_CTXTTB(when, TBX, cfg):
    if DEBUG['TBR']:
        sec = cfg['ToolBar']
        fnc = sys._getframe(1).f_code.co_name
        when = 'BEFORE' if when == 'B' else ' AFTER'
        print('[%14s] %6s:  SHW_ICO  TBX  %1d, cfg  %1d' % (fnc, when, int(TBX['SHW_ICO'][1]), int(sec['ShowIcons'])))
        print(' %14s  %6s   SHW_TXT       %1d,      %1d' % (' ', ' ',  int(TBX['SHW_TXT'][1]), int(sec['ShowText'])))
        print(' %14s  %6s   LRG_ICO       %1d,      %1d' % (' ', ' ',  int(TBX['LRG_ICO'][1]), int(sec['LargeIcons'])))
        print(' %14s  %6s   LRG_TXT       %1d,      %1d' % (' ', ' ',  int(TBX['LRG_TXT'][1]), int(sec['LargeText'])))
        print(' %14s  %6s   ALN_HOR       %1d,      %1d' % (' ', ' ',  int(TBX['ALN_HOR'][1]), int(sec['AlignHorizontally'])))
        print(' %14s  %6s   LOC_TOP       %1d,      %1d' % (' ', ' ',  int(TBX['LOC_TOP'][1]), int(sec['Top'])))
        print(' %14s  %6s   LOC_LFT       %1d,      %1d' % (' ', ' ',  int(TBX['LOC_LFT'][1]), int(sec['Left'])))
        print(' %14s  %6s   LOC_BOT       %1d,      %1d' % (' ', ' ',  int(TBX['LOC_BOT'][1]), int(sec['Bottom'])))
        print(' %14s  %6s   LOC_RIT       %1d,      %1d' % (' ', ' ',  int(TBX['LOC_RIT'][1]), int(sec['Right'])))
        if 'A' in when:
            print('\n')
        else:
            print('%17s%s%2s%s%2s%s%2s%s%2s%s%2s%s' % (' ', rs_(7, '='), ' ', rs_(7), ' ', rs_(3), ' ', rs_(1), ' ', rs_(3), ' ', rs_(1)))


# used in '_xxx_docstate'
def dbg_DOCSTATE(fnm, docstate):
    if DEBUG['DOC']:
        print('\n%s:' % sys._getframe(1).f_code.co_name)
        # print('  %-32s: [%d] [%-5s] [%d] [%-5s] - [%-5s] [%-5s] [%-5s] [%-5s] - [%-5s] [%-5s] [%-5s]' % (
        print('  %-32s: [%d] [%-5s] [%d] [%-5s] - [%-5s] [%-5s] [%-5s]' % (
                    fnm, docstate[MI['DOC_WRP']],
                         docstate[MI['DOC_EOL']],
                         docstate[MI['DOC_WSP']],
                         docstate[MI['DOC_LCK']],
                         # docstate[MI['MGN_ALL']],
                         # docstate[MI['MGN_NUM']],
                         # docstate[MI['MGN_SYM']],
                         # docstate[MI['MGN_FOL']],
                         docstate[MI['EDG_NON']],
                         docstate[MI['EDG_BCK']],
                         docstate[MI['EDG_LIN']],
                )
        )


# used in several modules
def dbg_EVENT(evt):
    if evt:
        obj = str(evt.EventObject)
        # strip ' object at <0xADDRESS>'
        obj = obj[:obj.find(' object at ')]
        tim = dtm.now().strftime(TIM_FMT)
        out_lst = [tim, evt.Id, evt.EventType, obj, evt.Skipped]
        if hasattr(evt.EventObject, 'FirstVisibleLine'):
            top = 'topline: ' + str(evt.EventObject.FirstVisibleLine + 1)
            out_lst.append(top)
        if evt.EventType != stc.EVT_STC_UPDATEUI:
            print(f'    {out_lst}')
        else:
            pass


# file action/info
def dbg_FILE(txt):
    if not DEBUG['FIL']:
        return
    if DEBUG['FIL'] > 1:
        if txt in ['IN', 'OUT']:
            txt = f'  cwd {txt:>3}: [{cwd()}]'
        print(txt)
    else:
        if txt not in ['IN', 'OUT']:
            print(txt)


# recent file history
def dbg_FILE_HISTORY(rfh_cache):
    for fnm in range(rfh_cache.Count):
        print('%2d = %s' % (fnm, rfh_cache.GetHistoryFile(fnm)))


# used in several modules
#NOTE, 'SetFocus' is FUNCTIONAL code and ALWAYS executed
#FIX, needs better coding...
def dbg_FOCUS(win):
    if win:
        win.SetFocus()  # FUNCTIONAL
    if DEBUG['FCS']:
        # window type is 'doc (editor)'?
        if is_stc(win):
            typ = 'doc'
            txt = win.fnm
        if is_txc(win):
            typ = 'txc'
            txt = win.Name
        else:
            typ = 'WIN'
            txt = 'type: [%s]' % win.Name
        print(f'   {typ} got focus: [{txt}]')


#DONE, rename 'dbg_STYLE' to 'dbg_LANG'
# used in 'LngRead'
def dbg_LANG(lng):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, OVERRIDDEN value is NOT ACCESSIBLE from 'debug' NAMESPACE!!
#     Try: 'deepcopy'
#   Cause: most likely a data type conflict
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # print(f'{DEBUG["LANG"]} in dbg_LANG: {type(DEBUG["LANG"])=} (0)')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    if DEBUG['LNG'] > 1:
        print('%2s%s' % ('', rs_(30, '*')))
        print('%2s*****   Syntax Styling   *****' % '')
        print('%2s%s' % ('', rs_(30, '*')))
        for sec in lng:
            print('\n%2s%s (%d)' % ('', sec, len(list(lng[sec]))))
            print('%2s%s' % ('', rs_(30)))
            for key in lng[sec]:
                val = lng[sec][key]
                typ = d_type(val)
                print('%2s%-30s = <%-5s> %s' % ('', key, typ, val))


# used in 'build_menubar'
def dbg_MENU(menubar):
#INFO, URL=https://stackoverflow.com/questions/24419487/find-index-of-nested-item-in-python
    if DEBUG['MNU'] < 2:
        return

    # recursive menu walk
    def __walk_menu(mnu, lvl=1):
        for mni in mnu.MenuItems:
            acc = mni.Accel.ToString() if mni.Accel else ''
            lbl = mni.ItemLabelText if not mni.IsSeparator() else rs_(25)
            if (sub := mni.SubMenu):
                print('%s%29s %s' % (rs_(4, " ") * lvl, 'SUBMENU:', lbl))
                __walk_menu(sub, lvl=lvl + 1)
            else:
                print('%s%-20s %s' % (rs_(4, " ") * lvl, acc, lbl))

    # start with menubar
    print(rs_(12, '*'))
    print('Menu Listing')
    print(rs_(12, '*'))
    for mnu, lbl in menubar.Menus:
        print(rs_(50))
        print('{} {}'.format('MENU:', lbl))
        print(rs_(50))
        __walk_menu(mnu, lvl=1)
    raise SystemExit


# used in 'file_new'
def dbg_MODEVTMASK(doc):
#     doc.SetModEventMask(stc.STC_LASTSTEPINUNDOREDO)
#INFO, URL=https://stackoverflow.com/questions/20461847/str-startswith-with-a-list-of-strings-to-test-for
    pfx = ('STC_LAST', 'STC_MOD_', 'STC_MODE', 'STC_PERF')
    mod = {}
    for nam in dir(stc):
        if nam.startswith(pfx):
            val = getattr(stc, nam)
            mod[val] = nam  # [4:]
    fmt_str = '  %-24s = %s'
    msk = doc.ModEventMask
    print('GetModEventMask:')
    for k, v in sorted(mod.items(), key=lambda itm: itm[1]):
        print(fmt_str % (v, 'ON' if msk & k else 'off'))
    print(rs_(16))


# used in 'text_modified'
# Lookup editor modification types
def dbg_MOD_TYPE(evt, doc):
    def mod_type_lookup(typ):
        typ_lst = [
            (stc.STC_LASTSTEPINUNDOREDO, 'Last-Undo/Redo'),
            (stc.STC_MOD_BEFOREDELETE,   'B4-Delete'),
            (stc.STC_MOD_BEFOREINSERT,   'B4-Insert'),
            (stc.STC_MOD_CHANGEFOLD,     'ChangeFold'),
            (stc.STC_MOD_CHANGEMARKER,   'ChangeMarker'),
            (stc.STC_MOD_CHANGESTYLE,    'ChangeStyle'),
            (stc.STC_MOD_DELETETEXT,     'DeleteText'),
            (stc.STC_MOD_INSERTTEXT,     'InsertText'),
            (stc.STC_PERFORMED_REDO,     'Redo'),
            (stc.STC_PERFORMED_UNDO,     'Undo'),
            (stc.STC_PERFORMED_USER,     'UserFlag'),
        ]

        dsc = ''
        for flg, txt in typ_lst:
            if flg & typ:
                dsc = f'{dsc}{txt:14} '

        if 'B4-Insert' in dsc:
            dsc += f'{doc.LineFromPosition(evt.Position):4}'
        if 'InsertText' in dsc:
            dsc += f'{doc.LineFromPosition(evt.Position + evt.Length):4}'
        if not dsc:
            dsc = 'UNKNOWN'

        return dsc

    mod = evt.ModificationType
    print(f'mod: {mod:4} = {mod_type_lookup(mod)}')


# used in 'pos_changed', 'goto_caret_pos'
def dbg_POSITION_HISTORY(doc, txt=None):
    # called from Search method
    if not txt:
        print('doc.cph_idx = [%d]' % doc.cph_idx)
        print('        len = [%d]' % len(doc.cph_cache_lst))
        print('        pos = [%d]' % doc.cph_cache_lst[doc.cph_idx])
    else:
        print('%s(%3d): %s' % (txt, doc.cph_idx, '[' + ', '.join(['%4d' % p for p in doc.cph_cache_lst]) + ']'))


# used in 'notebook.py'
def dbg_PTH_CACHE_INFO(nbk):
    if DEBUG['PTH'] < 3:
        return

    def caller():
        return sys._getframe(2).f_code.co_name

    if nbk.sec_pth['Enable']:
        cal = caller()
        sel = nbk.Selection
        szc = nbk.pth_cache.size()
        lnc = len(nbk.pth_cache)
        print(f'{rs_(6)} {cal:>19}: {sel}, cache size: {szc:2}, cache count: {lnc}')
        pprint(list(nbk.pth_cache.items()))
        print()


# used in 'RemoveTrailingWhiteSpace'
def dbg_RMTWS(txt, cpos, clin, clin_len, epos, doc):
    if DEBUG['TWS']:
        print(f'  {txt} cpos=[{cpos:6d}], clin+1=[{clin + 1:4d}], clin_len=[{clin_len:3d}], epos=[{epos:6d}], doc_len=[{doc.TextLength:6d}]')


# used in '__main__'
def dbg_SCINTILLA_CMDS():
    if not DEBUG['SCC']:
        return

    pfx = 'STC_CMD'
    cmd = {}
    for nam in dir(stc):
        if nam.startswith(pfx):
            val = getattr(stc, nam)
            cmd[val] = nam  # [4:]
    fmt_str = '%-31s   %4s'
    fmt_int = '%-31s = %4d'
    print(fmt_str % (rs_(38), TXT_NIL))
    print(fmt_str % ('Scintilla commands: STC_CMD_*', 'Code'))
    print(fmt_str % (rs_(31), rs_(4)))
    idx = 0  # sort by code
    if DEBUG['SCC'] > 1:
        idx = 1  # sort by name
    for k, v in sorted(cmd.items(), key=lambda itm: itm[idx]):
        print(fmt_int % (v, k))
    print(fmt_str % (rs_(38), '\n'))
#INFO, URL=https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used/19747562
#INFO, URL=https://stackoverflow.com/questions/73663/terminating-a-python-script/73673#73673
    raise SystemExit


# used in 'class SidePanel'
def dbg_SIDEPANEL(spn, doc):
    if DEBUG['SPN'] < 2:
        return

    hdr = ''.join(['  ' + t for t in SPT]) + f'  *  [{doc.fnm}]'
    print(hdr)
    print(f'{"  ---" * len(SPT)}      {"-" * len(doc.fnm)}')
    pnl_txt, YES_, NO_, N_A_ = TXT_NIL, '  YES', '   no', '   - '
    for spt in SPT.values():
        pnl_txt += YES_ if spn.cbp_lst[spt.idx].IsShown() else NO_
    print(f'{pnl_txt}      cbp')  # choice book page panel (parent)

    for __, doc in glb.NBK.open_docs():
        ctl_txt = ''
        for spt in SPT.values():
            obj = doc.spt_lst[spt.idx]
            if obj:
                cur = f'* {YES_.strip()}'
                ctl_txt += cur if obj.IsShown() else NO_
            else:
                ctl_txt += N_A_
        shw = '*' if doc.fnm in hdr else ' '
        print(f'{ctl_txt}  {shw}   ctl  {shw} {doc.fnm}')
    print('\n')


# used in 'Startup'
def dbg_SESSION(ssn):
    if DEBUG['SSN'] < 2:
        return

    for sec in ssn:
        print('\n%2s%s (%d)' % ('', sec, len(list(ssn[sec]))))
        print('%2s%s' % ('', rs_(10)))
        for key in ssn[sec]:
            val = ssn[sec][key]
            print('%2s%-10s = %s' % ('', key, val))


# used in 'SyntaxStyling'
def dbg_STYLESPEC(dlg):
    if DEBUG['LNG'] > 1:
        print(f'\n  {dlg.cx1.StringSelection} - [{dlg.lb1.StringSelection}]')
        print('   Style IN  = [%s]' % dlg.stylespec)
        print('     "   CHK = [%s]' % dlg.join_stylespec())
        print('    fore     : [%s]' % dlg.fore)
        print('    back     : [%s]' % dlg.back)
        print('    bold     : [%s]' % dlg.bold)
        print('    italic   : [%s]' % dlg.italic)
        print('    underline: [%s]' % dlg.underline)
        print('    eol      : [%s]' % dlg.eol)
        print('    face     : [%s]' % dlg.face)
        print('    size     : [%s]' % dlg.size)


# used in 'util.py'
def dbg_SYMBOL_INDEX(desc=False, word=False, total=False, count=False, verbose=False):
    if not DEBUG['SIX']:
        return

    for typ in SYMBOL:
        if desc:
            dsc = SYMBOL[typ][0]
            print(f'{dsc}(s):')

        idx = SYMBOL[typ][4]

        for wrd in sorted(idx):
            tot = 0
            if word:
                print(f'  {wrd}')
            for fil in sorted(idx[wrd]):
                flc = 0
                for lin in sorted(idx[wrd][fil]):
                    flc += 1
                    if verbose:
                        print(f'    {fil}:{lin}')
                tot += flc
                if count:
                    print(f'   [{fil:20}: {flc:2d}]')

            if total:
                print(f'   [Total: {tot:3d}]')


# used in 'symbol.py'
def dbg_SYMBOL_POPUP(main=None, wrd=None, total=False, verbose=False):
    if not DEBUG['SPU']:
        return

    if not (main and wrd):
        return

    _plural = lambda d, c: d + 's' if c > 1 else d + ''

    print(f'\n{wrd}')

    for typ in SYMBOL:
        SYMBOL[typ][1] = SYMBOL[typ][2] = 0  # reset symbol/file count

        nam = typ.lower()
        idx = SYMBOL[typ][4]

        if wrd not in idx:
            continue

        __ = idx[wrd]  # convenient short naming (__)
        for fil in sorted(__):
            if verbose:
                for lin in sorted(__[fil]):
                    print(f'{nam} ** {fil}:{lin[0]}')

            SYMBOL[typ][1] += len(__[fil])  # add to symbol count

        SYMBOL[typ][2] += len(__)  # add to file count

    if not total:
        return

    for typ in SYMBOL:
        lst = SYMBOL[typ]  # convenient short naming (lst)
        if lst[1] == 0:
            continue
        s, w = ' ', len(str(lst[2]))  # fill, width
        print(f'  {_plural(*lst[:2]):14}: {lst[1]:4d} {s:{4-w}}({lst[2]:{w}d})')


# used in 'Startup'
def dbg_THEME(thm):
    if DEBUG['THM'] < 2:
        return

    for sec in thm:
        print('\n%2s%s (%d)' % ('', sec, len(list(thm[sec]))))
        print('%2s%s' % ('', rs_(30)))
        for key in thm[sec]:
            if 'Colour' not in key:
                continue
            val = thm[sec][key]
            # typ = d_type(val)
            # print('%2s%-30s = <%-5s> %s' % ('', key, typ, val))
            print('%2s%-30s = %s' % ('', key, val))


# global timer vars
TIMER = {
    '__test__'   : 0,  # scratch test
    'close'      : 0,
#   'draw'       : 0,
    'exit'       : 0,  # not used
    'guess_eol'  : 0,
    'index'      : 0,
    'mark_mch'   : 0,
    'multisel'   : 0,
    'open'       : 0,
    'preferences': 0,
    'pycodestyle': 0,
    'pyflakes'   : 0,
    'pylint'     : 0,
    'search'     : 0,  # search, FIF
    'session'    : 0,
    'setalpha'   : 0,  # setalpha, doc map
    'startup'    : 0,
}


# timing
def dbg_TIMER(name, mode='INIT', src=''):
    if not DEBUG['TMR']:
        return

    # validate arguments
    if not name:
        return
    elif name not in TIMER:
        print(f'  {me_("F")}: <Invalid timer variable: [{name}]>')
        raise SystemExit
    elif mode not in ['INIT', 'STOP']:
        print(f'  {me_("F")}: <Invalid timer mode: [{mode}]>')
        raise SystemExit

    # validate debug level
    if name == 'session':
        if DEBUG['TMR'] < 2:
            return
    elif name == 'setalpha':
    # elif name == 'draw':
        if DEBUG['TMR'] < 3:
            return

    # start/stop timing
    out = f'Timer {mode}: [{name:>8}]'
    if mode == 'INIT':
        TIMER[name] = now_()
        print(f'{out}')
    elif mode == 'STOP':
        TIMER[name] = now_() - TIMER[name]
        print(f'{out} time = [{TIMER[name]:>6} ms] {src}')
        # reset
        TIMER[name] = 0


#######################
# temporary code: TRACE
#######################
    # DO_NOT_TRACEFUNCS = [
    #     '<lambda>',
    #     '__getitem__',
    #     '__init__',
    #     '__new__',
    #     '__setitem__',
    #     '__stop',
    #     '_a_to_u',
    # ]

    # def tracefunc(frm, evt, arg, indent=[0]):
    #     if frm.f_code.co_name in DO_NOT_TRACEFUNCS:
    #         return None
    #     if evt == "call":
    #         indent[0] += 2
    #         print('-' * indent[0] + '> call function', frm.f_code.co_name)
    #     elif evt == 'return':
    #         print('<' + '-" * indent[0], "exit function", frm.f_code.co_name)
    #         indent[0] -= 2
    #     return tracefunc

    # sys.settrace(tracefunc)
#######################
# temporary code: TRACE
#######################


#NOTE, limit output for 'dbg_TRACEFUNC'
#FIX, remove list below by efficient filtering of internal module calls
EXCLUDE_FNC = [
    # '__getattr__',
    # '__getitem__',
    # '__init__',
    # '__new__',
    # '__setitem__',
    # '_a_to_u',
]

INCLUDE_FNC = [
    '__ColumnSorter',
    '_activate_item',
    '_close',
    '_create_columns',
    '_hide',
    '_nothing',
    '_page_panels',
    '_populate_list',
    '_refresh_list',
    '_refresh_title',
    '_update_choice_labels',
    '_update_icons',
    '_virtual_sort',
    'FilterBox',
    'GetColumnSorter',
    'GetListCtrl',
    'GetSortImages',
    'OnGetItemColumnImage',
    'OnGetItemImage',
    'OnGetItemText',
    'page_changed',
    'page_changed',
    'resize',
    'show_list_filter_box',
    'SidePanel',
    'tabctrl_wheel',
    'update_list',
    'update_ui',
]


# used from 'app.MainLoop' onwards
def dbg_TRACEFUNC(frm, evt, arg, indent=[0]):
    # fnc = frm.f_code.co_name
    # # if fnc not in INCLUDE_FNC:
    # if fnc in EXCLUDE_FNC:
    #     return
    # # datetime in millisecs
    # tim = dtm.now().strftime(TIM_FMT + '.%f')[:-3]
    # if evt == 'call':
    #     print(f'{tim} {rs_(indent[0])}[{str(int(indent[0] / 2))}] {fnc} ({sys._getframe(2).f_code.co_name})')
    #     indent[0] += 2
    # elif evt == 'return':
    #     print('{} <{} {} {}'.format(tim, rs_(indent[0]), fnc, '(exit)'))
    #     indent[0] -= 2
    # return dbg_TRACEFUNC

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, How to trace what files, classes and functions are being used
#INFO, URL=https://nedyoxall.github.io/tracing_classes_and_methods_called_from_notebook.html
    file_name = frm.f_code.co_filename
    func_name = frm.f_code.co_name

    # if any(n in file_name for n in ['Python38', 'app.py', 'util.py', 'configobj']):
    if not any(n in file_name for n in ['sidepanel.py']):
        return

    # this is a bit of a hack to get the class out of the locals
    # - it relies on 'self' being used... normally a safe assumption!
    try:
        class_name = frm.f_locals['self'].__class__.__name__
    except (KeyError, AttributeError):
        class_name = "No Class"

    if evt == 'call':
        print("Dirname: " + os.path.dirname(file_name) + \
              " -> Filename: " + os.path.basename(file_name) + \
              " -> Class: " + class_name + \
              " -> Function: " + func_name)

    return dbg_TRACEFUNC
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
SEQ = 0

#FIX, KeyError: 'DEC' when loaded via debug file
DEBUG['DEC'] = 0

#INFO, Attaching a decorator to all functions within a class
#INFO, URL=https://stackoverflow.com/questions/3467526/attaching-a-decorator-to-all-functions-within-a-class
#INFO, URL=https://stackoverflow.com/questions/6307761/how-to-decorate-all-functions-of-a-class-without-typing-it-over-and-over-for-eac
def dbg_method_calls(*d_args, **d_kwargs):
    exclude = d_kwargs.get('exclude', None)
    if not exclude:
        exclude = []
    future_ = d_kwargs.get('future_', None)

    def __class_decorator(cls):

        # if not DEBUG['DEC']:
        #     return cls

        def __method_name(fnc):
            @functools.wraps(fnc)
            def __wrapper(*args, **kwargs):
                global SEQ
                SEQ += 1
                if DEBUG['DEC']: print(f'#[{SEQ:5}]: [{cls.__name__}] -> [{fnc.__name__}]')
                return fnc(*args, **kwargs)

            return __wrapper

        if DEBUG['DEC']: print(f'class: {cls.__name__},  {d_args = },  {d_kwargs = }')
        if DEBUG['DEC']: print(f'  decorating method(s):')

        for att in cls.__dict__:
            val = getattr(cls, att)
            if callable(val) and att not in exclude:
                if DEBUG['DEC']: print(f'    [{att}]')
                setattr(cls, att, __method_name(val))

        if DEBUG['DEC']: print(f'\n')

        return cls

    return __class_decorator


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, an interesting alternative for 'dbg_method_calls'
#INFO, URL=https://www.codementor.io/@dobristoilov/python-class-decorator-part-ii-with-configuration-arguments-rv73o8pjn
# class dbg_class_method_alternative:
#     def __init__(self, *args, **kwargs):
#         pass

#     def __call__(self, fnc):
#         def __wrapper(*args, **kwargs):
#             return fnc(*args, **kwargs)
#         return __wrapper


# @dbg_class_method_alternative(1001,a='some configuration')
# def my_function(*args, **kwargs):
#     print('call my_function', args, kwargs)
#     return 3


# my_function(1,2,3, a="OK")
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def dbg_call_stack(txt=''):
    if DEBUG['STK'] > 1:
        print(f'\n{txt}\n  *** stack depth: {len(stack()):2d} ***')
        for idx in range(3, 0, -1):
            loc = sys._getframe(idx).f_locals
            cls = f'{loc["self"].__class__.__name__}' if 'self' in loc else '<n/a>'
            print(f'{idx:5d} {cls:15s} {sys._getframe(idx).f_code.co_name}')


#FIX, reorganize dbg_callername, dbg_funcname dbg_funcname_app, me_
def dbg_callername():
    if DEBUG['STK'] > 1:
        lvl = len(getouterframes(currentframe()))
        print('%s[%d]->%s' % (rs_(2 * (lvl - 1), " "), lvl, sys._getframe(2).f_code.co_name))


#FIX, reorganize dbg_callername, dbg_funcname dbg_funcname_app, me_
def dbg_funcname(lvl=1):
    if DEBUG['FNM'] >= lvl:
        fnc = sys._getframe(1).f_code.co_name
        print('{}[{}]'.format(rs_(2 * (lvl - 1), " "), fnc))


#FIX, reorganize dbg_callername, dbg_funcname dbg_funcname_app, me_
def dbg_funcname_app():
    if DEBUG['APP']:
        print(f'## App: {sys._getframe(1).f_code.co_name}')


def dbg_help(evt, src=rs_(8, '_')):
    if DEBUG['APP']:
        print(f'{src}    {evt.Id}, {evt.ClassName}, {evt.GetClientObject()}, {evt.EventObject}')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if DEBUG['APP'] > 1: print(f'  HLP: {id(glb.DOC) = } -> {glb.DOC.fnm = }')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



#INFO, URL=http://code.activestate.com/recipes/66062-determining-current-function-name/
#INFO, URL=http://code.activestate.com/recipes/578352-get-full-caller-name-packagemodulefunction/
def dbg_whoami():
    if DEBUG['STK']:
        # get class, function
        frm = sys._getframe(1)
        try:
            cls = frm.f_locals['self'].__class__.__name__
#TODO, check 'except .. as ..' syntax
        except KeyError as AttributeError:
            cls = ''
#         fnm = frm.f_code.co_filename
#         lin = frm.f_code.co_firstlineno
        fnc = frm.f_code.co_name
#         print(fnm, lin, fnc)
        clr = ''
        lvl = len(getouterframes(currentframe()))
        # get up to 3 caller functions
        clr = ''
        if DEBUG['STK'] <= 4:
            for i in range(2, DEBUG['STK'] + 1):
                try:
                    frm = sys._getframe(i)
                    try:
                        cls2 = frm.f_locals['self'].__class__.__name__
#TODO, check 'except .. as ..' syntax
                    except KeyError as AttributeError:
                        cls2 = 'MAIN'
                except ValueError:
                    break
                finally:
                    clr += ' <= (' + cls2 + ').' + frm.f_code.co_name
        return('%s[%d]->(%s).%s%s' % (rs_(2 * (lvl - 1), " "), lvl, cls, fnc, clr))  # instead of print
