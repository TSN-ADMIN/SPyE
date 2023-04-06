#!/usr/bin/python

from pprint import pprint

import wx

from common.doc import get_doc
# from common.file import win32_file_properties, open_files
from common.path import cwd
from common.util import not_implemented, set_icon, swap_dict
from conf.debug import DEBUG, dbg_CTXTTB
from const.editor import MGN
from const import glb
from const.menu import MI, BMX, SDX, TSX, BPX, DMX
from const.sidepanel import SPT
from const.statusbar import SBF, SBF_CPY, SBX, SBX_ENC, SBX_EOL
from const.toolbar import TBX
from extern.itemspicker import (
    ItemsPicker, IP_REMOVE_FROM_CHOICES, EVT_IP_SELECTION_CHANGED
)


def CtxToolBar(evt):
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)
    sec = cfg['ToolBar']
    tb = glb.TB

    if DEBUG['TBR']: print(f'  label = [{lbl}]')
    if DEBUG['TBR']: print(f'bitmask = {tb.WindowStyle:016b}\n')

    # customize toolbar
    if id_ == TBX['CUS'][0]:
        # helper mapping (key: tool label) to populate and process items picker dialog
        selectable_lbl_dct = {}
        for key in tb.ttd:
            selectable_lbl_dct[key] = tb.ttd[key][2]
        if DEBUG['TBR']: pprint(selectable_lbl_dct)

        # populate picker lists
        available = []
        selected = []
        for key in tb.ttd:
            if key in sec['Tools']:
                selected.append(selectable_lbl_dct[key])
            else:
                available.append(selectable_lbl_dct[key])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # for key in sec['Tools']:
        #     selected.append(selectable_lbl_dct[key])
        # for key in tb.ttd:
        #     if key not in sec['Tools']:
        #         available.append(selectable_lbl_dct[key])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # setup items picker dialog
        with wx.Dialog(tlw, size=(450, 275), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE) as dlg:
            set_icon(dlg)
            dlg.SetTitle('ToolBar Tools')

            def __ip_selection(e):
                if DEBUG['TBR']: print('selected items', e.GetItems())

            dlg.Bind(EVT_IP_SELECTION_CHANGED, __ip_selection)

            ip = ItemsPicker(dlg,
                             label='Available:',
                             selectedLabel='Selected:',
                             ipStyle=IP_REMOVE_FROM_CHOICES)
                             # ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES)

            ip.SetItems(available)
            ip.SetSelections(selected)

            dlg.Centre()
            if (res := dlg.ShowModal()) == wx.ID_CANCEL:
                print('  ID_CANCEL')
                return

        if DEBUG['TBR']: print('\nAvailable:\n----------')
        if DEBUG['TBR']: pprint(ip.Items, width=20)
        if DEBUG['TBR']: print('\n Selected:\n----------')
        if DEBUG['TBR']: pprint(ip.Selections, width=20)

        # swap helper mapping (tool label: key)
        selectable_lbl_dct = swap_dict(selectable_lbl_dct)
        if DEBUG['TBR']: pprint(selectable_lbl_dct)

        # get selected dialog items with helper mapping and update config
        sec['Tools'] = []
        for sel in ip.Selections:
            sec['Tools'].append(selectable_lbl_dct[sel])
    else:
        dbg_CTXTTB('B', TBX, cfg)

        # update toolbar context menu item check marks ('LOC_xxx' key is radio group member)
        for key in TBX:
            if id_ != TBX[key][0]:
                continue
            # process selected item
            if key.startswith('LOC_'):
                # first uncheck all LOC_xxx radio items
                for loc_key in TBX:
                    if loc_key.startswith('LOC_'):
                        TBX[loc_key][1] = False
                # check selected LOC_xxx item
                TBX[key][1] = True
            else:
                # toggle selected non-radio item
                TBX[key][1] = not TBX[key][1]
            break

        # update them in config, too
        sec['ShowIcons'] = TBX['SHW_ICO'][1]
        sec['ShowText'] = TBX['SHW_TXT'][1]
        sec['LargeIcons'] = TBX['LRG_ICO'][1]
        sec['LargeText'] = TBX['LRG_TXT'][1]
        sec['AlignHorizontally'] = TBX['ALN_HOR'][1]
        sec['Top'] = TBX['LOC_TOP'][1]
        sec['Left'] = TBX['LOC_LFT'][1]
        sec['Bottom'] = TBX['LOC_BOT'][1]
        sec['Right'] = TBX['LOC_RIT'][1]

        dbg_CTXTTB('A', TBX, cfg)

    # update toolbar
    tb.rebuild()

    if DEBUG['TBR']: print(f'bitmask = {tb.WindowStyle:016b}\n')


################################################################################################


#FIX: show/hide statusbar fields
def CtxStatusBarMain(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)
    sb = glb.SB

    sec = cfg['StatusBar']

    if DEBUG['SBR']: print(f'\n  label  = [{lbl}]')

    # selector menu items: (de)select the 'selectable_key_lst'
    selector_lst = ['ALL', 'NON', 'CUS']
    disabled_lst = ['PSW', 'MSG', 'AUX']

    # selectable menu item keys: to (un)check statusbar fields (1st 3 fields always visible though disabled)
    selectable_key_lst = [key for key in SBX if key not in selector_lst + disabled_lst]
    print(selectable_key_lst)
    if DEBUG['SBR']: pprint(selectable_key_lst, width=9)

    # check 'All' or 'None' selector and (un)check all selectables
    if id_ == SBX['ALL'][0]:
        SBX['ALL'][1] = True
        for key in selectable_key_lst:
            SBX[key][1] = True
    elif id_ == SBX['NON'][0]:
        SBX['NON'][1] = True
        for key in selectable_key_lst:
            SBX[key][1] = False
    # check custom selector, proceed to items picker dialog
    elif id_ == SBX['CUS'][0]:
        SBX['CUS'][1] = True

        # helper mapping (key: menu label) to populate and process items picker dialog
        selectable_lbl_dct = {}
        for key in selectable_key_lst:
            selectable_lbl_dct[key] = SBX[key][2]
        if DEBUG['SBR']: pprint(selectable_lbl_dct)

        # populate picker lists
        available = []
        selected = []
        for key in selectable_key_lst:
            if SBX[key][1]:
                selected.append(selectable_lbl_dct[key])
            else:
                available.append(selectable_lbl_dct[key])

        # setup items picker dialog
        with wx.Dialog(tlw, size=(450, 275), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE) as dlg:
            set_icon(dlg)
            dlg.SetTitle('StatusBar Fields')

            def __ip_selection(e):
                if DEBUG['SBR']: print('selected items', e.GetItems())

            dlg.Bind(EVT_IP_SELECTION_CHANGED, __ip_selection)

            ip = ItemsPicker(dlg,
                             label='Available:',
                             selectedLabel='Selected:',
                             ipStyle=IP_REMOVE_FROM_CHOICES)
                             # ipStyle=IP_SORT_SELECTED | IP_SORT_CHOICES | IP_REMOVE_FROM_CHOICES)

            ip.SetItems(available)
            ip.SetSelections(selected)

            dlg.Centre()
            if (res := dlg.ShowModal()) == wx.ID_CANCEL:
                print('  ID_CANCEL')
                return

        if DEBUG['SBR']: print('\nAvailable:\n----------')
        if DEBUG['SBR']: pprint(ip.Items, width=20)
        if DEBUG['SBR']: print('\n Selected:\n----------')
        if DEBUG['SBR']: pprint(ip.Selections, width=20)

        # swap helper mapping (menu label: key)
        selectable_lbl_dct = swap_dict(selectable_lbl_dct)
        if DEBUG['SBR']: pprint(selectable_lbl_dct)

        # uncheck available dialog items with helper mapping
        for key in ip.Items:
            SBX[selectable_lbl_dct[key]][1] = False

        # check selected dialog items with helper mapping
        for sel in ip.Selections:
            SBX[selectable_lbl_dct[sel]][1] = True
    # (un)check clicked selectable
    else:
        for key in selectable_key_lst:
            if id_ == SBX[key][0]:
                SBX[key][1] = not SBX[key][1]
                if DEBUG['SBR']: print(f'   [{key}] -> clicked')
            else:
                if DEBUG['SBR']: print(f'    {key}')

    # check selector based on checked item count
    cnt = 0
    for key in selectable_key_lst:
        if SBX[key][1]:
            cnt += 1

    SBX['ALL'][1] = bool(cnt == len(selectable_key_lst))
    SBX['NON'][1] = bool(cnt == 0)
    SBX['CUS'][1] = bool(0 < cnt < len(selectable_key_lst))

    # rebuild statusbar fields
    SBF.clear()
    cnt = 0
    for key, val in SBF_CPY.items():
        if SBX[key][1]:
            SBF[key] = val     # original list
            SBF[key][0] = cnt  # field number (consecutive)
            cnt += 1

    # update config
    sec['Fields'] = list(SBF)

    # update statusbar
    sb.rebuild()


################################################################################################


def CtxStatusBarSCH(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    # if DEBUG['SBR']:
    print(f'\n  label  = [{lbl}]')

    tlw.toggle_search_option(evt)


################################################################################################


def CtxStatusBarENC(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    if DEBUG['SBR']: print(f'\n  label  = [{lbl}]')

#NOTE, although defined as 'CHECK', this group is treated like a 'RADIO' group
#NOTE, because: we need separators in menu and 'RADIO' needs a discontiguous range
    # update statusbar (file encoding) context menu item check marks
    for key in SBX_ENC:
        itm = SBX_ENC[key]
        itm[1] = bool(id_ == itm[0])

#FIX, implement handlers
    if id_ == SBX_ENC['U08'][0]:
        print('# UTF-8')
    elif id_ == SBX_ENC['U6L'][0]:
        print('# UTF-16 LE')
    elif id_ == SBX_ENC['U6B'][0]:
        print('# UTF-16 BE')
    elif id_ == SBX_ENC['WIN'][0]:
        print('# Western (Windows 1252)')
        # doc.StyleSetFontEncoding(stc.STC_STYLE_DEFAULT, wx.FONTENCODING_CP1252)
    elif id_ == SBX_ENC['I01'][0]:
        print('# Western (ISO-8859-1)')
    elif id_ == SBX_ENC['I03'][0]:
        print('# Western (ISO-8859-3)')
    elif id_ == SBX_ENC['I15'][0]:
        print('# Western (ISO-8859-15)')
        # doc.StyleSetFontEncoding(stc.STC_STYLE_DEFAULT, wx.FONTENCODING_ISO8859_15)
    elif id_ == SBX_ENC['MAC'][0]:
        print('# Western (Mac Roman)')
    elif id_ == SBX_ENC['DOS'][0]:
        print('# DOS (CP 437)')
    elif id_ == SBX_ENC['CW0'][0]:
        print('# Central European (Windows 1250)')
    elif id_ == SBX_ENC['CI2'][0]:
        print('# Central European (ISO-8859-2)')
    elif id_ == SBX_ENC['HEX'][0]:
        print('# Hexadecimal')


################################################################################################


def CtxStatusBarEOL(evt):
    # 'Mixed EOLs': display-only, no further processing
    if evt.Id == SBX_EOL['EMX'][0]:
        return

    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    if DEBUG['SBR']: print(f'\n  label  = [{lbl}]')

    # update statusbar (end of line) context menu item check marks
    for key in SBX_EOL:
        itm = SBX_EOL[key]
        itm[1] = bool(id_ == itm[0])

#FIX, implement handlers
    if id_ == SBX_EOL['ECL'][0]:
        print('# Windows (CRLF)')
        tlw.convert_eol(evt)
    elif id_ == SBX_EOL['ELF'][0]:
        print('# Unix (LF)')
        tlw.convert_eol(evt)
    elif id_ == SBX_EOL['ECR'][0]:
        print('# Mac (CR)')
        tlw.convert_eol(evt)


################################################################################################


def CtxStatusBarIND(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    if DEBUG['SBR']: print(f'\n  label  = [{lbl}]')

#FIX, implement handlers
    if id_ == MI['IND_GSB']:
        print('# guess settings from buffer')
        return
    elif id_ == MI['IND_ITS']:
        print('# convert indentation to spaces')
        doc.convert_indentation(doc.TabWidth, False)
        return
    elif id_ == MI['IND_ITT']:
        print('# convert indentation to tabs')
        doc.convert_indentation(doc.TabWidth, True)
        return

    mb = glb.MB

    # update statusbar (indentation) context menu item check marks
    if id_ == MI['IND_IUS']:
        mb.Check(id_, evt.IsChecked())
        doc.SetUseTabs(bool(not mb.IsChecked(id_)))
        doc.SetTabIndents(True)
        doc.SetBackSpaceUnIndents(True)
    else:
        for wid in range(1, 9):
            if id_ ==  MI[f'IND_TW{wid}']:
                mb.Check(id_, evt.IsChecked())
                doc.SetTabWidth(wid)
                doc.SetIndent(wid)  # glb.CFG['Indentation']['Size']
                doc.SetHighlightGuide(wid)


################################################################################################


def CtxBookmarkList(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    if DEBUG['BMK']: print(f'  label = [{lbl}]')

    # explicit method call w/ proper event attributes
    evt.Index = (ctl := doc.spt_lst[SPT.BMK.idx]).FocusedItem
    if id_ == BMX['DEL']:
        evt.KeyCode = wx.WXK_DELETE
        ctl.delete_item(evt)
    else:
        ctl.activate_item(evt)


################################################################################################


def CtxSymbolDef(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    ctl = doc.spt_lst[SPT.SDF.idx]

    if id_ == SDX['EXP']:
        ctl.ExpandAll()
        if DEBUG['GEN']: print('Expanding...')
    else:
        ctl.CollapseAll()
        if DEBUG['GEN']: print('Collapsing...')


################################################################################################


def CtxTaskList(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    if DEBUG['TSK']: print(f'  label = [{lbl}]')

    # explicit method call w/ proper event attributes
    evt.Index = (ctl := doc.spt_lst[SPT.TSK.idx]).FocusedItem
    if id_ == TSX['DEL']:
        evt.KeyCode = wx.WXK_DELETE
        print(evt.Index, evt.KeyCode)
        ctl.delete_item(evt)
    else:
        ctl.activate_item(evt)


################################################################################################


def CtxBreakpointList(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    if DEBUG['BPT']: print(f'  label = [{lbl}]')

    # explicit method call w/ proper event attributes
    evt.Index = (ctl := doc.spt_lst[SPT.BPT.idx]).FocusedItem
    if id_ == BPX['DEL']:
        evt.KeyCode = wx.WXK_DELETE
        ctl.delete_item(evt)
    elif id_ == BPX['GTO']:
        ctl.activate_item(evt)
    else:
        evt.KeyCode = wx.WXK_INSERT
        ctl.enable_item(evt)


################################################################################################


def CtxDocMap(evt):
    if not (doc := get_doc()): return
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    if DEBUG['DCM']: print(f'  label = [{lbl}]')

    # update doc map context menu item check marks
    for key in DMX:
        if id_ == DMX[key][0]:
            DMX[key][1] = not DMX[key][1]

    # update them in config, too
    cfg['DocMap']['ZoneRectRounded'] = DMX['ZRC_RND'][1]
    cfg['DocMap']['ZoneCentreLine'] = DMX['ZCT_LIN'][1]
    cfg['DocMap']['ZoneCentreDot'] = DMX['ZCT_DOT'][1]
    cfg['DocMap']['EdgeTextIndicator'] = DMX['EDG_TXT'][1]
    cfg['DocMap']['AutoFocus'] = DMX['AUT_FCS'][1]
    cfg['DocMap']['MarkerLineHighlight'] = DMX['MRK_LHL'][1]
    cfg['DocMap']['SnapCursorAtDragStart'] = DMX['SNP_CDS'][1]
    cfg['CodePreview']['Enable'] = DMX['COD_PVW'][1]
    cfg['CodePreview']['Caption'] = DMX['COD_CAP'][1]
    cfg['CodePreview']['Border'] = DMX['COD_BRD'][1]
    cfg['CodePreview']['Margin'] = DMX['COD_MGN'][1]

#TODO, create method for 'update doc map panel/control'
    # update doc map control/code preview
    if (ctl := doc.spt_lst[SPT.DCM.idx]):
        ctl.Refresh()  # force 'doc map' update
        ctl.SetMarginWidth(MGN['SYM'], 0 if cfg['DocMap']['MarkerLineHighlight'] else 1)
        if ctl.cod_pvw:
            # ctl.cod_pvw.ToggleMargin()
            stc, mgn = ctl.cod_pvw.stc_pvw, cfg['CodePreview']['Margin']
            stc.SetMarginWidth(MGN['NUM'], cfg['Margin']['LineNumberWidth'] if mgn else 0)
            stc.SetMarginWidth(MGN['SYM'], cfg['Margin']['SymbolWidth'] if mgn else 0)


################################################################################################


def CtxWhere(evt):
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    if DEBUG['SCH']: print(f'  CtxWhere\n    [{lbl}]')

    sch = glb.SCH

    # get 'where filter' text
    whr_txt = ''
    if id_ == MI['WHR_CLE']:
        sch.txc_whr.Value = ''
    elif id_ == MI['WHR_FFF']:
        print('  Read Filters from File: [filters.fif] (not implemented)')
        not_implemented(None, 'Read Filters from File: [filters.fif]')
    elif id_ == MI['WHR_FDR']:
        sty = wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST  # | wx.DD_CHANGE_DIR
        with wx.DirDialog(sch, lbl, cwd(), sty) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                whr_txt = dlg.Path
    elif id_ == MI['WHR_IFE']:
        whr_txt = '*.ext'
    elif id_ == MI['WHR_IFP']:
        whr_txt = r'*\path\*'
    elif id_ == MI['WHR_EFE']:
        whr_txt = '-*.ext'
    elif id_ == MI['WHR_EFP']:
        whr_txt = r'-*\path\*'
    elif id_ == MI['WHR_OFD']:
        whr_txt = '<open folders>'
    elif id_ == MI['WHR_OFL']:
        whr_txt = '<open files>'
    elif id_ == MI['WHR_CFL']:
        whr_txt = '<current file>'
    elif id_ == MI['WHR_PVW']:
        whr_txt = '<preview>'
    # else:
    #     pass
    if whr_txt:
        sch.txc_whr.Value += f',{whr_txt}' if sch.txc_whr.Value else whr_txt


################################################################################################


def CtxSearchHistory(evt):
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    obj = evt.EventObject
    # which search panel object invoked this handler
    fld = obj.InvokingWindow  # field: Find|Replace|Where
    val = lbl[lbl.index('  ') + 2:]  # strip 'number/spaces' prefix

    print(f'  CtxSearchHistory\n    [{lbl}]  [{fld.Name}] := [{val}]')

    # set field to selected menu item label
    fld.Value = lbl


################################################################################################


def CtxMenuBar(evt):
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    print(f'  CtxMenuBar\n    [{lbl}]')
    pass

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    tlw.toggle_menubar(evt)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@


################################################################################################


def CtxInfoBar(evt):
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    print(f'  CtxInfoBar\n    [{lbl}]')
    pass

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # tlw.toggle_infobar(evt)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@


################################################################################################


def CtxSearchResults(evt):
    tlw, cfg, id_, lbl = _ctx_set_common_vars(evt)

    print(f'  CtxSearchResults\n    [{lbl}]')

    pass


################################################################################################


# set common vars for context menu handlers above
def _ctx_set_common_vars(evt):
    tlw = glb.TLW
    cfg = glb.CFG
    id_ = evt.Id
    lbl = evt.EventObject.GetLabel(id_)
    return tlw, cfg, id_, lbl
