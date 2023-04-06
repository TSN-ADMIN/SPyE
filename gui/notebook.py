#!/usr/bin/python


# from _DEV._WRK._R+D.dummy_tabart import DummyTabArt


from pprint import pprint

from pubsub import pub
import pylru
import wx
import wx.aui as aui
from wx import stc

from conf.debug import (
    DEBUG, dbg_EVENT, dbg_FOCUS, dbg_PTH_CACHE_INFO, dbg_method_calls
)
from common.date import tim_str
from common.doc import get_doc
from common.util import (
    ColourToolTip, drop_shadow, me_, msg_box, not_implemented, rs_,
    scale_bitmap, TopLineToolTip
)
from const.app import APP
from const.common import TXT_NIL, TABCTRL_ID
from const import glb
from const.sidepanel import SPT
from data.images import catalog as PNG
import gui
import mix
from tool.docmap import add_doc_view  # not used


# @dbg_method_calls(
#     exclude=['open_docs',            'set_pth_cache_size', 'page_tab_history_init',
#              'page_tab_history_update', 'on_paint',           'tabctrl_access',
#              '_getPagDoc']
# )
class Notebook(aui.AuiNotebook, mix.Help):
#     def __init__(self, prt, id, pos, size, style):

    __slots__ = ['CFG', 'sec', 'sec_pth', 'prt', 'tlw', 'bmp', 'tab_ctl',
                 'pag_creating', 'pag_created', 'pth_active', 'pth_cache',
                 'pth_nav_key', 'pth_nav_src', 'tlt']

    def __init__(self, prt):
        self.sec = glb.CFG['Notebook']
        self.sec_pth = glb.CFG['PageTabHistory']
        sty = 0
        sty += aui.AUI_NB_BOTTOM              if self.sec['TabPosition'] == 'BOTTOM' else aui.AUI_NB_TOP
        sty += aui.AUI_NB_TAB_SPLIT           if self.sec['TabDragSplit'] else 0
        sty += aui.AUI_NB_TAB_MOVE            if self.sec['TabDragMove'] else 0
        sty += aui.AUI_NB_CLOSE_BUTTON        if self.sec['TabCloseButton'] else 0
        sty += aui.AUI_NB_CLOSE_ON_ACTIVE_TAB if self.sec['TabCloseButtonOnActive'] else 0
        sty += aui.AUI_NB_CLOSE_ON_ALL_TABS   if self.sec['TabCloseButtonOnAll'] else 0
        sty += aui.AUI_NB_SCROLL_BUTTONS      if self.sec['TabScrollButtons'] else 0
        sty += aui.AUI_NB_WINDOWLIST_BUTTON   if self.sec['TabWindowListButton'] else 0
        sty += aui.AUI_NB_TAB_FIXED_WIDTH     if self.sec['TabFixedWidth'] else 0
        sty += aui.AUI_NB_MIDDLE_CLICK_CLOSE  if self.sec['TabMiddleClickIsClose'] else 0

        sty += aui.AUI_NB_TAB_EXTERNAL_MOVE

#FIX, sty is never 0, handle AUI_NB_DEFAULT_STYLE properly
        if not sty:
            sty = aui.AUI_NB_DEFAULT_STYLE
        sty += wx.BORDER_RAISED

        super().__init__(prt, style=sty)
        self.SetName('Notebook')
        self.prt = prt
        self.bmp = PNG['splash_wide_rgba'].Bitmap

#HACK: enable access to 'wx.aui.AuiTabCtrl' (tab control window)
        self.tab_ctl = None

        # flag to veto executing 'page_changing' when 'glancing'
        self.glc_active = False

        # flags to simulate non-existing 'PageCreat...' 'events'
        self.pag_creating = False
        self.pag_created = False

#INFO, using PyLRU, A least recently used (LRU) cache for Python
#INFO, URL=https://github.com/jlhutch/pylru
        # activity starts with navigation keypress, ends with Ctrl/Shift key release
        self.pth_active = False
        if self.sec_pth['Enable']:
#TODO, create 'Class PageTabHistory'
            # initial history cache size (adjusts dynamically)
            self.pth_cache = pylru.lrucache(self.sec_pth['CacheSize'])
            # navigation keypress: 'Ctrl+Tab', 'Ctrl+Shift+Tab', 'Ctrl+PageDown' or 'Ctrl+PageUp'
            self.pth_nav_key = TXT_NIL
            # source page tab (where navigation starts)
            self.pth_nav_src = -1

        self.set_theme(self.sec['ArtProviderTheme'])

#FIX, create page tab icons in size 16x16 pixels, maybe 24x24 could fit..
        siz = self.sec['PageTabIconSize']
        self.SetUniformBitmapSize((siz, siz))

        # top line tooltip, shows when scrolling document w/ scrollbar
        self.tlt = TopLineToolTip(self)
        self.ctt = ColourToolTip(self)

        self.binds()


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, use '__getitem__' as page iterator
#INFO, URL=https://stackoverflow.com/questions/8580656/python-wxpython-auinotebook-get-all-pages
    def __getitem__(self, idx):
        ''' More pythonic way to get a specific page, also useful for iterating
            over all pages, e.g: for page in notebook: ... '''
        if idx < self.PageCount:
            return self.GetPage(idx)
        else:
            raise IndexError

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, EXAMPLE
    # print(self, self.PageCount)
    # for page in self:
    #     print('using __getitem__ ->', page)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    def binds(self):
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.page_changing)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.page_changed)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.page_close)
        self.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_DOWN, lambda e: gui.ContextMenu(e, 'NBK'))
        self.Bind(aui.EVT_AUINOTEBOOK_BEGIN_DRAG, self.page_begin_drag)
        self.Bind(aui.EVT_AUINOTEBOOK_END_DRAG, self.page_end_drag)

#TODO, this might bind to 'file_new'...
        # self.Bind(aui.EVT_AUINOTEBOOK_BG_DCLICK, glb.TLW.file_new)
        self.Bind(aui.EVT_AUINOTEBOOK_BG_DCLICK, self.notebook_info)

        # for page tab history
        self.Bind(wx.EVT_NAVIGATION_KEY, self.page_tab_history_init if self.sec_pth['Enable'] else None)
        self.Bind(wx.EVT_LEFT_DOWN, self.page_changed, source=wx.NewIdRef())

        self.Bind(wx.EVT_SIZE, self.tabctrl_access)

        bgd_img = self.on_paint if self.sec['BackgroundImage'] else None
        self.Bind(wx.EVT_IDLE, bgd_img)
        self.Bind(wx.EVT_SIZE, bgd_img)

        self.Bind(wx.EVT_HELP, self.Help)


    def on_paint(self, evt):
        # open documents?
        if self.PageCount:
            return

        cw, ch = self.ClientSize

        # client size too small
        if cw <= 0 or ch <= 0:
            return

        bw, bh = self.bmp.Size

        # adjust bitmap to client size
        if not (bw <= cw and bh <= ch):
            if cw < ch:
                bw = bh = cw
            else:
                bw = bh = ch

        bmp = scale_bitmap(self.bmp, bw, bh)

        self.Update()  # keep image visible when sizing main window

        # centre in client
        dc = wx.ClientDC(self)
        dc.DrawBitmap(bmp, (cw - bw) // 2, (ch - bh) // 2, True)


    def set_theme(self, theme='DEFAULT'):
        # self.SetArtProvider(DummyTabArt() if theme == 'DEFAULT' else aui.AuiSimpleTabArt())
        self.SetArtProvider(aui.AuiDefaultTabArt() if theme == 'DEFAULT' else aui.AuiSimpleTabArt())
        self.SetBackgroundColour(self.sec['BackColour'])
        self.SetForegroundColour(self.sec['ForeColour'])
        self.ArtProvider.SetColour(self.sec['TabColour'])
        self.ArtProvider.SetActiveColour(self.sec['TabActiveColour'])

        # force update only when page tabs visible
        if self.TabCtrlHeight:
            self.SetTabCtrlHeight(0)
            self.SetTabCtrlHeight(-1)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: P a g e   T a b   H i s t o r y - BEGIN
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # next page index key: nxt=1 (default); previous page index key: nxt=-1
    def get_pth_cache_key(self, key, nxt=1):
        key_lst = list(self.pth_cache)
        return key_lst[(key_lst.index(key) + nxt) % len(key_lst)]


    # set current page tab as MRU item (head) of LRU cache
    def set_pth_cache_head(self, evt, src):
        if self.pth_cache:
#NOTE, obsolete code? ==>> NO!!
            # lookup: move current LRU cache key/value to MRU position (head)
            __ = self.pth_cache[self.Selection]
#FIX, PTH levels, 'set head':(1) and add 1 to existing levels: (1->2, 2->3)
            if DEBUG['PTH']:
                print('\n')
                print(f'  {evt.Id}, {evt.EventType}, {evt.EventObject}')
                print(f'  {me_("F")}: {self.Selection}, {src}')
                for itm in self.pth_cache.items(): print('   ', itm)
                print('Page' in self.pth_nav_key, rs_(36, '*'))


    # adjust history cache size
    def set_pth_cache_size(self):
        siz = self.pth_cache.size()
        cnt = len(self.pth_cache)

        dbg_PTH_CACHE_INFO(self)

        if siz < self.PageCount:
            self.pth_cache.addTailNode(self.sec_pth['CacheSizeIncrease'])
        elif siz - cnt > self.sec_pth['CacheSizeDecrease']:
            self.pth_cache.removeTailNode(self.sec_pth['CacheSizeDecrease'])

        dbg_PTH_CACHE_INFO(self)


    def current_page(self, _fwd):
        pag = self.Selection + (1 if _fwd else -1)
        pag = 0 if (pag > self.PageCount - 1) else self.PageCount - 1 if (pag < 0) else pag
        return pag


#FIX, move 'page_tab_history_build' (restore) to end of 'apply()' in 'config.py'...?
    def page_tab_history_build(self, evt):
        if DEBUG['PTH']: print(f'{me_()}')
        if DEBUG['PTH'] > 1: print('\n## STAGE 0: Build cache (1st time only)')
        if DEBUG['PTH'] > 1: print(f'   Build page tab history cache from open tabs (MRU = current page [{self.Selection}]):')

        # adjust history cache size
        self.set_pth_cache_size()

        # restore cache and navigation order
        for pag in self.sec_pth['Stack']:
            doc = self.GetPage(pag)
            self.pth_cache[pag] = doc.pnm
            del doc

        self.set_pth_cache_head(evt, f'{me_("F")}')

        if DEBUG['PTH'] > 1: pprint([i for i in self.pth_cache.items()], indent=4, width=99)


    def page_tab_history_init(self, evt):
        if DEBUG['PTH']: print(f'{me_()}')
        # create history cache at first use
        if not self.pth_cache and self.PageCount:
            self.page_tab_history_build(evt)

        self.pth_nav_src = self.Selection
        if DEBUG['PTH']: print(f'  ** {self.pth_nav_src = }')

        _fwd = evt.Direction
        _tab = evt.IsFromTab()

        # Tab or Page key pressed, infer modifier keys
        if _tab:
            self.pth_active = True
            self.pth_nav_key = 'Ctrl+Tab' if _fwd else 'Ctrl+Shift+Tab'
        else:
            self.pth_active = False
            self.pth_nav_key = 'Ctrl+PageDown' if _fwd else 'Ctrl+PageUp'

        if DEBUG['PTH'] > 1: print('\n## STAGE 1: Navigation key used')
        if DEBUG['PTH'] > 1: print(f'  {me_("F")}    (page tab {self.current_page(_fwd)}): Tab [{_tab!r:>5}]  Fwd [{_fwd!r:>5}]  Key [{self.pth_nav_key}]')

        # disable this handler until Ctrl and/or Shift are released
        self.Bind(wx.EVT_NAVIGATION_KEY, None)
        # enable idle handler to intercept Ctrl and/or Shift release, when Tab used
        self.Bind(wx.EVT_IDLE, self.page_tab_history_update)
        evt.Skip()


    def page_tab_history_update(self, evt):
        if DEBUG['PTH']: print(f'{me_()}')
        # Page keys are NOT further processed and keep default navigation behaviour
        if 'Page' in self.pth_nav_key:
            self.Bind(wx.EVT_NAVIGATION_KEY, self.page_tab_history_init)
            self.Bind(wx.EVT_IDLE, None)
            return

        # catch keypress
        _gks = wx.GetKeyState
        _tab, ctrl, shift = _gks(wx.WXK_TAB), _gks(wx.WXK_CONTROL), _gks(wx.WXK_SHIFT)

        # Tab key pressed, plus 1 or 2 modifier keys
        if _tab and (ctrl or shift):
            if not shift:
                _fwd = True
                self.pth_nav_key = 'Ctrl+Tab'
            else:
                _fwd = False
                self.pth_nav_key = 'Ctrl+Shift+Tab'

            if DEBUG['PTH'] > 1: print('\n## STAGE 2: Navigation key used')
            if DEBUG['PTH'] > 1: print(f'  {me_("F")}  (page tab {self.Selection}): Tab [{_tab!r:>5}]  Fwd [{_fwd!r:>5}]  Key [{self.pth_nav_key}]')

            if DEBUG['PTH'] > 1: print('\n## STAGE 2: Wait for Ctrl/Shift key release...')
            if DEBUG['PTH'] > 1: print(f'++ {_tab=}  {ctrl=}  {shift=}')

            if _fwd:
                _new_page_tab = self.get_pth_cache_key(self.Selection)
            else:
                _new_page_tab = self.get_pth_cache_key(self.Selection, nxt=-1)
            if DEBUG['PTH']: print(f'  ** {_new_page_tab = }')

            self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, None)
            # self.pth_active = False  # avoid veto in 'PageChang...' events
            self.SetSelection(_new_page_tab)
            # self.pth_active = True
            self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.page_changing)

#HACK: prevent selecting sequence of page tabs instead of just one
            wx.MilliSleep(200)

        # Ctrl and/or Shift released
        if not (ctrl or shift):
            if DEBUG['PTH'] > 1: print('=' * 46)
            if DEBUG['PTH'] > 1: print(f'  Ctrl/Shift released (MRU = page tab {self.Selection})')
            if DEBUG['PTH'] > 1: print('=' * 46)

            self.set_pth_cache_head(evt, 'STAGE 3: Ctrl/Shift released')  # self.set_pth_cache_head(evt, f'{me_("F")}')

            if DEBUG['PTH'] > 1: pprint([i for i in self.pth_cache.items()], indent=4, width=99)

            self.pth_active = False  # avoid veto in 'PageChang...' events
            # call 'PageChang...' events after INSTEAD OF before this update handler
            wx.CallAfter(self.page_changing, wx.PyCommandEvent(aui.EVT_AUINOTEBOOK_PAGE_CHANGING.typeId, self.Id))
            # wx.CallAfter(self.page_changed, wx.PyCommandEvent(aui.EVT_AUINOTEBOOK_PAGE_CHANGED.typeId, self.Id))

            # enable navigation keys again
            self.Bind(wx.EVT_NAVIGATION_KEY, self.page_tab_history_init)
            # disable this idle handler; Ctrl and/or Shift are released
            self.Bind(wx.EVT_IDLE, None)


    def page_changing(self, evt):
        if not (doc := get_doc()): return

        # discard/veto page change when 'glancing'
        if self.glc_active:
            if DEBUG['GEN']: print(f'{me_("C, F")}: {self.glc_active = }')
            evt.Veto()
            return

        if not self.pth_active or 'Page' in self.pth_nav_key:
            if DEBUG['PTH'] > 1: print(f'    {me_("F")}: Allow on page tab {self.Selection}', evt)
        else:
            if DEBUG['PTH'] > 1: print(f'    {me_("F")}: Veto on page tab {self.Selection}')
            evt.Veto()
            return

        if DEBUG['PTH'] > 1: print(f'\n## STAGE 4: {me_("F")} from page tab {self.pth_nav_src} to {self.Selection}')

        # handle current page before switching to target page
        if DEBUG['GEN']: print(f'{me_()}')
        if DEBUG['EVT'] > 1: dbg_EVENT(evt)
#FIX, global macro recording? if not stop record at page change
        if doc.mac_rec_active:
            doc.macro_stop(None)

        # doc.state = doc.get_docstate()
        self.update_ui(doc)

        if self.pag_creating:
            self.pag_creating = False

        dbg_PTH_CACHE_INFO(self)

        evt.Skip()


    def page_changed(self, evt):
        if not (doc := get_doc()): return

        glb.DOC = self.GetPage(self.Selection)
        if DEBUG['GLB']:
            print(f'  NBK: {id(glb.DOC) = } -> {glb.DOC.fnm = }')

        if not self.pth_active or 'Page' in self.pth_nav_key:
            if DEBUG['PTH'] > 1: print(f'     {me_("F")}: Allow on page tab {self.Selection}', evt)
        else:
            if DEBUG['PTH'] > 1: print(f'     {me_("F")}: Veto on page tab {self.Selection}')
            evt.Veto()
            return

        glb.TLW.Freeze()

        if DEBUG['PTH'] > 1: print(f'\n## STAGE 5: {me_("F")} from page tab {self.pth_nav_src} to {self.Selection}')
        if DEBUG['AFE']: print(f'{" "*11}Includes: {me_("F")}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL CODE: P a g e   T a b   H i s t o r y - END
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # handle target page
        if DEBUG['GEN']: print(f'{me_()}')
        if DEBUG['EVT'] > 1: dbg_EVENT(evt)

        if self.sec_pth['Enable']:
            # adjust history cache size
            self.set_pth_cache_size()
            # insert unique page index key
            self.pth_cache[self.PageCount - 1] = doc.pnm

            if 'Page' not in self.pth_nav_key:
                self.set_pth_cache_head(evt, f'STAGE 4: {me_("F")}')

        # doc.state = doc.set_docstate()
        self.update_ui(doc, full=True)

        wx.CallAfter(self.tabctrl_access, evt)

        if self.pag_created:
            self.pag_created = False

        dbg_PTH_CACHE_INFO(self)

        evt.Skip()

        glb.TLW.Thaw()


    def page_close(self, evt, fil_cls_called=False):
        if DEBUG['GEN']: print(f'{me_()}')
        if DEBUG['EVT'] > 1: dbg_EVENT(evt)
#HACK: 'aui PAGE_CLOSE' event ONLY fires when page close button is clicked
#NOTE,        it does NOT fire when Ctrl-W shortcut is pressed, so FORCE call to file_close
        if not fil_cls_called:
            cur_sel = evt.Selection
            # page close button is clicked on an unfocused page tab
            self.SetSelection(evt.Selection)
            glb.TLW.file_close(evt, pag_cls_called=True)
        else:
            cur_sel = self.Selection

        # rebuild history cache after page tab close (deletes current page index key)
        if self.sec_pth['Enable']:
            if self.PageCount:

                dbg_PTH_CACHE_INFO(self)

                # copy cache
                pth_cache_tmp = {i[0]:i[1] for i in list(self.pth_cache.items())}
                # delete current page index key in copy
                pth_cache_tmp.pop(cur_sel)
                # clear cache and recreate from copy
                self.pth_cache.clear()
                for k, v in reversed(pth_cache_tmp.items()):
                    if k > cur_sel:
                        self.pth_cache[k - 1] = v
                    else:
                        self.pth_cache[k] = v
                del pth_cache_tmp

                dbg_PTH_CACHE_INFO(self)

        evt.Veto()  # prevent main window close


    def page_begin_drag(self, evt):
        if DEBUG['GEN']: print(f'{me_()}')
        if DEBUG['EVT'] > 1: dbg_EVENT(evt)

        dbg_PTH_CACHE_INFO(self)

        evt.Skip()


    def page_end_drag(self, evt):
        if DEBUG['GEN']: print(f'{me_()}')
        if DEBUG['EVT'] > 1: dbg_EVENT(evt)
#NOTE, solves unresponsive page tab
        # self.SetSelection(evt.Selection)

        if self.sec_pth['Enable']:

            dbg_PTH_CACHE_INFO(self)

            for key in reversed(list(self.pth_cache)):
                if key == evt.Selection:
                    self.pth_cache[evt.Selection] = self.GetPage(key).pnm
                else:
                    self.pth_cache[key] = self.GetPage(key).pnm

#NOTE, obsolete code? ==>> NO!!
            self.set_pth_cache_head(evt, f'page_end_drag: {me_("F")}')

            dbg_PTH_CACHE_INFO(self)

        # update document list control order (after tab drag)
        if (ctl := glb.SPN.sgl_lst[SPT.DOC.idx]):
            ctl.update_list(self.CurrentPage)

        evt.Skip()


    def notebook_info(self, evt):
        if DEBUG['GEN']: print(f'{me_()}')
        if DEBUG['EVT'] > 1: dbg_EVENT(evt)
#TODO, fill with info, open files, editor statistics? whatever comes to mind
        not_implemented(None, 'notebook_info')
        msg = APP['Base'] + ' Info\n\n'
        msg_box(self, 'INFO', msg)


    def insert_page_tab(self, *args, **kwargs):
        self.pag_creating = True
        self.pag_created = True
        self.InsertPage(*args, **kwargs)


#NOTE: convenience generator function, yields pagenum and document (Editor) object
    def open_docs(self):
        for pag in range(self.PageCount):
            # print('before')
            doc = self.GetPage(pag)
            yield pag, doc  # with body executes here
            # print('after')


    def update_page_tab(self, doc, newtab=False):
#NOTE, prevent circular dependency
        from common.file import get_file_attributes, get_file_icon

        def __tooltip(doc):
            fnm, pnm = doc.fnm, doc.pnm

            # build page tab tooltip
            tti = glb.CFG['Notebook']['TabToolTipFileInfo']
            wsp = '\n\t'
            sep = ' : '
            ttp = f'File{sep}'
            ttp += pnm if 'P' in tti else fnm  # pathname or filename

            # timestamps/size for existing file (having a dnm)
            if doc.dnm:
#NOTE, prevent circular dependency
                from common.file import get_file_status
                cre, mod, acc, szk, szb = get_file_status(pnm)
                att_lst = get_file_attributes(pnm)

                ttp += f'{wsp}Size\t{sep}{szk} Kb ({szb} bytes)' if 'S' in tti else TXT_NIL
                ttp += f'{wsp}Type\t{sep}{doc.lng_nam}'          if 'T' in tti else TXT_NIL
                ttp += f'{wsp}Created\t{sep}{tim_str(cre)}'      if 'C' in tti else TXT_NIL
                ttp += f'{wsp}Modified{sep}{tim_str(mod)}'       if 'M' in tti else TXT_NIL
                ttp += f'{wsp}Accessed{sep}{tim_str(acc)}'       if 'A' in tti else TXT_NIL
                ttp += f'{wsp}Attrib\t{sep}{att_lst[0]}'         if 'B' in tti else TXT_NIL
                ttp += f'{wsp}\t   {att_lst[1]}'                 if 'L' in tti else TXT_NIL

                ttp += f'\n\n *  Modified' if doc.IsModified() else TXT_NIL
                ttp += f'\n # ReadOnly'    if doc.ReadOnly else TXT_NIL

            return ttp

        if DEBUG['GEN']: print(f'{me_()}')

        fnm, pnm, pag = doc.fnm, doc.pnm, self.Selection

        # add new tab to right of current tab
        if newtab:
            pag += 1
            ico = get_file_icon(doc.lng_typ)
            self.insert_page_tab(pag, doc, fnm, bitmap=ico)

        # page tab indicators
        if doc.IsModified():
            mod = glb.CFG['General']['DocModifiedIndicator']
            fnm += mod
            pnm += mod

        if doc.ReadOnly:
            lck = glb.CFG['General']['DocReadOnlyIndicator']
            fnm += lck
            pnm += lck

        # frame and page tab text
        glb.TLW.SetTitle(f"{APP['Base']} - [{pnm}]")
        self.SetPageText(pag, fnm)

        # dynamically toggle all page tab tooltips
        for pag_ttp, doc_ttp in self.open_docs():
            self.SetPageToolTip(pag_ttp, __tooltip(doc_ttp))

        dbg_FOCUS(doc)


    def update_ui(self, doc, full=False):
        doc.state = doc.set_docstate() if full else doc.get_docstate()
        self.update_page_tab(doc)
        if full:
            if DEBUG['APP']: print(f'   NBK: {wx.GetApp().ready = }\n   {self.Selection:3}) {doc.fnm}\n')

            pub.sendMessage('pag_chg_spn', evt=None)
            pub.sendMessage('pag_chg_kws', evt=None, mnu_obj=glb.MB)

            # update document list control selection
            if (ctl := glb.SPN.sgl_lst[SPT.DOC.idx]):
                ctl.Select(self.Selection)

            # glb.SPN.page_changed(None)
            # glb.TLW.update_keyword_sets_menu(None, glb.MB)


    def make_tab_visible(self):
        if (tab_ctl := self.FindWindow('wxAuiTabCtrl')) is None:
            return
        if not (sel := self.Selection):
            return
        tab_ctl.Update()  # force 'rect' update
        # tab state from 'AuiTabContainer' and 'AuiNotebookPage'
        tab = tab_ctl.Pages[sel]
        vis = tab.rect != wx.Rect(0, 0, 0, 0)
        if not vis:
            tab_ctl.MakeTabVisible(sel, tab_ctl)
        if DEBUG['NBK']: print(f'==>> {me_("F")}: Active tab [{sel:3}]: visible=[{vis!r:>5}], caption=[{tab.caption}]')


#HACK: enable access to 'wx.aui.AuiTabCtrl' (tab control window)
    def tabctrl_access(self, evt):
        self.tab_ctl = self.FindWindow('wxAuiTabCtrl')

        # cycle notebook tab controls ('wxAuiTabCtrl'), start at 1st id
        for _tc_id_ in range(TABCTRL_ID, TABCTRL_ID + 20):
            _tc_obj = self.FindWindow(_tc_id_)
            pag_cnt = _tc_obj.PageCount if _tc_obj else 0
            TABCTRL_FOUND = bool(_tc_obj)

            # tab control has page tabs
            if pag_cnt:
                if DEBUG['NBK'] > 1: print(f'{_tc_id_}: {pag_cnt} pages in {_tc_obj} at pos: {_tc_obj.Position}')
#FIX, use enumerate, cnt
                cnt = 0
                # documents in this tab control
                for pag, __ in self.open_docs():
                    if cnt >= pag_cnt:
                        break
                    # active = 'Active'  if cnt == self.Selection else '      '
                    wsp = rs_(8, ' ')
                    txt = f'{cnt}: {_tc_obj.GetPage(pag).window.fnm}'
                    if cnt == self.Selection:
                        if DEBUG['NBK'] > 1: print(f'{wsp}[CUR] [{txt}]')
                    else:
                        if DEBUG['NBK'] > 1: print(f'{wsp}       {txt}')
                    cnt += 1
            elif _tc_obj and pag_cnt == 0:
                if DEBUG['NBK'] > 1: print(f'{_tc_id_}: {pag_cnt} pages in {_tc_obj}')
            # else:
                # if DEBUG['NBK'] > 1: print(f'{_tc_id_}: non-existent tab control id')

        if DEBUG['NBK'] > 1:
            if TABCTRL_FOUND:
                print()

        if self.tab_ctl:
            # self.tab_ctl.Bind(wx.EVT_MOTION, self.tabctrl_hover)
            self.tab_ctl.Bind(wx.EVT_SET_FOCUS, self.tabctrl_focus)
            self.tab_ctl.Bind(wx.EVT_MOUSEWHEEL, self.tabctrl_wheel)

        evt.Skip()


    def tabctrl_hover(self, evt):
        def __set_glance_active(val):
            self.glc_active = val

        evt.Skip()

        x, y = evt.Position
        hit, doc = self.tab_ctl.TabHitTest(x, y)

        # hide all 'glance views' except for current doc
        for pag, doc_chk in self.open_docs():
            if doc_chk is not doc and doc_chk.glc_obj and doc_chk.glc_obj.IsShown():
                doc_chk.glc_obj.Hide()

        __set_glance_active(True)

        if hit:
            # discard (and hide) current doc's 'glance view'
            if doc is self.CurrentPage:
                __set_glance_active(False)
                if doc.glc_obj:
                    doc.glc_obj.Hide()
                return

            pag = self.tab_ctl.GetIdxFromWindow(doc)

            if not doc.glc_obj:
                if DEBUG['GEN']: print(f'{me_("C, F")}: {pag=}, {doc.fnm=}, {doc}')
                doc.glc_obj = TabCtrlDocGlance(self, pag)
                if DEBUG['GEN']: print(f'{me_("C, F")}: {pag=}, {doc.fnm=}, {doc}\n')

            self.tab_ctl.Bind(wx.EVT_LEAVE_WINDOW, lambda e: doc.glc_obj.Hide())

            tab_lst = self.tab_ctl.Pages
            x, y = tab_lst[pag].rect.Position

            doc.glc_obj.SetPosition(self.tab_ctl.ClientToScreen(x, y + self.TabCtrlHeight))
            doc.glc_obj.SetTitle(f'[{doc.fnm}]')
            doc.glc_obj.stc_pvw.SetFirstVisibleLine(doc.FirstVisibleLine)

            if not doc.glc_obj.IsShown():
                doc.glc_obj.Show()

        # force focus on tab ctrl and implicitly on current doc
        self.tabctrl_focus(None)

        # 10 ms: just enough wait time for flag (veto) check in 'page_changing'
        wx.CallLater(10, __set_glance_active, False)


#HACK: prevent page tab focus (dotted rectangle), transfer to associated document
    def tabctrl_focus(self, evt):
        dbg_FOCUS(self.CurrentPage)


    def tabctrl_wheel(self, evt):
        _rot = evt.WheelRotation  # is multiple of 120 (+/- delta)
        _fwd = bool(_rot < 0)

        ctrl, shift = evt.controlDown, evt.shiftDown

        if ctrl:
            if shift:
                # Ctrl+Shift: select first/last page tab
                self.SetSelection(self.PageCount - 1 if _fwd else 0)
            else:
                # Ctrl: select next/previous page tab (wraparound)
                self.AdvanceSelection(bool(_fwd))
        elif shift:
            # Shift: move current page tab left/right
            pag = self.Selection
            # validate first/last page tab indices
            if _fwd and pag + 1 > self.PageCount - 1:
                return
            if not _fwd and pag - 1 < 0:
                return

            glb.TLW.Freeze()
            # save arguments
            doc = self.GetPage(pag)
            fnm = doc.fnm
            ico = self.GetPageBitmap(pag)
            # delete
            self.RemovePage(pag)
            # move left or right
            pag = pag + 1 if _fwd else pag - 1
            # reinsert, reselect
            self.insert_page_tab(pag, doc, fnm, bitmap=ico)
            self.SetSelection(pag)
            glb.TLW.Thaw()
#TODO, config option: select next/previous page tab (wraparound), WITHOUT Ctrl
        # else:
        #     self.AdvanceSelection(bool(_fwd))


# @dbg_method_calls()
class TabCtrlDocGlance(wx.MiniFrame):

    __slots__ = ['stc_pvw']

    def __init__(self, prt, pag, **kwargs):
        # self.sec = glb.CFG['TabCtrlDocGlance']
        # wid = self.sec['Width']  # preview to editor width ratio (0.00 to 1)
        # hgh = self.sec['Height']  # num preview lines (use line height in pixels)
        # sty = wx.CAPTION if self.sec['Caption'] else 0
        sty = 0  # wx.CAPTION
        super().__init__(prt, wx.ID_ANY, style=sty, name='mnfTabCtrlDocGlance')

        # if self.sec['DropShadow']:
        #     drop_shadow(self)

        drop_shadow(self, show=False)

        doc = prt.GetPage(pag)
        if DEBUG['GEN']: print(f'{me_("C, F")}: {pag=}, {doc.fnm=}, {doc}')

        # self.SetBackgroundColour(self.sec['BorderColour'])  # '#C6E2FF'

        self.SetBackgroundColour('#C6E2FF')

        self.stc_pvw = gui.Editor(self, [doc.dnm, doc.fnm, doc.fbs, doc.ext])

        # prevent zoom event from firing in main editor doc
        self.stc_pvw.Bind(stc.EVT_STC_ZOOM, None)

        add_doc_view(doc, self.stc_pvw, is_dcm=True)  # init 'doc glancer' editor control

        if DEBUG['GEN']: print(f'  {         doc = }\n  {self.stc_pvw = }\n')

        self.SetSize(160, 200)

#HACK: use sizer to simulate border (width/colour)
        bxv = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(bxv)
        self.Show()
