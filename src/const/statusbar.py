#!/usr/bin/python

from copy import deepcopy

import wx

from common.type import DotDict


# new (window) ID ref: alias
__ID = wx.NewIdRef

# StatusBar: all fields with context menu
SBR_CTX_FIELDS = [
    'PSW',
    'SCH',
    'ENC',
    'EOL',
    'IND',
    'LNG'
]

# do NOT clear statusbar auxiliary field when it contains specified (sub)string(s)
SBF_NO_CLEAR_AUX = ['Sel:']  #, 'macro']  #, 'history']  #, 'mode']

# clock time: width including seconds (HH:MM:SS)
SBF_TIM_SECONDS_WIDTH = 45

#INFO, URL=https://stackoverflow.com/questions/16607704/one-liner-creating-a-dictionary-from-list-with-indices-as-keys
# StatusBar Fields (SBF), definitions
sbf = (
#    key   width  style
    ('PSW',   20, wx.SB_SUNKEN,),  # panel switcher icon (context menu)
    ('MSG',   -1, wx.SB_RAISED,),  # message
    ('AUX',  130, wx.SB_SUNKEN,),  # auxiliary
#   ------
    ('LNC',  100, wx.SB_RAISED,),  # Ln xx, Col yy
    ('INS',   25, wx.SB_SUNKEN,),  # INS/OVR
    ('CNS',   25, wx.SB_RAISED,),  # Caps/Num/Scroll lock
#   ------
    ('SCH',  140, wx.SB_SUNKEN,),  # search flags (context menu)
    ('FSZ',   85, wx.SB_RAISED,),  # file size
#   ------
#FIX, field 'ENC' not implemented
    ('ENC',   30, wx.SB_SUNKEN,),  # file encoding (context menu)
    ('EOL',   50, wx.SB_RAISED,),  # end of line (context menu)
#FIX, field 'IND' not implemented
    ('IND',   50, wx.SB_SUNKEN,),  # indentation (context menu)
#
    ('LNG',   75, wx.SB_RAISED,),  # language (context menu)
#   ------
    ('TIM',   25, wx.SB_SUNKEN,),  # clock time (HH:MM)
)

# create dotdict from tuple
SBF = DotDict()

for idx, (key, wid, sty) in enumerate(sbf):
    SBF[key] = DotDict({'idx': idx, 'wid': wid, 'sty': sty})

del sbf

# StatusBar Fields: COPY, used in 'CtxStatusBarMain'
SBF_CPY = deepcopy(SBF)

# StatusBar conteXt menu (SBX), definitions: main
sbx = (
#    key    checked  menu label
    ('ALL', True,    'Select All',),
    ('NON', False,   'Select None',),
    ('CUS', False,   'Custom...',),
    ('PSW', True,    'Panel switcher',),
    ('MSG', True,    'Message',),
    ('AUX', True,    'Auxiliary',),
    ('LNC', True,    'Ln xx, Col yy',),
    ('INS', True,    'INS/OVR',),
    ('CNS', True,    'Caps/Num/Scroll',),
    ('SCH', True,    'Search flags',),
    ('FSZ', True,    'File size',),
    ('ENC', True,    'File encoding',),
    ('EOL', True,    'Line endings',),
    ('IND', True,    'Indentation',),
    ('LNG', True,    'Language',),
    ('TIM', True,    'Clock time',),
)

# create dotdict from tuple
SBX = DotDict()

for (key, chk, lbl) in sbx:
    SBX[key] = DotDict({'id': __ID(), 'chk': chk, 'lbl': lbl})

del sbx

#FIX, save/restore to/from config
# StatusBar conteXt menu (SBX_ENC), definitions: file encoding
sbx_enc = (
#    key    checked
    ('U08', True,),   # UTF-8
    ('U6L', False,),  # UTF-16 LE
    ('U6B', False,),  # UTF-16 BE
    ('WIN', False,),  # Western (Windows 1252)
    ('I01', False,),  # Western (ISO-8859-1)
    ('I03', False,),  # Western (ISO-8859-3)
    ('I15', False,),  # Western (ISO-8859-15)
    ('MAC', False,),  # Western (Mac Roman)
    ('DOS', False,),  # DOS (CP 437)
    ('CW0', False,),  # Central European (Windows 1250)
    ('CI2', False,),  # Central European (ISO-8859-2)
    ('HEX', False,),  # Hexadecimal
)

# create dotdict from tuple
SBX_ENC = DotDict()

for (key, chk) in sbx_enc:
    SBX_ENC[key] = DotDict({'id': __ID(), 'chk': chk})

del sbx_enc

#FIX, save/restore to/from config
# StatusBar conteXt menu (SBX_EOL), definitions: end of line
sbx_eol = (
#    key    checked
    ('ECL', True,),   # CRLF (Windows)
    ('ELF', False,),  # LF (Unix)
    ('ECR', False,),  # CR (Mac)
    ('EMX', False,),  # mixed EOLs
)

# create dotdict from tuple
SBX_EOL = DotDict()

for (key, chk) in sbx_eol:
    SBX_EOL[key] = DotDict({'id': __ID(), 'chk': chk})

del sbx_eol

# StatusBar Labels
sbl = (
    # line/column/length
    ('LNC', 'Ln %d, Col %d, (%3d)',),
    # insert/overwrite
    ('INS', 'INS',),
    ('OVR', 'OVR',),
    # Caps/Num/Scroll lock
    ('CAP', 'C',),
    ('NUM', 'N',),
    ('SCL', 'S',),
    # find/search, separator = '|' (dynamically added at runtime)
    ('SCH', 'Srch:',),
    ('CAS', 'Cs',),  # 'Case',
    ('REG', 'Re',),  # 'RE',
    ('WRD', 'Wd',),  # 'Word',
    ('WRP', '\u2195',),  # up/down arrow
    ('ISL', 'Se',),
    ('HLM', 'Hm',),
    ('PCS', 'Pc',),
    ('CXT', 'Cx',),
    ('BUF', 'Bf',),
    # size
    ('FSZ', 'File size: %d',),
#FIX, field 'ENC' not implemented
    # file encoding
    ('ENC', 'UTF-8',),  # dummy
    # end of line
    ('EOL', 'dummy',),
#FIX, field 'IND' not implemented
    # indentation
    ('IND', 'dummy',),
)

# create dotdict from tuple
SBL = DotDict()

for (key, lbl) in sbl:
    SBL[key] = DotDict({'lbl': lbl})

del sbl

# ************************************** DEPRECATED ********
#FIX, save/restore to/from config
# StatusBar conteXt menu: Indentation
# SBX_IND = {
# #   key  :  id             checked
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
