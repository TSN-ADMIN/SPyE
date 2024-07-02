#!/usr/bin/python

from queue import Queue, Empty
import subprocess as SP
from threading import Thread

import wx

from common.date import now_
from common.file import open_files
from common.util import msg_box, rs_
from conf.debug import DBG, DEBUG, me_
from const.app import EXE, PDB_PROMPT
from const.editor import MRK
from const import glb


class Debugger:
    def __init__(self, doc):
        self.sec = glb.CFG['Debugger']

        self.doc = doc
        self.proc = None
        self.prv_lin = None
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.watches = []
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def exec_cmd(self, cmd):
        self.stdin_write(cmd)
        return self.stdout_read(self.q_out)

    def command(self, cmd):
        out = self.exec_cmd(cmd)

        print(f'\n[{cmd.upper()}]')
        print(out)

        # these commands do not return current filename and line
        if cmd == 'restart':
            self.quit()
            self.start()
            return

        # these commands do not return current filename and line
        if any(cmd in c for c in {'break', 'clear', 'able', 'p', 'display', 'whatis'}):
            return out

        fnm, lin, fnc = self.parse_output(out)
        if not lin:
            print('lin is None')
            return

        # must be an error, so continue to error
        if lin == self.prv_lin:
            print('*'*80)
            wx.CallAfter(self.command, 'continue')
            return

        self.prv_lin = lin

        # DBG('PDB', f'{lin:>4} [{fnm}]\n     [{self.doc.pnm}]')

        # switch to other file?
        if fnm != self.doc.pnm.lower():
            fil_lst = [[fnm]]
            open_files(fil_lst)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, redundant?
            # activate other file's page tab
            for pag, doc in glb.NBK.open_docs():
                if fnm == doc.pnm.lower():
                    glb.NBK.SetSelection(pag)
                    break
            self.doc = doc
# print(f'new:[{self.doc.pnm.lower()}]')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.jump_to_line(lin)

    def enqueue_stderr(self, err, queue, stop):
        for blk in iter(lambda: err.read(4096), ''):
            blk = blk.decode('utf-8')
            queue.put_nowait(blk)
            if stop():
                break
        err.close()
        DBG('PDB', f'Thread [{me_("F")}] closed')

    def enqueue_stdout(self, out, queue, stop):
        for blk in iter(lambda: out.read(4096), ''):
            blk = blk.decode('utf-8')
            # for c in blk:
            #     print(c, ord(c))
            queue.put_nowait(blk)
            if stop():
                break
        out.close()
        DBG('PDB', f'Thread [{me_("F")}] closed')

    def init_breakpoints(self):
        out = self.exec_cmd('break')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#FIX, needs better coding...
        # no output
        if out != PDB_PROMPT:
            return

        DBG('PDB==2', 'NO breakpoints')
        bpt_lst = self.doc.get_breakpoints()
        for bpn in bpt_lst:
            out = self.exec_cmd(f'break {bpn[2]}')
            if bpn[1] == 'No':
                out = self.exec_cmd(f'disable {bpn[0]}')

        # out = self.exec_cmd('break 261')
        # out = self.exec_cmd('break 262')
        # out = self.exec_cmd('condition 1 a == 4')
        # out = self.exec_cmd('condition 1 a == 5')
        # out = self.exec_cmd('tbreak 263')
        # out = self.exec_cmd('disable 2')

        out = self.exec_cmd('break')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def parse_output(self, out):
        # parse output
        out_lst = out.splitlines()

        for cur in out.splitlines():
            if cur.startswith('> '):
                break
            out_lst.pop(0)

        if not out_lst:
            return None, None, None

        cur = out_lst[0]  # current filename and line

#FIX, error handling when NO parentheses
        if (fr := cur.find('('))> -1:
            fr += 1
        else:
            print('>>>>>>>>>>> NO parentheses <<<<<<<<<<<')
        if (to := cur.find(')')) > -1:
            pass

        fnm, lin, fnc = cur[2:fr - 1], int(cur[fr:to]), cur[to + 1:-2]

        # DBG('PDB', f'{lin:>4} [{fnm}] {fnc}')

        return fnm, lin, fnc

    def quit(self):
        self.doc.MarkerDeleteAll(MRK['DBC']['NUM'])

        # self.doc.SetCaretLineBackground(glb.CFG['Caret']['LineBackColour'])
        # self.doc.SetCaretLineBackAlpha(glb.CFG['Caret']['LineBackAlpha'])

        # re-enable menu items with plain Function key accelerator
        # glb.MBR.rebuild_menubar(glb.TLW)
        glb.TLW.SetAcceleratorTable(self.sav_acc_tbl)

        # force stop of stdout/stderr threads
        self.stop_thread = True
        if self.proc:
            self.proc.terminate()
        self.proc = None

    def stdin_write(self, cmd=None):
        if not (cmd and self.proc):
            return
        DBG('PDB==3', f'{now_()}-stdin_:\n{rs_(21, "0")}\n{cmd}\n{rs_(21, "0")}\n')
        self.proc.stdin.write(bytes(cmd, 'utf-8'))
        self.proc.stdin.write(b'\n')
        self.proc.stdin.flush()

        # out = self.stdout_read(self.q_out)
        # return out

    def stderr_read(self, q_err):
        # err = prv_err = None
        err = None

        while True:
            # read stderr without blocking
            try:
                lin = q_err.get_nowait()  # or q_err.get(timeout=.001)
            except Empty:
                break
            else:
                err = lin

            # if err != prv_err:
            #     prv_err = err

        # DBG('PDB', err, end='')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # check stderr for exception and quit
        if err is not None:
            DBG('PDB>4', f'{now_()}-stderr:\n{rs_(21, "2")}\n{err}\n{rs_(21, "2")}\n')
            if 'Traceback' in err:
                msg_box(glb.TLW, 'ERROR', f'Exception (stderr)\n\n{err}')
                wx.CallAfter(self.quit)
            return True

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        return False

    def stdout_read(self, q_out):
        self.stderr_read(self.q_err)

        # out = prv_out = None
        out = None

        while True:
            # read stdout without blocking
            try:
                lin = q_out.get_nowait()  # or q_out.get(timeout=.001)
            except Empty:
                pass
            else:
                out = lin

            # if out != prv_out:
            #     prv_out = out
                break

        # DBG('PDB', out, end='')

        DBG('PDB>3', f'{now_()}-stdout:\n{rs_(21, "1")}\n{out}\n{rs_(21, "1")}\n')
        # strip prompt from output: 'out[:-8]'
        if DEBUG['PDB'] == 2 and 'breakpoint' in out: print(f'Breakpoints:\n{rs_(21, "-")}\n{out[:-8]}\n{rs_(21, "-")}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if out is not None:
#FIX, force 'quit' and 'start' after this msg to prevent crash
            if 'will be restarted' in out:
                # DBG('PDB', 'THE PROGRAM FINISHED AND WILL BE RESTARTED')
                if 'Post mortem debugger finished' in out:
                    msg_box(glb.TLW, 'WARN', f'{out}')
                else:
                    msg_box(glb.TLW, 'INFO', f'{out}')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        return out

    def jump_to_line(self, lin):
        self.doc.MarkerDeleteAll(MRK['DBC']['NUM'])
        # self.doc.MarkerDeleteAll(MRK['DBE']['NUM'])
        self.doc.MarkerAdd(lin - 1, MRK['DBC']['NUM'])
        # self.doc.MarkerAdd(262, MRK['DBE']['NUM'])
        self.doc.GotoLine(lin - 1)
        if self.sec['CentreCaret']:
            self.doc.VerticalCentreCaret()

    def start(self):
        def __walk_menu(mnu, lbl):
            # recursive menu walk
            for mni in mnu.MenuItems:
                if mni.IsSeparator():
                    continue
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                if '\tF' in mni.GetItemLabel() and not '\tF9' in mni.GetItemLabel():
                    mni.SetItemLabel(mni.GetItemLabelText())
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                if (sub := mni.SubMenu):
                    __walk_menu(sub, lbl)
        # self.doc.SetCaretLineBackground(self.sec['LineBackColour'])
        # self.doc.SetCaretLineBackAlpha(self.sec['LineBackAlpha'])

#FIX, save/set accel table on 'AppFrame'
        self.sav_acc_tbl = glb.MBR.acc_tbl

        for i in range(10):
#NOTE, prevent circular dependency
            from const.menubar import MI
            glb.MBR.Enable(MI[f'BMK_JB{i}'], False)

        glb.TLW.SetAcceleratorTable(glb.MBR.acc_tbl)

        # disable menu items with plain Function key accelerator
        # so overlapping 'PDB_KEYS' can be used for debugging
        # for mnu, lbl in glb.MBR.Menus:
        #     __walk_menu(mnu, lbl)

        self.proc = SP.Popen(f'{EXE["PYTHON"]} -m {EXE["PDB"]} {self.doc.pnm}', stdin=SP.PIPE, stdout=SP.PIPE, stderr=SP.PIPE, bufsize=0)

#INFO, Different ways to kill a Thread (use stop flag)
#INFO, URL=https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
        self.stop_thread = False

        self.q_out = Queue()
        t_out = Thread(target=self.enqueue_stdout, args=(self.proc.stdout, self.q_out, lambda: self.stop_thread), daemon=True)
        t_out.start()

        self.q_err = Queue()
        t_err = Thread(target=self.enqueue_stderr, args=(self.proc.stderr, self.q_err, lambda: self.stop_thread), daemon=True)
        t_err.start()

        out = self.exec_cmd('')
        __, lin, __ = self.parse_output(out)

        self.jump_to_line(lin)
        self.init_breakpoints()
