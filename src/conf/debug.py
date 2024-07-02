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
import configparser
from datetime import datetime as dtm
import functools
from inspect import getouterframes, currentframe, stack
import os
from pprint import pprint
import re
import sys

#@@@@@@@@@@@@@@@
import anytree  # not used, yet
#@@@@@@@@@@@@@@@
from extern.configobj import ConfigObj, __version__ as cfo_version
from extern.configobj.validate import Validator, __version__ as vld_version
from pathlib import Path
from pubsub import __version__ as pub_version, pub
import pycodestyle
import pyflakes
import pylint
import radon
import vulture
import win32api
import wx
from wx import stc

from app.__version__ import ver_pyt, ver_wxp, ver_stc
from common.date import TIM_FMT, now_
from common.path import cwd
from common.type import is_stc, is_txc
from const import glb
from const.menubar import MI
from const.app import APP, EXE, COMMON_EVENTS, FILTER_EVENTS
from const.common import TXT_NIL
from const.sidepanel import SPT
from const.statusbar import SBF
from const.symbol import SYMBOL
from tool.ctags import ctags_version


#FIX, refactor (also check 'from .debug import DBG, DEBUG')
# global 'DEBUG' dict (used for import)
DEBUG = {}


class Debug(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.load()

    def default(self):
        # DBG('_DBG_', f'{me_()}\n  File = {self.filename}\n')
        self['DEBUG'] = {}
        # self['DEBUG']['_DBG_'] = 0  # 1: Experimental, DeBuG debug...

        # create debug keys w/ zero value
        for key in ('ACC', 'ACP', 'ACT', 'AFE', 'AIB', 'APP', 'BMK', 'BPT',
                    'BRC', 'CDB', 'CFG', 'CPH', 'CTP', 'CTX', 'DCL', 'DCM',
                    'DEC', 'DFC', 'DST', 'EVT', 'FCS', 'FIL', 'FNM', 'FZT',
                    'GEN', 'GLB', 'IDL', 'IND', 'INF', 'KBD', 'LFL', 'LNG',
                    'MAC', 'MCB', 'MDC', 'MNU', 'NBK', 'NIM', 'OAC', 'PDB',
                    'PTH', 'RBM', 'RFH', 'RLR', 'SAS', 'SBR', 'SCC', 'SCH',
                    'SCL', 'SFH', 'SIX', 'SME', 'SPN', 'SPU', 'SSN', 'STK',
                    'TAG', 'TBR', 'THM', 'TLW', 'TMR', 'TRC', 'TSK', 'TWS',
                    'UPD', 'WNM', 'ZOO',):
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
        __['ACT'] = ' 1: ACTion: handler names'
        __['AFE'] = ' 1: Application Filter Events    2: ++ all events (verbose)'
        __['AIB'] = ' 1: AUtoInsert Braces            2: ++ event info'
        __['APP'] = ' 1: APPlication: (context) help  2: ++ status (ready)   3: ++ variables'
        __['BMK'] = ' 1: BookMarK                     2: ++ Get/Set/Update'
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
        __['DST'] = ' 1: DOCument state'
        __['EVT'] = ' 1: most EVenTs                  2: ++ AuiNotebook/Fold/Margin/ContextMenu events'
        __['FCS'] = ' 1: window FoCuS'
        __['FIL'] = ' 1: FILe action                  2: ++ file info'
        __['FNM'] = ' 1: Function NAMe                2: ++ _function_name;  3: ++ frequent calls'
        __['FZT'] = ' 1: FreeZe/Thaw, e.g. \'_avoid_flicker\''
        __['GEN'] = ' 1: GENeric (general)            2: ++ idle/updateui/refresh/scroll events'
        __['GLB'] = ' 1: GLoBal doc ptr (TEST)'
        __['IDL'] = ' 1: IDLe event                   2: ++ event info'
        __['IND'] = ' 1: INDicator: mark matches'
        __['INF'] = ' 1: app start / stop INFo        2: ++ timestamp/PID/versions (verbose)'
        __['KBD'] = ' 1: KeyBoarD: key presses        2: ++ BRIEF keys;      3: ++ event info     4: ++ file.kbd content'
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
        __['PRF'] = ' 1: PReFerences dialog'
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
        __['TAG'] = ' 1: cTAGs'
        __['TBR'] = ' 1: TooLBaR                      2: ++ all items'
        __['THM'] = ' 1: THeME colours                2: ++ file.thm content'
        __['TLW'] = ' 1: Top Level Window attributes (references)'
        __['TMR'] = ' 1: TiMeR: startup/open/close    2: ++ session;         3: ++ DragZone.set_transparency'
        __['TRC'] = ' 1: system TRaCe func'
        __['TSK'] = ' 1: TaSKs (code comment tags)'
        __['TWS'] = ' 1: Trailing WhiteSpace'
        __['UPD'] = ' 1: UPDateui events              2: ++ event info'
        __['WNM'] = ' 1: set Window NaMe, used in WIT'
        __['ZOO'] = ' 1: editor ZOOm/offset'

    def create(self):
        # DBG('_DBG_', f'{me_()}\n  File = {self.filename}\n')

        # get default configuration
        self.default()
        self.save()

    def load(self):
        # DBG('_DBG_', f'{me_()}\n  File = {self.filename}\n')

#HACK, copy our 'self['DEBUG']' to the global 'DEBUG' dict (used for import)
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
    def save(self):
        # DBG('_DBG_', f'{me_()}\n  File = {self.filename}\n')
        self.write()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



# DBG defs
# comparison operators mapping
CMP_OPS = {
    '<' : lambda k, v: k <  v,
    '>' : lambda k, v: k >  v,
    '<=': lambda k, v: k <= v,
    '>=': lambda k, v: k >= v,
    '==': lambda k, v: k == v,
    '!=': lambda k, v: k != v,
}


# regex: conditional expression OR variable only (default: 'VAR>0')
cxp_reg = re.compile(r'^(?P<var>[A-Z]{3}) *((?P<cmp>[<>=!][=]{,1}) *(?P<val>\d{1})){,1}$')

def DBG(cxp, out='', *args, **kwargs):
    """Info based on conditional expression for DEBUG variable.
#TODO,
    [description]

    Args:
        cxp: (str) conditional expression
                format: '<var>[<cmp><val>]'
        out: (str or List[function, List[args]]),
                literal or function([args]) output (default: {''})
        *args: arguments for final print()
        **kwargs: keyword arguments for final print()

    Raises:
        SystemExit: DEBUG variable [{var}] not found
    """

    # parse/validate expression: '<var>[<cmp><val>]'
    nam, org_cxp = 'DBG', cxp
    cxp = cxp.replace(' ', '').upper()  # strip spaces/caps
    if not (mch := cxp_reg.search(cxp)):
        print(f'  {nam}: Invalid conditional expression or variable: [{cxp}]')
        return

    # get/check var name
    if (var := mch['var']) not in DEBUG:
        print(f'  {nam}: DEBUG variable [{var}] not found')
        raise SystemExit

    cmp_opr, val = (mch['cmp'], mch['val']) if mch['cmp'] else ('>', '0')
    cmp_fnc = CMP_OPS.get(cmp_opr)
    cxp = f'{var}{cmp_opr}{val}'  # rebuild from parsed parts
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # res = cmp_fnc(DEBUG[var], int(val))
    # print(f'  {nam}: [{cxp = }]\n  ====\n'
    #       f'        {var = }\n    {cmp_opr = !r:3s}\n        {val = !r:>3s}\n\n'
    #       f'       [{out = }]\n   [{cmp_fnc = }]\n       [{res = }]\n')
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # except NameError as e:
    #     print(f'  {nam}: {e}')
    #     return

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # if cxp != org_cxp:
    #     print(f'  {nam}: * var only expression [{org_cxp}] converted to [{cxp}]')
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    if (res := cmp_fnc(DEBUG[var], int(val))):
        pfx = f'{nam}[{var}={val}]::'
        # pfx = f'@[{var}]<{val}>::'

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: nested f-strings
        # global PRV_DBG_PFX
        # if pfx == PRV_DBG_PFX:
        #     pfx = rs_(len(PRV_DBG_PFX), ' ')
        # else:
        #     PRV_DBG_PFX = pfx
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, Traceback (most recent call last):
#       File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\SPyE.py", line 104, in <module>
#         main()
#       File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\SPyE.py", line 78, in main
#         glb.CFG.apply()
#       File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\conf\config.py", line 1486, in apply
#         create_symbol_index()
#       File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\common\util.py", line 570, in create_symbol_index
#         app.dfn_idx, app.ref_idx, app.imp_idx, app.var_idx, app.wrd_idx, app.qts_idx = sym_idx.create()
#       File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\tool\symbol.py", line 202, in create
#         DBG('SIX>=0', (dbg_SYMBOL_INDEX_SUMMARY, flc))
#       File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\conf\debug.py", line 282, in DBG
#         out = out.replace('\n', f'\n{pfx}')  # prefix multiple lines
#     AttributeError: 'tuple' object has no attribute 'replace'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, reproducable w/ 'DBG('SIX>=0', (dbg_SYMBOL_INDEX_SUMMARY, flc))'
#         out = out.replace('\n', f'\n{pfx}')  # prefix multiple lines
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # when function passed, parse args, exec and return
        if type(out) in (list, tuple):
            fnc, *arg = out
            if (_out := fnc(*arg)):
#NOTE, see FIX above: THIS WORKS
                _out = _out.replace('\n', f'\n{pfx}')  # prefix multiple lines
                print(f'{pfx}{_out}')
            return

        print(f'{pfx}{out}', *args, **kwargs)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # from datetime import datetime as dtm
        # TIM_FMT = '%Y-%m-%d %H:%M:%S.%f'
        # tim = dtm.now().strftime(TIM_FMT)
        # print(f'>>>[{var}]::[{tim}]::{out}', *args, **kwargs)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # print(f'>>>[{var}]:{out}', *args, **kwargs)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # print(f'  {nam}: Cond:[DEBUG[\'{var}\'] {cmp_opr} {val}]'
    #          f' -> {res} ([DEBUG[\'{var}\'] = {DEBUG[var]}')
    # if res:
    #     print(f'  {nam}:  Out:[{out}]', **kwargs)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#NOTE, prevent circular dependency
from common.util import d_type, get_keypress, rs_


# dbf.TIMER defs
TIMERS = {
    '__test__'   : 0,  # scratch test
    'close'      : 0,
#   'draw'       : 0,
    'exit'       : 0,  # not used
    'guess_eol'  : 0,
    'index'      : 0,
    'infobar'    : 0,
    'mark_mch'   : 0,
    'menubar'    : 0,
    'multisel'   : 0,
    'open'       : 0,
    'preferences': 0,
    'pycodestyle': 0,
    'pyflakes'   : 0,
    'pylint'     : 0,
#   -----------------
    'FND_all'    : 0,
    'RPL_all'    : 0,
    'FIF_find'   : 0,
    'FIF_replace': 0,
#   -----------------
    'session'    : 0,
    'setalpha'   : 0,  # setalpha, doc map
    'startup'    : 0,
    'statusbar'  : 0,
    'toolbar'    : 0,
}


# dbf.TRACEFUNC defs
parser = configparser.RawConfigParser(allow_no_value=True)
parser.optionxform = lambda option: option
parser.read('D:/Dev/D/wx/TSN_SPyE/dev/spye/conf/SPyE.trc')

sec = parser._sections
TRC_FIL = sec['Files']
TRC_CLS = sec['Classes']
TRC_FNC = sec['Functions']


class dbf:
    """Collection of debug functions."""

    # used in '__main__'
    def ACTION(act):
        if not DEBUG['ACT']:
            return

        # convert option data type: string -> list/boolean/int/float
        print('%2s%s' % ('', rs_(35, '*')))
        print('%2s*****     Action Handlers     *****' % '')
        print('%2s%s' % ('', rs_(35, '*')))
        for sec in act:
            print('\n%2s%s (%d)' % ('', sec, len(list(act[sec]))))
            print('%2s%s' % ('', rs_(35)))
            for key in act[sec]:
                val = act[sec][key]
                typ = d_type(val)
                print('%2s%-7s = <%-5s> %s' % ('', key, typ, val))
        # raise SystemExit


    def APP():
        out = f'\n  Application variables\n  {rs_(56)}\n  Key   Value\n  {rs_(4)}  {rs_(50)}\n'
        for key, val in APP.items():
            out += f'  {key}  {val}\n'
        return f'{out}\n'


#FIX, needs better coding...
    # used in 'Application.FilterEvent'
    def APP_FILTER_EVENT(app, evt):
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
        if nam == 'CHAR_HOOK':
            kpr_sct, __, __ = get_keypress(evt)
            print(kpr_sct)

        if nam == TXT_NIL:
            # if typ == 10416:
            #     nam = 'STC_DO_DROP'
            # else:
                nam = f'*** _EVT_TYPE_UNKNOWN_: {typ} ***'

        # catch selected or all events (empty FILTER_EVENTS list)
        if FILTER_EVENTS and (nam not in FILTER_EVENTS or f'-{nam}' in FILTER_EVENTS):
            return res

        # strip ' object at <0xADDRESS>' and keep name only
        obj = str(evt.EventObject)
        obj = obj[:obj.find(' object at ')]
        obj = obj[obj.rfind('.') + 1:]

        # discard repeating event names
        out = f'{typ:5d}  {nam:30s}  {obj}'
        if verbose:
            fnm = evt.EventObject.fnm if obj in 'Editor' else TXT_NIL
            out += f'  {fnm}'
            print(f'{out}')
        elif typ != app.prv_evt_typ:
            app.prv_evt_typ = typ
            print(f'{out}')

        # continue processing the event normally
        return res


    # used in '__main__'
    # application start / stop info
    def APP_INFO(mode='START', version=True, verbose=True):
        DBG('APP==3', dbf.APP())

        if DEBUG['INF'] < 2 or DEBUG['TRC']:
            return

        ver_any = anytree.__version__  # not used, yet
        ver_arg = argparse.__version__
        ver_cfo = cfo_version
        ver_vld = f'{vld_version} (Validate)'
        ver_pub = f'{pub_version} (API: v{pub.VERSION_API}, SVN: v{pub.VERSION_SVN})'
        ver_pys = pycodestyle.__version__
        ver_pfl = pyflakes.__version__
        ver_plt = pylint.__version__
        ver_lru = '1.2.0'
        ver_rad = radon.__version__
        ver_vlt = vulture.version.__version__
        ver_pwn = win32api.GetFileVersionInfo(win32api.__file__, '\\')['FileVersionLS'] >> 16
        ver_pwn = f'build {ver_pwn}'
        ver_ctg = ctags_version().split('(')[0]
        ver_os_ = wx.GetOsDescription()

        wsp = rs_(1, ' ')

        out = f"""* [{wx.Now()}]: {mode.title()} {APP["Base"]}
{wsp}  PythonExec [{EXE["PYTHON"]}]
{wsp}  PythonPath [{EXE["PYPATH"]}]
{wsp}     AppPath [{APP["Path"]}]
{wsp}         PID [{os.getpid()}]
    """

        if version:
            out += f"""{wsp} -----------
{wsp}      Python [{ver_pyt}]
{wsp}    wxPython [{ver_wxp}]
{wsp}   Scintilla [{ver_stc}]
{wsp}     anytree [{ver_any}]
{wsp}    ArgParse [{ver_arg}]
{wsp}   ConfigObj [{ver_cfo}]
{wsp}       "     [{ver_vld}]
{wsp}    PyPubSub [{ver_pub}]
{wsp} Pycodestyle [{ver_pys}]
{wsp}    Pyflakes [{ver_pfl}]
{wsp}      Pylint [{ver_plt}]
{wsp}       PyLRU [{ver_lru}]
{wsp}       Radon [{ver_rad}]
{wsp}     Vulture [{ver_vlt}]
{wsp}     PyWin32 [{ver_pwn}]
{wsp}       Ctags [{ver_ctg}]
{wsp} -----------
{wsp} OS Platform [{ver_os_}]
    """

        if verbose:
            cnt = 0
            # out += f'{rs_(21)}\nParse debug variables\n{rs_(21)}\n'
            out += f'\n* Parse debug variables:\n'
            # out += rs_(17\n)
#NOTE, use main scope (possible DEBUG dict update in 'startup.py')
            for cat, val in DEBUG.items():
                if val:
                    if not cnt:
                        out += '  DEBUG:\n'
                    out += (f'    {cat} = {f"ON  [{val}]" if val else "off"}\n')
                    cnt += 1
            if not cnt:
                out += '  DEBUG: not active\n'
            # out += f'{rs_(17)}\n'
            print(out)

        # only run these at startup (and when enabled)
        if mode == 'START':
            # ColourDatabase
            dbf.CLRDB()

            # Scintilla commands
            dbf.SCINTILLA_CMDS()


    # used in 'open_files' and 'file_close_all'
    def BOOKMARK(when, doc, bmk_lst):
        out = TXT_NIL

        if not bmk_lst:
            return out

        if (cnt := len(bmk_lst)):
            out += f'\n  {when}: Bookmarks ({cnt}) in [{doc.pnm}]:\n'
            out += f'    Nr   Line    Col  Source\n'
            out += f'    --  -----  -----  {rs_(50)}\n'
        for bmk in bmk_lst:
            bmn, lin = bmk[:2]
#TODO, bookmark column, #       bco = bmk[2]
            src = doc.GetLine(lin - 1).strip()
            out += f'    {bmn:2}  {lin:5}      ?  {src}\n'

        return out


    # used in 'open_files' and 'file_close_all'
    def BREAKPOINT(when, doc, bpt_lst):
        out = TXT_NIL

        if not bpt_lst:
            return out

        if (cnt := len(bpt_lst)):
            out += f'\n  {when}: Breakpoints ({cnt}) in [{doc.pnm}]:\n'
            out += f'    Nr  Enabled   Line  Source\n'
            out += f'    --  -------  -----  {rs_(50)}\n'
        for bpt in bpt_lst:
            bpn, ena, lin = bpt[:3]
#TODO, breakpoint column, #       bco = bpt[2]
            src = doc.GetLine(lin - 1).strip()
            out += f'    {bpn:2}  {ena:7}  {lin:5}  {src}\n'

        return out


    # used in '__main__'
    def CLRDB():
        if not DEBUG['CDB']:
            return

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
    def CONFIG(cfg):
        if DEBUG['CFG'] < 2:
            return

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
    def CTX_SBR(pos, fld_num, rct, sfr_lst):
        nam = '???'
        for key in SBF:
            if SBF[key].idx == fld_num:
                nam = key
        out = '  RT click@: %s -> FIELD: [%s] (%d)\n' % (pos, nam, fld_num)
        out += '  StatusBar: %s\n' % rct
        out += '    Fld MSG: %s\n' % sfr_lst[SBF.MSG.idx]
        for key in SBF:
            if key == 'MSG':
                continue
            # out += f'        {key}: {sfr_lst[SBF[key].idx]}\n'
            print(f'        {key}')
            print(f'        {SBF[key]}')
            print(f'        {SBF[key].idx}')
            # print(f'        {sfr_lst[SBF[key].idx]}')
            print(f'  {sfr_lst}')
            print()
        return out


    # used in 'BuildToolBar', 'Config.apply', 'CtxToolBar'
    def CTX_TBR(when, TBX, cfg):
        if not DEBUG['TBR']:
            return

        sec = cfg['ToolBar']
        fnc = dbf.caller(2)
        when = 'BEFORE' if when == 'B' else ' AFTER'
        print(f'[{fnc:14s}] {when:6}:  SHW_ICO  TBX  {int(TBX["SHW_ICO"][1])}, cfg  {int(sec["ShowIcons"])}')
        print(f'{" ":26}SHW_TXT       {int(TBX["SHW_TXT"][1])},      {int(sec["ShowText"])}')
        print(f'{" ":26}LRG_ICO       {int(TBX["LRG_ICO"][1])},      {int(sec["LargeIcons"])}')
        print(f'{" ":26}LRG_TXT       {int(TBX["LRG_TXT"][1])},      {int(sec["LargeText"])}')
        print(f'{" ":26}ALN_HOR       {int(TBX["ALN_HOR"][1])},      {int(sec["AlignHorizontally"])}')
        print(f'{" ":26}LOC_TOP       {int(TBX["LOC_TOP"][1])},      {int(sec["Top"])}')
        print(f'{" ":26}LOC_LFT       {int(TBX["LOC_LFT"][1])},      {int(sec["Left"])}')
        print(f'{" ":26}LOC_BOT       {int(TBX["LOC_BOT"][1])},      {int(sec["Bottom"])}')
        print(f'{" ":26}LOC_RIT       {int(TBX["LOC_RIT"][1])},      {int(sec["Right"])}')
        print(f'{" ":17}=======  -------  ---  -  ---  -') if 'B' in when else '\n'


    # used in '_xxx_docstate'
    def DOCSTATE(fnm, docstate):
        if not DEBUG['DST']:
            return

        print('\n%s:' % dbf.caller(2))
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
    def EVENT(evt):
        # if not evt:
        #     print(f'{evt = }{evt = }{evt = }{evt = }{evt = }')
        #     return

        obj_str = str(evt.EventObject)  # strip ' object at <0xADDRESS>'
        obj, tim = obj_str[:obj_str.find(' object at ')], dtm.now().strftime(TIM_FMT)
        out_lst = [tim, evt.Id, evt.EventType, obj, evt.Skipped]
        if hasattr(evt.EventObject, 'FirstVisibleLine'):
            out_lst.append(f'topline: {evt.EventObject.FirstVisibleLine + 1}')
        if evt.EventType != stc.EVT_STC_UPDATEUI:
            return f'    {out_lst}'
        return ''


    # file action/info
    def FILE(txt):
        if not DEBUG['FIL']:
            return

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if DEBUG['FIL'] > 1:
            if txt in {'IN', 'OUT'}:
                txt = f'  cwd {txt:>3}: [{cwd()}]'
            print(txt)
        else:
            if txt not in {'IN', 'OUT'}:
                print(txt)
        # fnd = txt in {'IN', 'OUT'}
        # if DEBUG['FIL'] > 1:
        #     print(txt := f'  cwd {txt:>3}: [{cwd()}]' if fnd else '')
        # else:
        #     print(txt if not fnd else '')
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    # recent file history
    def FILE_HISTORY(rfh_cache):
        out = TXT_NIL
        for fnm in range(rfh_cache.Count):
            out += '%2d = %s\n' % (fnm, rfh_cache.GetHistoryFile(fnm))
        return out

#NOTE, 'SetFocus' is FUNCTIONAL code and ALWAYS executed
#FIX, needs better coding...
    # used in several modules
    def FOCUS(win):
        if win:
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            if win.Name == 'Edit1': DBG('FCS', f'dbg_FOCUS: {win}, {dbf.caller(2)}')
            win.SetFocus()  # FUNCTIONAL
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # EXAMPLE OUTPUT after 'Ctrl+N' (problem lies in 'text_modified')
        # TEST in 'editor.py' ==>> 'self.Bind(stc.EVT_STC_CHARADDED, self.text_modified)'
        #              INSTEAD OF: 'self.Bind(stc.EVT_STC_MODIFIED, self.text_modified)'
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # [Mth] key_pressed: [  N] Ctrl+N
        # <gui.editor.Editor object at 0x000001B2F40FE0D0> update_page_tab
        # <gui.editor.Editor object at 0x000001B2F40FE0D0> update_page_tab
        # <gui.editor.Editor object at 0x000001B2F40FE0D0> _activate_item
        # [Mth] key_pressed: [RETURN] RETURN
        # Global ENTER: [Mod] app.app (file: app.py), [Cls] Application, [Mth] global_char_hook, [Lin] 182
        # <gui.editor.Editor object at 0x000001B2F40FE0D0> text_modified
        # <gui.editor.Editor object at 0x000001B2F40FE0D0> update_page_tab
        # <gui.editor.Editor object at 0x000001B2F40D9AF0> text_modified
        # <gui.editor.Editor object at 0x000001B2F40D9AF0> update_page_tab
        # <gui.editor.Editor object at 0x000001B2F40FE0D0> text_modified
        # <gui.editor.Editor object at 0x000001B2F40FE0D0> update_page_tab
        # <gui.editor.Editor object at 0x000001B2F40D9AF0> text_modified
        # <gui.editor.Editor object at 0x000001B2F40D9AF0> update_page_tab
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if not DEBUG['FCS']:
            return

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


    # used in '__main__'
    def KEYBOARD(kbd):
        if DEBUG['KBD'] < 4:
            return

        # convert option data type: string -> list/boolean/int/float
        print('%2s%s' % ('', rs_(35, '*')))
        print('%2s*****   Keyboard Shortcuts    *****' % '')
        print('%2s%s' % ('', rs_(35, '*')))
        for sec in kbd:
            print('\n%2s%s (%d)' % ('', sec, len(list(kbd[sec]))))
            print('%2s%s' % ('', rs_(35)))
            for key in kbd[sec]:
                val = kbd[sec][key]
                typ = d_type(val)
                print('%2s%-7s = <%-5s> %s' % ('', key, typ, val))
        raise SystemExit


#DONE, rename 'dbg_STYLE' to 'dbg_LANG'
    # used in 'LngRead'
    def LANG(lng):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, OVERRIDDEN value is NOT ACCESSIBLE from 'debug' NAMESPACE!!
#     Try: 'deepcopy'
#   Cause: most likely a data type conflict
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # print(f'{DEBUG["LANG"]} in dbf.LANG: {type(DEBUG["LANG"])=} (0)')
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if DEBUG['LNG'] < 2:
            return

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
    def MENU(menubar):
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
#FIX, 'AttributeError: 'Menu' object has no attribute 'Menus''
        for mnu, lbl in menubar.Menus:
            print(rs_(50))
            print('{} {}'.format('MENU:', lbl))
            print(rs_(50))
            __walk_menu(mnu, lvl=1)
        raise SystemExit


    # used in 'text_modified'
    # Lookup editor modification types
    def MOD_TYPE(evt, doc):
        def __lookup(typ):
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

            if not dsc:
                dsc = 'UNKNOWN'
            if 'B4-Insert' in dsc:
                dsc += f'{doc.LineFromPosition(evt.Position):4}'
            if 'InsertText' in dsc:
                dsc += f'{doc.LineFromPosition(evt.Position + evt.Length):4}'

            return dsc

        mod = evt.ModificationType
        return f'mod: {mod:4} = {__lookup(mod)}'


    # used in 'file_new'
    def MODEVENTMASK(doc):
    #     doc.SetModEventMask(stc.STC_LASTSTEPINUNDOREDO)
#INFO, URL=https://stackoverflow.com/questions/20461847/str-startswith-with-a-list-of-strings-to-test-for
        pfx = ('STC_LAST', 'STC_MOD_', 'STC_MODE', 'STC_PERF')
        mod = {}
        for nam in dir(stc):
            if nam.startswith(pfx):
                val = getattr(stc, nam)
                mod[val] = nam  # [4:]
        fmt_str = '  %-24s = %s\n'
        msk = doc.ModEventMask
        out = 'GetModEventMask:\n'
        for k, v in sorted(mod.items(), key=lambda itm: itm[1]):
            out += fmt_str % (v, 'ON' if msk & k else '   off')
        return f'{out}{rs_(16)}'


    # used in 'pos_changed', 'goto_caret_pos'
    def POSITION_HISTORY(doc, txt=None):
        out = TXT_NIL
        if not txt:
            out += f'doc.cph_idx = [{doc.cph_idx}]\n'
            out += f'        len = [{len(doc.cph_cache_lst)}]\n'
            out += f'        pos = [{doc.cph_cache_lst[doc.cph_idx]}]'
        else:
            out += f'{txt}({doc.cph_idx:3}): [{"<SEP>".join(f"({s:6}, {e:6})" for s, e in doc.cph_cache_lst)}]'
            out = out.replace('<SEP>', f',\n{" ":19}')
        return out


    # used in 'notebook.py'
    def PTH_CACHE_INFO(nbk):
        if DEBUG['PTH'] < 3:
            return

        if nbk.sec_pth['Enable']:
            fnc = dbf.caller(1)
            sel = nbk.Selection
            szc = nbk.pth_cache.size()
            lnc = len(nbk.pth_cache)
            print(f'{rs_(6)} {fnc:>19}: {sel}, cache size: {szc:2}, cache count: {lnc}')
            pprint(list(nbk.pth_cache.items()))
            print()


    # used in 'RemoveTrailingWhiteSpace'
    def RMTWS(txt, cpos, clin, clin_len, epos, doc):
        DBG('TWS', f'  {txt} cpos=[{cpos:6d}], clin+1=[{clin + 1:4d}], clin_len=[{clin_len:3d}], epos=[{epos:6d}], doc_len=[{doc.TextLength:6d}]')


    # used in 'searchpanel'
    def SEARCH_WHERE(whr_dct):
        # if not DEBUG['SCH']:
        #     return

        for key, val in whr_dct.items():
            print(f'  {key}: [ {val.dsc:14} ] = {val.lst}')


    # used in '__main__'
    def SCINTILLA_CMDS():
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


    # used in 'Startup'
    def SESSION(ssn):
        if DEBUG['SSN'] < 2:
            return

        for sec in ssn:
            print('\n%2s%s (%d)' % ('', sec, len(list(ssn[sec]))))
            print('%2s%s' % ('', rs_(10)))
            for key in ssn[sec]:
                val = ssn[sec][key]
                print('%2s%-10s = %s' % ('', key, val))


    # used in 'class SidePanel'
    def SIDEPANEL(spn, doc):
        if DEBUG['SPN'] < 2:
            return

        hdr = ''.join([f'  {t}' for t in SPT]) + f'  *  [{doc.fnm}]'
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


    # used in 'SyntaxStyling'
    def STYLESPEC(dlg):
        if DEBUG['LNG'] < 2:
            return

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
    def SYMBOL_INDEX_COUNTS(desc=False, word=False, total=False, count=False, verbose=False):
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
    def SYMBOL_INDEX_MATCHES(pnm, lin, lnc, nam, dif, cnt, prv_pos, elm, col):
        out = TXT_NIL
        # control (white)space between matches
        cnt += 1
        pos = col - dif + 15

        if cnt == 1:
            out += f'[{nam}]::[{elm}]::[{pnm}]\n'
            out += f'  [{lnc:4d}]::[{lin=}]\n'
            wsp = pos
        else:
            wsp = pos - prv_pos

        # mark matches with '^' chars
        out += f'{" "*(wsp)}{"^"*len(elm)}\n'
        prv_pos = pos + len(elm)
        return out


    # used in 'symbol.py'
    def SYMBOL_INDEX_SUMMARY(flc):
        # summary/counts
        out =  f'\n  Indexed Files: {flc}\n'
        out += f'\n  Symbol Type      Total   Unique\n'
        out += f'  {rs_(13)}   {rs_(6)}   {rs_(6)}\n'

        for typ in SYMBOL:
            dsc = SYMBOL[typ][0]
            tot = SYMBOL[typ][3]
            unq = len(SYMBOL[typ][4])
            # sts = 'Excluded' if not glb.CFG['SymbolIndex'][f'Include{typ}'] else 'Active'
            # out += f'  {dsc:13}   {tot:6d}    {unq:5d}   {sts}'
            out += f'  {dsc:13}   {tot:6d}    {unq:5d}\n'

        out += f'\n'
        return out


    # used in 'symbol.py'
    def SYMBOL_POPUP(main=None, wrd=None, total=False, verbose=False):
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
            if not lst[1]:
                continue
            s, w = ' ', len(str(lst[2]))  # fill, width
            print(f'  {_plural(*lst[:2]):14}: {lst[1]:4d} {s:{4-w}}({lst[2]:{w}d})')


    # used in 'Startup'
    def THEME(thm):
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


    # timing
    def TIMER(nam, mode='INIT', src=''):
        if not DEBUG['TMR']:
            return

        # validate arguments
        if not nam:
            return
        elif nam not in TIMERS:
            print(f'  {me_("F")}: <Invalid timer variable: [{nam}]>')
            raise SystemExit
        elif mode not in {'INIT', 'STOP'}:
            print(f'  {me_("F")}: <Invalid timer mode: [{mode}]>')
            raise SystemExit

        # validate debug level
        if nam == 'session':
            if DEBUG['TMR'] < 2:
                return
        elif nam == 'setalpha':
        # elif nam == 'draw':
            if DEBUG['TMR'] < 3:
                return

        # start/stop timing
        out = f'Timer {mode}: [{nam:>8}]'
        if mode == 'INIT':
            TIMERS[nam] = now_()
            print(f'{out}')
        elif mode == 'STOP':
            TIMERS[nam] = now_() - TIMERS[nam]
            print(f'{out} time = [{TIMERS[nam]:>6} ms] {src}')
            # reset
            TIMERS[nam] = 0


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def TRACEFUNC(frm, evt, arg, pkg_nam='dedupe'):
        """ Function to track the methods, classes and filenames that are called from Jupyter notebook.
            Will need some tweaking for use outside of notebook environment.
            Useful for tracing what functions have been used in complex packages.
            Inspired by: http://stackoverflow.com/questions/8315389/how-do-i-print-functions-as-they-are-called

            Inputs: - frm, evt, arg -> See the docs: https://docs.python.org/3/library/sys.html#sys.settrace
                    - pkg_nam -> string of the package you want to track
                                 (without this get a load of notebook faff printed out too)

            Outputs: - prints to screen the filename, class and methods called by running cell.

            Usage: Turn on -> sys.settrace(tracefunc)
                   Turn off -> sys.settrace(None)
        """
        # TRC_FIL = glb.TRC['Files']
        # TRC_CLS = glb.TRC['Classes']
        # TRC_FNC = glb.TRC['Functions']

        frm.f_trace_lines = False  # disable 'line' events

        cfn = frm.f_code.co_filename
        fnm = os.path.basename(cfn)
        dnm = os.path.dirname(cfn)
        fnc = frm.f_code.co_name
        lin = frm.f_lineno

        # this is a bit of a hack to get the class out of the locals
        # - it relies on 'self' being used... normally a safe assumption!
        try:
            cls = frm.f_locals['self'].__class__.__name__
        except (KeyError, AttributeError) as e:
            cls = 'n/a'

        # to trace or not to ..
        evt_cxp = evt == 'call' and '<module>' not in fnc
        fil_cxp = not TRC_FIL or fnm in TRC_FIL
        cls_cxp = not TRC_CLS or cls in TRC_CLS
        fnc_cxp = not TRC_FNC or fnc in TRC_FNC

        if all([evt_cxp, fil_cxp, cls_cxp, fnc_cxp]):
            print(f'[TRC]::[Dir] {dnm}, [Fil] {fnm}, [Cls] {cls}, [Fnc] {fnc}, [Lin] {lin}')
            # print(f'      called from -> {dbf.caller(2)}\n')
            # breakpoint()
        return dbf.TRACEFUNC


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


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
        #         print(f'{"-" * indent[0]}> call function {frm.f_code.co_name}')
        #     elif evt == 'return':
        #         print(f'<{"-" * indent[0]} exit function {frm.f_code.co_name}')
        #         indent[0] -= 2
        #     return tracefunc

        # sys.settrace(tracefunc)
    #######################
    # temporary code: TRACE
    #######################


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #NOTE, limit output for '__OLD_dbg_TRACEFUNC'
# #FIX, remove list below by efficient filtering of internal module calls
    # EXCLUDE_FNC = [
    #     # '__getattr__',
    #     # '__getitem__',
    #     # '__init__',
    #     # '__new__',
    #     # '__setitem__',
    #     # '_a_to_u',
    # ]

    # INCLUDE_FNC = [
    #     '__ColumnSorter',
    #     '_activate_item',
    #     '_close',
    #     '_create_columns',
    #     '_hide',
    #     '_nothing',
    #     '_page_panels',
    #     '_populate_list',
    #     '_refresh_list',
    #     '_refresh_title',
    #     '_update_choice_labels',
    #     '_update_tool_icons',
    #     '_virtual_sort',
    #     'FilterBox',
    #     'GetColumnSorter',
    #     'GetListCtrl',
    #     'GetSortImages',
    #     'OnGetItemColumnImage',
    #     'OnGetItemImage',
    #     'OnGetItemText',
    #     'page_changed',
    #     'page_changed',
    #     'resize',
    #     'show_list_filter_box',
    #     'SidePanel',
    #     'tabctrl_wheel',
    #     'update',
    #     'update_ui',
    # ]


    # # used from 'app.MainLoop' onwards
    # def __OLD_dbg_TRACEFUNC(frm, evt, arg, indent=[0]):
    #     # fnc = frm.f_code.co_name
    #     # # if fnc not in INCLUDE_FNC:
    #     # if fnc in EXCLUDE_FNC:
    #     #     return
    #     # # datetime in millisecs
    #     # tim = dtm.now().strftime(TIM_FMT + '.%f')[:-3]
    #     # if evt == 'call':
    #     #     print(f'{tim} {rs_(indent[0])}[{str(int(indent[0] / 2))}] {fnc} ({dbf.caller(2)})')
    #     #     indent[0] += 2
    #     # elif evt == 'return':
    #     #     print('{} <{} {} {}'.format(tim, rs_(indent[0]), fnc, '(exit)'))
    #     #     indent[0] -= 2
    #     # return __OLD_dbg_TRACEFUNC

    # #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #INFO, How to trace what files, classes and functions are being used
# #INFO, URL=https://nedyoxall.github.io/tracing_classes_and_methods_called_from_notebook.html
    #     file_name = frm.f_code.co_filename
    #     func_name = frm.f_code.co_name

    #     # if any(n in file_name for n in {'Python38', 'app.py', 'util.py', 'configobj'}):
    #     if not any(n in file_name for n in {'sidepanel.py'}):
    #         return

    #     # this is a bit of a hack to get the class out of the locals
    #     # - it relies on 'self' being used... normally a safe assumption!
    #     try:
    #         class_name = frm.f_locals['self'].__class__.__name__
    #     except (KeyError, AttributeError):
    #         class_name = "No Class"

    #     if evt == 'call':
    #         print("Dirname: " + os.path.dirname(file_name) + \
    #               " -> Filename: " + os.path.basename(file_name) + \
    #               " -> Class: " + class_name + \
    #               " -> Function: " + func_name)

    #     return __OLD_dbg_TRACEFUNC
    # #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#FIX: get window name under mouse cursor
    def WIN_UNDER_CURSOR(app, evt):
        if not hasattr(app, 'prv_win_nam'):
            app.prv_win_nam = None

        _gks = wx.GetKeyState
        ctrl, alt = _gks(wx.WXK_CONTROL), _gks(wx.WXK_ALT)
        if not (ctrl and alt):
            return

        win, pos = wx.FindWindowAtPointer()
        nam = str(win)
        start = nam.rfind('.') + 1
        end = nam.find(' object at ')
        nam = nam[start:end]

        if nam == app.prv_win_nam:
            return

        app.prv_win_nam = nam
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


    def call_stack(txt=''):
        if DEBUG['STK'] > 1:
            print(f'\n{txt}\n  *** stack depth: {len(stack()):2d} ***')
            for idx in range(3, 0, -1):
                loc = sys._getframe(idx).f_locals
                cls = f'{loc["self"].__class__.__name__}' if 'self' in loc else '<n/a>'
                print(f'{idx:5d} {cls:15s} {dbf.caller(idx)}')


    def caller(depth=1):
        return sys._getframe(depth).f_code.co_name


    # #FIX, reorganize dbg_callername, dbg_funcname, me_
    # def dbg_callername():
    #     if DEBUG['STK'] > 1:
    #         lvl = len(getouterframes(currentframe()))
    #         print('%s[%d]->%s' % (rs_(2 * (lvl - 1), " "), lvl, dbf.caller(2)))


    # #FIX, reorganize dbg_callername, dbg_funcname, me_
    # def dbg_funcname(lvl=1):
    #     if DEBUG['FNM'] >= lvl:
    #         print('{}[{}]'.format(rs_(2 * (lvl - 1), " "), dbf.caller(2)))


    # #FIX, reorganize dbg_callername, dbg_funcname, me_
    # def funcname(lvl=1):
    #     return dbf.caller(lvl)


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def help_event(evt, src=rs_(8, '_')):
        DBG('APP==1', f'{src}    {evt.Id}, {evt.ClassName}, {evt.GetClientObject()}, {evt.EventObject}')
        DBG('APP==1', f'  HLP: {id(glb.DOC) = } -> {glb.DOC.fnm = }')
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    SEQ = 0

    #FIX, KeyError: 'DEC' when loaded via debug file
    DEBUG['DEC'] = 0

    #INFO, Attaching a decorator to all functions within a class
    #INFO, URL=https://stackoverflow.com/questions/3467526/attaching-a-decorator-to-all-functions-within-a-class
    #INFO, URL=https://stackoverflow.com/questions/6307761/how-to-decorate-all-functions-of-a-class-without-typing-it-over-and-over-for-eac
    def method_calls(*d_args, **d_kwargs):
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
                    DBG('DEC', f'#[{SEQ:5}]: [{cls.__name__}] -> [{fnc.__name__}]')
                    return fnc(*args, **kwargs)

                return __wrapper

            DBG('DEC', f'class: {cls.__name__},  {d_args = },  {d_kwargs = }')
            DBG('DEC', f'  decorating method(s):')

            for att in cls.__dict__:
                val = getattr(cls, att)
                if callable(val) and att not in exclude:
                    DBG('DEC', f'    [{att}]')
                    setattr(cls, att, __method_name(val))

            DBG('DEC', f'\n')

            return cls

        return __class_decorator


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #INFO, an interesting alternative for 'dbf.method_calls'
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
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #     from wx import stc
    #     import sys
    #     if evt.EventType == stc.EVT_STC_MODIFIED.typeId:
    #         print(f'\n  *** stack depth: ***')

    # #INFO, Print current call stack from a method in code
    # #INFO, URL=https://stackoverflow.com/questions/1156023/print-current-call-stack-from-a-method-in-code
    #         import inspect

    #         limit=None
    #         start=0

    #         # The call stack.
    #         stack = inspect.stack()

    #         # The penultimate frame is the caller to this function.
    #         here = stack[1]

    #         # The index of the first frame to print.
    #         begin = start + 2

    #         # The index of the last frame to print.
    #         end = len(stack)
    #         # if limit:
    #             # end = min(begin + limit, len(stack))
    #         # else:

    #         # Print the stack to the logger.
    #         file, line, func = here[1:4]
    #         print(file, line, func, start + 2, end - 1, len(stack) - 1)
    #         # Print the next frames up to the limit.
    #         for frame in stack[begin:end]:
    #             file, line, func = frame[1:4]
    #             print(file, line, func)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    #INFO, URL=http://code.activestate.com/recipes/66062-determining-current-function-name/
    #INFO, URL=http://code.activestate.com/recipes/578352-get-full-caller-name-packagemodulefunction/
    def whoami():
        if not DEBUG['STK']:
            return

        # get class, function
        frm = sys._getframe(1)

        try:
            cls = frm.f_locals['self'].__class__.__name__
    #TODO, check 'except .. as ..' syntax
        except KeyError as AttributeError:
            cls = ''

        # fnm = frm.f_code.co_filename
        # lin = frm.f_code.co_firstlineno
        fnc = frm.f_code.co_name
        # print(fnm, lin, fnc)
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
                except ValueError as e:
                    break
                finally:
                    clr += f' <= ({cls2}).{frm.f_code.co_name}'

        return('%s[%d]->(%s).%s%s' % (rs_(2 * (lvl - 1), " "), lvl, cls, fnc, clr))  # instead of print


#@@@@@@@@@@@@@@@@@@@
# END of 'class dbf'
#@@@@@@@@@@@@@@@@@@@


#FIX, reorganize dbg_callername, dbg_funcname, me_
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
