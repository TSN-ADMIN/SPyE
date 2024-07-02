#!/usr/bin/python

import sys


#@@@@@@@@@@@@ OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE @@@@@@@@@@
#@@@@@@@@@@@@ OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE @@@@@@@@@@
# #INFO, see 'create_tlw_att' and 'set_tlw_att' in 'util.py'
# #INFO,     called from '__init__' of frequently used classes
# # Top Level Window Attribute LiST (main application object references)
# TLW_ATT_LST = (
#     'app', 'CFG', 'tlw',  # application, configuration, top level window
#     'mbr', 'tbr', 'sbr',  # menubar, toolbar, statusbar
#     'nbk', 'sch', 'spn',  # notebook, search panel, side panel
#     'rlr', 'ccx', 'ibr'   # ruler, code context, infobar
# )
#@@@@@@@@@@@@ OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE @@@@@@@@@@
#@@@@@@@@@@@@ OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE OBSOLETE @@@@@@@@@@

# starting id for 'aui.AuiNotebook' tab controls ('wxAuiTabCtrl')
TABCTRL_ID = 5380

#TODO, for TESTING; placeholder text for visual check
LOREM_IPSUM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
    eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut
    enim ad minim veniam, quis nostrud exercitation ullamco laboris
    nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore eu fugiat
    nulla pariatur. Excepteur sint occaecat cupidatat non proident,
    sunt in culpa qui officia deserunt mollit anim id est laborum.""".replace(' '*4, '')

# ALL default delays in milliseconds (ms)
DELAY = {
    'DFC': 5000,   # Detect File Change
    'MSG': 5000,   # clear statusbar MesSaGe field
    'AUX': 500,    # clear statusbar AUXiliary field
    'SPL': 3000,   # hide SPLash screen
    'CTP': 1000,   # show editor CallTiP
    'TTS': 500,    # ToolTip Show
    'TTH': 10000,  # ToolTip Hide
    'TTR': 500,    # ToolTip Reshow
    'TLH': 2000,   # 'Top Line tooltip' Hide
    'SPS': 500,    # Symbol Popup Show
    'CTS': 50,     # Colour Tooltip Show
    'CTH': 2000,   # Colour Tooltip Hide
}

# label font styles
LBL_FNT_STYLES = {
#    style        function
    'bold'     : 'Bold',
    'italic'   : 'Italic',
    'large'    : 'Larger',
    'small'    : 'Smaller',
    'strike'   : 'Strikethrough',
    'underline': 'Underlined',
}

# max integer value
INFINITY = sys.maxsize

#FIX, 'SearchPanel' help icon (bottom left corner) slightly shifts vertically in 'FIF' mode when IconSize' in [16, 32]
#FIX, for now, optimized for 'IconSize' == 24
# splitter window: default sash positions
SASH_POS = {
    'SCH': {'FND': 95, 'RPL': 131, 'FIF': 174, 'INC': 95, 'RES': 400},
    # use '-25' when 'ShowCheckboxes = False'
    # 'SCH': {'FND': 95-25, 'RPL': 131-25, 'FIF': 167-25, 'INC': 95-25, 'RES': 400-25},
    'SPN': 335,
    'CCX': 100,
    'RLR': 26,
}

# empty text
TXT_NIL = ''

# file modification indicator
IND_DOC_MOD = ' *'
# file lock/read-only indicator
IND_DOC_LCK = ' #'
