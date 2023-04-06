#!/usr/bin/python

"""SPyE: ConfigObj default SPEC file

Scintilla/Python based Editor
"""


CFG_SPEC = """
# {tip}F|P=Filename|Pathname, S=Size, T=Type, C=Created, M=Modified, A=Accessed, B|L=key|description (Attributes){tip}
[General]
# {lbl}[lbl1] -> AppRedirectOutput{lbl}
# {tip}[tip1] ->    AppRedirectOutput|^AppRedirectOutput|^^AppRedirectOutput|^^^{tip} =>> [tip1]
# {hidden}
AppRedirectOutput = boolean(default=False)
# {lbl}[lbl2] -> AppRedirectOutputFile{lbl}
# {tip}[tip2] ->    AppRedirectOutputFile AppRedirectOutputFile|   AppRedirectOutputFile|{tip} =>> [tip2]
# {hidden}
AppRedirectOutputFile = string(default='')
# {lbl}[lbl3] -> AppUseBestVisual{lbl}
# {tip}[tip3] ->    AppUseBestVisual AppUseBestVisual|   AppUseBestVisual|{tip} =>> [tip3]
# {hidden}
AppUseBestVisual = boolean(default=False)
# {lbl}[lbl4] -> AppClearSigInt{lbl}
# {tip}[tip4] ->    AppClearSigInt AppClearSigInt|   AppClearSigInt|{tip} =>> [tip4]
# {hidden}
AppClearSigInt = boolean(default=True)
# {lbl}[lbl5] -> OpenSession{lbl}
# {tip}[tip5] ->    OpenSession|^OpenSession|^^OpenSession|^^^{tip} =>> [tip5]
OpenSession = boolean(default=True)
Theme = string(default=Default)
NewFilePrefix = string(default=Edit)
NewFileAtCloseLast = boolean(default=True)
SystemTrayMenu = boolean(default=False)
GlobalHotKey = string(default=Ctrl+Alt+Win+S)
AcceleratorTable = boolean(default=False)
MultiInstance = boolean(default=False)
DetectFileChange = boolean(default=False)
DelayDetectFileChange = integer(default=5000)
UIEventUpdateInterval = integer(min=-1, max=1000, default=200)
UIEventProcessSpecified = boolean(default=False)
DetectFileReadOnly = boolean(default=True)
DocModifiedIndicator = string(min=2, max=2, default=' *')
DocReadOnlyIndicator = string(min=2, max=2, default=' #')
DialogBackColour = colour(default='#E6F2FF')
OeufDePaques = boolean(default=False)
FlushClipboard = boolean(default=True)
OpenFileListSort = boolean(default=False)


[Splash]
Enable = boolean(default=False)
DelayHide = integer(default=3000)
Welcome = boolean(default=False)


[WidgetInspectionTool]
Enable = boolean(default=False)
ShortCut = string(default=Ctrl+Alt+Shift+I)
ShowAtStartup = boolean(default=False)
PreSelectObject = string(default=TLW)
RefreshWidgetTree = boolean(default=True)


[Window]
PositionX = integer(default=940)
PositionY = integer(default=0)
Width = integer(default=987)
Height = integer(default=1057)
OnTop = boolean(default=True)
DragAcceptFiles = boolean(default=True)
Transparency = boolean(default=True)
TransparencyAlpha = integer(default=255)


[ContextMenu]
Enable = boolean(default=True)
ShowTitle = boolean(default=True)
TitleBackColour = colour(default='#DFDFDF')
LeftClick = boolean(default=False)
MenuBar = boolean(default=True)
ToolBar = boolean(default=True)
InfoBar = boolean(default=True)
StatusBar = boolean(default=True)
PanelSwitcher = boolean(default=True)
SearchFlags = boolean(default=True)
FileEncoding = boolean(default=True)
EndOfLine = boolean(default=True)
Indentation = boolean(default=True)
Language = boolean(default=True)
Notebook = boolean(default=True)
Editor = boolean(default=True)
Margin = boolean(default=True)
Ruler = boolean(default=True)
CodeContext = boolean(default=True)
BookmarkList = boolean(default=True)
SymbolDef = boolean(default=True)
TaskList = boolean(default=True)
BreakpointList = boolean(default=True)
DocMap = boolean(default=True)
# SearchPanel = boolean(default=True)
SearchResults = boolean(default=True)
FindHistory = boolean(default=True)
ReplaceHistory = boolean(default=True)
WhereHistory = boolean(default=True)


[Backup]


[ToolBar]
Tools = list(default=list(SEP, NEW, OPN, SAV, SAS, CLS, SEP, CUT, CPY, PST, SEP, UDO, RDO, SEP, FND, NXT, RPL, PRV, SEP, FXP, SDF, SEP, BRC, SRT, SUM, SEP, FUL, SEP, PRF, SEP, SCH))
BackColour = colour(default='#E6F2FF')
TextFontSize = integer(default=7)
LargeTextFontSize = integer(default=9)
ShowIcons = boolean(default=True)
ShowText = boolean(default=True)
LargeIcons = boolean(default=False)
LargeText = boolean(default=False)
AlignHorizontally = boolean(default=False)
Top = boolean(default=True)
Left = boolean(default=False)
Bottom = boolean(default=False)
Right = boolean(default=False)


[InfoBar]
CloseButton = boolean(default=False)
Position = option('TOP', 'BOTTOM')
ForeColour = colour(default='#0000FF')
BackColour = colour(default='#E6F2FF')
WarningBackColour = colour(default='#FF6060')
ErrorBackColour = colour(default='#FF0000')
DelayHide = integer(default=2000)
Font = font(default=Consolas)
FontSize = integer(default=11)
FontBold = boolean(default=False)
FontItalic = boolean(default=False)


[StatusBar]
Fields = list(default=list(PSW, MSG, AUX, LNC, INS, CNS, SCH, FSZ, ENC, EOL, IND, LNG, TIM))
Border = boolean(default=True)
SizeGrip = boolean(default=True)
ToolTips = boolean(default=True)
BackColour = colour(default='#E6F2FF')
ErrorBackColour = colour(default='#FF0000')
WarningBackColour = colour(default='#FFE7CE')
FullScreenBackColour = colour(default='#71B3E8')
DelayClearFieldMSG = integer(default=5000)
DelayClearFieldAUX = integer(default=500)
ClockTimeSeconds = boolean(default=False)
ClockTimeColonBlink = boolean(default=False)


[Indentation]
Title = string(default=Indentation)
TitleFontStyle = list(default=list(bold, large))
TabIndents = boolean(default=True)
BackSpaceUnIndents = boolean(default=True)
UseTabs = boolean(default=False)
TabWidth = integer(default=4)
Size = integer(default=4)
Auto = boolean(default=False)
Smart = boolean(default=False)
Guides = integer(default=0)
GuidesForeColour = colour(default='#FF0000')
GuidesBackColour = colour(default='#FFFFFF')


[Language]
KeywordSetsAsSubMenu = boolean(default=True)
KeywordSetsInMenuBar = boolean(default=False)
NewFile = option('CURRENT', 'TEXT')
ListRowColour = colour(default='#C0C0C0')
ListRowAltColour = colour(default='#C6E2FF')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)


[Splitter]
Border = boolean(default=False)
LiveUpdate = boolean(default=False)
SashDoubleClickIsClose = boolean(default=True)


[Notebook]
BackgroundImage = boolean(default=False)
ArtProviderTheme = option('DEFAULT', 'SIMPLE')
PageTabIconSize = integer(default=16)
ForeColour = colour(default='#FF0000')
BackColour = colour(default='#FFFFF0')
TabColour = colour(default='#C6E2FF')
TabActiveColour = colour(default='#FFFFF0')
TabPosition = option('TOP', 'BOTTOM')
TabDragSplit = boolean(default=True)
TabDragMove = boolean(default=True)
TabCloseButton = boolean(default=False)
TabCloseButtonOnActive = boolean(default=True)
TabCloseButtonOnAll = boolean(default=True)
TabScrollButtons = boolean(default=True)
TabWindowListButton = boolean(default=True)
TabFixedWidth = boolean(default=False)
TabMiddleClickIsClose = boolean(default=True)
TabRightClickIsSelect = boolean(default=True)
TabToolTipFileInfo = string(default=FSM)


[PageTabHistory]
Enable = boolean(default=True)
CacheSize = integer(default=10)
CacheSizeIncrease = integer(default=5)
CacheSizeDecrease = integer(default=5)
Stack = list(default=[])


[Editor]
SelectionEOLFilled = boolean(default=False)
EOLMode = integer(default=0)
ZoomLevel = integer(default=0)
RevertConfirm = boolean(default=True)
DefaultBackColour = colour(default='#E6F2FF')
TimestampFormat = string(default=%Y-%m-%d %H:%M:%S)
BufferedDraw = boolean(default=True)
Technology = integer(default=1)
VirtualSpaceOptions = integer(default=1)
HorizontalScrollBar = boolean(default=True)
VerticalScrollBar = boolean(default=True)
ScrollWidthTracking = boolean(default=True)
EndAtLastLine = boolean(default=True)
WhitespaceSize = integer(default=2)


[MultiEdit]
Selection = boolean(default=True)
Typing = boolean(default=True)
SelForeColour = colour(default='#FFFFFF')
SelBackColour = colour(default='#3399FF')
SelAlpha = integer(default=256)
ExtraSelForeColour = colour(default='#FFFFFF')
ExtraSelBackColour = colour(default='#3399FF')
ExtraSelAlpha = integer(default=256)
ExtraCaretForeColour = colour(default='#0000FF')
ExtraCaretsBlink = boolean(default=True)
ExtraCaretsVisible = boolean(default=True)
Clipboard = boolean(default=False)


[Caret]
ForeColour = colour(default='#0000FF')
HomeEndKeysBRIEF = boolean(default=False)
LineVisible = boolean(default=True)
LineBackColour = colour(default='#FFFFF0')
LineBackAlpha = integer(default=256)
Sticky = integer(default=1)
Period = integer(default=500)
Style = integer(default=1)
Width = integer(default=2)


[CaretPositionHistory]
Enable = boolean(default=True)
MaxItems = integer(default=300)
DelayDefaultStyle = integer(default=500)
ForeColour = colour(default='#00FF00')
Period = integer(default=250)
Style = integer(default=1)
Width = integer(default=3)


[Margin]
LineNumber = boolean(default=True)
LineNumberWidth = integer(default=50)
LineNumberForeColour = colour(default='#000000')
LineNumberBackColour = colour(default='#C0C0C0')
Symbol = boolean(default=True)
SymbolWidth = integer(default=16)
Folding = boolean(default=True)
FoldingWidth = integer(default=16)
FoldingColour = colour(default='#C0C0C0')
FoldingHiColour = colour(default='#C0C0C0')
FoldingStyle = integer(default=3)
FoldingHighlight = boolean(default=False)
LeftWidth = integer(default=0)
RightWidth = integer(default=0)


[Edge]
Mode = integer(default=0)
Column = integer(default=79)
Colour = colour(default='#006400')


[Debugger]
LineBackColour = colour(default='#A020F0')
LineBackAlpha = integer(default=150)
CentreCaret = boolean(default=False)


[AutoComplete]
Enable = boolean(default=False)
MaxHeight = integer(default=15)
MaxWidth = integer(default=0)


[Brace]
Enable = boolean(default=True)
AutoInsert = boolean(default=True)
Pairs = string(default='')
LightForeColour = colour(default='#000000')
LightBackColour = colour(default='#00FF00')
BadForeColour = colour(default='#000000')
BadBackColour = colour(default='#FF0000')


[Indicator]
Enable = boolean(default=True)
MatchSelection = boolean(default=True)
BackColour0 = colour(default='#00FF00')
BackColour1 = colour(default='#9BFFFF')
BackColour2 = colour(default='#FFCD9B')
BackColour3 = colour(default='#FFFF9B')
BackColour4 = colour(default='#CD9BFF')
BackColour5 = colour(default='#9BCD9B')
OutlineAlpha = integer(default=255)
Alpha = integer(default=125)
Style = integer(default=6)
DrawUnder = boolean(default=True)


[CallTip]
Enable = boolean(default=False)
ForeColour = colour(default='#0000FF')
BackColour = colour(default='#E6F2FF')
DelayShow = integer(default=1000)


[Hotspot]
ForeColour = colour(default='#0000FF')
BackColour = colour(default='#E6F2FF')
Underline = boolean(default=True)
SingleLine = boolean(default=True)


[KeyBinding]


[MultiView]


[ToolTip]
MaxWidth = integer(default=-1)
DelayShow = integer(default=500)
DelayHide = integer(default=10000)
DelayReshow = integer(default=500)


[GotoAnything]
FuzzySearch = boolean(default=True)
BackColour = colour(default='#3399FF')
PositionY = integer(default=0)
TextCtrlBackColour = colour(default='#C6E2FF')
ListBoxBackColour = colour(default='#C6E2FF')
BorderWidth = integer(default=2)
DropShadow = boolean(default=False)
Font = font(default=Consolas)
FontSize = integer(default=11)
FontBold = boolean(default=True)


[SymbolBrowser]
FuzzySearch = boolean(default=True)
BackColour = colour(default='#3399FF')
PositionY = integer(default=0)
TextCtrlBackColour = colour(default='#C6E2FF')
ListBoxBackColour = colour(default='#C6E2FF')
ClassBackColour = colour(default='#FFFFD0')
MemberBackColour = colour(default='#71B3E8')
FunctionBackColour = colour(default='#FFBBAA')
BorderWidth = integer(default=2)
DropShadow = boolean(default=False)
Font = font(default=Consolas)
FontSize = integer(default=11)
FontBold = boolean(default=True)


[SymbolIndex]
Enable = boolean(default=True)
IncludeDFN = boolean(default=True)
IncludeREF = boolean(default=True)
IncludeIMP = boolean(default=True)
IncludeVAR = boolean(default=True)
IncludeWRD = boolean(default=True)
IncludeQTS = boolean(default=True)


[SymbolPopup]
Enable = boolean(default=True)
NeedCtrlKey = boolean(default=True)
CallablesOnly = boolean(default=True)
DropShadow = boolean(default=True)
DelayShow = integer(default=500)
PanelBackColour = colour(default='#71B3E8')
ShowSymbol = boolean(default=True)
SymbolFont = font(default=Arial Rounded MT Bold)
SymbolForeColour = colour(default='#0000FF')
SymbolBackColour = colour(default='#F0F0F0')
ShowSymbolType = boolean(default=True)
SymbolTypeFont = font(default=Arial Rounded MT Bold)
SymbolTypeForeColour = colour(default='#FFFFFF')
HyperlinkFont = font(default=Consolas)
CentreCaret = boolean(default=True)


[ColourToolTip]
Enable = boolean(default=True)
Width = integer(default=100)
Height = integer(default=75)
RectRounded = boolean(default=True)
RectRoundedRadius = integer(default=5)
RectLineColour = colour(default='#000000')
RectLineWidth = integer(default=5)
ShowHex = boolean(default=False)
ShowName = boolean(default=True)
ShowDec = boolean(default=False)
DelayShow = integer(default=50)
DelayHide = integer(default=2000)


[TopLineToolTip]
Enable = boolean(default=True)
ForeColour = colour(default='#0000FF')
BackColour = colour(default='#C6E2FF')
UseFade = boolean(default=False)
DropShadow = boolean(default=False)
DelayHide = integer(default=2000)


[FindHistory]


[WhereHistory]


[ReplaceHistory]


[Layout]
Caption = boolean(default=True)
MenuBar = boolean(default=True)
ToolBar = boolean(default=True)
InfoBar = boolean(default=True)
StatusBar = boolean(default=True)
MenuIcons = boolean(default=False)
MenuIconsCustomCheckable = boolean(default=False)
MenuHelpText = boolean(default=True)
PageTabs = boolean(default=True)
PageTabTheme = boolean(default=True)
PageTabIcons = boolean(default=True)
ToolTips = boolean(default=True)
FullScreen = boolean(default=False)
DistractionFree = boolean(default=False)


[PanelEffect]
Enable = boolean(default=False)
Duration = integer(default=200)
Choice = integer(default=0)


[Ruler]
Enable = boolean(default=False)
Swap = boolean(default=False)
SashPos = integer(default=26)
LineBottom = boolean(default=True)
LineColour = colour(default='#006400')
BackColour = colour(default='#C6E2FF')
TickLeftHeight = integer(default=25)
TickLeftColour = colour(default='#A9A9A9')
TickMaxHeight = integer(default=9)
TickLargeColour = colour(default='#FFFF00')
TickMediumColour = colour(default='#0000FF')
TickSmallColour = colour(default='#A9A9A9')
TextFontSize = integer(default=10)
TextColour = colour(default='#0000FF')
CaretColour = colour(default='#0000FF')
CaretType = option('TRIANGLE', 'BLOCK', 'LINE', 'TRIANGLE_SMALL', 'BLOCK_SMALL', 'LINE_SMALL')


[SidePanel]
Enable = boolean(default=False)
Swap = boolean(default=False)
SashPos = integer(default=335)
Choice = integer(default=0)
ListFilterBackColour = colour(default='#C6E2FF')


[SidePanelTool]


[Filter]
Document = string(default='')
Bookmark = string(default='')
Macro = string(default='')
Task = string(default='')
Breakpoint = string(default='')
Debug = string(default='')
Config = string(default='')
Help = string(default='')
Pylint = string(default='')
Pyflakes = string(default='')
Pycodestyle = string(default='')
Vulture = string(default='')


[Document]
ListRowColour = colour(default='#E6F2FF')
ListRowAltColour = colour(default='#C6E2FF')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)


[Project]


[Bookmark]
Symbol = integer(default=0)
OuterColour = colour(default='#0000FF')
InnerColour = colour(default='#0000FF')
ListRowColour = colour(default='#C6E2FF')
ListRowAltColour = colour(default='#CCFFCC')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
SearchWrap = boolean(default=False)
CentreCaret = boolean(default=False)
ShowPanel = boolean(default=False)
SyncPanel = boolean(default=False)


[Explorer]


[SymbolDef]
ShowIcons = boolean(default=True)
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
CentreCaret = boolean(default=False)


[Macro]
ListRowColour = colour(default='#ECFFEC')
ListRowAltColour = colour(default='#C6E2FF')


[Task]
Symbol = integer(default=23)
ShowMarker = boolean(default=False)
OuterColour = colour(default='#FF0000')
InnerColour = colour(default='#FF0000')
ListRowColour = colour(default='#ECFFEC')
ListRowAltColour = colour(default='#CCFFCC')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
SearchWrap = boolean(default=False)
CentreCaret = boolean(default=False)
ShowPanel = boolean(default=False)
SyncPanel = boolean(default=False)


[Breakpoint]
Symbol = integer(default=0)
OuterColour = colour(default='#FFFF00')
InnerColour = colour(default='#FFFF00')
ListRowColour = colour(default='#EAD5FF')
ListRowAltColour = colour(default='#CCFFCC')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
SearchWrap = boolean(default=False)
CentreCaret = boolean(default=False)
ShowPanel = boolean(default=False)
SyncPanel = boolean(default=False)


[Debug]
ListRowColour = colour(default='#FFFFF0')
ListRowAltColour = colour(default='#FFE7CE')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)


[Config]
SectionSelBackColour = colour(default='#0000FF')
KeySelBackColour = colour(default='#A020F0')
ListRowColour = colour(default='#C0C0C0')
ListRowAltColour = colour(default='#C6E2FF')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
CentreCaret = boolean(default=False)


[Help]
QuestionMarkButton = boolean(default=False)
ContextSensitiveMode = boolean(default=False)
CheckForUpdates = boolean(default=False)
ListRowColour = colour(default='#FF8000')
ListRowAltColour = colour(default='#C6E2FF')


[Pylint]
ListRowColour = colour(default='#C0C0C0')
ListRowAltColour = colour(default='#C6E2FF')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
CentreCaret = boolean(default=False)
ShowPanel = boolean(default=False)
SyncPanel = boolean(default=False)


[Pyflakes]
ListRowColour = colour(default='#C0C0C0')
ListRowAltColour = colour(default='#C6E2FF')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
CentreCaret = boolean(default=False)
ShowPanel = boolean(default=False)
SyncPanel = boolean(default=False)


[Pycodestyle]
ListRowColour = colour(default='#C0C0C0')
ListRowAltColour = colour(default='#C6E2FF')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
CentreCaret = boolean(default=False)
ShowPanel = boolean(default=False)
SyncPanel = boolean(default=False)


[Vulture]
ListRowColour = colour(default='#C0C0C0')
ListRowAltColour = colour(default='#C6E2FF')
HoverSelect = boolean(default=False)
NeedCtrlKey = boolean(default=True)
SingleClick = boolean(default=True)
CentreCaret = boolean(default=False)
ShowPanel = boolean(default=False)
SyncPanel = boolean(default=False)


[Markdown]


[Code2flow]


[Snippet]


[CodeContext]
Enable = boolean(default=False)
Swap = boolean(default=False)
SashPos = integer(default=100)
ForeColour = colour(default='#000000')
BackColour = colour(default='#E6F2FF')
Font = font(default=Courier New)
Depth = integer(default=10)


[SearchPanel]
Enable = boolean(default=False)
Swap = boolean(default=False)
SashPos = integer(default=95)
Mode = option('FND', 'RPL', 'FIF', 'INC', 'RES')
HasFocus = boolean(default=False)
IconSize = integer(default=24)
LabelFontStyle = string(default='bold')
TabTraversalAll = boolean(default=False)
BackColourFND = colour(default='#E6F2FF')
BackColourRPL = colour(default='#FFDDDD')
BackColourFIF = colour(default='#FFE7CE')
BackColourINC = colour(default='#C6E2FF')
BackColourRES = colour(default='#000000')
WarningBackColour = colour(default='#FF6060')
ErrorBackColour = colour(default='#FF0000')
DelayDefaultColour = integer(default=1000)
Border = boolean(default=False)
FindText = string(default='')
WhereText = string(default='')
ReplaceText = string(default='')
SelectedTextToFind = boolean(default=True)
ShowCheckboxes = boolean(default=True)
ShowCountButton = boolean(default=False)
ShowIcons = boolean(default=True)
CaseSensitive = boolean(default=False)
RegularExpression = boolean(default=False)
WholeWord = boolean(default=False)
WrapAround = boolean(default=False)
InSelection = boolean(default=False)
HighlightMatches = boolean(default=False)
PreserveCase = boolean(default=False)
ShowContext = boolean(default=False)
UseBuffer = boolean(default=False)


[DocMap]
ZoneRectRounded = boolean(default=False)
ZoneRectRoundedRadius = integer(default=5)
ZoneRectLineColour = colour(default='#0000FF')
ZoneRectLineStyle = integer(default=100)
ZoneRectLineWidth = integer(default=1)

ZoneFillColour = colour(default='#FFE7CE')
ZoneFillAlpha = integer(default=64)

ZoneCentreLine = boolean(default=True)
ZoneCentreLineColour = colour(default='#FF0000')
ZoneCentreLineStyle = integer(default=101)
ZoneCentreLineWidth = integer(default=1)

ZoneCentreDot = boolean(default=True)
ZoneCentreDotColour = colour(default='#0000FF')
ZoneCentreDotRadius = integer(default=2)

EdgeTextIndicator = boolean(default=True)
EdgeTextTop = string(default=' [ Top ] ')
EdgeTextBottom = string(default=' [ Bottom ] ')
EdgeTextFont = font(default=Courier New)
EdgeTextFontSize = integer(default=10)
EdgeTextForeColour = colour(default='#0000FF')
EdgeTextBackColour = colour(default='#FFD5AA')

AutoFocus = boolean(default=True)
MarkerLineHighlight = boolean(default=False)
SnapCursorAtDragStart = boolean(default=True)


[CodePreview]
Enable = boolean(default=False)
Caption = boolean(default=False)
Border = boolean(default=False)
BorderWidth = integer(default=2)
BorderColour = colour(default='#3399FF')
DropShadow = boolean(default=False)
Margin = boolean(default=False)
Width = float(0, 1, default=0.8)
Height = integer(default=10)
ShowOverZone = boolean(default=False)
"""