#!/usr/bin/python

from pprint import pprint
import webbrowser

import wx

from common.doc import get_doc
from common.util import me_, rs_
from conf.debug import DEBUG, dbg_EVENT
from const.common import TXT_NIL
from const.editor import MGN
from const import glb
from const.lang import LANG
from const.menu import NO_ACT, NO_HLP, NO_ICO, NO_SCT, SEP, MI, DMX
from const.sidepanel import SPT
from const.statusbar import SBX, SBX_ENC, SBX_EOL
from const.toolbar import TBX
import gui


#FIX, refactor 'if ref in' to dict with: key='ref', list=(sec, mnu, ttl)
CTX_REF_MAP = {
    'EDT': ('Editor',         'EDT', 'Editor',                           ),
    'MGN': ('Margin',         'MGN', 'Editor Margin',                    ),
    'NBK': ('Notebook',       'NBK', 'Notebook: [{FIL}{MOD}{LCK}]',      ),
    'MBR': ('MenuBar',        'MBR', 'MenuBar',                          ),
    'TBR': ('ToolBar',        'TBR', 'ToolBar',                          ),
    'IBR': ('InfoBar',        'IBR', 'InfoBar',                          ),
    'SBR': ('StatusBar',      'SBR', 'StatusBar',                        ),
    'PSW': ('PanelSwitcher',  'PSW', 'Panel Switcher',                   ),
    'SCH': ('SearchFlags',    'SCH', 'Search Flags',                     ),
    'ENC': ('FileEncoding',   'ENC', 'File Encoding (not implemented)',  ),
    'EOL': ('EndOfLine',      'EOL', 'End of Line',                      ),
    'IND': ('Indentation',    'IND', 'Indentation (almost implemented)', ),
    'LNG': ('Language',       'LNG', 'Language',                         ),
    'RLR': ('Ruler',          'RLR', 'Ruler',                            ),
    'CCX': ('CodeContext',    'CCX', 'Code Context',                     ),
    'BMK': ('BookmarkList',   'BMK', 'Bookmark {TTL}',                   ),
    'SDF': ('SymbolDef',      'SDF', 'Symbol Def',                       ),
    'TSK': ('TaskList',       'TSK', 'Task {TTL}',                       ),
    'BPT': ('BreakpointList', 'BPT', 'Breakpoint {TTL}',                 ),
    'DCM': ('DocMap',         'DCM', 'DocMap',                           ),
    'FNF': ('FindHistory',    'FNF', 'Find Field History',               ),
    'RPF': ('ReplaceHistory', 'RPF', 'Replace Field History',            ),
    'WHF': ('WhereHistory',   'WHF', 'Where Field History',              ),
    'WHR': ('WhereButton',    'WHR', 'Where',                            ),
    'RES': ('SearchResults',  'RES', 'Search Results',                   ),
}

__BEWARE__ = ('WHR', 'WhereButton', '-> new in SPyE.cfg')


#FIX, refactor to class ??
def ContextMenu(evt, ref=TXT_NIL):
    if not (doc := get_doc()): return

    # discard context menu when symbol popup active
    if doc.spu_active:
        return

    print(CTX_REF_MAP.get(ref))

    cfg, tlw, mb, sb, nbk, sch = glb.CFG, glb.TLW, glb.MB, glb.SB, glb.NBK, glb.SCH

    # # when no document open, allow ONLY main statusbar context menu
    # if not nbk.PageCount and ref != 'SBR':
    #     return

    obj = evt.EventObject
    sec = cfg['ContextMenu']

    if DEBUG['CTX']: print(f'{me_()}')
    if DEBUG['EVT'] > 1: dbg_EVENT(evt)

    # editor
    if ref in 'EDT':
        if DEBUG['CTX']: print('Editor')
        # click position and editor client rectangle
        pos = evt.Position
        clt = doc.ClientRect
        # single selection: put caret at click position
        if doc.Selections == 1:
            spos, epos = doc.GetSelection()
            clk = doc.CharPositionFromPoint(*doc.ScreenToClient(pos))
            doc.GotoPos(clk)
            # restore selection when clicked on it
            if spos <= clk <= epos:
                doc.SetSelection(spos, epos)
        # calc editor margin width
        wid = 0
        for m in (MGN['NUM'], MGN['SYM'], MGN['FOL']):
            if DEBUG['CTX']: print('Margin', doc.GetMarginWidth(m))
            wid += doc.GetMarginWidth(m)
        if DEBUG['CTX']: print(f'{rs_(9)}\n Total', wid)
        # convert editor client rectangle to screen coordinates
        rct = wx.Rect(doc.ClientToScreen(clt.Position), clt.Size)
        if DEBUG['CTX']: print(f'  pos: [{pos}], clt: [{clt}], rct: [{rct}]')
        # set editor client rectangle to margin width
        rct.SetWidth(wid)
        if DEBUG['CTX']: print(f'  pos: [{pos}], clt: [{clt}], rct: [{rct}]')
        # right click on editor margin?
        oac = None
        if rct.Contains(pos):
            if not sec['Margin']:
                return
            # mnu, ttl = 'MGN', 'Editor Margin'
            mnu, ttl = 'MGN', 'Editor Margin'
        else:
            if not sec['Editor']:
                return

            oac = tlw.file_open_at_caret(None, src=ref)

            # mnu, ttl = 'EDT', 'Editor'
            mnu, ttl = 'EDT', 'Editor'
            obj.edt_ctx_active = True
        if DEBUG['CTX']: print(ttl)
    # notebook
    elif ref in 'NBK':
        if DEBUG['CTX']: print('Notebook')
        if not sec['Notebook']:
            return
        # use right clicked page tab (focus irrelevant)
        cur = evt.Selection
        doc = nbk.GetPage(cur)
        # select right clicked page tab (set focus)
#FIX, when 'TabRightClickIsSelect = False', active tab is used instead of unfocused tab
        if cfg['Notebook']['TabRightClickIsSelect']:
            nbk.SetSelection(cur)
        # mod and lck indicator in title
        mod = cfg['General']['DocModifiedIndicator'] if doc.IsModified() else TXT_NIL
        lck = cfg['General']['DocReadOnlyIndicator'] if doc.ReadOnly else TXT_NIL
        # mnu, ttl = 'NBK', f'Notebook: [{doc.fnm}{mod}{lck}]'
        mnu, ttl = 'NBK', f'Notebook: [{doc.fnm}{mod}{lck}]'
    # menubar
    elif ref in 'MBR':
        if DEBUG['CTX']: print('MenuBar')
        if not sec['MenuBar']:
            return
        # mnu, ttl = 'MBR', 'MenuBar'
        mnu, ttl = 'MBR', 'MenuBar'
    # toolbar
    elif ref in 'TBR':
        if DEBUG['CTX']: print('ToolBar')
        if not sec['ToolBar']:
            return
        # mnu, ttl = 'TBR', 'ToolBar'
        mnu, ttl = 'TBR', 'ToolBar'
    # infobar
    elif ref in 'IBR':
        if DEBUG['CTX']: print('InfoBar')
        if not sec['InfoBar']:
            return
        # mnu, ttl = 'IBR', 'InfoBar'
        mnu, ttl = 'IBR', 'InfoBar'
    # statusbar
    elif ref in 'SBR':
        if DEBUG['CTX']: print('StatusBar')
        # click position and statusbar client rectangle
        pos = evt.Position
        pos = sb.ClientToScreen(pos) if sec['LeftClick'] else pos
        rct, clk_fld = sb.get_clicked_field(pos)

        # click on statusbar?
        if rct.Contains(pos):
            # when no document open, allow ONLY main statusbar context menu
            if not nbk.PageCount:
                clk_fld = 'SBR'
            # ... on panel switcher field?
            if clk_fld == 'PSW':
#FIX, replace 'StatusBar' when 'PSW' config section implemented
                if not sec['PanelSwitcher']:
                    return
                # mnu, ttl = 'PSW', 'Panel Switcher'
                mnu, ttl = 'PSW', 'Panel Switcher'



#FIX, create global icon size, now TEMPORARILY using 'SearchPanel' setting
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                siz = 16
                # siz = cfg['SearchPanel']['IconSize']

                # set menu icon size
                for m in tlw.ctx[mnu]:
                    if m is not None and not m[3].endswith(f'{siz}'):
                        m[3] = f'{m[3]}_{siz}'

                # mnu[0][3]  = f'ruler_panel_{siz}'
                # mnu[2][3]  = f'ruler_panel_{siz}'
                # mnu[3][3]  = f'ruler_panel_{siz}'
                # mnu[4][3]  = f'ruler_panel_{siz}'
                # mnu[5][3]  = f'ruler_panel_{siz}'
                # mnu[7][3]  = f'search_panel_{siz}'
                # mnu[8][3]  = f'ruler_panel_{siz}'
                # mnu[9][3]  = f'side_panel_{siz}'
                # mnu[10][3] = f'code_context_{siz}'
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


            # ... on search flags field?
            elif clk_fld == 'SCH':
#FIX, replace 'StatusBar' when 'PSW' config section implemented
                if not sec['SearchFlags']:
                    return
                # mnu, ttl = 'SCH', 'Search Flags'
                mnu, ttl = 'SCH', 'Search Flags'
            # ... on file encoding field?
            elif clk_fld == 'ENC':
#FIX, replace 'StatusBar' when 'ENC' config section implemented
                if not sec['FileEncoding']:
                    return
                # mnu, ttl = 'ENC', 'File Encoding (not implemented)'
                mnu, ttl = 'ENC', 'File Encoding (not implemented)'
            # ... on end of line field?
            elif clk_fld == 'EOL':
#FIX, replace 'StatusBar' when 'EOL' config section implemented
                if not sec['EndOfLine']:
                    return
                # mnu, ttl = 'EOL', 'End of Line'
                mnu, ttl = 'EOL', 'End of Line'
            # ... on indentation field?
            elif clk_fld == 'IND':
#FIX, replace 'StatusBar' when 'IND' config section implemented
                if not sec['Indentation']:
                    return
                # mnu, ttl = 'IND', 'Indentation (almost implemented)'
                mnu, ttl = 'IND', 'Indentation (almost implemented)'
            # ... on language field?
            elif clk_fld == 'LNG':
                if not sec['Language']:
                    return
                # mnu, ttl = 'LNG', 'Language'  # 'Syntax Highlighting'
                mnu, ttl = 'LNG', 'Language'  # 'Syntax Highlighting'
            # ... on another statusbar area
            else:
                if not sec['StatusBar']:
                    return
                # mnu, ttl = 'SBR', 'StatusBar'
                mnu, ttl = 'SBR', 'StatusBar'
            if DEBUG['CTX']: print(ttl)
        else:
            return
    # ruler
    elif ref in 'RLR':
        if DEBUG['CTX']: print('Ruler')
        if not sec['Ruler']:
            return
        # mnu, ttl = 'RLR', 'Ruler'
        mnu, ttl = 'RLR', 'Ruler'
    # code context
    elif ref in 'CCX':
    # elif ref in 'STT':  # StaticText':
        if DEBUG['CTX']: print('Code Context')
        if not sec['CodeContext']:
            return
        # mnu, ttl = 'CCX', 'Code Context'
        mnu, ttl = 'CCX', 'Code Context'
    # bookmark
    elif ref in 'BMK':
        if DEBUG['CTX']: print('Bookmark')
        if not sec['BookmarkList']:
            return
        # bookmark list control item selected?
        if (idx := (ctl := doc.spt_lst[SPT.BMK.idx]).FocusedItem) < 0:
            return
        # menu title
        lin = int(ctl.GetItemText(idx, 2))  # lineno in title
        ttl = f' #{idx + 1}, Line {lin}'
        # mnu, ttl = 'BMK', 'Bookmark' + ttl
        mnu, ttl = 'BMK', 'Bookmark' + ttl
    # symbol def
    elif ref in 'SDF':
        if DEBUG['CTX']: print('Symbol Def')
        if not sec['SymbolDef']:
            return
        # mnu, ttl = 'SDF', 'Symbol Def'
        mnu, ttl = 'SDF', 'Symbol Def'
    # task
    elif ref in 'TSK':
        if DEBUG['CTX']: print('Task')
        if not sec['TaskList']:
            return
        # task list control item selected?
        if (idx := (ctl := doc.spt_lst[SPT.TSK.idx]).FocusedItem) < 0:
            return
        # menu title
        lin = int(ctl.GetItemText(idx, 2))  # lineno in title
        dsc = ctl.GetItemText(idx, 3).strip()  # description
        ttl = f' #{idx + 1}, Line {lin}'

        oac = tlw.file_open_at_caret(None, src=ref, dsc=dsc)

        # mnu, ttl = 'TSK', 'Task' + ttl
        mnu, ttl = 'TSK', 'Task' + ttl
    # breakpoint
    elif ref in 'BPT':
        if DEBUG['CTX']: print('Breakpoint')
        if not sec['BreakpointList']:
            return
        # breakpoint list control item selected?
        if (idx := (ctl := doc.spt_lst[SPT.BPT.idx]).FocusedItem) < 0:
            return
        # menu title
        lin = int(ctl.GetItemText(idx, 3))  # lineno in title
        ttl = f' #{idx + 1}, Line {lin}'
        # mnu, ttl = 'BPT', 'Breakpoint' + ttl
        mnu, ttl = 'BPT', 'Breakpoint' + ttl
    # doc map
    elif ref in 'DCM':
        if DEBUG['CTX']: print('DocMap')
        if not sec['DocMap']:
            return
        # mnu, ttl = 'DCM', 'DocMap'
        mnu, ttl = 'DCM', 'DocMap'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # search panel: find field
    elif ref in 'FNF':
        if DEBUG['CTX']: print('Find Field')
        if not sec['FindHistory']:
            return
        # mnu, ttl, sch_fld = 'FNF', 'Find Field History', sch.txc_fnd
        mnu, ttl, sch_fld = 'FNF', 'Find Field History', sch.txc_fnd
    # search panel: replace field
    elif ref in 'RPF':
        if DEBUG['CTX']: print('Replace Field')
        if not sec['ReplaceHistory']:
            return
        # mnu, ttl, sch_fld = 'RPF', 'Replace Field History', sch.txc_rpl
        mnu, ttl, sch_fld = 'RPF', 'Replace Field History', sch.txc_rpl
    # search panel: where field
    elif ref in 'WHF':
        if DEBUG['CTX']: print('Where Field')
        if not sec['WhereHistory']:
            return
        # mnu, ttl, sch_fld = 'WHF', 'Where Field History', sch.txc_whr
        mnu, ttl, sch_fld = 'WHF', 'Where Field History', sch.txc_whr
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # search panel: where button
    elif ref in 'WHR':
        if DEBUG['CTX']: print('Find In Files: Where')
        # mnu, ttl = 'WHR', 'Where'
        mnu, ttl = 'WHR', 'Where'
    elif ref in 'RES':
        if DEBUG['CTX']: print('Search Results')
        if not sec['SearchResults']:
            return
        # mnu, ttl = 'RES', 'Search Results'
        mnu, ttl = 'RES', 'Search Results'
    else:
        # we should NEVER get here
        err = f'{tlw.__class__.__name__}: unknown context menu reference [{ref}]'
        raise AssertionError(err)


    # filter search fields history when selection exists
    if ref in ('FNF', 'RPF', 'WHF'):
        flt_txt = sel if (sel := sch_fld.StringSelection) else TXT_NIL
        print(f'sel = [{sel}]  {sch_fld.CanUndo() = }', )
        his_lst, his_fnc = sch_fld.his_lst, gui.CtxSearchHistory
        flt_lst = [itm for itm in his_lst if itm.lower().startswith(flt_txt.lower())]
        tlw.ctx[mnu] = [(f'{idx}  {itm}', NO_SCT, his_fnc) for idx, itm in enumerate(flt_lst, start=1)]


    ctx_lst = list(tlw.ctx[mnu])  # tuple -> list


    if ref in ('EDT', 'TSK'):
        if oac and oac.find('://') >= 0:
            # prepend URL and separator if present in editor
            ctx_lst.insert(0, (f'Open URL: {oac}', NO_SCT, lambda u: webbrowser.open(oac), NO_HLP, NO_ICO))
            ctx_lst.insert(1, (SEP))
        elif oac:
#NOTE, prevent circular dependency
            from common.file import open_files

            # prepend filename and separator if present in editor
            ctx_lst.insert(0, (f'Open File: {oac}', NO_SCT, lambda f: open_files([[oac]]), NO_HLP, NO_ICO))
            ctx_lst.insert(1, (SEP))


    # customize font/icon with 'set_menu_item_label'/'set_menu_item_icon'
    # pre-process title attributes: prepend menu title and separator
    if sec['ShowTitle']:
        ctx_lst.insert(0, (ttl + '[[bold]]', NO_SCT, NO_ACT, NO_HLP, 'context_menu'))
        if  ref in ('FNF', 'RPF', 'WHF') and flt_txt:
            ctx_lst.insert(1, (f'Filter: <<{flt_txt}>>[[bold]][[italic]]', NO_SCT, NO_ACT, NO_HLP, 'context_menu'))
            sep_pos = 2
        else:
            sep_pos = 1
        ctx_lst.insert(sep_pos, (SEP))


    # build menu
    mnu_ctx = mb.build_submenu(tlw, ctx_lst)


    # post-process title attributes: disable/colour
    if sec['ShowTitle']:
        for ttl_pos in range(2 if (ref in ('FNF', 'RPF', 'WHF') and flt_txt) else 1):
            ttl = mnu_ctx.FindItemByPosition(ttl_pos)
            ttl.Enable(False)  # disable title
            ttl.SetBackgroundColour(sec['TitleBackColour'])


    # context menu items: enable/disable and/or (un)check
    # notebook
    if ref in 'NBK':
#NOTE, prevent circular dependency
        from common.file import win32_file_properties

        mnu_ctx.Enable(MI['NBK_CAO'], bool(nbk.PageCount > 1))
        mnu_ctx.Enable(MI['NBK_CAL'], bool(cur > 0))
        mnu_ctx.Enable(MI['NBK_CAR'], bool(cur + 1 < nbk.PageCount))
        # rebind and pass path to Windows file properties call
        pnm = doc.pnm
        mnu_ctx.Bind(wx.EVT_MENU, lambda e: win32_file_properties(pnm), MI['NBK_WFP'])
    # editor
    elif ref in 'EDT' and mnu == 'EDT':
        # clear token styles 1 to 5
        cnt = 0
        for i in range(1, 6):
            mnu_ctx.Enable(MI[f'EDT_CS{i}'], bool(doc.sty_active[i]))
            if doc.sty_active[i]:
                cnt += 1
        # clear all token styles
        mnu_ctx.Enable(MI[f'EDT_CSA'], bool(cnt))
    # margin
    elif ref in 'EDT' and mnu == 'MGN':
        cnt_lst = (len(doc.get_bookmarks()), len(doc.get_breakpoints()))
        mnu_ctx.Enable(MI[f'MGN_CBM'], bool(cnt_lst[0]))
        mnu_ctx.Enable(MI[f'MGN_CBP'], bool(cnt_lst[1]))
        mnu_ctx.Enable(MI[f'MGN_CAM'], bool(cnt_lst[0] or cnt_lst[1]))
    # toolbar
    elif ref in 'TBR':
        for key in TBX:
            if key != 'CUS':
                mnu_ctx.Check(*TBX[key])
        mnu_ctx.Enable(TBX['SHW_ICO'][0], bool(TBX['SHW_TXT'][1]))
        mnu_ctx.Enable(TBX['SHW_TXT'][0], bool(TBX['SHW_ICO'][1]))
        mnu_ctx.Enable(TBX['LRG_ICO'][0], bool(TBX['SHW_ICO'][1]))
        mnu_ctx.Enable(TBX['LRG_TXT'][0], bool(TBX['SHW_TXT'][1]))
        mnu_ctx.Enable(TBX['ALN_HOR'][0], bool(TBX['SHW_ICO'][1] and TBX['SHW_TXT'][1]))
    # statusbar
    elif ref in 'SBR':
        # main
        if not clk_fld or clk_fld not in ('PSW', 'SCH', 'ENC', 'EOL', 'IND', 'LNG'):
            for key in SBX:
                mnu_ctx.Check(*SBX[key][:2])
            # 1st 3 statusbar fields always visible, though disabled
            disabled_lst = ['PSW', 'MSG', 'AUX']
            for key in disabled_lst:
                mnu_ctx.Enable(SBX[key][0], False)
        # file encoding
        elif clk_fld == 'ENC':
            for key in SBX_ENC:
                mnu_ctx.Check(*SBX_ENC[key])
        # end of line
        elif clk_fld == 'EOL':
            for key in SBX_EOL:
                mnu_ctx.Check(*SBX_EOL[key])
            # always disable 'mixed EOLs'
            mnu_ctx.Enable(SBX_EOL['EMX'][0], False)
        # search options
        elif clk_fld == 'SCH':
            # sync search options context menu with main menu selections
            for flg  in ('CAS', 'REG', 'WRD', 'WRP', 'ISL', 'HLM', 'PCS', 'CXT', 'BUF'):
                key = f'SCH_{flg}'
                chk, ena = mb.IsChecked(MI[key]), mb.IsEnabled(MI[key])
                mnu_ctx.Check(MI[key], chk and ena)
                mnu_ctx.Enable(MI[key], ena)
        # indentation
        elif clk_fld == 'IND':
            # sync indentation context menu with main menu selections
            mnu_ctx.Check(MI['IND_IUS'], mb.IsChecked(MI['IND_IUS']))
            for key in MI:
                if not key.startswith('IND_TW'):
                    continue
                mnu_ctx.Check(MI[key], mb.IsChecked(MI[key]))
        # language
        elif clk_fld == 'LNG':
#FIX, needs better coding...
            tlw.update_keyword_sets_menu(None, mnu_ctx)
            # sync language context menu with main menu selection
            id_ = [m[4] for m in LANG if mb.IsChecked(m[4])][0]
            mnu_ctx.Check(id_, True)
    # doc map
    elif ref in 'DCM':
        for key in DMX:
            mnu_ctx.Check(*DMX[key])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, 'AutoFocus' disabled, not fully impemented, maybe obsolete
        mnu_ctx.Enable(DMX['AUT_FCS'][0], False)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def context_menu_highlight(evt, mnu_ctx, tlw):
        id_ = evt.Id
        # emulate statusbar help text for context menu items
        itm = mnu_ctx.FindItemById(id_)
        hlp = itm.Help if itm else NO_HLP
        sb.set_text(hlp)
        if DEBUG['CTX']: print(f'{me_()}, {[hlp]}')


#HACK: highlighting only used for context menus (NOT main menu)
    tlw.Bind(wx.EVT_MENU_HIGHLIGHT, lambda e: context_menu_highlight(e, mnu_ctx, tlw))
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#HACK: for debugging 'file_open_at_caret'
    # import time
    # time.sleep(1)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    obj.PopupMenu(mnu_ctx)
    tlw.Bind(wx.EVT_MENU_HIGHLIGHT_ALL, None)

    obj.edt_ctx_active = False
