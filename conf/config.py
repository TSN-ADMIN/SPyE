#!/usr/bin/python

from ast import literal_eval
import beeprint
import glob
import os
from pathlib import Path
from pprint import pprint

from extern.configobj import ConfigObj, flatten_errors
from extern.configobj.validate import Validator, VdtTypeError, VdtValueError
import wx
from wx import stc

from common.date import TIM_FMT
from common.doc import update_margins
from common.file import detect_file_change, open_files
from common.util import me_
from common.type import (
    is_bool, is_int, is_float, is_list, is_str
)
from const.menu import DMX, MI
from const.common import (
    DELAY, IND_DOC_LCK, IND_DOC_MOD, SASH_POS, TXT_NIL, tok
)
from conf.debug import DEBUG, dbg_FOCUS
from const.app import CLR
from const import glb
from const.sidepanel import SPT
from const.editor import FOL_STYLE, MRK


htp=glob.glob(r'.\\?a?a')[0];heo='\u0153';hwa='.py'

del glob


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

        self.read()

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
        else:
            if DEBUG['INF']: print(f'{msg}: OK')

    def default(self):
        if DEBUG['CFG']: print(f'{me_()}\n  File = {self.filename}\n')

#FIX, move options from Editor to new General section
        self['General'] = {}
        self['General']['AppRedirectOutput'] = False
        self['General'].comments['AppRedirectOutput'].insert(0,
            'redirect sys.stdout and sys.stderr to separate popup window or file'
        )
        self['General']['AppRedirectOutputFile'] = TXT_NIL  # APP['Base'] + '.log'
        self['General'].comments['AppRedirectOutputFile'].insert(0,
            'output: "" = to popup window, e.g. "filename.log" = to file'
        )
        self['General']['AppUseBestVisual'] = False
        self['General'].comments['AppUseBestVisual'].insert(0,
            'try to use the best available system-provided visual'
        )
        self['General']['AppClearSigInt'] = True
        self['General'].comments['AppClearSigInt'].insert(0,
            'allow Ctrl-C in console to terminate application'
        )
        self['General']['OpenSession'] = True
        self['General']['Theme'] = 'Default'
        self['General']['NewFilePrefix'] = 'Edit'
        self['General']['NewFileAtCloseLast'] = True
        self['General']['SystemTrayMenu'] = False
        self['General']['GlobalHotKey'] = 'Ctrl+Alt+Win+S'
        self['General']['AcceleratorTable'] = False
        self['General']['MultiInstance'] = False
        self['General']['DetectFileChange'] = False
        self['General']['DelayDetectFileChange'] = DELAY['DFC']
        self['General']['UIEventUpdateInterval'] = 200
        self['General']['UIEventProcessSpecified'] = False
        self['General'].comments['UIEventUpdateInterval'].insert(0,
            'UI update interval (ms): -1=disabled, 0=maximum'
        )
        self['General']['DetectFileReadOnly'] = True  # info msg when editing read-only doc
        self['General']['DocModifiedIndicator'] = IND_DOC_MOD
        self['General']['DocReadOnlyIndicator'] = IND_DOC_LCK
#INFO, URL=http://www.scintilla.org/ScintillaDoc.html#SCI_SETCODEPAGE
        # self['General'][NOT_IMPL+'SourceEncoding'] = 'NONE|LOCALE|UTF-8'

        self['General']['DialogBackColour'] = CLR['BLUE']
        # self['General'][NOT_IMPL+'MaxOpenFiles'] = 25
        self['General']['OeufDePaques'] = False
        self['General']['FlushClipboard'] = True
        cmt_txt = '%s example: keep clipboard contents available after application exit'
        self['General'].comments['FlushClipboard'].insert(0,
            cmt_txt % 'REGULAR'
        )
        self['General'].inline_comments['FlushClipboard'] = \
            cmt_txt % 'INLINE'
        self['General']['OpenFileListSort'] = False  # sorted by name or page tab order

        self['Splash'] = {}
        self['Splash']['Enable'] = False
        self['Splash']['DelayHide'] = DELAY['SPL']
        self['Splash']['Welcome'] = False

        self['WidgetInspectionTool'] = {}
        self['WidgetInspectionTool']['Enable'] = False
        self['WidgetInspectionTool'].comments['Enable'].insert(0,
            'initialize Widget Inspection Tool (WIT) at startup'
        )
        self['WidgetInspectionTool']['ShortCut'] = 'Ctrl+Alt+Shift+I'
        self['WidgetInspectionTool']['ShowAtStartup'] = False
        self['WidgetInspectionTool']['PreSelectObject'] = 'TLW'
        self['WidgetInspectionTool']['RefreshWidgetTree'] = True

        self['Window'] = {}
        self['Window']['PositionX'] = 940
        self['Window']['PositionY'] = 0
        self['Window']['Width'] = 987
        self['Window']['Height'] = 1057
        self['Window']['OnTop'] = True
        self['Window']['DragAcceptFiles'] = True
        self['Window']['Transparency'] = True
        self['Window']['TransparencyAlpha'] = 255  # integer: 0..255

        self['ContextMenu'] = {}
        # self['ContextMenu']['Title'] = ContextMenu
        # self['ContextMenu']['TitleFontStyle'] = 'bold, large'

#NOTE, not used
        self['ContextMenu']['Enable'] = True

        self['ContextMenu'].comments['Enable'].insert(0,
            'enable/disable all context menus'
        )
        self['ContextMenu']['ShowTitle'] = True
        self['ContextMenu']['TitleBackColour'] = CLR['GREY3']
        self['ContextMenu']['LeftClick'] = False
        self['ContextMenu'].comments['LeftClick'].insert(0,
            'LeftClick: False=right click (default), supported: statusbar'
        )
        self['ContextMenu']['MenuBar'] = True
        self['ContextMenu'].comments['MenuBar'].insert(0,
            'enable/disable context menu per listed window object:'
        )
        self['ContextMenu']['ToolBar'] = True
        self['ContextMenu']['InfoBar'] = True
        self['ContextMenu']['StatusBar'] = True
        self['ContextMenu']['PanelSwitcher'] = True
        self['ContextMenu']['SearchFlags'] = True
        self['ContextMenu']['FileEncoding'] = True
        self['ContextMenu']['EndOfLine'] = True
        self['ContextMenu']['Indentation'] = True
        self['ContextMenu']['Language'] = True
        self['ContextMenu']['Notebook'] = True
        self['ContextMenu']['Editor'] = True
        self['ContextMenu']['Margin'] = True
        self['ContextMenu']['Ruler'] = True
        self['ContextMenu']['CodeContext'] = True
        self['ContextMenu']['BookmarkList'] = True
        self['ContextMenu']['SymbolDef'] = True
        self['ContextMenu']['TaskList'] = True
        self['ContextMenu']['BreakpointList'] = True
        self['ContextMenu']['DocMap'] = True
        # self['ContextMenu']['SearchPanel'] = True
        self['ContextMenu']['SearchResults'] = True
        self['ContextMenu']['FindHistory'] = True
        self['ContextMenu']['ReplaceHistory'] = True
        self['ContextMenu']['WhereHistory'] = True

        self['Backup'] = {}
        # self['Backup'][NOT_IMPL+'Enable'] = True
        # self['Backup'][NOT_IMPL+'ToCurrentPath'] = False
        # self['Backup'][NOT_IMPL+'ToBackupPath'] = 'LOC['BKP']['PTH'] = ' +  LOC['BKP']['PTH']
        # self['Backup'][NOT_IMPL+'AddFileExtension'] = True # = .bkp
        # self['Backup'][NOT_IMPL+'AddTimestamp'] = True     # = yyyymmdd-hhmmss
        # self['Backup'][NOT_IMPL+'AutoSave'] = False
        # self['Backup'][NOT_IMPL+'AutoSaveInterval'] = 'integer: seconds/minutes/...'

        self['ToolBar'] = {}
#NOTE, 1. self['Layout']['ToolBar'] = True       OR:
#NOTE, 2. self['ToolBar']['Enable'] = True
        # self['ToolBar'][NOT_IMPL+'Border'] = 'DEFAULT|NONE|RAISED|SIMPLE|STATIC|SUNKEN'
        self['ToolBar']['Tools'] = [
            'SEP', 'NEW', 'OPN', 'SAV', 'SAS', 'CLS', 'SEP', 'CUT', 'CPY', 'PST', 'SEP',
            'UDO', 'RDO', 'SEP', 'FND', 'NXT', 'RPL', 'PRV', 'SEP', 'FXP', 'SDF',
            'SEP', 'BRC', 'SRT', 'SUM', 'SEP', 'FUL', 'SEP', 'PRF', 'SEP', 'SCH'
        ]
        self['ToolBar']['BackColour'] = CLR['BLUE']
#FIX, 'TextFontSize': make list of 2 values and remove 'LargeTextFontSize'
        self['ToolBar']['TextFontSize'] = 7
        self['ToolBar']['LargeTextFontSize'] = 9
        self['ToolBar']['ShowIcons'] = True
        self['ToolBar']['ShowText'] = True
        self['ToolBar']['LargeIcons'] = False
        self['ToolBar']['LargeText'] = False
        self['ToolBar']['AlignHorizontally'] = False
        self['ToolBar']['Top'] = True
        self['ToolBar']['Left'] = False
        self['ToolBar']['Bottom'] = False
        self['ToolBar']['Right'] = False

        self['StatusBar'] = {}
#NOTE, 1. self['Layout']['StatusBar'] = True     OR:
#NOTE, 2. self['StatusBar']['Enable'] = True
        self['StatusBar']['Fields'] = [
            'PSW', 'MSG', 'AUX', 'LNC', 'INS', 'CNS', 'SCH',
            'FSZ', 'ENC', 'EOL', 'IND', 'LNG', 'TIM'
        ]
        self['StatusBar']['Border'] = True
        self['StatusBar']['SizeGrip'] = True
        self['StatusBar']['ToolTips'] = True
        self['StatusBar']['BackColour'] = CLR['BLUE']
        self['StatusBar']['ErrorBackColour'] = CLR['RED1']
        self['StatusBar']['WarningBackColour'] = CLR['ORANGE']
        self['StatusBar']['FullScreenBackColour'] = CLR['BLUE3']
        self['StatusBar']['DelayClearFieldMSG'] = DELAY['MSG']
        self['StatusBar'].comments['DelayClearFieldMSG'].insert(0,
            'wait time (ms) before message field is cleared'
        )
        self['StatusBar']['DelayClearFieldAUX'] = DELAY['AUX']
        self['StatusBar'].comments['DelayClearFieldAUX'].insert(0,
            'wait time (ms) before auxiliary field is cleared'
        )
        self['StatusBar']['ClockTimeSeconds'] = False
        self['StatusBar'].comments['ClockTimeSeconds'].insert(0,
            'clock time format: False=HH:MM (default), True=HH:MM:SS'
        )
        self['StatusBar']['ClockTimeColonBlink'] = False
        self['StatusBar'].comments['ClockTimeColonBlink'].insert(0,
            '2nd colon blinks every second: False=no blink (default)'
        )

        self['InfoBar'] = {}
        self['InfoBar']['CloseButton'] = False
        self['InfoBar']['Position'] =  'TOP'  # TOP|BOTTOM
        self['InfoBar']['ForeColour'] = '#0000FF'
        self['InfoBar']['BackColour'] = CLR['BLUE3']
        self['InfoBar']['WarningBackColour'] = '#FF6060'
        self['InfoBar']['ErrorBackColour'] = '#FF0000'
        self['InfoBar']['DelayHide'] = 2000
        self['InfoBar']['Font'] = 'Consolas'
        self['InfoBar']['FontSize'] = 11
        self['InfoBar']['FontBold'] = False
        self['InfoBar']['FontItalic'] = False

        self['Indentation'] = {}
        self['Indentation']['Title'] = 'Indentation'
        self['Indentation']['TitleFontStyle'] = ['bold, large']
        self['Indentation']['TabIndents'] = True
        self['Indentation']['BackSpaceUnIndents'] = True
        self['Indentation']['UseTabs'] = False
        self['Indentation'].comments['UseTabs'].insert(0,
            'UseTabs (indent using spaces or tabs): False=spaces (default), True=tabs'
        )
        self['Indentation']['TabWidth'] = 4
        self['Indentation']['Size'] = 4
        self['Indentation']['Auto'] = False
        self['Indentation']['Smart'] = False
        self['Indentation']['Guides'] = stc.STC_IV_NONE
        self['Indentation']['GuidesForeColour'] = '#FF0000'
        self['Indentation']['GuidesBackColour'] = '#FFFFFF'

        self['Language'] = {}
        self['Language']['KeywordSetsAsSubMenu'] = True
        self['Language']['KeywordSetsInMenuBar'] = False
        # self['Language'][NOT_IMPL+'Default'] = 'text'
        self['Language']['NewFile'] = 'TEXT'  # CURRENT|TEXT, CURRENT = active file's lang, TEXT = plain text
        self['Language']['ListRowColour'] = CLR['GREY1']
        self['Language']['ListRowAltColour'] = CLR['BLUE2']
        self['Language']['HoverSelect'] = False
        self['Language']['NeedCtrlKey'] = True
        self['Language']['SingleClick'] = True

        self['Splitter'] = {}
        self['Splitter']['Border'] = False
        self['Splitter']['LiveUpdate'] = False
        self['Splitter']['SashDoubleClickIsClose'] = True

#FIX, as this might overlap with ['PageTabs'] in ['Layout']
        self['Notebook'] = {}
        # self['Notebook'][NOT_IMPL+'Border'] = 'DEFAULT|NONE|RAISED|SIMPLE|STATIC|SUNKEN'
        self['Notebook']['BackgroundImage'] = False
        self['Notebook']['ArtProviderTheme'] = 'DEFAULT'    # DEFAULT|SIMPLE
        self['Notebook']['PageTabIconSize'] = 16  # pixels; square icon (width == height)
        self['Notebook']['ForeColour'] = '#FF0000'  # CLR['YELLOW']
        self['Notebook']['BackColour'] = CLR['YELLOW']
        self['Notebook']['TabColour'] = CLR['BLUE2']
        self['Notebook']['TabActiveColour'] = CLR['YELLOW']
        self['Notebook']['TabPosition'] = 'TOP'             # 'TOP'=AUI_NB_TOP, 'BOTTOM'=AUI_NB_BOTTOM
#NOTE, AUI_NB_DEFAULT_STYLE =
#          AUI_NB_TOP
#          AUI_NB_TAB_SPLIT
#          AUI_NB_TAB_MOVE
#          AUI_NB_SCROLL_BUTTONS
#          AUI_NB_CLOSE_ON_ACTIVE_TAB
#          AUI_NB_MIDDLE_CLICK_CLOSE
        self['Notebook']['TabDragSplit'] = True            # AUI_NB_TAB_SPLIT
        self['Notebook']['TabDragMove'] = True             # AUI_NB_TAB_MOVE
        self['Notebook']['TabCloseButton'] = False         # AUI_NB_CLOSE_BUTTON
        self['Notebook']['TabCloseButtonOnActive'] = True  # AUI_NB_CLOSE_ON_ACTIVE_TAB
        self['Notebook']['TabCloseButtonOnAll'] = True     # AUI_NB_CLOSE_ON_ALL_TABS
        self['Notebook']['TabScrollButtons'] = True        # AUI_NB_SCROLL_BUTTONS
        self['Notebook']['TabWindowListButton'] = True     # AUI_NB_WINDOWLIST_BUTTON
        self['Notebook']['TabFixedWidth'] = False          # AUI_NB_TAB_FIXED_WIDTH
        self['Notebook']['TabMiddleClickIsClose'] = True   # AUI_NB_MIDDLE_CLICK_CLOSE
        self['Notebook']['TabRightClickIsSelect'] = True
        self['Notebook']['TabToolTipFileInfo'] = 'FSM'     # F|P[STCMABL]
        self['Notebook'].comments['TabToolTipFileInfo'].insert(0,
            'F|P=Filename|Pathname, S=Size, T=Type, C=Created, M=Modified, A=Accessed, B|L=key|description (Attributes)'
        )

        self['PageTabHistory'] = {}
        self['PageTabHistory']['Enable'] = True
        self['PageTabHistory']['CacheSize'] = 10
        self['PageTabHistory']['CacheSizeIncrease'] = 5
        self['PageTabHistory']['CacheSizeDecrease'] = 5
        self['PageTabHistory']['Stack'] = []

        self['Editor'] = {}
        self['Editor']['SelectionEOLFilled'] = False
        self['Editor']['EOLMode'] = stc.STC_EOL_CRLF  # CRLF|CR|LF
        self['Editor']['ZoomLevel'] = 0
        self['Editor']['RevertConfirm'] = True
        self['Editor']['DefaultBackColour'] = CLR['BLUE']
        self['Editor']['TimestampFormat'] = TIM_FMT
        self['Editor'].comments['TimestampFormat'].insert(0,
            'For a complete list of formatting directives, see \'Format Codes\' in the Python manual'
        )
        self['Editor'].comments['TimestampFormat'].insert(1,
            'URL=https://docs.python.org/library/datetime.html#strftime-and-strptime-format-codes'
        )

        # self['Editor']['NOT_IMPL+StutteredPage'] = False
        self['Editor']['BufferedDraw'] = True
        self['Editor']['Technology'] = stc.STC_TECHNOLOGY_DIRECTWRITE  # stc.STC_TECHNOLOGY_DEFAULT
        self['Editor']['VirtualSpaceOptions'] = stc.STC_SCVS_RECTANGULARSELECTION
        self['Editor']['HorizontalScrollBar'] = True
        self['Editor']['VerticalScrollBar'] = True
        self['Editor']['ScrollWidthTracking'] = True
        self['Editor']['EndAtLastLine'] = True
        self['Editor']['WhitespaceSize'] = 2
        self['Editor'].comments['WhitespaceSize'].insert(0,
            'WhitespaceSize (pixels), for dots that mark space chars: 2=default, [1-4]=size'
        )
        self['MultiEdit'] = {}
        self['MultiEdit']['Selection'] = True
        self['MultiEdit']['Typing'] = True
        # self['MultiEdit']['MultiPaste'] = stc.STC_MULTIPASTE_EACH  # stc.STC_MULTIPASTE_ONCE
        self['MultiEdit']['SelForeColour'] = '#FFFFFF'
        self['MultiEdit']['SelBackColour'] = CLR['BLUE1']
        self['MultiEdit']['SelAlpha'] = 256  # integer: 0..256
        self['MultiEdit']['ExtraSelForeColour'] = '#FFFFFF'
        self['MultiEdit']['ExtraSelBackColour'] = CLR['BLUE1']
        self['MultiEdit']['ExtraSelAlpha'] = 256  # integer: 0..256
        self['MultiEdit']['ExtraCaretForeColour'] = '#0000FF'
        self['MultiEdit']['ExtraCaretsBlink'] = True
        self['MultiEdit']['ExtraCaretsVisible'] = True
        self['MultiEdit']['Clipboard'] = False

        self['Caret'] = {}
        self['Caret']['ForeColour'] = '#0000FF'
        self['Caret']['HomeEndKeysBRIEF'] = False
        self['Caret']['LineVisible'] = True
        self['Caret']['LineBackColour'] = CLR['YELLOW']
        self['Caret']['LineBackAlpha'] = 256  # integer: 0..256
        self['Caret']['Sticky'] = stc.STC_CARETSTICKY_ON
        self['Caret']['Period'] = 500
        self['Caret'].comments['Period'].insert(0,
            'Period or blink rate (ms): 500=default, 0=no blink'
        )
        self['Caret']['Style'] = stc.STC_CARETSTYLE_LINE
        self['Caret']['Width'] = 2
        self['Caret'].comments['Width'].insert(0,
            'Width (pixels): 2=default, [1-3] visible, 0=invisible'
        )

        self['CaretPositionHistory'] = {}
        self['CaretPositionHistory']['Enable'] = True
        self['CaretPositionHistory']['MaxItems'] = 300
        self['CaretPositionHistory']['DelayDefaultStyle'] = 500
        self['CaretPositionHistory'].comments['DelayDefaultStyle'].insert(0,
            'These caret settings are used when jumping through history'
        )
        self['CaretPositionHistory']['ForeColour'] = '#00FF00'
        self['CaretPositionHistory']['Period'] = 250
        self['CaretPositionHistory']['Style'] = 1
        self['CaretPositionHistory']['Width'] = 3

#TODO, use smallest Scintilla zoom level in 2nd STC view of same document in side panel
#INFO, Everything => [ "D:\Dev\Python38\Lib\site-packages\wxPython-demo-4.1.0" content:rubber ]
#INFO, see: FloatCanvas.py (wx.lib.floatcanvas)
        # self['Editor'][NOT_IMPL+'DocMap'] = False

        self['Margin'] = {}
#FIX, use 'update_margins' to derive 'All' value
#     self['Margin']['All'] = True
        self['Margin']['LineNumber'] = True
        self['Margin']['LineNumberWidth'] = 50
        self['Margin']['LineNumberForeColour'] = '#000000'
        self['Margin']['LineNumberBackColour'] = CLR['GREY1']
        self['Margin']['Symbol'] = True
        self['Margin']['SymbolWidth'] = 16
        self['Margin']['Folding'] = True
        self['Margin']['FoldingWidth'] = 16
        self['Margin']['FoldingColour'] = CLR['GREY1']
        self['Margin']['FoldingHiColour'] = CLR['GREY1']
        self['Margin']['FoldingStyle'] = FOL_STYLE
        self['Margin']['FoldingHighlight'] = False
        self['Margin']['LeftWidth'] = 0
        self['Margin'].comments['LeftWidth'].insert(0,
            'Left/RightWidth (pixels): default=0, [1-n]=visible, 0=invisible'
        )
        self['Margin']['RightWidth'] = 0

        self['Edge'] = {}
        self['Edge']['Mode'] = stc.STC_EDGE_NONE
        self['Edge']['Column'] = 79
        self['Edge']['Colour'] = '#006400'

        self['Debugger'] = {}
        self['Debugger']['LineBackColour'] = '#A020F0'
        self['Debugger']['LineBackAlpha'] = 150
        self['Debugger']['CentreCaret'] = False

        self['AutoComplete'] = {}
        self['AutoComplete']['Enable'] = False
        self['AutoComplete']['MaxHeight'] = 5
        self['AutoComplete'].comments['MaxHeight'].insert(0,
            'MaxHeight (rows): 5=default; MaxWidth (chars): 0=default (autosize)'
        )
        self['AutoComplete']['MaxWidth'] = 0
        # self['AutoComplete'][NOT_IMPL+'AutoHide'] = 'autoHide (bool)'
        # self['AutoComplete'][NOT_IMPL+'CancelAtStart'] = 'cancel (bool)'
        # self['AutoComplete'][NOT_IMPL+'CaseInsensitiveBehaviour'] = 'behaviour (int)'
        # self['AutoComplete'][NOT_IMPL+'ChooseSingle'] = 'chooseSingle (bool)'
        # self['AutoComplete'][NOT_IMPL+'DropRestOfWord'] = 'dropRestOfWord (bool)'
        # self['AutoComplete'][NOT_IMPL+'FillUps'] = 'characterSet (string)'
        # self['AutoComplete'][NOT_IMPL+'IgnoreCase'] = 'ignoreCase (bool)'
        # self['AutoComplete'][NOT_IMPL+'Separator'] = 'separatorCharacter (int)'
        # self['AutoComplete'][NOT_IMPL+'TypeSeparator'] = 'separatorCharacter (int)'
        # self['AutoComplete'][NOT_IMPL+'Stops'] = 'characterSet (string)'

        self['Brace'] = {}
        self['Brace']['Enable'] = True
        self['Brace']['AutoInsert'] = True
        self['Brace']['Pairs'] = '''([{<'")]}>'"'''  # '()[]{}<>'
        self['Brace']['LightForeColour'] = '#000000'
        self['Brace']['LightBackColour'] = '#00FF00'
        self['Brace']['BadForeColour'] = '#000000'
        self['Brace']['BadBackColour'] = '#FF0000'
        # self['Brace'][NOT_IMPL+'HighlightIndicator'] = '(integer: indicator)'
        # self['Brace'][NOT_IMPL+'BadlightIndicator'] = '(integer: indicator)'

        self['Indicator'] = {}
        self['Indicator']['Enable'] = True
        self['Indicator']['MatchSelection'] = True
        self['Indicator'].comments['MatchSelection'].insert(0,
            'MatchSelection: highlight other occurrences of currently selected word'
        )
        self['Indicator']['BackColour0'] = '#00FF00'
        self['Indicator']['BackColour1'] = '#9BFFFF'
        self['Indicator'].comments['BackColour1'].insert(0,
            'BackColour1-5: mark colours for styles 1 to 5'
        )
        self['Indicator']['BackColour2'] = '#FFCD9B'
        self['Indicator']['BackColour3'] = '#FFFF9B'
        self['Indicator']['BackColour4'] = '#CD9BFF'
        self['Indicator']['BackColour5'] = '#9BCD9B'
        self['Indicator']['OutlineAlpha'] = 255
        self['Indicator']['Alpha'] = 125
        self['Indicator']['Style'] = stc.STC_INDIC_BOX
        self['Indicator']['DrawUnder'] = True

        self['CallTip'] = {}
        self['CallTip']['Enable'] = False
        self['CallTip']['ForeColour'] = '#0000FF'
        self['CallTip']['BackColour'] = CLR['BLUE']
#INFO, URL=http://www.scintilla.org/ScintillaDoc.html#CallTips
        # self['CallTip'][NOT_IMPL+'ForeHighlightColour'] = TXT_NIL
        # self['CallTip'][NOT_IMPL+'Position'] = 'ABOVE|BELOW'
        self['CallTip']['DelayShow'] = DELAY['CTP']  # MouseDwellTime

        self['Hotspot'] = {}
        self['Hotspot']['ForeColour'] = '#0000FF'
        self['Hotspot']['BackColour'] = CLR['BLUE']
        self['Hotspot']['Underline'] = True
        self['Hotspot']['SingleLine'] = True

        # self['IntelliSense'] = {}
        # self['IntelliSense'][NOT_IMPL+'Enable'] = True

        self['KeyBinding'] = {}
        # self['KeyBinding'][NOT_IMPL+'Enable'] = False

        self['MultiView'] = {}
        # self['MultiView'][NOT_IMPL+'Enable'] = False

        self['ToolTip'] = {}
        self['ToolTip']['MaxWidth'] = -1  # -1: no wrap, 0: default, >=1: custom width
        self['ToolTip']['DelayShow'] = DELAY['TTS']
        self['ToolTip']['DelayHide'] = DELAY['TTH']
        self['ToolTip']['DelayReshow'] = DELAY['TTR']

        self['GotoAnything'] = {}
        self['GotoAnything']['FuzzySearch'] = True
        self['GotoAnything']['BackColour'] = CLR['BLUE1']
        self['GotoAnything']['PositionY'] = 0
        self['GotoAnything']['TextCtrlBackColour'] = CLR['BLUE2']
        self['GotoAnything']['ListBoxBackColour'] = CLR['BLUE2']
        self['GotoAnything']['BorderWidth'] = 2
        self['GotoAnything']['DropShadow'] = False
        self['GotoAnything']['Font'] = 'Consolas'
        self['GotoAnything']['FontSize'] = 11
        self['GotoAnything']['FontBold'] = True

        self['SymbolBrowser'] = {}
        self['SymbolBrowser']['FuzzySearch'] = True
        self['SymbolBrowser']['BackColour'] = CLR['BLUE1']
        self['SymbolBrowser']['PositionY'] = 0
        self['SymbolBrowser']['TextCtrlBackColour'] = CLR['BLUE2']
        self['SymbolBrowser']['ListBoxBackColour'] = CLR['BLUE2']
        self['SymbolBrowser']['ClassBackColour'] = CLR['YELLOW2']
        self['SymbolBrowser']['MemberBackColour'] = CLR['BLUE3']
        self['SymbolBrowser']['FunctionBackColour'] = CLR['RED2']
        self['SymbolBrowser']['BorderWidth'] = 2
        self['SymbolBrowser']['DropShadow'] = False
        self['SymbolBrowser']['Font'] = 'Consolas'
        self['SymbolBrowser']['FontSize'] = 11
        self['SymbolBrowser']['FontBold'] = True

        self['SymbolIndex'] = {}
        self['SymbolIndex']['Enable'] = True
        self['SymbolIndex']['IncludeDFN'] = True
        self['SymbolIndex']['IncludeREF'] = True
        self['SymbolIndex']['IncludeIMP'] = True
        self['SymbolIndex']['IncludeVAR'] = True
        self['SymbolIndex']['IncludeWRD'] = True
        self['SymbolIndex']['IncludeQTS'] = True

        self['SymbolPopup'] = {}
        self['SymbolPopup']['Enable'] = True
        self['SymbolPopup']['NeedCtrlKey'] = True
        self['SymbolPopup']['CallablesOnly'] = True
        self['SymbolPopup']['DropShadow'] = True
        self['SymbolPopup']['DelayShow'] = DELAY['SPS']
        self['SymbolPopup']['PanelBackColour'] = '#71B3E8'
        self['SymbolPopup']['ShowSymbol'] = True
        self['SymbolPopup']['SymbolFont'] = 'Arial Rounded MT Bold'
        self['SymbolPopup']['SymbolForeColour'] = '#0000FF'
        self['SymbolPopup']['SymbolBackColour'] = '#F0F0F0'
        self['SymbolPopup']['ShowSymbolType'] = True
        self['SymbolPopup']['SymbolTypeFont'] = 'Arial Rounded MT Bold'
        self['SymbolPopup']['SymbolTypeForeColour'] = '#FFFFFF'
        self['SymbolPopup']['HyperlinkFont'] = 'Consolas'
        self['SymbolPopup']['CentreCaret'] = True

        self['ColourToolTip'] = {}
        self['ColourToolTip']['Enable'] = True
        self['ColourToolTip']['Width'] = 100
        self['ColourToolTip']['Height'] = 75
        self['ColourToolTip']['RectRounded'] = True
        self['ColourToolTip']['RectRoundedRadius'] = 5
        self['ColourToolTip']['RectLineColour'] = '#000000'
        self['ColourToolTip']['RectLineWidth'] = 5
        self['ColourToolTip']['ShowHex'] = False
        self['ColourToolTip']['ShowName'] = True
        self['ColourToolTip']['ShowDec'] = False
        self['ColourToolTip']['DelayShow'] = DELAY['CTS']
        self['ColourToolTip']['DelayHide'] = DELAY['CTH']

        self['TopLineToolTip'] = {}
        self['TopLineToolTip']['Enable'] = True
        # self['TopLineToolTip'][NOT_IMPL+'Border'] = 'DEFAULT|NONE|RAISED|SIMPLE|STATIC|SUNKEN'
        self['TopLineToolTip']['ForeColour'] = '#0000FF'
        self['TopLineToolTip']['BackColour'] = CLR['BLUE2']
        self['TopLineToolTip']['UseFade'] = False
        self['TopLineToolTip']['DropShadow'] = False
        # self['TopLineToolTip'][NOT_IMPL+'Position'] = 'TL|TR|BL|BR'  # Top, Left, Bottom, Right
        self['TopLineToolTip']['Text'] = 'Top Line\r\n<hr>\r\nDocument  %7d\r\nDisplay   %7d\r\n\r\nLeft Col  %7d\r\n'
        self['TopLineToolTip'].comments['Text'].insert(0,
            'at start of line: <hr>=Horizontal Rule, </b>=Bold, </l>=hyperLink'
        )
        self['TopLineToolTip']['DelayHide'] = DELAY['TLH']
#     self['TopLineToolTip']['LeftColText'] = ' Left Col: %7d \n'

#TODO, put search history in 'conf\SPyE.(sch|his)' (no .default?):
#TODO,    'FindHistory', 'WhereHistory', 'ReplaceHistory'
        self['FindHistory'] = {}
        # self['FindHistory'][NOT_IMPL+'Enable'] = True
        # self['FindHistory'][NOT_IMPL+'MaxItems'] = 100

        self['WhereHistory'] = {}
        # self['WhereHistory'][NOT_IMPL+'Enable'] = True
        # self['WhereHistory'][NOT_IMPL+'MaxItems'] = 100

        self['ReplaceHistory'] = {}
        # self['ReplaceHistory'][NOT_IMPL+'Enable'] = True
        # self['ReplaceHistory'][NOT_IMPL+'MaxItems'] = 100

        self['Layout'] = {}
        self['Layout']['Caption'] = True
        self['Layout']['MenuBar'] = True
        self['Layout']['ToolBar'] = True
        self['Layout']['InfoBar'] = True
        self['Layout']['StatusBar'] = True
        self['Layout']['MenuIcons'] = False
        self['Layout']['MenuIconsCustomCheckable'] = False
        self['Layout']['MenuHelpText'] = True
        self['Layout']['PageTabs'] = True
        self['Layout']['PageTabTheme'] = True
        self['Layout']['PageTabIcons'] = True
        self['Layout']['ToolTips'] = True
        self['Layout']['FullScreen'] = False
        self['Layout']['DistractionFree'] = False
        # self['Layout'][NOT_IMPL+'MenuItemHelp'] = True  # statusbar: toggle short menu help visibility
        # self['Layout'].comments[NOT_IMPL+'MenuItemHelp'].insert(0,
        #     'short help text for selected menu item in statusbar'
        # )

        self['PanelEffect'] = {}
        self['PanelEffect']['Enable'] = False
        self['PanelEffect']['Duration'] = 200
        self['PanelEffect'].comments['Duration'].insert(0,
            'Animation duration (ms): 200=default, 0=current platform\'s default'
        )
        self['PanelEffect']['Choice'] = wx.SHOW_EFFECT_NONE

        self['Ruler'] = {}                        # rlr
        self['Ruler']['Enable'] = False
        self['Ruler']['Swap'] = False
        self['Ruler']['SashPos'] = SASH_POS['RLR']
        self['Ruler']['LineBottom'] = True
        self['Ruler']['LineColour'] = '#006400'
        self['Ruler']['BackColour'] = CLR['BLUE2']
        self['Ruler']['TickLeftHeight'] = 25
        self['Ruler']['TickLeftColour'] = '#A9A9A9'
        self['Ruler']['TickMaxHeight'] = 9
        self['Ruler'].comments['TickMaxHeight'].insert(0,
            'TickMaxHeight (pixels): 9=default, [1-18]=visible, 0=invisible'
        )
#FIX, create 'TickColour': make list of 3 values and remove '[Large|medium|small]TickColour'
        self['Ruler']['TickLargeColour'] = '#FFFF00'
        self['Ruler']['TickMediumColour'] = '#0000FF'
        self['Ruler']['TickSmallColour'] = '#A9A9A9'
        self['Ruler']['TextFontSize'] = 10
        self['Ruler'].comments['TextFontSize'].insert(0,
            'TextFontSize (pixels): 10=default, [8-18]=visible, 0=invisible'
        )
        self['Ruler']['TextColour'] = '#0000FF'
        self['Ruler']['CaretColour'] = '#0000FF'
        self['Ruler']['CaretType'] = 'TRIANGLE_SMALL'  # TRIANGLE|BLOCK|LINE[_SMALL]

        self['SidePanel'] = {}                    # spn
        self['SidePanel']['Enable'] = False
        self['SidePanel']['Swap'] = False
        # self['SidePanel'][NOT_IMPL+'BackColour'] = TXT_NIL
        # self['SidePanel'][NOT_IMPL+'ForeColour'] = TXT_NIL
        self['SidePanel']['SashPos'] = SASH_POS['SPN']
        self['SidePanel']['Choice'] = SPT.DOC.idx
        self['SidePanel']['ListFilterBackColour'] = CLR['BLUE2']

#TODO, naming: use 'SidePanelTool' or section per 'tool'
        self['SidePanelTool'] = {}
        # self['SidePanelTool'][NOT_IMPL+'Border'] = 'DEFAULT|NONE|RAISED|SIMPLE|STATIC|SUNKEN'
        # self['SidePanelTool'][NOT_IMPL+'BackColour'] = TXT_NIL
        # self['SidePanelTool'][NOT_IMPL+'ForeColour'] = TXT_NIL

        self['Filter'] = {}
        self['Filter']['Document'] = TXT_NIL
        self['Filter']['Bookmark'] = TXT_NIL
        # self['Filter']['Explorer'] = TXT_NIL
        # self['Filter']['Symbol'] = TXT_NIL
        self['Filter']['Macro'] = TXT_NIL
        self['Filter']['Task'] = TXT_NIL
        self['Filter']['Breakpoint'] = TXT_NIL
        self['Filter']['Debug'] = TXT_NIL
        # self['Filter']['DocMap'] = TXT_NIL
        self['Filter']['Config'] = TXT_NIL
        self['Filter']['Help'] = TXT_NIL
        self['Filter']['Pylint'] = TXT_NIL
        self['Filter']['Pyflakes'] = TXT_NIL
        self['Filter']['Pycodestyle'] = TXT_NIL
        self['Filter']['Vulture'] = TXT_NIL

        self['Document'] = {}
        self['Document']['ListRowColour'] = CLR['BLUE']
        self['Document']['ListRowAltColour'] = CLR['BLUE2']
        self['Document']['HoverSelect'] = False
        self['Document']['NeedCtrlKey'] = True
        self['Document']['SingleClick'] = True

        self['Project'] = {}

        self['Bookmark'] = {}
        self['Bookmark']['Symbol'] = MRK['BMK']['SYM']
        self['Bookmark']['OuterColour'] = '#0000FF'  # CLR['BLUE2']
        self['Bookmark']['InnerColour'] = '#0000FF'  # GREEN
        self['Bookmark']['ListRowColour'] = CLR['BLUE2']
        self['Bookmark']['ListRowAltColour'] = CLR['GREEN2']
        self['Bookmark']['HoverSelect'] = False
        self['Bookmark']['NeedCtrlKey'] = True
        self['Bookmark']['SingleClick'] = True
        self['Bookmark']['SearchWrap'] = False
        self['Bookmark']['CentreCaret'] = False
        self['Bookmark'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self['Bookmark']['ShowPanel'] = False
        self['Bookmark'].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self['Bookmark']['SyncPanel'] = False
        self['Bookmark'].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        self['Explorer'] = {}

        self['SymbolDef'] = {}
        self['SymbolDef']['ShowIcons'] = True
        self['SymbolDef']['HoverSelect'] = False
        self['SymbolDef']['NeedCtrlKey'] = True
        self['SymbolDef']['SingleClick'] = True
        self['SymbolDef']['CentreCaret'] = False
        self['SymbolDef'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )

        self['Macro'] = {}
#TODO, maybe toggle 'Macro' menu visibility
        # self['Macro'][NOT_IMPL+'Enable'] = True
        self['Macro']['ListRowColour'] = CLR['GREEN']
        self['Macro']['ListRowAltColour'] = CLR['BLUE2']
        self['Macro']['HoverSelect'] = False
        self['Macro']['NeedCtrlKey'] = True
        self['Macro']['SingleClick'] = True

        self['Task'] = {}
        self['Task']['Symbol'] = MRK['TSK']['SYM']
        self['Task']['ShowMarker'] = False
        self['Task']['OuterColour'] = '#FF0000'
        self['Task']['InnerColour'] = '#FF0000'
        self['Task']['ListRowColour'] = CLR['GREEN']
        self['Task']['ListRowAltColour'] = CLR['GREEN2']
        self['Task']['HoverSelect'] = False
        self['Task']['NeedCtrlKey'] = True
        self['Task']['SingleClick'] = True
        self['Task']['SearchWrap'] = False
        self['Task']['CentreCaret'] = False
        self['Task'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self['Task']['ShowPanel'] = False
        self['Task'].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self['Task']['SyncPanel'] = False
        self['Task'].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        self['Breakpoint'] = {}
        self['Breakpoint']['Symbol'] = MRK['BPT']['SYM']
        self['Breakpoint']['OuterColour'] = '#FFFF00'
        self['Breakpoint']['InnerColour'] = '#FFFF00'
        self['Breakpoint']['ListRowColour'] = CLR['PURPLE']
        self['Breakpoint']['ListRowAltColour'] = CLR['GREEN2']
        self['Breakpoint']['HoverSelect'] = False
        self['Breakpoint']['NeedCtrlKey'] = True
        self['Breakpoint']['SingleClick'] = True
        self['Breakpoint']['SearchWrap'] = False
        self['Breakpoint']['CentreCaret'] = False
        self['Breakpoint'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self['Breakpoint']['ShowPanel'] = False
        self['Breakpoint'].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self['Breakpoint']['SyncPanel'] = False
        self['Breakpoint'].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        self['Debug'] = {}
        self['Debug']['ListRowColour'] = CLR['YELLOW']
        self['Debug']['ListRowAltColour'] = CLR['ORANGE']
        self['Debug']['HoverSelect'] = False
        self['Debug']['NeedCtrlKey'] = True
        self['Debug']['SingleClick'] = True

        self['Config'] = {}
        self['Config']['SectionSelBackColour'] = '#0000FF'
        self['Config']['KeySelBackColour'] = '#A020F0'
        self['Config']['ListRowColour'] = CLR['GREY1']
        self['Config']['ListRowAltColour'] = CLR['BLUE2']
        self['Config']['HoverSelect'] = False
        self['Config']['NeedCtrlKey'] = True
        self['Config']['SingleClick'] = True
        self['Config']['CentreCaret'] = False
        self['Config'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )

        self['Help'] = {}
        self['Help']['QuestionMarkButton'] = False
        self['Help']['ContextSensitiveMode'] = False
        self['Help']['CheckForUpdates'] = False
        self['Help']['ListRowColour'] = CLR['ORANGE2']
        self['Help']['ListRowAltColour'] = CLR['BLUE2']
        self['Help']['HoverSelect'] = False
        self['Help']['NeedCtrlKey'] = True
        self['Help']['SingleClick'] = True

        self['Pylint'] = {}
        # self['Pylint']['Symbol'] = MRK['BPT']['SYM']
        # self['Pylint']['OuterColour'] = '#FFFF00'
        # self['Pylint']['InnerColour'] = '#FFFF00'
        self['Pylint']['ListRowColour'] = CLR['GREY1']
        self['Pylint']['ListRowAltColour'] = CLR['BLUE2']
        self['Pylint']['HoverSelect'] = False
        self['Pylint']['NeedCtrlKey'] = True
        self['Pylint']['SingleClick'] = True
        # self['Pylint']['SearchWrap'] = False
        self['Pylint']['CentreCaret'] = False
        self['Pylint'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self['Pylint']['ShowPanel'] = False
        self['Pylint'].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self['Pylint']['SyncPanel'] = False
        self['Pylint'].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        self['Pyflakes'] = {}
        # self['Pyflakes']['Symbol'] = MRK['BPT']['SYM']
        # self['Pyflakes']['OuterColour'] = '#FFFF00'
        # self['Pyflakes']['InnerColour'] = '#FFFF00'
        self['Pyflakes']['ListRowColour'] = CLR['GREY1']
        self['Pyflakes']['ListRowAltColour'] = CLR['BLUE2']
        self['Pyflakes']['HoverSelect'] = False
        self['Pyflakes']['NeedCtrlKey'] = True
        self['Pyflakes']['SingleClick'] = True
        # self['Pyflakes']['SearchWrap'] = False
        self['Pyflakes']['CentreCaret'] = False
        self['Pyflakes'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self['Pyflakes']['ShowPanel'] = False
        self['Pyflakes'].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self['Pyflakes']['SyncPanel'] = False
        self['Pyflakes'].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        self['Pycodestyle'] = {}
        # self['Pycodestyle']['Symbol'] = MRK['BPT']['SYM']
        # self['Pycodestyle']['OuterColour'] = '#FFFF00'
        # self['Pycodestyle']['InnerColour'] = '#FFFF00'
        self['Pycodestyle']['ListRowColour'] = CLR['GREY1']
        self['Pycodestyle']['ListRowAltColour'] = CLR['BLUE2']
        self['Pycodestyle']['HoverSelect'] = False
        self['Pycodestyle']['NeedCtrlKey'] = True
        self['Pycodestyle']['SingleClick'] = True
        # self['Pycodestyle']['SearchWrap'] = False
        self['Pycodestyle']['CentreCaret'] = False
        self['Pycodestyle'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self['Pycodestyle']['ShowPanel'] = False
        self['Pycodestyle'].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self['Pycodestyle']['SyncPanel'] = False
        self['Pycodestyle'].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        self['Vulture'] = {}
        # self['Vulture']['Symbol'] = MRK['BPT']['SYM']
        # self['Vulture']['OuterColour'] = '#FFFF00'
        # self['Vulture']['InnerColour'] = '#FFFF00'
        self['Vulture']['ListRowColour'] = CLR['GREY1']
        self['Vulture']['ListRowAltColour'] = CLR['BLUE2']
        self['Vulture']['HoverSelect'] = False
        self['Vulture']['NeedCtrlKey'] = True
        self['Vulture']['SingleClick'] = True
        # self['Vulture']['SearchWrap'] = False
        self['Vulture']['CentreCaret'] = False
        self['Vulture'].comments['CentreCaret'].insert(0,
            'CentreCaret: centre caret vertically after successful search'
        )
        self['Vulture']['ShowPanel'] = False
        self['Vulture'].comments['ShowPanel'].insert(0,
            'ShowPanel: show panel when searching'
        )
        self['Vulture']['SyncPanel'] = False
        self['Vulture'].comments['SyncPanel'].insert(0,
            'SyncPanel: sync panel selection when searching'
        )

        self['Markdown'] = {}

        self['Code2flow'] = {}

        self['Snippet'] = {}

        self['CodeContext'] = {}                  # ccx
        self['CodeContext']['Enable'] = False
        self['CodeContext']['Swap'] = False
        self['CodeContext']['SashPos'] = SASH_POS['CCX']
        self['CodeContext']['ForeColour'] = '#000000'
        self['CodeContext']['BackColour'] = CLR['BLUE']
        self['CodeContext']['Font'] = 'Courier New'
        self['CodeContext']['Depth'] = 10  # number of lines, level

        self['SearchPanel'] = {}                  # sch
        self['SearchPanel']['Enable'] = False
        self['SearchPanel']['Swap'] = False
        self['SearchPanel']['SashPos'] = SASH_POS['SCH']['FND']
        self['SearchPanel']['Mode'] = 'FND'
        self['SearchPanel']['HasFocus'] = False
        self['SearchPanel']['IconSize'] = 24  # 16 x 16 | 24 x 24 | 32 x 32
        self['SearchPanel'].comments['IconSize'].insert(0,
            'IconSize (pixels), sizes 16x16|24x24|32x32: 16=small, 24=medium (default), 32=large'
        )
        self['SearchPanel']['LabelFontStyle'] = 'bold'
        self['SearchPanel'].comments['LabelFontStyle'].insert(0,
            'LabelFontStyle: bold (default), see \'LBL_FNT_STYLES\': any combination of bold|italic|large|small|strike|underline'
        )
        self['SearchPanel']['TabTraversalAll'] = False
        self['SearchPanel']['BackColourFND'] = CLR['BLUE']
        self['SearchPanel']['BackColourRPL'] = CLR['RED']
        self['SearchPanel']['BackColourFIF'] = CLR['ORANGE']
        self['SearchPanel']['BackColourINC'] = CLR['BLUE2']
        self['SearchPanel']['BackColourRES'] = '#000000'
        self['SearchPanel']['WarningBackColour'] = CLR['RED3']
        self['SearchPanel']['ErrorBackColour'] = CLR['RED1']
        self['SearchPanel']['DelayDefaultColour'] = 1000
        self['SearchPanel']['Border'] = False
        self['SearchPanel']['FindText'] = TXT_NIL
        self['SearchPanel']['WhereText'] = TXT_NIL
        self['SearchPanel']['ReplaceText'] = TXT_NIL
        # self['SearchPanel'][NOT_IMPL+'IncrementalText'] = TXT_NIL
        self['SearchPanel']['SelectedTextToFind'] = True
        self['SearchPanel']['ShowCheckboxes'] = True
        self['SearchPanel']['ShowCountButton'] = False
        self['SearchPanel']['ShowIcons'] = True
        self['SearchPanel']['CaseSensitive'] = False
        self['SearchPanel']['RegularExpression'] = False
        self['SearchPanel']['WholeWord'] = False
        self['SearchPanel']['WrapAround'] = False
        self['SearchPanel']['InSelection'] = False
        self['SearchPanel']['HighlightMatches'] = False
        self['SearchPanel']['PreserveCase'] = False
        self['SearchPanel']['ShowContext'] = False
        self['SearchPanel']['UseBuffer'] = False
        # self['SearchPanel'][NOT_IMPL+'CentreFoundLine'] = True
        # self['SearchPanel'][NOT_IMPL+'CentreFoundColumn'] = True

#TODO, naming: use 'SidePanelTool' or section per 'tool'
        self['DocMap'] = {}
        self['DocMap']['ZoneRectRounded'] = False
        self['DocMap']['ZoneRectRoundedRadius'] = 5
        self['DocMap']['ZoneRectLineColour'] = CLR['BLUE6']
        self['DocMap']['ZoneRectLineStyle'] = wx.PENSTYLE_SOLID
        self['DocMap']['ZoneRectLineWidth'] = 1

        self['DocMap']['ZoneFillColour'] = CLR['ORANGE']
        self['DocMap']['ZoneFillAlpha'] = 64

        self['DocMap']['ZoneCentreLine'] = True
        self['DocMap']['ZoneCentreLineColour'] = '#FF0000'
        self['DocMap']['ZoneCentreLineStyle'] = wx.PENSTYLE_DOT
        self['DocMap']['ZoneCentreLineWidth'] = 1

        self['DocMap']['ZoneCentreDot'] = True
        self['DocMap']['ZoneCentreDotColour'] = '#0000FF'
        self['DocMap']['ZoneCentreDotRadius'] = 2

        # self['DocMap']['ScrollNumLinesWheel'] = 10
        # self['DocMap']['ScrollNumLinesEdge'] = 25
        # self['DocMap']['ScrollFactorWheel'] = 11  # higher value: finer wheel scroll whilst nearing edge

        self['DocMap']['EdgeTextIndicator'] = True
        self['DocMap']['EdgeTextTop'] = ' [ Top ] '
        self['DocMap']['EdgeTextBottom'] = ' [ Bottom ] '
        self['DocMap']['EdgeTextFont'] = 'Courier New'
        self['DocMap']['EdgeTextFontSize'] = 10
        self['DocMap']['EdgeTextForeColour'] = '#0000FF'
        self['DocMap']['EdgeTextBackColour'] = CLR['ORANGE3']
        # self['DocMap'][NOT_IMPL+'EdgeTextPosition'] = 'TL|TR|BL|BR'  # Top, Left, Bottom, Right

#DONE, add code for 'Cursor' and 'ToolTip' properties in 'sidepanel.py'
        # self['DocMap']['CursorTypeNormal'] = wx.CURSOR_ARROW
        # self['DocMap']['CursorTypeHover'] = wx.CURSOR_SIZENS
        # self['DocMap']['CursorTypeDrag'] = wx.CURSOR_HAND
        # self['DocMap']['CursorTypeScroll'] = wx.CURSOR_WAIT
        # self['DocMap']['CursorTypeEdge'] = wx.CURSOR_NO_ENTRY

        # self['DocMap']['CursorTypeHoverShow'] = True
        # self['DocMap']['CursorTypeDragShow'] = True

        # self['DocMap']['ToolTipHoverShow'] = True
        # self['DocMap']['ToolTipDragShow'] = True  # naming: ['TopLineToolTip']?

#TODO, add code END #####
        self['DocMap']['AutoFocus'] = True
        self['DocMap']['MarkerLineHighlight'] = False
#INFO, URL=https://wxpython.org/Phoenix/docs/html/wx.RasterOperationMode.enumeration.html
        # self['DocMap']['RasterOperationMode'] = wx.AND  # wx.INVERT
        self['DocMap']['SnapCursorAtDragStart'] = True

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

        self['CodePreview'] = {}
        self['CodePreview']['Enable'] = False
        self['CodePreview']['Caption'] = False
        self['CodePreview']['Border'] = False
        self['CodePreview']['BorderWidth'] = 2
        self['CodePreview']['BorderColour'] = CLR['BLUE1']
        self['CodePreview']['DropShadow'] = False
        self['CodePreview']['Margin'] = False
        self['CodePreview']['Width'] = 0.8
        self['CodePreview']['Height'] = 10
        self['CodePreview']['ShowOverZone'] = False

    def create(self):
        # from conf.debug import DEBUG
        if DEBUG['CFG']: print(f'{me_()}\n  File = {self.filename}\n')

        # get default configuration
        self.default()

        # add blank lines and header before all sections, except the first
        first_sec = 'General'
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Comment header for %s' % sec)

        self.commit()

    def read(self):
        # from conf.debug import DEBUG
        if DEBUG['CFG']: print(f'{me_()}\n  File = {self.filename}\n')

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
                key = 'File' + str(cnt)
                if key in glb.SSN[sec]:
                    pnm, vis, pos, lin, col, lng, wrp, eol, wsp, tbu, tbw, ofs, sel_str, bmk_str, bpt_str = glb.SSN[sec][key].split('|')
                    sel_lst = literal_eval(sel_str)  # string -> tuple
                    bmk_lst = literal_eval(bmk_str)  # string -> list
                    bpt_lst = literal_eval(bpt_str)  # string -> list
                    self.fil_lst.append([pnm, vis, pos, lin, col, lng, wrp, eol, wsp, tbu, tbw, ofs, sel_lst, bmk_lst, bpt_lst])
                else:
                    break
                cnt += 1
            if DEBUG['CFG']: print('\n    fil_lst = %s\n' % self.fil_lst)
        else:
            for sec in ['SearchPanel', 'Ruler', 'SidePanel', 'CodeContext']:
                self[sec]['Enable'] = False

        # create list of last session's recent files
        if glb.RFH['RecentFileHistory']['Enable']:
            sec = 'RecentFiles'
            cnt = 0
            while True:
                key = 'File' + str(cnt)
                if key in glb.RFH[sec]:
                    pnm = glb.RFH[sec][key]
                    self.rfh_lst.append(pnm)
                else:
                    break
                cnt += 1
            if DEBUG['CFG']: print('\n  rfh_lst = %s\n' % self.rfh_lst)

#FIX, not used: obsolete/redundant?
    def commit(self):
        # from conf.debug import DEBUG
        if DEBUG['CFG']: print(f'{me_()}\n  File = {self.filename}\n')
        if DEBUG['CFG'] > 1: beeprint.pp(self, sort_keys=False)
        self.write()

    def apply(self):
        # convenience: use locals from GLOBALS
        tlw, spl, mb, tb, ib, sb, nbk, spn, sch = \
            glb.TLW, glb.SPL, glb.MB, glb.TB, glb.IB, glb.SB, glb.NBK, glb.SPN, glb.SCH

        if DEBUG['APP']: print(f'\nCFG: {wx.GetApp().ready = }\n')

        tlw.Freeze()

        if DEBUG['CFG']: print(f'{me_()}')
        if DEBUG['CFG'] > 1: beeprint.pp(self, sort_keys=False)

        # restore main menu item check marks:
        # - toolbar, statusbar, panels, page tabs, tooltips, full screen
        mb.Check(MI['LAY_CAP'], self['Layout']['Caption'])
        mb.Check(MI['LAY_MBR'], self['Layout']['MenuBar'])
        mb.Check(MI['LAY_TBR'], self['Layout']['ToolBar'])
        mb.Check(MI['LAY_IBR'], self['Layout']['InfoBar'])
        mb.Check(MI['LAY_SBR'], self['Layout']['StatusBar'])
        mb.Check(MI['LAY_SCH'], self['SearchPanel']['Enable'])
        mb.Check(MI['LAY_RLR'], self['Ruler']['Enable'])
        mb.Check(MI['LAY_SPN'], self['SidePanel']['Enable'])
        mb.Check(MI['LAY_CCX'], self['CodeContext']['Enable'])
        # chc = int(MI['PEF_NON']) + self['PanelEffect']['Choice']
        # mb.Check(chc, True)
        mb.Check(MI['LAY_MIC'], self['Layout']['MenuIcons'])
        mb.Check(MI['LAY_MIK'], self['Layout']['MenuIconsCustomCheckable'])
        mb.Check(MI['LAY_MHT'], self['Layout']['MenuHelpText'])
        mb.Check(MI['LAY_PTB'], self['Layout']['PageTabs'])  # , nbk.TabCtrlHeight)
        nbk.SetTabCtrlHeight(-1 if mb.IsChecked(MI['LAY_PTB']) else 0)
        mb.Check(MI['LAY_PTT'], self['Layout']['PageTabTheme'])
        mb.Check(MI['LAY_PTI'], self['Layout']['PageTabIcons'])
        mb.Check(MI['LAY_TTP'], self['Layout']['ToolTips'])
        mb.Check(MI['LAY_ACP'], self['AutoComplete']['Enable'])
        mb.Check(MI['LAY_CTP'], self['CallTip']['Enable'])
        mb.Check(MI['LAY_TLT'], self['TopLineToolTip']['Enable'])
        nbk.tlt.EnableTip(bool(mb.IsChecked(MI['LAY_TLT'])))
        mb.Check(MI['LAY_CTT'], self['ColourToolTip']['Enable'])
        mb.Check(MI['LAY_SPU'], self['SymbolPopup']['Enable'])
        mb.Check(MI['LAY_FUL'], self['Layout']['FullScreen'])

        # restore margins
#FIX, use 'update_margins' to derive 'All' value
    #     mb.Check(MI['MGN_ALL'], self['Margin']['All'])
        mb.Check(MI['MGN_NUM'], self['Margin']['LineNumber'])
        mb.Check(MI['MGN_SYM'], self['Margin']['Symbol'])
        mb.Check(MI['MGN_FOL'], self['Margin']['Folding'])
        update_margins()
#TODO, add fold_style to 3 docstate methods, FOR NOW it is GLOBAL
        self['Margin']['FoldingStyle'] = FOL_STYLE

        # restore edge
        val = self['Edge']['Mode']
        if val == stc.STC_EDGE_NONE:
            mb.Check(MI['EDG_NON'], True)
        elif val == stc.STC_EDGE_BACKGROUND:
            mb.Check(MI['EDG_BCK'], True)
        elif val == stc.STC_EDGE_LINE:
            mb.Check(MI['EDG_LIN'], True)
        # elif val == 3:
        # # elif val == stc.STC_EDGE_MULTILINE:
        #     mb.Check(MI['EDG_MUL'], True)
        # doc.SetEdgeMode(val)

        # restore indentation guides
        val = self['Indentation']['Guides']
        if val == stc.STC_IV_LOOKBOTH:
            mb.Check(MI['IND_GDS'], True)
        else:
            mb.Check(MI['IND_GDS'], False)

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
        mb.Check(mni, True)

        # restore BRIEF keys, caret line and sticky
        mb.Check(MI['CRT_BRF'], self['Caret']['HomeEndKeysBRIEF'])
        mb.Check(MI['CRT_LIN'], self['Caret']['LineVisible'])
        val = self['Caret']['Sticky']
        if val == stc.STC_CARETSTICKY_ON:
            mb.Check(MI['CRT_STK'], True)
        else:
            mb.Check(MI['CRT_STK'], False)

        # restore general settings
        sty = tlw.WindowStyle
        if self['Window']['OnTop']:
            tlw.SetWindowStyle(sty | wx.STAY_ON_TOP)
            mb.Check(MI['WIN_TOP'], True)
        else:
            tlw.SetWindowStyle(sty & ~wx.STAY_ON_TOP)
            mb.Check(MI['WIN_TOP'], False)
        tlw.DragAcceptFiles(self['Window']['DragAcceptFiles'])
        if self['Window']['Transparency']:
            tlw.SetTransparent(self['Window']['TransparencyAlpha'])
        if self['General']['DetectFileChange']:
            detect_file_change(self['General']['DelayDetectFileChange'])

        # restore tooltip settings
        # ALL - but TOOLBAR - tooltips are handled GLOBALLY
        wx.ToolTip.Enable(mb.IsChecked(MI['LAY_TTP']))
        wx.ToolTip.SetMaxWidth(self['ToolTip']['MaxWidth'])
        wx.ToolTip.SetDelay(self['ToolTip']['DelayShow'])
        wx.ToolTip.SetAutoPop(self['ToolTip']['DelayHide'])
        wx.ToolTip.SetReshow(self['ToolTip']['DelayReshow'])

        # restore toolbar tooltips SEPARATELY
        sty = tb.WindowStyle
        if mb.IsChecked(MI['LAY_TTP']):
            tb.SetWindowStyle(sty & ~wx.TB_NO_TOOLTIPS)
        else:
            tb.SetWindowStyle(sty | wx.TB_NO_TOOLTIPS)

        # restore caption/menu-/tool-/info-/statusbar
        sty, cap = tlw.WindowStyle, wx.CAPTION
        tlw.SetWindowStyle(sty | cap if mb.IsChecked(MI['LAY_CAP']) else sty & ~cap)
        mb.Show(mb.IsChecked(MI['LAY_MBR']))
        tb.Show(mb.IsChecked(MI['LAY_TBR']))

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # ib.Show(mb.IsChecked(MI['LAY_IBR']))
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        sb.Show(mb.IsChecked(MI['LAY_SBR']))

    #     tlw.XXX = self['SearchPanel']['CentreFoundLine']
    #     tlw.YYY = self['SearchPanel']['CentreFoundColumn']

        # restore search state
        sch.txc_fnd.Value = str(self['SearchPanel']['FindText'])
        sch.txc_whr.Value = str(self['SearchPanel']['WhereText'])
        sch.txc_rpl.Value = str(self['SearchPanel']['ReplaceText'])

#TODO, INCREMENTAL not implemented
        # sch.txc_inc.Value = str(self['SearchPanel']['IncrementalText'])

        sch.cbx_cas.Value = self['SearchPanel']['CaseSensitive']
        mb.Check(MI['SCH_CAS'], sch.cbx_cas.Value)
#TODO, REGEX not implemented
        sch.cbx_reg.Value = self['SearchPanel']['RegularExpression']
        mb.Check(MI['SCH_REG'], sch.cbx_reg.Value)
        sch.cbx_wrd.Value = self['SearchPanel']['WholeWord']
        mb.Check(MI['SCH_WRD'], sch.cbx_wrd.Value)
        sch.cbx_wrp.Value = self['SearchPanel']['WrapAround']
        mb.Check(MI['SCH_WRP'], sch.cbx_wrp.Value)

        sch.cbx_isl.Value = self['SearchPanel']['InSelection']
        mb.Check(MI['SCH_ISL'], sch.cbx_isl.Value)
        sch.cbx_hlm.Value = self['SearchPanel']['HighlightMatches']
        mb.Check(MI['SCH_HLM'], sch.cbx_hlm.Value)
        sch.cbx_pcs.Value = self['SearchPanel']['PreserveCase']
        mb.Check(MI['SCH_PCS'], sch.cbx_pcs.Value)

        sch.cbx_cxt.Value = self['SearchPanel']['ShowContext']
        mb.Check(MI['SCH_CXT'], sch.cbx_cxt.Value)
        sch.cbx_buf.Value = self['SearchPanel']['UseBuffer']
        mb.Check(MI['SCH_BUF'], sch.cbx_buf.Value)

        # restore panel state
        for sec, pnl in (('SearchPanel', 'SCH'), ('Ruler',       'RLR'),
                         ('SidePanel',   'SPN'), ('CodeContext', 'CCX')):
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
            sch.set_mode(self['SearchPanel']['Mode'])
            # set focus on active file
            for __, doc in nbk.open_docs():
                if glb.SSN['Session']['ActiveFile'] == doc.pnm:
                    # nbk.SetSelection(0)  # set 1st tab visible
                    # focus on active tab
                    dbg_FOCUS(doc)
                    # ... and on search panel
                    if self['SearchPanel']['HasFocus']:
                        dbg_FOCUS(sch)
                        # sch.txc_fnd.SelectAll()
                    break

        tlw.Thaw()

        nbk.make_tab_visible()

        if DEBUG['APP']: wx.GetApp().ready = True
        if DEBUG['APP']: print(f'CFG: {wx.GetApp().ready = }\n')


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
        import re
        match = re.search(r'^#(?:[0-9a-fA-F]{2}){3}$', value)
        # by name
        if not match:
#NOTE, avoid error 'wx._core.PyNoAppError: The wx.App object must be created first!'
            app = wx.App()
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
        pass
        return True


def is_font(value):
#NOTE, avoid error 'wx._core.PyNoAppError: The wx.App object must be created first!'
    app = wx.App()
    fne = FontEnum()
    # print(fne)
    # pprint(fne.GetFacenames(fixedWidthOnly=True))
    fne.EnumerateFacenames()
    return value

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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
