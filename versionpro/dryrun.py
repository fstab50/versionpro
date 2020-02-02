"""
Dry Run Report Generation Module:
    - Produces various versions report
    - Uses threading for concurrent processing

Module Functions:
    - Package Current Version:
        Reports current version label assigned to code in current repository
    - PYPI Version:
        Looks in global pypi.python.org registry for package
        reports version if found
    - Incremental Version:
        Reports next incremental version ( (> pypi or project version) + 1 )
    - display_table:
        renders vpt table to cli stdout
"""

import os
import sys
import inspect

# 3rd party
from veryprettytable import VeryPrettyTable
from libtools.js import export_iterobject
from libtools import stdout_message
from libtools import Colors
from libtools import stdout_message, logd
from versionpro import Colors, ColorMap


try:
    from keyup.oscodes_unix import exit_codes
    os_type = 'Linux'
    splitchar = '/'                             # character for splitting paths (linux)
    text = Colors.BRIGHT_CYAN
except Exception:
    from keyup.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    splitchar = '\\'                            # character for splitting paths (windows)
    text = Colors.CYAN


c = Colors()
cm = ColorMap()


# universal colors
yl = c.YELLOW + c.BOLD
fs = c.GOLD3
bd = c.BOLD
gn = c.BRIGHT_GREEN
btext = text + c.BOLD
bdwt = c.BOLD + c.BRIGHT_WHITE
dgray = c.DARK_GRAY1
frame = text
ub = c.UNBOLD
rst = c.RESET


tablespec = {
    'border': True,
    'header': True,
    'padding': 2,
    'field_max_width': 70
}

column_widths = {
    'project': 16,
    'pypi': 16,
    'incremental': 16,
}


def display_table(table, tabspaces=4):
    """
    Print Table Object offset from left by tabspaces
    """
    indent = ('\t').expandtabs(tabspaces)
    table_str = table.get_string()
    for e in table_str.split('\n'):
        print(indent + frame + e)
    sys.stdout.write(Colors.RESET + '\n\n')
    return True


def print_header(title, indent=4, spacing=4):
    """
    Paints title header grid of a vpt Table
    """
    divbar = frame + '-'
    upbar = frame + '|' + rst
    ltab = '\t'.expandtabs(indent)              # lhs indentation of title bar
    spac = '\t'.expandtabs(7)                   # rhs indentation of legend from divider bar
    tab4 = '\t'.expandtabs(4)                   # space between legend items
    tab5 = '\t'.expandtabs(5)                   # space between legend items
    tab6 = '\t'.expandtabs(6)                   # space between legend items
    # output header
    print('\n\n\n')
    print(tab4, end='')
    print(divbar * 67, end='\n')
    print(tab4 + '|' + ' ' * 65 + '|', end='\n')
    print('{}{}'.format(tab4 + '|' + tab4 * 5, title))
    print(tab4 + upbar + rst + tab4 * 16 + frame + ' |' + rst)
    return True


def spacing(days):
    s = ''
    for digit in str(days):
        s = s + ' '
    return s


def _postprocessing():
    return True


def setup_table(pv, pypi, inc):
    """
    Renders Table containing data elements via cli stdout
    """
    # setup table
    x = VeryPrettyTable(
            border=tablespec['border'],
            header=tablespec['header'],
            padding_width=tablespec['padding']
        )

    x.field_names = [
        bdwt + 'Project Version' + frame,
        bdwt + 'PYPI Version' + frame,
        bdwt + 'Incremental Version' + frame,
    ]

    title_cell1 = 'Current Project'
    title_cell2 = 'PYPI Repository'
    title_cell3 = 'Next Increment'

    # cell max width
    x.max_width[bdwt + title_cell1 + frame] = column_widths['project']
    x.max_width[bdwt + title_cell2 + frame] = column_widths['pypi']
    x.max_width[bdwt + title_cell3 + frame] = column_widths['incremental']

    # cell min = max width
    x.min_width[bdwt + title_cell1 + frame] = column_widths['project']
    x.min_width[bdwt + title_cell2 + frame] = column_widths['pypi']
    x.min_width[bdwt + title_cell3 + frame] = column_widths['incremental']

    # cell alignment
    x.align[bdwt + title_cell1 + frame] = 'c'
    x.align[bdwt + title_cell2 + frame] = 'c'
    x.align[bdwt + title_cell3  + frame] = 'c'

    # populate table
    #  key credentials are either expired (age > KEYAGE_MAX) or valid
    project_version = c.BOLD + c.BRIGHT_BLUE + pv + rst
    pypi_version = c.BOLD + c.BRIGHT_BLUE + pypi + rst
    inc_version = c.BOLD + c.BRIGHT_BLUE + inc + rst

    x.add_row(
        [
            rst + project_version + frame,
            rst + pypi_version + frame,
            rst + inc_version + frame,
        ]
    )

    # Table
    vtab_int = 7
    vtab = '\t'.expandtabs(vtab_int)
    msg = '{}Project Version Labels{}{}|{}'.format(btext, rst + frame, '  ' + vtab * 3, rst)
    print_header(title=msg, indent=10, spacing=vtab_int)
    display_table(x, tabspaces=4)
    return _postprocessing()
