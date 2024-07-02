#!/usr/bin/python

from copy import deepcopy
from inspect import isclass, ismethod
import types

import wx
import wx.lib.agw.floatspin as FS
from wx import stc


#INFO, URL=https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
#IFNO, https://stackoverflow.com/questions/49901590/python-using-copy-deepcopy-on-dotdict
class DotDict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __deepcopy__(self, memo=None):
        return DotDict(deepcopy(dict(self), memo=memo))


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# BOOLEAN_TERMS, causes ERROR when a config key equals 1 of its values (here 'active'):
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#   File "D:\Dev\Python38\lib\site-packages\configobj\__init__.py", line 929, in as_bool
#   raise ValueError('Value "%s" is neither True nor False' % val)
#   ValueError: Value "active" is neither True nor False
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#INFO, Possible boolean values in the configuration.
#INFO, URL=D:\Dev\Python38\Lib\configparser.py
# BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True,
#                   '0': False, 'no': False, 'false': False, 'off': False}
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# boolean synonyms
BOOLEAN_TERMS = (
#FIX, '1'/'0' incorrectly converts to boolean; conflicts with is_int(string)
#INFO, swap 'is_bool' and 'is_int' test order??
    # '1',       '0',
    'on',      'off',
    'true',    'false',
    'yes',     'no',
    # 'active',  'inactive',
    # 'checked', 'unchecked',
    # 'enabled', 'disabled',
)


    # # boolean synonyms (try with dict mapping str -> boolean)
    # BOOLEAN_TERMS = {
    #     '1'        : True,
    #     '0'        : False,
    #     'active'   : True,
    #     'inactive' : False,
    #     'checked'  : True,
    #     'unchecked': False,
    #     'enabled'  : True,
    #     'disabled' : False,
    #     'on'       : True,
    #     'off'      : False,
    #     'true'     : True,
    #     'false'    : False,
    #     'yes'      : True,
    #     'no'       : False,
    # }


    # # common data types
    # def is_bool(val):
    #     if isinstance(val, bool):
    #         print(val, type(val))
    #         return True
    #     elif val in BOOLEAN_TERMS:
    #         print(val, type(val), BOOLEAN_TERMS[val])
    #         return BOOLEAN_TERMS[val]
    #     return False
    #     # elif not hasattr(val, 'lower'):
    #     #     return False
#     # return val.lower() in BOOLEAN_TERMS
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# common data types
def is_bool(val):
    if isinstance(val, bool):
        return True
    elif not hasattr(val, 'lower'):
        return False
    return val.lower() in BOOLEAN_TERMS

#INFO, URL=https://stackoverflow.com/questions/15357422/python-determine-if-a-string-should-be-converted-into-int-or-float
def is_float(val):
    return isinstance(val, float)

def is_int(val):
    try:
        int(val)
        return True
    except (TypeError, ValueError):
        return False

def is_list(val):
    return isinstance(val, (list, tuple))

def is_str(val):
    return isinstance(val, str)


# wx object types
def is_btn(obj):
    return isinstance(obj, wx.Button)

def is_cbb(obj):
    return isinstance(obj, wx.ComboBox)

def is_cbx(obj):
    return isinstance(obj, wx.CheckBox)

def is_cpc(obj):
    return isinstance(obj, wx.ColourPickerCtrl)

def is_evb(obj):
    return isinstance(obj, wx.PyEventBinder)

def is_fpc(obj):
    return isinstance(obj, wx.FontPickerCtrl)

def is_fsp(obj):
    return isinstance(obj, FS.FloatSpin)

# def is_gbs(obj):
#     return isinstance(obj, wx.GridBagSizer)

def is_lbx(obj):
    return isinstance(obj, wx.ListBox)

def is_lct(obj):
    return isinstance(obj, wx.ListCtrl)

def is_spc(obj):
    return isinstance(obj, wx.SpinCtrl)

# used in 'searchpanel.py' for icon (bitmap) click
def is_stb(obj):
    return isinstance(obj, wx.StaticBitmap)

def is_stc(obj):
    return isinstance(obj, stc.StyledTextCtrl)

def is_stt(obj):
    return isinstance(obj, wx.StaticText)

def is_tlw(obj):
    return isinstance(obj, wx.TopLevelWindow)

def is_txc(obj):
    return isinstance(obj, wx.TextCtrl)


###################################################################################################
# BEGIN: FOR FUTURE USE: object type tests
###################################################################################################
##################
# def is_cls(obj):
#     return inspect.isclass(obj)
# def is_fnc(obj):
#     return isinstance(obj, types.FunctionType)
# def is_mth(obj):
#     # return inspect.ismethod(obj)
#     return isinstance(obj, types.MethodType)
# def is_mnu(obj):
#     return isinstance(obj, wx.Menu)
# def is_peb(obj):
#     return isinstance(obj, wx.PyEventBinder)
# def is_tlw(obj):
#################################################################################################
#   END: FOR FUTURE USE: object type tests
###################################################################################################
