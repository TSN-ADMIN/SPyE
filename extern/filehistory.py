#!/usr/bin/python

# copied from GitHub "wxWidgets/Phoenix", workaround for wx.FileHistory
#INFO, FileHistory puts non-intuitive mix of full paths and file-name-only items in managed menu #984
#INFO, URL=https://github.com/wxWidgets/Phoenix/issues/984

import pathlib
import wx


class FileHistory(wx.FileHistory):
    """Like wx.FileHistory, but changing how menu items are displayed
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.managed_menus = []
        self.base_id = super().GetBaseId()

    def _remove_file_from_menu(self, menu, i):
        # Delete specified item and all lower items
        # range + 1 because we've already removed the item in super()
        #   but not in our own menu
        for file_hist_i in range(i, super().GetCount() + 1):
            menu.Delete(self.base_id + file_hist_i)

        # Add back items with new IDs
        self._add_all_files_to_menu(menu, starting_file=i)

    def _remove_file_from_menus(self, i):
        for menu in self.managed_menus:
            self._remove_file_from_menu(menu, i)

    def _add_file_to_menu(self, menu):
        # Delete all history items
        # range - 1 because we've already added the item in super()
        #   but not in our own menu
        for file_hist_i in range(super().GetCount() - 1):
            menu.Delete(self.base_id + file_hist_i)

        # Add back items with new IDs
        self._add_all_files_to_menu(menu)

    def _add_file_to_menus(self):
        for menu in self.managed_menus:
            self._add_file_to_menu(menu)

    def _add_all_files_to_menu(self, menu, starting_file=0):
        # Add all items to end of menu
        for idx, file_hist_i in enumerate(range(starting_file, super().GetCount())):
            # prefix path with ordered number
            path = str(idx + 1) + ' ' + super().GetHistoryFile(file_hist_i)
            menu.Append(
                    self.base_id + file_hist_i,
                    self.FormatFilePathMenu(path)
                    )

    def _add_all_files_to_menus(self):
        for menu in self.managed_menus:
            self._add_all_files_to_menu(menu)

    def FormatFilePathMenu(self, file_path):
        file_path = pathlib.Path(file_path)
        try:
            # Attempt to find path relative to home directory
            file_path = file_path.relative_to(pathlib.Path.home())
        except ValueError:
            # keep absolute path if path not under home directory
            pass
        return str(file_path)

    def UseMenu(self, menu):
        self.managed_menus.append(menu)

    def RemoveMenu(self, menu):
        self.managed_menus.remove(menu)

    def AddFilesToMenu(self, *args, **kwargs):
        if args or kwargs.get('menu', False):
            self._add_all_files_to_menu(args[0])
        elif kwargs.get('menu', False):
            self._add_all_files_to_menu(kwargs['menu'])
        else:
            self._add_all_files_to_menus()

    def AddFileToHistory(self, filename):
        super().AddFileToHistory(filename)
        self._add_file_to_menus()

    def RemoveFileFromHistory(self, i):
        super().RemoveFileFromHistory(i)
        self._remove_file_from_menus(i)
