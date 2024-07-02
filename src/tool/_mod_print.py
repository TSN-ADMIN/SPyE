#INFO, How to modify imported source code on-the-fly?
#INFO, URL=https://stackoverflow.com/questions/41858147/how-to-modify-imported-source-code-on-the-fly

In [28]: import builtins

In [29]: _print = builtins.print

In [30]: def print(*args, **kw):
    ...:    _print('print overridden:', *args, **kw)
    ...:

In [31]: print('anything')
print overridden anything

In [32]:

#!/usr/bin/env python3
# my_script.py

import builtins

_print = builtins.print

def my_print(*args, **kwargs):
    _print('In my_print: ', end='')
    return _print(*args, **kwargs)

builtins.print = my_print

import my_module  # -> In my_print: hello
