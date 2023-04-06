#!/usr/bin/python

import beeprint

from copy import deepcopy
from pathlib import Path

from extern.configobj import ConfigObj
from extern.configobj.validate import Validator
import wx
from wx import stc

from common.util import hex_colour, me_, msg_box
from conf.debug import DEBUG, dbg_LANG, dbg_STYLESPEC
from const.app import APP, LOC
from const.common import TXT_NIL
from const.editor import MGN
from const import glb
from const.lang import FACES, LANG, LANG_KWRD, LANG_PRVW, LANG_STYL


# frame title
TTL_FRM = f'{APP["Base"]} - Syntax Styling for [%s] - [%s]'

# new (window) ID ref: alias
__ID = wx.NewIdRef

# Syntax Styling: reset button ids
STY_RESET = {
    'LNG': __ID(),  # language
    'ELM': __ID(),  # element
    'ALL': __ID(),  # all
}


class Language(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.read()

    def default(self):
        if DEBUG['LNG']: print(f'{me_()}\n  File = {self.filename}\n')
        # sort on lng_nam
        for lst in sorted(LANG, key=lambda itm: itm[2]):
            lexer, lng_typ, lng_nam = lst[:3]
            sec = '|'.join((lng_nam, lng_typ, str(lexer)))
            if LANG_STYL[lexer]:
                if DEBUG['LNG']: print(' ', sec)
                self[sec] = {}
                for lbl, tok, sty in LANG_STYL[lexer]:
                    key = '|'.join((lbl, str(tok)))
                    if DEBUG['LNG']: print('    %-30s %s' % (key, sty))
                    self[sec][key] = sty

    def create(self):
        if DEBUG['LNG']: print(f'{me_()}\n  File = {self.filename}\n')

        # get default language configuration
        self.default()

        # add blank lines and header before all sections, except the first
        # first_sec = sorted(LANG, key=lambda itm: itm[2])[0][2]  # lng_nam
        first_sec = list(self)[0]  # lng_nam
        if DEBUG['LNG']: print('first lng_nam: [%s]' % first_sec)
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Styling for %s' % sec.split('|')[0])

        self.commit()

#FIX, not used: obsolete?
    def read(self):
        if DEBUG['LNG']: print(f'{me_()}\n  File = {self.filename}\n')
        dbg_LANG(self)

#FIX, not used: obsolete?
    def commit(self):
        if DEBUG['LNG']: print(f'{me_()}\n  File = {self.filename}\n')
        if DEBUG['LNG'] > 1: beeprint.pp(self, sort_keys=False)
        self.write()


#INFO, URL=D:\Dev\D\wx\TSN_SPyE\contrib\demo\STCStyleEditor\STCStyleEditor.py
class SyntaxStyling(wx.Dialog):
    def __init__(self, doc):
        super().__init__(glb.TLW, id=wx.ID_ANY, pos=(-1, -1), size=(610, 600), style=wx.DEFAULT_DIALOG_STYLE)
        self.doc = doc
        self.lexer = doc.lexer
        self.lang = ''
        self.elm_lst = []
        self.stylespec = ''

        # read styles from 'file.lng', create work copy
        self.cur = Language(LOC['LNG']['FIL'])
        self.wrk = deepcopy(self.cur)

        self.create_dialog()
        self._enable_buttons(False)

        # supported languages: (lng_nam, lng_typ, lexer)
        self.lng_lst = [(n[2], n[1], n[0]) for n in LANG]

        # populate languages, position on current
        lng_nam_lst = [n[0] for n in self.lng_lst]
        self.cbb_lng.Append(lng_nam_lst)
        cur = self.lng_lst.index([n for n in self.lng_lst if self.lexer == n[2]][0])
        self.cbb_lng.SetSelection(cur)

        # force 1st 'get_language' call to populate all widgets
        self.get_language(None)

        self.binds()

    def binds(self):
        self.Bind(wx.EVT_COMBOBOX, self.get_language)
        self.Bind(wx.EVT_LISTBOX, self.get_code_element)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.style_colour)
        self.Bind(wx.EVT_CHECKBOX, self.style_emphasis)
        self.Bind(wx.EVT_FONTPICKER_CHANGED, self.style_font)
        self.Bind(wx.EVT_BUTTON, self.on_button)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_escape)

    def create_dialog(self):
#TODO: try dialog redesign in 'wxFormBuilder'
#FIX, setup 'GridBagSizer' structure like 'search_panel.set_mode'
        gbs = wx.GridBagSizer(vgap=0, hgap=0)
        gbs.SetFlexibleDirection(wx.BOTH)
        gbs.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_ALL)
        gbs.SetEmptyCellSize((-1, 10))
        border = 5

        self.stt_lng = wx.StaticText(self, wx.ID_ANY, '&Language:')
        self.cbb_lng = wx.ComboBox(self, wx.ID_ANY, TXT_NIL, (-1, -1), (100, -1), list(), wx.CB_READONLY)
        self.stl_lng = wx.StaticLine(self, wx.ID_ANY, (5, 35), (595, -1))  # not in sizer

        self.stt_elm = wx.StaticText(self, wx.ID_ANY, '&Code Element:')
        self.lbx_elm = wx.ListBox(self, wx.ID_ANY, (-1, -1), (175, 370), list(), 0)

        self.stt_fgc = wx.StaticText(self, wx.ID_ANY, 'F&oreground:')
        self.cpc_fgc = wx.ColourPickerCtrl(self, wx.ID_ANY, 'BLACK', (-1, -1), (100, -1), wx.CLRP_DEFAULT_STYLE | wx.CLRP_SHOW_LABEL, name='fore')

        self.stt_bgc = wx.StaticText(self, wx.ID_ANY, 'B&ackground:')
        self.cpc_bgc = wx.ColourPickerCtrl(self, wx.ID_ANY, 'BLACK', (-1, -1), (100, -1), wx.CLRP_DEFAULT_STYLE | wx.CLRP_SHOW_LABEL, name='back')

        self.cbx_bld = wx.CheckBox(self, wx.ID_ANY, '&Bold', name='bold')
        self.cbx_ita = wx.CheckBox(self, wx.ID_ANY, '&Italic', name='italic')
        self.cbx_und = wx.CheckBox(self, wx.ID_ANY, '&Underline', name='underline')
        self.cbx_eol = wx.CheckBox(self, wx.ID_ANY, '&EOL Filled', name='eol')

        self.stt_fnt = wx.StaticText(self, wx.ID_ANY, '&Font:')
#INFO, URL=https://groups.google.com/forum/#!topic/wxpython-users/F1PrSirxOBc
        self.fpc_fnt = wx.FontPickerCtrl(self, wx.ID_ANY, wx.NullFont, (-1, -1), (100, -1), style=0)

        self.stt_pvw = wx.StaticText(self, wx.ID_ANY, '&Preview:')
        self.stc_pvw = stc.StyledTextCtrl(self, wx.ID_ANY, (-1, -1), (414, 349), 0)

        self.btn_lng = wx.Button(self, STY_RESET['LNG'], 'Reset Language', size=(109, -1))
        self.btn_elm = wx.Button(self, STY_RESET['ELM'], 'Reset Element', size=(109, -1))
        self.btn_all = wx.Button(self, STY_RESET['ALL'], 'Reset All Styles', size=(109, -1))
        self.btn_ok_ = wx.Button(self, wx.ID_OK, 'OK')
        self.btn_can = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        self.btn_apl = wx.Button(self, wx.ID_APPLY, 'Apply')

        one = (1, 1)  # one row/column

        gbs.Add(self.stt_lng, (0, 1), one, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.cbb_lng, (0, 2), one, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border)

        gbs.Add(self.stt_elm, (3, 0), one, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, border)
        gbs.Add(self.lbx_elm, (4, 0), (5, 1), wx.ALL, border)

        gbs.Add(self.stt_fgc, (1, 1), one, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.cpc_fgc, (1, 2), one, wx.ALL, border)

        gbs.Add(self.stt_bgc, (2, 1), one, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.cpc_bgc, (2, 2), one, wx.ALL, border)

        gbs.Add(self.cbx_bld, (1, 3), one, wx.ALL | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.cbx_ita, (2, 3), one, wx.ALL | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.cbx_und, (1, 4), one, wx.ALL | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.cbx_eol, (2, 4), one, wx.ALL | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)

        gbs.Add(self.stt_fnt, (3, 1), one, wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.fpc_fnt, (3, 2), (1, 2), wx.ALL, border)

        gbs.Add(self.stt_pvw, (4, 1), one, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.stc_pvw, (5, 1), (4, border), wx.RIGHT, border)

        gbs.Add(self.btn_lng, (0, 0), one, wx.ALL, border)
        gbs.Add(self.btn_elm, (2, 0), one, wx.ALL, border)
        gbs.Add(self.btn_all, (9, 0), one, wx.ALL, border)
        gbs.Add(self.btn_ok_, (9, 2), one, wx.ALL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.btn_can, (9, 3), one, wx.ALL | wx.ALIGN_RIGHT, border)
        gbs.Add(self.btn_apl, (9, 4), one, wx.ALL | wx.ALIGN_LEFT, border)

        self.lbx_elm.SetBackgroundColour(glb.CFG['General']['DialogBackColour'])
        for m in 'NUM', 'SYM', 'FOL':  # disable preview margins
            self.stc_pvw.SetMarginWidth(MGN[m], 0)
        self.SetSizer(gbs)
        self.Layout()
        self.Centre()

    def get_language(self, evt):
        idx = self.cbb_lng.Selection
        self.lang = '|'.join(map(str, self.lng_lst[idx]))
        self.lexer = self.lng_lst[idx][2]
        if self.lang in self.wrk:
            elm_nam_lst = [n.split('|')[0] for n in self.wrk[self.lang]]
        else:
            elm_nam_lst = []
        self.lbx_elm.Clear()
        if elm_nam_lst:
            # prepare preview
            self.stc_pvw.SetLexer(self.lexer)
            # keywords
            for lbl, kws, lst in LANG_KWRD[self.lexer]:
                self.stc_pvw.SetKeyWords(kws, lst)
            # reset global default styles
            self.stc_pvw.StyleResetDefault()
            self.stc_pvw.ClearDocumentStyle()
            self.stc_pvw.StyleSetSpec(stc.STC_STYLE_DEFAULT, 'face:%(helv)s,size:%(size)d' % FACES)
            self.stc_pvw.StyleSetBackground(stc.STC_STYLE_DEFAULT, glb.CFG['Editor']['DefaultBackColour'])
            # populate code elements, position on 1st
            self.lbx_elm.Append(elm_nam_lst)
            self.lbx_elm.SetSelection(0)
            self.get_code_element(None)
        else:
            self._set_title('NOT implemented')
        self._enable_widgets(len(elm_nam_lst) > 0)

    def get_code_element(self, evt):
        idx = self.lbx_elm.Selection
        self._set_title(self.lbx_elm.StringSelection)
        self.elm_lst = list(self.wrk[self.lang])[idx]
        self.stylespec = self.wrk[self.lang][self.elm_lst]  # code element style
        self._split_stylespec(self.stylespec)
        dbg_STYLESPEC(self)

        # populate style widgets
#TODO, review code: default colours, set globally?
        # colours
        self.cpc_fgc.SetColour(self.fore if self.fore else 'BLACK')
        self.cpc_bgc.SetColour(self.back if self.back else 'WHITE')
        # emphasis
        self.cbx_bld.SetValue(bool(self.bold))
        self.cbx_ita.SetValue(bool(self.italic))
        self.cbx_und.SetValue(bool(self.underline))
        self.cbx_eol.SetValue(bool(self.eol))
#TODO, review code: default font/size, set globally?
        # font
        face = self.face if self.face else 'Courier New'
        size = int(self.size) if self.size else 10
        fnt_cur = wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, face)
        fnt_dft = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Courier New')
        self.fpc_fnt.SetSelectedFont(fnt_cur if self.face or self.size else fnt_dft)
        # preview source code
        self.stc_pvw.SetText(LANG_PRVW[self.lexer].replace('\n', TXT_NIL, 1))  # replace(rs_(4, ' '), TXT_NIL))
        # discard redundant debug output
        self._update_preview(False)

    def style_colour(self, evt):
        obj = evt.EventObject
        clr = hex_colour(evt)
        if DEBUG['LNG']: print(f'[{obj.Name}] = [{clr}]')
        if obj.Name == 'fore':
            self.fore = clr
        if obj.Name == 'back':
            self.back = clr
        self._update_preview()

    def style_emphasis(self, evt):
        obj = evt.EventObject
        if DEBUG['LNG']: print(f'[{obj.Name}] = [{obj.IsChecked()}]')
        pass
#FIX, needs better coding...
        cmd = 'self.' + obj.Name + ' = \'' + obj.Name + '\' if obj.IsChecked() else \'\''
        exec(cmd)
        # print(f'[{cmd}]')
        # var = 'print(self.' + obj.Name + ')'
        # exec(var)
        self._update_preview()

    def style_font(self, evt):
        obj = evt.Font
        if DEBUG['LNG']: print(f'[face,size] = [{obj.FaceName},{obj.PointSize}]')
        self.face = obj.FaceName
        self.size = str(obj.PointSize)
        self._update_preview()

    def on_button(self, evt):
        if (id_ := evt.Id) == STY_RESET['LNG']:
            if DEBUG['LNG']: print('RESET_LNG')
            self.wrk[self.lang] = deepcopy(self.cur[self.lang])
            self.get_language(None)  # repopulate all widgets
        elif id_ == STY_RESET['ELM']:
            if DEBUG['LNG']: print('RESET_ELM')
            self.wrk[self.lang][self.elm_lst] = deepcopy(self.cur[self.lang][self.elm_lst])
            self.get_code_element(None)  # repopulate element widgets
        elif id_ == STY_RESET['ALL']:
            if DEBUG['LNG']: print('RESET_ALL')
            msg = 'Are you sure?\n\nThis resets ALL styles to application defaults.\n(You still need to click OK and/or Apply)'
            if (res := msg_box(self, 'WARN_ASK', msg, extra='Reset to Defaults')) == wx.ID_YES:
                if DEBUG['LNG']: print('  ID_YES')
                self._reset_work()
                self.get_code_element(None)  # update style widgets
            elif res == wx.ID_NO:
                if DEBUG['LNG']: print('  ID_NO')
                pass
            elif res == wx.ID_CANCEL:
                if DEBUG['LNG']: print('  ID_CANCEL')
                pass
        elif id_ == wx.ID_OK:
            if DEBUG['LNG']: print('ID_OK')
            # write styles to 'file.lng' and exit
            self._save_work()
            self.Destroy()
        elif id_ == wx.ID_CANCEL:
            if DEBUG['LNG']: print('ID_CANCEL')
            # discard style changes and exit
            self.Destroy()
        elif id_ == wx.ID_APPLY:
            if DEBUG['LNG']: print('ID_APPLY')
            # write styles to 'file.lng'
            self._save_work()
            self._enable_buttons(False)
        evt.Skip()

    def on_escape(self, evt):
        if evt.KeyCode == wx.WXK_ESCAPE:
            self.Destroy()
        evt.Skip()

    def _set_title(self, lbl):
        self.SetTitle(TTL_FRM % (self.cbb_lng.StringSelection, lbl))

    def _enable_buttons(self, flg=True):
        # 3 Reset buttons and Apply
        for button in [self.btn_lng, self.btn_elm, self.btn_all, self.btn_apl]:
            button.Enable(flg)

    def _enable_widgets(self, flg=True):
        # empty preview, uncheck boxes when language style unavailable
        if not flg:
            self.stc_pvw.ClearAll()
            # checkbox widget: uncheck
            for wgt in ['cbx_bld', 'cbx_ita', 'cbx_und', 'cbx_eol']:
                att = getattr(self, wgt)
                att.SetValue(flg)

        for wgt in ['stt_elm', 'stt_fgc', 'stt_bgc', 'stt_fnt', 'stt_pvw',
                    'lbx_elm', 'cpc_fgc', 'cpc_bgc', 'cbx_bld', 'cbx_ita',
                    'cbx_und', 'cbx_eol', 'fpc_fnt', 'stc_pvw']:
            att = getattr(self, wgt)
            att.Enable(flg)

        # self.stc_pvw.Disable()  # preview

    def _split_stylespec(self, stylespec=''):
        self.fore = ''
        self.back = ''
        self.bold = ''
        self.italic = ''
        self.underline = ''
        self.eol = ''
        self.face = ''
        self.size = ''
        sty_lst = stylespec.split(',')
        for elm in sty_lst:
            if elm.find(':') > -1:
                nam, val = elm.split(':')
            else:
                nam = elm
            if nam == 'fore':
                self.fore = val
            elif nam == 'back':
                self.back = val
            elif nam == 'bold':
                self.bold = 'bold'
            elif nam == 'italic':
                self.italic = 'italic'
            elif nam == 'underline':
                self.underline = 'underline'
            elif nam == 'eol':
                self.eol = 'eol'
            elif nam == 'face':
                self.face = val
            elif nam == 'size':
                self.size = val

    def _join_stylespec(self):
        sty_lst = []
        if self.fore:
            sty_lst.append('fore:' + self.fore)
        if self.back:
            sty_lst.append('back:' + self.back)
        if self.bold:
            sty_lst.append(self.bold)
        if self.italic:
            sty_lst.append(self.italic)
        if self.underline:
            sty_lst.append(self.underline)
        if self.eol:
            sty_lst.append(self.eol)
        if self.face:
            sty_lst.append('face:' + self.face)
        if self.size:
            sty_lst.append('size:' + self.size)
        self.stylespec = ','.join(map(str, sty_lst))
        return self.stylespec

    def _update_preview(self, flg=True):
        if flg:
            if DEBUG['LNG']: print(f'{me_()}')
        stylenum = int(self.elm_lst.split('|')[1])
        self.stylespec = self._join_stylespec()
        self.wrk[self.lang][self.elm_lst] = self.stylespec
        if flg:
            if DEBUG['LNG']: print(' CUR:', self.cur[self.lang][self.elm_lst])
            if DEBUG['LNG']: print(' WRK:', self.wrk[self.lang][self.elm_lst])
        # reset all styles to default
        self.stc_pvw.StyleClearAll()
        # style all code elements
        for elm in self.wrk[self.lang]:
            __, tok = elm.split('|')
            sty = self.wrk[self.lang][elm]
            self.stc_pvw.StyleSetSpec(int(tok), sty)
        # restyle current code element
        self.stc_pvw.StyleSetSpec(stylenum, self.stylespec)
        self.stc_pvw.StartStyling(pos=0, mask=0xff)

        # compare current and work config content
        self._enable_buttons(bool(self.cur != self.wrk))

    def _reset_work(self):
        if DEBUG['LNG'] > 1: print(' CUR:', self.cur, '\n-----')
        if DEBUG['LNG'] > 1: print(' WRK:', self.wrk, '\n-----')
        # read/copy default styles from 'file.lng.default'
        dft = Language(LOC['LNG']['DFT'])
        self.wrk = deepcopy(dft)
        self.wrk.filename = LOC['LNG']['FIL']  # correct: 'file.lng.default' -> 'file.lng'
        if DEBUG['LNG'] > 1: print(' DFT:', self.wrk, '\n-----')

    def _save_work(self):
        if DEBUG['LNG'] > 1: print(' CUR:', self.cur, '\n-----')
        if DEBUG['LNG'] > 1: print(' WRK:', self.wrk, '\n-----')
        self.wrk.write()
        # verify styles just written to 'file.lng'
        if DEBUG['LNG'] > 1: new = Language(LOC['LNG']['FIL'])
        if DEBUG['LNG'] > 1: print(' NEW:', new, '\n-----')
        # restyle all open documents
        for __, doc in glb.NBK.open_docs():
            lng_lst = [t for t in LANG if doc.lng_typ == t[1]]
            doc.update_language_styling(lng_lst)
#FIX, set default background colour for ALL elements
            # doc.StyleSetBackground(stc.STC_STYLE_DEFAULT, glb.CFG['Editor']['DefaultBackColour'])
            # doc.StyleClearAll()  # reset all styles to default


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, not used: 'set_language', 'file_list'           >>>>  FOR FUTURE USE  <<<<
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#FIX, deduce language from context: (missing) file extension, selected menu, etc.
#INFO, search for: 'LANG' and 'update_language_styling'
# def _infer_language():
def set_language():
    pass

# walk open documents with 'PageCount', return as list, not used
def file_list(nbk):
    pass
    fil_lst = []
    for __, doc in nbk.open_docs():
        fil_lst.append(doc.pnm)
    return fil_lst
