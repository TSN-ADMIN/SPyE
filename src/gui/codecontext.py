#!/usr/bin/python

#INFO, copied from 'Python\Lib\idlelib', (modified) module 'CodeContext.py'

import re
import wx
from wx import stc

from common.util import curdoc
from conf.lang import Language
from const.app import LOC
from const.common import INFINITY, TXT_NIL
from const import glb
from const.editor import MGN
from const.lang import CCX_BLOCKOPENERS, FACES, LANG, LANG_KWRD
import gui
import mix


getspacesfirstword = lambda s, c=re.compile(r'^(\s*)(\w*)'): c.match(s).groups()


class CodeContext(wx.Panel, mix.Help):
    """CodeContext - Extension to display the block context above the edit window

    Once code has scrolled off the top of a window, it can be difficult to
    determine which block you are in.  This extension implements a pane at the top
    of each IDLE edit window which provides block structure hints.  These hints are
    the lines which contain the block opening keywords, e.g. 'if', for the
    enclosing block.  The number of hint lines is determined by the numlines
    variable in the CodeContext section of config-extensions.def. Lines which do
    not open blocks are not shown in the context hints pane.
    """
    def __init__(self, prt):
        sec = glb.CFG['CodeContext']
        sty = wx.WANTS_CHARS
        super().__init__(prt, wx.ID_ANY, style=sty, name='CodeContext')
        mix.Help.__init__(self)
        self.SetExtraStyle(wx.WS_EX_PROCESS_UI_UPDATES)

        self.context_depth = sec['Depth']
        bgc = sec['BackColour']
        fgc = sec['ForeColour']
        fnt = sec['Font']

        sty = wx.ST_ELLIPSIZE_START | wx.ST_NO_AUTORESIZE | wx.BORDER_SUNKEN
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.stc_ccx = stc.StyledTextCtrl(self, style=sty)
        self.stc_ccx.SetUseHorizontalScrollBar(False)
        self.stc_ccx.SetUseVerticalScrollBar(False)
        self.stc_ccx.SetMarginWidth(MGN['SYM'], 0)
        self.stc_ccx.SetCaretWidth(0)  # hide caret

        self.lexer = stc.STC_LEX_PYTHON
        self.stc_ccx.SetLexer(self.lexer)

        # reset global default styles
        self.stc_ccx.StyleResetDefault()
        self.stc_ccx.ClearDocumentStyle()
        self.stc_ccx.StyleSetSpec(stc.STC_STYLE_DEFAULT, 'face:%(helv)s,size:%(size)d' % FACES)
        self.stc_ccx.StyleSetBackground(stc.STC_STYLE_DEFAULT, glb.CFG['Editor']['DefaultBackColour'])
        self.stc_ccx.StyleClearAll()

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, refactor to method, see also 'Editor.styling'
        # lexer keywords
        for lbl, kws, lst in LANG_KWRD[self.lexer]:
            self.stc_ccx.SetKeyWords(kws, lst)

        # read styles from 'file.lng'
        lng = Language(LOC['LNG']['FIL'])

        # current language
        cur = [[n[2], n[1], n[0]] for n in LANG if self.lexer == n[0]][0]
        cur = '|'.join(map(str, cur))

        # style code elements for current language
        if cur in lng:
            for elm in lng[cur]:
                __, tok = elm.split('|')
                sty = lng[cur][elm]
                self.stc_ccx.StyleSetSpec(int(tok), sty)

        # self.stc_ccx.StartStyling(pos=0, mask=0xff)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#TODO, box around code context?
#         self.stb = wx.StaticBox(self.stc_ccx, size=(900, 100), label='Code Context')
#         self.stb.SetForegroundColour('black')

        # self.info is a list of (line number, indent level, line text, block
        # keyword) tuples providing the block structure associated with
        # self.topvisible (the linenumber of the line displayed at the top of
        # the edit window). self.info[0] is initialized as a 'dummy' line which
        # starts the toplevel 'block' of the module.
        self.info = [(0, -1, TXT_NIL, False)]
#NOTE, 1-based line numbering, STC is 0-based...
        self.topvisible = 1

        self.stc_ccx.Bind(wx.EVT_CONTEXT_MENU, lambda e: gui.ContextMenu(e, 'CCX'))
        self.Bind(wx.EVT_UPDATE_UI, self.update)
#INFO, URL=https://stackoverflow.com/questions/3420021/wxpython-how-to-make-a-textctrl-fill-a-panel
        box = wx.BoxSizer()  # auto sizing StaticText
        box.Add(self.stc_ccx, 1, wx.EXPAND)
        self.SetSizerAndFit(box)

    @curdoc
    def get_line_info(self, linenum):
        """Get the line indent value, text, and any block start keyword

        If the line does not start a block, the keyword value is False.
        The indentation of empty lines (or comment lines) is INFINITY.
        """
        txt = doc.GetLine(linenum - 1)
        spaces, firstword = getspacesfirstword(txt)
        opener = firstword in CCX_BLOCKOPENERS and firstword
        if len(txt) == len(spaces) or txt[len(spaces)] == '#':
            indent = INFINITY
        else:
            indent = len(spaces)
        return indent, txt, opener

    def get_context(self, new_topvisible, stopline=1, stopindent=0):
        """Get context lines, starting at new_topvisible and working backwards.

        Stop when stopline or stopindent is reached. Return a tuple of context
        data and the indent level at the top of the region inspected.
        """
        assert stopline > 0
        lines = []
        # The indentation level we are currently in:
        lastindent = INFINITY
        # For a line to be interesting, it must begin with a block opening
        # keyword, and have less indentation than lastindent.
        for linenum in range(new_topvisible, stopline - 1, -1):
            indent, text, opener = self.get_line_info(linenum)
            if indent < lastindent:
                lastindent = indent
                if opener in {'else', 'elif'}:
                    # We also show the if statement
                    lastindent += 1
                if opener and linenum < new_topvisible and indent >= stopindent:
                    lines.append((linenum, indent, text, opener))
                if lastindent <= stopindent:
                    break
        lines.reverse()
        return lines, lastindent

    @curdoc
    def update(self, evt):
        """Update context information and lines visible in the context pane.

        """
        if not glb.SPL['CCX'].IsSplit():  # code context not visible
            return

        new_topvisible = doc.FirstVisibleLine + 1
        if self.topvisible == new_topvisible:      # haven't scrolled
            return
        if self.topvisible < new_topvisible:       # scroll down
            lines, lastindent = self.get_context(new_topvisible,
                                                 self.topvisible)
            # retain only context info applicable to the region
            # between topvisible and new_topvisible:
            while self.info[-1][1] >= lastindent:
                del self.info[-1]
        elif self.topvisible > new_topvisible:     # scroll up
            stopindent = self.info[-1][1] + 1
            # retain only context info associated
            # with lines above new_topvisible:
            while self.info[-1][0] >= new_topvisible:
                stopindent = self.info[-1][1]
                del self.info[-1]
            lines, lastindent = self.get_context(new_topvisible,
                                                 self.info[-1][0] + 1,
                                                 stopindent)
        self.info.extend(lines)
        self.topvisible = new_topvisible
        # empty lines in context pane:
        context_strings = [''] * max(0, self.context_depth - len(self.info))
        # followed by the context hint lines:
        context_strings += [x[2] for x in self.info[-self.context_depth:]]
        self.stc_ccx.SetReadOnly(False)
        self.stc_ccx.SetText(''.join(context_strings))
        self.stc_ccx.SetReadOnly(True)
