#!/usr/bin/python

import wx

from .menubar import MI


# new (window) ID ref: alias
__ID = wx.NewIdRef

# ToolBar: tool item ids
TBR = {
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
# TBR['ALL'] = {
#     TBR['NEW']: 'new',
#     TBR['OPN']: 'open',
#     TBR['SAV']: 'save',
#     TBR['SAS']: 'save_as',
#     TBR['CLS']: 'close',
#     TBR['CUT']: 'cut',
#     TBR['CPY']: 'copy',
#     TBR['PST']: 'paste',
#     TBR['UDO']: 'undo',
#     TBR['RDO']: 'redo',
#     TBR['FND']: 'find',
#     TBR['NXT']: 'find_next',
#     TBR['RPL']: 'replace',
#     TBR['PRV']: 'find_prev',
#     TBR['FXP']: 'explorer',
#     TBR['SDF']: 'symbol_defs',
#     TBR['BRC']: 'brace_match',
#     TBR['SRT']: 'sort',
#     TBR['SUM']: 'calc_sum',
#     TBR['FUL']: 'fullscreen_16',
#     TBR['PRF']: 'prefs',
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
