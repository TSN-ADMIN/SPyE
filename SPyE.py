#!/usr/bin/python

"""Main SPyE module.

#TODO, module docstring

Scintilla/Python based Editor
"""


# >>>>>>>>>>>>>>>> STANDARD LIBRARY imports <<<<<
import os
import sys

# >>>>>>>>>>>>>>>> THIRD PARTY imports <<<<<<<<<<
from pubsub import pub
print('pubsub API version', pub.VERSION_API)
# from pubsub.utils.notification import useNotifyByWriteFile
# useNotifyByWriteFile(sys.stdout, all=False, subscribe=True, newTopic=True)
#    notification flags for each type of pubsub activity. The kwargs keys can be any of the following:
#    - subscribe:    if True, get notified whenever a listener subscribes to a topic;
#    - unsubscribe:  if True, get notified whenever a listener unsubscribes from a topic;
#    - deadListener: if True, get notified whenever a subscribed listener has been garbage-collected;
#    - sendMessage:  if True, get notified whenever sendMessage() is called;
#    - newTopic:     if True, get notified whenever a new topic is created;
#    - delTopic:     if True, get notified whenever a topic is "deleted" from topic tree;
#    - all:          set all of the above to the given value (True or False).


# >>>>>>>>>>>>>>>> LOCAL imports <<<<<<<<<<<<<<<<
from pathlib import Path
#HACK: enable main module startup from outside its directory
os.chdir(Path(sys.argv[0]).parent)

# from exception import (
#     SPyEException, ...
# )

from app.app import Application
from app.frame import AppFrame
from app.startup import startup
from common.util import WindowIDRef_hack
from conf.debug import DEBUG, dbg_APP_INFO, dbg_TIMER
from const.app import APP
from const import glb

#HACK: avoid "DeprecationWarning: an integer is required (got type WindowIDRef)."
WindowIDRef_hack()


def main():
    # startup
    dbg_APP_INFO()

    # create application
    sec = glb.CFG['General']
    app = Application(AppFrame, APP,
                      redirect=sec['AppRedirectOutput'],
                      filename=sec['AppRedirectOutputFile'],
                      useBestVisual=sec['AppUseBestVisual'],
                      clearSigInt=sec['AppClearSigInt'])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, glb.MNU -> NOT USED YET
    # # apply main menu
    # glb.MNU.apply()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # process config
    glb.CFG.apply()

    dbg_TIMER('startup', 'STOP')

    # main GUI event loop
    app.MainLoop()
    import wx
    wx.Exit()

    dbg_TIMER('session', 'STOP')

    # exit
    dbg_APP_INFO('EXIT', version=False, verbose=False)


if __name__ == '__main__':
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # def audit(event, args):
    #     # if event == 'open':
    #     if event == 'import':
    #         print(f'audit: {event} with args={args}')
    # sys.addaudithook(audit)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # sys.stdout = sys.stderr = open('NUL', 'w')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, add KBD, ICO for keyboard shortcuts/mni icons
#FIX, use var DBG in 'startup'; then copy to var DEBUG
    DBG, CFG, LNG, MNU, PLG, RFH, SFH, SSN, THM = startup()  # DBG, PLG not used
#@@@@@@@@@@@@@@@@@@
    glb.CFG = CFG
    glb.RFH = RFH
    glb.SFH = SFH
    glb.SSN = SSN
#@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, glb.MNU -> NOT USED YET
    # glb.MNU = MNU
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # glb.CFG, glb.DBG, glb.LNG, glb.PLG, glb.THM = startup()  # DBG, PLG not used
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # from pprint import pprint
    # pprint(DBG)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #NOTE, EXPERIMENTAL CODE: profiler, PERFORMANCE TESTING
#     import cProfile, pstats, io
#     from pstats import SortKey
#     pr = cProfile.Profile()

#     pr.enable()
# #@@@@@@@@@@@
#     main()
# #@@@@@@@@@@@
#     pr.disable()

#     s = io.StringIO()
#     sortby = SortKey.TIME
#     # sortby = SortKey.CUMULATIVE
#     ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#     ps.print_stats(10)
#     print(s.getvalue())
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#     # import cProfile
#     # cProfile.run('main()', filename='SPyE.profile', sort=-1)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@
    main()
#@@@@@@@@@@@
