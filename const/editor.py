#!/usr/bin/python

import string

from wx import stc

from const.app import CLR

# multiple selection keys
MSL_KEYS = (
#TODO, extend line based multiple selection
    # 'UP',
    # 'Shift+UP',
    # 'DOWN',
    # 'Shift+DOWN',
    'LEFT',
    'Shift+LEFT',
    'RIGHT',
    'Shift+RIGHT',
    'HOME',
    'Shift+HOME',
    'END',
    'Shift+END',
    'Ctrl+LEFT',
    'Ctrl+Shift+LEFT',
    'Ctrl+RIGHT',
    'Ctrl+Shift+RIGHT',
    'UP',
    'DOWN',
    'PAGEUP',
    'PAGEDOWN',
)

# Python debugger keys
PDB_KEYS = {
    'F2': 'start',       # start debugger
    'F5': 'continue',    # continue
    'F6': 'next',        # next
    'F7': 'step',        # step
    'F8': 'until',       # until
    'F9': 'break',       # break
    'F10': 'jump',       # jump
    'F11': 'return',     # return
    'F12': 'quit',       # quit

    # 'Fxx': 'break',      # break
    # 'Fxx': 'enable',     # enable
    # 'Fxx': 'disable',    # disable
    # 'Fxx': 'clear',      # clear
    # 'Fxx': 'where',      # where
    # 'Fxx': 'p',          # p
    # 'Fxx': 'pp',         # pp
    # 'Fxx': 'whatis',     # whatis
    # 'Fxx': 'display',    # display
    # 'Fxx': 'undisplay',  # undisplay
    # 'Fxx': 'retval',     # retval
}

# BRIEF multi-stroke keys
BRF_KEYS = {
#    Key    #pressed (max = 3)
    'HOME': 0,
    'END' : 0,
}

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, integrate in config file, not (properly) used yet
# End Of Line (newline) modes
EOL_MODES = {
    'CRLF': stc.STC_EOL_CRLF,
    'CR'  : stc.STC_EOL_CR,
    'LF'  : stc.STC_EOL_LF
}

# End Of Line (newline) characters
EOL_CHARS = {
    'CRLF': '\r\n',  # 'WIN', Windows
    'CR'  : '\r',    # 'MAC', Apple
    'LF'  : '\n'     # 'LNX', Linux/UNIX
}

# EOL modes/characters: aliases
EOM = EOL_MODES  # not used
EOC = EOL_CHARS  # not used

# editor: newline characters
CRLF = '\r\n'
CR = '\r'
LF = '\n'
NEWLINE = CRLF  # default
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# hotspot styling
DOC_STYLE_HOTSPOT = 4

#INFO, List of URI schemes
#INFO, URL=https://en.wikipedia.org/wiki/List_of_URI_schemes#Official_IANA-registered_schemes
#NOTE, used in 'file_open_at_caret'
URI_SCHEMES = (
    'about:',     # Displaying product information and internal information
    'chrome://',  # Used for the management of Google Chrome's settings.
    #@@@@@@@@@@ CH# ECK '://' vs ':///' @@@@@@@@@@@
                  # local/network files
    'file://',    # file://[host]/path or
    'file:///',   # (RFC 3986) file:[//host]/path
    #@@@@@@@@@@@@@# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    'ftp://',     # FTP resources
    'ftps://',    # FTP resources
    'git://',     # Provides a link to a GIT repository
    'http://',    # HTTP resources
    'https://',   # HTTP connections secured using SSL/TLS
    'imap://',    # Accessing e-mail resources through IMAP
    'ldap://',    # LDAP directory request
    'ldaps://',   # Secure equivalent of ldap
    'mailto:',    # SMTP e-mail addresses and default content
    'sftp://',    # SFTP file transfers (not be to confused with FTPS (FTP/SSL))
    'ssh://',     # SSH connections (like telnet:)
    'telnet://',  # Used with telnet
)

#INFO, URL=https://gist.github.com/jbjornson/1186126
#INFO, URL=https://stackoverflow.com/questions/1547899/which-characters-make-a-url-invalid/1547940#1547940

# valid characters (per category)
spc = ' '  # space char

CHARS = {
    # # filename characters (space included)
    # 'FNM': f'{spc}-_.(){string.ascii_letters}{string.digits}/:\\',
    # filename characters (NO space allowed)
    'FNM': f'-_.(){string.ascii_letters}{string.digits}/:\\',
    # URL characters (NO space allowed)
    'URL': f'-_.(){string.ascii_letters}{string.digits}/:~?#%[]@!$&*+,;=\'',
    # hex colour characters
    'HEX': f'#{string.hexdigits}',
    # named colour characters (space included)
    'CLR': f'{spc}{string.ascii_letters}',
}

#TODO, use 'enumerate', i.e. {k:v for v, k in enumerate((<list with keys>))}
# margin ids
MGN = {
    'NUM': 0,  # line numbers
    'SYM': 1,  # symbols (bookmarks/tasks)
    'FOL': 2,  # folders (code folding)
    'TXT': 3,  # left text
    'RTX': 4,  # right text
}

#NOTE, 'None' symbol markers use 'MarkerDefineBitmap'
# bookmark, task, breakpoint (disabled) and match markers
MRK = {
#  marker:  number    symbol                          mask
    'BMK': {'NUM':  0, 'SYM': stc.STC_MARK_CIRCLE,     'MSK': 2** 0},  # BookMarK
    'TSK': {'NUM':  1, 'SYM': stc.STC_MARK_DOTDOTDOT,  'MSK': 2** 1},  # TaSK
    'BPT': {'NUM':  2, 'SYM': stc.STC_MARK_CIRCLE,     'MSK': 2** 2},  # BreakPoinT: default
    'BPD': {'NUM':  3, 'SYM': stc.STC_MARK_MINUS,      'MSK': 2** 3},  # BreakPoint: Disabled
    'MCH': {'NUM':  4, 'SYM': stc.STC_MARK_SHORTARROW, 'MSK': 2** 4},  # MatCHes
    'HLS': {'NUM':  5, 'SYM': None,                    'MSK': 2** 5},  # Hidden Lines: Start
    'HLU': {'NUM':  6, 'SYM': stc.STC_MARK_UNDERLINE,  'MSK': 2** 6},  # Hidden Lines: Underline
    'HLE': {'NUM':  7, 'SYM': None,                    'MSK': 2** 7},  # Hidden Lines: End
    'DBC': {'NUM':  8, 'SYM': stc.STC_MARK_BACKGROUND, 'MSK': 2** 8},  # DeBug: Current line
    'DBE': {'NUM':  9, 'SYM': stc.STC_MARK_BACKGROUND, 'MSK': 2** 9},  # DeBug: Error line
    'BAB': {'NUM': 10, 'SYM': None,                    'MSK': 2**10},  # Brace: Angle Both,  '<>'
    'BAL': {'NUM': 11, 'SYM': None,                    'MSK': 2**11},  # Brace: Angle Left
    'BAR': {'NUM': 12, 'SYM': None,                    'MSK': 2**12},  # Brace: Angle Right
    'BCB': {'NUM': 13, 'SYM': None,                    'MSK': 2**13},  # Brace: Curly Both,  '{}'
    'BCL': {'NUM': 14, 'SYM': None,                    'MSK': 2**14},  # Brace: Curly Left
    'BCR': {'NUM': 15, 'SYM': None,                    'MSK': 2**15},  # Brace: Curly Right
    'BRB': {'NUM': 16, 'SYM': None,                    'MSK': 2**16},  # Brace: Round Both,  '()'
    'BRL': {'NUM': 17, 'SYM': None,                    'MSK': 2**17},  # Brace: Round Left
    'BRR': {'NUM': 18, 'SYM': None,                    'MSK': 2**18},  # Brace: Round Right
    'BSB': {'NUM': 19, 'SYM': None,                    'MSK': 2**19},  # Brace: Square Both, '[]'
    'BSL': {'NUM': 20, 'SYM': None,                    'MSK': 2**20},  # Brace: Square Left
    'BSR': {'NUM': 21, 'SYM': None,                    'MSK': 2**21},  # Brace: Square Right
}

#TODO, refactor 'FOL_STY_XXX'-> 'FOL_STY' dict
#TODO, use 'enumerate', i.e. FOL_STY = {k:v for v,k in enumerate((<list with keys>))}
#TODO, keys = ('NIL', 'ARW', 'PLM', 'CIR', 'SQR', )
# folding styles in margin: [0-4]
FOL_STY_NIL = 0  # EMPTY
FOL_STY_ARW = 1  # arrows
FOL_STY_PLM = 2  # plus/minus
FOL_STY_CIR = 3  # circular
FOL_STY_SQR = 4  # squared
# default folding style
FOL_STYLE = FOL_STY_CIR

# folding marker numbers
#TODO, needs better coding... -> fold_marker data in 1 dict
FOLD_MARKER_NUMS = (
    stc.STC_MARKNUM_FOLDEROPEN,
    stc.STC_MARKNUM_FOLDER,
    stc.STC_MARKNUM_FOLDERSUB,
    stc.STC_MARKNUM_FOLDERTAIL,
    stc.STC_MARKNUM_FOLDEREND,
    stc.STC_MARKNUM_FOLDEROPENMID,
    stc.STC_MARKNUM_FOLDERMIDTAIL,
)
#TODO, needs better coding... -> fold_style/_marker data in 1 dict
# FOLD_STYLES = {
#     FOL_STY_NIL: FOLD_MARKER_NUMS,
#     FOL_STY_ARW: FOLD_MARKER_NUMS,
#     FOL_STY_PLM: FOLD_MARKER_NUMS,
#     FOL_STY_CIR: FOLD_MARKER_NUMS,
#     FOL_STY_SQR: FOLD_MARKER_NUMS,
# }

#TODO, needs better coding... -> fold_style/_marker data in 1 dict
_empty = stc.STC_MARK_EMPTY

FOLD_MARKER_SYMBOLS = {
    FOL_STY_NIL: (
        'None',
        (_empty,                            'WHITE', 'WHITE'),
        (_empty,                            'WHITE', 'WHITE'),
        (_empty,                            'WHITE', 'WHITE'),
        (_empty,                            'WHITE', 'WHITE'),
        (_empty,                            'WHITE', 'WHITE'),
        (_empty,                            'WHITE', 'WHITE'),
        (_empty,                            'WHITE', 'WHITE'),
    ),
    FOL_STY_ARW: (
        'Arrow',
        (stc.STC_MARK_ARROWDOWN,            'BLACK', 'BLACK'),
        (stc.STC_MARK_ARROW,                'BLACK', 'BLACK'),
        (_empty,                            'BLACK', 'BLACK'),
        (_empty,                            'BLACK', 'BLACK'),
        (_empty,                            'WHITE', 'BLACK'),
        (_empty,                            'WHITE', 'BLACK'),
        (_empty,                            'WHITE', 'BLACK'),
    ),
    FOL_STY_PLM: (
        'Plus/Minus',
        (stc.STC_MARK_MINUS,                'WHITE', 'BLACK'),
        (stc.STC_MARK_PLUS,                 'WHITE', 'BLACK'),
        (_empty,                            'WHITE', 'BLACK'),
        (_empty,                            'WHITE', 'BLACK'),
        (_empty,                            'WHITE', 'BLACK'),
        (_empty,                            'WHITE', 'BLACK'),
        (_empty,                            'WHITE', 'BLACK'),
    ),
    FOL_STY_CIR: (
        'Circle',
        (stc.STC_MARK_CIRCLEMINUS,          'WHITE', CLR['GREY2']),
        (stc.STC_MARK_CIRCLEPLUS,           'WHITE', CLR['GREY2']),
        (stc.STC_MARK_VLINE,                'WHITE', CLR['GREY2']),
        (stc.STC_MARK_LCORNERCURVE,         'WHITE', CLR['GREY2']),
        (stc.STC_MARK_CIRCLEPLUSCONNECTED,  'WHITE', CLR['GREY2']),
        (stc.STC_MARK_CIRCLEMINUSCONNECTED, 'WHITE', CLR['GREY2']),
        (stc.STC_MARK_TCORNERCURVE,         'WHITE', CLR['GREY2']),
    ),
    FOL_STY_SQR: (
        'Square',
        (stc.STC_MARK_BOXMINUS,             'WHITE', 'GREY'),
        (stc.STC_MARK_BOXPLUS,              'WHITE', 'GREY'),
        (stc.STC_MARK_VLINE,                'WHITE', 'GREY'),
        (stc.STC_MARK_LCORNER,              'WHITE', 'GREY'),
        (stc.STC_MARK_BOXPLUSCONNECTED,     'WHITE', 'GREY'),
        (stc.STC_MARK_BOXMINUSCONNECTED,    'WHITE', 'GREY'),
        (stc.STC_MARK_TCORNER,              'WHITE', 'GREY'),
    ),
}
del _empty
