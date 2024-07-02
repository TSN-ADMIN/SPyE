#!/usr/bin/python

import wx
import wx.adv as adv

from conf.debug import DBG, dbf
from const.app import APP
from const import glb


class SystemTrayMenu(adv.TaskBarIcon):

    __slots__ = ['tlw']

    def __init__(self, tlw):
        super().__init__()
        self.tlw = tlw

        self.SetIcon(APP['Icon'], APP['Base'])
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.toggle_main_window)

    def CreatePopupMenu(self):
        mnu_ctx = glb.MBR.build_submenu(self, self.tlw.ctx['STM'])
        return mnu_ctx

    def toggle_main_window(self, evt):
        self.tlw.Iconize(bool(not self.tlw.IsIconized()))
        dbf.FOCUS(glb.NBK)


def global_hot_key(tlw):
    DBG('KBD', 'global_hot_key')
    tlw.Iconize(bool(not tlw.IsIconized()))
    dbf.FOCUS(glb.NBK)
