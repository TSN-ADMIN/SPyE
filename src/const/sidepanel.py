#!/usr/bin/python

from common.type import DotDict


SPT_TMPFIL_NAME = '$$$tmp$$$'  # temp filename

# Side Panel Tools (SPT), definitions
#TODO, add field 'python only'?
spt = (
#    key    label      accelerator  class          arg (doc)  singleton (1 control for all documents)
    ('DOC', 'Document',    'Alt+D', 'DocumentList',    True,  True, ),
    ('PRJ', 'Project',     'Alt+J', 'ProjectTree',     True,  True, ),
    ('BMK', 'Bookmark',    'Alt+B', 'BookmarkList',    True,  False,),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ('LNG', 'Language',    ''     , 'LanguageList',    False, True, ),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    ('FXP', 'Explorer',    'Alt+E', 'ExplorerTree',    True,  False,),
    ('SDF', 'Symbol',      'Alt+Y', 'SymbolTree',      True,  False,),
    ('MAC', 'Macro',       'Alt+M', 'MacroList',       False, True, ),
    ('TSK', 'Task',        'Alt+T', 'TaskList',        True,  False,),
    ('BPT', 'Breakpoint',  'Alt+K', 'BreakpointList',  True,  False,),
    ('DBG', 'Debug',       'Alt+G', 'DebugList',       False, True, ),
    ('DCM', 'DocMap',      'Alt+A', 'DocMap',          True,  False,),
    ('CFG', 'Config',      'Alt+F', 'ConfigList',      False, True, ),
    ('ENV', 'Environment', ''     , 'EnvironmentList', False, True, ),
    ('HLP', 'Help',        'Alt+H', 'HelpList',        False, True, ),
    ('PLT', 'Pylint',      'Alt+N', 'PylintList',      True,  False,),
    ('PFL', 'Pyflakes',    ''     , 'PyflakesList',    True,  False,),
    ('PYS', 'Pycodestyle', 'Alt+C', 'PycodestyleList', True,  False,),
    ('VLT', 'Vulture',     'Alt+V', 'VultureList',     True,  False,),
    ('MDN', 'Markdown',    'Alt+R', 'MarkdownHtml',    True,  False,),
    ('CFW', 'Code2flow',   'Alt+W', 'Code2flowGraph',  False, False,),
    ('DIA', 'Diagrams',    '',      'DiagramsGraph',   False, False,),
    ('SNP', 'Snippet',     'Alt+I', 'SnippetCode',     False, False,),
)

# create dotdict from tuple, while inserting choice ids (idx) from 0 to dict length
SPT = DotDict()

for idx, (key, lbl, acc, cls, arg, sgl) in enumerate(spt):
    SPT[key] = DotDict({'idx': idx, 'lbl': lbl, 'acc': acc, 'cls': cls, 'arg': arg, 'sgl': sgl})

del spt


# Side Panel Tools, NOT having ListCtrl as main control
SPT_NO_LCT = {'PRJ', 'FXP', 'SDF', 'DCM', 'MDN', 'CFW', 'DIA', 'SNP'}

# Side Panel Tools, ListCtrl column headers
# format: 'L'=Left, 'R'=Right, 'C'=Centre, -1=None
#HACK, -1 hides 'mandatory item image' in empty column 0
#INFO, see 'ListCtrlTool.add_item'
#INFO, URL=https://discuss.wxpython.org/t/listctrl-without-icons/34643/8
_empty = ('', -1),

SPT_COL_HEADERS = {
    # document
    'DOC': (
        *_empty,
        ('#',           'R'),
        ('Filename',    'L'),
        ('Dirname',     'L'),
        ('Language',    'L'),
        # ('Size',        -1),
    ),
    # bookmark
    'BMK': (
        *_empty,
        ('#',           'R'),
        ('Line',        'R'),
        # ('Col',         'R'),
        ('Source',      'L'),
    ),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # language
    'LNG': (
        *_empty,
        ('#',           'R'),
        ('Name',        'L'),
        ('Type',        'L'),
        ('Extension',   'L'),
    ),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # macro
    'MAC': (
        *_empty,
        ('Macro',       'L'),
        ('Description', 'L'),
    ),
    # task
    'TSK': (
        *_empty,
        ('Task',        'L'),
        ('Line',        'R'),
        ('Description', 'L'),
        ('Reserved',    'L'),
    ),
    # breakpoint
    'BPT': (
        *_empty,
        ('#',           'R'),
        ('Enabled',     'R'),
        ('Line',        'R'),
        ('Source',      'L'),
    ),
    # debug
    'DBG': (
        *_empty,
        ('Type',        'L'),
        ('Status',      'L'),
        ('Value',       'R'),
        ('Description', 'L'),
        ('Reserved',    'L'),
    ),
    # config
    'CFG': (
        *_empty,
        ('#',           'R'),
        ('Section',     'L'),
        ('Key',         'L'),
        ('Type',        'L'),
        ('Value',       'L'),
        ('Description', 'L'),
    ),
    # environment
    'ENV': (
        *_empty,
        ('Variable',    'L'),
        ('Value',       'L'),
    ),
    # help
    'HLP': (
        *_empty,
        ('Help',        'L'),
        ('Description', 'L'),
    ),
    # pylint
    'PLT': (
        *_empty,
        ('Line',        'R'),
        ('Col',         'R'),
        ('Category',    'L'),
        ('MsgId',       'L'),
        ('Symbol',      'L'),
        ('Object',      'L'),
        ('Message',     'L'),
    ),
    # pyflakes
    'PFL': (
        *_empty,
        ('Line',        'R'),
        ('Col',         'R'),
        # ('Category',    'L'),
        # ('MsgId',       'L'),
        # ('Symbol',      'L'),
        # ('Object',      'L'),
        ('Message',     'L'),
    ),
    # pycodestyle
    'PYS': (
        *_empty,
        ('Line',        'R'),
        ('Col',         'R'),
        ('MsgId',       'L'),
        ('Message',     'L'),
    ),
    # vulture
    'VLT': (
        *_empty,
        ('Line',        'R'),
        ('Message',     'L'),
    ),
}
del _empty

# task code tags
TSK_TAGS = (
    '#INFO',
    '#NOTE',
    '#TODO',
    '#FIX',
    '#DONE',
    '#HACK',
)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, temporary dummy lists (until respective SPT tools are implemented)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

SPT_DUMMY = {'MAC': {}, 'ENV': {}, 'HLP': {}, }

for k in SPT_DUMMY:
    for n in range(10):
        SPT_DUMMY[k][f'{k} {n}'] = f'dummy description {n}'
