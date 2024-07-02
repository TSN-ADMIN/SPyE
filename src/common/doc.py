#!/usr/bin/python

from wx import stc

# from common.util import curdoc
from conf.debug import DBG, me_
from const.editor import LF, CR, CRLF
from const import glb
from const.menubar import MI


#INFO, Undo affects Line Endings
#INFO, URL=https://github.com/ProgerXP/Notepad2e/issues/239
#INFO, SCI_GETEOLMODE doesn't return correct value when undo used after SetEOLMode
#INFO, URL=https://sourceforge.net/p/scintilla/bugs/1077/
def guess_eol_mode(doc):

#FIX, use 'collections.Counter'

    # EOL count in document
    #      CRLF   LF   CR
    cnt = [0,     0,   0]

    # scan doc, count EOLs
    for lin in range(doc.LineCount):
        txt = doc.GetLine(lin)
        if CRLF in txt:
            cnt[0] += 1
        elif LF in txt:
            cnt[1] += 1
        elif CR in txt:
            cnt[2] += 1

    # more than 1 EOL type?
    typ_cnt = len([c for c in cnt if c > 0])

    # set descriptor, 'SBX_EOL' key and corresponding Scintilla EOLMode flag
    dft_eol_lst = ['Windows', 'ECL', stc.STC_EOL_CRLF]

    if typ_cnt > 1:
        txt, key, flg = 'Mixed', None, None
        _max = max(cnt)
        dft_txt = 'CRLF'
        eol = dft_txt if _max == cnt[0] else '  LF' if _max == cnt[1] else '  CR'if _max == cnt[2] else dft_txt
        DBG('SBR', f'max EOL: [{eol}]: [{_max}]')
    elif cnt[0]:
        txt, key, flg = dft_eol_lst
    elif cnt[1]:
        txt, key, flg = 'Unix', 'ELF', stc.STC_EOL_LF
    elif cnt[2]:
        txt, key, flg = 'Mac', 'ECR', stc.STC_EOL_CR
    else:
        txt, key, flg = dft_eol_lst  # default when empty doc

    return txt, key, flg


# @curdoc()
def update_margins():
    """will doxygen detect this docstring?"""
#FIX, replace this statement with 1 '@curdoc()' above 'update_margins'
#NOTE, NOW gives this ERROR when FIX is done
#INFO,   Traceback (most recent call last):
#INFO,     File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\SPyE.py", line 44, in <module>
#INFO,       from app.app import Application
#INFO,     File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\app\app.py", line 22, in <module>
#INFO,       from common.util import (
#INFO,     File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\common\__init__.py", line 5, in <module>
#INFO,       from .file import *
#INFO,     File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\common\file.py", line 13, in <module>
#INFO,       from .doc import update_margins
#INFO,     File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\common\doc.py", line 5, in <module>
#INFO,       from common.util import curdoc
#INFO,     File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\common\util.py", line 27, in <module>
#INFO,       from conf.debug import DBG, DEBUG
#INFO,     File "D:\Dev\D\wx\TSN_SPyE\dev\spye\src\conf\debug.py", line 204, in <module>
#INFO,       from common.util import d_type, rs_
#INFO,   ImportError: cannot import name 'd_type' from partially initialized module 'common.util' (most likely due to a circular import) (D:\Dev\D\wx\TSN_SPyE\dev\spye\src\common\util.py)
    if not (doc := glb.DOC): return

    sec, mbr = glb.CFG['Margin'], glb.MBR

    mgn_lst = [MI['MGN_NUM'], MI['MGN_SYM'], MI['MGN_FOL']]
    mbr.Check(MI['MGN_ALL'], all([mbr.IsChecked(m) for m in mgn_lst]))

    num = sec['LineNumberWidth']
    sym = sec['SymbolWidth']
    fol = sec['FoldingWidth']
    tot = 0
    tot += num if mbr.IsChecked(MI['MGN_NUM']) else 0
    tot += sym if mbr.IsChecked(MI['MGN_SYM']) else 0
    tot += fol if mbr.IsChecked(MI['MGN_FOL']) else 0

    # update ruler alignment
    glb.RLR.set_offset(tot - doc.XOffset)

    DBG('ZOO', f'num {num:3d}, sym {sym:3d}, fol {fol:3d}, tot {tot:3d}  (ruler offset:   1 margin)')
