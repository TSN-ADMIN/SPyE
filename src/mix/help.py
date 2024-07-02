#!/usr/bin/python

import wx

from conf.debug import DBG, dbf, me_
from const import glb


class Help:

    def __init__(self):
        self.Bind(wx.EVT_HELP, self.Help)

    def Help(self, evt):
        dbf.help_event(evt, f'(type={evt.EventType})   {me_()}')

        obj = evt.EventObject
        skip = True
        # if obj.__doc__:
        #     print(obj.__doc__)
        #     skip = False
        evt.Skip(skip)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # pprint(dir(evt))
        # pprint(dir(evt.EventObject))

        # print('ClassInfo =', evt.ClassInfo)
        # print('ClassName =', evt.ClassName)
        # print('ClientData =', evt.ClientData)
        # print('Clone =', evt.Clone)
        # print('Destroy =', evt.Destroy)
        # print('EventObject =', evt.EventObject)
        # print('EventType =', evt.EventType)
        # print('ExtraLong =', evt.ExtraLong)
        # print('GetClassInfo =', evt.GetClassInfo)
        # print('GetClassName =', evt.GetClassName)
        # print('GetClientData =', evt.GetClientData)
        # print('GetClientObject =', evt.GetClientObject)
        # print('GetEventCategory =', evt.GetEventCategory)
        # print('GetEventObject =', evt.GetEventObject)
        # print('GetEventType =', evt.GetEventType)
        # print('GetEventUserData =', evt.GetEventUserData)
        # print('GetExtraLong =', evt.GetExtraLong)
        # print('GetId =', evt.GetId)
        # print('GetInt =', evt.GetInt)
        # print('GetOrigin =', evt.GetOrigin)
        # print('GetPosition =', evt.GetPosition)
        # print('GetRefData =', evt.GetRefData)
        # print('GetSelection =', evt.GetSelection)
        # print('GetSkipped =', evt.GetSkipped)
        # print('GetString =', evt.GetString)
        # print('GetTimestamp =', evt.GetTimestamp)
        # print('Id =', evt.Id)
        # print('Int =', evt.Int)
        # print('IsChecked =', evt.IsChecked)
        # print('IsCommandEvent =', evt.IsCommandEvent)
        # print('IsSameAs =', evt.IsSameAs)
        # print('IsSelection =', evt.IsSelection)
        # print('Origin =', evt.GetOrigin())
        # print('Origin_HelpButton =', evt.Origin_HelpButton)
        # print('Origin_Keyboard =', evt.Origin_Keyboard)
        # print('Origin_Unknown =', evt.Origin_Unknown)
        # print('Position =', evt.Position)
        # print('Ref =', evt.Ref)
        # print('RefData =', evt.RefData)
        # print('ResumePropagation =', evt.ResumePropagation)
        # print('Selection =', evt.Selection)
        # print('SetClientData =', evt.SetClientData)
        # print('SetClientObject =', evt.SetClientObject)
        # print('SetEventObject =', evt.SetEventObject)
        # print('SetEventType =', evt.SetEventType)
        # print('SetExtraLong =', evt.SetExtraLong)
        # print('SetId =', evt.SetId)
        # print('SetInt =', evt.SetInt)
        # print('SetOrigin =', evt.SetOrigin)
        # print('SetPosition =', evt.SetPosition)
        # print('SetRefData =', evt.SetRefData)
        # print('SetString =', evt.SetString)
        # print('SetTimestamp =', evt.SetTimestamp)
        # print('ShouldPropagate =', evt.ShouldPropagate)
        # print('Skip =', evt.Skip)
        # print('Skipped =', evt.Skipped)
        # print('StopPropagation =', evt.StopPropagation)
        # print('String =', evt.String)
        # print('Timestamp =', evt.Timestamp)
        # print('UnRef =', evt.UnRef)
        # print('UnShare =', evt.UnShare)
