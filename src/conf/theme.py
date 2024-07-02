#!/usr/bin/python

from pathlib import Path

from extern.configobj import ConfigObj
from extern.configobj.validate import Validator

from const.common import TXT_NIL
from .debug import DBG, dbf, me_


# colour element count
__ = 10  # convenient short naming (__)

THEMES = {
    'KEY|VAL': ('ToolBar|BackColour',
                'StatusBar|BackColour',
                'Editor|DefaultBackColour',
                'Margin|LineNumberBackColour',
                'Margin|FoldingColour',
                'Margin|FoldingHiColour',
                'SearchPanel|BackColourFND',
                'SearchPanel|BackColourRPL',
                'SearchPanel|BackColourFIF',
                'SearchPanel|BackColourINC',),
    'Default': ('#E6F2FF', '#71B3E8', '#E6F2FF', '#C0C0C0', '#C0C0C0', '#C0C0C0', '#E6F2FF', '#FFDDDD', '#FFE7CE', '#C6E2FF',),
    'Red'    : ['RED']*__,
    'Green'  : ['GREEN']*__,
    'Blue'   : ['BLUE']*__,
}

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#NOTE, EXPERIMENTAL: colour list for TESTING
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # 'Aquamarine': ['AQUAMARINE']*__,
    # 'Black': ['BLACK']*__,
    # 'Blue Violet': ['BLUE VIOLET']*__,
    # # 'Blue': ['BLUE']*__,
    # 'Brown': ['BROWN']*__,
    # 'Cadet Blue': ['CADET BLUE']*__,
    # 'Coral': ['CORAL']*__,
    # 'Cornflower Blue': ['CORNFLOWER BLUE']*__,
    # 'Cyan': ['CYAN']*__,
    # 'Dark Green': ['DARK GREEN']*__,
    # 'Dark Grey': ['DARK GREY']*__,
    # 'Dark Olive Green': ['DARK OLIVE GREEN']*__,
    # 'Dark Orchid': ['DARK ORCHID']*__,
    # 'Dark Slate Blue': ['DARK SLATE BLUE']*__,
    # 'Dark Slate Grey': ['DARK SLATE GREY']*__,
    # 'Dark Turquoise': ['DARK TURQUOISE']*__,
    # 'Dim Grey': ['DIM GREY']*__,
    # 'Firebrick': ['FIREBRICK']*__,
    # 'Forest Green': ['FOREST GREEN']*__,
    # 'Gold': ['GOLD']*__,
    # 'Goldenrod': ['GOLDENROD']*__,
    # 'Green Yellow': ['GREEN YELLOW']*__,
    # # 'Green': ['GREEN']*__,
    # 'Grey': ['GREY']*__,
    # 'Indian Red': ['INDIAN RED']*__,
    # 'Khaki': ['KHAKI']*__,
    # 'Light Blue': ['LIGHT BLUE']*__,
    # 'Light Grey': ['LIGHT GREY']*__,
    # 'Light Magenta': ['LIGHT MAGENTA']*__,
    # 'Light Steel Blue': ['LIGHT STEEL BLUE']*__,
    # 'Lime Green': ['LIME GREEN']*__,
    # 'Magenta': ['MAGENTA']*__,
    # 'Maroon': ['MAROON']*__,
    # 'Medium Aquamarine': ['MEDIUM AQUAMARINE']*__,
    # 'Medium Blue': ['MEDIUM BLUE']*__,
    # 'Medium Forest Green': ['MEDIUM FOREST GREEN']*__,
    # 'Medium Goldenrod': ['MEDIUM GOLDENROD']*__,
    # 'Medium Grey': ['MEDIUM GREY']*__,
    # 'Medium Orchid': ['MEDIUM ORCHID']*__,
    # 'Medium Sea Green': ['MEDIUM SEA GREEN']*__,
    # 'Medium Slate Blue': ['MEDIUM SLATE BLUE']*__,
    # 'Medium Spring Green': ['MEDIUM SPRING GREEN']*__,
    # 'Medium Turquoise': ['MEDIUM TURQUOISE']*__,
    # 'Medium Violet Red': ['MEDIUM VIOLET RED']*__,
    # 'Midnight Blue': ['MIDNIGHT BLUE']*__,
    # 'Navy': ['NAVY']*__,
    # 'Orange Red': ['ORANGE RED']*__,
    # 'Orange': ['ORANGE']*__,
    # 'Orchid': ['ORCHID']*__,
    # 'Pale Green': ['PALE GREEN']*__,
    # 'Pink': ['PINK']*__,
    # 'Plum': ['PLUM']*__,
    # 'Purple': ['PURPLE']*__,
    # # 'Red': ['RED']*__,
    # 'Salmon': ['SALMON']*__,
    # 'Sea Green': ['SEA GREEN']*__,
    # 'Sienna': ['SIENNA']*__,
    # 'Sky Blue': ['SKY BLUE']*__,
    # 'Slate Blue': ['SLATE BLUE']*__,
    # 'Spring Green': ['SPRING GREEN']*__,
    # 'Steel Blue': ['STEEL BLUE']*__,
    # 'Tan': ['TAN']*__,
    # 'Thistle': ['THISTLE']*__,
    # 'Turquoise': ['TURQUOISE']*__,
    # 'Violet Red': ['VIOLET RED']*__,
    # 'Violet': ['VIOLET']*__,
    # 'Wheat': ['WHEAT']*__,
    # 'White': ['WHITE']*__,
    # 'Yellow Green': ['YELLOW GREEN']*__,
    # 'Yellow': ['YELLOW']*__,
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class Theme(ConfigObj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#TODO, use configspec and validate it against a Validator object
        self.vld = Validator()  # not used

        if not Path(self.filename).is_file():
            self.create()

        self.load()

    def default(self):
        DBG('THM', f'{me_()}\n  File = {self.filename}\n')

        for thm in THEMES:
            if thm == 'KEY|VAL':
                continue
            self[thm] = {}
            for clr in range(len(THEMES[thm])):
                self[thm][THEMES['KEY|VAL'][clr]] = THEMES[thm][clr]

    def create(self):
        DBG('THM', f'{me_()}\n  File = {self.filename}\n')

        # get default theme configuration
        self.default()

        # add blank lines and header before all sections, except the first
        first_sec = 'Default'
        for sec in self:
            if sec != first_sec:
                for i in range(2):
                    self.comments[sec].insert(i, TXT_NIL)
            self.comments[sec].insert(2, 'Comment header for %s theme' % sec)

        self.save()

#FIX, not used: obsolete?
    def load(self):
        DBG('THM', f'{me_()}\n  File = {self.filename}\n')

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # for sec in self:
        #     print(sec)
        #     for key in self[sec]:
        #         print(' ', key, self[sec][key])
        #     print()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

#FIX, not used: obsolete?
    def save(self):
        DBG('THM', f'{me_()}\n  File = {self.filename}\n')

        self.write()
