#!/usr/bin/python

import ctypes as CT
import ctypes.wintypes as WT
import os
from pathlib import Path

import wx
from wx import stc

from common.date import tim_str
from common.doc import get_doc, update_margins
from common.util import funcname, me_, msg_box, zero
from conf.debug import DEBUG, dbg_BOOKMARK, dbg_BREAKPOINT, dbg_FILE, dbg_FOCUS
from const.app import FILE_ATTRS
from const.common import DELAY, TXT_NIL
from const.editor import MGN
from const import glb
from const.lang import LANG
from const.menu import MI
from data.images import catalog as PNG
import gui


#FIX, "NameError: name 'CFG' is not defined" when arg equals "delay=CFG['General']['DelayDetectFileChange']"
def detect_file_change(delay=DELAY['DFC']):
    if DEBUG['DFC']: print(f'{me_()}')
    if DEBUG['DFC'] > 1: print(f'  back in {delay} ms')
    tlw, nbk = glb.TLW, glb.NBK

    # win = tlw.FindFocus()  # save current focus
#FIX, no need to save/restore current page with 'cur'
    # cur = nbk.GetPageIndex(nbk.CurrentPage)  # save current page

    for __, cur in nbk.open_docs():
        if not cur:
            continue

        # skip new/unsaved file
        if not cur.dnm:
            continue

        # deleted on disk
        if not cur.del_detected:
            if not Path(cur.pnm).exists:
                cur.del_detected = True
#FIX, ask to save buffer to file with 'WARN_ASK'
                msg = f'{cur.fnm} deleted from disk'
                msg_box(tlw, 'INFO', msg)
        # changed on disk
        if not cur.chg_detected:
            # disk and edit buffer modification times
            dsk_mod = Path(cur.pnm).stat().st_mtime
            doc_mod = cur.dat_mod
            if dsk_mod != doc_mod:
                cur.chg_detected = True
#FIX, ask to reload file OR keep this buffer (and manually save it) with 'WARN_ASK'
                msg = f'{cur.fnm} timestamps differ:\n\n'
                msg += f'{tim_str(dsk_mod)} => on Disk\n'
                msg += f'{tim_str(doc_mod)} => in Editor\n'
                msg_box(tlw, 'INFO', msg)

#FIX, focus changes to doc when it is elsewhere, e.g. sidepanel
    # dbg_FOCUS(win)  # restore current focus
    # nbk.SetSelection(cur)  # restore current page

    # # 1st call at startup: doc = None
    # if not (doc := get_doc()): return
    # if doc:
    #     dbg_FOCUS(doc)

    # call myself repeatedly
    wx.CallLater(delay, detect_file_change, delay)


def get_file_attributes(pnm):
    tti = glb.CFG['Notebook']['TabToolTipFileInfo']
    att = CT.windll.kernel32.GetFileAttributesW(pnm)
    wsp = '\n\t\t   '
    att_key = att_dsc = TXT_NIL

    for key, (dsc, flg) in FILE_ATTRS.items():
        if flg & att:
            if 'B' in tti:
                att_key += key
            if 'L' in tti:
                att_dsc += f'+%s{wsp}' % dsc

    # attribute: key (letter), description (long)
    key, dsc = att_key, att_dsc.rstrip()
    return key, dsc


def get_file_icon(lng_typ):
    if DEBUG['GEN']: print(f'{me_()}')
    try:
        ico = (PNG['ext_' + lng_typ].Bitmap if glb.MB.IsChecked(MI['LAY_PTI']) else wx.NullBitmap)
    except KeyError:
        ico = wx.NullBitmap
    return ico


        # print(evt, type(evt), evt.IsChecked, evt.IsChecked())
        # print(isinstance(evt, wx.Event))


def get_file_status(pnm):
    # used in page tab tooltip
#FIX, not used: obsolete? => assign class attributes ('dat_/fil_')
    fst = Path(pnm).stat()

    cre = fst.st_ctime  # created
    mod = fst.st_mtime  # modified
    acc = fst.st_atime  # accessed
    szb = fst.st_size   # bytes
    szk = szb // 1024   # Kbytes

    return cre, mod, acc, szk, szb


#INFO, How to tell if a directory is a windows junction in python
#INFO, URL=https://stackoverflow.com/questions/47469836/how-to-tell-if-a-directory-is-a-windows-junction-in-python
def is_junction(path: str) -> bool:
     try:
         return bool(os.readlink(path))
     except OSError:
         return False


def is_open_file(pnm):
    for __, doc in glb.NBK.open_docs():
        if pnm.lower() == doc.pnm.lower():
            return True
    return False


def open_files(fil_lst):
    CFG, tlw, mb, nbk = glb.CFG, glb.TLW, glb.MB, glb.NBK

    if DEBUG['GEN']: print(f'{me_()}')
    tlw.Freeze()

    # add zeroes to file list when only filename is passed
    if fil_lst and len(fil_lst[0]) < 2:
        fil_lst = [f + zero(14) for f in fil_lst]

    for pnm, vis, pos, lin, col, lng, wrp, eol, wsp, tbu, tbw, ofs, sel_lst, bmk_lst, bpt_lst in fil_lst:
        dbg_FILE(f'  OK:[{pnm}, {vis}, {pos}, {lin}, {col}, {lng}, {wrp}, {eol}, {wsp}, {tbu}, {tbw}, {ofs}, {sel_lst}, {bmk_lst}, {bpt_lst}]')

        if not Path(pnm).is_file():
            dbg_FILE(f'    File NOT found: skipping [{pnm}]')
            continue

#DONE, focus on page tab if that file is already open => needs 'doc registry'
        if is_open_file(pnm):
            continue

        dnm, fnm, fbs, ext = split_path(pnm)
        doc = gui.Editor(nbk, [dnm, fnm, fbs, ext])
        doc.LoadFile(pnm)

#FIX, enable full doc search
#             # enable full doc search
#             doc.SetTargetStart(0)
#             doc.SetTargetEnd(doc.LastPosition)

        # restore caret's last position
        if int(pos):
            doc.GotoPos(int(pos))
            doc.SetFirstVisibleLine(int(vis) - 1)

        # get language based on file extension
        lng_lst = [e for e in LANG if ext in e[3].split('|')]

        # restore language
        if DEBUG['CFG']: print(f'{TXT_NIL:2}*** LANG:  In = [{lng_lst}]')
        if lng and lng_lst and lng not in lng_lst[0]:
            if DEBUG['CFG']: print(f'{TXT_NIL:11}CONF = [{lng}]')
            # get language based on lng_typ
            lng_lst = [t for t in LANG if lng == t[1]]

#NOTE, EXPERIMENTAL CODE FOR EXTENSION-LESS FILENAMES (e.g. '.pylintrc')
#INFO, see "D:\Dev\D\wx\TSN_SPyE\dev\spye\_WORK\HOWTO - find _bas_ext in extensions list.txt"
        # _bas_ext = lambda x, y: '' if not (s := set(y).intersection([x[-i:] for i in range(2, 3)])) else s
        # _is_bas_ext = lambda x, y: bool(_bas_ext(x, y))
        # if not lng_lst:
        #     lng_lst = [e for e in LANG if _is_bas_ext(fbs, e[3].split('|'))]
        # print([e for e in LANG if _is_bas_ext(fbs, e[3].split('|'))])

        if DEBUG['CFG']: print(f'{TXT_NIL:11} Out = [{lng_lst}]')
        doc.update_language_styling(lng_lst)
        nbk.update_page_tab(doc, newtab=True)

        # restore word wrap
        if DEBUG['CFG']: print(f'{TXT_NIL:2}*** WRAP:  In =       i[{doc.WrapMode}]')
        if int(wrp):
            if DEBUG['CFG']: print(f'{TXT_NIL:11}CONF = s[{wrp}], i[{doc.WrapMode}]')
            doc.SetWrapMode(int(wrp))  # stc.STC_WRAP_WORD
            mb.Check(MI['DOC_WRP'], True)
        if DEBUG['CFG']: print(f'{TXT_NIL:11} Out =       i[{doc.WrapMode}]\n')

        # restore EOL view
        if int(eol):
            doc.SetViewEOL(int(eol))
            mb.Check(MI['DOC_EOL'], True)

        # restore whitespace view
        if int(wsp):
            doc.SetViewWhiteSpace(int(wsp))
            mb.Check(MI['DOC_WSP'], True)

        # restore use tabs
        doc.SetUseTabs(int(tbu))

        # restore tab width
        doc.SetTabWidth(int(tbw))

        # restore zoom, offset
        doc.Zoom = CFG['Editor']['ZoomLevel']
        doc.XOffset = int(ofs)

        # restore selection
        if sel_lst and sel_lst[0] != sel_lst[1]:
            doc.SetSelection(*sel_lst)

        # restore bookmarks
        if bmk_lst:
            doc.set_bookmarks(bmk_lst)
        dbg_BOOKMARK('LOAD', doc, bmk_lst)

        # restore breakpoints
        if bpt_lst:
            doc.set_breakpoints(bpt_lst)
        dbg_BREAKPOINT('LOAD', doc, bpt_lst)

        # restore margins
        sec = CFG['Margin']
        val = sec['LineNumber']
        mb.Check(MI['MGN_NUM'], val)
        doc.SetMarginWidth(MGN['NUM'], 0 if not val else sec['LineNumberWidth'])

        val = sec['Symbol']
        mb.Check(MI['MGN_SYM'], val)
        doc.SetMarginWidth(MGN['SYM'], 0 if not val else sec['SymbolWidth'])

        val = sec['Folding']
        mb.Check(MI['MGN_FOL'], val)
        doc.SetMarginWidth(MGN['FOL'], 0 if not val else sec['FoldingWidth'])

        update_margins()

        # restore edge
        sec = CFG['Edge']
        val = sec['Mode']
        if val == stc.STC_EDGE_NONE:
            mb.Check(MI['EDG_NON'], val)
        elif val == stc.STC_EDGE_BACKGROUND:
            mb.Check(MI['EDG_BCK'], val)
        elif val == stc.STC_EDGE_LINE:
            mb.Check(MI['EDG_LIN'], val)
        # elif val == 3:
        # # elif val == stc.STC_EDGE_MULTILINE:
        #     mb.Check(MI['EDG_MUL'], val)
        doc.SetEdgeMode(val)
        doc.SetEdgeColumn(sec['Column'])
        doc.SetEdgeColour(sec['Colour'])

#TODO, add fold_style to 3 docstate methods, FOR NOW it is GLOBAL
        # # restore folding style
        # if int(fst) > -1:
        #     doc.fold_style = fst

    tlw.Thaw()

    nbk.make_tab_visible()

    # activate last file's page tab
    for pag, doc in nbk.open_docs():
        if pnm == doc.pnm:
            nbk.SetSelection(pag)
            break

    return doc


#NOTE, EXPERIMENTAL CODE FOR dynamic function call (Windows File Properties)
#INFO, Show Explorer's properties dialog for a file in Windows
#INFO, URL=https://stackoverflow.com/questions/7985122/show-explorers-properties-dialog-for-a-file-in-windows
#INFO, URL=https://docs.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-shellexecuteinfoa#syntax
SEE_MASK_NOCLOSEPROCESS = 0x00000040
SEE_MASK_INVOKEIDLIST = 0x0000000C


def win32_file_properties(pnm):
    ShellExecuteEx = CT.windll.shell32.ShellExecuteEx
    ShellExecuteEx.restype = WT.BOOL

    sei = SHELLEXECUTEINFO()
    sei.cbSize = CT.sizeof(sei)
    sei.fMask = SEE_MASK_NOCLOSEPROCESS | SEE_MASK_INVOKEIDLIST
    sei.lpVerb = CT.c_char_p(b"properties")
    sei.lpFile = CT.c_char_p(pnm.encode('utf-8'))
    sei.nShow = 1
    ShellExecuteEx(CT.byref(sei))


class SHELLEXECUTEINFO(CT.Structure):
    _fields_ = (
        ('cbSize',         WT.DWORD),
        ('fMask',          CT.c_ulong),
        ('hwnd',           WT.HANDLE),
        ('lpVerb',         CT.c_char_p),
        ('lpFile',         CT.c_char_p),
        ('lpParameters',   CT.c_char_p),
        ('lpDirectory',    CT.c_char_p),
        ('nShow',          CT.c_int),
        ('hInstApp',       WT.HINSTANCE),
        ('lpIDList',       CT.c_void_p),
        ('lpClass',        CT.c_char_p),
        ('hKeyClass',      WT.HKEY),
        ('dwHotKey',       WT.DWORD),
        ('hIconOrMonitor', WT.HANDLE),
        ('hProcess',       WT.HANDLE),
    )


def split_path(path):
    """
    Path Components:

        /path/leading/to/a/basename.extension
                           <_fbs__> <__ext__>
        <______dnm_______> <______fnm_______>
    """
    if DEBUG['GEN']: print(f'{me_()}')
    dnm = str(Path(path).parent)
    fnm = Path(path).name
    fbs = Path(fnm).stem
    ext = Path(fnm).suffix[1:].lower()  # strip dot
    dbg_FILE(f'  [{dnm}]\n  [{fnm}]\n  [{fbs}]\n  [{ext}]')
    return dnm, fnm, fbs, ext
