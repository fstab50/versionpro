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

        $ ''' + act + PACKAGE + rst + ' ' + lbct + ' --update ' + ctr + ' --dryrun ' + rbct + ' ' + lbct + ''' --set-version <value> ''' + rbct + '''

                         -u, --update
                        [-p, --pypi  ]
                        [-s, --set-version <value>  ]
                        [-d, --debug  ]
                        [-h, --help   ]

  ''' + bd + '''OPTIONS''' + rst + '''

        ''' + bd + '''-D''' + rst + ''', ''' + bd + '''--debug''' + rst + ''': Debug mode, verbose output for debug tracing.

        ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--dryrun''' + rst + ''':  Simulate version label update without altering
            the actual project version signature, print useful stats.

        ''' + bd + '''-h''' + rst + ''', ''' + bd + '''--help''' + rst + ''':  Print this help menu and detailed option info.

        ''' + bd + '''-p''' + rst + ''', ''' + bd + '''--pypi''' + rst + ''': Increment current package version if found in the
            public pypi.python.org registry.

        ''' + bd + '''-s''' + rst + ''', ''' + bd + '''--set-version''' + rst + ''' (string): When given, overrides all version
            information contained in the project to hardset the exact
            version specified by set-version parameter.  Must be used
            with --update option to effect a version label change.

        ''' + bd + '''-u''' + rst + ''', ''' + bd + '''--update''' + rst + ''':  Increment current package version. Can be used
            with --set-version to update to forced version number.

        ''' + bd + '''-V''' + rst + ''', ''' + bd + '''--version''' + rst + ''': Print package version and copyright info.
    '''
    print(menu)
    return True
