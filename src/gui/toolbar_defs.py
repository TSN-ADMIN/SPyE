#!/usr/bin/python

from common.util import not_implemented
from const.menubar import NO_HLP, NO_ICO, NO_KND, NO_SCT, NO_UIH, SEP, MI
from const.toolbar import TBR


#NOTE, a TOOLBAR TOOL shares the SAME id with its corresponding MENU ITEM
#INFO, URL=http://wxpython-users.1045709.n5.nabble.com/Binding-mouse-clicks-to-toolbar-button-td2353483.html
TTD = {
    # 'SEP': (None, None, 'Separator'),
    'NEW': ('New', 'tlw.file_new', 'New', 'new', NO_KND, NO_UIH, TBR['NEW']),
    'OPN': ('Open', 'tlw.file_open', 'Open', 'open', NO_KND, NO_UIH, TBR['OPN']),
    'SAV': ('Save', 'tlw.file_save', 'Save', 'save', NO_KND, 'Mod', TBR['SAV']),
    'SAS': ('SaveAs', 'tlw.file_save_as', 'Save As', 'save_as', NO_KND, 'Doc', TBR['SAS']),
    'CLS': ('Close', 'tlw.file_close', 'Close', 'close', NO_KND, 'Doc', TBR['CLS']),
    'CUT': ('Cut', 'tlw.edit_clipboard', 'Cut', 'cut', NO_KND, 'Sel', TBR['CUT']),
    'CPY': ('Copy', 'tlw.edit_clipboard', 'Copy', 'copy', NO_KND, 'Sel', TBR['CPY']),
    'PST': ('Paste', 'tlw.edit_clipboard', 'Paste', 'paste', NO_KND, 'Doc', TBR['PST']),
    'UDO': ('Undo', 'tlw.edit_undo', 'Undo', 'undo', NO_KND, 'Doc', TBR['UDO']),
    'RDO': ('Redo', 'tlw.edit_redo', 'Redo', 'redo', NO_KND, 'Doc', TBR['RDO']),
    'FND': ('Find', 'tlw.set_search_mode_find', 'Find', 'find', NO_KND, 'Doc', TBR['FND']),
    'NXT': ('Next', 'tlw.search_find_next', 'Find Next', 'find_next', NO_KND, 'Sch', TBR['NXT']),
    'RPL': ('Replace', 'tlw.set_search_mode_replace', 'Replace', 'replace', NO_KND, 'Doc', TBR['RPL']),
    'PRV': ('Prev', 'tlw.search_find_previous', 'Find Previous', 'find_prev', NO_KND, 'Sch', TBR['PRV']),
    'FXP': ('Explore', 'tlw.view_side_panel_tool', 'File Explorer', 'explorer', NO_KND, 'Doc', TBR['FXP']),
    'SDF': ('Symbols', 'tlw.view_side_panel_tool', 'Symbol Defs', 'symbol_defs', NO_KND, 'Doc', TBR['SDF']),
    'BRC': ('Brace', 'tlw.do_brace_match', 'Brace Match', 'brace_match', NO_KND, 'Doc', TBR['BRC']),
    'SRT': ('Sort', 'tlw.edit_sort_lines', 'Sort', 'sort_lines', NO_KND, 'Sel', TBR['SRT']),

    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    'SUM': ('Sum', 'tlw.edit_calc_sum_of_text', 'Sum', 'calc_sum', NO_KND, 'Sel', TBR['SUM']),
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    'FUL': ('Full', 'tlw.toggle_fullscreen', 'Full Screen', 'fullscreen', NO_KND, NO_UIH, TBR['FUL']),
    'PRF': ('Prefs', 'tlw.show_preferences', 'Preferences', 'preferences', NO_KND, NO_UIH, TBR['PRF']),
    'SCH': ('Search', not_implemented, 'Search', NO_ICO, NO_KND, NO_UIH, TBR['SCH']),
    # '___': ('', not_implemented, '', 'alpha_zero_1x100', NO_KND, NO_UIH, -1),
}
