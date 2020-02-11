"""
Display of help menu contents and available options

"""
from versionpro import Colors, PACKAGE

c = Colors()


def help_menu():
    """
    Summary.

        Command line parameter options (Help Menu)

    """
    # formatting
    act = c.ORANGE                         # accent highlight (bright orange)
    bcy = c.BRIGHT_CYAN
    bd = c.BOLD + c.BRIGHT_WHITE           # title formatting
    rst = c.RESET
    lbct = bcy + '[' + rst
    rbct = bcy + ']' + rst
    ctr = bcy + '|' + rst

    menu = '''
                      ''' + bd + PACKAGE + rst + ''' help contents

  ''' + bd + '''DESCRIPTION''' + rst + '''

        Automates build package version updates. Validates incremental
        version with pypi registery to ensure consistent version sign-
        ature progression.

  ''' + bd + '''SYNOPSIS''' + rst + '''

        $ ''' + act + PACKAGE + rst + ' ' + lbct + ' --update ' + ctr + ' --dryrun ' + rbct + ' ' + lbct + ''' --force-set <value> ''' + rbct + '''

                         -u, --update
                        [-p, --pypi  ]
                        [-s, --force-set <value>  ]
                        [-d, --debug  ]
                        [-h, --help   ]

  ''' + bd + '''OPTIONS''' + rst + '''

        ''' + bd + '''-D''' + rst + ''', ''' + bd + '''--debug''' + rst + ''': Debugging mode, verbose output for bug tracing.

        ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--dryrun''' + rst + ''': Simulate version label update without altering
            the actual project version signature, but print stats.

        ''' + bd + '''-h''' + rst + ''', ''' + bd + '''--help''' + rst + ''':  Print this help menu and detailed option info.

        ''' + bd + '''-p''' + rst + ''', ''' + bd + '''--pypi''' + rst + ''': Increment the pypi package version if package is
            deployed in the public pypi.python.org registry.

        ''' + bd + '''-s''' + rst + ''', ''' + bd + '''--force-set''' + rst + ''' (string):  When given, overrides all version
            information contained in project to set the next version
            to the value specified by force-set parameter.  Must use
            with the --update option to affect a version change.

        ''' + bd + '''-u''' + rst + ''', ''' + bd + '''--update''' + rst + ''': Increment current package version. Can be used
            with --force-set to update to forced version number.

        ''' + bd + '''-V''' + rst + ''', ''' + bd + '''--version''' + rst + ''': Print app package version and copyright info.
    '''
    print(menu)
    return True
