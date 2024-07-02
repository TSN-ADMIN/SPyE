#!/usr/bin/python

import re
import wx

from common.type import DotDict
from const.menubar import MI


# search panel: search flags
SCH_FLAGS = [
    'CAS',  # Case Sensitive
    'REG',  # Regular Expression
    'WRD',  # Whole Words Only
    'WRP',  # Wrap Around
    'ISL',  # In Selection
    'HLM',  # Highlight Matches
    'PCS',  # Preserve Case
    'CXT',  # Show context
    'BUF',  # Use buffer
]

# search panel: history keys (text controls)
SCH_HIS_KEYS = (
    wx.WXK_UP,
    wx.WXK_DOWN,
    wx.WXK_RETURN,
    wx.WXK_NUMPAD_ENTER,
)

# search panel: accelerator keys
SCH_KEYS = {
    'Find'      : 'RETURN',           # find next
    'FindAll'   : 'Alt+RETURN',
    'FindPrev'  : 'Shift+RETURN',
    'Replace'   : 'Ctrl+RETURN',
    'ReplaceAll': 'Ctrl+Alt+RETURN',
    'Count'     : 'Alt+Shift+C',      # occurrences
    'Exit'      : 'ESCAPE',
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    'SelectAll' : 'Ctrl+A',           # in text control
    'Case'      : 'Alt+C',
    'Regex'     : 'Alt+R',
    'Word'      : 'Alt+W',
}

#FIX, not used: obsolete?
#FIX, use 'swap_dict' in 'util.py' for inverse lookup
# search panel mapping: widget name, keypress
SCH_MAP = {
    'btnFind'      : SCH_KEYS['Find'],
    'btnFindAll'   : SCH_KEYS['FindAll'],
    'btnFindPrev'  : SCH_KEYS['FindPrev'],
    'btnReplace'   : SCH_KEYS['Replace'],
    'btnReplaceAll': SCH_KEYS['ReplaceAll'],
    'btnCount'     : SCH_KEYS['Count'],
    'ESCAPE'       : SCH_KEYS['Exit'],
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    'Ctrl+A'       : SCH_KEYS['SelectAll'],
    'Alt+C'        : 'Case',
    'Alt+R'        : 'Regex',
    'Alt+W'        : 'Word',
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # 'Ctrl+F',           #   "  : Find
    # 'Ctrl+I',           #   "  : Incremental
    # 'Ctrl+H',           #   "  : Replace
    # 'Ctrl+Shift+F',     #   "  : Find in Files
    # 'Shift+TAB',        # previous field
    # 'TAB',              # next       "
    # 'F3',               #   "    "
    # 'Shift+F3',         #   "      "
}

# search option mapping
SCH_OPT = {
    MI['SCH_CAS']: ('cas', 'cbx_cas',),
    MI['SCH_REG']: ('reg', 'cbx_reg',),
    MI['SCH_WRD']: ('wrd', 'cbx_wrd',),
    MI['SCH_WRP']: ('wrp', 'cbx_wrp',),
    MI['SCH_ISL']: ('isl', 'cbx_isl',),
    MI['SCH_HLM']: ('hlm', 'cbx_hlm',),
    MI['SCH_PCS']: ('pcs', 'cbx_pcs',),
    MI['SCH_CXT']: ('cxt', 'cbx_cxt',),
    MI['SCH_BUF']: ('buf', 'cbx_buf',),
}

# search panel field tooltips
#FIX, for TESTING: 'tst'
tst = ' - SearchPanel tooltip TEST field'
ico = '\n\nClick to toggle checkbox'
cbx = '\n\nClick to toggle OR press <Space>'

SCH_TTP = {
    'SearchPanel'   : '[SearchPanel: Escape to Exit]',
    'sttFind'       : f'[sttFind]{tst}',
    'txcFind'       : f'[txcFind]{tst}',
    'btnFind'       : f'[btnFind]{tst}',
    'btnFindPrev'   : f'[btnFindPrev]{tst}',
    'btnFindAll'    : f'[btnFindAll]{tst}',
    'sttWhere'      : f'[sttWhere]{tst}',
    'txcWhere'      : f'[txcWhere]{tst}',
    'btnWhere'      : f'[btnWhere]{tst}',
    'sttReplace'    : f'[sttReplace]{tst}',
    'txcReplace'    : f'[txcReplace]{tst}',
    'btnReplace'    : f'[btnReplace]{tst}',
    'btnReplaceAll' : f'[btnReplaceAll]{tst}',
    'sttIncremental': f'[sttIncremental]{tst}',
    'txcIncremental': f'[txcIncremental]{tst}',
    'btnCount'      : f'[btnCount]{tst}',
    'cbxCase'       : f'[cbxCase]{tst}\n\nAlt+C or{cbx}',
    'cbxRegex'      : f'[cbxRegex]{tst}\n\nAlt+R or{cbx}',
    'cbxWord'       : f'[cbxWord]{tst}\n\nAlt+W or{cbx}',
    'cbxWrap'       : f'[cbxWrap]{tst}{cbx}',
    'cbxInsel'      : f'[cbxInsel]{tst}{cbx}',
    'cbxHilite'     : f'[cbxHilite]{tst}{cbx}',
    'cbxPrcase'     : f'[cbxPrcase]{tst}{cbx}',
    'cbxContext'    : f'[cbxContext]{tst}{cbx}',
    'cbxBuffer'     : f'[cbxBuffer]{tst}{cbx}',
    'ggeProgressBar': f'[ggeProgressBar]{tst}',
    'btnCancel'     : f'[btnCancel]{tst}',
    'icoHelp'       : f'[icoHelp]{tst}',
    'icoCase'       : f'[icoCase]{tst}{ico}',
    'icoRegex'      : f'[icoRegex]{tst}{ico}',
    'icoWord'       : f'[icoWord]{tst}{ico}',
    'icoWrap'       : f'[icoWrap]{tst}{ico}',
    'icoInsel'      : f'[icoInsel]{tst}{ico}',
    'icoHilite'     : f'[icoHilite]{tst}{ico}',
    'icoPrcase'     : f'[icoPrcase]{tst}{ico}',
    'icoContext'    : f'[icoContext]{tst}{ico}',
    'icoBuffer'     : f'[icoBuffer]{tst}{ico}',
    'stcResults'    : f'[stcResults]{tst}',
}

# where string: element types/descriptions (tag type: max items = 1)
#NOTE, 'lst' will contain strings found per type
whr = (
#    key    lst  style
    ('OFD',  [], '<tag>'         ,),  # tag: open folders
    ('OFL',  [], '<tag>'         ,),  #  " : open files
    ('CFL',  [], '<tag>'         ,),  #  " : current file
    ('BIN',  [], '<tag>'         ,),  #  " : allow binary content
    ('PVW',  [], '<tag>'         ,),  #  " : preview (dry run)
    ('ITG',  [], '_INVALID_<tag>',),  #  " : INVALID
    ('INC',  [], 'Include'       ,),  # includes
    ('EXC',  [], 'eXclude'       ,),  # excludes
    ('PNM',  [], 'Path'          ,),  # pathnames
    ('FNM',  [], 'File'          ,),  # filenames
    ('DCD',  [], '_DISCARD'      ,),  # DISCARD
)

# create dotdict from tuple
WHR = DotDict()

for (key, lst, dsc) in whr:
    WHR[key] = DotDict({'lst': lst, 'dsc': dsc})

del whr

# where string (WHR_) and results panel (RES_): regex patterns
tag_lst = ('openfolders', 'openfiles', 'currentfile', 'binary', 'preview')
ptn = (
#    key    regex
#           for tags, e.g. <currentfile>
    ('WHR_TAG', [re.compile(rf'^<{tag}>$', re.IGNORECASE) for tag in tag_lst]),
#           for in/exclude (with subdir/extension) filters
    ('WHR_FLT', re.compile(r'[+-]{0,1}\*\.{0,1}[a-zA-Z0-9_\-.()/:\\]*\*{0,1}')),
#           for pathnames
    ('WHR_PNM', re.compile(r'^[a-zA-Z]{0,1}[:]{0,1}[/\\]{0,1}[a-zA-Z0-9_\-()/\\]+')),
#           for filenames
    ('WHR_FNM', re.compile(r'^[a-zA-Z0-9_\-.()]+')),  # \*{0,1},),
#           for filename
    ('RES_FNM', re.compile(r'^\s\s[^ ].*:$')),
#           for line number
    ('RES_LIN', re.compile(r'^ *?[0-9]+:')),
)

# create dotdict from tuple
PTN = DotDict()

for (key, reg) in ptn:
    PTN[key] = DotDict({'reg': reg})

del ptn
