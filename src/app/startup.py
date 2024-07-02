#!/usr/bin/python

import argparse
# from copy import deepcopy
import os
from pathlib import Path
from pprint import pprint
from shutil import copyfile, which
import sys

from .__version__ import (
    __credits__ as crd, __version__ as ver, ver_pyt, ver_wxp, ver_stc
 )
from common.type import is_int
from common.util import rs_
from conf.config import Config
from conf.debug import Debug, DBG, DEBUG, dbf, me_
from data.license import __license__
from conf.action import Action
from conf.keyboard import Keyboard
from conf.lang import Language
from conf.menu import Menu
from conf.recent_file_history import RecentFileHistory
from conf.search_field_history import SearchFieldHistory
from conf.session import Session
from conf.theme import Theme
from conf.trace import Trace
from const import glb
from const.app import APP, ENV_VARS, LOC, EXE
from tool.ctags import ctags_version

import wx
from wx import stc


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: profiler, PERFORMANCE TESTING
#INFO, URL=https://github.com/bpabel/profiler
# from extern import profiler
# profiler.profiler('.\\log\\profiler.log').start(True)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, OVERRIDDEN value is NOT ACCESSIBLE from 'debug' NAMESPACE!!
#     Try: 'deepcopy'
#   Cause: most likely a data type conflict
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def startup():
    # set 'DEBUG' and 'glb' globals
    read_debug_settings()

    dbf.TIMER('startup')
    dbf.TIMER('session')

    DBG('TRC', (sys.settrace, dbf.TRACEFUNC))

    check_dependencies()

    parse_config_files()

    parse_environment_vars()

    parse_commandline_args()

    glb.PLG = parse_plugins()

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # # generate Environment keys from debug/config/language/theme objects
    # for typ in [DEBUG, glb.CFG, glb.LNG, glb.THM]:
    #     for k, v in typ.items():
    #         pprint(f'{k:5} = [{v}]')
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    return


def read_debug_settings():
    fil = LOC['DBG']['FIL']
    Debug(fil)  # this sets 'DEBUG' global var

    return


def check_dependencies():
    DBG('INF', f'* Check application dependencies:')

    for exe in (EXE[e] for e in ('CTAGS', 'RADON', 'PYCODESTYLE', 'PYFLAKES', 'PYLINT', 'VULTURE')):
        DBG('INF', f'  * {exe:11}:', end='')
        if not (pnm := which(exe)):
            print(f'[{exe}] executable not found')
            raise SystemExit
        elif exe in EXE['CTAGS']:
            dsc = 'Universal Ctags'
            if dsc not in (ver := ctags_version()):
                print(f' [{dsc}] not found in version string of [{pnm}]\n')
                print(f' version string:\n[{ver.strip()}]')
                raise SystemExit
        DBG('INF', f' OK')

    return


def parse_config_files():
    DBG('INF', f'* Read debug settings:')
    DBG('INF', f'  * Debug: OK')
    DBG('INF', f'    using debug file: [{LOC["DBG"]["FIL"]}]')

    DBG('INF', f'* Parse configuration files:')

    # recent file history
    DBG('INF', f'  * Recent file history: OK')
    fil = LOC['RFH']['FIL']
    DBG('INF', f'    using recent file history file: [{fil}]\n')
    glb.RFH = RecentFileHistory(fil)
#FIX, call and func args in 'debug.py'; now only handling 'rfh_cache'
    # dbf.FILE_HISTORY(???)

    # search field history
    DBG('INF', f'  * Search field history: OK')
    fil = LOC['SFH']['FIL']
    DBG('INF', f'    using search field history file: [{fil}]\n')
    glb.SFH = SearchFieldHistory(fil)
#FIX, implement new function in 'debug.py'
    # dbf.SEARCH_HISTORY(???)

    # session file
    DBG('INF', f'  * Session: OK')
    fil = LOC['SSN']['FIL']
    DBG('INF', f'    using session file: [{fil}]\n')
    glb.SSN = Session(fil)
    dbf.SESSION(glb.SSN)

    # config (plus spec) file
    DBG('INF', f'  * Config:')
    fil = LOC['CFG']['FIL']
    csp = Path(f'{fil}_spec')
    DBG('INF', f'    using config     file: [{fil}]')
    DBG('INF', f'      and configspec file: [{csp}]')

    # missing spec file
    if not Path(csp).is_file():
        err = f'{me_("F")}: configspec file not found: [{csp}]'
        raise OSError(err)

    glb.CFG = Config(infile=fil, configspec=csp)  #, unrepr=True)
    dbf.CONFIG(glb.CFG)

    # keyboard file
    DBG('INF', f'  * Keyboard: OK')
    fil = LOC['KBD']['FIL']
    DBG('INF', f'    using keyboard file: [{fil}]\n')
    glb.KBD = Keyboard(fil)
#FIX, implement new function in 'debug.py'
    dbf.KEYBOARD(glb.KBD)

    # action file
    DBG('INF', f'  * Action: OK')
    fil = LOC['ACT']['FIL']
    DBG('INF', f'    using action file: [{fil}]\n')
    glb.ACT = Action(fil)
#FIX, implement new function in 'debug.py'
    dbf.ACTION(glb.ACT)

    # language file
    DBG('INF', f'  * Language: OK')
    fil = LOC['LNG']['FIL']
    DBG('INF', f'    using language file: [{fil}]\n')
    glb.LNG = Language(fil)
    dbf.LANG(glb.LNG)

    # menu file
    DBG('INF', f'  * Menu: OK')
    fil = LOC['MNU']['FIL']
    DBG('INF', f'    using menu file: [{fil}]\n')
    glb.MNU = Menu(fil)
    dbf.MENU(glb.MNU)

    # theme file
    DBG('INF', f'  * Theme: OK')
    fil = LOC['THM']['FIL']
    DBG('INF', f'    using theme file: [{fil}]\n')
    glb.THM = Theme(fil)
    dbf.THEME(glb.THM)

    # trace file
    DBG('INF', f'  * Trace: OK')
    fil = LOC['TRC']['FIL']
    DBG('INF', f'    using trace file: [{fil}]\n')
    # glb.TRC = Trace(fil)
    # dbf.TRACEFUNC(glb.TRC)

    # create '.default' file (for    ALL types, if NOT exist)
    # create '.bak'     file (for CONFIG type,        ALWAYS)
    for typ in {'DBG', 'CFG', 'LNG', 'MNU', 'THM'}:  # 'SSN'
        loc = LOC[typ]
        if not Path(loc['DFT']).is_file():
            DBG('INF', f'* Create {typ} default file: [{loc["DFT"]}]\n')
            copyfile(loc['FIL'], loc['DFT'])
        if typ == 'CFG':
            DBG('INF', f'* Create {typ} backup file: [{loc["BAK"]}]\n')
            copyfile(loc['FIL'], loc['BAK'])

    return


def parse_environment_vars():
    # Environment variables (ALWAYS override their debug/config/language equals)
    DBG('INF', f'* Parse environment variables:')
    cnt = 0
    pfx = APP['Base'].upper()

    # walk env variables
    for var in os.environ:
        # discard unsupported application prefix
        if not var.startswith(pfx):
            continue

        # get value
        val = os.environ[var]

#FIX, merge unsupported variable check
        # discard unsupported variable
        if var not in ENV_VARS:
            DBG('INF', f'    reject: [{var}]={val}')
            DBG('INF', f'  {rs_(9)}')
            continue

        # discard unsupported variable
        if not any(s in var for s in ('_DBG_', '_CFG_', '_LNG_')):
            DBG('INF', f'      skip: [{var}]={val}')
            DBG('INF', f'  {rs_(9)}')
            continue

        DBG('INF', f'  {rs_(9)}')

#DONE, implement for 'debug/config/language' variable
        typ = 'debug' if 'DBG' in var else 'config' if 'CFG' in var else 'language' if 'LNG' in var else '**unknown**'
        DBG('INF', f'    accept: [{var}] {typ} environment variable')
        ENV_VARS[var] = val

        # override debug/config/language
        txt = '  override:'
        if 'DBG' in var:
            nam = var.split(f'_DBG_')[-1]
            if is_int(val):
                DBG('INF', f'{txt} [{nam}={DEBUG[nam]}] in [{LOC["DBG"]["FIL"]}]')
                DEBUG[nam] = int(val)
            else:
                # we should NEVER get here
                err = f'expected [int], got [{type(val)}] for [{var}={val}]'
                raise TypeError(err)
        elif 'CFG' in var:
            nam = var.split(f'_CFG_')[-1]
            DBG('INF', f'{txt} [{nam}={CFG[nam]}] in [{LOC["CFG"]["FIL"]}]')
            CFG[nam] = val
        elif 'LNG' in var:
            nam = var.split(f'_LNG_')[-1]
            DBG('INF', f'{txt} [{nam}={LNG[nam]}] in [{LOC["LNG"]["FIL"]}]')
            LNG[nam] = val
        else:
            # we should NEVER get here
            err = f'unknown type in name [{var}], must contain: _[DBG|CFG|LNG]_'
            raise AssertionError(err)

        cnt += 1
        DBG('INF', f'      with: [{nam}={val}]')

        DBG('INF', f'  {rs_(9)}')

    if not cnt:
        DBG('INF', f'  none set\n')
    else:
        DBG('INF')

    return


    ###################################################################################################
    # Attempt to create generic code fragment
    ###################################################################################################
    # typ = DBG CFG LNG
    # if any('_DBG_', '_CFG_', '_LNG_') in var:
    #     pass
    # typ = 'DBG' if '_DBG_' in var else 'CFG' if '_CFG_' in var else 'LNG' if '_LNG_' in var else None
    # if not typ:
    #     print(f'Environment type')
    #     continue
    # else:
    #     print(var)
    # nam = var.split(f'_{typ}_')[-1]
    # print(f'  Override: {nam}=[{DEBUG[nam]}] in [{LOC[typ]["FIL"]}]')
    # DEBUG[nam] = val
    ###################################################################################################


def parse_commandline_args():
    # command line arguments
    DBG('INF', f'* Parse command line arguments(TODO):')

    class BlankLinesHelpFormatter(argparse.HelpFormatter):
        def __split_lines(self, text, width):
            return super().__split_lines(text, width) + ['']

    # # add empty line if help ends with \n
    #     def __split_lines(self, text, width):
    #         lines = super().__split_lines(text, width)
    #         if text.endswith('\n'):
    #             lines += ['']
    #         return lines

    def add_arguments(parser):
        add = parser.add_argument  # convenient short naming (add)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: argument parsing
        add('-s',
            action='store',
            dest='simple_value',
            help='Store a simple value')

        add('-c',
            action='store_const',
            const='value-to-store',
            dest='constant_value',
            help='Store a constant value')

        add('-t',
            action='store_true', default=False,
            dest='boolean_switch',
            help='Set a switch to true')

        add('-f',
            action='store_false', default=False,
            dest='boolean_switch',
            help='Set a switch to false')

        add('-a',
            action='append', default=[],
            dest='collection',
            help='Add repeated values to a list')

        add('-A',
            action='append_const',
            const='value-1-to-append', default=[],
            dest='const_collection',
            help='Add different values to list')

        add('-B',
            action='append_const',
            const='value-2-to-append',
            dest='const_collection',
            help='Add different values to list')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        add('-L',
            '--license',
            action='store_true',
            dest='lic',
            help='Show license and exit')

        add('-C',
            '--credits',
            action='store_true',
            dest='crd',
            help='Show credits and exit')

        add('-V',
            '--version',
            action='version',
            version='%(prog)s'f' {ver} (Python {ver_pyt})')

        add('-wx',
            '--wxversion',
            action='store_true',
            dest='wx_ver',
            help='Show wxPython/wxWidgets version and exit')

        add('-stc',
            '--scintilla',
            action='store_true',
            dest='stc_ver',
            help='Show Scintilla/StyledTextCtrl version and exit')


    parser = argparse.ArgumentParser(description=f'{APP["Base"]} - {APP["Desc"]}',
                                     # formatter_class=BlankLinesHelpFormatter,
                                     fromfile_prefix_chars='@',
                                     usage='%(prog)s [options]'
                                    )
    add_arguments(parser)
    args = parser.parse_args()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    DBG('INF', f'    {"-"*24}')
    DBG('INF', f'    TEMPORARY ARGPARSER DATA')
    DBG('INF', f'    {"-"*24}')
    for arg, val in vars(args).items():
        DBG('INF', f'    {arg:16} : {val}')
    DBG('INF', f'    {"-"*24}\n')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    if args.lic:
        print(__license__)
        raise SystemExit
    elif args.crd:
        print(f'\nCredits: {crd[0]}', *[f'\n{" "*9}{c}' for c in crd[1:]])
        raise SystemExit
    elif args.wx_ver:
        print('wxPython', ver_wxp)
        raise SystemExit
    elif args.stc_ver:
        print('Scintilla', ver_stc)
        raise SystemExit

    return


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # dbg_CLI_ARGS()

    # parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    # parser.add_argument('a',
    #                      help='a first argument')
    # parser.add_argument('b',
    #                      help='a second argument')
    # parser.add_argument('c',
    #                      help='a third argument')
    # parser.add_argument('d',
    #                      help='a fourth argument')
    # parser.add_argument('e',
    #                      help='a fifth argument')
    # parser.add_argument('-q',
    #                     '--quiet',
    #                       action='store_true',
    #                       help='an optional argument')
    # parser.add_argument('-v',
    #                     '--verbose',
    #                     action='store_true',
    #                     help='an optional argument')

    # args = parser.parse_args()

    # # print('If you read this line it means that you have provided all the parameters\n')

    # print('  a      ', args.a)
    # print('  b      ', args.b)
    # print('  c      ', args.c)
    # print('  d      ', args.d)
    # print('  e      ', args.e)
    # print('  quiet  ', args.quiet)
    # print('  verbose', args.verbose, '\n')
    # # print('  help', args.help)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # class FakeGit
    #     def __init__(self):
    #         parser = argparse.ArgumentParser(
    #             description='Pretends to be git',
    #             usage='''git <command> [<args>]

    # The most commonly used git commands are:
    #    commit     Record changes to the repository
    #    fetch      Download objects and refs from another repository
    # ''')
    #         parser.add_argument('command', help='Subcommand to run')
    #         # parse_args defaults to [1:] for args, but you need to
    #         # exclude the rest of the args too, or validation will fail
    #         args = parser.parse_args(sys.argv[1:2])
    #         if not hasattr(self, args.command):
    #             print('Unrecognized command [%s]\n\n' % args.command)
    #             parser.print_help()
    #             exit(1)
    #         # use dispatch pattern to invoke method with same name
    #         getattr(self, args.command)()

    #     def commit(self):
    #         parser = argparse.ArgumentParser(
    #             description='Record changes to the repository')
    #         # prefixing the argument with -- means it's optional
    #         parser.add_argument('--amend', action='store_true')
    #         # now that we're inside a subcommand, ignore the first
    #         # TWO argvs, ie the command (git) and the subcommand (commit)
    #         args = parser.parse_args(sys.argv[2:])
    #         print('Running git commit, amend=%s' % args.amend)

    #     def fetch(self):
    #         parser = argparse.ArgumentParser(
    #             description='Download objects and refs from another repository')
    #         # NOT prefixing the argument with -- means it's not optional
    #         parser.add_argument('repository')
    #         args = parser.parse_args(sys.argv[2:])
    #         print('Running git fetch, repository=%s' % args.repository)


    # FakeGit()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def parse_plugins():
    DBG('INF', f'* Parse plugins to be loaded (TODO):')

    PLG = {}
    PLG['DUMMY'] = 'dummy plugin'

    DBG('INF', f'  {PLG}\n')

    return PLG