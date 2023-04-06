#!/usr/bin/python

# >>>>>>>>>>>>>>>> THIRD PARTY imports <<<<<<<<<<
from pubsub import pub
import wx
import wx.lib.colourdb

# >>>>>>>>>>>>>>>> LOCAL imports <<<<<<<<<<<<<<<<
from const import glb
from common.doc import get_doc
from common.file import open_files
from common.util import create_symbol_index, me_, not_implemented
from conf.config import cnuf
from conf.debug import DEBUG, dbg_EVENT, dbg_method_calls, dbg_whoami
import actions as act
import gui
import mix


#INFO, URL=http://pythonhosted.org/Autologging/examples.html
# @traced
# @logged

# @dbg_method_calls(
#     exclude=['updateui_doc', 'updateui_sch', 'updateui_hlp', 'updateui_his',
#              'updateui_mac', 'updateui_mod', 'updateui_sel', 'do_brace_match']
# )
class AppFrame(wx.Frame, mix.Help, act.Test____,
                    act.File, act.Edit, act.Select, act.Search, act.View,
                    act.Goto, act.Run, act.Language, act.Project, act.Format,
                    act.Macro, act.Layout, act.Help, act.UpdateUI):

    __slots__ = ['mb', 'ctx', 'tb', 'sb', 'ccx', 'rlr', 'nbk', 'sch', 'spn']

    def __init__(self, *args, **kwargs):
        if DEBUG['STK']: print(dbg_whoami())
        super().__init__(*args, name='AppFrame', **kwargs)

        glb.TLW = self

        self.SetExtraStyle(wx.WS_EX_PROCESS_UI_UPDATES)

#FIX, handle ESCAPE centrally; app level? -> see 'global_char_hook'
        self.sch_esc_active = False  # ESCAPE pressed in 'SearchPanel'
        self.sch_res_active = False  # search results in 'SearchPanel'
        self.xit_active = False      # discard some file_close actions when called from 'file_exit'
        self.multi_clp_lst = None    # multiple selection clipboard
        self.debugger = None         # Python debugger object
        self.fil_num = 0             # filenum for new file creation

        create_symbol_index(self, me_("C"))

        self.create_gui()

        self.binds()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, for TESTING
        # dlg = self.show_menu_editor(None)

        from const.common import LOREM_IPSUM
        txt = LOREM_IPSUM.replace('\n', ' ')
        glb.IB.info_msg(txt, wx.ICON_INFORMATION, autohide=False)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        pub.subscribe(self.update_keyword_sets_menu, 'pag_chg_kws')

    def binds(self):
        # self.Bind(wx.EVT_IDLE, self.idle)
        self.Bind(wx.EVT_SIZE, self.resize)
        self.Bind(wx.EVT_CLOSE, self.file_exit)
        self.Bind(wx.EVT_DROP_FILES, self.drop_files)
        self.Bind(wx.EVT_MAXIMIZE, self.maximize)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'MBR'))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: use 'updateui_main' for current application context
        # self.Bind(wx.EVT_UPDATE_UI, self.updateui_main)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.Bind(wx.EVT_HELP, self.Help)



    #     self.Bind(wx.EVT_MENU_HIGHLIGHT, self.mselect)
    #     self.Bind(wx.EVT_MENU_OPEN, self.mopen)

    # def mselect(self, evt):
    #     if (itm := glb.MB.FindItemById(evt.MenuId)) is not None:
    #         print('select', itm.GetItemLabelText() if evt.MenuId != -3 else 'separator')

    # def mopen(self, evt):
    #     ttl = evt.Menu.Title.replace('&', '')
    #     print('open', ttl if ttl else 'submenu')



    def create_gui(self):
        # >>>> SPLITTERS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        glb.SPL['SCH'] = spl_sch = gui.Splitter(self,    'SCH', True,  1.0)  # horizontal (spn/SearchPanel)
        glb.SPL['SPN'] = spl_spn = gui.Splitter(spl_sch, 'SPN', False, 1.0)  # vertical (ccx/SidePanel)
        glb.SPL['CCX'] = spl_ccx = gui.Splitter(spl_spn, 'CCX', True,  0.0)  # horizontal (CodeContext/rlr)
        glb.SPL['RLR'] = spl_rlr = gui.Splitter(spl_ccx, 'RLR', True,  0.0)  # mid horizontal (Ruler/Notebook)

        # >>>> BARS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # includes: main, recent file history and system tray menus
        glb.MB = self.mb = gui.MenuBar(self)

        self.ctx = self.mb.ctx  # context menu definitions
        if glb.CFG['Layout']['MenuBar']:
            self.SetMenuBar(self.mb)

        glb.TB = tb = gui.ToolBar(self)
        self.SetToolBar(tb)

        glb.IB = gui.InfoBar(self)

        glb.SB = self.sb = gui.StatusBar(self)
        self.SetStatusBar(self.sb)

        # >>>> WINDOWS <<<<<<<<<<<<<<<<<<<<<<<<<
        glb.NBK = nbk = gui.Notebook(spl_rlr)
        glb.RLR = rlr = gui.Ruler(spl_rlr)
        glb.CCX = ccx = gui.CodeContext(spl_ccx)
        glb.SPN = spn = gui.SidePanel(spl_spn)
        glb.SCH = sch = gui.SearchPanel(spl_sch)

        # assign windows to splitters
        spl_rlr.set_windows(rlr,     nbk)
        spl_ccx.set_windows(ccx,     spl_rlr)
        spl_spn.set_windows(spl_ccx, spn)
        spl_sch.set_windows(spl_spn, sch)

#HACK: split/unsplit immediately...
        for spl in (spl_sch, spl_spn, spl_ccx, spl_rlr):
            spl.split_windows()
            spl.unsplit_windows()

    def drop_files(self, evt):
        if DEBUG['GEN']: print(' ', evt.Files)
        if DEBUG['GEN']: print(' ', evt.NumberOfFiles)

        print('drop_files', evt.NumberOfFiles, evt.Files)

        fil_lst = [[fnm] for fnm in evt.Files]
        open_files(fil_lst)

    # @cur_doc
    # def idle(self, doc, evt):
    def idle(self, evt):
#NOTE, for statusbar delay timer tests
        # for t in ['MSG', 'AUX']:
        #     print(glb.SB.tmr_cfd[t].IsRunning())

        if not (doc := get_doc()): return
        if DEBUG['IDL']: print(f'{me_()}')
        if DEBUG['IDL'] > 1: dbg_EVENT(evt)
        if DEBUG['IDL']: print(f'[{doc.fnm}] - [{doc.dnm}]')

#FIX, direct call from 'Bind(wx.EVT_MAXIMIZE, ...') does NOT force default sash position
    def maximize(self, evt):
        self.reset_side_panel(evt)

    def resize(self, evt):
        evt.Skip()
        if DEBUG['GEN'] > 1: print(f'{me_()}')
        if DEBUG['GEN'] > 1: dbg_EVENT(evt)

        self.Refresh()

    def split_editor(self, evt):
        if not (doc := get_doc()): return
        not_implemented(None, 'SPLIT EDITOR')


cnuf()
