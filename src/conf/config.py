#!/usr/bin/python

from ast import literal_eval
import beeprint
import glob
import os
from pathlib import Path
from pprint import pprint
import re

from extern.configobj import ConfigObj, flatten_errors
from extern.configobj.validate import Validator, VdtTypeError, VdtValueError
import wx
from wx import stc

from common.date import TIM_FMT
from common.doc import update_margins
from common.file import detect_file_change, open_files
from common.type import (
    is_bool, is_int, is_float, is_list, is_str
)
from common.util import create_symbol_index
from const.menubar import DMX, MI
from const.common import (
    DELAY, IND_DOC_LCK, IND_DOC_MOD, SASH_POS, TXT_NIL
)
from conf.debug import DBG, DEBUG, dbf, me_
from const.app import CLR
from const import glb
from const.sidepanel import SPT
from const.editor import FOL_STYLE, MRK


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#INFO, URL=https://www.blog.pythonlibrary.org/2010/01/01/a-brief-configobj-tutorial/
#INFO, URL=http://configobj.readthedocs.io/en/latest/configobj.html?highlight=configspec#validation
#TODO, use configspec and validate it against a Validator object

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, Scintilla research: candidate cfg sections/keys?
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# ClearDocumentStyle
# CodePage
# FontQuality
# Scrolling
# Selection
# SetLineEndTypesAllowed(SC_LINE_END_TYPE_UNICODE)
# SetRepresentation('\xe2\x84\xa6', 'U+2126 \xe2\x84\xa6')
# SwapMainAnchorCaret
# Tab/Indent/Width/AsSpaces
# VirtualSpace
# Whitespace
# WordWrapSymbols
# Words (Navigation)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class Config(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # print(f'{self.filename   = }')
        # print(f'{self.configspec = }')
        # print(f'{self.stringify  = }')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used
        self.fil_lst = []
        self.rfh_lst = []

        if not Path(self.filename).is_file():
            self.create()

        self.load()

        # add custom validators
        self.vld.functions['colour'] = is_colour
        self.vld.functions['font'] = is_font

        # start validation
        fbs = Path(self.filename).name
        msg = f'    validate config [{fbs}]'

#NOTE, 'res' contains: boolean 'True' (OK) or dict of sections/values (FAILED)
        if (res := self.validate(self.vld, preserve_errors=True)) != True:
            print(f'{msg}: FAILED')
            # pprint(res)
            pprint(flatten_errors(self, res), width=300)
            raise SystemExit

        DBG('INF', f'{msg}: OK')

    def default(self):
        DBG('CFG', f'{me_()}\n  File = {self.filename}\n')

#FIX, move options from Editor to new General section
        sec = 'General'
        self[sec] = {}
        self[sec]['AppRedirectOutput'] = False
        self[sec].comments['AppRedirectOutput'].insert(0,
            'redirect sys.stdout and sys.stderr to separate popup window or file'
        )
        self[sec]['AppRedirectOutputFile'] = TXT_NIL  # APP['Base'] + '.log'
        self[sec].comments['AppRedirectOutputFile'].insert(0,
            'output: "" = to popup window, e.g. "filename.log" = to file'
        )
        self[sec]['AppUseBestVisual'] = False
        self[sec].comments['AppUseBestVisual'].insert(0,
            'try to use the best available system-provided visual'
        )
        self[sec]['AppClearSigInt'] = True
        self[sec].comments['AppClearSigInt'].insert(0,
            'allow Ctrl+C in console to terminate application'
        )
        self[sec]['OpenSession'] = True
        self[sec]['Theme'] = 'Default'
        self[sec]['NewFilePrefix'] = 'Edit'
        self[sec]['NewFileAtCloseLast'] = True
        self[sec]['SystemTrayMenu'] = False
        self[sec]['GlobalHotKey'] = 'Ctrl+Alt+Win+S'
        self[sec]['AcceleratorTable'] = False
        self[sec]['MultiInstance'] = False
        self[sec]['DetectFileChange'] = False
        self[sec]['DelayDetectFileChange'] = DELAY['DFC']
        self[sec]['UIEventUpdateInterval'] = 200
        self[sec]['UIEventProcessSpecified'] = False
        self[sec]['IdleEventProcessSpecified'] = False
        self[sec].comments['UIEventUpdateInterval'].insert(0,
            'UI update interval (ms): -1=disabled, 0=maximum'
        )
        self[sec]['DetectFileReadOnly'] = True  # info msg when editing read-only doc
        self[sec]['DocModifiedIndicator'] = IND_DOC_MOD
        self[sec]['DocReadOnlyIndicator'] = IND_DOC_LCK
#INFO, URL=http://www.scintilla.org/ScintillaDoc.html#SCI_SETCODEPAGE
        # self[sec][NOT_IMPL+'SourceEncoding'] = 'NONE|LOCALE|UTF-8'

        self[sec]['DialogBackColour'] = CLR['BLUE']
        # self[sec][NOT_IMPL+'MaxOpenFiles'] = 25
        self[sec]['OeufDePaques'] = False
        self[sec]['FlushClipboard'] = True
        cmt_txt = '%s example: keep clipboard contents available after application exit'
        self[sec].comments['FlushClipboard'].insert(0,
            cmt_txt % 'REGULAR'
        )
        self[sec].inline_comments['FlushClipboard'] = \
            cmt_txt % 'INLINE'
        self[sec]['OpenFileListSort'] = False  # sorted by name or page tab order

        sec = 'Splash'
        self[sec] = {}
        self[sec]['Enable'] = False
        self[sec]['DelayHide'] = DELAY['SPL']
        self[sec]['Welcome'] = False

        sec = 'WidgetInspectionTool'
        self[sec] = {}
        self[sec]['Enable'] = False
        self[sec].comments['Enable'].insert(0,
            'initialize Widget Inspection Tool (WIT) at startup'
        )
        self[sec]['ShortCut'] = 'Ctrl+Alt+Shift+I'
        self[sec]['ShowAtStartup'] = False
        self[sec]['PreSelectObject'] = 'TLW'
        self[sec]['RefreshWidgetTree'] = True

        sec = 'Window'
        self[sec] = {}
        self[sec]['PositionX'] = 940
        self[sec]['PositionY'] = 0
        self[sec]['Width'] = 987
        self[sec]['Height'] = 1057
        self[sec]['OnTop'] = False
        self[sec]['DragAcceptFiles'] = True
        self[sec]['Transparency'] = True
        self[sec]['TransparencyAlpha'] = 255  # integer: 0..255

        sec = 'ContextMenu'
        self[sec] = {}
        # self[sec]['Title'] = ContextMenu
        # self[sec]['TitleFontStyle'] = 'bold, large'

#NOTE, not used
        self[sec]['Enable'] = True

        self[sec].comments['Enable'].insert(0,
            'enable/disable all context menus'
        )
        self[sec]['ShowTitle'] = True
        self[sec]['TitleBackColour'] = CLR['GREY3']
        self[sec]['LeftClick'] = False
        self[sec].comments['LeftClick'].insert(0,
            'LeftClick: False=right click (default), supported: statusbar'
        )
        self[sec]['MenuBar'] = True
        self[sec].comments['MenuBar'].insert(0,
            'enable/disable context menu per listed window object:'
        )
        self[sec]['ToolBar'] = True
        self[sec]['InfoBar'] = True
        self[sec]['StatusBar'] = True
        self[sec]['PanelSwitcher'] = True
        self[sec]['SearchFlags'] = True
        self[sec]['FileEncoding'] = True
        self[sec]['EndOfLine'] = True
        self[sec]['Indentation'] = True
        self[sec]['Language'] = True
        self[sec]['Notebook'] = True
        self[sec]['Editor'] = True
        self[sec]['Margin'] = True
        self[sec]['Ruler'] = True
        self[sec]['CodeContext'] = True
        self[sec]['BookmarkList'] = True
        self[sec]['SymbolDef'] = True
        self[sec]['TaskList'] = True
        self[sec]['BreakpointList'] = True
        self[sec]['DocMap'] = True
        # self[sec]['SearchPanel'] = True
        self[sec]['SearchResults'] = True
        self[sec]['FindHistory'] = True
        self[sec]['ReplaceHistory'] = True
        self[sec]['WhereHistory'] = True
        self[sec]['WhereButton'] = True

        sec = 'Backup'
        self[sec] = {}
        # self[sec][NOT_IMPL+'Enable'] = True
        # self[sec][NOT_IMPL+'ToCurrentPath'] = False
        # self[sec][NOT_IMPL+'ToBackupPath'] = LOC['BKP']['PTH']
        # self[sec][NOT_IMPL+'AddFileExtension'] = True # = .bkp
        # self[sec][NOT_IMPL+'AddTimestamp'] = True     # = yyyymmdd-hhmmss
        # self[sec][NOT_IMPL+'AutoSave'] = False
        # self[sec][NOT_IMPL+'AutoSaveInterval'] = 'integer: seconds/minutes/...'

        sec = 'MenuBar'
        self[sec] = {}
        self[sec]['UseAltKeyAsToggle'] = False

        sec = 'ToolBar'
        self[sec] = {}
#NOTE, 1. self['Layout']['ToolBar'] = True       OR:
#NOTE, 2. self['ToolBar']['Enable'] = True
        # self[sec][NOT_IMPL+'Border'] = 'DEFAULT|NONE|RAISED|SIMPLE|STATIC|SUNKEN'
        self[sec]['Tools'] = [
            'SEP', 'NEW', 'OPN', 'SAV', 'SAS', 'CLS', 'SEP', 'CUT', 'CPY', 'PST', 'SEP',
            'UDO', 'RDO', 'SEP', 'FND', 'NXT', 'RPL', 'PRV', 'SEP', 'FXP', 'SDF',
            'SEP', 'BRC', 'SRT', 'SUM', 'SEP', 'FUL', 'SEP', 'PRF', 'SEP', 'SCH'
        ]
        self[sec]['BackColour'] = CLR['BLUE']
#FIX, 'TextFontSize': make list of 2 values and remove 'LargeTextFontSize'
        self[sec]['TextFontSize'] = 7
        self[sec]['LargeTextFontSize'] = 9
        self[sec]['ShowIcons'] = True
        self[sec]['ShowText'] = True
        self[sec]['LargeIcons'] = False
        self[sec]['LargeText'] = False
        self[sec]['AlignHorizontally'] = False
        self[sec]['Top'] = True
        self[sec]['Left'] = False
        self[sec]['Bottom'] = False
        self[sec]['Right'] = False

        sec = 'StatusBar'
        self[sec] = {}
#NOTE, 1. self['Layout']['StatusBar'] = True     OR:
#NOTE, 2. self['StatusBar']['Enable'] = True
        self[sec]['Fields'] = [
            'PSW', 'MSG', 'AUX', 'LNC', 'INS', 'CNS', 'SCH',
            'FSZ', 'ENC', 'EOL', 'IND', 'LNG', 'TIM'
        ]
        self[sec]['Border'] = True
        self[sec]['SizeGrip'] = True
        self[sec]['ToolTips'] = True
        self[sec]['BackColour'] = CLR['BLUE']
        self[sec]['ErrorBackColour'] = CLR['RED1']
        self[sec]['WarningBackColour'] = CLR['ORANGE']
        self[sec]['FullScreenBackColour'] = CLR['BLUE3']
        self[sec]['DelayClearFieldMSG'] = DELAY['MSG']
        self[sec].comments['DelayClearFieldMSG'].insert(0,
            'wait time (ms) before message field is cleared'
        )
        self[sec]['DelayClearFieldAUX'] = DELAY['AUX']
        self[sec].comments['DelayClearFieldAUX'].insert(0,
            'wait time (ms) before auxiliary field is cleared'
        )
        self[sec]['ClockTimeSeconds'] = False
        self[sec].comments['ClockTimeSeconds'].insert(0,
            'clock time format: False=HH:MM (default), True=HH:MM:SS'
        )
        self[sec]['ClockTimeColonBlink'] = False
        self[sec].comments['ClockTimeColonBlink'].insert(0,
            '2nd colon blinks every second: False=no blink (default)'
        )

        sec = 'InfoBar'
        self[sec] = {}
        self[sec]['CloseButton'] = False
        self[sec]['Position'] =  'TOP'  # TOP|BOTTOM
        self[sec]['ForeColour'] = '#0000FF'
        self[sec]['BackColour'] = CLR['BLUE3']
        self[sec]['WarningBackColour'] = '#FF6060'
        self[sec]['ErrorBackColour'] = '#FF0000'
        self[sec]['DelayHide'] = 2000
        self[sec]['Font'] = 'Consolas'
        self[sec]['FontSize'] = 11
        self[sec]['FontBold'] = False
        self[sec]['FontItalic'] = False

        sec = 'Indentation'
        self[sec] = {}
        self[sec]['Title'] = 'Indentation'
        self[sec]['TitleFontStyle'] = ['bold, large']
        self[sec]['TabIndents'] = True
        self[sec]['BackSpaceUnIndents'] = True
        self[sec]['UseTabs'] = False
        self[sec].comments['UseTabs'].insert(0,
            'UseTabs (indent using spaces or tabs): False=spaces (default), True=tabs'
        )
        self[sec]['TabWidth'] = 4
        self[sec]['Size'] = 4
        self[sec]['Auto'] = False
        self[sec]['Smart'] = False
        self[sec]['Guides'] = stc.STC_IV_NONE
        self[sec]['GuidesForeColour'] = '#FF0000'
        self[sec]['GuidesBackColour'] = '#FFFFFF'

        sec = 'Language'
        self[sec] = {}
        self[sec]['KeywordSetsAsSubMenu'] = True
        self[sec]['KeywordSetsInMenuBar'] = False
        # self[sec][NOT_IMPL+'Default'] = 'text'
        self[sec]['NewFile'] = 'TEXT'  # CURRENT|TEXT, CURRENT = active file's lang, TEXT = plain text
        self[sec]['ListRowColour'] = CLR['GREY1']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True

        sec = 'Splitter'
        self[sec] = {}
        self[sec]['Border'] = False
        self[sec]['LiveUpdate'] = False
        self[sec]['SashDoubleClickIsClose'] = True

#FIX, as this might overlap with ['PageTabs'] in ['Layout']
        sec = 'Notebook'
        self[sec] = {}
        # self[sec][NOT_IMPL+'Border'] = 'DEFAULT|NONE|RAISED|SIMPLE|STATIC|SUNKEN'
        self[sec]['BackgroundImage'] = False
        self[sec]['ArtProviderTheme'] = 'DEFAULT'    # DEFAULT|SIMPLE
        self[sec]['PageTabIconSize'] = 16  # pixels; square icon (width == height)
        self[sec]['ForeColour'] = '#FF0000'  # CLR['YELLOW']
        self[sec]['BackColour'] = CLR['YELLOW']
        self[sec]['TabColour'] = CLR['BLUE2']
        self[sec]['TabActiveColour'] = CLR['YELLOW']
        self[sec]['TabPosition'] = 'TOP'             # 'TOP'=AUI_NB_TOP, 'BOTTOM'=AUI_NB_BOTTOM
#NOTE, AUI_NB_DEFAULT_STYLE =
#          AUI_NB_TOP
#          AUI_NB_TAB_SPLIT
#          AUI_NB_TAB_MOVE
#          AUI_NB_SCROLL_BUTTONS
#          AUI_NB_CLOSE_ON_ACTIVE_TAB
#          AUI_NB_MIDDLE_CLICK_CLOSE
        self[sec]['TabDragSplit'] = True            # AUI_NB_TAB_SPLIT
        self[sec]['TabDragMove'] = True             # AUI_NB_TAB_MOVE
        self[sec]['TabCloseButton'] = False         # AUI_NB_CLOSE_BUTTON
        self[sec]['TabCloseButtonOnActive'] = True  # AUI_NB_CLOSE_ON_ACTIVE_TAB
        self[sec]['TabCloseButtonOnAll'] = True     # AUI_NB_CLOSE_ON_ALL_TABS
        self[sec]['TabScrollButtons'] = True        # AUI_NB_SCROLL_BUTTONS
        self[sec]['TabWindowListButton'] = True     # AUI_NB_WINDOWLIST_BUTTON
        self[sec]['TabFixedWidth'] = False          # AUI_NB_TAB_FIXED_WIDTH
        self[sec]['TabMiddleClickIsClose'] = True   # AUI_NB_MIDDLE_CLICK_CLOSE
        self[sec]['TabRightClickIsSelect'] = True
        self[sec]['TabToolTipFileInfo'] = 'FSM'     # F|P[STCMABL]
        self[sec].comments['TabToolTipFileInfo'].insert(0,
            'F|P=Filename|Pathname, S=Size, T=Type, C=Created, M=Modified, A=Accessed, B|L=key|description (Attributes)'
        )

        sec = 'PageTabHistory'
        self[sec] = {}
        self[sec]['Enable'] = True
        self[sec]['CacheSize'] = 10
        self[sec]['CacheSizeIncrease'] = 5
        self[sec]['CacheSizeDecrease'] = 5
        self[sec]['Stack'] = []

        sec = 'Editor'
        self[sec] = {}
        self[sec]['SelectionEOLFilled'] = False
        self[sec]['EOLMode'] = stc.STC_EOL_CRLF  # CRLF|CR|LF
        self[sec]['ZoomLevel'] = 0
        self[sec]['RevertConfirm'] = True
        self[sec]['DefaultBackColour'] = CLR['BLUE']
        self[sec]['TimestampFormat'] = TIM_FMT
        self[sec].comments['TimestampFormat'].insert(0,
            'For a complete list of formatting directives, see \'Format Codes\' in the Python manual'
        )
        self[sec].comments['TimestampFormat'].insert(1,
            'URL=https://docs.python.org/library/datetime.html#strftime-and-strptime-format-codes'
        )

        # self[sec]['NOT_IMPL+StutteredPage'] = False
        self[sec]['BufferedDraw'] = True
        self[sec]['Technology'] = stc.STC_TECHNOLOGY_DIRECTWRITE  # stc.STC_TECHNOLOGY_DEFAULT
        self[sec]['VirtualSpaceOptions'] = stc.STC_SCVS_RECTANGULARSELECTION
        self[sec]['HorizontalScrollBar'] = True
        self[sec]['VerticalScrollBar'] = True
        self[sec]['ScrollWidthTracking'] = True
        self[sec]['EndAtLastLine'] = True
        self[sec]['WhitespaceSize'] = 2
        self[sec].comments['WhitespaceSize'].insert(0,
            'WhitespaceSize (pixels), for dots that mark space chars: 2=default, [1-4]=size'
        )
        sec = 'MultiEdit'
        self[sec] = {}
        self[sec]['Selection'] = True
        self[sec]['Typing'] = True
        # self[sec]['MultiPaste'] = stc.STC_MULTIPASTE_EACH  # stc.STC_MULTIPASTE_ONCE
        self[sec]['SelForeColour'] = '#FFFFFF'
        self[sec]['SelBackColour'] = CLR['BLUE1']
        self[sec]['SelAlpha'] = 256  # integer: 0..256
        self[sec]['ExtraSelForeColour'] = '#FFFFFF'
        self[sec]['ExtraSelBackColour'] = CLR['BLUE1']
        self[sec]['ExtraSelAlpha'] = 256  # integer: 0..256
        self[sec]['ExtraCaretForeColour'] = '#0000FF'
        self[sec]['ExtraCaretsBlink'] = True
        self[sec]['ExtraCaretsVisible'] = True
        self[sec]['Clipboard'] = False

        sec = 'Caret'
        self[sec] = {}
        self[sec]['ForeColour'] = '#0000FF'
        self[sec]['HomeEndKeysBRIEF'] = False
        self[sec]['LineVisible'] = True
        self[sec]['LineBackColour'] = CLR['YELLOW']
        self[sec]['LineBackAlpha'] = 256  # integer: 0..256
        self[sec]['Sticky'] = stc.STC_CARETSTICKY_ON
        self[sec]['Period'] = 500
        self[sec].comments['Period'].insert(0,
            'Period or blink rate (ms): 500=default, 0=no blink'
        )
        self[sec]['Style'] = stc.STC_CARETSTYLE_LINE
        self[sec]['Width'] = 2
        self[sec].comments['Width'].insert(0,
            'Width (pixels): 2=default, [1-3] visible, 0=invisible'
        )

        sec = 'CaretPositionHistory'
        self[sec] = {}
        self[sec]['Enable'] = True
        self[sec]['MaxItems'] = 300
        self[sec]['DelayDefaultStyle'] = 500
        self[sec].comments['DelayDefaultStyle'].insert(0,
            'These caret settings are used when jumping through history'
        )
        self[sec]['ForeColour'] = '#00FF00'
        self[sec]['Period'] = 250
        self[sec]['Style'] = 1
        self[sec]['Width'] = 3

        sec = 'Margin'
        self[sec] = {}
#FIX, use 'update_margins' to derive 'All' value
        # self[sec]['All'] = True
        self[sec]['LineNumber'] = True
        self[sec]['LineNumberWidth'] = 50
        self[sec]['LineNumberForeColour'] = '#000000'
        self[sec]['LineNumberBackColour'] = CLR['GREY1']
        self[sec]['Symbol'] = True
        self[sec]['SymbolWidth'] = 16
        self[sec]['Folding'] = True
        self[sec]['FoldingWidth'] = 16
        self[sec]['FoldingColour'] = CLR['GREY1']
        self[sec]['FoldingHiColour'] = CLR['GREY1']
        self[sec]['FoldingStyle'] = FOL_STYLE
        self[sec]['FoldingHighlight'] = False
        self[sec]['LeftWidth'] = 0
        self[sec].comments['LeftWidth'].insert(0,
            'Left/RightWidth (pixels): default=0, [1-n]=visible, 0=invisible'
        )
        self[sec]['RightWidth'] = 0

        sec = 'Edge'
        self[sec] = {}
        self[sec]['Mode'] = stc.STC_EDGE_NONE
        self[sec]['Column'] = 79
        self[sec]['Colour'] = '#006400'

        sec = 'Debugger'
        self[sec] = {}
        self[sec]['LineBackColour'] = '#A020F0'
        self[sec]['LineBackAlpha'] = 150
        self[sec]['CentreCaret'] = False

        sec = 'AutoComplete'
        self[sec] = {}
        self[sec]['Enable'] = False
        self[sec]['MaxHeight'] = 5
        self[sec].comments['MaxHeight'].insert(0,
            'MaxHeight (rows): 5=default; MaxWidth (chars): 0=default (autosize)'
        )
        self[sec]['MaxWidth'] = 0
        # self[sec][NOT_IMPL+'AutoHide'] = 'autoHide (bool)'
        # self[sec][NOT_IMPL+'CancelAtStart'] = 'cancel (bool)'
        # self[sec][NOT_IMPL+'CaseInsensitiveBehaviour'] = 'behaviour (int)'
        # self[sec][NOT_IMPL+'ChooseSingle'] = 'chooseSingle (bool)'
        # self[sec][NOT_IMPL+'DropRestOfWord'] = 'dropRestOfWord (bool)'
        # self[sec][NOT_IMPL+'FillUps'] = 'characterSet (string)'
        # self[sec][NOT_IMPL+'IgnoreCase'] = 'ignoreCase (bool)'
        # self[sec][NOT_IMPL+'Separator'] = 'separatorCharacter (int)'
        # self[sec][NOT_IMPL+'TypeSeparator'] = 'separatorCharacter (int)'
        # self[sec][NOT_IMPL+'Stops'] = 'characterSet (string)'

        sec = 'Brace'
        self[sec] = {}
        self[sec]['Enable'] = True
        self[sec]['AutoInsert'] = True
        self[sec]['Pairs'] = '''([{<'")]}>'"'''  # '()[]{}<>'
        self[sec]['LightForeColour'] = '#000000'
        self[sec]['LightBackColour'] = '#00FF00'
        self[sec]['BadForeColour'] = '#000000'
        self[sec]['BadBackColour'] = '#FF0000'
        # self[sec][NOT_IMPL+'HighlightIndicator'] = '(integer: indicator)'
        # self[sec][NOT_IMPL+'BadlightIndicator'] = '(integer: indicator)'

        sec = 'Indicator'
        self[sec] = {}
        self[sec]['Enable'] = True
        self[sec]['MatchSelection'] = True
        self[sec].comments['MatchSelection'].insert(0,
            'MatchSelection: highlight other occurrences of currently selected word'
        )
        self[sec]['BackColour0'] = '#00FF00'
        self[sec]['BackColour1'] = '#9BFFFF'
        self[sec].comments['BackColour1'].insert(0,
            'BackColour1-5: mark colours for styles 1 to 5'
        )
        self[sec]['BackColour2'] = '#FFCD9B'
        self[sec]['BackColour3'] = '#FFFF9B'
        self[sec]['BackColour4'] = '#CD9BFF'
        self[sec]['BackColour5'] = '#9BCD9B'
        self[sec]['OutlineAlpha'] = 255
        self[sec]['Alpha'] = 125
        self[sec]['Style'] = stc.STC_INDIC_BOX
        self[sec]['DrawUnder'] = True

        sec = 'CallTip'
        self[sec] = {}
        self[sec]['Enable'] = False
        self[sec]['ForeColour'] = '#0000FF'
        self[sec]['BackColour'] = CLR['BLUE']
#INFO, URL=http://www.scintilla.org/ScintillaDoc.html#CallTips
        # self[sec][NOT_IMPL+'ForeHighlightColour'] = TXT_NIL
        # self[sec][NOT_IMPL+'Position'] = 'ABOVE|BELOW'
        self[sec]['DelayShow'] = DELAY['CTP']  # MouseDwellTime

        sec = 'Hotspot'
        self[sec] = {}
        self[sec]['ForeColour'] = '#0000FF'
        self[sec]['BackColour'] = CLR['BLUE']
        self[sec]['Underline'] = True
        self[sec]['SingleLine'] = True

        # sec = 'IntelliSense'
        # self[sec] = {}
        # self[sec][NOT_IMPL+'Enable'] = True

        sec = 'KeyBinding'
        self[sec] = {}
        # self[sec][NOT_IMPL+'Enable'] = False

        sec = 'MultiView'
        self[sec] = {}
        # self[sec][NOT_IMPL+'Enable'] = False

        sec = 'ToolTip'
        self[sec] = {}
        self[sec]['MaxWidth'] = -1  # -1: no wrap, 0: default, >=1: custom width
        self[sec]['DelayShow'] = DELAY['TTS']
        self[sec]['DelayHide'] = DELAY['TTH']
        self[sec]['DelayReshow'] = DELAY['TTR']

        sec = 'GotoAnything'
        self[sec] = {}
        self[sec]['FuzzySearch'] = True
        self[sec]['BackColour'] = CLR['BLUE1']
        self[sec]['PositionY'] = 0
        self[sec]['TextCtrlBackColour'] = CLR['BLUE2']
        self[sec]['ListBoxBackColour'] = CLR['BLUE2']
        self[sec]['ListBoxSelBackColour'] = CLR['BLUE3']
        self[sec]['BorderWidth'] = 2
        self[sec]['DropShadow'] = False
        self[sec]['Font'] = 'Consolas'
        self[sec]['FontSize'] = 11
        self[sec]['FontBold'] = True

        sec = 'SymbolBrowser'
        self[sec] = {}
        self[sec]['FuzzySearch'] = True
        self[sec]['BackColour'] = CLR['BLUE1']
        self[sec]['PositionY'] = 0
        self[sec]['TextCtrlBackColour'] = CLR['BLUE2']
        self[sec]['ListBoxBackColour'] = CLR['BLUE2']
        self[sec]['ListBoxSelBackColour'] = CLR['BLUE3']
        self[sec]['ClassBackColour'] = CLR['YELLOW2']
        self[sec]['MemberBackColour'] = CLR['BLUE3']
        self[sec]['FunctionBackColour'] = CLR['RED2']
        self[sec]['BorderWidth'] = 2
        self[sec]['DropShadow'] = False
        self[sec]['Font'] = 'Consolas'
        self[sec]['FontSize'] = 11
        self[sec]['FontBold'] = True

        sec = 'SymbolIndex'
        self[sec] = {}
        self[sec]['Enable'] = True
        self[sec]['IncludeDFN'] = True
        self[sec]['IncludeREF'] = True
        self[sec]['IncludeIMP'] = True
        self[sec]['IncludeVAR'] = True
        self[sec]['IncludeWRD'] = True
        self[sec]['IncludeQTS'] = True

        sec = 'SymbolPopup'
        self[sec] = {}
        self[sec]['Enable'] = True
        self[sec]['NeedCtrlKey'] = True
        self[sec]['CallablesOnly'] = True
        self[sec]['DropShadow'] = True
        self[sec]['DelayShow'] = DELAY['SPS']
        self[sec]['PanelBackColour'] = '#71B3E8'
        self[sec]['ShowSymbol'] = True
        self[sec]['SymbolFont'] = 'Arial Rounded MT Bold'
        self[sec]['SymbolForeColour'] = '#0000FF'
        self[sec]['SymbolBackColour'] = '#F0F0F0'
        self[sec]['ShowSymbolType'] = True
        self[sec]['SymbolTypeFont'] = 'Arial Rounded MT Bold'
        self[sec]['SymbolTypeForeColour'] = '#FFFFFF'
        self[sec]['HyperlinkFont'] = 'Consolas'
        self[sec]['CentreCaret'] = True

        sec = 'SymbolPreview'
        self[sec] = {}
        self[sec]['Enable'] = False
        self[sec]['Caption'] = False
        self[sec]['Border'] = False
        self[sec]['BorderWidth'] = 2
        self[sec]['BorderColour'] = '#3399FF'
        self[sec]['DropShadow'] = False
        self[sec]['CentreCaret'] = True
        self[sec]['Margin'] = False
        self[sec]['Width'] = 99
        self[sec]['Height'] = 11

        sec = 'ColourToolTip'
        self[sec] = {}
        self[sec]['Enable'] = True
        self[sec]['Width'] = 100
        self[sec]['Height'] = 75
        self[sec]['RectRounded'] = True
        self[sec]['RectRoundedRadius'] = 5
        self[sec]['RectLineColour'] = '#000000'
        self[sec]['RectLineWidth'] = 5
        self[sec]['ShowHex'] = False
        self[sec]['ShowName'] = True
        self[sec]['ShowDec'] = False
        self[sec]['DelayShow'] = DELAY['CTS']
        self[sec]['DelayHide'] = DELAY['CTH']

        sec = 'TopLineToolTip'
        self[sec] = {}
        self[sec]['Enable'] = True
        # self[sec][NOT_IMPL+'Border'] = 'DEFAULT|NONE|RAISED|SIMPLE|STATIC|SUNKEN'
        self[sec]['ForeColour'] = '#0000FF'
        self[sec]['BackColour'] = CLR['BLUE2']
        self[sec]['UseFade'] = False
        self[sec]['DropShadow'] = False
        # self[sec][NOT_IMPL+'Position'] = 'TL|TR|BL|BR'  # Top, Left, Bottom, Right
        self[sec]['Text'] = 'Top Line\r\n<hr>\r\nDocument  %7d\r\nDisplay   %7d\r\n\r\nLeft Col  %7d\r\n'
        self[sec].comments['Text'].insert(0,
            'at start of line: <hr>=Horizontal Rule, </b>=Bold, </l>=hyperLink'
        )
        self[sec]['DelayHide'] = DELAY['TLH']
        # self[sec]['LeftColText'] = ' Left Col: %7d \n'

        sec = 'Layout'
        self[sec] = {}
        self[sec]['Caption'] = True
        self[sec]['MenuBar'] = True
        self[sec]['ToolBar'] = True
        self[sec]['InfoBar'] = True
        self[sec]['StatusBar'] = True
        self[sec]['MenuIcons'] = False
        self[sec]['MenuIconsCustomCheckable'] = False
        self[sec]['MenuIconSize'] = 16
        self[sec]['MenuHelpText'] = True
        self[sec]['PageTabs'] = True
        self[sec]['PageTabTheme'] = True
        self[sec]['PageTabIcons'] = True
        self[sec]['ToolTips'] = True
        self[sec]['FullScreen'] = False
        self[sec]['DistractionFree'] = False
        # self[sec][NOT_IMPL+'MenuItemHelp'] = True  # statusbar: toggle short menu help visibility
        # self[sec].comments[NOT_IMPL+'MenuItemHelp'].insert(0,
        #     'short help text for selected menu item in statusbar'
        # )

        sec = 'PanelEffect'
        self[sec] = {}
        self[sec]['Enable'] = False
        self[sec]['Duration'] = 200
        self[sec].comments['Duration'].insert(0,
            'Animation duration (ms): 200=default, 0=current platform\'s default'
        )
        self[sec]['Choice'] = wx.SHOW_EFFECT_NONE

        sec = 'Ruler'
        self[sec] = {}                        # rlr
        self[sec]['Enable'] = False
        self[sec]['Swap'] = False
        self[sec]['SashPos'] = SASH_POS['RLR']
        self[sec]['LineBottom'] = True
        self[sec]['LineColour'] = '#006400'
        self[sec]['BackColour'] = CLR['BLUE2']
        self[sec]['TickLeftHeight'] = 25
        self[sec]['TickLeftColour'] = '#A9A9A9'
        self[sec]['TickMaxHeight'] = 9
        self[sec].comments['TickMaxHeight'].insert(0,
            'TickMaxHeight (pixels): 9=default, [1-18]=visible, 0=invisible'
        )
#FIX, create 'TickColour': make list of 3 values and remove '[Large|medium|small]TickColour'
        self[sec]['TickLargeColour'] = '#FFFF00'
        self[sec]['TickMediumColour'] = '#0000FF'
        self[sec]['TickSmallColour'] = '#A9A9A9'
        self[sec]['TextFontSize'] = 10
        self[sec].comments['TextFontSize'].insert(0,
            'TextFontSize (pixels): 10=default, [8-18]=visible, 0=invisible'
        )
        self[sec]['TextColour'] = '#0000FF'
        self[sec]['CaretColour'] = '#0000FF'
        self[sec]['CaretType'] = 'TRIANGLE_SMALL'  # TRIANGLE|BLOCK|LINE[_SMALL]

        sec = 'SidePanel'
        self[sec] = {}                    # spn
        self[sec]['Enable'] = False
        self[sec]['Swap'] = False
        # self[sec][NOT_IMPL+'BackColour'] = TXT_NIL
        # self[sec][NOT_IMPL+'ForeColour'] = TXT_NIL
        self[sec]['SashPos'] = SASH_POS['SPN']
        self[sec]['Choice'] = SPT.DOC.idx
        self[sec]['ListFilterBackColour'] = CLR['BLUE2']
        self[sec]['ListCtrlIsVirtual'] = False

#TODO, naming: use 'SidePanelTool' or section per 'tool'
        sec = 'SidePanelTool'
        self[sec] = {}
        # self[sec][NOT_IMPL+'Border'] = 'DEFAULT|NONE|RAISED|SIMPLE|STATIC|SUNKEN'
        # self[sec][NOT_IMPL+'BackColour'] = TXT_NIL
        # self[sec][NOT_IMPL+'ForeColour'] = TXT_NIL

        sec = 'Filter'
        self[sec] = {}
        self[sec]['Document'] = TXT_NIL
        self[sec]['Bookmark'] = TXT_NIL
        # self[sec]['Explorer'] = TXT_NIL
        # self[sec]['Symbol'] = TXT_NIL
        self[sec]['Macro'] = TXT_NIL
        self[sec]['Task'] = TXT_NIL
        self[sec]['Breakpoint'] = TXT_NIL
        self[sec]['Debug'] = TXT_NIL
        # self[sec]['DocMap'] = TXT_NIL
        self[sec]['Config'] = TXT_NIL
        self[sec]['Help'] = TXT_NIL
        self[sec]['Pylint'] = TXT_NIL
        self[sec]['Pyflakes'] = TXT_NIL
        self[sec]['Pycodestyle'] = TXT_NIL
        self[sec]['Vulture'] = TXT_NIL

        sec = 'Document'
        self[sec] = {}
        self[sec]['ListRowColour'] = CLR['BLUE']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True

        sec = 'Project'
        self[sec] = {}

        sec = 'Bookmark'
        self[sec] = {}
        self[sec]['Symbol'] = MRK['BMK']['SYM']
        self[sec]['OuterColour'] = '#0000FF'  # CLR['BLUE2']
        self[sec]['InnerColour'] = '#0000FF'  # GREEN
        self[sec]['ListRowColour'] = CLR['BLUE2']
        self[sec]['ListRowAltColour'] = CLR['GREEN2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        self[sec]['SearchWrap'] = False
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self[sec]['ShowPanel'] = False
        self[sec].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self[sec]['SyncPanel'] = False
        self[sec].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        sec = 'Explorer'
        self[sec] = {}

        sec = 'SymbolDef'
        self[sec] = {}
        self[sec]['ShowIcons'] = True
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )

        sec = 'Macro'
        self[sec] = {}
#TODO, maybe toggle 'Macro' menu visibility
        # self[sec][NOT_IMPL+'Enable'] = True
        self[sec]['ListRowColour'] = CLR['GREEN']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True

        sec = 'Task'
        self[sec] = {}
        self[sec]['Symbol'] = MRK['TSK']['SYM']
        self[sec]['ShowMarker'] = False
        self[sec]['OuterColour'] = '#FF0000'
        self[sec]['InnerColour'] = '#FF0000'
        self[sec]['ListRowColour'] = CLR['GREEN']
        self[sec]['ListRowAltColour'] = CLR['GREEN2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        self[sec]['SearchWrap'] = False
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self[sec]['ShowPanel'] = False
        self[sec].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self[sec]['SyncPanel'] = False
        self[sec].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        sec = 'Breakpoint'
        self[sec] = {}
        self[sec]['Symbol'] = MRK['BPT']['SYM']
        self[sec]['OuterColour'] = '#FFFF00'
        self[sec]['InnerColour'] = '#FFFF00'
        self[sec]['ListRowColour'] = CLR['PURPLE']
        self[sec]['ListRowAltColour'] = CLR['GREEN2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        self[sec]['SearchWrap'] = False
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self[sec]['ShowPanel'] = False
        self[sec].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self[sec]['SyncPanel'] = False
        self[sec].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        sec = 'Debug'
        self[sec] = {}
        self[sec]['ListRowColour'] = CLR['YELLOW']
        self[sec]['ListRowAltColour'] = CLR['ORANGE']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True

        sec = 'Config'
        self[sec] = {}
        self[sec]['SectionSelBackColour'] = '#0000FF'
        self[sec]['KeySelBackColour'] = '#A020F0'
        self[sec]['ListRowColour'] = CLR['GREY1']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )

        sec = 'Environment'
        self[sec] = {}
        self[sec]['QuestionMarkButton'] = False
        self[sec]['ContextSensitiveMode'] = False
        self[sec]['CheckForUpdates'] = False
        self[sec]['ListRowColour'] = '#EDFFC6'
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True

        sec = 'Help'
        self[sec] = {}
        self[sec]['QuestionMarkButton'] = False
        self[sec]['ContextSensitiveMode'] = False
        self[sec]['CheckForUpdates'] = False
        self[sec]['ListRowColour'] = CLR['ORANGE2']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True

        sec = 'Pylint'
        self[sec] = {}
        # self[sec]['Symbol'] = MRK['BPT']['SYM']
        # self[sec]['OuterColour'] = '#FFFF00'
        # self[sec]['InnerColour'] = '#FFFF00'
        self[sec]['ListRowColour'] = CLR['GREY1']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        # self[sec]['SearchWrap'] = False
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self[sec]['ShowPanel'] = False
        self[sec].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self[sec]['SyncPanel'] = False
        self[sec].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        sec = 'Pyflakes'
        self[sec] = {}
        # self[sec]['Symbol'] = MRK['BPT']['SYM']
        # self[sec]['OuterColour'] = '#FFFF00'
        # self[sec]['InnerColour'] = '#FFFF00'
        self[sec]['ListRowColour'] = CLR['GREY1']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        # self[sec]['SearchWrap'] = False
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self[sec]['ShowPanel'] = False
        self[sec].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self[sec]['SyncPanel'] = False
        self[sec].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        sec = 'Pycodestyle'
        self[sec] = {}
        # self[sec]['Symbol'] = MRK['BPT']['SYM']
        # self[sec]['OuterColour'] = '#FFFF00'
        # self[sec]['InnerColour'] = '#FFFF00'
        self[sec]['ListRowColour'] = CLR['GREY1']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        # self[sec]['SearchWrap'] = False
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self[sec]['ShowPanel'] = False
        self[sec].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self[sec]['SyncPanel'] = False
        self[sec].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        sec = 'Vulture'
        self[sec] = {}
        # self[sec]['Symbol'] = MRK['BPT']['SYM']
        # self[sec]['OuterColour'] = '#FFFF00'
        # self[sec]['InnerColour'] = '#FFFF00'
        self[sec]['ListRowColour'] = CLR['GREY1']
        self[sec]['ListRowAltColour'] = CLR['BLUE2']
        self[sec]['HoverSelect'] = False
        self[sec]['NeedCtrlKey'] = True
        self[sec]['SingleClick'] = True
        # self[sec]['SearchWrap'] = False
        self[sec]['CentreCaret'] = False
        self[sec].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self[sec]['ShowPanel'] = False
        self[sec].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self[sec]['SyncPanel'] = False
        self[sec].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        sec = 'Markdown'
        self[sec] = {}

        sec = 'Diagrams'
        self[sec] = {}

        sec = 'Code2flow'
        self[sec] = {}

        sec = 'Snippet'
        self[sec] = {}

        sec = 'CodeContext'
        self[sec] = {}                  # ccx
        self[sec]['Enable'] = False
        self[sec]['Swap'] = False
        self[sec]['SashPos'] = SASH_POS['CCX']
        self[sec]['ForeColour'] = '#000000'
        self[sec]['BackColour'] = CLR['BLUE']
        self[sec]['Font'] = 'Courier New'
        self[sec]['Depth'] = 10  # number of lines, level

        sec = 'SearchPanel'
        self[sec] = {}                  # sch
        self[sec]['Enable'] = False
        self[sec]['Swap'] = False
        self[sec]['SashPos'] = SASH_POS['SCH']['FND']
        self[sec]['Mode'] = 'FND'
        self[sec]['HasFocus'] = False
        self[sec]['IconSize'] = 24  # 16 x 16 | 24 x 24 | 32 x 32
        self[sec].comments['IconSize'].insert(0,
            'IconSize (pixels), sizes 16x16|24x24|32x32: 16=small, 24=medium (default), 32=large'
        )
        self[sec]['LabelFontStyle'] = 'bold'
        self[sec].comments['LabelFontStyle'].insert(0,
            'LabelFontStyle: bold (default), see \'LBL_FNT_STYLES\': any combination of bold|italic|large|small|strike|underline'
        )
        self[sec]['TabTraversalAll'] = False
        self[sec]['BackColourFND'] = CLR['BLUE']
        self[sec]['BackColourRPL'] = CLR['RED']
        self[sec]['BackColourFIF'] = CLR['ORANGE']
        self[sec]['BackColourINC'] = CLR['BLUE2']
        self[sec]['BackColourRES'] = '#000000'
        self[sec]['WarningBackColour'] = CLR['RED3']
        self[sec]['ErrorBackColour'] = CLR['RED1']
        self[sec]['DelayDefaultColour'] = 1000
        self[sec]['Border'] = False
        self[sec]['FindText'] = TXT_NIL
        self[sec]['WhereText'] = TXT_NIL
        self[sec]['ReplaceText'] = TXT_NIL
        # self[sec][NOT_IMPL+'IncrementalText'] = TXT_NIL
        self[sec]['SelectedTextToFind'] = True
        self[sec]['ShowCheckboxes'] = True
        self[sec]['ShowCountButton'] = False
        self[sec]['ShowIcons'] = True
        self[sec]['CaseSensitive'] = False
        self[sec]['RegularExpression'] = False
        self[sec]['WholeWord'] = False
        self[sec]['WrapAround'] = False
        self[sec]['InSelection'] = False
        self[sec]['HighlightMatches'] = False
        self[sec]['PreserveCase'] = False
        self[sec]['ShowContext'] = False
        self[sec]['UseBuffer'] = False
        # self[sec][NOT_IMPL+'CentreFoundLine'] = True
        # self[sec][NOT_IMPL+'CentreFoundColumn'] = True

#TODO, naming: use 'SidePanelTool' or section per 'tool'
        sec = 'DocMap'
        self[sec] = {}
        self[sec]['ZoneRectRounded'] = False
        self[sec]['ZoneRectRoundedRadius'] = 5
        self[sec]['ZoneRectLineColour'] = CLR['BLUE6']
        self[sec]['ZoneRectLineStyle'] = wx.PENSTYLE_SOLID
        self[sec]['ZoneRectLineWidth'] = 1

        self[sec]['ZoneFillColour'] = CLR['ORANGE']
        self[sec]['ZoneFillAlpha'] = 64

        self[sec]['ZoneCentreLine'] = True
        self[sec]['ZoneCentreLineColour'] = '#FF0000'
        self[sec]['ZoneCentreLineStyle'] = wx.PENSTYLE_DOT
        self[sec]['ZoneCentreLineWidth'] = 1

        self[sec]['ZoneCentreDot'] = True
        self[sec]['ZoneCentreDotColour'] = '#0000FF'
        self[sec]['ZoneCentreDotRadius'] = 2

        # self[sec]['ScrollNumLinesWheel'] = 10
        # self[sec]['ScrollNumLinesEdge'] = 25
        # self[sec]['ScrollFactorWheel'] = 11  # higher value: finer wheel scroll whilst nearing edge

        self[sec]['EdgeTextIndicator'] = True
        self[sec]['EdgeTextTop'] = ' [ Top ] '
        self[sec]['EdgeTextBottom'] = ' [ Bottom ] '
        self[sec]['EdgeTextFont'] = 'Courier New'
        self[sec]['EdgeTextFontSize'] = 10
        self[sec]['EdgeTextForeColour'] = '#0000FF'
        self[sec]['EdgeTextBackColour'] = CLR['ORANGE3']
        # self[sec][NOT_IMPL+'EdgeTextPosition'] = 'TL|TR|BL|BR'  # Top, Left, Bottom, Right

#DONE, add code for 'Cursor' and 'ToolTip' properties in 'sidepanel.py'
        # self[sec]['CursorTypeNormal'] = wx.CURSOR_ARROW
        # self[sec]['CursorTypeHover'] = wx.CURSOR_SIZENS
        # self[sec]['CursorTypeDrag'] = wx.CURSOR_HAND
        # self[sec]['CursorTypeScroll'] = wx.CURSOR_WAIT
        # self[sec]['CursorTypeEdge'] = wx.CURSOR_NO_ENTRY

        # self[sec]['CursorTypeHoverShow'] = True
        # self[sec]['CursorTypeDragShow'] = True

        # self[sec]['ToolTipHoverShow'] = True
        # self[sec]['ToolTipDragShow'] = True  # naming: ['TopLineToolTip']?

#TODO, add code END #####
        self[sec]['AutoFocus'] = True
        self[sec]['MarkerLineHighlight'] = False
#INFO, URL=https://wxpython.org/Phoenix/docs/html/wx.RasterOperationMode.enumeration.html
        # self[sec]['RasterOperationMode'] = wx.AND  # wx.INVERT
        self[sec]['SnapCursorAtDragStart'] = True

        # add blank line BEFORE each key below; for readability
        key_lst = (
            'ZoneFillColour', 'ZoneCentreLine', 'ZoneCentreDot',
            # 'ScrollNumLinesWheel',
            'EdgeTextIndicator',
            # 'CursorTypeNormal',
            # 'CursorTypeHoverShow',
            # 'ToolTipHoverShow',
            'AutoFocus',
        )
        for key in key_lst:
            self['DocMap'].comments[key].append(TXT_NIL)

        sec = 'CodePreview'
        self[sec] = {}
        self[sec]['Enable'] = False
        self[sec]['Caption'] = False
        self[sec]['Border'] = False
        self[sec]['BorderWidth'] = 2
        self[sec]['BorderColour'] = CLR['BLUE1']
        self[sec]['DropShadow'] = False
        self[sec]['Margin'] = False
        self[sec]['Width'] = 0.8
        self[sec]['Height'] = 10
        self[sec]['ShowOverZone'] = False

    def create(self):
        # from conf.debug import DBG, DEBUG
        DBG('CFG', f'{me_()}\n  File = {self.filename}\n')

        # get default configuration
        self.default()

        # add blank lines and header before all sections, except the first
        first_sec = 'General'
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Comment header for %s' % sec)

        self.save()

    def load(self):
        # from conf.debug import DBG, DEBUG
        DBG('CFG', f'{me_()}\n  File = {self.filename}\n')

        # convert option data type: string -> boolean/float/int/list
        for sec in self:
            for key in self[sec]:
                val = self[sec][key]  # convenient short naming (val)
                if is_bool(val):
                    val = self[sec].as_bool(key)
                elif is_float(val):
                    val = self[sec].as_float(key)
                elif is_int(val):
                    val = self[sec].as_int(key)
                elif is_list(val):
                    val = self[sec].as_list(key)
                elif is_str(val):
                    pass
                else:
                    # unexpected data type
                    err = f'{self.__class__.__name__}: unexpected type [{type(val).__name__}] for value [{val[:15]} ...]'
                    raise TypeError(err)
                self[sec][key] = val  # convenient short naming (val)

        # create list of last session's open files
        if self['General']['OpenSession']:
            sec = 'Session'
            cnt = 0
            while True:
                key = f'File{cnt}'
                if key in glb.SSN[sec]:
                    pnm, vis, pos, lin, col, lng, wrp, eol, wsp, tbu, tbw, ofs, sel_str, bmk_str, bpt_str = glb.SSN[sec][key].split('|')
                    sel_lst = literal_eval(sel_str)  # string -> tuple
                    bmk_lst = literal_eval(bmk_str)  # string -> list
                    bpt_lst = literal_eval(bpt_str)  # string -> list
                    self.fil_lst.append([pnm, vis, pos, lin, col, lng, wrp, eol, wsp, tbu, tbw, ofs, sel_lst, bmk_lst, bpt_lst])
                else:
                    break
                cnt += 1
            DBG('CFG', '\n    fil_lst = %s\n' % self.fil_lst)
        else:
            for sec in {'SearchPanel', 'Ruler', 'SidePanel', 'CodeContext'}:
                self[sec]['Enable'] = False

        # create list of last session's recent files
        if glb.RFH['RecentFileHistory']['Enable']:
            sec = 'RecentFiles'
            cnt = 0
            while True:
                key = f'File{cnt}'
                if key in glb.RFH[sec]:
                    pnm = glb.RFH[sec][key]
                    self.rfh_lst.append(pnm)
                else:
                    break
                cnt += 1
            DBG('CFG', '\n  rfh_lst = %s\n' % self.rfh_lst)

#FIX, not used: obsolete/redundant?
    def save(self):
        # from conf.debug import DBG, DEBUG
        DBG('CFG', f'{me_()}\n  File = {self.filename}\n')
        if DEBUG['CFG'] > 1: beeprint.pp(self, sort_keys=False)
        self.write()

    def apply(self):
        # convenience: use locals from GLOBALS
        tlw, spl, mbr, tbr, ibr, sbr, nbk, spn, sch = \
            glb.TLW, glb.SPL, glb.MBR, glb.TBR, glb.IBR, glb.SBR, glb.NBK, glb.SPN, glb.SCH

        DBG('APP==2', f'CFG: {glb.APP.ready = }')

        tlw.Freeze()

        DBG('CFG', f'{me_()}')
        if DEBUG['CFG'] > 1: beeprint.pp(self, sort_keys=False)

        # restore main menu item check marks:
        # - toolbar, statusbar, panels, page tabs, tooltips, full screen
        mbr.Check(MI['LAY_CAP'], self['Layout']['Caption'])
        mbr.Check(MI['LAY_MBR'], self['Layout']['MenuBar'])
        mbr.Check(MI['LAY_TBR'], self['Layout']['ToolBar'])
        mbr.Check(MI['LAY_IBR'], self['Layout']['InfoBar'])
        mbr.Check(MI['LAY_SBR'], self['Layout']['StatusBar'])
        mbr.Check(MI['LAY_SCH'], self['SearchPanel']['Enable'])
        mbr.Check(MI['LAY_RLR'], self['Ruler']['Enable'])
        mbr.Check(MI['LAY_SPN'], self['SidePanel']['Enable'])
        mbr.Check(MI['LAY_CCX'], self['CodeContext']['Enable'])
        # chc = int(MI['PEF_NON']) + self['PanelEffect']['Choice']
        # mbr.Check(chc, True)
        mbr.Check(MI['LAY_MIC'], self['Layout']['MenuIcons'])
        mbr.Check(MI['LAY_MIK'], self['Layout']['MenuIconsCustomCheckable'])

        # restore menu icon size
        isz = self['Layout']['MenuIconSize']
        mbr.Check(MI[f'LAY_I{isz}'], True)

        mbr.Check(MI['LAY_MHT'], self['Layout']['MenuHelpText'])
        mbr.Check(MI['LAY_PTB'], self['Layout']['PageTabs'])  # , nbk.TabCtrlHeight)
        nbk.SetTabCtrlHeight(-1 if mbr.IsChecked(MI['LAY_PTB']) else 0)
        mbr.Check(MI['LAY_PTT'], self['Layout']['PageTabTheme'])
        mbr.Check(MI['LAY_PTI'], self['Layout']['PageTabIcons'])
        mbr.Check(MI['LAY_TTP'], self['Layout']['ToolTips'])
        mbr.Check(MI['LAY_ACP'], self['AutoComplete']['Enable'])
        mbr.Check(MI['LAY_CTP'], self['CallTip']['Enable'])
        mbr.Check(MI['LAY_TLT'], self['TopLineToolTip']['Enable'])
        nbk.tlt.EnableTip(bool(mbr.IsChecked(MI['LAY_TLT'])))
        mbr.Check(MI['LAY_CTT'], self['ColourToolTip']['Enable'])
        mbr.Check(MI['LAY_SPU'], self['SymbolPopup']['Enable'])
        mbr.Check(MI['LAY_FUL'], self['Layout']['FullScreen'])

        # restore margins
#FIX, use 'update_margins' to derive 'All' value
    #     mbr.Check(MI['MGN_ALL'], self['Margin']['All'])
        mbr.Check(MI['MGN_NUM'], self['Margin']['LineNumber'])
        mbr.Check(MI['MGN_SYM'], self['Margin']['Symbol'])
        mbr.Check(MI['MGN_FOL'], self['Margin']['Folding'])
        update_margins()
#TODO, add fold_style to 3 docstate methods, FOR NOW it is GLOBAL
        self['Margin']['FoldingStyle'] = FOL_STYLE

        # restore edge
        val = self['Edge']['Mode']
        if val == stc.STC_EDGE_NONE:
            mbr.Check(MI['EDG_NON'], True)
        elif val == stc.STC_EDGE_BACKGROUND:
            mbr.Check(MI['EDG_BCK'], True)
        elif val == stc.STC_EDGE_LINE:
            mbr.Check(MI['EDG_LIN'], True)
        # elif val == 3:
        # # elif val == stc.STC_EDGE_MULTILINE:
        #     mbr.Check(MI['EDG_MUL'], True)
        # doc.SetEdgeMode(val)

        # restore indentation guides
        val = self['Indentation']['Guides']
        if val == stc.STC_IV_LOOKBOTH:
            mbr.Check(MI['IND_GDS'], True)
        else:
            mbr.Check(MI['IND_GDS'], False)

        # restore scrollbars
        hor = self['Editor']['HorizontalScrollBar']
        ver = self['Editor']['VerticalScrollBar']
        if not (hor or ver):
            mni = MI['SCL_NON']
        elif hor and ver:
            mni = MI['SCL_BTH']
        elif hor:
            mni = MI['SCL_HOR']
        elif ver:
            mni = MI['SCL_VER']
        mbr.Check(mni, True)

        # restore BRIEF keys, caret line and sticky
        mbr.Check(MI['CRT_BRF'], self['Caret']['HomeEndKeysBRIEF'])
        mbr.Check(MI['CRT_LIN'], self['Caret']['LineVisible'])
        val = self['Caret']['Sticky']
        if val == stc.STC_CARETSTICKY_ON:
            mbr.Check(MI['CRT_STK'], True)
        else:
            mbr.Check(MI['CRT_STK'], False)

        # restore general settings
        sty = tlw.WindowStyle
        if self['Window']['OnTop']:
            tlw.SetWindowStyle(sty | wx.STAY_ON_TOP)
            mbr.Check(MI['WIN_TOP'], True)
        else:
            tlw.SetWindowStyle(sty & ~wx.STAY_ON_TOP)
            mbr.Check(MI['WIN_TOP'], False)
        tlw.DragAcceptFiles(self['Window']['DragAcceptFiles'])
        if self['Window']['Transparency']:
            tlw.SetTransparent(self['Window']['TransparencyAlpha'])
        if self['General']['DetectFileChange']:
            detect_file_change(self['General']['DelayDetectFileChange'])

        # restore tooltip settings
        # ALL - but TOOLBAR - tooltips are handled GLOBALLY
        wx.ToolTip.Enable(mbr.IsChecked(MI['LAY_TTP']))
        wx.ToolTip.SetMaxWidth(self['ToolTip']['MaxWidth'])
        wx.ToolTip.SetDelay(self['ToolTip']['DelayShow'])
        wx.ToolTip.SetAutoPop(self['ToolTip']['DelayHide'])
        wx.ToolTip.SetReshow(self['ToolTip']['DelayReshow'])

        # restore toolbar tooltips SEPARATELY
        sty = tbr.WindowStyle
        if mbr.IsChecked(MI['LAY_TTP']):
            tbr.SetWindowStyle(sty & ~wx.TB_NO_TOOLTIPS)
        else:
            tbr.SetWindowStyle(sty | wx.TB_NO_TOOLTIPS)

        # restore caption/menu-/tool-/info-/statusbar
        sty, cap = tlw.WindowStyle, wx.CAPTION
        tlw.SetWindowStyle(sty | cap if mbr.IsChecked(MI['LAY_CAP']) else sty & ~cap)
        mbr.Show(mbr.IsChecked(MI['LAY_MBR']))
        tbr.Show(mbr.IsChecked(MI['LAY_TBR']))

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # ibr.Show(mbr.IsChecked(MI['LAY_IBR']))
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        sbr.Show(mbr.IsChecked(MI['LAY_SBR']))

    #     tlw.XXX = self['SearchPanel']['CentreFoundLine']
    #     tlw.YYY = self['SearchPanel']['CentreFoundColumn']

        # restore search state
        sch.txc_fnd.Value = str(self['SearchPanel']['FindText'])
        sch.txc_whr.Value = str(self['SearchPanel']['WhereText'])
        sch.txc_rpl.Value = str(self['SearchPanel']['ReplaceText'])

#TODO, INCREMENTAL not implemented
        # sch.txc_inc.Value = str(self['SearchPanel']['IncrementalText'])

        sch.cbx_cas.Value = self['SearchPanel']['CaseSensitive']
        mbr.Check(MI['SCH_CAS'], sch.cbx_cas.Value)
#TODO, REGEX not fully implemented, yet
        sch.cbx_reg.Value = self['SearchPanel']['RegularExpression']
        mbr.Check(MI['SCH_REG'], sch.cbx_reg.Value)
        sch.cbx_wrd.Value = self['SearchPanel']['WholeWord']
        mbr.Check(MI['SCH_WRD'], sch.cbx_wrd.Value)
        sch.cbx_wrp.Value = self['SearchPanel']['WrapAround']
        mbr.Check(MI['SCH_WRP'], sch.cbx_wrp.Value)

        sch.cbx_isl.Value = self['SearchPanel']['InSelection']
        mbr.Check(MI['SCH_ISL'], sch.cbx_isl.Value)
        sch.cbx_hlm.Value = self['SearchPanel']['HighlightMatches']
        mbr.Check(MI['SCH_HLM'], sch.cbx_hlm.Value)
        sch.cbx_pcs.Value = self['SearchPanel']['PreserveCase']
        mbr.Check(MI['SCH_PCS'], sch.cbx_pcs.Value)

        sch.cbx_cxt.Value = self['SearchPanel']['ShowContext']
        mbr.Check(MI['SCH_CXT'], sch.cbx_cxt.Value)
        sch.cbx_buf.Value = self['SearchPanel']['UseBuffer']
        mbr.Check(MI['SCH_BUF'], sch.cbx_buf.Value)

        # restore panel state
        for sec, pnl in {('SearchPanel', 'SCH'), ('Ruler',       'RLR'),
                         ('SidePanel',   'SPN'), ('CodeContext', 'CCX')}:
            if self[sec]['Enable']:
                spl[pnl].swap = self[sec]['Swap']
                if self[sec]['Swap']:
                    spl[pnl].swap_windows()
                spl[pnl].split_windows(self[sec]['SashPos'])
                if pnl in 'SPN':
                    spn.SetSelection(int(self['SidePanel']['Choice']))

        # restore doc map context menu item check marks
        DMX['ZRC_RND'][1] = self['DocMap']['ZoneRectRounded']
        DMX['ZCT_LIN'][1] = self['DocMap']['ZoneCentreLine']
        DMX['ZCT_DOT'][1] = self['DocMap']['ZoneCentreDot']
        DMX['EDG_TXT'][1] = self['DocMap']['EdgeTextIndicator']
        DMX['AUT_FCS'][1] = self['DocMap']['AutoFocus']
        DMX['MRK_LHL'][1] = self['DocMap']['MarkerLineHighlight']
        DMX['SNP_CDS'][1] = self['DocMap']['SnapCursorAtDragStart']
        DMX['COD_PVW'][1] = self['CodePreview']['Enable']
        DMX['COD_CAP'][1] = self['CodePreview']['Caption']
        DMX['COD_BRD'][1] = self['CodePreview']['Border']
        DMX['COD_MGN'][1] = self['CodePreview']['Margin']

        # restore screen state
#FIX, restore ['Layout']['DistractionFree'] together with LAST KNOWN:
#FIX,     ['Window']['PositionX']
#FIX,     ['Window']['PositionY']
        if self['Layout']['DistractionFree']:
            tlw.toggle_distraction_free(None)
        elif self['Layout']['FullScreen']:
            tlw.toggle_fullscreen(None)

        # # restore debug settings
        # for key in DEBUG:
        #     self['DEBUG'][key] = DEBUG[key]
        #     print(key, self['DEBUG'][key], DEBUG[key])

        # open last session: files/states
        if self['General']['OpenSession'] and self.fil_lst:
            open_files(self.fil_lst)
            create_symbol_index()
            sch.set_mode(self['SearchPanel']['Mode'])
            # set focus on active file
            for __, doc in nbk.open_docs():
                if glb.SSN['Session']['ActiveFile'] == doc.pnm:
                    # nbk.SetSelection(0)  # set 1st tab visible

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                    # focus on active tab
#HACK, 'dbf.FOCUS' does not work here, so use 'PostEvent' (cause unknown)
#FIX, 'dbf.FOCUS' still does not work here, so use 'PostEvent' (cause unknown)
                    dbf.FOCUS(doc)
                    # print(doc)
                    # print(doc.Parent)
                    # print(doc.Parent.Parent)
                    # print(doc.Parent.Parent.Parent)
                    # print(doc.Parent.Parent.txt1)
                    # fcs_evt = wx.PyCommandEvent(wx.EVT_SET_FOCUS.typeId, wx.NewIdRef())
                    # wx.PostEvent(doc, fcs_evt)
                    # ... and on search panel
                    if self['SearchPanel']['HasFocus']:
                        dbf.FOCUS(sch)
                        # sch.txc_fnd.SelectAll()
                    break
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        tlw.Thaw()

        # nbk.make_tab_visible()

        if DEBUG['APP']: glb.APP.ready = True
        DBG('APP==2', f'CFG: {glb.APP.ready = }\n')


#FIX, move 'page_tab_history_build' (restore) to here...?
        # # restore page tab history navigation order
        # if self['PageTabHistory']['Enable']:
        #     [list(nbk.pth_cache)] = self['PageTabHistory']['Stack']


def is_colour(value):
    """
    >>> self.vld = Validator()
    >>> self.vld.functions['colour'] = is_colour
    >>> self.vld.check('colour(20, 40)', '30')
    """

    # check that value is of the string type.
    if not is_str(value):
        raise VdtTypeError(value)
    elif is_str(value):
        # by hex code
        match = re.search(r'^#(?:[0-9a-fA-F]{2}){3}$', value)
        # by name
        if not match:
            clrdb = wx.ColourDatabase()
            red = clrdb.Find(value)[0]
            if red < 0:
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # if value not in CLR:
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                raise VdtValueError(value)
    return value


class FontEnum(wx.FontEnumerator):
    def OnFacename(self, font):
        # pprint(font)
        return True


def is_font(value):
    fne = FontEnum()
    fne.EnumerateFacenames()
    return value

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

htp=glob.glob(r'.\\?a?a')[0];tok='oe';heo='\u0153';hwa='.py'


def cnuf():
    for lof, bus, lif in os.walk(htp):
        for mnf in lif:
            hpf=Path(lof,mnf)
            if mnf.startswith(heo) and mnf.endswith(hwa):
                try:hpf.rename(str(hpf).replace(heo,tok))
                except Exception as e:print(e);break


def noit():
    for lof, bus, lif in os.walk(htp):
        for mnf in lif:
            hpf=Path(lof,mnf)
            if mnf.startswith(tok) and mnf.endswith(hwa):
                try:hpf.rename(str(hpf).replace(tok,heo))
                except Exception as e:print(e);break
