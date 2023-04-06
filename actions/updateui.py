#!/usr/bin/python

from ._load import _load
from common.doc import get_doc
from common.util import is_shown, me_
from conf.debug import DEBUG, dbg_EVENT
from const import glb
from const.menu import MI
from const.toolbar import TB
import gui


#@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE:
CNT_updateui_main = 0
#@@@@@@@@@@@@@@@@@@@@@@@@


@_load
class UpdateUI:


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: remove/create menus for current application context
#INFO, most top menus are useless in 'non-doc mode', e.g. 'KeywordSets'
    def updateui_main(self, evt):
        global CNT_updateui_main

        mb, nbk, doc = glb.MB, glb.NBK, glb.DOC

        if nbk.PageCount:
            print(f'{me_("C, F")}, [{doc.fnm if doc else doc }], {nbk.PageCount}')

        if not nbk.PageCount and doc is not None:
            print(f'{CNT_updateui_main:4d} No open documents')
            CNT_updateui_main += 1
            glb.DOC = None

#TODO, hide full menus when NO document open
            # for m in range(mb.GetMenuCount()):
            #     mb.EnableTop(m, False if m not in (0, 13) else True)

#TODO, hide toolbar when NO document open
            # glb.TB.Show(False)
            # self.SendSizeEvent()

#FIX, update menu ONLY ONCE on 1st opened document
        # else:
        #     for m in range(mb.GetMenuCount()):
        #         mb.EnableTop(m, True if m not in (0, 13) else False)




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#NOTE, EXPERIMENTAL CODE: EVT_UPDATE_UI counters
    # CNT_UPDUI = {
    #     'DOC': 0,
    #     'HLP': 0,
    #     'HIS': 0,
    #     'MAC': 0,
    #     'MOD': 0,
    #     'SEL': 0,
    #     'SCH': 0,
    # }

    def updateui_doc(self, evt):
#NOTE, EXPERIMENTAL CODE: EVT_UPDATE_UI counters
        # self.CNT_UPDUI['DOC'] += 1
        # if DEBUG['UPD']: print(f'{me_()}{self.CNT_UPDUI["DOC"]:>6}')

        # glb.MB.Check(MI['LAY_MHT'], bool(glb.CFG['Layout']['MenuHelpText']))
        # print(glb.CFG['Layout']['MenuHelpText'], bool(glb.CFG['Layout']['MenuHelpText']))

        if DEBUG['UPD']: print(f'{me_()}')
        if DEBUG['UPD'] > 1: dbg_EVENT(evt)

#TODO, hide full menus when NO document open
        # for m in range(12):
        #     glb.MB.EnableTop(m, False if m not in (0, 5, 9, 10, 11) and not glb.NBK.PageCount else True)

        # always disable 'mixed EOLs'
        glb.MB.Enable(MI['FMT_EMX'], False)

        # when document open
        if glb.NBK.PageCount:
            if not (doc := get_doc()): return

            # file operations
            for id_ in ('FIL_REN', 'FIL_INS', 'FIL_APD', 'FIL_CLS', 'FIL_CLA', 'FIL_CAE'):
                glb.MB.Enable(MI[id_], True)

            # save as, change to file directory (not for new/unsaved file)
            for id_ in ('FIL_SAS', 'FIL_CFD'):
                glb.MB.Enable(MI[id_], bool(doc.dnm))

            # caret position history
            for id_ in ('JMP_BCK', 'JMP_FWD'):
                glb.MB.Enable(MI[id_], bool(glb.CFG['CaretPositionHistory']['Enable']))

            # debugger breakpoints
            # for id_ in ('BPT_ENA', 'BPT_NXT', 'BPT_PRV'):
            #     glb.MB.Enable(MI[id_], bool(doc.get_breakpoints()))

            # enable swap/reset when corresponding panel visible
            for id_, pnl in (('LAY_SCS', 'SCH'), ('LAY_RLS', 'RLR'), ('LAY_SPS', 'SPN'),
                             ('LAY_SPR', 'SPN'), ('LAY_CCS', 'CCX')):
                glb.MB.Enable(MI[id_], bool(is_shown(pnl)))
                glb.MB.Check(MI[f'LAY_{pnl}'], bool(is_shown(pnl)))

            # enable list filter when visible panel is a list
            if is_shown('SPN'):
                lst = not any(is_shown(p) for p in ('PRJ', 'FXP', 'SDF', 'DCM', 'MDN', 'CFW', 'SNP'))
                glb.MB.Enable(MI['SPT_FLT'], bool(lst))
                # enable delete list filter when filter text present
                if lst:
                    ctl = gui.get_spt()
                    glb.MB.Enable(MI['SPT_DLF'], bool(ctl.mnf_flt.txc_flt.Value))

            # panel effect menu available?
            # glb.MB.Enable(MI['PEF_MNU'], bool(glb.CFG['PanelEffect']['Enable']))

            # disable 'CustomCheckable' when 'MenuIcons' unchecked
            glb.MB.Enable(MI['LAY_MIK'], bool(glb.MB.IsChecked(MI['LAY_MIC'])))

            # disable 'PageTabTheme' and 'PageTabIcons' when 'PageTabs' unchecked
            glb.MB.Enable(MI['LAY_PTT'], bool(glb.MB.IsChecked(MI['LAY_PTB'])))
            glb.MB.Enable(MI['LAY_PTI'], bool(glb.MB.IsChecked(MI['LAY_PTB'])))

            # disable 'PageTabIcons' when 'PageTabTheme' unchecked
            glb.MB.Enable(MI['LAY_PTI'], bool(glb.MB.IsChecked(MI['LAY_PTT'])))

############################################################################
#FIX, message never shows, see 'edit_undo/edit_redo'
            glb.MB.Enable(MI['EDT_UDO'], bool(doc.CanUndo()))
            glb.MB.Enable(MI['EDT_RDO'], bool(doc.CanRedo()))

#DONE, enable/disable undo/redo buttons on toolbar, too
            glb.TB.EnableTool(TB['UDO'], bool(doc.CanUndo()))
            glb.TB.EnableTool(TB['RDO'], bool(doc.CanRedo()))

#FIX, enable/disable paste on menu, toolbar, context menu
#NOTE, it seems Windows and Scintilla have a SEPARATE clipboard!
            glb.MB.Enable(MI['EDT_CUT'], bool(doc.CanCut()))
            glb.MB.Enable(MI['EDT_CPY'], bool(doc.CanCopy()))
            glb.MB.Enable(MI['EDT_PST'], bool(doc.CanPaste()))
############################################################################
        else:
            evt.Enable(False)

    def updateui_hlp(self, evt):
        if DEBUG['UPD']: print(f'{me_()}')
        if DEBUG['UPD'] > 1: dbg_EVENT(evt)

        # help menu items enabled?
        glb.MB.Enable(MI['HLP_CTX'], bool(glb.CFG['Help']['ContextSensitiveMode']))
        glb.MB.Enable(MI['HLP_UPD'], bool(glb.CFG['Help']['CheckForUpdates']))
        glb.MB.Enable(MI['HLP_WIT'], bool(glb.CFG['WidgetInspectionTool']['Enable']))

    def updateui_his(self, evt):
        if DEBUG['UPD']: print(f'{me_()}')
        if DEBUG['UPD'] > 1: dbg_EVENT(evt)

        # recent file history items available?
        glb.MB.Enable(MI['SUB_RFH'], bool(glb.MB.rfh_cache.Count))

    def updateui_mac(self, evt):
        if DEBUG['UPD']: print(f'{me_()}')
        if DEBUG['UPD'] > 1: dbg_EVENT(evt)

        # when document open, macro recording?
        if glb.NBK.PageCount:
            if not (doc := get_doc()): return
            if doc.mac_rec_active:
                evt.Enable(bool(evt.Id in (MI['MAC_STP'], MI['MAC_TST'])))
            else:
                evt.Enable(bool(evt.Id != MI['MAC_STP']))
                if not doc.mac_lst and evt.Id in (MI['MAC_PLY'], MI['MAC_PLM']):
                    evt.Enable(False)
        else:
            evt.Enable(False)

    def updateui_mod(self, evt):
        if DEBUG['UPD']: print(f'{me_()}')
        if DEBUG['UPD'] > 1: dbg_EVENT(evt)

        # when document open, modified?
        if glb.NBK.PageCount:
            if not (doc := get_doc()): return
            evt.Enable(bool(doc.IsModified()))
        else:
            evt.Enable(False)

    def updateui_sel(self, evt):
        if DEBUG['UPD']: print(f'{me_()}')
        if DEBUG['UPD'] > 1: dbg_EVENT(evt)

        # when document open, text selected?
        if glb.NBK.PageCount:
            if not (doc := get_doc()): return
            cnt, spos, epos = doc.Selections, *doc.GetSelection()
            if cnt > 1 or spos != epos:
                evt.Enable(True)
            else:
                evt.Enable(False)
        else:
            evt.Enable(False)

    def updateui_sch(self, evt):
        if DEBUG['UPD']: print(f'{me_()}')
        if DEBUG['UPD'] > 1: dbg_EVENT(evt)

        # when document open
        if glb.NBK.PageCount:
            # selected search mode: allowed fields
            all_lst = ['CAS', 'REG', 'WRD', 'WRP', 'ISL', 'HLM', 'PCS', 'CXT', 'BUF']
            mod_lst = all_lst[:3]
            if glb.SCH.mode in ('FND', 'INC'):
                mod_lst.extend(all_lst[3:6])
            elif glb.SCH.mode == 'RPL':
                mod_lst.extend(all_lst[3:7])
            elif glb.SCH.mode == 'FIF':
                mod_lst.extend(all_lst[7:])

            for fld in all_lst:
                glb.MB.Enable(MI[f'SCH_{fld}'], bool(fld in mod_lst))

            # empty find string?
            _efs = bool(glb.SCH.txc_fnd.Value)
            for id_, _tb_id in (('SCH_NXT', 'NXT'), ('SCH_PRV', 'PRV')):
                glb.MB.Enable(MI[id_], _efs)
                glb.TB.EnableTool(TB[_tb_id], _efs)
        else:
            evt.Enable(False)
