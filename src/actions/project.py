#!/usr/bin/python

from ._load import _load
from common.util import curdoc, curdoc_class, not_implemented


@_load
@curdoc_class(curdoc)
class Project:

    def project_close(self, evt):
        not_implemented(evt)

    def project_close_all_files(self, evt):
        not_implemented(evt)

    def project_files(self, evt):
        not_implemented(evt)

    def project_manage_file_list(self, evt):
        not_implemented(evt)

    def project_new(self, evt):
        not_implemented(evt)

    def project_open(self, evt):
        not_implemented(evt)

    def project_open_all_files(self, evt):
        not_implemented(evt)

    def project_recent_projects(self, evt):
        not_implemented(evt)
