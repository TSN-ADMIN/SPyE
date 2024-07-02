#!/usr/bin/python

# >>>>>>>>>>>>>>>> THIRD PARTY imports <<<<<<<<<<
import wx
import wx.lib.colourdb

# >>>>>>>>>>>>>>>> LOCAL imports <<<<<<<<<<<<<<<<
from const import glb
from common.file import open_files
from common.util import create_symbol_index, curdoc, not_implemented
from conf.config import cnuf
from conf.debug import DBG, DEBUG, dbf, me_
from const.common import LOREM_IPSUM
import actions as act
import gui
import mix


# from extern.ide2py_POC.debugger import DebuggerProxy, EVT_DEBUG_ID, EVT_EXCEPTION_ID, \
#                      EnvironmentPanel, StackListCtrl, SessionListCtrl


#INFO, URL=http://pythonhosted.org/Autologging/examples.html
# @traced
# @logged

# @dbf.method_calls(
#     exclude=['updateui_doc', 'updateui_sch', 'updateui_hlp', 'updateui_his',
#              'updateui_mac', 'updateui_mod', 'updateui_sel', 'do_brace_match']
# )
class AppFrame(wx.Frame, mix.Help, act.Test____,
                    act.File, act.Edit, act.Select, act.Search, act.View,
                    act.Goto, act.Run, act.Language, act.Project, act.Format,
                    act.Macro, act.Layout, act.Help, act.UpdateUI):

    __slots__ = ['mbr', 'ctx', 'tbr', 'sbr', 'ccx', 'rlr', 'nbk', 'sch', 'spn']

    def __init__(self, *args, **kwargs):
        DBG('STK', dbf.whoami)
        super().__init__(*args, name='AppFrame', **kwargs)
        mix.Help.__init__(self)

        glb.TLW = self

        self.SetExtraStyle(wx.WS_EX_PROCESS_UI_UPDATES)

#FIX, handle ESCAPE centrally; app level? -> see 'global_char_hook'
        self.sch_esc_active = False  # ESCAPE pressed in 'SearchPanel'
        self.sch_res_active = False  # search results in 'SearchPanel'
        self.xit_active = False      # discard some 'file_close' actions when NOT exiting
        self.multi_clp_lst = None    # multiple selection clipboard
        self.debugger = None         # Python debugger object
        self.fil_num = 0             # filenum for new file creation

        self.create_gui()

        self.binds()

        self.subscriptions()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, for TESTING
        # dlg = self.show_menu_editor(None)

        txt = LOREM_IPSUM.replace('\n', ' ')
        wx.CallAfter(glb.IBR.info_msg, txt, 'INFO')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def binds(self):
        self.Bind(wx.EVT_IDLE, self.idle)
        self.Bind(wx.EVT_SIZE, self.resize)
        self.Bind(wx.EVT_CLOSE, self.file_exit)
        self.Bind(wx.EVT_DROP_FILES, self.drop_files)
        self.Bind(wx.EVT_MAXIMIZE, self.maximize)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'MBR'))

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: use 'updateui_main' for current application context
        # self.Bind(wx.EVT_UPDATE_UI, self.updateui_main)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



    #     self.Bind(wx.EVT_MENU_HIGHLIGHT, self.mselect)
    #     self.Bind(wx.EVT_MENU_OPEN, self.mopen)

    # def mselect(self, evt):
    #     if (itm := glb.MBR.FindItemById(evt.MenuId)) is not None:
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

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # dbf.TIMER('menubar')
        glb.MBR = self.mbr = gui.MenuBar(self)

        self.ctx = self.mbr.ctx  # context menu definitions
        if glb.CFG['Layout']['MenuBar']:
            self.SetMenuBar(self.mbr)
        # dbf.TIMER('menubar', 'STOP')

        # dbf.TIMER('toolbar')
        glb.TBR = tbr = gui.ToolBar(self)
        self.SetToolBar(tbr)
        # dbf.TIMER('toolbar', 'STOP')

        # dbf.TIMER('infobar')
        glb.IBR = gui.InfoBar(self)
        # dbf.TIMER('infobar', 'STOP')

        # dbf.TIMER('statusbar')
        glb.SBR = self.sbr = gui.StatusBar(self)
        self.SetStatusBar(self.sbr)
        # dbf.TIMER('statusbar', 'STOP')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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

#HACK, split/unsplit immediately...
        for spl in (spl_sch, spl_spn, spl_ccx, spl_rlr):
            spl.split_windows()
            spl.unsplit_windows()

    def drop_files(self, evt):
        DBG('GEN', ' ', evt.Files)
        DBG('GEN', ' ', evt.NumberOfFiles)

        print('drop_files', evt.NumberOfFiles, evt.Files)

        fil_lst = [[fnm] for fnm in evt.Files]
        open_files(fil_lst)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, move 'idle' to 'class Application'
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @curdoc
    # def idle(self, doc, evt):
    def idle(self, evt):
#NOTE, for statusbar delay timer tests
        # for t in {'MSG', 'AUX'}:
        #     print(glb.SBR.tmr_cfd[t].IsRunning())

        print(f'{me_()}')
        DBG('IDL>1', (dbf.EVENT, evt))
        DBG('IDL', f'[{doc.fnm}] - [{doc.dnm}]')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, direct call from 'Bind(wx.EVT_MAXIMIZE, ...') does NOT force default sash position
    def maximize(self, evt):
        self.reset_side_panel(evt)

    def resize(self, evt):
        evt.Skip()
        DBG('GEN>1', f'{me_()}')
        DBG('GEN>1', (dbf.EVENT, evt))

        self.Refresh()

    @curdoc
    def split_editor(self, evt):
        not_implemented(None, 'SPLIT EDITOR')
        # spl = doc.Parent
        # spl.Unsplit(spl.Parent.txt2) if spl.IsSplit() else spl.split_windows()
        # glb.NBK.update_page_tab(doc, newtab=False, spl=spl)

    def subscriptions(self):
        glb.SUB(self.update_keyword_sets_menu, 'pub_kws')
        # glb.SUB(glb.SPN.page_changed, 'pub_spn')


cnuf()
