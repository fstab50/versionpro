"""
Summary:
    Copyright, legal plate for display with PACKAGE version information
Args:
    url_doc (str): http url location pointer to official PACKAGE documentation
    url_sc (str):  http url location pointer to PACKAGE source code
    current_year (int): the current calendar year (4 digit)
Returns:
    copyright, legal objects
"""

import sys
import datetime
from libtools.colors import Colors
from versionpro import PACKAGE, __version__


# url formatting
url_sc = Colors.URL + 'https://github.com/fstab50/versionpro' + Colors.RESET

# copyright range thru current calendar year
current_year = datetime.datetime.today().year
copyright_range = '2017-' + str(current_year)

# python version number header
python_version = sys.version.split(' ')[0]
python_header = 'python'.title() + Colors.RESET + ' ' + python_version

# formatted package header
package_name = Colors.BOLD + PACKAGE + Colors.RESET


# --- package about statement -------------------------------------------------


title_separator = (
    ('\t').expandtabs(4) +
    '__________________________________________________________________\n\n\n'
    )

package_header = (
    '\n\t\t' + Colors.CYAN + PACKAGE + Colors.RESET + ' version: ' + Colors.WHITE +
    Colors.BOLD + __version__ + Colors.RESET + '  |  ' + python_header + '\n\n'
    )

copyright = Colors.LT2GRAY + """
    Copyright """ + copyright_range + """, Blake Huber.  This program distributed under
    MIT LICENSE.  Copyright notice must remain with derivative works.""" + Colors.RESET + """
    __________________________________________________________________
        """ + Colors.RESET

about_object = """
""" + title_separator + """

""" + package_header + """


    __________________________________________________________________
""" + copyright
