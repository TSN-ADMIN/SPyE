#!/usr/bin/python

from common.util import not_implemented
from const.app import APP
from const import glb
from const.menubar import (
    NO_HLP, NO_ICO, NO_KND, NO_SCT, NO_UIH, SEP, MI, BMX, SDX, TSX, BPX, DMX
)
from const.statusbar import SBX, SBX_ENC, SBX_EOL
from const.toolbar import TBX
import gui


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, refactor 'if ref in' to dict with: key='ref', list=(sec, mnu, ttl)
CTX_REF_MAP = {
#    ---     -------------     --------------------------------
#    ref     sec               ttl
#    ---     -------------     --------------------------------
    'EDT': ('Editor',         'Editor',                           ),
    'MGN': ('Margin',         'Editor Margin',                    ),
    'NBK': ('Notebook',       'Notebook',                         ),
    'MBR': ('MenuBar',        'MenuBar',                          ),
    'TBR': ('ToolBar',        'ToolBar',                          ),
    'IBR': ('InfoBar',        'InfoBar',                          ),
    'SBR': ('StatusBar',      'StatusBar',                        ),
    'PSW': ('PanelSwitcher',  'Panel Switcher',                   ),
    'SCH': ('SearchFlags',    'Search Flags',                     ),
    'ENC': ('FileEncoding',   'File Encoding (not implemented)',  ),
    'EOL': ('EndOfLine',      'End of Line',                      ),
    'IND': ('Indentation',    'Indentation (almost implemented)', ),
    'LNG': ('Language',       'Language',                         ),
    'RLR': ('Ruler',          'Ruler',                            ),
    'CCX': ('CodeContext',    'Code Context',                     ),
    'BMK': ('BookmarkList',   'Bookmark',                         ),
    'SDF': ('SymbolDef',      'Symbol Def',                       ),
    'TSK': ('TaskList',       'Task',                             ),
    'BPT': ('BreakpointList', 'Breakpoint',                       ),
    'DCM': ('DocMap',         'DocMap',                           ),
    'FNF': ('FindHistory',    'Find Field History',               ),
    'RPF': ('ReplaceHistory', 'Replace Field History',            ),
    'WHF': ('WhereHistory',   'Where Field History',              ),
    'WHR': ('WhereButton',    'Where',                            ),
    'RES': ('SearchResults',  'Search Results',                   ),
}

BEWARE_ = ('WHR', 'WhereButton', '-> NEW in SPyE.cfg')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


def context_menu_defs(tlw, sub_lst):
#NOTE, prevent circular dependency
    from common.file import win32_file_properties

    sch, ind, lng = sub_lst

#DONE, add context menu title (through reference); see 'ref' in 'def ContextMenu'
    # context menu definitions
    CTX = {
        # MENUBAR
        'MBR': (
            ('&Customize...', NO_SCT, 'gui.CtxMenuBar', NO_HLP, 'customize', NO_KND, NO_UIH),  # MBX['CUS'][0]),
            (SEP),
            ('Show', NO_SCT, 'gui.CtxMenuBar', NO_HLP, NO_ICO, 'CHECK', NO_UIH, MI['LAY_MBR']),
        ),
        # TOOLBAR
        'TBR': (
            ('&Customize...', NO_SCT, 'gui.CtxToolBar', NO_HLP, 'customize', NO_KND, NO_UIH, TBX['CUS'][0]),
            (SEP),
            ('Show Icons', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'CHECK', NO_UIH, TBX['SHW_ICO'][0]),
            ('Show Text Labels', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'CHECK', NO_UIH, TBX['SHW_TXT'][0]),
            (SEP),
            ('Large Icons', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'CHECK', NO_UIH, TBX['LRG_ICO'][0]),
            ('Large Text Labels', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'CHECK', NO_UIH, TBX['LRG_TXT'][0]),
            ('Align Horizontally', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'CHECK', NO_UIH, TBX['ALN_HOR'][0]),
            (SEP),
            ('Align at Top', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'RADIO', NO_UIH, TBX['LOC_TOP'][0]),
            ('Align at Left', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'RADIO', NO_UIH, TBX['LOC_LFT'][0]),
            ('Align at Bottom', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'RADIO', NO_UIH, TBX['LOC_BOT'][0]),
            ('Align at Right', NO_SCT, 'gui.CtxToolBar', NO_HLP, NO_ICO, 'RADIO', NO_UIH, TBX['LOC_RIT'][0]),
        ),
        # INFOBAR
        'IBR': (
            ('&Customize...', NO_SCT, 'gui.CtxInfoBar', NO_HLP, 'customize', NO_KND, NO_UIH),  # IBX['CUS'][0]),
            (SEP),
            ('Show', NO_SCT, 'gui.CtxInfoBar', NO_HLP, NO_ICO, 'CHECK', NO_UIH, MI['LAY_IBR']),
        ),
        # STATUSBAR: main
        'SBR': (
            ('Select All', NO_SCT, 'gui.CtxStatusBarMain', 'Select all statusbar fields', NO_ICO, 'RADIO', NO_UIH, SBX.ALL.id),
            ('Select None', NO_SCT, 'gui.CtxStatusBarMain', 'Deselect all statusbar fields', NO_ICO, 'RADIO', NO_UIH, SBX.NON.id),
            ('Customize...', NO_SCT, 'gui.CtxStatusBarMain', 'Custom selection dialog for statusbar fields', 'customize', 'RADIO', NO_UIH, SBX.CUS.id),
            (SEP),
            ('Panel switcher', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.PSW.id),
            ('Message', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.MSG.id),
            ('Auxiliary', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.AUX.id),
            (SEP),
            ('Ln xx, Col yy', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.LNC.id),
            ('INS/OVR', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.INS.id),
            ('Caps/Num/Scroll', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.CNS.id),
            (SEP),
            ('Search flags', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.SCH.id),
            ('File size', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.FSZ.id),
            (SEP),
            ('File encoding', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.ENC.id),
            ('Line endings', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.EOL.id),
            ('Indentation', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.IND.id),
            ('Language', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.LNG.id),
            (SEP),
            ('Clock time', NO_SCT, 'gui.CtxStatusBarMain', NO_HLP, NO_ICO, 'CHECK', NO_UIH, SBX.TIM.id),
        ),
        # STATUSBAR: panel switcher
#TODO, create 16x16/24x24 icons (for now use 'ruler_panel')
        'PSW': [
            ['Console Output', 'Ctrl+Shift+O', not_implemented, 'Show console output in bottom panel', 'ruler_panel', NO_KND, 'Doc'],
            (SEP),
            ['&Find...', 'Ctrl+F', 'tlw.set_search_mode', 'Find text dialog in search panel', 'ruler_panel', NO_KND, 'Doc', MI['SCH_FND']],
            ['&Replace...', 'Ctrl+H', 'tlw.set_search_mode', 'Replace text dialog in search panel', 'ruler_panel', NO_KND, 'Doc', MI['SCH_RPL']],
            ['Find in Files...', 'Ctrl+Shift+F', 'tlw.set_search_mode', 'Find/replace text in files dialog in search panel', 'ruler_panel', NO_KND, 'Doc', MI['SCH_FIF']],
            ['&Incremental Search...', 'Ctrl+I', 'tlw.set_search_mode', 'Progressively find text while typing', 'ruler_panel', NO_KND, 'Doc', MI['SCH_INC']],
            ['Search Results', 'Ctrl+Shift+R', 'tlw.set_search_mode', 'Show last search results in bottom panel', 'ruler_panel', NO_KND, 'Doc', MI['SCH_RES']],
            (SEP),
            ['&Search Panel', 'Alt+S', 'lambda e: glb.TLW.toggle_panel(e, "SCH", -1)', 'Toggle search panel visibility', 'search_panel', NO_KND, 'Doc', MI['LAY_SCH']],
            ['R&uler Panel', 'Alt+U', 'lambda e: glb.TLW.toggle_panel(e, "RLR", 1)', 'Toggle ruler visibility', 'ruler_panel', NO_KND, 'Doc', MI['LAY_RLR']],
            ['Side &Panel', 'Alt+P', 'lambda e: glb.TLW.toggle_panel(e, "SPN", -1)', 'Toggle side panel visibility', 'side_panel', NO_KND, 'Doc', MI['LAY_SPN']],
            ['C&ode Context Panel', 'Alt+O', 'lambda e: glb.TLW.toggle_panel(e, "CCX", 1)', 'Toggle code context window visibility', 'code_context', NO_KND, 'Doc', MI['LAY_CCX']],
        ],
        # STATUSBAR: search options
        'SCH': (
            sch
        ),
        # STATUSBAR: file encoding
        'ENC': (
            ('UTF-8', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.U08.id),
            ('UTF-16 LE', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.U6L.id),
            ('UTF-16 BE', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.U6B.id),
            (SEP),
            ('Western (Windows 1252)', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.WIN.id),
            ('Western (ISO-8859-1)', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.I01.id),
            ('Western (ISO-8859-3)', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.I03.id),
            ('Western (ISO-8859-15)', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.I15.id),
            ('Western (Mac Roman)', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.MAC.id),
            ('DOS (CP 437)', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.DOS.id),
            ('Central European (Windows 1250)', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.CW0.id),
            ('Central European (ISO-8859-2)', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.CI2.id),
            (SEP),
            ('Hexadecimal', NO_SCT, 'gui.CtxStatusBarENC', NO_HLP, 'prefs', 'CHECK', 'Doc', SBX_ENC.HEX.id),
        ),
    # menu item substitution: 'anti-redundancy' lambdas (returning a tuple)
        # STATUSBAR: end of line
        'EOL': (
            ('&Windows (CRLF)', NO_SCT, 'gui.CtxStatusBarEOL', NO_HLP, NO_ICO, 'RADIO', 'Doc', SBX_EOL.ECL.id),
            ('&Unix (LF)', NO_SCT, 'gui.CtxStatusBarEOL', NO_HLP, NO_ICO, 'RADIO', 'Doc', SBX_EOL.ELF.id),
            ('&Mac (CR)', NO_SCT, 'gui.CtxStatusBarEOL', NO_HLP, NO_ICO, 'RADIO', 'Doc', SBX_EOL.ECR.id),
            ('Mixed EOLs', NO_SCT, 'gui.CtxStatusBarEOL', NO_HLP, NO_ICO, 'RADIO', 'Doc', SBX_EOL.EMX.id),
            (SEP),
#INFO, URL=https://docs.python.org/howto/unicode.html
            ('U&nicode (UTF-8)', NO_SCT, not_implemented, NO_HLP, 'unicode'),
        ),
        # STATUSBAR: indentation
        'IND': (
            ind
        ),
        # STATUSBAR: language (syntax highlighting)
        'LNG': (
            lng
#INFO, URL=https://stackoverflow.com/questions/24419487/find-index-of-nested-item-in-python
            # 'Language' menu = [6][1] => [language list]
            # MNU[6][1]
            # 'View' menu = [2][1] + 'Syntax Highlighting' submenu = [9][1] => [language list]
            # MNU[2][1][9][1]
        ),
        # NOTEBOOK: page tab
        'NBK': (
            ('&Close', 'Ctrl+W', 'tlw.file_close', 'Close document', 'close'),
            (SEP),
            ('Close All Other', NO_SCT, 'tlw.file_close_other', 'Close all other documents', NO_ICO, NO_KND, NO_UIH, MI['NBK_CAO']),
            ('Close All Left', NO_SCT, 'tlw.file_close_left_or_right', 'Close all documents to left of this tab', NO_ICO, NO_KND, NO_UIH, MI['NBK_CAL']),
            ('Close All Right', NO_SCT, 'tlw.file_close_left_or_right', 'Close all documents to right of this tab', NO_ICO, NO_KND, NO_UIH, MI['NBK_CAR']),
            (SEP),
            ('&Split Editor', NO_SCT, 'tlw.split_editor', 'Split/Unsplit window for 2nd view of active document', 'close'),
            ('Cop&y Filename', NO_SCT, 'tlw.edit_copy_filename', 'Copy filename to clipboard', NO_ICO),
            (SEP),
            ('Windows File &Properties...', NO_SCT, win32_file_properties, 'Show Windows file properties', 'file_properties', NO_KND, NO_UIH, MI['NBK_WFP']),

        ),
        # EDITOR: main
        'EDT': (
            ('&CtxTEST1', NO_SCT, 'tlw.CtxTEST1', 'CtxTEST1', NO_ICO),
            ('&CtxTEST2', NO_SCT, 'tlw.CtxTEST2', 'CtxTEST2', NO_ICO),
            ('&CtxTEST3 - Background Colour', NO_SCT, 'tlw.CtxTEST3', 'CtxTEST3', NO_ICO),
            ('&CtxTEST4 - Application Theme', NO_SCT, 'tlw.CtxTEST4', 'CtxTEST4', NO_ICO),
            (SEP),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # ('Open &File', NO_SCT, 'tlw.file_open_at_caret', 'Open filename at caret in new tab', 'open', NO_KND, 'Doc'),
                # ('Open &URL', NO_SCT, 'tlw.file_open_at_caret', 'Open URL at caret in browser', 'open', NO_KND, 'Doc'),
                # (SEP),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            ('Style Token', NO_SCT, [
                ('Using 1st Style', NO_SCT, 'tlw.edit_mark_matches', NO_HLP, 'style_token_1_16', NO_KND, 'Sel', MI['EDT_MS1']),
                ('Using 2nd Style', NO_SCT, 'tlw.edit_mark_matches', NO_HLP, 'style_token_2_16', NO_KND, 'Sel', MI['EDT_MS2']),
                ('Using 3rd Style', NO_SCT, 'tlw.edit_mark_matches', NO_HLP, 'style_token_3_16', NO_KND, 'Sel', MI['EDT_MS3']),
                ('Using 4th Style', NO_SCT, 'tlw.edit_mark_matches', NO_HLP, 'style_token_4_16', NO_KND, 'Sel', MI['EDT_MS4']),
                ('Using 5th Style', NO_SCT, 'tlw.edit_mark_matches', NO_HLP, 'style_token_5_16', NO_KND, 'Sel', MI['EDT_MS5']),
            ], 'Mark all like selected', NO_ICO, NO_KND, 'Doc'),
            ('Remove Style', NO_SCT, [
                ('Clear 1st Style', NO_SCT, 'tlw.edit_mark_matches_clear', NO_HLP, 'style_token_1_16', NO_KND, NO_UIH, MI['EDT_CS1']),
                ('Clear 2nd Style', NO_SCT, 'tlw.edit_mark_matches_clear', NO_HLP, 'style_token_2_16', NO_KND, NO_UIH, MI['EDT_CS2']),
                ('Clear 3rd Style', NO_SCT, 'tlw.edit_mark_matches_clear', NO_HLP, 'style_token_3_16', NO_KND, NO_UIH, MI['EDT_CS3']),
                ('Clear 4th Style', NO_SCT, 'tlw.edit_mark_matches_clear', NO_HLP, 'style_token_4_16', NO_KND, NO_UIH, MI['EDT_CS4']),
                ('Clear 5th Style', NO_SCT, 'tlw.edit_mark_matches_clear', NO_HLP, 'style_token_5_16', NO_KND, NO_UIH, MI['EDT_CS5']),
                (SEP),
                ('Clear all Styles', NO_SCT, 'tlw.edit_mark_matches_clear', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['EDT_CSA']),
            ], 'Clear all like selected', NO_ICO, NO_KND, 'Doc'),
            (SEP),
            ('&Split...', NO_SCT, 'tlw.edit_split_text', 'Split Text', 'split', NO_KND, 'Sel'),
            ('&Join...', NO_SCT, 'tlw.edit_join_text', 'Join Text', 'join', NO_KND, 'Sel'),
            ('&Hide Lines', NO_SCT, 'tlw.edit_hide_lines', 'Hide Selected Lines', 'hidelines', NO_KND, 'Sel'),
            (SEP),
            ('Cu&t', NO_SCT, 'tlw.edit_clipboard', 'Cut to clipboard', 'cut', NO_KND, 'Sel', MI['EDT_CUT']),  # EditCut
            ('&Copy', NO_SCT, 'tlw.edit_clipboard', 'Copy to clipboard', 'copy', NO_KND, 'Sel', MI['EDT_CPY']),  # EditCopy
            ('&Paste', NO_SCT, 'tlw.edit_clipboard', 'Paste from clipboard', 'paste', NO_KND, 'Doc', MI['EDT_PST']),  # EditPaste
            (SEP),
            ('&Delete', NO_SCT, 'tlw.edit_delete', 'Delete selection', 'delete', NO_KND, 'Sel'),
            ('Select &All', NO_SCT, 'tlw.select_all', 'Select all text', 'select_all', NO_KND, 'Doc'),
            ('&Mark Matches', NO_SCT, 'tlw.edit_mark_matches', 'Mark all occurrences of selected text', 'select_all', NO_KND, 'Sel', MI['EDT_MS0']),
            (SEP),
            ('&Undo', NO_SCT, 'tlw.edit_undo', 'Undo last action', 'undo', NO_KND, 'Doc'),
            ('&Redo', NO_SCT, 'tlw.edit_redo', 'Redo last action', 'redo', NO_KND, 'Doc'),
        ),
        # EDITOR: margin
        'MGN': (
            ('Delete All Bookmarks', NO_SCT, 'tlw.delete_all_bookmarks', NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MGN_DBM']),
            ('Delete All Breakpoints', NO_SCT, 'tlw.delete_all_breakpoints', NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MGN_DBP']),
            ('Delete All Task Markers', NO_SCT, 'tlw.delete_all_task_markers', NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MGN_DTM']),
            (SEP),
            ('Delete All Markers', NO_SCT, 'tlw.delete_all_markers', NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MGN_DAM']),
            (SEP),
            ('Dummy updateui_sel', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Sel'),
            ('Dummy updateui_mod', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Mod'),
            ('Dummy updateui_sch', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Sch'),
            ('Dummy None', NO_SCT, not_implemented),
        ),
        # RULER
        'RLR': (
            ('&Customize...', NO_SCT, not_implemented, NO_HLP, 'customize'),
            (SEP),
            ('&Large Buttons', NO_SCT, not_implemented, NO_HLP, NO_ICO, 'CHECK'),
            ('&Text Labels', NO_SCT, not_implemented, NO_HLP, NO_ICO, 'CHECK'),
        ),
        # CODE CONTEXT
        'CCX': (
            ('&Customize...', NO_SCT, not_implemented, NO_HLP, 'customize'),
            (SEP),
            ('&Large Buttons', NO_SCT, not_implemented, NO_HLP, NO_ICO, 'CHECK'),
            ('&Text Labels', NO_SCT, not_implemented, NO_HLP, NO_ICO, 'CHECK'),
        ),
        # SIDE PANEL: bookmarks
        'BMK': (
            ('Delete', 'Delete',' gui.CtxBookmarkList', NO_HLP, NO_ICO, NO_KND, NO_UIH, BMX['DEL']),
            ('Go to', 'Enter',' gui.CtxBookmarkList', NO_HLP, NO_ICO, NO_KND, NO_UIH, BMX['GTO']),
        ),
        # SIDE PANEL: symbol defs
        'SDF': (
            ('Expand All', NO_SCT, 'gui.CtxSymbolDef', NO_HLP, NO_ICO, NO_KND, NO_UIH, SDX['EXP']),
            ('Collapse All', NO_SCT, 'gui.CtxSymbolDef', NO_HLP, NO_ICO, NO_KND, NO_UIH, SDX['COL']),
        ),
        # SIDE PANEL: tasks
        'TSK': (
            ('Delete', 'Delete',' gui.CtxTaskList', NO_HLP, NO_ICO, NO_KND, NO_UIH, TSX['DEL']),
            ('Go to', 'Enter',' gui.CtxTaskList', NO_HLP, NO_ICO, NO_KND, NO_UIH, TSX['GTO']),
        ),
        # SIDE PANEL: breakpoints
        'BPT': (
            ('Enable/Disable', 'Insert',' gui.CtxBreakpointList', NO_HLP, NO_ICO, NO_KND, NO_UIH, BPX['ENA']),
            ('Delete', 'Delete',' gui.CtxBreakpointList', NO_HLP, NO_ICO, NO_KND, NO_UIH, BPX['DEL']),
            ('Go to', 'Enter',' gui.CtxBreakpointList', NO_HLP, NO_ICO, NO_KND, NO_UIH, BPX['GTO']),
        ),
        # SIDE PANEL: doc map
        'DCM': (
            ('ZoneRectRounded', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['ZRC_RND'][0]),
            ('ZoneCentreLine', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['ZCT_LIN'][0]),
            ('ZoneCentreDot', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['ZCT_DOT'][0]),
            (SEP),
            ('EdgeTextIndicator', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['EDG_TXT'][0]),
            ('AutoFocus', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['AUT_FCS'][0]),
            ('MarkerLineHighlight', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['MRK_LHL'][0]),
            ('SnapCursorAtDragStart', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['SNP_CDS'][0]),
            (SEP),
            ('CodePreview', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['COD_PVW'][0]),
            ('CodePreview: Caption', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['COD_CAP'][0]),
            ('CodePreview: Border', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['COD_BRD'][0]),
            ('CodePreview: Margin', NO_SCT, 'gui.CtxDocMap', NO_HLP, NO_ICO, 'CHECK', NO_UIH, DMX['COD_MGN'][0]),
        ),
        # SEARCH PANEL: where filter in 'Find In Files'
        'WHR': (
            ('Clear', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_CLE']),
            (SEP),
            ('Read Filters from File', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_FFF']),
            (SEP),
            ('Add Folder', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_FDR']),
            (SEP),
            ('Add Include Filter (extension)', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_IFE']),
            ('Add Include Filter (path)', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_IFP']),
            (SEP),
            ('Add Exclude Filter (extension)', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_EFE']),
            ('Add Exclude Filter (path)', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_EFP']),
            (SEP),
            ('Add Open Folders', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_OFD']),
            ('Add Open Files', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_OFL']),
            ('Add Current File', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_CFL']),
            (SEP),
            ('Preview Only (dry run)', NO_SCT, 'gui.CtxWhere', NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['WHR_PVW']),
        ),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # SEARCH PANEL: 'search results'
        'RES': (
            ('Goto File', NO_SCT, 'gui.CtxSearchResults', NO_HLP, NO_ICO),  # , NO_KND, NO_UIH, RSX['GTF']),  # or: MI['RES_GTF']
            ('Goto File, Line X', NO_SCT, 'gui.CtxSearchResults', NO_HLP, NO_ICO),  # , NO_KND, NO_UIH, RSX['GTL']),  # or: MI['RES_GTL']
            (SEP),
            ('Enable Mouse Input', NO_SCT, 'lambda e: glb.SCH.toggle_mouse_active(e, enable=True)', NO_HLP, NO_ICO),
            ('Disable Mouse Input', NO_SCT, 'lambda e: glb.SCH.toggle_mouse_active(e, enable=False)', NO_HLP, NO_ICO),
            # ('Toggle Mouse Input', NO_SCT, 'gui.CtxSearchResults', NO_HLP, NO_ICO),
            (SEP),
            ('Cu&t', NO_SCT, 'tlw.edit_clipboard', 'Cut to clipboard', 'cut', NO_KND, 'Sel', MI['EDT_CUT']),  # EditCut
            ('&Copy', NO_SCT, 'tlw.edit_clipboard', 'Copy to clipboard', 'copy', NO_KND, 'Sel', MI['EDT_CPY']),  # EditCopy
            ('&Paste', NO_SCT, 'tlw.edit_clipboard', 'Paste from clipboard', 'paste', NO_KND, 'Doc', MI['EDT_PST']),  # EditPaste
        ),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    }

        # SYSTEM TRAY MENU
    if glb.CFG['General']['SystemTrayMenu']:
        CTX['STM'] = (
#NOTE, pass 'action' (3rd parm) as 'string' to allow lazy loading
            ('Minimize/Restore Window[[bold]][[italic]][[underline]][[small]][[large]]', NO_SCT, 'glb.STM.toggle_main_window', 'Toggle minimize/restore main window'),
            (SEP),
            ('Full Screen', NO_SCT, 'glb.TLW.toggle_fullscreen', 'Toggle full screen visibility', 'fullscreen', NO_KND, NO_UIH, MI['LAY_FUL']),
            ('Preferences...', NO_SCT, 'glb.TLW.show_preferences', 'Application preferences', 'preferences'),
            (SEP),
            (f'Exit {APP["Base"]}', NO_SCT, 'glb.TLW.file_exit', 'Quit application: prompts to save modified documents', 'exit'),
        )
    return CTX
