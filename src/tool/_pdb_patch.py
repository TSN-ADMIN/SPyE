from pdb import Pdb

_p = Pdb()
old_msg_mth = _p.message
_p.message('BEFORE patch')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def message(self, msg):
    print(msg, file=self.stdout)
    print('... and more ...')

Pdb.message = message

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

print('----------------------------')
_p.message('AFTER  patch')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

_p.message = old_msg_mth

print('----------------------------')
_p.message('RESTORE  patch')


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
EOF    c          d        h         list      q        rv       undisplay
a      cl         debug    help      ll        quit     s        unt
alias  clear      disable  ignore    longlist  r        source   until
args   commands   display  interact  n         restart  step     up
b      condition  down     j         next      return   tbreak   w
break  cont       enable   jump      p         retval   u        whatis
bt     continue   exit     l         pp        run      unalias  where

# Python debugger commands
PDB_CMDS = (
    'alias',
    'args',
    'break',
    'clear',
    'commands',
    'condition',
    'continue', True
    'debug',
    'disable', True
    'display',
    'down',
    'enable', True
    'EOF',
    'help',
    'ignore',
    'interact',
    'jump', True
    'list',
    'longlist',
    'next', True
    'p',
    'pp',
    'quit',
    'restart', True
    'return', True
    'retval', True
    'run',
    'source',
    'step', True
    'tbreak',
    'unalias',
    'undisplay',
    'until', True
    'up',
    'whatis',
    'where',
)


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


grep -C2 -HnE "^ *(class |def |return)" "D:\Dev\Python38\Lib\pdb.py"|cut -c21-

grep     -HnE "^ *(class |def |return)" "D:\Dev\Python38\Lib\pdb.py"|cut -c21-

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# D:\Dev\D\wx\TSN_SPyE\dev\spye\src>grep -HnE "^ *(class |def |return)" "D:\Dev\Python38\Lib\pdb.py"|cut -c21-
pdb.py:  87:    class Restart(Exception):
pdb.py:  94:    def find_function(funcname, filename):
pdb.py:  99:            return None
pdb.py:  104:                   return funcname, filename, lineno
pdb.py:  105:       return None
pdb.py:  107:   def getsourcelines(obj):
pdb.py:  111:           return lines, 1
pdb.py:  113:           return lines, 1
pdb.py:  114:       return inspect.getblock(lines[lineno:]), lineno+1
pdb.py:  116:   def lasti2lineno(code, lasti):
pdb.py:  121:               return lineno
pdb.py:  122:       return 0
pdb.py:  125:   class _rstr(str):
pdb.py:  127:       def __repr__(self):
pdb.py:  128:           return self
pdb.py:  138:   class Pdb(bdb.Bdb, cmd.Cmd):
pdb.py:  142:       def __init__(self, completekey='tab', stdin=None, stdout=None, skip=None,
pdb.py:  189:       def sigint_handler(self, signum, frame):
pdb.py:  196:       def reset(self):
pdb.py:  200:       def forget(self):
pdb.py:  207:       def setup(self, f, tb):
pdb.py:  222:           return self.execRcLines()
pdb.py:  225:       def execRcLines(self):
pdb.py:  227:               return
pdb.py:  241:                       return True
pdb.py:  245:       def user_call(self, frame, argument_list):
pdb.py:  249:               return
pdb.py:  254:       def user_line(self, frame):
pdb.py:  259:                   return
pdb.py:  264:       def bp_commands(self, frame):
pdb.py:  285:               return
pdb.py:  286:           return 1
pdb.py:  288:       def user_return(self, frame, return_value):
pdb.py:  291:               return
pdb.py:  296:       def user_exception(self, frame, exc_info):
pdb.py:  300:               return
pdb.py:  316:       def _cmdloop(self):
pdb.py:  329:       def preloop(self):
pdb.py:  342:       def interaction(self, frame, traceback):
pdb.py:  355:               return
pdb.py:  360:       def displayhook(self, obj):
pdb.py:  368:       def default(self, line):
pdb.py:  390:       def precmd(self, line):
pdb.py:  393:               return line
pdb.py:  413:           return line
pdb.py:  415:       def onecmd(self, line):
pdb.py:  423:               return cmd.Cmd.onecmd(self, line)
pdb.py:  425:               return self.handle_command_def(line)
pdb.py:  427:       def handle_command_def(self, line):
pdb.py:  431:               return
pdb.py:  434:               return # continue to handle other cmd def in the cmd list
pdb.py:  437:               return 1 # end of cmd list
pdb.py:  452:               return 1
pdb.py:  453:           return
pdb.py:  457:       def message(self, msg):
pdb.py:  460:       def error(self, msg):
pdb.py:  466:       def _complete_location(self, text, line, begidx, endidx):
pdb.py:  470:               return []
pdb.py:  483:           return ret
pdb.py:  485:       def _complete_bpnumber(self, text, line, begidx, endidx):
pdb.py:  489:           return [str(i) for i, bp in enumerate(bdb.Breakpoint.bpbynumber)
pdb.py:  492:       def _complete_expression(self, text, line, begidx, endidx):
pdb.py:  495:               return []
pdb.py:  510:                   return []
pdb.py:  512:               return [prefix + n for n in dir(obj) if n.startswith(dotted[-1])]
pdb.py:  515:               return [n for n in ns.keys() if n.startswith(text)]
pdb.py:  521:       def do_commands(self, arg):
pdb.py:  565:                   return
pdb.py:  600:       def do_break(self, arg, temporary = 0):
pdb.py:  621:               return
pdb.py:  640:                   return
pdb.py:  648:                   return
pdb.py:  675:                           return
pdb.py:  693:       def defaultFile(self):
pdb.py:  698:           return filename
pdb.py:  705:       def do_tbreak(self, arg):
pdb.py:  714:       def lineinfo(self, identifier):
pdb.py:  725:               return failed
pdb.py:  732:                   return failed
pdb.py:  745:           return answer or failed
pdb.py:  747:       def checkline(self, filename, lineno):
pdb.py:  759:               return 0
pdb.py:  765:               return 0
pdb.py:  766:           return lineno
pdb.py:  768:       def do_enable(self, arg):
pdb.py:  785:       def do_disable(self, arg):
pdb.py:  805:       def do_condition(self, arg):
pdb.py:  832:       def do_ignore(self, arg):
pdb.py:  867:       def do_clear(self, arg):
pdb.py:  885:               return
pdb.py:  903:               return
pdb.py:  918:       def do_where(self, arg):
pdb.py:  928:       def _select_frame(self, number):
pdb.py:  936:       def do_up(self, arg):
pdb.py:  943:               return
pdb.py:  948:               return
pdb.py:  956:       def do_down(self, arg):
pdb.py:  963:               return
pdb.py:  968:               return
pdb.py:  976:       def do_until(self, arg):
pdb.py:  989:                   return
pdb.py:  993:                   return
pdb.py:  997:           return 1
pdb.py:  1000:      def do_step(self, arg):
pdb.py:  1007:          return 1
pdb.py:  1010:      def do_next(self, arg):
pdb.py:  1016:          return 1
pdb.py:  1019:      def do_run(self, arg):
pdb.py:  1036:      def do_return(self, arg):
pdb.py:  1041:          return 1
pdb.py:  1044:      def do_continue(self, arg):
pdb.py:  1059:          return 1
pdb.py:  1062:      def do_jump(self, arg):
pdb.py:  1075:              return
pdb.py:  1091:      def do_debug(self, arg):
pdb.py:  1114:      def do_quit(self, arg):
pdb.py:  1120:          return 1
pdb.py:  1125:      def do_EOF(self, arg):
pdb.py:  1132:          return 1
pdb.py:  1134:      def do_args(self, arg):
pdb.py:  1151:      def do_retval(self, arg):
pdb.py:  1161:      def _getval(self, arg):
pdb.py:  1163:              return eval(arg, self.curframe.f_globals, self.curframe_locals)
pdb.py:  1169:      def _getval_except(self, arg, frame=None):
pdb.py:  1172:                  return eval(arg, self.curframe.f_globals, self.curframe_locals)
pdb.py:  1174:                  return eval(arg, frame.f_globals, frame.f_locals)
pdb.py:  1178:              return _rstr('** raised %s **' % err)
pdb.py:  1180:      def do_p(self, arg):
pdb.py:  1189:      def do_pp(self, arg):
pdb.py:  1202:      def do_list(self, arg):
pdb.py:  1233:                  return
pdb.py:  1253:      def do_longlist(self, arg):
pdb.py:  1263:              return
pdb.py:  1267:      def do_source(self, arg):
pdb.py:  1274:              return
pdb.py:  1279:              return
pdb.py:  1284:      def _print_lines(self, lines, start, breaks=(), frame=None):
pdb.py:  1305:      def do_whatis(self, arg):
pdb.py:  1313:              return
pdb.py:  1322:              return
pdb.py:  1330:              return
pdb.py:  1334:              return
pdb.py:  1340:      def do_display(self, arg):
pdb.py:  1359:      def do_undisplay(self, arg):
pdb.py:  1374:      def complete_undisplay(self, text, line, begidx, endidx):
pdb.py:  1375:          return [e for e in self.displaying.get(self.curframe, {})
pdb.py:  1378:      def do_interact(self, arg):
pdb.py:  1387:      def do_alias(self, arg):
pdb.py:  1416:              return
pdb.py:  1422:      def do_unalias(self, arg):
pdb.py:  1431:      def complete_unalias(self, text, line, begidx, endidx):
pdb.py:  1432:          return [a for a in self.aliases if a.startswith(text)]
pdb.py:  1446:      def print_stack_trace(self):
pdb.py:  1453:      def print_stack_entry(self, frame_lineno, prompt_prefix=line_prefix):
pdb.py:  1464:      def do_help(self, arg):
pdb.py:  1472:              return cmd.Cmd.do_help(self, arg)
pdb.py:  1476:                  return topic()
pdb.py:  1485:                  return
pdb.py:  1490:      def help_exec(self):
pdb.py:  1502:      def help_pdb(self):
pdb.py:  1507:      def lookupmodule(self, filename):
pdb.py:  1514:              return filename
pdb.py:  1517:              return f
pdb.py:  1522:              return filename
pdb.py:  1528:                  return fullname
pdb.py:  1529:          return None
pdb.py:  1531:      def _runmodule(self, module_name):
pdb.py:  1549:      def _runscript(self, filename):
pdb.py:  1596:  def run(statement, globals=None, locals=None):
pdb.py:  1599:  def runeval(expression, globals=None, locals=None):
pdb.py:  1600:      return Pdb().runeval(expression, globals, locals)
pdb.py:  1602:  def runctx(statement, globals, locals):
pdb.py:  1606:  def runcall(*args, **kwds):
pdb.py:  1607:      return Pdb().runcall(*args, **kwds)
pdb.py:  1609:  def set_trace(*, header=None):
pdb.py:  1617:  def post_mortem(t=None):
pdb.py:  1631:  def pm():
pdb.py:  1639:  def test():
pdb.py:  1643:  def help():
pdb.py:  1662:  def main():

