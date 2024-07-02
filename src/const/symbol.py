#!/usr/bin/python

import re

from common.type import DotDict


# symbol browser
SBW_TMPFIL_NAME = '$$$tmp$$$'  # temp filename

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# symbol regex pattern constants
pfx = '(def|class) +'
nam = '[a-zA-Z_][a-zA-Z0-9_]*'
tsq = "'''"  # triple single quote, not used
tdq = '"""'  #   "    double   ", not used
qts = '(\'(.*?)\')|(\"(.*?)\")'  # quoted string
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# symbol index types
#                         symbol   file  total  index  regex                                    regex
#    type    description   count  count  count   dict  pattern                                  group
SYMBOL = {
    'DFN': ['Definition',      0,     0,     0,    {}, rf'{pfx}({nam})',                            2,],
    'REF': ['Reference',       0,     0,     0,    {}, rf'({nam})\(',                               1,],
    'IMP': ['Import',          0,     0,     0,    {}, rf'(import) +([a-zA-Z._][a-zA-Z0-9._]+)',    2,],
    'VAR': ['Variable',        0,     0,     0,    {}, rf'({nam}) *=[^=]',                          1,],
    'WRD': ['Word',            0,     0,     0,    {}, rf'({nam})',                                 1,],
    'QTS': ['Quoted String',   0,     0,     0,    {}, rf'({qts})',                                 1,],
}


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# # symbol index types
# sym = (
# #                         symbol   file  total  index  regex                                    regex
# #    type    description   count  count  count   dict  pattern                                  group
#     ['DFN', 'Definition',      0,     0,     0,    {}, rf'{pfx}({nam})',                            2,],
#     ['REF', 'Reference',       0,     0,     0,    {}, rf'({nam})\(',                               1,],
#     ['IMP', 'Import',          0,     0,     0,    {}, rf'(import) +([a-zA-Z._][a-zA-Z0-9._]+)',    2,],
#     ['VAR', 'Variable',        0,     0,     0,    {}, rf'({nam}) *=[^=]',                          1,],
#     ['WRD', 'Word',            0,     0,     0,    {}, rf'({nam})',                                 1,],
#     ['QTS', 'Quoted String',   0,     0,     0,    {}, rf'({qts})',                                 1,],
# )

# # create dotdict from tuple
# new_SYMBOL = DotDict()

# for typ, dsc, sym_cnt, fil_cnt, tot_cnt, idx_dct, reg_pat, reg_grp in sym:
#     new_SYMBOL[typ] = DotDict({'dsc': dsc, 'sym_cnt': sym_cnt, 'fil_cnt': fil_cnt, 'tot_cnt': tot_cnt,
#                                            'idx_dct': idx_dct, 'reg_pat': reg_pat, 'reg_grp': reg_grp}
#     )

# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# for typ in new_SYMBOL:
#     t = new_SYMBOL[typ]
#     print(f'{t.dsc = :13}, {t.reg_pat = :37}, {t.reg_grp = }')
# #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# del sym
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# compile regex patterns
for typ in SYMBOL:
    if SYMBOL[typ][5]:
        SYMBOL[typ][5] = re.compile(SYMBOL[typ][5])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


#FIX, refactor to Enum class ??
# from enum import Enum
# class SymIcon(Enum):
#     VARIABLE = 0
#     UNKNOWN = 1
#     NAMESPACE = 2
#     CLASS = 3
#     MEMBER = 4
#     FUNCTION = 5

# symbol def tree icons
SDF_ICO_VARIABLE = 0
SDF_ICO_UNKNOWN = 1
SDF_ICO_NAMESPACE = 2
SDF_ICO_CLASS = 3
SDF_ICO_MEMBER = 4
SDF_ICO_FUNCTION = 5

# symbol def tree type info
SDF_TYPE = [
    ['V', 'Variables',  SDF_ICO_VARIABLE,],
    ['U', 'Unknowns',   SDF_ICO_UNKNOWN,],
    ['N', 'Namespaces', SDF_ICO_NAMESPACE,],
    ['C', 'Classes',    SDF_ICO_CLASS,],
    ['F', 'Functions',  SDF_ICO_FUNCTION,],
]
