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

# CTags command options (auxiliary)
# not used
OPT_CTAGS_AUX = f'{OPT_CTAGS} --excmd=pattern'

# APPLICATION INFO
APP = {}

# filename, pathname, (base)name, description
APP['File'] = resolve_path(sys.argv[0])
APP['Path'] = APP['File'].parent
APP['Base'] = APP['File'].stem
APP['Desc'] = 'Scintilla/Python based Editor'

# timestamps: Created, Modified, Accessed
fst = APP['File'].stat()
APP['TimC'] = tim_str(fst.st_ctime)
APP['TimM'] = tim_str(fst.st_mtime)
APP['TimA'] = tim_str(fst.st_atime)

# version, full description, icon
APP['Vrsn'] = __version__
# APP['Vrsn'] = '0.9 beta'
APP['Full'] = f'{APP["Base"]} v{APP["Vrsn"]} [{APP["TimM"]}]'

#NOTE, avoid error 'wx._core.PyNoAppError: The wx.App object must be created first!'
app = wx.App()
APP['Icon'] = PNG['app'].Icon

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# environment variables
pfx = APP['Base'].upper()

ENV_VARS = {
    f'{pfx}_DBG_INF'  : 0,
    f'{pfx}_DBG_MAC'  : 0,
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
                evtmap[evt.typeId] = nam
    del evt, nam
    return evtmap

# event mapping: typeId, name
COMMON_EVENTS = build_evtmap()

# catch events in 'app_filter_event'
FILTER_EVENTS = (
    # '_EVT_TYPE_UNKNOWN_',
    # 'EVT_ACTIVATE',
    # 'EVT_ACTIVATE_APP',
    # 'EVT_AUI_FIND_MANAGER',
    # 'EVT_AUI_RENDER',
    # 'EVT_AUINOTEBOOK_PAGE_CHANGED',
    # 'EVT_AUINOTEBOOK_PAGE_CHANGING',
    # 'EVT_CHAR_HOOK',
    # 'EVT_CHILD_FOCUS',
    # 'EVT_CHOICEBOOK_PAGE_CHANGING',
    # 'EVT_CONTEXT_MENU',
    # 'EVT_ENTER_WINDOW',
    # 'EVT_ERASE_BACKGROUND',
    # 'EVT_IDLE',
    # 'EVT_KILL_FOCUS',
    # 'EVT_LEAVE_WINDOW',
    # 'EVT_LEFT_DCLICK',
    # 'EVT_LEFT_DOWN',
    # 'EVT_LEFT_UP',
    # 'EVT_MOTION',
    # 'EVT_MOUSE_CAPTURE_CHANGED',
    # 'EVT_MOUSE_EVENTS',
    # 'EVT_MOVE',
    # 'EVT_NAVIGATION_KEY',
    # 'EVT_NC_PAINT',
    # 'EVT_PAINT',
    # 'EVT_SET_CURSOR',
    # 'EVT_SET_FOCUS',
    # 'EVT_SHOW',
    # 'EVT_SIZE',
    # 'EVT_STC_AUTOCOMP_CANCELLED',
    # 'EVT_STC_AUTOCOMP_CHAR_DELETED',
    # 'EVT_STC_AUTOCOMP_COMPLETED',
    # 'EVT_STC_AUTOCOMP_SELECTION',
    # 'EVT_STC_AUTOCOMP_SELECTION_CHANGE',
    # 'EVT_STC_CALLTIP_CLICK',
    # 'EVT_STC_CHANGE',
    # 'EVT_STC_CHARADDED',
    # 'EVT_STC_CLIPBOARD_COPY',
    # 'EVT_STC_CLIPBOARD_PASTE',
    # 'EVT_STC_DO_DROP',
    # 'EVT_STC_DOUBLECLICK',
    # 'EVT_STC_DRAG_OVER',
    # 'EVT_STC_DWELLEND',
    # 'EVT_STC_DWELLSTART',
    # 'EVT_STC_HOTSPOT_CLICK',
    # 'EVT_STC_HOTSPOT_DCLICK',
    # 'EVT_STC_HOTSPOT_RELEASE_CLICK',
    # 'EVT_STC_INDICATOR_CLICK',
    # 'EVT_STC_INDICATOR_RELEASE',
    # 'EVT_STC_KEY',
    # 'EVT_STC_MACRORECORD',
    # 'EVT_STC_MARGIN_RIGHT_CLICK',
    # 'EVT_STC_MARGINCLICK',
    # 'EVT_STC_MODIFIED',
    # 'EVT_STC_NEEDSHOWN',
    # 'EVT_STC_PAINTED',
    # 'EVT_STC_ROMODIFYATTEMPT',
    # 'EVT_STC_SAVEPOINTLEFT',
    # 'EVT_STC_SAVEPOINTREACHED',
    # 'EVT_STC_START_DRAG',
    # 'EVT_STC_STYLENEEDED',
    # 'EVT_STC_UPDATEUI',
    # 'EVT_STC_URIDROPPED',
    # 'EVT_STC_USERLISTSELECTION',
    # 'EVT_STC_ZOOM',
    # 'EVT_TEXT',
    # 'EVT_TIMER',
    # 'EVT_TREE_GET_INFO',
    # 'EVT_TREE_ITEM_EXPANDED',
    # 'EVT_TREE_ITEM_EXPANDING',
    # 'EVT_TREE_SEL_CHANGED',
    # 'EVT_TREE_SEL_CHANGING',
    # 'EVT_UPDATE_UI_RANGE',
    # 'EVT_WINDOW_CREATE',
)

# keyboard mapping
def build_keymap():
    keymap = {}
    pfx = 'WXK_'
    for nam in dir(wx):
        if nam.startswith(pfx):
            cod = getattr(wx, nam)
            keymap[cod] = nam[4:]
    for mod in ['CONTROL', 'ALT', 'SHIFT', 'MENU']:
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
# PDB_COMMANDS = (
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
    # ('BKP', 'backup', 'bak'),  # backup
    ('CFG', 'conf',   'cfg'),  # configuration
    ('DBG', 'conf',   'dbg'),  # debug
    ('LNG', 'conf',   'lng'),  # language
    ('MNU', 'conf',   'mnu'),  # menu
    ('RFH', 'conf',   'rfh'),  # recent file history
    ('SFH', 'conf',   'sfh'),  # search field history
    ('SSN', 'conf',   'ssn'),  # session
    ('THM', 'conf',   'thm'),  # theme
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ('HLP', 'help',   'hhp'),  # help
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ('LOG', 'log',    'log'),  # logging
    # ('MAC', 'macro',  'mac'),  # macro
    # ('PLG', 'plugin', 'plg'),  # plugin
    # ('TAG', 'tag',     None),  # tags
    # ('TMP', 'tmp',    'tmp'),  # temp
)

#TODO, use nameing convention as in 'Editor'

# dnm, fnm, fbs, ext

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
# for typ in LOC:
#     dir_ = Path(LOC[typ]['PTH'])
#     if not dir_.exists():
#         dir_.mkdir()

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
OUT_CTAGS = f'{LOC["CFG"]["PTH"]}tags'

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
