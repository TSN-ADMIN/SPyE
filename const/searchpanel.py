#!/usr/bin/python

import wx


# search panel: accelerator keys
SCH_KEYS = {
    'Exit'      : 'ESCAPE',           # exit
    'Find'      : 'RETURN',           # find next
    'FindPrev'  : 'Shift+RETURN',     # find previous
    'Count'     : 'Alt+Shift+C',      # count occurrences
    'FindAll'   : 'Alt+RETURN',       # find all
    'Replace'   : 'Ctrl+RETURN',      # replace
    'ReplaceAll': 'Ctrl+Alt+RETURN',  # replace all
    'SelectAll' : 'Ctrl+A',           # focused text control: Select All
}

# search panel: history keys (text controls)
SCH_HIS_KEYS = (
    wx.WXK_UP,
    wx.WXK_DOWN,
    wx.WXK_RETURN,
    wx.WXK_NUMPAD_ENTER,
)

#FIX, not used: obsolete?
#FIX, use 'swap_dict' in 'util.py' for inverse lookup
# search panel mapping: button name, keypress
SCH_MAP = {
    'ESCAPE'       : SCH_KEYS['Exit'],
    'btnFind'      : SCH_KEYS['Find'],
    'btnFindPrev'  : SCH_KEYS['FindPrev'],
    'btnCount'     : SCH_KEYS['Count'],
    'btnFindAll'   : SCH_KEYS['FindAll'],
    'btnReplace'   : SCH_KEYS['Replace'],
    'btnReplaceAll': SCH_KEYS['ReplaceAll'],
    'Ctrl+A'       : SCH_KEYS['SelectAll'],
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

# search panel field tooltips
#FIX, for TESTING: 'tst'
tst = ' - SearchPanel tooltip TEST field'
ico = '\n\nClick to toggle checkbox'
cbx = '\n\nClick to toggle OR press <Space>'

SCH_TTP = {
    # 'SearchPanel'   : '[SearchPanel: Escape to Exit]',
    'sttFind'       : '[sttFind]' + tst,
    'txcFind'       : '[txcFind]' + tst,
    'btnFind'       : '[btnFind]' + tst,
    'btnFindPrev'   : '[btnFindPrev]' + tst,
    'btnFindAll'    : '[btnFindAll]' + tst,
    'sttWhere'      : '[sttWhere]' + tst,
    'txcWhere'      : '[txcWhere]' + tst,
    'btnWhere'      : '[btnWhere]' + tst,
    'sttReplace'    : '[sttReplace]' + tst,
    'txcReplace'    : '[txcReplace]' + tst,
    'btnReplace'    : '[btnReplace]' + tst,
    'btnReplaceAll' : '[btnReplaceAll]' + tst,
    'sttIncremental': '[sttIncremental]' + tst,
    'txcIncremental': '[txcIncremental]' + tst,
    'btnCount'      : '[btnCount]' + tst,
    'cbxCase'       : '[cbxCase]' + tst  + '\n\nAlt-C or' + cbx,
    'cbxRegex'      : '[cbxRegex]' + tst  + '\n\nAlt-R or' + cbx,
    'cbxWord'       : '[cbxWord]' + tst  + '\n\nAlt-W or' + cbx,
    'cbxWrap'       : '[cbxWrap]' + tst + cbx,
    'cbxInsel'      : '[cbxInsel]' + tst + cbx,
    'cbxHilite'     : '[cbxHilite]' + tst + cbx,
    'cbxPrcase'     : '[cbxPrcase]' + tst + cbx,
    'cbxContext'    : '[cbxContext]' + tst + cbx,
    'cbxBuffer'     : '[cbxBuffer]' + tst + cbx,
    'ggeProgressBar': '[ggeProgressBar]' + tst,
    'btnCancel'     : '[btnCancel]' + tst,
    'icoHelp'       : '[icoHelp]' + tst,
    'icoCase'       : '[icoCase]' + tst + ico,
    'icoRegex'      : '[icoRegex]' + tst + ico,
    'icoWord'       : '[icoWord]' + tst + ico,
    'icoWrap'       : '[icoWrap]' + tst + ico,
    'icoInsel'      : '[icoInsel]' + tst + ico,
    'icoHilite'     : '[icoHilite]' + tst + ico,
    'icoPrcase'     : '[icoPrcase]' + tst + ico,
    'icoContext'    : '[icoContext]' + tst + ico,
    'icoBuffer'     : '[icoBuffer]' + tst + ico,
    'stcResults'    : '[stcResults]' + tst,
}
