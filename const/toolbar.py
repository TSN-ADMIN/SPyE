#!/usr/bin/python

import wx

from const.menu import MI


# new (window) ID ref: alias
__ID = wx.NewIdRef

# ToolBar: tool item ids
TB = {
    'NEW': __ID(),
    'OPN': __ID(),
    'SAV': __ID(),
    'SAS': __ID(),
    'CLS': __ID(),
    'CUT': MI['EDT_CUT'],
    'CPY': MI['EDT_CPY'],
    'PST': MI['EDT_PST'],
    'UDO': __ID(),
    'RDO': __ID(),
    'FND': __ID(),
    'NXT': __ID(),
    'RPL': __ID(),
    'PRV': __ID(),
    'FXP': MI['SPT_FXP'],
    'SDF': MI['SPT_SDF'],
    'BRC': __ID(),
    'SRT': __ID(),
    'SUM': __ID(),
    'FUL': __ID(),
    'PRF': __ID(),
    'SCH': __ID(),
}

# # ToolBar: tool Labels
# TB['ALL'] = {
#     TB['NEW']: 'new',
#     TB['OPN']: 'open',
#     TB['SAV']: 'save',
#     TB['SAS']: 'save_as',
#     TB['CLS']: 'close',
#     TB['CUT']: 'cut',
#     TB['CPY']: 'copy',
#     TB['PST']: 'paste',
#     TB['UDO']: 'undo',
#     TB['RDO']: 'redo',
#     TB['FND']: 'find',
#     TB['NXT']: 'find_next',
#     TB['RPL']: 'replace',
#     TB['PRV']: 'find_prev',
#     TB['FXP']: 'explorer',
#     TB['SDF']: 'symbol_defs',
#     TB['BRC']: 'brace_match',
#     TB['SRT']: 'sort',
#     TB['SUM']: 'calc_sum',
#     TB['FUL']: 'fullscreen',
#     TB['PRF']: 'prefs',
# }

# ToolBar conteXt menu
TBX = {
#   menu item:  id      checked
    'CUS'    : [__ID(), None,],   # customize (no check)
    'SHW_ICO': [__ID(), True,],   # show icons
    'SHW_TXT': [__ID(), True,],   # show text
    'LRG_ICO': [__ID(), False,],  # large icons
    'LRG_TXT': [__ID(), False,],  # large text
    'ALN_HOR': [__ID(), False,],  # align horizontally
    'LOC_TOP': [__ID(), True,],   # top
    'LOC_LFT': [__ID(), False,],  # left
    'LOC_BOT': [__ID(), False,],  # bottom
    'LOC_RIT': [__ID(), False,],  # right
}
