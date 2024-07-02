#!/usr/bin/python

from pprint import pprint
import webbrowser

import wx

from common.util import curdoc, rs_
from conf.debug import DBG, me_
from const.common import TXT_NIL
from const.editor import MGN
from const import glb
from const.lang import LANG
from const.menubar import NO_ACT, NO_HLP, NO_ICO, NO_SCT, SEP, MI, DMX
from const.sidepanel import SPT
from const.searchpanel import SCH_FLAGS
from const.statusbar import SBR_CTX_FIELDS, SBX, SBX_ENC, SBX_EOL
from const.toolbar import TBX
import gui


#FIX, refactor to class ??
@curdoc
def ContextMenu(evt, ref=TXT_NIL):
    """Show context menu for specific reference.

    Three stages for building menu:
        1. get menu defs for passed ref
        2. preprocess and build menu
        3. enable/disable radio/check menu items

    Args:
        evt: wx.EVT_CONTEXT_MENU
        ref: key for menu reference in CTX_REF_MAP (default: {TXT_NIL})

    Raises:
        AssertionError: unknown context menu reference
    """

    def __is_disabled(mnu):
        """Check if menu is disabled in config.

        Args:
            mnu: menu reference in CTX_REF_MAP

        Returns:
            bool
        """
        txt = f'{me_("F")}: [{mnu}] [{sec_key}] [{ttl}]'
        DBG('CTX==0', f'{txt}')
        if mnu in {'SBR', *SBR_CTX_FIELDS}:
            print(f'{txt} ({f"[{clk_fld}] was clicked" if mnu != clk_fld else "same as clicked"})')
        else:
            print(f'{txt} -> {[gui.BEWARE_] = }')

        if sec[sec_key]:
            return False
        print(f'Context menu [{sec_key}] disabled: returning')
        return True

    def __highlight(evt, mnu_ctx, tlw):
        """Emulate statusbar help text for context menu items.

        Args:
            evt: wx.EVT_MENU_HIGHLIGHT
            mnu_ctx: ready built context menu
            tlw: top level window (AppFrame)
        """
        id_ = evt.Id
        itm = mnu_ctx.FindItemById(id_)
        hlp = itm.Help if itm else NO_HLP
        sbr.set_text(hlp)
        DBG('CTX', f'{me_()}, {[hlp]}')

    if not (doc := glb.DOC): return

    # discard context menu when symbol popup active
    if doc.spu_active:
        return

    if ref not in gui.CTX_REF_MAP:
        # we should NEVER get here
        err = f'{glb.TLW.__class__.__name__}: unknown context menu reference [{ref}]'
        raise AssertionError(err)

    cfg, tlw, mbr, sbr, nbk, sch = glb.CFG, glb.TLW, glb.MBR, glb.SBR, glb.NBK, glb.SCH
    obj = evt.EventObject
    sec = cfg['ContextMenu']

    mnu = ref
    (sec_key, ttl) = gui.CTX_REF_MAP[mnu]

    if mnu in 'EDT':
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
            DBG('CTX', 'Margin', doc.GetMarginWidth(m))
            wid += doc.GetMarginWidth(m)
        DBG('CTX', f'{rs_(9)}\n Total', wid)
        # convert editor client rectangle to screen coordinates
        rct = wx.Rect(doc.ClientToScreen(clt.Position), clt.Size)
        DBG('CTX', f'  pos: [{pos}], clt: [{clt}], rct: [{rct}]')
        # set editor client rectangle to margin width
        rct.SetWidth(wid)
        DBG('CTX', f'  pos: [{pos}], clt: [{clt}], rct: [{rct}]')
        # right click on editor margin?
        oac = None
        if rct.Contains(pos):
            mnu = 'MGN'
        else:
            oac = tlw.file_open_at_caret(src=mnu)
            obj.edt_ctx_active = True

        (sec_key, ttl) = gui.CTX_REF_MAP[mnu]

        DBG('CTX', ttl)
    elif mnu in 'NBK':
        # use right clicked page tab (focus irrelevant)
        cur = evt.Selection
        # doc = nbk.GetPage(cur)
        # select right clicked page tab (set focus)
#FIX, when 'TabRightClickIsSelect = False', active tab is used instead of unfocused tab
        if cfg['Notebook']['TabRightClickIsSelect']:
            nbk.SetSelection(cur)
        # mod and lck indicator in title
        mod = cfg['General']['DocModifiedIndicator'] if doc.IsModified() else TXT_NIL
        lck = cfg['General']['DocReadOnlyIndicator'] if doc.ReadOnly else TXT_NIL
        ttl += f': [{doc.fnm}{mod}{lck}]'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: for 'split_editor'
        # print(tlw.ctx[mnu][6][0])
        # tlw.ctx[mnu] = list(tlw.ctx[mnu])
        # tlw.ctx[mnu][6][0] = 'UN***SPLIT' if doc.Parent.IsSplit() else 'SPLIT'
        # print('UN***SPLIT' if doc.Parent.IsSplit() else 'SPLIT')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    elif mnu in 'MBR':
#HACK, show ONLY when right click on top level frame (caption area)
        if not sec['MenuBar'] or obj != glb.TLW:
            return
    elif mnu in 'SBR':
        # click position and statusbar client rectangle
        pos = evt.Position
        pos = sbr.ClientToScreen(pos) if sec['LeftClick'] else pos
        rct, clk_fld = sbr.get_clicked_field(pos)

        # prevent fall through (edge cases)
        if clk_fld is None or not rct.Contains(pos) or not nbk.PageCount:
            return

        # show main statusbar context menu when these field rectangles are clicked
        mnu = 'SBR' if clk_fld not in SBR_CTX_FIELDS else clk_fld
        (sec_key, ttl) = gui.CTX_REF_MAP[mnu]

        # process clicked field (panel switcher?)
        if mnu in 'PSW':

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

        # ... one of the other fields? (stub)
        elif mnu in {'SCH', 'ENC', 'EOL', 'IND', 'LNG'}:
            ...

        DBG('CTX', ttl)
    elif mnu in 'BMK':
        # bookmark list control item selected?
        if (idx := (ctl := doc.spt_lst[SPT.BMK.idx]).FocusedItem) < 0:
            return
        # menu title
        lin = int(ctl.GetItemText(idx, 2))  # lineno in title
        ttl += f' #{idx + 1}, Line {lin}'
    elif mnu in 'TSK':
        # task list control item selected?
        if (idx := (ctl := doc.spt_lst[SPT.TSK.idx]).FocusedItem) < 0:
            return
        # menu title
        lin = int(ctl.GetItemText(idx, 2))  # lineno in title
        dsc = ctl.GetItemText(idx, 3).strip()  # description
        ttl += f' #{idx + 1}, Line {lin}'
        oac = tlw.file_open_at_caret(src=mnu, dsc=dsc)
    elif mnu in 'BPT':
        # breakpoint list control item selected?
        if (idx := (ctl := doc.spt_lst[SPT.BPT.idx]).FocusedItem) < 0:
            return
        # menu title
        lin = int(ctl.GetItemText(idx, 3))  # lineno in title
        ttl += f' #{idx + 1}, Line {lin}'
    elif mnu in 'FNF':
        sch_fld = sch.txc_fnd
    elif mnu in 'RPF':
        sch_fld = sch.txc_rpl
    elif mnu in 'WHF':
        sch_fld = sch.txc_whr

    if __is_disabled(mnu):
        return

    # filter search fields history when selection exists
    if mnu in {'FNF', 'RPF', 'WHF'}:
        flt_txt = sel if (sel := sch_fld.StringSelection) else TXT_NIL
        # print(f'sel = [{sel}]  {sch_fld.CanUndo() = }', )
        his_lst, his_fnc = sch_fld.his_lst, gui.CtxSearchHistory
        flt_lst = [itm for itm in his_lst if flt_txt.lower() in itm.lower()]
        tlw.ctx[mnu] = [(f'{idx}  {itm}', NO_SCT, his_fnc) for idx, itm in enumerate(flt_lst, start=1)]

    ctx_lst = list(tlw.ctx[mnu])  # tuple -> list

    # found URL or filename; prepend it in menu with separator
    if mnu in {'EDT', 'TSK'}:
        if oac and oac.find('://') >= 0:
            ctx_lst.insert(0, (f'Open URL: {oac}', NO_SCT, lambda u: webbrowser.open(oac), NO_HLP, NO_ICO))
            ctx_lst.insert(1, (SEP))
        elif oac:
#NOTE, prevent circular dependency
            from common.file import open_files
            ctx_lst.insert(0, (f'Open File: {oac}', NO_SCT, lambda f: open_files([[oac]]), NO_HLP, NO_ICO))
            ctx_lst.insert(1, (SEP))

    # customize font/icon with 'set_menu_item_label'/'set_menu_item_icon'
    # pre-process title attributes: prepend menu title and separator
    if sec['ShowTitle']:
        ctx_lst.insert(0, (ttl + '[[bold]]', NO_SCT, NO_ACT, NO_HLP, 'context_menu'))
        if  mnu in ('FNF', 'RPF', 'WHF') and flt_txt:
            ctx_lst.insert(1, (f'Filter: <<{flt_txt}>>[[bold]][[italic]]', NO_SCT, NO_ACT, NO_HLP, 'context_menu'))
            sep_pos = 2
        else:
            sep_pos = 1
        ctx_lst.insert(sep_pos, (SEP))

    # build menu
    mnu_ctx = mbr.build_submenu(tlw, ctx_lst)

    # post-process title attributes: disable/colour
    if sec['ShowTitle']:
        for ttl_pos in range(2 if (mnu in ('FNF', 'RPF', 'WHF') and flt_txt) else 1):
            ttl = mnu_ctx.FindItemByPosition(ttl_pos)
            ttl.Enable(False)  # disable title
            ttl.SetBackgroundColour(sec['TitleBackColour'])

    # context menu items: enable/disable and/or (un)check
    # notebook
    if mnu in 'NBK':
#NOTE, prevent circular dependency
        from common.file import win32_file_properties

        mnu_ctx.Enable(MI['NBK_CAO'], bool(nbk.PageCount > 1))
        mnu_ctx.Enable(MI['NBK_CAL'], bool(cur > 0))
        mnu_ctx.Enable(MI['NBK_CAR'], bool(cur + 1 < nbk.PageCount))
        # rebind and pass path to Windows file properties call
        pnm = doc.pnm
        mnu_ctx.Bind(wx.EVT_MENU, lambda e: win32_file_properties(pnm), MI['NBK_WFP'])
    # editor
    elif mnu in 'EDT':
        # clear token styles 1 to 5
        cnt = 0
        for i in range(1, 6):
            mnu_ctx.Enable(MI[f'EDT_CS{i}'], bool(doc.sty_active[i]))
            if doc.sty_active[i]:
                cnt += 1
        # clear all token styles
        mnu_ctx.Enable(MI['EDT_CSA'], bool(cnt))
    # margin
    elif mnu in 'MGN':
        cnt_lst = (len(doc.get_bookmarks()), len(doc.get_breakpoints()), len(doc.get_task_markers()))
        mnu_ctx.Enable(MI['MGN_DBM'], bool(cnt_lst[0]))
        mnu_ctx.Enable(MI['MGN_DBP'], bool(cnt_lst[1]))
        mnu_ctx.Enable(MI['MGN_DTM'], bool(cnt_lst[2]))
        mnu_ctx.Enable(MI['MGN_DAM'], any(cnt_lst))
    # toolbar
    elif mnu in 'TBR':
        for key in TBX:
            if key != 'CUS':
                mnu_ctx.Check(*TBX[key])
        mnu_ctx.Enable(TBX['SHW_ICO'][0], bool(TBX['SHW_TXT'][1]))
        mnu_ctx.Enable(TBX['SHW_TXT'][0], bool(TBX['SHW_ICO'][1]))
        mnu_ctx.Enable(TBX['LRG_ICO'][0], bool(TBX['SHW_ICO'][1]))
        mnu_ctx.Enable(TBX['LRG_TXT'][0], bool(TBX['SHW_TXT'][1]))
        mnu_ctx.Enable(TBX['ALN_HOR'][0], bool(TBX['SHW_ICO'][1] and TBX['SHW_TXT'][1]))
    # statusbar
    elif mnu in {'SBR', *SBR_CTX_FIELDS}:
        # main
        if mnu not in SBR_CTX_FIELDS:
            for key in SBX:
                mnu_ctx.Check(SBX[key].id, SBX[key].chk)
            # 1st 3 statusbar fields always visible, though disabled
            disabled_lst = ['PSW', 'MSG', 'AUX']
            for key in disabled_lst:
                mnu_ctx.Enable(SBX[key].id, False)
        # file encoding
        elif mnu in 'ENC':
            for key in SBX_ENC:
                mnu_ctx.Check(SBX_ENC[key].id, SBX_ENC[key].chk)
        # end of line
        elif mnu in 'EOL':
            for key in SBX_EOL:
                mnu_ctx.Check(SBX_EOL[key].id, SBX_EOL[key].chk)
            # always disable 'mixed EOLs'
            mnu_ctx.Enable(SBX_EOL.EMX.id, False)
        # search options
        elif mnu in 'SCH':
            # sync search options context menu with main menu selections
            for flg in SCH_FLAGS:
                key = f'SCH_{flg}'
                chk, ena = mbr.IsChecked(MI[key]), mbr.IsEnabled(MI[key])
                mnu_ctx.Check(MI[key], chk and ena)
                mnu_ctx.Enable(MI[key], ena)
        # indentation
        elif mnu in 'IND':
            # sync indentation context menu with main menu selections
            mnu_ctx.Check(MI['IND_IUS'], mbr.IsChecked(MI['IND_IUS']))
            for key in MI:
                if not key.startswith('IND_TW'):
                    continue
                mnu_ctx.Check(MI[key], mbr.IsChecked(MI[key]))
        # language
        elif mnu in 'LNG':
#FIX, needs better coding...
            glb.SMS('pub_kws', mnu_obj=mnu_ctx)
            # sync language context menu with main menu selection
            id_ = [m[4] for m in LANG if mbr.IsChecked(m[4])][0]
            mnu_ctx.Check(id_, True)
    # doc map
    elif mnu in 'DCM':
        for key in DMX:
            mnu_ctx.Check(*DMX[key])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, 'AutoFocus' disabled, not fully impemented, maybe obsolete
        mnu_ctx.Enable(DMX['AUT_FCS'][0], False)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#HACK, highlighting only used for context menus (NOT main menu)
    tlw.Bind(wx.EVT_MENU_HIGHLIGHT, lambda e: __highlight(e, mnu_ctx, tlw))
    obj.PopupMenu(mnu_ctx)
    tlw.Bind(wx.EVT_MENU_HIGHLIGHT, None)

    obj.edt_ctx_active = False
