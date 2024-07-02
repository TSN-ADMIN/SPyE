#!/usr/bin/python

from pathlib import Path

import wx

from extern.configobj import ConfigObj
from extern.configobj.validate import Validator

from const.common import TXT_NIL
from .debug import DBG, dbf, me_


class Menu(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used yet

        if not Path(self.filename).is_file():
            self.create()

#TODO, NOT USED YET
        # set menu toggles
        self.ico = True  # self.CFG['Layout']['MenuIcons']
        self.icc = True  # self.CFG['Layout']['MenuIconsCustomCheckable']
        self.ics = 16    # self.CFG['Layout']['MenuIconSize']
        self.hlp = True  # self.CFG['Layout']['MenuHelpText']

        self.load()

    def default(self):
        # DBG('MNU', f'{me_()}\n  File = {self.filename}\n')

        # populate 1 menu section and submenu sections, when available
        def populate_section(sec_lst, sub_lst):
            sec = sec_lst[0]
            self[sec] = dict()
            for num, mni in enumerate(sec_lst[1:], start=1):
                self[sec][f'{num:02}'] = mni
            for lst in sub_lst:
                print(lst)
                sub = lst[0]
                self[sec][sub] = dict()
                for num, mni in enumerate(lst[1:], start=1):
                    self[sec][sub][f'{num:02}'] = mni

        populate_section(('&File',
            'FIL_NEW', 'FIL_OPN', 'FIL_QOP', 'SUB_RFH|Open Recen&t|app', '__SEP__', 'FIL_SAV',
            'FIL_SAS', 'FIL_SVA', '__SEP__', 'FIL_REN', 'FIL_RVS', 'FIL_CHD', 'FIL_CFD',
            '__SEP__', 'FIL_INS', 'FIL_APD', 'FIL_WBL', '__SEP__', 'FIL_NWN', 'FIL_CWN',
            '__SEP__', 'FIL_CLS', 'FIL_CLA', 'FIL_CAE', '__SEP__', 'FIL_XIT',
            ),
            (('SUB_RFH',
                'FIL_RCF', 'FIL_RCA', 'FIL_CLI',),))

        populate_section(('&Edit',
            'EDT_UDO', 'EDT_RDO', '__SEP__', 'EDT_CUT', 'EDT_CPY', 'EDT_PST', 'EDT_DEL', 'EDT_CPF', '__SEP__',
            'SUB_CRO|C&aret Operations|app', 'SUB_LNO|&Line Operations|app', '__SEP__', 'EDT_COL', 'EDT_CTP',
            'EDT_ACP', 'EDT_XWD', '__SEP__', 'SRT_LIN', 'SRT_REV', 'SRT_UNQ', '__SEP__', 'EDT_SUM',
            ),
            (('SUB_CRO',
                'CRT_TOP', 'CRT_CTR', 'CRT_BOT', '__SEP__', 'PAR_NXT', 'PAR_PRV',),
            ('SUB_LNO',
                'EDT_DPL', 'EDT_TPL', '__SEP__', 'LIN_TOP', 'LIN_CTR', 'LIN_BOT',
                '__SEP__', 'LIN_SLD', 'LIN_SLU',),))

        populate_section(('Se&lect',
            'SEL_SPL', 'SEL_APL', 'SEL_ANL', 'SEL_SGL', 'SEL_INV', '__SEP__', 'SEL_ALL', 'SEL_WRD',
            'SEL_LIN', 'SEL_PAR', 'SEL_BRC', 'SEL_IND', '__SEP__', 'SEL_SWP',
            ),
            ())

        populate_section(('&Search',
            'SCH_FND', 'SCH_RPL', 'SCH_NXT', 'SCH_PRV', '__SEP__', 'SCH_CUN', 'SCH_CUP', 'SCH_CUA',
            '__SEP__', 'SCH_FIF', 'SCH_INC', '__SEP__', 'SUB_SCH|&Option Flags|app',
            ),
            (('SUB_SCH',
                'SCH_CAS', 'SCH_REG', 'SCH_WRD', '__SEP__', 'SCH_WRP', 'SCH_ISL', 'SCH_HLM', '__SEP__',
                'SCH_PCS', '__SEP__', 'SCH_CXT', 'SCH_BUF',),))

        populate_section(('&View',
            'SCH_RES', 'CON_OUT', '__SEP__', 'SUB_SPT|Side Panel &Tools|app', '__SEP__',
            'DOC_WRP', 'DOC_EOL', 'DOC_WSP', '__SEP__', 'SUB_IND|&Indentation|app',
            'IND_GDS', 'SUB_SCL|Scroll&bars|app', 'AUT_SCL', '__SEP__', 'SUB_CRT|Caret|app',
            'SUB_MGN|&Margins|app', 'SUB_EDG|&Edge (long lines)|app', '__SEP__', 'FOL_STY', '__SEP__',
            'ZOO_RST', 'ZOO_IN_', 'ZOO_OUT', '__SEP__', 'SRC_STA', 'DOC_LCK', '__SEP__', 'WIN_TOP',),
            (('SUB_SPT',
                'SPT_FLT', 'SPT_DLF', '__SEP__', 'SPT_DOC', 'SPT_PRJ', 'SPT_BMK', 'SPT_LNG', 'SPT_FXP',
                'SPT_SDF', 'SPT_MAC', 'SPT_TSK', 'SPT_BPT', 'SPT_DBG', 'SPT_DCM', 'SPT_CFG', 'SPT_HLP',
                'SPT_PLT', 'SPT_PFL', 'SPT_PYS', 'SPT_VLT', 'SPT_MDN', 'SPT_CFW', 'SPT_DIA', 'SPT_SNP',),
            ('SUB_IND',
                'IND_IUS', '__SEP__', 'IND_TW1', 'IND_TW2', 'IND_TW3', 'IND_TW4', 'IND_TW5', 'IND_TW6',
                'IND_TW7', 'IND_TW8', '__SEP__', 'IND_GSB', '__SEP__', 'IND_ITS', 'IND_ITT',),
            ('SUB_SCL',
                'SCL_NON', 'SCL_BTH', 'SCL_HOR', 'SCL_VER',),
            ('SUB_CRT',
                'CRT_BRF', '__SEP__', 'CRT_LIN', 'CRT_STK',),
            ('SUB_MGN',
                'MGN_ALL', '__SEP__', 'MGN_NUM', 'MGN_SYM', 'MGN_FOL',),
            ('SUB_EDG',
                'EDG_NON', 'EDG_BCK', 'EDG_LIN', 'EDG_MUL', '__SEP__', 'EDG_COL', 'EDG_CLR',),))

        populate_section(('&Goto',
            'GTO_ANY', '__SEP__', 'GTO_SYM', 'GTO_LIN', '__SEP__', 'JMP_BCK', 'JMP_FWD', '__SEP__',
            'GTO_OFL', 'SUB_BMK|&Bookmarks|app', 'SUB_TSK|&Tasks|app', '__SEP__', 'MCH_BRC',
            ),
            (('SUB_BMK',
                'GTO_TBM', 'BMK_NXT', 'BMK_PRV', '__SEP__', 'SUB_JBM|&Jump to Bookmark|app',),
            ('SUB_JBM',
                'BMK_JB1', 'BMK_JB2', 'BMK_JB3', 'BMK_JB4', 'BMK_JB5', 'BMK_JB6', 'BMK_JB7',
                'BMK_JB8', 'BMK_JB9', 'BMK_JB0',),
            ('SUB_TSK',
                'GTO_TTK', 'TSK_NXT', 'TSK_PRV',),))

        populate_section(('&Run',
            'RUN_MOD', '__SEP__', 'RUN_DBM', '__SEP__', 'RUN_TBP', 'BPT_ENA', 'BPT_NXT', 'BPT_PRV',
            ),
            ())

        populate_section(('La&nguage',
            'SUB_KWS|&Keyword Sets|app', '__SEP__', 'LNG_BASH', 'LNG_BATCH', 'LNG_CONF', 'LNG_CPP',
            'LNG_CSS', 'LNG_HTML', 'LNG_MARKDOWN', 'LNG_PASCAL', 'LNG_PERL', 'LNG_PHPSCRIPT',
            'LNG_POWERSHELL', 'LNG_PROPERTIES', 'LNG_PYTHON', 'LNG_RUBY', 'LNG_SQL', 'LNG_TCL',
            'LNG_XML', 'LNG_YAML', 'LNG_NULL',
            ),
            (('SUB_KWS',
                '__SEP__',),))

        # [KeywordSets]
        # # KWS = ('&KeywordSets', [
        # #                (SEP),

        populate_section(('Project',
            'PRJ_NEW', 'PRJ_OPN', 'PRJ_CLS', '__SEP__', 'PRJ_OPA', 'PRJ_CLA', '__SEP__',
            'PRJ_FIL', 'PRJ_RPH', '__SEP__', 'PRJ_MFL',
            ),
            ())

        populate_section(('Fo&rmat',
            'SUB_CAS|&Convert Case|app', '__SEP__', 'FMT_PAR', 'FMT_FLB', 'FMT_ITP', 'FMT_CMT', 'FMT_ITM',
            '__SEP__', 'SUB_EOL|C&onvert Text to...|app', 'FMT_CST', 'FMT_CTS', 'FMT_RMC', 'FMT_RMT',
            ),
            (('SUB_CAS',
                'FMT_TTL', 'FMT_UPR', 'FMT_LWR', 'FMT_INV',),
            ('SUB_EOL',
                'FMT_ECL', 'FMT_ELF', 'FMT_ECR', 'FMT_EMX', '__SEP__', 'FMT_UNI',),))

        populate_section(('M&acro',
            'MAC_TST', 'MAC_QRC', 'MAC_REC', 'MAC_STP', 'MAC_PLY', 'MAC_PLM', '__SEP__', 'MAC_LOD',
            'MAC_SAV', '__SEP__', 'MAC_EDT', 'SUB_MAC|Re&cent/Saved Macros|app',
            ),
            (('SUB_MAC',
                'MAC_xx1', 'MAC_xx2', 'MAC_xx3', 'MAC_xx4',),))

        populate_section(('La&yout',
            'SUB_GUI|Toggle UI Elements|app', 'SUB_EDT|Toggle Editor Features|app', '__SEP__',
            'LAY_FUL', 'LAY_DFM', '__SEP__', 'LAY_PRF', 'LAY_MNE', 'LAY_SYN', 'LAY_KBD',
            ),
            (('SUB_GUI',
                'LAY_CAP', 'LAY_MBR', 'LAY_TBR', 'LAY_IBR', 'LAY_SBR', '__SEP__', 'LAY_TTP',
                '__SEP__', 'LAY_MIC', 'LAY_MIK', 'LAY_MHT', '__SEP__', 'LAY_SCH', 'LAY_SCS',
                '__SEP__', 'LAY_RLR', 'LAY_RLS', '__SEP__', 'LAY_SPN', 'LAY_SPS', 'LAY_SPR',
                '__SEP__', 'LAY_CCX', 'LAY_CCS', '__SEP__', 'LAY_PTB', 'LAY_PTT', 'LAY_PTI',),
            ('SUB_EDT',
                'LAY_ACP', 'LAY_CTP', 'LAY_TLT', 'LAY_CTT', 'LAY_SPU',),))

            # 'LAY_SPN', 'LAY_SPS', 'LAY_CCX', 'LAY_CCS', '__SEP__', 'SUB_PEF|Panel E&ffect|app',
            # '__SEP__', 'SUB_ISZ| Men&u Icons (Size Demo)|app', '__SEP__', 'LAY_MIC', 'LAY_MIK',
            # (('SUB_PEF',
            #     'PEF_DUR', '__SEP__', 'PEF_NON', 'PEF_RLL', 'PEF_RLR', 'PEF_RLT', 'PEF_RLB',
            #     'PEF_SLL', 'PEF_SLR', 'PEF_SLT', 'PEF_SLB', 'PEF_BLN', 'PEF_EXP',),
            # ('SUB_ISZ',
            #     'LAY_INO', '__SEP__', 'LAY_I16', 'LAY_I24', 'LAY_I32',),))

        populate_section(('&Help',
            'HLP_CON', 'HLP_CTX', '__SEP__', 'HLP_UPD', 'HLP_WIT', '__SEP__', 'HLP_ABT',
            ),
            ())

        # pprint(self)
        # print(self["File"].scalars)

    def create(self):
        # DBG('MNU', f'{me_()}\n  File = {self.filename}\n')

        # get default menu configuration
        self.default()

        # add blank lines and header before all (sub)sections, except the first
        first_sec = '&File'
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, '')
            self.comments[sec].insert(2, f'Comment header for {sec} menu')

        self.save()

#FIX, not used: obsolete?
    def load(self):
        # DBG('MNU', f'{me_()}\n  File = {self.filename}\n')
        ...
        # _dbf.MENU(self)

#FIX, not used: obsolete?
    def save(self):
        # DBG('MNU', f'{me_()}\n  File = {self.filename}\n')

        self.write()

    def apply(self):
        # DBG('MNU', f'{me_()}\n  File = {self.filename}\n')
        # recursive menu section walk
        def __walk_menu_section(root, sub=None, lbl='', lvl=1):
            mnu = wx.Menu()
            # print(' '*4*(lvl-1), f'{lvl} {root} {sub} {lbl}')
            sec = self[root] if not sub else self[root][sub]

            for key in sec.keys():
                val = sec[key]

#HACK, skip subsection key (handled below via 'sub')
                if isinstance(val, Section):
                    # print(key)
                    continue

                # handle separator
                if '__SEP__' in val or '-' in val:
                    mnu.AppendSeparator()
                    continue

#HACK, handle subsection reference in value
                if 'SUB_' in val:  # or '_MNU' in val
                    # print(sub, itm_lst)
                    # print(val, '\n')
                    sub, *itm_lst = val.split('|')
                    # sub, *itm_lst = val.split('|')
                    # itm_lst = MENU_ITEM[sub]
                    ico = sty = None
                    lbl, ico = itm_lst
                    mni = wx.MenuItem(None, wx.ID_ANY, lbl)

                    # label with optional font style
                    set_menu_item_label(mni, lbl)

                    # icon bitmap
                    if ico:
                        set_menu_item_icon(mni, False, ico, False)

                    # walk subsection in root
                    mni.SetSubMenu(__walk_menu_section(root, sub, lbl, lvl=lvl + 1))
                    mnu.Append(mni)
                    continue

                # print(' '*4*lvl, key, val)

                # handle menu item attributes positionally
                # attr#: 1 = label        2 = shortcut   3 = action
                #        4 = help text    5 = icon       6 = kind
                #        7 = ui handler   8 = id         9 = style (not used)

                # append 'None' elements up to max_ list length
                itm_lst = MENU_ITEM[val]
                len_, min_, max_ = len(itm_lst), 2, 9
                itm_lst = list(itm_lst) + [None] * (max_ - len_)

                if min_ <= len_ <= max_:
                    # ico = knd = uih = id_ = sty = None
                    lbl, sct, act, hlp, ico, knd, uih, id_, sty = itm_lst
                    hlp = TXT_NIL if hlp is None else hlp
                else:
                    err = f'{me_("F")}: menu item [{itm_lst[0]}] takes {min_} to {max_} arguments ({len_} given)'
                    raise AssertionError(err)

                if sct:
                    lbl = f'{lbl}\t{sct}'

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, 'MI' not used: check
                # menu item id
                if not id_:
                    id_ = MI[val]  # wx.NewIdRef()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                # check, radio or normal type
                typ = wx.ITEM_CHECK if knd == 'CHECK' else wx.ITEM_RADIO if knd == 'RADIO' else wx.ITEM_NORMAL

                # help text (statusbar)
                hlp = hlp if hlp else TXT_NIL

                mni = wx.MenuItem(None, id_, lbl, hlp, typ)

                # label with optional font style
                set_menu_item_label(mni, lbl)

                # icon bitmap
                if ico:
                    set_menu_item_icon(mni, False, ico, False)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # add action to menu item
                try:
                    if is_str(act):
                        act = eval(act)  # str -> function
                    # frm.Bind(wx.EVT_MENU, act, id=id_)
                    # print(act)
                except NameError as e:
                    print(f'NameError     : [{act = }]')
                except AttributeError as e:
                    print(f'AttributeError: [{act = }]')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # if not is_str(act):
                #     print(act)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                mnu.Append(mni)

            return mnu

        # pprint(self.sections)

        # walk root menu sections, i.e. 'File', 'Edit', ..., 'Help'
        for root in self:
            # print(root)
            # pprint(self[root].sections)
            self.mbr.Append(__walk_menu_section(root), root)

            # print()
