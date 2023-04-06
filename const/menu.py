#!/usr/bin/python

import wx


# new (window) ID ref: alias
__ID = wx.NewIdRef

# menu font (auxiliary)
MNU_FNT_AUX = False  # activate
# menu font:   pointSize  family               style                weight                faceName
MNU_FNT_TYP = (10,        wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 'Consolas')

# keyword sets: menu item ids
ALL_KWS_ID = __ID()  # Select All
NON_KWS_ID = __ID()  # Select None

# absent menu item attribute constants
# shortcut, action, statusbar text, icon, type, ui handler
#TODO, NO_ACT, OBSOLETE when all items have action
NO_SCT = None
NO_ACT = None  # OR: 'not_implemented'
NO_HLP = '[Missing help text]'
NO_ICO = None
NO_KND = None
NO_UIH = None

# MenuBar/ToolBar: separator
SEP = None

# MenuBar: menu item ids
MI = {
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    'SUB_CRO'       : __ID(),
    'SUB_LNO'       : __ID(),
    'SUB_SCH'       : __ID(),
    'SUB_SPT'       : __ID(),
    'SUB_SCL'       : __ID(),
    'SUB_CRT'       : __ID(),
    'SUB_MGN'       : __ID(),
    'SUB_EDG'       : __ID(),
    'SUB_JBM'       : __ID(),
    'SUB_BMK'       : __ID(),
    'SUB_TSK'       : __ID(),
    'SUB_CAS'       : __ID(),
    'SUB_EOL'       : __ID(),
    'SUB_MAC'       : __ID(),
    'SUB_GUI'       : __ID(),
    'SUB_EDT'       : __ID(),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    'AUT_SCL'       : __ID(),
    'CON_OUT'       : __ID(),
    'EDT_ACP'       : __ID(),
    'EDT_CPF'       : __ID(),
    'EDT_CTP'       : __ID(),
    'EDT_DEL'       : __ID(),
    'EDT_DPL'       : __ID(),
    'EDT_SUM'       : __ID(),
    'EDT_TPL'       : __ID(),
    'EDT_XWD'       : __ID(),
    'FIL_CHD'       : __ID(),
    'FIL_NEW'       : __ID(),
    'FIL_OPN'       : __ID(),
    'FIL_QOP'       : __ID(),
    'FIL_RVS'       : __ID(),
    'FIL_SAV'       : __ID(),
    'FIL_SVA'       : __ID(),
    'FIL_WBL'       : __ID(),
    'FIL_XIT'       : __ID(),
    'FMT_CMT'       : __ID(),
    'FMT_CST'       : __ID(),
    'FMT_CTS'       : __ID(),
    'FMT_FLB'       : __ID(),
    'FMT_ITM'       : __ID(),
    'FMT_ITP'       : __ID(),
    'FMT_PAR'       : __ID(),
    'FMT_RMC'       : __ID(),
    'FMT_RMT'       : __ID(),
    'FMT_UNI'       : __ID(),
    'FOL_STY'       : __ID(),
    'GTO_ANY'       : __ID(),
    'GTO_LIN'       : __ID(),
    'GTO_OFL'       : __ID(),
    'GTO_SYM'       : __ID(),
    'GTO_TBM'       : __ID(),
    'GTO_TTK'       : __ID(),
    'HLP_ABT'       : __ID(),
    'HLP_CON'       : __ID(),
    'SUB_IND'       : __ID(),
    'LAY_CPU'       : __ID(),
    'LAY_KBD'       : __ID(),
    'LAY_MNE'       : __ID(),
    'LAY_PRF'       : __ID(),
    'LAY_SYN'       : __ID(),
    'MAC_LOD'       : __ID(),
    'MAC_SAV'       : __ID(),
    'MAC_xx1'       : __ID(),
    'MAC_xx2'       : __ID(),
    'MAC_xx3'       : __ID(),
    'MAC_xx4'       : __ID(),
    'MCH_BRC'       : __ID(),
    'RUN_DBM'       : __ID(),
    'RUN_MOD'       : __ID(),
    'RUN_TBP'       : __ID(),
    'SRC_STA'       : __ID(),
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # file operations
    'FIL_SAS'       : __ID(),  # save as
    'FIL_REN'       : __ID(),  # rename
    'FIL_CFD'       : __ID(),  # change to file dir
    'FIL_INS'       : __ID(),  # insert
    'FIL_APD'       : __ID(),  # append
    'FIL_CLS'       : __ID(),  # close
    'FIL_CLA'       : __ID(),  #   "   all
    'FIL_CAE'       : __ID(),  #   "    "  except
    'FIL_NWN'       : __ID(),  # new window
    'FIL_CWN'       : __ID(),  # close "
    # recent file history
    'SUB_RFH'       : __ID(),  # recent file history submenu in 'File'
    'FIL_RCF'       : __ID(),  # reopen closed (1 file)
    'FIL_RCA'       : __ID(),  #   "      "    (ALL)
    'FIL_CLI'       : __ID(),  # clear items
    # undo, redo, cut, copy, paste
    'EDT_UDO'       : __ID(),
    'EDT_RDO'       : __ID(),
    'EDT_CUT'       : __ID(),
    'EDT_CPY'       : __ID(),
    'EDT_PST'       : __ID(),
    # move caret to
    'CRT_TOP'       : __ID(),
    'CRT_CTR'       : __ID(),
    'CRT_BOT'       : __ID(),
    # paragraph
    'PAR_NXT'       : __ID(),
    'PAR_PRV'       : __ID(),
    # scroll line to
    'LIN_TOP'       : __ID(),
    'LIN_CTR'       : __ID(),
    'LIN_BOT'       : __ID(),
    # move selected lines down/up
    'LIN_SLD'       : __ID(),
    'LIN_SLU'       : __ID(),
    # sort lines
    'SRT_LIN'       : __ID(),
    'SRT_REV'       : __ID(),
    'SRT_UNQ'       : __ID(),
    # select
    'SEL_SPL'       : __ID(),
    'SEL_APL'       : __ID(),
    'SEL_ANL'       : __ID(),
    'SEL_SGL'       : __ID(),
    'SEL_INV'       : __ID(),
    'SEL_ALL'       : __ID(),
    'SEL_WRD'       : __ID(),
    'SEL_LIN'       : __ID(),
    'SEL_PAR'       : __ID(),
    'SEL_BRC'       : __ID(),
    'SEL_IND'       : __ID(),
    'SEL_SWP'       : __ID(),
    # search
    'SCH_FND'       : __ID(),  # find
    'SCH_RPL'       : __ID(),  # replace
    'SCH_NXT'       : __ID(),  # find next
    'SCH_PRV'       : __ID(),  #   "  previous
    'SCH_CUN'       : __ID(),  #   "  current next
    'SCH_CUP'       : __ID(),  #   "     "    previous
    'SCH_CUA'       : __ID(),  #   "     "    all
    'SCH_FIF'       : __ID(),  #   "  in files
    'SCH_INC'       : __ID(),  # incremental
    'SCH_RES'       : __ID(),  # results
    # search options
    'SCH_CAS'       : __ID(),  # case sensitive
    'SCH_REG'       : __ID(),  # regular expression
    'SCH_WRD'       : __ID(),  # whole words only
    'SCH_WRP'       : __ID(),  # wrap around
    'SCH_ISL'       : __ID(),  # in selection
    'SCH_HLM'       : __ID(),  # highlight matches
    'SCH_PCS'       : __ID(),  # preserve case
    'SCH_CXT'       : __ID(),  # show context
    'SCH_BUF'       : __ID(),  # use buffer
    # bookmarks
    'BMK_NXT'       : __ID(),  # next
    'BMK_PRV'       : __ID(),  # previous
    'BMK_JB1'       : __ID(),  # jump to #num
    'BMK_JB2'       : __ID(),
    'BMK_JB3'       : __ID(),
    'BMK_JB4'       : __ID(),
    'BMK_JB5'       : __ID(),
    'BMK_JB6'       : __ID(),
    'BMK_JB7'       : __ID(),
    'BMK_JB8'       : __ID(),
    'BMK_JB9'       : __ID(),
    'BMK_JB0'       : __ID(),
    # tasks
    'TSK_NXT'       : __ID(),
    'TSK_PRV'       : __ID(),
    # caret position history
    'JMP_BCK'       : __ID(),
    'JMP_FWD'       : __ID(),
    # side panel tools
    'SPT_FLT'       : __ID(),
    'SPT_DLF'       : __ID(),  # delete list filter
    'SPT_DCL'       : __ID(),
    'SPT_PRJ'       : __ID(),
    'SPT_BMK'       : __ID(),
    'SPT_LNG'       : __ID(),
    'SPT_FXP'       : __ID(),
    'SPT_SDF'       : __ID(),
    'SPT_MAC'       : __ID(),
    'SPT_TSK'       : __ID(),
    'SPT_BPT'       : __ID(),
    'SPT_DBG'       : __ID(),
    'SPT_DCM'       : __ID(),
    'SPT_CFG'       : __ID(),
    'SPT_HLP'       : __ID(),
    'SPT_PLT'       : __ID(),
    'SPT_PFL'       : __ID(),
    'SPT_PYS'       : __ID(),
    'SPT_VLT'       : __ID(),
    'SPT_MDN'       : __ID(),
    'SPT_CFW'       : __ID(),
    'SPT_SNP'       : __ID(),
    # word wrap, EOL, whitespace, read-only
    'DOC_WRP'       : __ID(),
    'DOC_EOL'       : __ID(),
    'DOC_WSP'       : __ID(),
    'DOC_LCK'       : __ID(),
    # indent guides
    'IND_GDS'       : __ID(),
    # scrollbars
    'SCL_NON'       : __ID(),
    'SCL_BTH'       : __ID(),
    'SCL_HOR'       : __ID(),
    'SCL_VER'       : __ID(),
    # BRIEF Home/End keys
    'CRT_BRF'       : __ID(),
    # caret line and sticky
    'CRT_LIN'       : __ID(),
    'CRT_STK'       : __ID(),
    # margin
    'MGN_ALL'       : __ID(),
    'MGN_NUM'       : __ID(),
    'MGN_SYM'       : __ID(),
    'MGN_FOL'       : __ID(),
    # edge
    'EDG_NON'       : __ID(),
    'EDG_BCK'       : __ID(),
    'EDG_LIN'       : __ID(),
    'EDG_MUL'       : __ID(),
    'EDG_COL'       : __ID(),
    'EDG_CLR'       : __ID(),
    # zoom
    'ZOO_RST'       : __ID(),
    'ZOO_IN_'       : __ID(),
    'ZOO_OUT'       : __ID(),
    # window on top
    'WIN_TOP'       : __ID(),
    # breakpoints
    'BPT_ENA'       : __ID(),
    'BPT_NXT'       : __ID(),
    'BPT_PRV'       : __ID(),
    # language
    'SUB_KWS'       : __ID(),  # keyword sets submenu in 'Language'
    'LNG_BASH'      : __ID(),
    'LNG_BATCH'     : __ID(),
    'LNG_CONF'      : __ID(),
    'LNG_CPP'       : __ID(),
    'LNG_CSS'       : __ID(),
    'LNG_HTML'      : __ID(),
    'LNG_MARKDOWN'  : __ID(),
    'LNG_PASCAL'    : __ID(),
    'LNG_PERL'      : __ID(),
    'LNG_PHPSCRIPT' : __ID(),
    'LNG_POWERSHELL': __ID(),
    'LNG_PROPERTIES': __ID(),
    'LNG_PYTHON'    : __ID(),
    'LNG_RUBY'      : __ID(),
    'LNG_SQL'       : __ID(),
    'LNG_TCL'       : __ID(),
    'LNG_XML'       : __ID(),
    'LNG_YAML'      : __ID(),
    'LNG_NULL'      : __ID(),
    # recent project history
    'PRJ_NEW'       : __ID(),
    'PRJ_OPN'       : __ID(),
    'PRJ_CLS'       : __ID(),
    'PRJ_OPA'       : __ID(),
    'PRJ_CLA'       : __ID(),
    'PRJ_FIL'       : __ID(),
    'PRJ_RPH'       : __ID(),  # recent project history submenu in 'Project'
    'PRJ_CLI'       : __ID(),  # clear items
    'PRJ_MFL'       : __ID(),
    # format case
    'FMT_TTL'       : __ID(),
    'FMT_UPR'       : __ID(),
    'FMT_LWR'       : __ID(),
    'FMT_INV'       : __ID(),
    # format convert EOL
    'FMT_ECL'       : __ID(),  # Windows (CRLF)
    'FMT_ELF'       : __ID(),  # Unix (LF)
    'FMT_ECR'       : __ID(),  # Mac (CR)
    'FMT_EMX'       : __ID(),  # Mixed EOLs
    # macro
    'MAC_TST'       : __ID(),  # temporary macro test
    'MAC_QRC'       : __ID(),
    'MAC_REC'       : __ID(),
    'MAC_STP'       : __ID(),
    'MAC_PLY'       : __ID(),
    'MAC_PLM'       : __ID(),
    'MAC_EDT'       : __ID(),
    # layout
    # 'PEF_MNU'       : __ID(),  # panel effect submenu in 'Layout'
    'LAY_CAP'       : __ID(),
    'LAY_MBR'       : __ID(),
    'LAY_TBR'       : __ID(),
    'LAY_IBR'       : __ID(),
    'LAY_SBR'       : __ID(),
    'LAY_SCH'       : __ID(),  # search panel
    'LAY_SCS'       : __ID(),  #   swap
    'LAY_RLR'       : __ID(),  # ruler
    'LAY_RLS'       : __ID(),  #   swap
    'LAY_SPN'       : __ID(),  # side panel
    'LAY_SPS'       : __ID(),  #   swap
    'LAY_SPR'       : __ID(),  #   reset
    'LAY_CCX'       : __ID(),  # code context
    'LAY_CCS'       : __ID(),  #   swap
    'LAY_MIC'       : __ID(),  # menu icons
    'LAY_MIK'       : __ID(),  #  ''  icons (custom checkable)
    'LAY_MHT'       : __ID(),  #  ''  help text
    'LAY_PTB'       : __ID(),  # page tabs
    'LAY_PTT'       : __ID(),  #  theme
    'LAY_PTI'       : __ID(),  #  icons
    'LAY_TTP'       : __ID(),  # tooltips
    'LAY_ACP'       : __ID(),  # autocomplete
    'LAY_CTP'       : __ID(),  # calltips
    'LAY_TLT'       : __ID(),  # top line tooltip
    'LAY_CTT'       : __ID(),  # colour tooltip
    'LAY_SPU'       : __ID(),  # symbol popup
    'LAY_FUL'       : __ID(),
    'LAY_DFM'       : __ID(),
    # # panel effect
    # 'PEF_DUR'       : __ID(),
    # 'PEF_NON'       : __ID(),
    # 'PEF_RLL'       : __ID(),
    # 'PEF_RLR'       : __ID(),
    # 'PEF_RLT'       : __ID(),
    # 'PEF_RLB'       : __ID(),
    # 'PEF_SLL'       : __ID(),
    # 'PEF_SLR'       : __ID(),
    # 'PEF_SLT'       : __ID(),
    # 'PEF_SLB'       : __ID(),
    # 'PEF_BLN'       : __ID(),
    # 'PEF_EXP'       : __ID(),
    # # icon size
    # 'LAY_INO'       : __ID(),
    # 'LAY_I16'       : __ID(),
    # 'LAY_I24'       : __ID(),
    # 'LAY_I32'       : __ID(),
    # help
    'HLP_CTX'       : __ID(),  # Context-sensitive Mode
    'HLP_UPD'       : __ID(),  # Check for Updates
    'HLP_WIT'       : __ID(),  # Widget Inspection Tool
    # context menu: title
    'CTX_TTL'       : __ID(),
    # context menu: editor
    'EDT_MS0'       : __ID(),  # mark using style 0 (on double-click)
    'EDT_MS1'       : __ID(),  # mark using style 1
    'EDT_MS2'       : __ID(),  #  "     "     "   2
    'EDT_MS3'       : __ID(),  #  "     "     "   3
    'EDT_MS4'       : __ID(),  #  "     "     "   4
    'EDT_MS5'       : __ID(),  #  "     "     "   5
    'EDT_CS1'       : __ID(),  # clear style 1
    'EDT_CS2'       : __ID(),  #   "     "   2
    'EDT_CS3'       : __ID(),  #   "     "   3
    'EDT_CS4'       : __ID(),  #   "     "   4
    'EDT_CS5'       : __ID(),  #   "     "   5
    'EDT_CSA'       : __ID(),  # clear all styles
    # context menu: margin
    'MGN_CBM'       : __ID(),  # clear bookmarks
    'MGN_CBP'       : __ID(),  #   "   breakpoints
    'MGN_CTM'       : __ID(),  #   "   task markers
    'MGN_CAM'       : __ID(),  #   "   all markers
    # context menu: statusbar, indentation
    'IND_IUS'       : __ID(),
    'IND_TW1'       : __ID(),
    'IND_TW2'       : __ID(),
    'IND_TW3'       : __ID(),
    'IND_TW4'       : __ID(),
    'IND_TW5'       : __ID(),
    'IND_TW6'       : __ID(),
    'IND_TW7'       : __ID(),
    'IND_TW8'       : __ID(),
    'IND_GSB'       : __ID(),
    'IND_ITS'       : __ID(),
    'IND_ITT'       : __ID(),
    # context menu: notebook, close all
    'NBK_CAO'       : __ID(),  # other
    'NBK_CAL'       : __ID(),  # left
    'NBK_CAR'       : __ID(),  # right
    'NBK_WFP'       : __ID(),  # Windows file properties
    # context menu: search panel, where filter
    'WHR_CLE'       : __ID(),  # clear
    'WHR_FFF'       : __ID(),  # read filters from file
    'WHR_FDR'       : __ID(),  # add folder
    'WHR_IFE'       : __ID(),  #  "  include filter (extension)
    'WHR_IFP'       : __ID(),  #  "  include filter (path)
    'WHR_EFE'       : __ID(),  #  "  exclude filter (extension)
    'WHR_EFP'       : __ID(),  #  "  exclude filter (path)
    'WHR_OFD'       : __ID(),  #  "  open folders
    'WHR_OFL'       : __ID(),  #  "  open files
    'WHR_CFL'       : __ID(),  #  "  current file
    'WHR_PVW'       : __ID(),  #  "  preview (dry run)
}

###########################################################
#NOTE, use this when we have CUSTOM accelerator keys ######
###########################################################
#   # menu item links to ToolBar Tools
#   MI['NEW'] = 18010  # new
#   MI['OPN'] = 18020  # open
#   MI['SAV'] = 18030  # save
#   MI['SAS'] = 18040  # save as
#   MI['CLS'] = 18050  # close
#   MI['CUT'] = 18060  # cut
#   MI['CPY'] = 18070  # copy
#   MI['PST'] = 18080  # paste
#   MI['UDO'] = 18090  # undo
#   MI['RDO'] = 18100  # redo
#   MI['FND'] = 18110  # find
#   MI['NXT'] = 18120  # find next
#   MI['RPL'] = 18130  # replace
#   MI['BRC'] = 18140  # brace match
#   MI['SRT'] = 18150  # sort
#   MI['SUM'] = 18160  # calc sum
#   MI['FUL'] = 18170  # fullscreen
#   MI['PRF'] = 18180  # prefs
#   ###################################
#   # link ToolBar Tools to Menu Items
#   # - use same accelerator text
#   #   in both tooltip and item
#   TB_MI_LNK = {
#       TB['NEW']: MI['NEW'],
#       TB['OPN']: MI['OPN'],
#       TB['SAV']: MI['SAV'],
#       TB['SAS']: MI['SAS'],
#       TB['CLS']: MI['CLS'],
#       TB['CUT']: MI['CUT'],
#       TB['CPY']: MI['CPY'],
#       TB['PST']: MI['PST'],
#       TB['UDO']: MI['UDO'],
#       TB['RDO']: MI['RDO'],
#       TB['FND']: MI['FND'],
#       TB['NXT']: MI['NXT'],
#       TB['RPL']: MI['RPL'],
#       TB['BRC']: MI['BRC'],
#       TB['SRT']: MI['SRT'],
#       TB['SUM']: MI['SUM'],
#       TB['FUL']: MI['FUL'],
#       TB['PRF']: MI['PRF']
#   }
###########################################################
#NOTE, END ################################################
###########################################################

# BookMarks conteXt menu
BMX = {
    'DEL': __ID(),  # delete
    'GTO': __ID(),  # goto
}

# Symbol Def conteXt menu
SDX = {
    'EXP': __ID(),  # expand
    'COL': __ID(),  # collapse
}

# TaSks conteXt menu
TSX = {
    'DEL': __ID(),  # delete
    'GTO': __ID(),  # goto
}

# BreakPoint conteXt menu
BPX = {
    'ENA': __ID(),  # enable
    'DEL': __ID(),  # delete
    'GTO': __ID(),  # goto
}

# Doc Map conteXt menu
DMX = {
#   menu item:  id      checked
    'ZRC_RND': [__ID(), False,],  # ZoneRectRounded
    'ZCT_LIN': [__ID(), True,],   # ZoneCentreLine
    'ZCT_DOT': [__ID(), True,],   # ZoneCentreDot
    'EDG_TXT': [__ID(), True,],   # EdgeTextIndicator
    'AUT_FCS': [__ID(), True,],   # AutoFocus
    'MRK_LHL': [__ID(), False,],  # MarkerLineHighlight
    'SNP_CDS': [__ID(), False,],  # SnapCursorAtDragStart
    'COD_PVW': [__ID(), False,],  # CodePreview (enable)
    'COD_CAP': [__ID(), False,],  # CodePreview (caption)
    'COD_BRD': [__ID(), False,],  # CodePreview (border)
    'COD_MGN': [__ID(), False,],  # CodePreview (margin)
}
