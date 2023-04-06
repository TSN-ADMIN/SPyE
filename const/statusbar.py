#!/usr/bin/python

from copy import deepcopy

import wx


# new (window) ID ref: alias
__ID = wx.NewIdRef

#INFO, URL=https://stackoverflow.com/questions/16607704/one-liner-creating-a-dictionary-from-list-with-indices-as-keys
#TODO, use 'enumerate', i.e. {k:v for v, k in enumerate((<list with keys>))}
# StatusBar Fields
SBF = {
#   field:   #  width  style
    'PSW': [ 0,    20, wx.SB_SUNKEN,],  # panel switcher icon (context menu)
    'MSG': [ 1,    -1, wx.SB_RAISED,],  # message
    'AUX': [ 2,   130, wx.SB_SUNKEN,],  # auxiliary
#   ------
    'LNC': [ 3,   100, wx.SB_RAISED,],  # Ln xx, Col yy
    'INS': [ 4,    25, wx.SB_SUNKEN,],  # INS/OVR
    'CNS': [ 5,    25, wx.SB_RAISED,],  # Caps/Num/Scroll lock
#   ------
    'SCH': [ 6,   140, wx.SB_SUNKEN,],  # search flags
    'FSZ': [ 7,    85, wx.SB_RAISED,],  # file size
#   ------
#FIX, field 'ENC' not implemented
    'ENC': [ 8,    30, wx.SB_SUNKEN,],  # file encoding (context menu)
    'EOL': [ 9,    50, wx.SB_RAISED,],  # end of line (context menu)
#FIX, field 'IND' not implemented
    'IND': [10,    50, wx.SB_SUNKEN,],  # indentation (context menu)
#
    'LNG': [11,    75, wx.SB_RAISED,],  # language (context menu)
#   ------
    'TIM': [12,    25, wx.SB_SUNKEN,],  # clock time (HH:MM)
}

# StatusBar Fields: COPY, used in 'CtxStatusBarMain'
SBF_CPY = deepcopy(SBF)

# do NOT clear statusbar auxiliary field when it contains specified (sub)string(s)
SBF_NO_CLEAR_AUX = ['Sel:']  #, 'macro']  #, 'history']  #, 'mode']

# clock time: width including seconds (HH:MM:SS)
SBF_TIM_SECONDS_WIDTH = 45

# StatusBar conteXt menu: main
SBX = {
#   field:  id      checked  menu label
    'ALL': [__ID(), True,    'Select All',],
    'NON': [__ID(), False,   'Select None',],
    'CUS': [__ID(), False,   'Custom...',],
    'PSW': [__ID(), True,    'Panel switcher',],
    'MSG': [__ID(), True,    'Message',],
    'AUX': [__ID(), True,    'Auxiliary',],
    'LNC': [__ID(), True,    'Ln xx, Col yy',],
    'INS': [__ID(), True,    'INS/OVR',],
    'CNS': [__ID(), True,    'Caps/Num/Scroll',],
    'SCH': [__ID(), True,    'Search flags',],
    'FSZ': [__ID(), True,    'File size',],
    'ENC': [__ID(), True,    'File encoding',],
    'EOL': [__ID(), True,    'Line endings',],
    'IND': [__ID(), True,    'Indentation',],
    'LNG': [__ID(), True,    'Language',],
    'TIM': [__ID(), True,    'Clock time',],
}

#FIX, save/restore to/from config
# StatusBar conteXt menu: file encoding
SBX_ENC = {
#   field:  id      checked
    'U08': [__ID(), True,],   # UTF-8
    'U6L': [__ID(), False,],  # UTF-16 LE
    'U6B': [__ID(), False,],  # UTF-16 BE
    'WIN': [__ID(), False,],  # Western (Windows 1252)
    'I01': [__ID(), False,],  # Western (ISO-8859-1)
    'I03': [__ID(), False,],  # Western (ISO-8859-3)
    'I15': [__ID(), False,],  # Western (ISO-8859-15)
    'MAC': [__ID(), False,],  # Western (Mac Roman)
    'DOS': [__ID(), False,],  # DOS (CP 437)
    'CW0': [__ID(), False,],  # Central European (Windows 1250)
    'CI2': [__ID(), False,],  # Central European (ISO-8859-2)
    'HEX': [__ID(), False,],  # Hexadecimal
}

#FIX, save/restore to/from config
# StatusBar conteXt menu: end of line
SBX_EOL = {
#   field:  id      checked
    'ECL': [__ID(), True,],   # CRLF (Windows)
    'ELF': [__ID(), False,],  # LF (Unix)
    'ECR': [__ID(), False,],  # CR (Mac)
    'EMX': [__ID(), False,],  # mixed EOLs
}

# ************************************** DEPRECATED ********
#FIX, save/restore to/from config
# StatusBar conteXt menu: Indentation
# SBX_IND = {
# #   field:  id             checked
#     'IUS': [MI['IND_IUS'], True,],   # indent using spaces
#     'TW1': [MI['IND_TW1'], False,],  # tab width: 1-8
#     'TW2': [MI['IND_TW2'], False,],
#     'TW3': [MI['IND_TW3'], False,],
#     'TW4': [MI['IND_TW4'], True,],
#     'TW5': [MI['IND_TW5'], False,],
#     'TW6': [MI['IND_TW6'], False,],
#     'TW7': [MI['IND_TW7'], False,],
#     'TW8': [MI['IND_TW8'], False,],
# }
# ************************************** DEPRECATED ********

# StatusBar Labels
SBL = {
    # line/column/length
    'LNC': 'Ln %d, Col %d, (%3d)',
    # insert/overwrite
    'INS': 'INS',
    'OVR': 'OVR',
    # Caps/Num/Scroll lock
    'CAP': 'C',
    'NUM': 'N',
    'SCL': 'S',
    # find/search, separator = '|'
    'SCH': 'Srch:',
    'CAS': 'Cs|',  # 'Case|',
    'REG': 'Re|',  # 'RE|',
    'WRD': 'Wd|',  # 'Word|',
    'WRP': '\u2195|',  # up/down arrow
    'ISL': 'Se|',
    'HLM': 'Hm|',
    'PCS': 'Pc|',
    'CXT': 'Cx|',
    'BUF': 'Bf|',
    # size
    'FSZ': 'File size: %d',
#FIX, field 'ENC' not implemented
    # file encoding
    'ENC': 'UTF-8',  # dummy
    # end of line
    'EOL': 'dummy',
#FIX, field 'IND' not implemented
    # indentation
    'IND': 'dummy',
}
