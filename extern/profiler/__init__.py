"""
Tools to easily profile python code and view results.

Usage:

>>> import profiler
>>> profiler.profiler().start(True)

Profiling will automatically end when python exits and open
the results with the default text editor.

Alternatively, you can perform profiling manually.

>>> import profiler
>>> p = profiler.profiler()
>>> p.start()
>>> print('All code called after start will be profiled')
>>> p.end()

The Profiler can also be used as a context manager

>>> import profiler
>>> with profiler.profiler():
...     print('Code in here will be profiled')

In each example, profile results will automatically be opened
in the default text editor when profiling completes.


"""

import atexit
import os
import pstats
import tempfile

try:
    import cProfile as _profile
except:
    import profile as _profile

from .__version__ import __version__

__all__ = ['profiler']


def profiler(filepath=None, sortby=None):
    """

    :param filepath: Optional filepath to save the profile stats.  By default they are
                     written to a temp file.
    :param sortby: Optional argument for sorting the profiling stats.
    :return:
    """
    return Profiler(filepath=filepath, sortby=sortby)


class Profiler:

    def __init__(self, filepath=None, sortby=None):
        if not sortby:
            sortby = 'cumulative'
        self.filepath = filepath
        self.sortby = sortby
        self.profile = None

    def __enter__(self):
        self.start(False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

    def start(self, auto_end=False):
        if self.profile is None:
            self.profile = _profile.Profile()
            self.profile.enable()
            if auto_end:
                atexit.register(self.end)

    def end(self):
        if self.profile is not None:
            self.profile.disable()
            sortby = self.sortby if isinstance(self.sortby, (list, tuple)) else [self.sortby]
            filepath = self.filepath
            if not filepath:
                _, filepath = tempfile.mkstemp('.txt', 'profile_')
            with open(filepath, 'w') as f:
                ps = pstats.Stats(self.profile, stream=f).sort_stats(*sortby)
                ps.print_stats()
                self.profile = None
            os.startfile(filepath)
