#!/usr/bin/python

from wx import stc

from conf.debug import DEBUG
from common.util import funcname, me_
from const.editor import LF, CR, CRLF
from const import glb
from const.menu import MI


def get_doc():
    if DEBUG['GEN'] > 1: print(f'{me_()}')
    # # when 'search results' active
    # if is_shown('RES') and glb.SCH.stc_res.HasFocus():
    #     return None, glb.SCH.stc_res
    # active or clicked notebook tab
    return glb.NBK.CurrentPage


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
        if DEBUG['SBR']: print(f'max EOL: [{eol}]: [{_max}]')
    elif cnt[0]:
        txt, key, flg = dft_eol_lst
    elif cnt[1]:
        txt, key, flg = 'Unix', 'ELF', stc.STC_EOL_LF
    elif cnt[2]:
        txt, key, flg = 'Mac', 'ECR', stc.STC_EOL_CR
    else:
        txt, key, flg = dft_eol_lst  # default when empty doc

    return txt, key, flg


def update_margins():
    """will doxygen detect this docstring?"""

    sec, mb = glb.CFG['Margin'], glb.MB

    if not (doc := get_doc()): return
    mgn_lst = [MI['MGN_NUM'], MI['MGN_SYM'], MI['MGN_FOL']]
    mb.Check(MI['MGN_ALL'], all([mb.IsChecked(m) for m in mgn_lst]))

    num = sec['LineNumberWidth']
    sym = sec['SymbolWidth']
    fol = sec['FoldingWidth']
    tot = 0
    tot += num if mb.IsChecked(MI['MGN_NUM']) else 0
    tot += sym if mb.IsChecked(MI['MGN_SYM']) else 0
    tot += fol if mb.IsChecked(MI['MGN_FOL']) else 0

    # update ruler alignment
    glb.RLR.set_offset(tot - doc.XOffset)

    if DEBUG['ZOO']:
        print(f'num {num:3d}, sym {sym:3d}, fol {fol:3d}, tot {tot:3d}  (ruler offset:   1 margin)')
