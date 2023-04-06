#!/usr/bin/python

import wx

from ._load import _load
from common.util import msg_box, me_, splash
from conf.debug import DEBUG, dbg_help
from const.app import APP
from const import glb
import data


@_load
class Help:


    def help_about(self, evt):
        if glb.CFG['General']['OeufDePaques']:
            data.Oeuf(self)
        splash(self)


#FIX, focus is lost and outside app
        # dbg_FOCUS(wx.GetApp())
    def help_check_updates(self, evt):
        msg = APP['Base'] + ' is up to date.\n\n'
        msg_box(self, 'INFO', msg)


    def help_contents(self, evt):
        dbg_help(evt, f'(type={evt.EventType})   {me_()}')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# #NOTE, EXPERIMENTAL CODE: call HTML Help, generated w/ Sphinx
        import subprocess as SP
        from const.app import EXE, LOC

        # for val in ('PTH', 'EXT', 'FIL', 'DFT', 'BAK'):
        #     print(f'  LOC[HLP][{val}] = [{LOC["HLP"][val]}]')

        # suppress output
        SP.Popen(f'{EXE["HELPVIEWER"]} {LOC["HLP"]["FIL"]}', stdout=SP.DEVNULL, stderr=SP.STDOUT)
        return
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


        txt = APP['Base'] + ' Help Contents\n'
        msg1 = txt + '\nNot implemented, yet.'
        res = msg_box(self, 'HELP', msg1)
        if glb.CFG['General']['OeufDePaques']:
            msg2 = txt + '\nSorry, not implemented, yet.\n\nWill you accept my apologies?'
            msg3 = txt + '\nSorry, I\'m so sorry.\n\nI just said: "Sorry, not implemented, yet."\n\nWill you please accept..?'
            msg4 = txt + '\nGreatly admiring your humongous persistence, though.\n\nI\'ll be quitting this monologue, too.\n\nSo silly.\n\nAnd sorry..\n\nPS Sorry for my humble advice: get some help, yet.'
            if res == wx.ID_HELP:
                if (res := msg_box(self, 'WARN_ASK', msg2)) == wx.ID_NO:
                    if (res := msg_box(self, 'WARN_ASK', msg3)) == wx.ID_NO:
                        res = msg_box(self, 'ERROR', msg4)


#TODO, implement context-sensitive help details
    def help_context(self, evt):
        wx.ContextHelp(self)
        evt.Skip()
        # flg = wx.WS_EX_CONTEXTHELP
        # if self.HasExtraStyle(flg):
        #     self.SetExtraStyle(~flg)
        # else:
        #     self.SetExtraStyle(flg)


    def help_inspection_tool(self, evt):
        sec = glb.CFG['WidgetInspectionTool']
        wx.lib.inspection.InspectionTool().Show(
            selectObj=eval(f'glb.{sec["PreSelectObject"]}'),
            refreshTree=sec['RefreshWidgetTree'])
