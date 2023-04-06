#!/usr/bin/python

from wx import stc

from common.util import not_implemented
from const.app import APP
from const import glb
from const.lang import LANG
from const.menu import NO_HLP, NO_ICO, NO_KND, NO_SCT, NO_UIH, SEP, MI
from const.statusbar import SBL
import gui


def search_submenu_defs(tlw):
    fnc = tlw.toggle_search_option

    sch = [
        (f'&Case Sensitive   [{SBL["CAS"][:-1]}]', 'Ctrl+F5', fnc, 'Toggle case sensitive search', 'sch_cas_16', 'CHECK', 'Sch', MI['SCH_CAS']),
        (f'Regular E&xpression   [{SBL["REG"][:-1]}]', 'Ctrl+F6', fnc, 'Toggle regular expression search', 'sch_reg_16', 'CHECK', 'Sch', MI['SCH_REG']),
        (f'Whole &Words Only   [{SBL["WRD"][:-1]}]', 'Ctrl+F7', fnc, 'Toggle whole words only search', 'sch_wrd_16', 'CHECK', 'Sch', MI['SCH_WRD']),
        (SEP),
        (f'Wrap &Around   [{SBL["WRP"][:-1]}]', 'Ctrl+F8', fnc, 'Toggle wrap around search', 'sch_wrp_cus_16', 'CHECK', 'Sch', MI['SCH_WRP']),
        (f'In &Selection   [{SBL["ISL"][:-1]}]', 'Ctrl+F9', fnc, 'Toggle in selection search', 'sch_isl_16', 'CHECK', 'Sch', MI['SCH_ISL']),
        (f'Hig&hlight Matches   [{SBL["HLM"][:-1]}]', 'Ctrl+F10', fnc, 'Toggle highlight matches search', 'sch_hlm_16', 'CHECK', 'Sch', MI['SCH_HLM']),
        (SEP),
        (f'&Preserve Case   [{SBL["PCS"][:-1]}]', 'Ctrl+F11', fnc, 'Toggle preserve case search', 'sch_pcs_16', 'CHECK', 'Sch', MI['SCH_PCS']),
        (SEP),
        (f'Show conte&xt   [{SBL["CXT"][:-1]}]', NO_SCT, fnc, 'Toggle show context in search results', 'sch_cxt_16', 'CHECK', 'Sch', MI['SCH_CXT']),
        (f'Use &buffer   [{SBL["BUF"][:-1]}]', NO_SCT, fnc, 'Toggle use buffer for search results', 'sch_buf_16', 'CHECK', 'Sch', MI['SCH_BUF']),
    ]

    return sch

def indentation_submenu_defs(tlw):
#HACK: helper function to generate tab width menu items in 'IND' (context) menu
    fnc = gui.CtxStatusBarIND
    _ind_twn = lambda num: (f'Tab width: {num}', NO_SCT, fnc, NO_HLP, NO_ICO, 'RADIO', 'Doc', MI[f'IND_TW{num}'])

    ind = [
        ('Indent using spaces', NO_SCT, fnc, NO_HLP, NO_ICO, 'CHECK', 'Doc', MI['IND_IUS']),
        (SEP),
#FIX, this starred expression does NOT work in Python 3.9/3.10
#INFO, URL=https://bugs.python.org/issue40631
        *(_ind_twn(n) for n in range(1, 9)),
        # (*(_ind_twn(n) for n in range(1, 9))),
        (SEP),
        ('Guess settings from buffer', NO_SCT, fnc, NO_HLP, 'prefs', NO_KND, 'Doc', MI['IND_GSB']),
        (SEP),
        ('Convert indentation to spaces', NO_SCT, fnc, NO_HLP, 'prefs', NO_KND, 'Doc', MI['IND_ITS']),
        ('Convert indentation to tabs', NO_SCT, fnc, NO_HLP, 'prefs', NO_KND, 'Doc', MI['IND_ITT']),
    ]

    return ind

def language_submenu_defs(tlw):
#HACK: helper function to generate language menu items in 'LNG' (context) menu
    fnc = tlw.update_styling
    _lng_mni = lambda nam, mni: (f'&{nam}', NO_SCT, fnc, f'Syntax highlighting for [{nam}] documents', NO_ICO, 'RADIO', NO_UIH, mni)

    lng = [
#INFO, see 5th paragraph, risky when menu item is not part of a radio group
#INFO, URL=https://docs.wxpython.org/wx.Menu.html#phoenix-title-wx-menu
        ('&Keyword Sets', NO_SCT, [
              (SEP),  # dummy
        ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_KWS']),
        (SEP),
#FIX, this starred expression does NOT work in Python 3.9/3.10
        *(_lng_mni(i[2], i[4]) for i in LANG if i[0] != stc.STC_LEX_NULL),
        # (*(_lng_mni(i[2], i[4]) for i in LANG if i[0] != stc.STC_LEX_NULL)),
        ('&No highlighting', NO_SCT, fnc, 'No syntax highlighting', NO_ICO, 'RADIO', NO_UIH, MI['LNG_NULL']),
    ]

    return lng

def menubar_defs(tlw, sch, ind, lng):

    # mxi = glb.RFH['RecentFileHistory']['MaxItems']
    #           (f'Open Recen&t (max: {mxi})', NO_SCT, [

    FIL = ('&File', [
              ('&New', 'Ctrl+N', tlw.file_new, 'Create new document', 'new', NO_KND, NO_UIH, MI['FIL_NEW']),
              ('&Open...', 'Ctrl+O', tlw.file_open, 'Open existing document', 'open', NO_KND, NO_UIH, MI['FIL_OPN']),
              ('&Quick Open...', 'Ctrl+Q', tlw.file_quick_open, 'Quickly open existing document(s)', 'save', NO_KND, NO_UIH, MI['FIL_QOP']),
              ('Open Recen&t', NO_SCT, [
                  ('Reopen Closed File', 'Ctrl+Shift+T', tlw.file_reopen_closed_from_history, 'Reopen closed document from history', NO_ICO, NO_KND, 'His', MI['FIL_RCF']),
                  ('Reopen All Closed File(s)', NO_SCT, tlw.file_reopen_closed_from_history, 'Reopen all closed document(s) from history', NO_ICO, NO_KND, 'His', MI['FIL_RCA']),
                  ('Clear Items', NO_SCT, tlw.file_clear_history, 'Clear recent file history', NO_ICO, NO_KND, 'His', MI['FIL_CLI']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_RFH']),
              (SEP),
              ('&Save', 'Ctrl+S', tlw.file_save, 'Save active document', 'save', NO_KND, 'Mod', MI['FIL_SAV']),
              ('Save &As...', 'Ctrl+Shift+S', tlw.file_save_as, 'Save active document with new name', 'save_as', NO_KND, 'Doc', MI['FIL_SAS']),
              ('Save A&ll', NO_SCT, tlw.file_save_all, 'Save all modified documents', 'save_all', NO_KND, 'Mod', MI['FIL_SVA']),
              (SEP),
              ('&Rename...', NO_SCT, tlw.file_rename, 'Rename active document and file', NO_ICO, NO_KND, 'Doc', MI['FIL_REN']),
              ('Re&vert to Saved...', NO_SCT, tlw.file_revert_to_saved, 'Reload active document and lose changes', NO_ICO, NO_KND, 'Mod', MI['FIL_RVS']),
              ('Change to &Directory...', NO_SCT, tlw.file_change_directory, 'Change to selected directory from dialog', NO_ICO, NO_KND, NO_UIH, MI['FIL_CHD']),
              ('Change to File &Directory', NO_SCT, tlw.file_change_to_file_directory, 'Change to active document\'s directory', NO_ICO, NO_KND, 'Doc', MI['FIL_CFD']),
              (SEP),
              ('&Insert File at Current Position...', NO_SCT, tlw.file_insert_file, 'Insert file at current position of active document', NO_ICO, NO_KND, 'Doc', MI['FIL_INS']),
              ('A&ppend File...', NO_SCT, tlw.file_append_file, 'Insert file at end of active document', NO_ICO, NO_KND, 'Doc', MI['FIL_APD']),
              ('&Write Block to File...', NO_SCT, tlw.file_write_block_to_file, 'Save selection to file', NO_ICO, NO_KND, 'Sel', MI['FIL_WBL']),
              (SEP),
              ('New Window', NO_SCT, tlw.file_new_window, 'Open new application window', NO_ICO, NO_KND, 'Doc', MI['FIL_NWN']),
              ('Close Window', NO_SCT, tlw.file_new_window, 'Close active application window', NO_ICO, NO_KND, 'Doc', MI['FIL_CWN']),
              (SEP),
              ('&Close', 'Ctrl+W', tlw.file_close, 'Close active document', 'close', NO_KND, 'Doc', MI['FIL_CLS']),
              ('C&lose All', 'Ctrl+Shift+F4', tlw.file_close_all, 'Close all documents', 'close_all', NO_KND, 'Doc', MI['FIL_CLA']),
              ('Close All &Except This', 'Ctrl+Alt+Shift+F4', tlw.file_close_other, 'Close all documents except active document', 'close_all', NO_KND, 'Doc', MI['FIL_CAE']),
              (SEP),
              ('E&xit', 'Alt+X', tlw.file_exit, 'Quit application: prompts to save modified documents', 'exit', NO_KND, NO_UIH, MI['FIL_XIT']),
          ])

    EDT = ('&Edit', [
              ('&Undo', 'Ctrl+Z', tlw.edit_undo, 'Undo last action', 'undo', NO_KND, 'Doc', MI['EDT_UDO']),
              ('&Redo', 'Ctrl+Shift+Z', tlw.edit_redo, 'Redo last action', 'redo', NO_KND, 'Doc', MI['EDT_RDO']),
              (SEP),
              ('Cu&t', 'Ctrl+X', tlw.edit_clipboard, 'Cut to clipboard', 'cut', NO_KND, 'Sel', MI['EDT_CUT']),
              ('&Copy', 'Ctrl+C', tlw.edit_clipboard, 'Copy to clipboard', 'copy', NO_KND, 'Sel', MI['EDT_CPY']),
              ('&Paste', 'Ctrl+V', tlw.edit_clipboard, 'Paste from clipboard', 'paste', NO_KND, 'Doc', MI['EDT_PST']),
              ('&Delete', 'Backspace', tlw.edit_delete, 'Delete selection', 'delete', NO_KND, 'Sel', MI['EDT_DEL']),
              ('Cop&y Filename', NO_SCT, tlw.edit_copy_filename, 'Copy filename to clipboard', NO_ICO, NO_KND, 'Doc', MI['EDT_CPF']),
              (SEP),
              ('C&aret Operations', NO_SCT, [
                  ('Move to &Top', 'Ctrl+Alt+Shift+T', tlw.edit_move_caret_to, 'Move caret to top of screen', NO_ICO, NO_KND, 'Doc', MI['CRT_TOP']),
                  ('Move to &Centre', 'Ctrl+Alt+Shift+C', tlw.edit_move_caret_to, 'Move caret to centre of screen', NO_ICO, NO_KND, 'Doc', MI['CRT_CTR']),
                  ('Move to &Bottom', 'Ctrl+Alt+Shift+B', tlw.edit_move_caret_to, 'Move caret to bottom of screen', NO_ICO, NO_KND, 'Doc', MI['CRT_BOT']),
                  (SEP),
                  ('&Next Paragraph', 'Alt+Shift+Down', tlw.edit_goto_paragraph, 'Go to next paragraph (delimited by empty lines)', NO_ICO, NO_KND, 'Doc', MI['PAR_NXT']),
                  ('&Previous Paragraph', 'Alt+Shift+Up', tlw.edit_goto_paragraph, 'Go to previous paragraph (delimited by empty lines)', NO_ICO, NO_KND, 'Doc', MI['PAR_PRV']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_CRO']),
              ('&Line Operations', NO_SCT, [
                  ('Duplicate &Line', 'Ctrl+Shift+D', tlw.edit_duplicate_line, 'Duplicate current line', 'dup_line', NO_KND, 'Doc', MI['EDT_DPL']),
                  ('Transpose L&ine', 'Ctrl+T', tlw.edit_transpose_line, 'Switch current line with previous', 'transpose', NO_KND, 'Doc', MI['EDT_TPL']),
                  (SEP),
                  ('Scroll Line to T&op', 'Ctrl+Alt+T', tlw.edit_scroll_line_to, 'Scroll current line to top of screen', NO_ICO, NO_KND, 'Doc', MI['LIN_TOP']),
                  ('Scroll Line to C&entre', 'Ctrl+Alt+C', tlw.edit_scroll_line_to, 'Scroll current line to centre of screen', NO_ICO, NO_KND, 'Doc', MI['LIN_CTR']),
                  ('Scroll Line to &Bottom', 'Ctrl+Alt+B', tlw.edit_scroll_line_to, 'Scroll current line to bottom of screen', NO_ICO, NO_KND, 'Doc', MI['LIN_BOT']),
                  (SEP),
                  ('Move Selection Down', 'Ctrl+Shift+Down', tlw.edit_move_selected_lines, 'Move selected line(s) down', NO_ICO, NO_KND, 'Sel', MI['LIN_SLD']),
                  ('Move Selection Up', 'Ctrl+Shift+Up', tlw.edit_move_selected_lines, 'Move selected line(s) up', NO_ICO, NO_KND, 'Sel', MI['LIN_SLU']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_LNO']),
              (SEP),
#TODO, NO_HLP = 'Show calltip for text under mouse cursor' ??
              ('Calltip', 'Ctrl+Alt+Space', tlw.edit_calltip, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['EDT_CTP']),
#TODO, NO_HLP = 'Show autocompletions based on typed characters' ??
              ('Autocomplete', 'Ctrl+Space', tlw.edit_autocomplete, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['EDT_ACP']),
#TODO, Autocomplete vs IntelliSense ??
              # ('IntelliSense', 'Ctrl+Alt+Space', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'),
#TODO, NO_HLP = 'Expand word based on typed characters' ??
              ('Expand Word', 'Alt+\\', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['EDT_XWD']),
              (SEP),
              ('&Sort Lines', 'Shift+F2', tlw.edit_sort_lines, 'Sort selected lines', 'sort', NO_KND, 'Sel', MI['SRT_LIN']),
              ('Sort Lines Re&verse', 'Ctrl+Shift+F2', tlw.edit_sort_lines, 'Reverse sort selected lines', 'sort_rev', NO_KND, 'Sel', MI['SRT_REV']),
              ('Sort Lines Uni&q', 'Alt+F2', tlw.edit_sort_lines, 'Sort/Uniq selected lines', 'sort_uniq', NO_KND, 'Sel', MI['SRT_UNQ']),
              (SEP),
              ('Calculate Su&m of Text', 'Ctrl+F2', tlw.edit_calc_sum_of_text, 'Calculate sum of selected text', 'calc_sum', NO_KND, 'Sel', MI['EDT_SUM']),
          ])

    SEL = ('Se&lect', [
              ('Split into Lines', 'Ctrl+Shift+L', tlw.select_split_into_lines, NO_HLP, NO_ICO, NO_KND, 'Sel', MI['SEL_SPL']),
              ('Add Previous Line', 'Ctrl+Alt+Up', tlw.select_add_line, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_APL']),
              ('Add Next Line', 'Ctrl+Alt+Down', tlw.select_add_line, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_ANL']),
              ('Single Selection', 'Escape', None, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_SGL']),
              ('Invert Selection', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_INV']),
              (SEP),
              ('Select &All', 'Ctrl+A', tlw.select_all, 'Select all text', 'select_all', NO_KND, 'Doc', MI['SEL_ALL']),
              ('Expand to Word', 'Ctrl+D', tlw.select_word, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_WRD']),
              ('Expand to Line', 'Ctrl+L', tlw.select_line, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_LIN']),
              ('Expand to Paragraph', 'Ctrl+Shift+G', tlw.select_paragraph, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_PAR']),
              ('Expand to Braces', 'Ctrl+Shift+M', tlw.select_braces, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_BRC']),
              ('Expand to Indentation', 'Ctrl+Shift+J', tlw.select_indentation, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['SEL_IND']),
              (SEP),
              ('Swap Anchor and Caret', NO_SCT, tlw.select_anchor_caret_swap, 'Swap anchor and caret for (multiple) selection', NO_ICO, NO_KND, 'Sel', MI['SEL_SWP']),
          ])

    SCH = ('&Search', [
              ('&Find...', 'Ctrl+F', tlw.set_search_mode, 'Find text dialog in search panel', 'find', NO_KND, 'Doc', MI['SCH_FND']),
              ('&Replace...', 'Ctrl+H', tlw.set_search_mode, 'Replace text dialog in search panel', 'replace', NO_KND, 'Doc', MI['SCH_RPL']),
              ('Find &Next', 'F3', tlw.search_find_next, 'Find next text occurrence', 'find_next', NO_KND, 'Sch', MI['SCH_NXT']),
              ('Find Pr&evious', 'Shift+F3', tlw.search_find_previous, 'Find previous text occurrence', 'find_prev', NO_KND, 'Sch', MI['SCH_PRV']),
              (SEP),
              ('Find Current', 'Ctrl+F3', tlw.search_find_current, 'Find word under caret OR next (selection) occurrence', NO_ICO, NO_KND, 'Sch', MI['SCH_CUN']),
              ('Find Current Previous', 'Ctrl+Shift+F3', tlw.search_find_current, 'Find word under caret OR previous (selection) occurrence', NO_ICO, NO_KND, 'Sch', MI['SCH_CUP']),
              ('Find Current All', 'Alt+F3', tlw.search_find_current, 'Find word under caret and/or ALL (selection) occurrences', NO_ICO, NO_KND, 'Sch', MI['SCH_CUA']),
              (SEP),
              ('Find in Files...', 'Ctrl+Shift+F', tlw.set_search_mode, 'Find/replace text in files dialog in search panel', NO_ICO, NO_KND, 'Doc', MI['SCH_FIF']),
              ('&Incremental Search...', 'Ctrl+I', tlw.set_search_mode, 'Progressively find text while typing', NO_ICO, NO_KND, 'Doc', MI['SCH_INC']),
              (SEP),
              ('&Option Flags', NO_SCT, sch),
          ])

    # select side panel tool
    fnc = tlw.view_side_panel_tool

    VEW = ('&View', [
              ('Search Results', 'Ctrl+Shift+R', tlw.set_search_mode, 'Show last search results in bottom panel', NO_ICO, NO_KND, 'Doc', MI['SCH_RES']),
              ('Console Output', 'Ctrl+Shift+O', tlw.view_console_output, 'Show console output in bottom panel', NO_ICO, NO_KND, 'Doc', MI['CON_OUT']),
              (SEP),
              ('Side Panel &Tools', NO_SCT, [
                  ('&Edit List Filter...', 'Ctrl+Alt+F', fnc, 'Filter current side panel list', NO_ICO, NO_KND, 'Doc', MI['SPT_FLT']),
                  ('&Delete List Filter', 'Ctrl+Alt+Shift+F', fnc, 'Delete filter for current side panel list', NO_ICO, NO_KND, 'Doc', MI['SPT_DLF']),
                  (SEP),
                  ('&Document', 'Alt+D', fnc, 'Show open documents in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_DCL']),
                  ('Pro&ject', 'Alt+J', fnc, 'Show project in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_PRJ']),
                  ('&Bookmark', 'Alt+B', fnc, 'Show bookmarks in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_BMK']),
                  ('&Language', '[?????????]', fnc, 'Show languages in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_LNG']),
                  ('&Explorer', 'Alt+E', fnc, 'Show File Explorer in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_FXP']),
                  ('S&ymbol', 'Alt+Y', fnc, 'Show symbol definitions in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_SDF']),
                  ('&Macro', 'Alt+M', fnc, 'Show saved macros in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_MAC']),
                  ('&Task', 'Alt+T', fnc, 'Show tasks in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_TSK']),
                  ('Brea&kpoint', 'Alt+K', fnc, 'Show breakpoints in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_BPT']),
                  ('Debu&g', 'Alt+G', fnc, 'Show debug settings in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_DBG']),
                  ('Document M&ap', 'Alt+A', fnc, 'Show code overview in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_DCM']),
                  ('Con&figuration', 'Alt+F', fnc, 'Show configuration in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_CFG']),
                  ('&Help', 'Alt+H', fnc, 'Show help information in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_HLP']),
                  ('Pyli&nt', 'Alt+N', fnc, 'Show Python linter (pylint) in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_PLT']),
                  ('Pyf&lakes', '[?????????]', fnc, 'Show Python error checker (pyflakes) in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_PFL']),
                  ('Py&codestyle', 'Alt+C', fnc, 'Show Python style checker (pycodestyle) in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_PYS']),
                  ('&Vulture', 'Alt+V', fnc, 'Show Python dead code checker (vulture) in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_VLT']),
                  ('Ma&rkdown', 'Alt+R', fnc, 'Show HTML for markdown text in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_MDN']),
                  ('Code2flo&w', 'Alt+W', fnc, 'Show call graph (code2flow) in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_CFW']),
                  ('Sn&ippet', 'Alt+I', fnc, 'Show source snippets in side panel', NO_ICO, NO_KND, 'Doc', MI['SPT_SNP']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_SPT']),
              (SEP),
              ('&Word Wrap', 'Ctrl+Shift+W', tlw.view_word_wrap, 'Wrap lines within window width', NO_ICO, 'CHECK', 'Doc', MI['DOC_WRP']),
              ('&EOL Characters', 'Ctrl+Shift+E', tlw.view_eol_chars, 'Toggle end of line character visibility', NO_ICO, 'CHECK', 'Doc', MI['DOC_EOL']),
              ('White&space Characters', 'Ctrl+Shift+V', tlw.view_whitespace_chars, 'Toggle whitespace character visibility', NO_ICO, 'CHECK', 'Doc', MI['DOC_WSP']),
              (SEP),
              ('&Indentation', NO_SCT, ind),
              ('Indentation &Guides', NO_SCT, tlw.view_indent_guides, 'Show indentation guides', NO_ICO, 'CHECK', 'Doc', MI['IND_GDS']),
              ('Scroll&bars', NO_SCT, [
                  ('&None', NO_SCT, tlw.view_scroll_bars, 'Hide scrollbars', NO_ICO, 'RADIO', 'Doc', MI['SCL_NON']),
                  ('&Both', NO_SCT, tlw.view_scroll_bars, 'Show both scrollbars', NO_ICO, 'RADIO', 'Doc', MI['SCL_BTH']),
                  ('&Horizontal', NO_SCT, tlw.view_scroll_bars, 'Show horizontal scrollbar only', NO_ICO, 'RADIO', 'Doc', MI['SCL_HOR']),
                  ('&Vertical', NO_SCT, tlw.view_scroll_bars, 'Show vertical scrollbar only', NO_ICO, 'RADIO', 'Doc', MI['SCL_VER']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_SCL']),
              ('AutoScroll', 'Alt+Shift+A', tlw.view_auto_scroll, 'Automatically scroll document up/down', NO_ICO, NO_KND, 'Doc', MI['AUT_SCL']),
              (SEP),
              ('Caret', NO_SCT, [
                  ('BRIEF Home/End Keys', NO_SCT, tlw.view_caret, 'Mimic BRIEF multi-stroke Home/End keys', NO_ICO, 'CHECK', 'Doc', MI['CRT_BRF']),
                  (SEP),
                  ('Caret Line', NO_SCT, tlw.view_caret, 'Toggle caret line visibility', NO_ICO, 'CHECK', 'Doc', MI['CRT_LIN']),
                  ('Caret Sticky', NO_SCT, tlw.view_caret, 'Toggle caret stickiness', NO_ICO, 'CHECK', 'Doc', MI['CRT_STK']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_CRT']),
              ('&Margins', NO_SCT, [
                  ('&All', 'Alt+Shift+G', tlw.view_all_margins, 'Toggle visibility of all margins', NO_ICO, 'CHECK', 'Doc', MI['MGN_ALL']),
                  (SEP),
                  ('Line &Number', 'Alt+Shift+N', tlw.view_margin, 'Toggle line number margin visibility', NO_ICO, 'CHECK', 'Doc', MI['MGN_NUM']),
                  ('Sym&bol', 'Alt+Shift+B', tlw.view_margin, 'Toggle symbol marker margin visibility', NO_ICO, 'CHECK', 'Doc', MI['MGN_SYM']),
                  ('Fo&lding', 'Alt+Shift+L', tlw.view_margin, 'Toggle folding margin visibility', NO_ICO, 'CHECK', 'Doc', MI['MGN_FOL']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_MGN']),
              ('&Edge (long lines)', NO_SCT, [
                  ('&None', NO_SCT, tlw.view_edge, 'Disable edge', NO_ICO, 'RADIO', 'Doc', MI['EDG_NON']),
                  ('&Background', NO_SCT, tlw.view_edge, 'Enable edge with background highlighting', NO_ICO, 'RADIO', 'Doc', MI['EDG_BCK']),
                  ('&Line', NO_SCT, tlw.view_edge, 'Enable edge with line', NO_ICO, 'RADIO', 'Doc', MI['EDG_LIN']),
                  ('&Multiline', NO_SCT, tlw.view_edge, 'Enable edges with multiple lines', NO_ICO, 'RADIO', 'Doc', MI['EDG_MUL']),
                  (SEP),
                  ('&At Column...', NO_SCT, tlw.view_edge, 'Set edge column position', NO_ICO, NO_KND, 'Doc', MI['EDG_COL']),
                  ('&Colour...', NO_SCT, tlw.view_edge, 'Set edge colour', NO_ICO, NO_KND, 'Doc', MI['EDG_CLR']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_EDG']),
              (SEP),
              ('Folding St&yle', 'Ctrl+Shift+Y', tlw.view_folding_style, 'Cycle through and set to next folding style in margin', NO_ICO, NO_KND, 'Doc', MI['FOL_STY']),
              (SEP),
              ('Zoom Reset', 'Ctrl+\\', tlw.view_zoom, 'Zoom: reset text point size to default', NO_ICO, NO_KND, 'Doc', MI['ZOO_RST']),
              ('Zoom In', 'Ctrl++', tlw.view_zoom, 'Zoom: increase text point size', NO_ICO, NO_KND, 'Doc', MI['ZOO_IN_']),
              ('Zoom Out', 'Ctrl+-', tlw.view_zoom, 'Zoom: decrease text point size', NO_ICO, NO_KND, 'Doc', MI['ZOO_OUT']),
              (SEP),
              ('St&atistics...', NO_SCT, tlw.view_statistics, 'Report source code statistics', NO_ICO, NO_KND, 'Doc', MI['SRC_STA']),
              ('&Read-only', NO_SCT, tlw.view_read_only, 'Toggle document read/write', NO_ICO, 'CHECK', 'Doc', MI['DOC_LCK']),
              (SEP),
              ('Keep Window On To&p', NO_SCT, tlw.view_on_top, 'Toggle window on top of other windows', NO_ICO, 'CHECK', NO_UIH, MI['WIN_TOP']),
          ])

    GTO = ('&Goto', [
              ('Goto &Anything...', 'Ctrl+P', tlw.goto_anything, 'Quickly navigate to an open document', NO_ICO, NO_KND, 'Doc', MI['GTO_ANY']),
              (SEP),
              ('Symbol &Browser...', 'Ctrl+R', tlw.symbol_browser, 'Open symbol browser dialog', NO_ICO, NO_KND, 'Doc', MI['GTO_SYM']),
              ('&Go to Line...', 'Ctrl+G', tlw.goto_line, 'Go to line number', NO_ICO, NO_KND, 'Doc', MI['GTO_LIN']),
              (SEP),
              ('Jump Back', 'Alt+-', tlw.goto_caret_pos, 'Jump to previous caret history position', 'jump_back', NO_KND, 'Doc', MI['JMP_BCK']),
              ('Jump Forward', 'Alt+Shift+-', tlw.goto_caret_pos, 'Jump to next caret history position', 'jump_forward', NO_KND, 'Doc', MI['JMP_FWD']),
              (SEP),
              ('Open &File List...', 'Alt+L', tlw.list_open_files, 'Open file list dialog', NO_ICO, NO_KND, 'Doc', MI['GTO_OFL']),
              ('&Bookmarks', NO_SCT, [
                  ('&Toggle Bookmark', 'F8', tlw.toggle_bookmark, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['GTO_TBM']),
                  ('&Next Bookmark', 'Shift+F8', tlw.goto_bookmark, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['BMK_NXT']),
                  ('&Previous Bookmark', 'Ctrl+Shift+F8', tlw.goto_bookmark, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['BMK_PRV']),
                  (SEP),
                  ('&Jump to Bookmark', NO_SCT, [
                      (' &1', 'Ctrl+1', tlw.jump_to_bookmark, NO_HLP, 'bmark1', NO_KND, 'Doc', MI['BMK_JB1']),
                      (' &2', 'Ctrl+2', tlw.jump_to_bookmark, NO_HLP, 'bmark2', NO_KND, 'Doc', MI['BMK_JB2']),
                      (' &3', 'Ctrl+3', tlw.jump_to_bookmark, NO_HLP, 'bmark3', NO_KND, 'Doc', MI['BMK_JB3']),
                      (' &4', 'Ctrl+4', tlw.jump_to_bookmark, NO_HLP, 'bmark4', NO_KND, 'Doc', MI['BMK_JB4']),
                      (' &5', 'Ctrl+5', tlw.jump_to_bookmark, NO_HLP, 'bmark5', NO_KND, 'Doc', MI['BMK_JB5']),
                      (' &6', 'Ctrl+6', tlw.jump_to_bookmark, NO_HLP, 'bmark6', NO_KND, 'Doc', MI['BMK_JB6']),
                      (' &7', 'Ctrl+7', tlw.jump_to_bookmark, NO_HLP, 'bmark7', NO_KND, 'Doc', MI['BMK_JB7']),
                      (' &8', 'Ctrl+8', tlw.jump_to_bookmark, NO_HLP, 'bmark8', NO_KND, 'Doc', MI['BMK_JB8']),
                      (' &9', 'Ctrl+9', tlw.jump_to_bookmark, NO_HLP, 'bmark9', NO_KND, 'Doc', MI['BMK_JB9']),
                      ('1&0', 'Ctrl+0', tlw.jump_to_bookmark, NO_HLP, 'bmark0', NO_KND, 'Doc', MI['BMK_JB0']),
                  ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_JBM']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_BMK']),
              ('&Tasks', NO_SCT, [
#NOTE, F10: default=activate menubar
                  ('&Toggle Task', 'F10', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['GTO_TTK']),
#                                            tlw.toggle_task
                  ('&Next Task', 'Shift+F10', tlw.goto_task, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['TSK_NXT']),
                  ('&Previous Task', 'Ctrl+Shift+F10', tlw.goto_task, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['TSK_PRV']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_TSK']),
              (SEP),
              ('&Matching Brace', 'Ctrl+M', tlw.do_brace_match, 'Jump to matching brace', 'brace_match', NO_KND, 'Doc', MI['MCH_BRC']),
          ])

    RUN = ('&Run', [
              ('&Run Module', NO_SCT, tlw.run_module, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['RUN_MOD']),
              (SEP),
              ('&Debug Module ', NO_SCT, tlw.debugger_start, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['RUN_DBM']),
              (SEP),
              ('&Toggle Breakpoint', 'F9', tlw.toggle_breakpoint, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['RUN_TBP']),
              ('&Enable Breakpoint', 'Alt+F9', tlw.enable_breakpoint, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['BPT_ENA']),
              ('&Next Breakpoint', 'Shift+F9', tlw.goto_breakpoint, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['BPT_NXT']),
              ('&Previous Breakpoint', 'Ctrl+Shift+F9', tlw.goto_breakpoint, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['BPT_PRV']),
          ])

    LNG = ('La&nguage', lng)

    KWS = ('&KeywordSets', [
              (SEP),  # dummy
          ])

    # not_implemented
    PRJ = ('Project', [
              ('&New...', NO_SCT, tlw.project_new, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['PRJ_NEW']),
              ('&Open...', NO_SCT, tlw.project_open, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['PRJ_OPN']),
              ('&Close', NO_SCT, tlw.project_close, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['PRJ_CLS']),
              (SEP),
              ('&Open All Files', NO_SCT, tlw.project_open_all_files, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['PRJ_OPA']),
              ('C&lose All Files', NO_SCT, tlw.project_close_all_files, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['PRJ_CLA']),
              (SEP),
              ('&Project Files      >>', NO_SCT, tlw.project_files, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['PRJ_FIL']),
              ('&Recent Projects    >>', NO_SCT, tlw.project_recent_projects, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['PRJ_RPH']),
              (SEP),
              ('&Manage File List...', NO_SCT, tlw.project_manage_file_list, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['PRJ_MFL']),
          ])

    FMT = ('Fo&rmat', [
              ('&Convert Case', NO_SCT, [
                  ('&Title Case', NO_SCT, tlw.format_case, 'Update selection to title case', NO_ICO, NO_KND, 'Sel', MI['FMT_TTL']),
                  ('&Upper Case', 'Shift+F5', tlw.format_case, 'Update selection to upper case', 'uppercase', NO_KND, 'Sel', MI['FMT_UPR']),
                  ('&Lower Case', 'Alt+F5', tlw.format_case, 'Update selection to lower case', 'lowercase', NO_KND, 'Sel', MI['FMT_LWR']),
                  ('&Invert Case', 'F5', tlw.format_case, 'Invert case of each character in selection', 'invertcase', NO_KND, 'Sel', MI['FMT_INV']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_CAS']),
              (SEP),
              ('Reformat Para&graph', 'Ctrl+Alt+Shift+G', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Sel', MI['FMT_PAR']),
              ('&Fill Block', 'Ctrl+Alt+Shift+L', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Sel', MI['FMT_FLB']),
              ('Insert Code from Te&mplate...', 'Ctrl+Alt+Shift+M', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['FMT_ITP']),
              ('&Comment/Uncomment Code', 'Ctrl+Shift+C', tlw.format_comment, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['FMT_CMT']),
              ('Insert Timestamp (&Date/Time)', 'Ctrl+Alt+Shift+D', tlw.insert_timestamp, 'Insert timestamp at current position', NO_ICO, NO_KND, 'Doc', MI['FMT_ITM']),
              (SEP),
              ('C&onvert Text to...', NO_SCT, [
                  ('&Windows (CRLF)', NO_SCT, tlw.convert_eol, NO_HLP, NO_ICO, 'RADIO', 'Doc', MI['FMT_ECL']),
                  ('&Unix (LF)', NO_SCT, tlw.convert_eol, NO_HLP, NO_ICO, 'RADIO', 'Doc', MI['FMT_ELF']),
                  ('&Mac (CR)', NO_SCT, tlw.convert_eol, NO_HLP, NO_ICO, 'RADIO', 'Doc', MI['FMT_ECR']),
                  ('Mixed EOLs', NO_SCT, not_implemented, NO_HLP, NO_ICO, 'RADIO', NO_UIH, MI['FMT_EMX']),
                  (SEP),
                  ('U&nicode (UTF-8)', NO_SCT, not_implemented, NO_HLP,  'prefs', NO_KND, NO_UIH, MI['FMT_UNI']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_EOL']),
              ('Convert S&paces to Tabs...', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['FMT_CST']),
              ('Convert T&abs to Spaces...', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['FMT_CTS']),
              ('Remove Comm&ents', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['FMT_RMC']),
              ('Remove &Trailing Whitespace', NO_SCT, tlw.remove_trailing_whitespace, 'Remove trailing spaces or tabs on every line', NO_ICO, NO_KND, 'Doc', MI['FMT_RMT']),
          ])

    MAC = ('M&acro', [
              ('Macro TEST Scintilla', NO_SCT, tlw.macro_TEST, NO_HLP, 'mac_rec_quick', NO_KND, 'Mac', MI['MAC_TST']),
              ('&Quick Record', 'Alt+Shift+Q', tlw.macro_start, NO_HLP, 'mac_rec_quick', NO_KND, 'Mac', MI['MAC_QRC']),
              ('&Record...', 'Alt+Shift+R', tlw.macro_start, NO_HLP, 'mac_rec', NO_KND, 'Mac', MI['MAC_REC']),
              ('S&top Recording', 'Alt+Shift+T', tlw.macro_stop, NO_HLP, 'mac_rec_stop', NO_KND, 'Mac', MI['MAC_STP']),
              ('&Play Again', 'Alt+Shift+P', tlw.macro_play, NO_HLP, 'mac_play', NO_KND, 'Mac', MI['MAC_PLY']),
              ('Play &Multiple Times', 'Alt+Shift+M', tlw.macro_play, NO_HLP, 'mac_play_multi', NO_KND, 'Mac', MI['MAC_PLM']),
              (SEP),
              ('&Load...', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MAC_LOD']),
              ('&Save...', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MAC_SAV']),
              (SEP),
              ('&Edit Macro...', NO_SCT, tlw.macro_edit, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MAC_EDT']),
              ('Re&cent/Saved Macros', NO_SCT, [
                  ('Macro &1', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MAC_xx1']),
                  ('Macro &2', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MAC_xx2']),
                  ('Macro &3', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MAC_xx3']),
                  ('Macro &4', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc', MI['MAC_xx4']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_MAC']),
          ])

    # # panel effect submenu values
    # fnc = tlw.panel_effect_choice
    # txt = '%s effect'

    LAY = ('La&yout', [
              ('Toggle UI Elements', NO_SCT, [
                  ('Caption', '[?????????]', tlw.toggle_caption, 'Toggle title bar (caption) visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_CAP']),
                  ('Menubar', 'Ctrl+Alt+M', tlw.toggle_menubar, 'Toggle menubar visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_MBR']),
                  ('Toolbar', NO_SCT, tlw.toggle_toolbar, 'Toggle toolbar visibility', 'TOOLBAR_MenuIconsCustomCheckable_TEST', 'CHECK', NO_UIH, MI['LAY_TBR']),
                  ('Infobar', 'Ctrl+Alt+I', tlw.toggle_infobar, 'Toggle infobar visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_IBR']),
                  ('Statusbar', NO_SCT, tlw.toggle_statusbar, 'Toggle statusbar visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_SBR']),
                  (SEP),
                  ('T&ooltips', NO_SCT, tlw.toggle_tooltips, 'Toggle tooltip visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_TTP']),
                  (SEP),
                  ('Men&u Icons', 'Ctrl+Shift+U', tlw.toggle_menu_item, 'Toggle menu icons visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_MIC']),
                  ('Men&u Icons (Custom Checkable)', NO_SCT, tlw.toggle_menu_item, 'Toggle custom/system-defined checkable menu icons visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_MIK']),
                  ('Menu &Help Text', 'Ctrl+Shift+H', tlw.toggle_menu_item, 'Toggle menu help text visibility in statusbar', NO_ICO, 'CHECK', NO_UIH, MI['LAY_MHT']),
                  (SEP),
                  ('&Search Panel', 'Alt+S', lambda e: tlw.toggle_panel(e, 'SCH', -1), 'Toggle search panel visibility', NO_ICO, 'CHECK', 'Doc', MI['LAY_SCH']),
                  ('Swap &Search Panel', 'Ctrl+Alt+S', lambda e: tlw.swap_panel(e, 'SCH', None), 'Swap search panel to top/bottom', NO_ICO, NO_KND, 'Doc', MI['LAY_SCS']),
                  (SEP),
                  ('R&uler', 'Alt+U', lambda e: tlw.toggle_panel(e, 'RLR', 1), 'Toggle ruler visibility', NO_ICO, 'CHECK', 'Doc', MI['LAY_RLR']),
                  ('Swap R&uler', 'Ctrl+Alt+U', lambda e: tlw.swap_panel(e, 'RLR', None), 'Swap ruler to top/bottom', NO_ICO, NO_KND, 'Doc', MI['LAY_RLS']),
                  (SEP),
                  ('Side &Panel', 'Alt+P', lambda e: tlw.toggle_panel(e, 'SPN', -1), 'Toggle side panel visibility', NO_ICO, 'CHECK', 'Doc', MI['LAY_SPN']),
                  ('Swap Side &Panel', 'Ctrl+Alt+P', lambda e: tlw.swap_panel(e, 'SPN', -1), 'Swap side panel to left/right', NO_ICO, NO_KND, 'Doc', MI['LAY_SPS']),
                  ('Reset Side &Panel', 'Ctrl+Alt+Shift+P', tlw.reset_side_panel, 'Reset side panel to default width', NO_ICO, NO_KND, 'Doc', MI['LAY_SPR']),
                  (SEP),
                  ('C&ode Context', 'Alt+O', lambda e: tlw.toggle_panel(e, 'CCX', 1), 'Toggle code context window visibility', NO_ICO, 'CHECK', 'Doc', MI['LAY_CCX']),
                  ('Swap C&ode Context', 'Ctrl+Alt+O', lambda e: tlw.swap_panel(e, 'CCX', -1), 'Swap code context window to top/bottom', NO_ICO, NO_KND, 'Doc', MI['LAY_CCS']),
                  (SEP),
                  ('Page &Tabs', NO_SCT, tlw.toggle_page_tabs, 'Toggle document page tab visibility', NO_ICO, 'CHECK', 'Doc', MI['LAY_PTB']),
                  ('Tab Th&eme', NO_SCT, tlw.toggle_page_tab_theme, 'Toggle document page tab theme (default/simple)', NO_ICO, 'CHECK', 'Doc', MI['LAY_PTT']),
                  ('Tab &Icons', NO_SCT, tlw.toggle_page_tab_icons, 'Toggle document page tab icon visibility', NO_ICO, 'CHECK', 'Doc', MI['LAY_PTI']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_GUI']),
              ('Toggle Editor Features', NO_SCT, [
                  ('Autocomplete', NO_SCT, tlw.toggle_autocomplete, 'Toggle autocomplete on/off', NO_ICO, 'CHECK', NO_UIH, MI['LAY_ACP']),
                  ('Calltips', NO_SCT, tlw.toggle_calltips, 'Toggle calltip visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_CTP']),
                  ('Top Line Tooltip', NO_SCT, tlw.toggle_topline_tooltip, 'Toggle top line tooltip visibility when scrolling', NO_ICO, 'CHECK', 'Doc', MI['LAY_TLT']),
                  ('Colour Tooltip', NO_SCT, tlw.toggle_colour_tooltip, 'Toggle colour tooltip visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_CTT']),
                  ('Symbol Popup', NO_SCT, tlw.toggle_symbol_popup, 'Toggle symbol popup visibility', NO_ICO, 'CHECK', NO_UIH, MI['LAY_SPU']),
              ], NO_HLP, 'app', NO_KND, NO_UIH, MI['SUB_EDT']),
              # (SEP),
              # ('Panel E&ffect', [
              #     ('&Duration...', tlw.panel_effect_duration, 'Set panel effect duration (milliseconds)', 'clock', NO_KND, 'Doc', MI['PEF_DUR']),
              #     (SEP),
              #     ('None', fnc, txt % 'No', NO_ICO, 'RADIO', 'Doc', MI['PEF_NON']),
              #     ('Roll Left', fnc, txt % 'Roll Left', NO_ICO, 'RADIO', 'Doc', MI['PEF_RLL']),
              #     ('Roll Right', fnc, txt % 'Roll Right', NO_ICO, 'RADIO', 'Doc', MI['PEF_RLR']),
              #     ('Roll Top', fnc, txt % 'Roll Top', NO_ICO, 'RADIO', 'Doc', MI['PEF_RLT']),
              #     ('Roll Bottom', fnc, txt % 'Roll Bottom', NO_ICO, 'RADIO', 'Doc', MI['PEF_RLB']),
              #     ('Slide Left', fnc, txt % 'Slide Left', NO_ICO, 'RADIO', 'Doc', MI['PEF_SLL']),
              #     ('Slide Right', fnc, txt % 'Slide Right', NO_ICO, 'RADIO', 'Doc', MI['PEF_SLR']),
              #     ('Slide Top', fnc, txt % 'Slide Top', NO_ICO, 'RADIO', 'Doc', MI['PEF_SLT']),
              #     ('Slide Bottom', fnc, txt % 'Slide Bottom', NO_ICO, 'RADIO', 'Doc', MI['PEF_SLB']),
              #     ('Blend', fnc, txt % 'Blend', NO_ICO, 'RADIO', 'Doc', MI['PEF_BLN']),
              #     ('Expand', fnc, txt % 'Expand', NO_ICO, 'RADIO', 'Doc', MI['PEF_EXP']),
              # ], NO_HLP, 'fx', NO_KND, NO_UIH, MI['PEF_MNU']),
              (SEP),
              # ('?????? Men&u ??????Icons ??????(Size Demo)', [
              #     ('None', not_implemented, NO_HLP, NO_ICO, NO_KND, NO_UIH, MI['LAY_INO']),
              #     (SEP),
              #     ('&16 x 16', not_implemented, NO_HLP, 'menu_icons_size_16', NO_KND, NO_UIH, MI['LAY_I16']),
              #     ('&24 x 24', not_implemented, NO_HLP, 'menu_icons_size_24', NO_KND, NO_UIH, MI['LAY_I24']),
              #     ('&32 x 32', not_implemented, NO_HLP, 'menu_icons_size_32', NO_KND, NO_UIH, MI['LAY_I32']),
              # ], NO_HLP, 'menu_icons_menu_16'),
              # (SEP),
              # (SEP),
              ('&Full Screen', 'F11', tlw.toggle_fullscreen, 'Toggle full screen', NO_ICO, 'CHECK', NO_UIH, MI['LAY_FUL']),
              ('&Distraction Free Mode', 'Shift+F11', tlw.toggle_distraction_free, 'Toggle distraction free mode', NO_ICO, NO_KND, NO_UIH, MI['LAY_DFM']),
              (SEP),
              # removed '', 'Ctrl+K'
              ('&Preferences...', 'F12', tlw.show_preferences, 'Application preferences', 'prefs', NO_KND, NO_UIH, MI['LAY_PRF']),
              ('&Menu Editor...', NO_SCT, tlw.show_menu_editor, 'Customize menubar', NO_ICO, NO_KND, NO_UIH, MI['LAY_MNE']),
              ('&Syntax Styling...', 'Shift+F12', tlw.show_syntax_styling, 'Syntax highlighting styles', NO_ICO, NO_KND, 'Doc', MI['LAY_SYN']),
              ('Short&cut Editor...', 'Ctrl+Shift+F12', tlw.show_shortcut_editor, 'Customize and change keyboard shortcuts', NO_ICO, NO_KND, NO_UIH, MI['LAY_KBD']),
          ])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    HLP = ('&Help', [
              ('&Contents...', 'F1', tlw.help_contents, NO_HLP, 'help_16', NO_KND, 'Hlp', MI['HLP_CON']),
              ('&Context-sensitive Mode...', 'Alt+F1', tlw.help_context, NO_HLP, 'help_16', NO_KND, 'Hlp', MI['HLP_CTX']),
              (SEP),
#TODO, use 'wx.lib.softwareupdate.SoftwareUpdate'
#INFO, URL=https://wxpython.org/Phoenix/docs/html/wx.lib.softwareupdate.SoftwareUpdate.html
              ('Check for &Updates...', NO_SCT, tlw.help_check_updates, NO_HLP, NO_ICO, NO_KND, 'Hlp', MI['HLP_UPD']),
              ('Widget Inspection Tool...', NO_SCT, tlw.help_inspection_tool, NO_HLP, NO_ICO, NO_KND, 'Hlp', MI['HLP_WIT']),
              (SEP),
              ('&About...', 'Ctrl+F1[[bold]][[small]][[strike]]', tlw.help_about, 'About ' + APP['Base'], 'about', NO_KND, 'Hlp', MI['HLP_ABT']),
          ])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# temporary code: TEST - top level menu
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # TST1 = ('{{TEST1}}', [
    #           ('TESTMETHOD', tlw.TESTMETHOD, NO_HLP, NO_ICO, NO_KND),
    #       ])
    # TST2 = ('{{TEST2}}', [
    #           ('TESTMETHOD', tlw.TESTMETHOD, NO_HLP, NO_ICO, NO_KND),
    #       ])

    # main menu definition combines all above
    # return [FIL, EDT, SEL, SCH, VEW, GTO, RUN, LNG, KWS, TST1, PRJ, FMT, MAC, LAY, HLP, TST2,]
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# temporary code: TEST - top level menu
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    if glb.CFG['Language']['KeywordSetsInMenuBar']:
        return [FIL, EDT, SEL, SCH, VEW, GTO, RUN, LNG, KWS, PRJ, FMT, MAC, LAY, HLP,]
    else:
        return [FIL, EDT, SEL, SCH, VEW, GTO, RUN, LNG,      PRJ, FMT, MAC, LAY, HLP,]
