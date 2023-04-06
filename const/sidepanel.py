#!/usr/bin/python

SPT_TMPFIL_NAME = '$$$tmp$$$'  # temp filename

# # #INFO, URL=https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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
    ('HLP', 'Help',        'Alt+H', 'HelpList',        False, True, ),
    ('PLT', 'Pylint',      'Alt+N', 'PylintList',      True,  False,),
    ('PFL', 'Pyflakes',    ''     , 'PyflakesList',    True,  False,),
    ('PYS', 'Pycodestyle', 'Alt+C', 'PycodestyleList', True,  False,),
    ('VLT', 'Vulture',     'Alt+V', 'VultureList',     True,  False,),
    ('MDN', 'Markdown',    'Alt+R', 'MarkdownHtml',    False, False,),
    ('CFW', 'Code2flow',   'Alt+W', 'Code2flowGraph',  False, False,),
    ('SNP', 'Snippet',     'Alt+I', 'SnippetCode',     False, False,),
)

# create dict from tuple, while inserting choice ids (idx) from 0 to dict length
SPT = DotDict()

for idx, (key, lbl, acc, cls, arg, sgl) in enumerate(spt):
    SPT[key] = DotDict({'idx': idx, 'lbl': lbl, 'acc': acc, 'cls': cls, 'arg': arg, 'sgl': sgl})

del spt


# Side Panel Tools, ListCtrl column headers
# format: 'L'=Left, 'R'=Right, 'C'=Centre, -1=None
#HACK: -1 hides 'mandatory item image' in empty column 0
#INFO, see 'ListCtrlTool.add_item'
#INFO, URL=https://discuss.wxpython.org/t/listctrl-without-icons/34643/8
_empty = ('', -1),

SPT_COL_HEADERS = {
    # document
    'DOC': (
        *_empty,
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
        ('Name',        'R'),
        ('Type',        'R'),
        ('Extension',   'R'),
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
