#!/usr/bin/python

import wx

from ._load import _load
from common.doc import get_doc
from common.util import is_shown
from conf.debug import dbg_FOCUS
from const.common import SASH_POS
from const import glb
from const.menu import MI


@_load
class Search:

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    def search_find_current(self, evt):
        if not (doc := get_doc()): return

        prv = _all = False
        if (id_ := evt.Id) == MI['SCH_CUP']:
            prv = True
        elif id_ == MI['SCH_CUA']:
            _all = True

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # if not _all:
        #     cnt, spos, epos = doc.Selections, *doc.GetSelection()
        #     if cnt > 1 or spos != epos:
        #         print('Before____', doc.CurrentPos)
        #         doc.SelectNone()
        #         print('SelectNone', doc.CurrentPos)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        fnd, flg = doc.SelectedText, glb.SCH.get_flags()

        if not fnd:
            print(f'{doc.cur_sel_wrd=}')
            doc.select_next_word()
            print(f'{doc.cur_sel_wrd=}')
            fnd = doc.cur_sel_wrd
            if _all:
                glb.SCH.do_find_all(doc, fnd, flg)
        else:
            #@@@@@@@@@@@@@@@@@@@@@@@@@
            # # clear selections
            # pos = doc.CurrentPos
            # doc.SelectNone()
            # doc.SetSelection(pos, pos)
            #@@@@@@@@@@@@@@@@@@@@@@@@@
            if _all:
                glb.SCH.do_find_all(doc, fnd, flg)
            else:
                glb.SCH.do_find(None, doc, fnd, flg, prv=prv)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def search_find_next(self, evt):
        if not (doc := get_doc()): return
        fnd, flg = glb.SCH.txc_fnd.Value, glb.SCH.get_flags()
        glb.SCH.do_find(None, doc, fnd, flg)

    def search_find_previous(self, evt):
        if not (doc := get_doc()): return
        fnd, flg = glb.SCH.txc_fnd.Value, glb.SCH.get_flags()
        glb.SCH.do_find(None, doc, fnd, flg, prv=True)

    def set_search_mode(self, evt, mode=None):
        if (id_ := evt.Id) == MI['SCH_FND']:
            mode = 'FND'
        elif id_ == MI['SCH_RPL']:
            mode = 'RPL'
        elif id_ == MI['SCH_FIF']:
            mode = 'FIF'
        elif id_ == MI['SCH_INC']:
            mode = 'INC'
        elif id_ == MI['SCH_RES']:
            mode = 'RES'

        # mode already current and focused
        if mode == glb.SCH.mode and glb.SCH.txc_fnd.HasFocus():
        # if mode == glb.SCH.mode and glb.SCH.txc_fnd.HasFocus() or \
        #     mode == glb.SCH.mode and glb.SCH.txc_inc.HasFocus():
            return

        self.Freeze()
        glb.NBK.Freeze()

#FIX, 'SearchPanel' help icon (bottom left corner) slightly shifts vertically in 'FIF' mode and IconSize' in [16, 32]
#FIX, for now, optimized for 'IconSize' == 24
        # if mode == 'FIF':
        #     sec = CFG['SearchPanel']
        #     pos = 179 if sec['IconSize'] == 16 else 155 if sec['IconSize'] == 32 else 167

        if not is_shown('SCH'):
            self.toggle_panel(None, 'SCH', -1)

        pos = SASH_POS['SCH'][mode]
        glb.SPL['SCH'].SetSashPosition(pos if glb.SPL['SCH'].swap else -pos)
#FIX, redundant? -> to be called 3 lines from here...
        glb.SCH.set_mode(mode)

        self.Thaw()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#         # glb.SCH.HideWithEffect(wx.SHOW_EFFECT_ROLL_TO_BOTTOM, 0)
#         glb.SCH.Hide()
# #FIX, redundant? -> just called this 3 lines back...
#         glb.SCH.set_mode(mode)
#         # glb.SPL['SCH'].Show()
#         sec = CFG['PanelEffect']
#         glb.SCH.ShowWithEffect(sec['Choice'] if glb.SPL['SCH'].swap else sec['Choice'], sec['Duration'])
#         # glb.SCH.ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM if glb.SPL['SCH'].swap else wx.SHOW_EFFECT_SLIDE_TO_TOP, 200)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        glb.NBK.Thaw()

        if mode == 'RES':
            wx.CallAfter(dbg_FOCUS, glb.SCH.stc_res)

###############################################################################################################
#FIX, 'slide into view' effect
###############################################################################################################
#         self.Freeze()              ; glb.SPL['SPN'].Freeze() ; glb.SPL['CCX'].Freeze() ; glb.SPL['RLR'].Freeze()
#         glb.NBK.Freeze()           ; glb.SCH.Freeze()   ; glb.SPL['SCH'].Freeze() ; glb.NBK.CurrentPage.Freeze()
#
#         if not is_shown('SCH'):
#             self.toggle_panel(None, 'SCH', -1)
#
#         glb.SPL['SCH'].SetSashPosition(0)
#         pos = SASH_POS['SCH'][mode]
#         glb.SCH.set_mode(mode)
#
#         glb.NBK.CurrentPage.Thaw() ; glb.SPL['SCH'].Thaw()   ; glb.SCH.Thaw()     ; glb.NBK.Thaw()
#         glb.SPL['RLR'].Thaw()          ; glb.SPL['CCX'].Thaw()   ; glb.SPL['SPN'].Thaw()   ; self.Thaw()
#
#         for s in range(pos + 1):
#             print(pos)
#             glb.SPL['SCH'].SetSashPosition(s if glb.SPL['SCH'].swap else -s)
###############################################################################################################

    def set_search_mode_find(self, evt):
        self.set_search_mode(evt, mode='FND')

    def set_search_mode_replace(self, evt):
        self.set_search_mode(evt, mode='RPL')

    def toggle_search_option(self, evt):
        id_ = evt.Id

        mb, sch = glb.MB, glb.SCH

        # which search option
        SCH_OPT = {
            MI['SCH_CAS']: ('cas', sch.cbx_cas,),
            MI['SCH_REG']: ('reg', sch.cbx_reg,),
            MI['SCH_WRD']: ('wrd', sch.cbx_wrd,),
            MI['SCH_WRP']: ('wrp', sch.cbx_wrp,),
            MI['SCH_ISL']: ('isl', sch.cbx_isl,),
            MI['SCH_HLM']: ('hlm', sch.cbx_hlm,),
            MI['SCH_PCS']: ('pcs', sch.cbx_pcs,),
            MI['SCH_CXT']: ('cxt', sch.cbx_cxt,),
            MI['SCH_BUF']: ('buf', sch.cbx_buf,),
        }

        fld, cbx = SCH_OPT[id_]

        # sync corresponding menu item, checkbox and icon
        mb.Check(id_, evt.IsChecked())
        cbx.SetValue(mb.IsChecked(id_))
        sch.toggle_icon(fld)
