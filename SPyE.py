#!/usr/bin/python

"""Main SPyE module.

#TODO, module docstring

Scintilla/Python based Editor
"""


# >>>>>>>>>>>>>>>> STANDARD LIBRARY imports <<<<<
import os
from pathlib import Path
import sys


# >>>>>>>>>>>>>>>> THIRD PARTY imports <<<<<<<<<<
import wx

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


#HACK, avoid error 'wx._core.PyNoAppError: The wx.App object must be created first!'
app = wx.App()

#HACK, enable main module startup from outside its directory
os.chdir(Path(sys.argv[0]).parent)


# >>>>>>>>>>>>>>>> LOCAL imports <<<<<<<<<<<<<<<<
# from exception import (
#     SPyEException, ...
# )

from app.app import Application
from app.startup import startup
from common.util import WindowIDRef_hack
from conf.debug import dbf
from const import glb

#HACK, avoid "DeprecationWarning: an integer is required (got type WindowIDRef)."
WindowIDRef_hack()


def main():
    # init
    startup()

    dbf.APP_INFO()

    dbf.SCINTILLA_CMDS()

    # create application
    sec = glb.CFG['General']

    app = Application(redirect=sec['AppRedirectOutput'],
                      filename=sec['AppRedirectOutputFile'],
                      useBestVisual=sec['AppUseBestVisual'],
                      clearSigInt=sec['AppClearSigInt'])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, glb.MNU -> NOT USED YET
    # # apply main menu
    # glb.MNU.apply()  # menubar
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    glb.CFG.apply()  # config
    glb.SFH.apply()  # search field history

    dbf.TIMER('startup', 'STOP')

    # main GUI event loop
    app.MainLoop()

#@@@@@@@@@@@@@@
    # wx.Exit()
#@@@@@@@@@@@@@@

    dbf.TIMER('session', 'STOP')

    # exit
    dbf.APP_INFO('STOP', version=False, verbose=False)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# import tracemalloc

# tracemalloc.start(25)

# ... run your application ...
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == '__main__':
    main()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# snapshot = tracemalloc.take_snapshot()
# top_stats = snapshot.statistics('lineno')

# print("[ Top 10 ]")
# for stat in top_stats[:10]:
#     print(stat)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#TODO, add KBD, ICO for keyboard shortcuts/mni icons
#FIX, use var DBG in 'startup'; then copy to var DEBUG
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #NOTE, EXPERIMENTAL: profiler, PERFORMANCE TESTING
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
