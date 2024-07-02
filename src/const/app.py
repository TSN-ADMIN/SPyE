#!/usr/bin/python

from pathlib import Path
import stat
import sys

import wx
from wx import stc

from app.__version__ import __version__
from common.date import tim_str
from common.path import resolve_path
from common.type import is_evb
from data.images import catalog as PNG


# Python modules and external executables
EXE = {
    'PYTHON'     : sys.executable,
    'PYPATH'     : resolve_path(sys.executable).parent,
    'PDB'        : 'pdb',
    'CTAGS'      : 'ctags',
    'HELPVIEWER' : 'helpviewer',
    'RADON'      : 'radon',
    'PYCODESTYLE': 'pycodestyle',
    'PYFLAKES'   : 'pyflakes',
    'PYLINT'     : 'pylint',
    'VULTURE'    : 'vulture',
}

# CTags command options
OPT_CTAGS = f'-nu --extras=-p --fields=fiKlmnsStz -R'

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  @@@@@@@@@@@@@@@@@@@@@@
OPT_CTAGS = f'-nu --extras=-p --fields=fiKlmnsStz -R --kinds-python=*'  # include locals et al
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  @@@@@@@@@@@@@@@@@@@@@@

# CTags command options (auxiliary)
# not used
OPT_CTAGS_AUX = f'{OPT_CTAGS} --excmd=pattern'

# APPLICATION INFO
APP = {}

# filename, pathname, basename, description
APP['File'] = resolve_path(sys.argv[0])
APP['Path'] = APP['File'].parent
APP['Base'] = APP['File'].stem
APP['Desc'] = 'Scintilla/Python based Editor'

# timestamps: Created, Modified, Accessed
fst = APP['File'].stat()
APP['TimC'] = tim_str(fst.st_ctime)
APP['TimM'] = tim_str(fst.st_mtime)
APP['TimA'] = tim_str(fst.st_atime)

# version, info, icon
APP['Vrsn'] = __version__
# APP['Vrsn'] = '0.9 beta'
APP['Info'] = f'{APP["Base"]} v{APP["Vrsn"]} [{APP["TimM"]}]'
APP['Icon'] = PNG['app_16'].Icon

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# environment variables
pfx = APP['Base'].upper()

ENV_VARS = {
    f'{pfx}_DBG_AFE'  : 0,
    f'{pfx}_DBG_INF'  : 0,
    f'{pfx}_DBG_KBD'  : 0,
    f'{pfx}_DBG_MAC'  : 0,
    f'{pfx}_DBG_MNU'  : 0,
    f'{pfx}_DBG_TMR'  : 0,
    # <placeholders> for TESTING
    f'{pfx}_CFG_<DBG>': 0,
    f'{pfx}_CFG_<CFG>': 0,
    f'{pfx}_LNG_<LNG>': 0,
    # dummy for TESTING (skip)
    f'{pfx}_SKP_SKIP_': 0,
}

# commandline arguments
# not used
CLI_ARGS = {
#   ...
#   ...
#   ...
}
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# event mapping
def build_evtmap():
    # besides 'wx' and 'wx.stc', load these wx modules to cover most events
    import wx.adv as adv
    import wx.aui as aui
    import wx.dataview as dataview
    import wx.grid as grid
    import wx.html as html
    import wx.html2 as html2
    import wx.media as media
    import wx.propgrid as propgrid
    import wx.ribbon as ribbon
    # import wx.richtext as richtext

    evtmap = {}
    pfx = 'EVT_'
    cat = 'EVT_CATEGORY_'
    for mod in (wx, stc, adv, aui, dataview, grid, html, html2,
                    # media, propgrid, ribbon, richtext):
                    media, propgrid, ribbon):
        for nam in dir(mod):
            # discard non events/categories
            if not nam.startswith(pfx) or nam.startswith(cat):
                continue
            evt = getattr(mod, nam)
            if is_evb(evt):
                evtmap[evt.typeId] = nam[4:]  ## strip 'EVT_'
    del evt, nam
    return evtmap

# event mapping: typeId, name
COMMON_EVENTS = build_evtmap()

# catch events in 'dbf.APP_FILTER_EVENT' (events specified w/o 'EVT_' prefix)
FILTER_EVENTS = (
    # '_TYPE_UNKNOWN_',
    # 'ACTIVATE',
    # 'ACTIVATE_APP',
    # 'AUI_FIND_MANAGER',
    # 'AUI_RENDER',
    # 'AUINOTEBOOK_PAGE_CHANGED',
    # 'AUINOTEBOOK_PAGE_CHANGING',
    # 'CHAR_HOOK',
    # 'CHILD_FOCUS',
    # 'CHOICEBOOK_PAGE_CHANGING',
    # 'CONTEXT_MENU',
    # 'ENTER_WINDOW',
    # 'ERASE_BACKGROUND',
    # 'IDLE',
    # 'KEY_DOWN',
    # 'KEY_UP',
    # '-KILL_FOCUS',
    # 'LEAVE_WINDOW',
    # 'LEFT_DCLICK',
    # 'LEFT_DOWN',
    # 'LEFT_UP',
    # 'LIST_COL_DRAGGING',
    # 'LIST_DELETE_ALL_ITEMS',
    # 'LIST_INSERT_ITEM',
    # 'LIST_ITEM_SELECTED',
    # 'MOTION',
    # 'MOUSE_CAPTURE_CHANGED',
    # 'MOUSE_EVENTS',
    # 'MOVE',
    # 'NAVIGATION_KEY',
    # 'NC_PAINT',
    # 'PAINT',
    # 'SET_CURSOR',
    # '-SET_FOCUS',
    # 'SHOW',
    # 'SIZE',
    # 'STC_AUTOCOMP_CANCELLED',
    # 'STC_AUTOCOMP_CHAR_DELETED',
    # 'STC_AUTOCOMP_COMPLETED',
    # 'STC_AUTOCOMP_SELECTION',
    # 'STC_AUTOCOMP_SELECTION_CHANGE',
    # 'STC_CALLTIP_CLICK',
    # 'STC_CHANGE',
    # 'STC_CHARADDED',
    # 'STC_CLIPBOARD_COPY',
    # 'STC_CLIPBOARD_PASTE',
    # 'STC_DO_DROP',
    # 'STC_DOUBLECLICK',
    # 'STC_DRAG_OVER',
    # 'STC_DWELLEND',
    # 'STC_DWELLSTART',
    # 'STC_HOTSPOT_CLICK',
    # 'STC_HOTSPOT_DCLICK',
    # 'STC_HOTSPOT_RELEASE_CLICK',
    # 'STC_INDICATOR_CLICK',
    # 'STC_INDICATOR_RELEASE',
    # 'STC_KEY',
    # 'STC_MACRORECORD',
    # 'STC_MARGIN_RIGHT_CLICK',
    # 'STC_MARGINCLICK',
    # 'STC_MODIFIED',
    # 'STC_NEEDSHOWN',
    # 'STC_PAINTED',
    # 'STC_ROMODIFYATTEMPT',
    # 'STC_SAVEPOINTLEFT',
    # 'STC_SAVEPOINTREACHED',
    # 'STC_START_DRAG',
    # 'STC_STYLENEEDED',
    # 'STC_UPDATEUI',
    # 'STC_URIDROPPED',
    # 'STC_USERLISTSELECTION',
    # 'STC_ZOOM',
    # 'TEXT',
    # 'TIMER',
    # 'TREE_GET_INFO',
    # 'TREE_ITEM_EXPANDED',
    # 'TREE_ITEM_EXPANDING',
    # 'TREE_SEL_CHANGED',
    # 'TREE_SEL_CHANGING',
    # 'UPDATE_UI',
    # 'UPDATE_UI_RANGE',
    # 'WINDOW_CREATE',
)

# keyboard mapping
def build_keymap():
    keymap = {}
    pfx = 'WXK_'
    for nam in dir(wx):
        if nam.startswith(pfx):
            cod = getattr(wx, nam)
            keymap[cod] = nam[4:]
    for mod in {'CONTROL', 'ALT', 'SHIFT', 'MENU'}:
        cod = getattr(wx, pfx + mod)
        keymap[cod] = ''
    del cod, nam
    return keymap

# keyboard mapping: code, name
COMMON_KEYS = build_keymap()

# accelerator keys
ACC_KEYS = {
    wx.ACCEL_ALT   : 'Alt',
    wx.ACCEL_CTRL  : 'Ctrl',
    wx.ACCEL_NORMAL: '',
    wx.ACCEL_SHIFT : 'Shift',
}

# modifier keys
MOD_KEYS = {
    wx.MOD_ALT    : 'Alt',
    wx.MOD_CONTROL: 'Ctrl',
    wx.MOD_NONE   : '',
    wx.MOD_SHIFT  : 'Shift',
    wx.MOD_WIN    : 'Win',
}

# Python debugger prompt
PDB_PROMPT = '(Pdb) '

# Python debugger commands
# PDB_CMDS = (
#     'alias',
#     'args',
#     'break',
#     'clear',
#     'commands',
#     'condition',
#     'continue', True
#     'debug',
#     'disable', True
#     'display',
#     'down',
#     'enable', True
#     'EOF',
#     'help',
#     'ignore',
#     'interact',
#     'jump', True
#     'list',
#     'longlist',
#     'next', True
#     'p',
#     'pp',
#     'quit',
#     'return', True
#     'retval', True
#     'run',
#     'source',
#     'step', True
#     'tbreak',
#     'unalias',
#     'undisplay',
#     'until', True
#     'up',
#     'whatis',
#     'where',
# )

# listbox navigation keys (symbol browser/goto anything)
LBX_NAV_KEYS = (
    wx.WXK_UP,
    wx.WXK_DOWN,
    wx.WXK_PAGEDOWN,
    wx.WXK_PAGEUP,
    wx.WXK_HOME,
    wx.WXK_END,
)

#TODO, put sessions in 'conf\SPyE.ssn' (no .default?):
# locations for application file types
LOC = {}
APP_FILE_TYPE = (
#    type   subdir    extension
    ('ACT', 'conf',   'act'),  # action
    # ('BKP', 'backup', 'bak'),  # backup
    ('CFG', 'conf',   'cfg'),  # configuration
    ('DBG', 'conf',   'dbg'),  # debug
    ('KBD', 'conf',   'kbd'),  # keyboard
    ('LNG', 'conf',   'lng'),  # language
    ('MNU', 'conf',   'mnu'),  # menu
    ('RFH', 'conf',   'rfh'),  # recent file history
    ('SFH', 'conf',   'sfh'),  # search field history
    ('SSN', 'conf',   'ssn'),  # session
    ('THM', 'conf',   'thm'),  # theme
    ('TRC', 'conf',   'trc'),  # system trace
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ('HLP', 'help',   'hhp'),  # help
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ('LOG', 'log',    'log'),  # logging
    # ('MAC', 'macro',  'mac'),  # macro
    # ('PLG', 'plugin', 'plg'),  # plugin
    # ('TAG', 'tag',     None),  # tags
    # ('TMP', 'tmp',    'tmp'),  # temp
)

#TODO, use naming convention as in 'Editor' -> 'dnm', 'fnm', 'fbs', 'ext'

fbs = APP['Base']

for typ, sub, ext in APP_FILE_TYPE:
    LOC[typ] = {}
    # full path
    LOC[typ]['PTH'] = pth = str(resolve_path(APP['Path'], f'../{sub}'))
    # extension, full filename
    LOC[typ]['EXT'] = f'.{ext}'
    LOC[typ]['FIL'] = str(Path(pth, f'{fbs}.{ext}'))
    # full filename.default, full filename.bak
    LOC[typ]['DFT'] = str(Path(pth, f'{fbs}.{ext}.default'))
    LOC[typ]['BAK'] = str(Path(pth, f'{fbs}.{ext}.bak'))

#TODO, create subdirs if not exist
for typ in LOC:
    dir_ = Path(LOC[typ]['PTH'])
    if not dir_.exists():
        dir_.mkdir()

# border style keywords
OPT_BORDER = {
    'DEFAULT': wx.BORDER_DEFAULT,
    'NONE'   : wx.BORDER_NONE,
    'RAISED' : wx.BORDER_RAISED,
    'SIMPLE' : wx.BORDER_SIMPLE,
    'STATIC' : wx.BORDER_STATIC,
    'SUNKEN' : wx.BORDER_SUNKEN,
}

# Top/Bottom Left/Right keywords for Top Line Tooltip location
#FIX, calculate top/bottom left/right positions for '(posx, posy)'
TLT_POSITION = {
    'TL': (-500, 20),  # (posx, posy),
# 'TR': NOW hardcoded default, solve in util.py->'TopLineToolTip.update'
    'TR': (-165, 20),
    'BL': (0, 0),      # (posx, posy),
    'BR': (0, 0),      # (posx, posy),
}

# CTags output file in config directory
OUT_CTAGS = f'{LOC["CFG"]["PTH"]}/tags'

#TODO, for TESTING; function not implemented
NOT_IMPL = '(NOT_IMPLEMENTED)'

#TODO, for TESTING ??; exit app w/o saving modifications
APP_EXIT_FAST = False

#INFO, Color Hex Color Codes
#INFO, URL=https://www.color-hex.com/
# application colours, wx identifiers unavailable for these hex codes
CLR = {
    'BLACK'  : '#000000',
    'BLUE'   : '#E6F2FF',
    'BLUE1'  : '#3399FF',
    'BLUE2'  : '#C6E2FF',
    'BLUE3'  : '#71B3E8',
    'BLUE4'  : '#37A5FF',
    'BLUE5'  : '#0078D7',
    'BLUE6'  : '#0000FF',
    'GREEN'  : '#ECFFEC',
    'GREEN1' : '#D7FFD7',
    'GREEN2' : '#CCFFCC',
    'GREY'   : '#F0F0F0',
    'GREY1'  : '#C0C0C0',
    'GREY2'  : '#404040',
    'GREY3'  : '#DFDFDF',
    'ORANGE' : '#FFE7CE',
    'ORANGE2': '#FF8000',
    'ORANGE3': '#FFD5AA',  # lighter, for 'doc map'
    'PURPLE' : '#EAD5FF',
    'RED'    : '#FFDDDD',
    'RED1'   : '#FF0000',
    'RED2'   : '#FFBBAA',
    'RED3'   : '#FF6060',
    'RED4'   : '#FEDBDB',
    'WHITE'  : '#FFFFFF',
    'YELLOW' : '#FFFFF0',
    'YELLOW2': '#FFFFD0',
}

# messages, not used
MSG_xxx = ''
MSG_yyy = ''
MSG_zzz = ''

# errors, not used
ERR_ITM_PARMS = 'Item %s must have 2 to 7 parms'
ERR_yyy = ''
ERR_zzz = ''

# file attributes
#   key:   description           flag (stat module)
FILE_ATTRS = {
    'A': ('Archive',             stat.FILE_ATTRIBUTE_ARCHIVE),
    'C': ('Compressed',          stat.FILE_ATTRIBUTE_COMPRESSED),
    'D': ('Directory',           stat.FILE_ATTRIBUTE_DIRECTORY),
    'E': ('Encrypted',           stat.FILE_ATTRIBUTE_ENCRYPTED),
    'H': ('Hidden',              stat.FILE_ATTRIBUTE_HIDDEN),
    'I': ('Not content indexed', stat.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED),
    'L': ('Reparsepoint',        stat.FILE_ATTRIBUTE_REPARSE_POINT),
    'N': ('Normal',              stat.FILE_ATTRIBUTE_NORMAL),
    'O': ('Offline',             stat.FILE_ATTRIBUTE_OFFLINE),
    'P': ('Sparse file',         stat.FILE_ATTRIBUTE_SPARSE_FILE),
    'R': ('Read only',           stat.FILE_ATTRIBUTE_READONLY),
    'S': ('System',              stat.FILE_ATTRIBUTE_SYSTEM),
    'T': ('Temporary',           stat.FILE_ATTRIBUTE_TEMPORARY),
    'V': ('Device',              stat.FILE_ATTRIBUTE_DEVICE),
}
