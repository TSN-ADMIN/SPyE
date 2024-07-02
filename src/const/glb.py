#!/usr/bin/python

from pubsub import pub

# GLOBAL VARIABLES (glb.<name>)

APP = None  # application
STM = None  # system tray menu

TLW = None  # top level window

ACT = None  # action
CFG = None  # config
DBG = None  # debug    -> (NOT USED, TODO)
KBD = None  # keyboard -> (NOT USED, TODO)
LNG = None  # language -> (NOT USED, TODO)
MNU = None  # menu     -> (NOT USED, TODO)
PLG = None  # plugin   -> (NOT USED, TODO)
RFH = None  # recent file history
SFH = None  # search field history
SSN = None  # session
THM = None  # theme
TRC = None  # trace    -> (NOT USED, TODO)

SPL = {     # splitter windows
    'CCX': None,  # code context
    'RLR': None,  # ruler
    'SCH': None,  # search panel
    'SPN': None,  # side panel
}

MBR = None  # menubar (items)
TBR = None  # toolbar
IBR = None  # infobar
SBR = None  # statusbar

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, glb.MNU -> NOT USED YET
# MNU = None  # menubar
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

NBK = None  # notebook
CCX = None  # code context
RLR = None  # ruler
SCH = None  # search panel
SPN = None  # side panel
SPT = None  #  ''    ''  tool

DOC = None  # current document

SMS = pub.sendMessage  # pubsub message
SUB = pub.subscribe    # pubsub subscription
