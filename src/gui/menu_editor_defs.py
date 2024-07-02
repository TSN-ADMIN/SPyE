#!/usr/bin/python

from common.util import not_implemented
from const.app import APP
from const.menubar import NO_ACT, NO_HLP, NO_ICO, NO_KND, NO_SCT, NO_UIH
from const.statusbar import SBL


MENU_ITEM = {
    '__SEP__': None,
    'FIL_NEW': ['&New', 'Ctrl+N', 'tlw.file_new', 'Create new document', 'new', NO_KND, NO_UIH],
    'FIL_OPN': ['&Open...', 'Ctrl+O', 'tlw.file_open', 'Open existing document', 'open', NO_KND, NO_UIH],
    'FIL_QOP': ['&Quick Open...', 'Ctrl+Q', 'tlw.file_quick_open', 'Quickly open existing document(s)', 'save', NO_KND, NO_UIH],

    'SUB_RFH': ['Open Recen&t', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'FIL_RCF': ['Reopen Closed File', 'Ctrl+Shift+T', 'tlw.file_reopen_closed_from_history', 'Reopen closed document from history', NO_ICO, NO_KND, 'His'],
    'FIL_RCA': ['Reopen All Closed File(s)', NO_SCT, 'tlw.file_reopen_closed_from_history', 'Reopen all closed document(s) from history', NO_ICO, NO_KND, 'His'],
    'FIL_CLI': ['Clear Items', NO_SCT, 'tlw.file_clear_history', 'Clear recent file history', NO_ICO, NO_KND, 'His'],

    'FIL_SAV': ['&Save', 'Ctrl+S', 'tlw.file_save', 'Save active document', 'save', NO_KND, 'Mod'],
    'FIL_SAS': ['Save &As...', 'Ctrl+Shift+S', 'tlw.file_save_as', 'Save active document with new name', 'save_as', NO_KND, 'Doc'],
    'FIL_SVA': ['Save A&ll', NO_SCT, 'tlw.file_save_all', 'Save all modified documents', 'save_all', NO_KND, 'Mod'],
    'FIL_REN': ['&Rename...', NO_SCT, 'tlw.file_rename', 'Rename active document and file', NO_ICO, NO_KND, 'Doc'],
    'FIL_RVS': ['Re&vert to Saved...', NO_SCT, 'tlw.file_revert_to_saved', 'Reload active document and lose changes', NO_ICO, NO_KND, 'Mod'],
    'FIL_CHD': ['Change to &Directory...', NO_SCT, 'tlw.file_change_directory', 'Change to selected directory from dialog', NO_ICO, NO_KND, NO_UIH],
    'FIL_CFD': ['Change to File &Directory', NO_SCT, 'tlw.file_change_to_file_directory', 'Change to active document\'s directory', NO_ICO, NO_KND, 'Doc'],
    'FIL_INS': ['&Insert File at Current Position...', NO_SCT, 'tlw.file_insert_file', 'Insert file at current position of active document', NO_ICO, NO_KND, 'Doc'],
    'FIL_APD': ['A&ppend File...', NO_SCT, 'tlw.file_append_file', 'Insert file at end of active document', NO_ICO, NO_KND, 'Doc'],
    'FIL_WBL': ['&Write Block to File...', NO_SCT, 'tlw.file_write_block_to_file', 'Save selection to file', NO_ICO, NO_KND, 'Sel'],
    'FIL_NWN': ['New Window', NO_SCT, 'tlw.file_new_window', 'Open new application window', NO_ICO, NO_KND, 'Doc'],
    'FIL_CWN': ['Close Window', NO_SCT, 'tlw.file_new_window', 'Close active application window', NO_ICO, NO_KND, 'Doc'],
    'FIL_CLS': ['&Close', 'Ctrl+W', 'tlw.file_close', 'Close active document', 'close', NO_KND, 'Doc'],
    'FIL_CLA': ['C&lose All', 'Ctrl+Shift+F4', 'tlw.file_close_all', 'Close all documents', 'close_all', NO_KND, 'Doc'],
    'FIL_CAE': ['Close All &Except This', 'Ctrl+Alt+Shift+F4', 'tlw.file_close_other', 'Close all documents except active document', 'close_all', NO_KND, 'Doc'],
    'FIL_XIT': ['E&xit', 'Alt+X', 'tlw.file_exit', 'Quit application: prompts to save modified documents', 'exit', NO_KND, NO_UIH],

    'EDT_UDO': ['&Undo', 'Ctrl+Z', 'tlw.edit_undo', 'Undo last action', 'undo', NO_KND, 'Doc'],
    'EDT_RDO': ['&Redo', 'Ctrl+Shift+Z', 'tlw.edit_redo', 'Redo last action', 'redo', NO_KND, 'Doc'],
    'EDT_CUT': ['Cu&t', 'Ctrl+X', 'tlw.edit_clipboard', 'Cut to clipboard', 'cut', NO_KND, 'Sel'],
    'EDT_CPY': ['&Copy', 'Ctrl+C', 'tlw.edit_clipboard', 'Copy to clipboard', 'copy', NO_KND, 'Sel'],
    'EDT_PST': ['&Paste', 'Ctrl+V', 'tlw.edit_clipboard', 'Paste from clipboard', 'paste', NO_KND, 'Doc'],
    'EDT_DEL': ['&Delete', 'Backspace', 'tlw.edit_delete', 'Delete selection', 'delete', NO_KND, 'Sel'],
    'EDT_CPF': ['Cop&y Filename', NO_SCT, 'tlw.edit_copy_filename', 'Copy filename to clipboard', NO_ICO, NO_KND, 'Doc'],

    'SUB_CRO': ['C&aret Operations', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'CRT_TOP': ['Move to &Top', 'Ctrl+Alt+Shift+T', 'tlw.edit_move_caret_to', 'Move caret to top of screen', NO_ICO, NO_KND, 'Doc'],
    'CRT_CTR': ['Move to &Centre', 'Ctrl+Alt+Shift+C', 'tlw.edit_move_caret_to', 'Move caret to centre of screen', NO_ICO, NO_KND, 'Doc'],
    'CRT_BOT': ['Move to &Bottom', 'Ctrl+Alt+Shift+B', 'tlw.edit_move_caret_to', 'Move caret to bottom of screen', NO_ICO, NO_KND, 'Doc'],
    'PAR_NXT': ['&Next Paragraph', 'Alt+Shift+Down', 'tlw.edit_goto_paragraph', 'Go to next paragraph (delimited by empty lines)', NO_ICO, NO_KND, 'Doc'],
    'PAR_PRV': ['&Previous Paragraph', 'Alt+Shift+Up', 'tlw.edit_goto_paragraph', 'Go to previous paragraph (delimited by empty lines)', NO_ICO, NO_KND, 'Doc'],

    'SUB_LNO': ['&Line Operations', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'EDT_DPL': ['Duplicate &Line', 'Ctrl+Shift+D', 'tlw.edit_duplicate_line', 'Duplicate current line', 'duplicate_line', NO_KND, 'Doc'],
    'EDT_TPL': ['Transpose L&ine', 'Ctrl+T', 'tlw.edit_transpose_line', 'Switch current line with previous', 'transpose_line', NO_KND, 'Doc'],
    'LIN_TOP': ['Scroll Line to T&op', 'Ctrl+Alt+T', 'tlw.edit_scroll_line_to', 'Scroll current line to top of screen', NO_ICO, NO_KND, 'Doc'],
    'LIN_CTR': ['Scroll Line to C&entre', 'Ctrl+Alt+C', 'tlw.edit_scroll_line_to', 'Scroll current line to centre of screen', NO_ICO, NO_KND, 'Doc'],
    'LIN_BOT': ['Scroll Line to &Bottom', 'Ctrl+Alt+B', 'tlw.edit_scroll_line_to', 'Scroll current line to bottom of screen', NO_ICO, NO_KND, 'Doc'],
    'LIN_SLD': ['Move Selection Down', 'Ctrl+Shift+Down', 'tlw.edit_move_selected_lines', 'Move selected line(s) down', NO_ICO, NO_KND, 'Sel'],
    'LIN_SLU': ['Move Selection Up', 'Ctrl+Shift+Up', 'tlw.edit_move_selected_lines', 'Move selected line(s) up', NO_ICO, NO_KND, 'Sel'],

    'EDT_COL': ['Column Editor...', NO_SCT, 'tlw.edit_column_editor', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'EDT_CTP': ['Calltip', 'Ctrl+Alt+Space', 'tlw.edit_calltip', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'EDT_ACP': ['Autocomplete', 'Ctrl+Space', 'tlw.edit_autocomplete', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'EDT_XWD': ['Expand Word', 'Alt+\\', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SRT_LIN': ['&Sort Lines', 'Shift+F2', 'tlw.edit_sort_lines', 'Sort selected lines', 'sort_lines', NO_KND, 'Sel'],
    'SRT_REV': ['Sort Lines Re&verse', 'Ctrl+Shift+F2', 'tlw.edit_sort_lines', 'Reverse sort selected lines', 'sort_lines_reverse', NO_KND, 'Sel'],
    'SRT_UNQ': ['Sort Lines Uni&que', 'Alt+F2', 'tlw.edit_sort_lines', 'Sort/Uniq selected lines', 'sort_lines_unique', NO_KND, 'Sel'],
    'EDT_SUM': ['Calculate Su&m of Text', 'Ctrl+F2', 'tlw.edit_calc_sum_of_text', 'Calculate sum of selected text', 'calc_sum', NO_KND, 'Sel'],

    'SEL_SPL': ['Split into Lines', 'Ctrl+Shift+L', 'tlw.select_split_into_lines', NO_HLP, NO_ICO, NO_KND, 'Sel'],
    'SEL_APL': ['Add Previous Line', 'Ctrl+Alt+Up', 'tlw.select_add_line', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_ANL': ['Add Next Line', 'Ctrl+Alt+Down', 'tlw.select_add_line', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_SGL': ['Single Selection', 'Escape', None, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_INV': ['Invert Selection', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_ALL': ['Select &All', 'Ctrl+A', 'tlw.select_all', 'Select all text', 'select_all', NO_KND, 'Doc'],
    'SEL_WRD': ['Expand to Word', 'Ctrl+D', 'tlw.select_word', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_LIN': ['Expand to Line', 'Ctrl+L', 'tlw.select_line', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_PAR': ['Expand to Paragraph', 'Ctrl+Shift+G', 'tlw.select_paragraph', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_BRC': ['Expand to Braces', 'Ctrl+Shift+M', 'tlw.select_braces', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_IND': ['Expand to Indentation', 'Ctrl+Shift+J', 'tlw.select_indentation', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'SEL_SWP': ['Swap Anchor and Caret', NO_SCT, 'tlw.select_anchor_caret_swap', 'Swap anchor and caret for (multiple) selection', NO_ICO, NO_KND, 'Sel'],

    'SCH_FND': ['&Find...', 'Ctrl+F', 'tlw.set_search_mode', 'Find text dialog in search panel', 'find', NO_KND, 'Doc'],
    'SCH_RPL': ['&Replace...', 'Ctrl+H', 'tlw.set_search_mode', 'Replace text dialog in search panel', 'replace', NO_KND, 'Doc'],
    'SCH_NXT': ['Find &Next', 'F3', 'tlw.search_find_next', 'Find next text occurrence', 'find_next', NO_KND, 'Sch'],
    'SCH_PRV': ['Find Pr&evious', 'Shift+F3', 'tlw.search_find_previous', 'Find previous text occurrence', 'find_prev', NO_KND, 'Sch'],
    'SCH_CUN': ['Find Current', 'Ctrl+F3', 'tlw.search_find_current', 'Find word under caret OR next (selection) occurrence', NO_ICO, NO_KND, 'Sch'],
    'SCH_CUP': ['Find Current Previous', 'Ctrl+Shift+F3', 'tlw.search_find_current', 'Find word under caret OR previous (selection) occurrence', NO_ICO, NO_KND, 'Sch'],
    'SCH_CUA': ['Find Current All', 'Alt+F3', 'tlw.search_find_current', 'Find word under caret and/or ALL (selection) occurrences', NO_ICO, NO_KND, 'Sch'],
    'SCH_FIF': ['Find in Files...', 'Ctrl+Shift+F', 'tlw.set_search_mode', 'Find/replace text in files dialog in search panel', NO_ICO, NO_KND, 'Doc'],
    'SCH_INC': ['&Incremental Search...', 'Ctrl+I', 'tlw.set_search_mode', 'Progressively find text while typing', 'incremental_search', NO_KND, 'Doc'],

    'SUB_SCH': ['&Option Flags', NO_SCT, None, NO_HLP, 'search_prefs', NO_KND, NO_UIH],
    ##########
    'SCH_CAS': [f'&Case Sensitive   [{SBL.CAS.lbl}]', 'Ctrl+F5', 'tlw.toggle_search_option', 'Toggle case sensitive search', 'sch_cas', 'CHECK', 'Sch'],
    'SCH_REG': [f'Regular E&xpression   [{SBL.REG.lbl}]', 'Ctrl+F6', 'tlw.toggle_search_option', 'Toggle regular expression search', 'sch_reg', 'CHECK', 'Sch'],
    'SCH_WRD': [f'Whole &Words Only   [{SBL.WRD.lbl}]', 'Ctrl+F7', 'tlw.toggle_search_option', 'Toggle whole words only search', 'sch_wrd', 'CHECK', 'Sch'],
    'SCH_WRP': [f'Wrap &Around   [{SBL.WRP.lbl}]', 'Ctrl+F8', 'tlw.toggle_search_option', 'Toggle wrap around search', 'sch_wrp_cus', 'CHECK', 'Sch'],
    'SCH_ISL': [f'In &Selection   [{SBL.ISL.lbl}]', 'Ctrl+F9', 'tlw.toggle_search_option', 'Toggle in selection search', 'sch_isl', 'CHECK', 'Sch'],
    'SCH_HLM': [f'Hig&hlight Matches   [{SBL.HLM.lbl}]', 'Ctrl+F10', 'tlw.toggle_search_option', 'Toggle highlight matches search', 'sch_hlm', 'CHECK', 'Sch'],
    'SCH_PCS': [f'&Preserve Case   [{SBL.PCS.lbl}]', 'Ctrl+F11', 'tlw.toggle_search_option', 'Toggle preserve case search', 'sch_pcs', 'CHECK', 'Sch'],
    'SCH_CXT': [f'Show conte&xt   [{SBL.CXT.lbl}]', NO_SCT, 'tlw.toggle_search_option', 'Toggle show context in search results', 'sch_cxt', 'CHECK', 'Sch'],
    'SCH_BUF': [f'Use &buffer   [{SBL.BUF.lbl}]', NO_SCT, 'tlw.toggle_search_option', 'Toggle use buffer for search results', 'sch_buf', 'CHECK', 'Sch'],

    'SCH_RES': ['Search Results', 'Ctrl+Shift+R', 'tlw.set_search_mode', 'Show last search results in bottom panel', NO_ICO, NO_KND, 'Doc'],
    'CON_OUT': ['Console Output', 'Ctrl+Shift+O', 'tlw.view_console_output', 'Show console output in bottom panel', NO_ICO, NO_KND, 'Doc'],

    'SUB_SPT': ['Side Panel &Tools', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'SPT_FLT': ['&Edit List Filter...', 'Ctrl+Alt+F', 'tlw.view_side_panel_tool', 'Filter current side panel list', NO_ICO, NO_KND, 'Doc'],
    'SPT_DLF': ['&Delete List Filter', 'Ctrl+Alt+Shift+F', 'tlw.view_side_panel_tool', 'Delete filter for current side panel list', NO_ICO, NO_KND, 'Doc'],
    'SPT_DOC': ['&Document', 'Alt+D', 'tlw.view_side_panel_tool', 'Show open documents in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_PRJ': ['Pro&ject', 'Alt+J', 'tlw.view_side_panel_tool', 'Show project in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_BMK': ['&Bookmark', 'Alt+B', 'tlw.view_side_panel_tool', 'Show bookmarks in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_LNG': ['&Language', '[?????????]', 'tlw.view_side_panel_tool', 'Show languages in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_FXP': ['&Explorer', 'Alt+E', 'tlw.view_side_panel_tool', 'Show File Explorer in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_SDF': ['S&ymbol', 'Alt+Y', 'tlw.view_side_panel_tool', 'Show symbol definitions in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_MAC': ['&Macro', 'Alt+M', 'tlw.view_side_panel_tool', 'Show saved macros in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_TSK': ['&Task', 'Alt+T', 'tlw.view_side_panel_tool', 'Show tasks in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_BPT': ['Brea&kpoint', 'Alt+K', 'tlw.view_side_panel_tool', 'Show breakpoints in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_DBG': ['Debu&g', 'Alt+G', 'tlw.view_side_panel_tool', 'Show debug settings in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_DCM': ['Document M&ap', 'Alt+A', 'tlw.view_side_panel_tool', 'Show code overview in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_CFG': ['Con&figuration', 'Alt+F', 'tlw.view_side_panel_tool', 'Show configuration in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_ENV': ['&Environment', '[?????????]', 'tlw.view_side_panel_tool', 'Show environment in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_HLP': ['&Help', 'Alt+H', 'tlw.view_side_panel_tool', 'Show help information in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_PLT': ['Pyli&nt', 'Alt+N', 'tlw.view_side_panel_tool', 'Show Python linter (pylint) in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_PFL': ['Pyf&lakes', '[?????????]', 'tlw.view_side_panel_tool', 'Show Python error checker (pyflakes) in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_PYS': ['Py&codestyle', 'Alt+C', 'tlw.view_side_panel_tool', 'Show Python style checker (pycodestyle) in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_VLT': ['&Vulture', 'Alt+V', 'tlw.view_side_panel_tool', 'Show Python dead code checker (vulture) in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_MDN': ['Ma&rkdown', 'Alt+R', 'tlw.view_side_panel_tool', 'Show HTML for markdown text in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_CFW': ['Code2flo&w', 'Alt+W', 'tlw.view_side_panel_tool', 'Show call graph (code2flow) in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_DIA': ['Diagram&s', '[?????????]', 'tlw.view_side_panel_tool', 'Show diagram (diagrams) in side panel', NO_ICO, NO_KND, 'Doc'],
    'SPT_SNP': ['Sn&ippet', 'Alt+I', 'tlw.view_side_panel_tool', 'Show source snippets in side panel', NO_ICO, NO_KND, 'Doc'],

    'DOC_WRP': ['&Word Wrap', 'Ctrl+Shift+W', 'tlw.view_word_wrap', 'Wrap lines within window width', NO_ICO, 'CHECK', 'Doc'],
    'DOC_EOL': ['&EOL Characters', 'Ctrl+Shift+E', 'tlw.view_eol_chars', 'Toggle end of line character visibility', NO_ICO, 'CHECK', 'Doc'],
    'DOC_WSP': ['White&space Characters', 'Ctrl+Shift+V', 'tlw.view_whitespace_chars', 'Toggle whitespace character visibility', NO_ICO, 'CHECK', 'Doc'],

    'SUB_IND': ['&Indentation', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'IND_IUS': ['Indent using spaces', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'CHECK', 'Doc'],
    'IND_TW1': ['Tab width: 1', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'IND_TW2': ['Tab width: 2', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'IND_TW3': ['Tab width: 3', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'IND_TW4': ['Tab width: 4', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'IND_TW5': ['Tab width: 5', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'IND_TW6': ['Tab width: 6', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'IND_TW7': ['Tab width: 7', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'IND_TW8': ['Tab width: 8', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'IND_GSB': ['Guess settings from buffer', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, 'prefs', NO_KND, 'Doc'],
    'IND_ITS': ['Convert indentation to spaces', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, 'prefs', NO_KND, 'Doc'],
    'IND_ITT': ['Convert indentation to tabs', NO_SCT, 'gui.CtxStatusBarIND', NO_HLP, 'prefs', NO_KND, 'Doc'],

    'IND_GDS': ['Indentation &Guides', NO_SCT, 'tlw.view_indent_guides', 'Show indentation guides', NO_ICO, 'CHECK', 'Doc'],

    'SUB_SCL': ['Scroll&bars', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'SCL_NON': ['&None', NO_SCT, 'tlw.view_scroll_bars', 'Hide scrollbars', NO_ICO, 'RADIO', 'Doc'],
    'SCL_BTH': ['&Both', NO_SCT, 'tlw.view_scroll_bars', 'Show both scrollbars', NO_ICO, 'RADIO', 'Doc'],
    'SCL_HOR': ['&Horizontal', NO_SCT, 'tlw.view_scroll_bars', 'Show horizontal scrollbar only', NO_ICO, 'RADIO', 'Doc'],
    'SCL_VER': ['&Vertical', NO_SCT, 'tlw.view_scroll_bars', 'Show vertical scrollbar only', NO_ICO, 'RADIO', 'Doc'],

    'AUT_SCL': ['AutoScroll', 'Alt+Shift+A', 'tlw.view_auto_scroll', 'Automatically scroll document up/down', NO_ICO, NO_KND, 'Doc'],

    'SUB_CRT': ['Caret', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'CRT_BRF': ['BRIEF Home/End Keys', NO_SCT, 'tlw.view_caret', 'Mimic BRIEF multi-stroke Home/End keys', NO_ICO, 'CHECK', 'Doc'],
    'CRT_LIN': ['Caret Line', NO_SCT, 'tlw.view_caret', 'Toggle caret line visibility', NO_ICO, 'CHECK', 'Doc'],
    'CRT_STK': ['Caret Sticky', NO_SCT, 'tlw.view_caret', 'Toggle caret stickiness', NO_ICO, 'CHECK', 'Doc'],

    'SUB_MGN': ['&Margins', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'MGN_ALL': ['&All', 'Alt+Shift+G', 'tlw.view_all_margins', 'Toggle visibility of all margins', NO_ICO, 'CHECK', 'Doc'],
    'MGN_NUM': ['Line &Number', 'Alt+Shift+N', 'tlw.view_margin', 'Toggle line number margin visibility', NO_ICO, 'CHECK', 'Doc'],
    'MGN_SYM': ['Sym&bol', 'Alt+Shift+B', 'tlw.view_margin', 'Toggle symbol marker margin visibility', NO_ICO, 'CHECK', 'Doc'],
    'MGN_FOL': ['Fo&lding', 'Alt+Shift+L', 'tlw.view_margin', 'Toggle folding margin visibility', NO_ICO, 'CHECK', 'Doc'],

    'SUB_EDG': ['&Edge (long lines)', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'EDG_NON': ['&None', NO_SCT, 'tlw.view_edge', 'Disable edge', NO_ICO, 'RADIO', 'Doc'],
    'EDG_BCK': ['&Background', NO_SCT, 'tlw.view_edge', 'Enable edge with background highlighting', NO_ICO, 'RADIO', 'Doc'],
    'EDG_LIN': ['&Line', NO_SCT, 'tlw.view_edge', 'Enable edge with line', NO_ICO, 'RADIO', 'Doc'],
    'EDG_MUL': ['&Multiline', NO_SCT, 'tlw.view_edge', 'Enable edges with multiple lines', NO_ICO, 'RADIO', 'Doc'],
    'EDG_COL': ['&At Column...', NO_SCT, 'tlw.view_edge', 'Set edge column position', NO_ICO, NO_KND, 'Doc'],
    'EDG_CLR': ['&Colour...', NO_SCT, 'tlw.view_edge', 'Set edge colour', NO_ICO, NO_KND, 'Doc'],

    'FOL_STY': ['Folding St&yle', 'Ctrl+Shift+Y', 'tlw.view_folding_style', 'Cycle through and set to next folding style in margin', NO_ICO, NO_KND, 'Doc'],
    'ZOO_RST': ['Zoom Reset', 'Ctrl+\\', 'tlw.view_zoom', 'Zoom: reset text point size to default', NO_ICO, NO_KND, 'Doc'],
    'ZOO_IN_': ['Zoom In', 'Ctrl++', 'tlw.view_zoom', 'Zoom: increase text point size', NO_ICO, NO_KND, 'Doc'],
    'ZOO_OUT': ['Zoom Out', 'Ctrl+-', 'tlw.view_zoom', 'Zoom: decrease text point size', NO_ICO, NO_KND, 'Doc'],
    'SRC_STA': ['St&atistics...', NO_SCT, 'tlw.view_statistics', 'Report source code statistics', NO_ICO, NO_KND, 'Doc'],
    'DOC_LCK': ['&Read-only', NO_SCT, 'tlw.view_read_only', 'Toggle document read/write', NO_ICO, 'CHECK', 'Doc'],
    'WIN_TOP': ['Keep Window On To&p', NO_SCT, 'tlw.view_on_top', 'Toggle window on top of other windows', NO_ICO, 'CHECK', NO_UIH],

    'GTO_ANY': ['Goto &Anything...', 'Ctrl+P', 'tlw.goto_anything', 'Quickly navigate to an open document', NO_ICO, NO_KND, 'Doc'],
    'GTO_SYM': ['Symbol &Browser...', 'Ctrl+R', 'tlw.symbol_browser', 'Open symbol browser dialog', NO_ICO, NO_KND, 'Doc'],
    'GTO_LIN': ['&Go to Line...', 'Ctrl+G', 'tlw.goto_line', 'Go to line number', NO_ICO, NO_KND, 'Doc'],
    'JMP_BCK': ['Jump Back', 'Alt+-', 'tlw.goto_caret_pos', 'Jump to previous caret history position', 'jump_back', NO_KND, 'Doc'],
    'JMP_FWD': ['Jump Forward', 'Alt+Shift+-', 'tlw.goto_caret_pos', 'Jump to next caret history position', 'jump_forward', NO_KND, 'Doc'],
    'GTO_OFL': ['Open &File List...', 'Alt+L', 'tlw.list_open_files', 'Open file list dialog', NO_ICO, NO_KND, 'Doc'],

    'SUB_BMK': ['&Bookmarks', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'GTO_TBM': ['&Toggle Bookmark', 'F8', 'tlw.toggle_bookmark', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'BMK_NXT': ['&Next Bookmark', 'Shift+F8', 'tlw.goto_bookmark', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'BMK_PRV': ['&Previous Bookmark', 'Ctrl+Shift+F8', 'tlw.goto_bookmark', NO_HLP, NO_ICO, NO_KND, 'Doc'],

    'SUB_JBM': ['&Jump to Bookmark', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'BMK_JB1': [' &1', 'Ctrl+1', 'tlw.jump_to_bookmark', NO_HLP, 'bmark1', NO_KND, 'Doc'],
    'BMK_JB2': [' &2', 'Ctrl+2', 'tlw.jump_to_bookmark', NO_HLP, 'bmark2', NO_KND, 'Doc'],
    'BMK_JB3': [' &3', 'Ctrl+3', 'tlw.jump_to_bookmark', NO_HLP, 'bmark3', NO_KND, 'Doc'],
    'BMK_JB4': [' &4', 'Ctrl+4', 'tlw.jump_to_bookmark', NO_HLP, 'bmark4', NO_KND, 'Doc'],
    'BMK_JB5': [' &5', 'Ctrl+5', 'tlw.jump_to_bookmark', NO_HLP, 'bmark5', NO_KND, 'Doc'],
    'BMK_JB6': [' &6', 'Ctrl+6', 'tlw.jump_to_bookmark', NO_HLP, 'bmark6', NO_KND, 'Doc'],
    'BMK_JB7': [' &7', 'Ctrl+7', 'tlw.jump_to_bookmark', NO_HLP, 'bmark7', NO_KND, 'Doc'],
    'BMK_JB8': [' &8', 'Ctrl+8', 'tlw.jump_to_bookmark', NO_HLP, 'bmark8', NO_KND, 'Doc'],
    'BMK_JB9': [' &9', 'Ctrl+9', 'tlw.jump_to_bookmark', NO_HLP, 'bmark9', NO_KND, 'Doc'],
    'BMK_JB0': ['1&0', 'Ctrl+0', 'tlw.jump_to_bookmark', NO_HLP, 'bmark0', NO_KND, 'Doc'],

    'SUB_TSK': ['&Tasks', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'GTO_TTK': ['&Toggle Task', 'F10', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'TSK_NXT': ['&Next Task', 'Shift+F10', 'tlw.goto_task', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'TSK_PRV': ['&Previous Task', 'Ctrl+Shift+F10', 'tlw.goto_task', NO_HLP, NO_ICO, NO_KND, 'Doc'],

    'MCH_BRC': ['&Matching Brace', 'Ctrl+M', 'tlw.do_brace_match', 'Jump to matching brace', 'brace_match', NO_KND, 'Doc'],

    'RUN_MOD': ['&Run Module', NO_SCT, 'tlw.run_module', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'RUN_DBM': ['&Debug Module ', NO_SCT, 'tlw.start_debugger', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'RUN_TBP': ['&Toggle Breakpoint', 'F9', 'tlw.toggle_breakpoint', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'BPT_ENA': ['&Enable Breakpoint', 'Alt+F9', 'tlw.enable_breakpoint', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'BPT_NXT': ['&Next Breakpoint', 'Shift+F9', 'tlw.goto_breakpoint', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'BPT_PRV': ['&Previous Breakpoint', 'Ctrl+Shift+F9', 'tlw.goto_breakpoint', NO_HLP, NO_ICO, NO_KND, 'Doc'],

    'SUB_KWS': ['&Keyword Sets', NO_SCT, None, '&Keyword Sets &Keyword Sets &Keyword Sets &Keyword Sets', 'app', NO_KND, NO_UIH],
    ##########
    'LNG_BASH': ['&Bash/Shell', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Bash/Shell] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_BATCH': ['&Batch/CMD', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Batch/CMD] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_CONF': ['&Config', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Config] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_CPP': ['&C/C++', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [C/C++] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_CSS': ['&CSS', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [CSS] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_HTML': ['&HTML', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [HTML] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_MARKDOWN': ['&Markdown', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Markdown] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_PASCAL': ['&Pascal', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Pascal] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_PERL': ['&Perl', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Perl] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_PHPSCRIPT': ['&PHP', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [PHP] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_POWERSHELL': ['&PowerShell', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [PowerShell] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_PROPERTIES': ['&Properties', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Properties] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_PYTHON': ['&Python', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Python] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_RUBY': ['&Ruby', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [Ruby] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_SQL': ['&SQL/(PL/SQL)', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [SQL/(PL/SQL)] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_TCL': ['&TCL', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [TCL] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_XML': ['&XML', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [XML] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_YAML': ['&YAML', NO_SCT, 'tlw.update_styling', 'Syntax highlighting for [YAML] documents', NO_ICO, 'RADIO', NO_UIH],
    'LNG_NULL': ['&No highlighting', NO_SCT, 'tlw.update_styling', 'No syntax highlighting', NO_ICO, 'RADIO', NO_UIH],

    'PRJ_NEW': ['&New...', NO_SCT, 'tlw.project_new', NO_HLP, NO_ICO, NO_KND, NO_UIH],
    'PRJ_OPN': ['&Open...', NO_SCT, 'tlw.project_open', NO_HLP, NO_ICO, NO_KND, NO_UIH],
    'PRJ_CLS': ['&Close', NO_SCT, 'tlw.project_close', NO_HLP, NO_ICO, NO_KND, NO_UIH],
    'PRJ_OPA': ['&Open All Files', NO_SCT, 'tlw.project_open_all_files', NO_HLP, NO_ICO, NO_KND, NO_UIH],
    'PRJ_CLA': ['C&lose All Files', NO_SCT, 'tlw.project_close_all_files', NO_HLP, NO_ICO, NO_KND, NO_UIH],
    'PRJ_FIL': ['&Project Files      >>', NO_SCT, 'tlw.project_files', NO_HLP, NO_ICO, NO_KND, NO_UIH],
    'PRJ_RPH': ['&Recent Projects    >>', NO_SCT, 'tlw.project_recent_projects', NO_HLP, NO_ICO, NO_KND, NO_UIH],
    'PRJ_MFL': ['&Manage File List...', NO_SCT, 'tlw.project_manage_file_list', NO_HLP, NO_ICO, NO_KND, NO_UIH],

    'SUB_CAS': ['&Convert Case', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'FMT_TTL': ['&Title Case', NO_SCT, 'tlw.format_case', 'Update selection to title case', 'title_case', NO_KND, 'Sel'],
    'FMT_UPR': ['&Upper Case', 'Shift+F5', 'tlw.format_case', 'Update selection to upper case', 'uppercase', NO_KND, 'Sel'],
    'FMT_LWR': ['&Lower Case', 'Alt+F5', 'tlw.format_case', 'Update selection to lower case', 'lowercase', NO_KND, 'Sel'],
    'FMT_INV': ['&Invert Case', 'F5', 'tlw.format_case', 'Invert case of each character in selection', 'invertcase', NO_KND, 'Sel'],

    'FMT_PAR': ['Reformat Para&graph', 'Ctrl+Alt+Shift+G', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Sel'],
    'FMT_FLB': ['&Fill Block', 'Ctrl+Alt+Shift+L', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Sel'],
    'FMT_ITP': ['Insert Code from Te&mplate...', 'Ctrl+Alt+Shift+M', not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'FMT_CMT': ['&Comment/Uncomment Code', 'Ctrl+Shift+C', 'tlw.format_comment', NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'FMT_ITM': ['Insert Timestamp (&Date/Time)', 'Ctrl+Alt+Shift+D', 'tlw.insert_timestamp', 'Insert timestamp at current position', NO_ICO, NO_KND, 'Doc'],

    'SUB_EOL': ['C&onvert Text to...', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'FMT_ECL': ['&Windows (CRLF)', NO_SCT, 'tlw.convert_eol', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'FMT_ELF': ['&Unix (LF)', NO_SCT, 'tlw.convert_eol', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'FMT_ECR': ['&Mac (CR)', NO_SCT, 'tlw.convert_eol', NO_HLP, NO_ICO, 'RADIO', 'Doc'],
    'FMT_EMX': ['Mixed EOLs', NO_SCT, not_implemented, NO_HLP, NO_ICO, 'RADIO', NO_UIH],
    'FMT_UNI': ['U&nicode (UTF-8)', NO_SCT, not_implemented, NO_HLP,  'unicode', NO_KND, NO_UIH],

    'FMT_CST': ['Convert S&paces to Tabs...', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'FMT_CTS': ['Convert T&abs to Spaces...', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'FMT_RMC': ['Remove Comm&ents', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'FMT_RMT': ['Remove &Trailing Whitespace', NO_SCT, 'tlw.remove_trailing_whitespace', 'Remove trailing spaces or tabs on every line', NO_ICO, NO_KND, 'Doc'],

    'MAC_TST': ['Macro TEST Scintilla', NO_SCT, 'tlw.macro_TEST', NO_HLP, '_DUMMY_', NO_KND, 'Mac'],
    'MAC_QRC': ['&Quick Record', 'Alt+Shift+Q', 'tlw.macro_start', NO_HLP, 'mac_rec_quick', NO_KND, 'Mac'],
    'MAC_REC': ['&Record...', 'Alt+Shift+R', 'tlw.macro_start', NO_HLP, 'mac_rec', NO_KND, 'Mac'],
    'MAC_STP': ['S&top Recording', 'Alt+Shift+T', 'tlw.macro_stop', NO_HLP, 'mac_rec_stop', NO_KND, 'Mac'],
    'MAC_PLY': ['&Play Again', 'Alt+Shift+P', 'tlw.macro_play', NO_HLP, 'mac_play', NO_KND, 'Mac'],
    'MAC_PLM': ['Play &Multiple Times', 'Alt+Shift+M', 'tlw.macro_play', NO_HLP, 'mac_play_multi', NO_KND, 'Mac'],
    'MAC_LOD': ['&Load...', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'MAC_SAV': ['&Save...', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'MAC_EDT': ['&Edit Macro...', NO_SCT, 'tlw.macro_edit', NO_HLP, NO_ICO, NO_KND, 'Doc'],

    'SUB_MAC': ['Re&cent/Saved Macros', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'MAC_xx1': ['Macro &1', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'MAC_xx2': ['Macro &2', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'MAC_xx3': ['Macro &3', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],
    'MAC_xx4': ['Macro &4', NO_SCT, not_implemented, NO_HLP, NO_ICO, NO_KND, 'Doc'],

    'SUB_GUI': ['Toggle UI Elements', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'LAY_CAP': ['Caption', '[?????????]', 'tlw.toggle_caption', 'Toggle title bar (caption) visibility', NO_ICO, 'CHECK', NO_UIH],
    'LAY_MBR': ['Menubar', 'Ctrl+Alt+M', 'tlw.toggle_menubar', 'Toggle menubar visibility', NO_ICO, 'CHECK', NO_UIH],
    'LAY_TBR': ['Toolbar', NO_SCT, 'tlw.toggle_toolbar', 'Toggle toolbar visibility', 'TOOLBAR_MenuIconsCustomCheckable_TEST', 'CHECK', NO_UIH],
    'LAY_IBR': ['Infobar', 'Ctrl+Alt+I', NO_ACT, 'Toggle infobar visibility', NO_ICO, 'CHECK', NO_UIH],
    'LAY_SBR': ['Statusbar', NO_SCT, 'tlw.toggle_statusbar', 'Toggle statusbar visibility', NO_ICO, 'CHECK', NO_UIH],
    'LAY_TTP': ['T&ooltips', NO_SCT, 'tlw.toggle_tooltips', 'Toggle tooltip visibility', NO_ICO, 'CHECK', NO_UIH],
    'LAY_MIC': ['Men&u Icons', 'Ctrl+Shift+U', 'tlw.toggle_menu_item', 'Toggle menu icons visibility', NO_ICO, 'CHECK', NO_UIH],
    'LAY_MIK': ['Men&u Icons (Custom Checkable)', NO_SCT, 'tlw.toggle_menu_item', 'Toggle custom/system-defined checkable menu icons visibility', NO_ICO, 'CHECK', NO_UIH],

    'SUB_ISZ': ['Men&u Icon Size', NO_SCT, None, NO_HLP, 'icon_size_rgb', NO_KND, NO_UIH],
    ##########
    'LAY_I16': ['&16 x 16', NO_SCT, 'tlw.toggle_menu_item', 'Set menu icon size to 16 x 16', 'icon_size_rgb_16', 'RADIO', 'Doc'],
    'LAY_I24': ['&24 x 24', NO_SCT, 'tlw.toggle_menu_item', 'Set menu icon size to 24 x 24', 'icon_size_rgb_24', 'RADIO', 'Doc'],
    'LAY_I32': ['&32 x 32', NO_SCT, 'tlw.toggle_menu_item', 'Set menu icon size to 32 x 32', 'icon_size_rgb_32', 'RADIO', 'Doc'],

    'LAY_MHT': ['Menu &Help Text', 'Ctrl+Shift+H', 'tlw.toggle_menu_item', 'Toggle menu help text visibility in statusbar', NO_ICO, 'CHECK', NO_UIH],

    'SUB_SCP': ['&Search Panel', NO_SCT, None, NO_HLP, 'search_panel', NO_KND, NO_UIH],
    ##########
    'LAY_SCH': ['&Toggle', 'Alt+S', lambda e: tlw.toggle_panel(e, 'SCH', -1), 'Toggle search panel visibility', 'toggle_panel', 'CHECK', 'Doc'],
    'LAY_SCS': ['&Swap', 'Ctrl+Alt+S', lambda e: tlw.swap_panel(e, 'SCH', None), 'Swap search panel to top/bottom', 'swap_panel_TB', NO_KND, 'Doc'],

    'SUB_RLP': ['R&uler Panel', NO_SCT, None, NO_HLP, 'ruler_panel', NO_KND, NO_UIH],
    ##########
    'LAY_RLR': ['&Toggle', 'Alt+U', lambda e: tlw.toggle_panel(e, 'RLR', 1), 'Toggle ruler visibility', 'toggle_panel', 'CHECK', 'Doc'],
    'LAY_RLS': ['&Swap', 'Ctrl+Alt+U', lambda e: tlw.swap_panel(e, 'RLR', None), 'Swap ruler to top/bottom', 'swap_panel_TB', NO_KND, 'Doc'],

    'SUB_SPP': ['Side &Panel', NO_SCT, None, NO_HLP, 'side_panel', NO_KND, NO_UIH],
    ##########
    'LAY_SPN': ['&Toggle', 'Alt+P', lambda e: tlw.toggle_panel(e, 'SPN', -1), 'Toggle side panel visibility', 'toggle_panel', 'CHECK', 'Doc'],
    'LAY_SPS': ['&Swap', 'Ctrl+Alt+P', lambda e: tlw.swap_panel(e, 'SPN', -1), 'Swap side panel to left/right', 'swap_panel_LR', NO_KND, 'Doc'],
    'LAY_SPR': ['&Reset', 'Ctrl+Alt+Shift+P', 'tlw.reset_side_panel', 'Reset side panel to default width', 'reset_panel', NO_KND, 'Doc'],

    'SUB_CCP': ['C&ode Context Panel', NO_SCT, None, NO_HLP, 'code_context', NO_KND, NO_UIH],
    ##########
    'LAY_CCX': ['&Toggle', 'Alt+O', lambda e: tlw.toggle_panel(e, 'CCX', 1), 'Toggle code context window visibility', 'toggle_panel', 'CHECK', 'Doc'],
    'LAY_CCS': ['&Swap', 'Ctrl+Alt+O', lambda e: tlw.swap_panel(e, 'CCX', -1), 'Swap code context window to top/bottom', 'swap_panel_TB', NO_KND, 'Doc'],

    'LAY_PTB': ['Page &Tabs', NO_SCT, 'tlw.toggle_page_tabs', 'Toggle document page tab visibility', NO_ICO, 'CHECK', 'Doc'],
    'LAY_PTT': ['Tab Th&eme', NO_SCT, 'tlw.toggle_page_tab_theme', 'Toggle document page tab theme (default/simple)', NO_ICO, 'CHECK', 'Doc'],
    'LAY_PTI': ['Tab &Icons', NO_SCT, 'tlw.toggle_page_tab_icons', 'Toggle document page tab icon visibility', NO_ICO, 'CHECK', 'Doc'],

    'SUB_EDT': ['Toggle Editor Features', NO_SCT, None, NO_HLP, 'app', NO_KND, NO_UIH],
    ##########
    'LAY_ACP': ['Autocomplete', NO_SCT, 'tlw.toggle_autocomplete', 'Toggle autocomplete on/off', NO_ICO, 'CHECK', NO_UIH],
    'LAY_CTP': ['Calltips', NO_SCT, 'tlw.toggle_calltips', 'Toggle calltip visibility', NO_ICO, 'CHECK', NO_UIH],
    'LAY_TLT': ['Top Line Tooltip', NO_SCT, 'tlw.toggle_topline_tooltip', 'Toggle top line tooltip visibility when scrolling', NO_ICO, 'CHECK', 'Doc'],
    'LAY_CTT': ['Colour Tooltip', NO_SCT, 'tlw.toggle_colour_tooltip', 'Toggle colour tooltip visibility', NO_ICO, 'CHECK', NO_UIH],
    'LAY_SPU': ['Symbol Popup', NO_SCT, 'tlw.toggle_symbol_popup', 'Toggle symbol popup visibility', NO_ICO, 'CHECK', NO_UIH],

    'LAY_FUL': ['&Full Screen', 'F11', 'tlw.toggle_fullscreen', 'Toggle full screen', NO_ICO, 'CHECK', NO_UIH],
    'LAY_DFM': ['&Distraction Free Mode', 'Shift+F11', 'tlw.toggle_distraction_free', 'Toggle distraction free mode', NO_ICO, NO_KND, NO_UIH],
    'LAY_PRF': ['&Preferences...', 'F12', 'tlw.show_preferences', 'Application preferences', 'preferences', NO_KND, NO_UIH],
    'LAY_MNE': ['&Menu Editor...', NO_SCT, 'tlw.show_menu_editor', 'Customize menubar', NO_ICO, NO_KND, NO_UIH],
    'LAY_SYN': ['&Syntax Styling...', 'Shift+F12', 'tlw.show_syntax_styling', 'Syntax highlighting styles', NO_ICO, NO_KND, 'Doc'],
    'LAY_KBD': ['Short&cut Editor...', 'Ctrl+Shift+F12', 'tlw.show_shortcut_editor', 'Customize and change keyboard shortcuts', NO_ICO, NO_KND, NO_UIH],

    'HLP_CON': ['&Contents...', 'F1', 'tlw.help_contents', NO_HLP, 'help', NO_KND, 'Hlp'],
    'HLP_CTX': ['&Context-sensitive Mode...', 'Alt+F1', 'tlw.help_context', NO_HLP, 'help', NO_KND, 'Hlp'],
    'HLP_UPD': ['Check for &Updates...', NO_SCT, 'tlw.help_check_updates', NO_HLP, NO_ICO, NO_KND, 'Hlp'],
    'HLP_SCR': ['Save Screenshot', NO_SCT, 'tlw.help_save_screenshot', 'Save screenshot of active document', 'screenshot', NO_KND, 'Hlp'],
    'HLP_WIT': ['Widget Inspection Tool...', NO_SCT, 'tlw.help_inspection_tool', NO_HLP, NO_ICO, NO_KND, 'Hlp'],
    'HLP_ABT': ['&About...', 'Ctrl+F1[[bold]][[small]][[strike]]', 'tlw.help_about', f'About {APP["Base"]}', 'about', NO_KND, 'Hlp'],
}