"""
Handles incremental changes to project version id

Use & Restrictions:
    - version format X.Y.Z
    - x, y, z integers
    - can have 0 as either x, y, or z

"""

import os
import sys
import argparse
import inspect
import subprocess
from libtools import stdout_message, logd
from versionpro import Colors
from versionpro.config import script_config
from versionpro.about import about_object
from versionpro import __version__, PACKAGE

c = Colors()


# global logger
module = os.path.basename(__file__)
logd.local_config = script_config
logger = logd.getLogger(__version__)

# formatting
act = c.ORANGE                  # accent highlight (bright orange)
bd = c.BOLD + c.WHITE           # title formatting
bn = c.CYAN                     # color for main binary highlighting
lk = c.DARK_BLUE                # color for filesystem path confirmations
red = c.RED                     # color for failed operations
yl = c.GOLD3                    # color when copying, creating paths
rst = c.RESET                   # reset all color, formatting


try:
    from libtools.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')

except Exception:
    from libtools.oscodes_win import exit_codes         # non-specific os-safe codes
    os_type = 'Windows'
    user_home = os.getenv('username')


def _root():
    """Returns root directory of git project repository"""
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def current_version(module_path):
    with open(module_path) as f1:
        f2 = f1.read()
    return f2.split('=')[1].strip()[1:-1]


def greater_version(versionA, versionB):
    """
    Summary:
        Compares to version strings with multiple digits and returns greater
    Returns:
        greater, TYPE: str
    """
    try:

        list_a = versionA.split('.')
        list_b = versionB.split('.')

    except AttributeError:
        return versionA or versionB    # either A or B is None

    try:

        for index, digit in enumerate(list_a):
            if int(digit) > int(list_b[index]):
                return versionA
            elif int(digit) < int(list_b[index]):
                return versionB
            elif int(digit) == int(list_b[index]):
                continue

    except ValueError:
        return versionA or versionB    # either A or B is ''
    return versionA


def help_menu():
    """
    Summary.

        Command line parameter options (Help Menu)

    """
    bcy = c.BRIGHT_CYAN
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

  ''' + bd + '''OPTIONS''' + rst + '''

        $ ''' + act + PACKAGE + rst + ' ' + lbct + ' --update ' + ctr + ' --dryrun ' + rbct + ' ' + lbct + ''' --set-version <value> ''' + rbct + '''

                         -u, --update
                        [-p, --pypi  ]
                        [-s, --set-version <value>  ]
                        [-d, --debug  ]
                        [-h, --help   ]

        ''' + bd + '''-d''' + rst + ''', ''' + bd + '''--dryrun''' + rst + ''':  Simulate version update without altering the
            real project version signature. Output useful parameters.

        ''' + bd + '''-s''' + rst + ''', ''' + bd + '''--set-version''' + rst + ''' (string): When given, overrides all version
            information contained in the project to hardset the exact
            version specified by set-version parameter. Must be used
            with --update option to effect a version label change.

        ''' + bd + '''-u''' + rst + ''', ''' + bd + '''--update''' + rst + ''': Increment current package version. Can be used
            with --set-version to update to forced version number.

        ''' + bd + '''-D''' + rst + ''', ''' + bd + '''--debug''' + rst + ''': Debug mode, verbose output.

        ''' + bd + '''-h''' + rst + ''', ''' + bd + '''--help''' + rst + ''': Print this help menu

        ''' + bd + '''-V''' + rst + ''', ''' + bd + '''--version''' + rst + ''': Print package version and copyright info.
    '''
    print(menu)
    return True


def locate_version_module(directory):
    files = list(filter(lambda x: x.endswith('.py'), os.listdir(directory)))
    return [f for f in files if 'version' in f][0]


def identical_version(new, existing):
    """
    Validates if current version signature is same as version
    provided by build scripts
    """
    if new == existing:
        return True
    return False


def increment_version(current):
    major = '.'.join(current.split('.')[:2])
    minor = int(current.split('.')[-1]) + 1
    return '.'.join([major, str(minor)])


def options(parser, help_menu=True):
    """
    Summary:
        parse cli parameter options

    Returns:
        TYPE: argparse object, parser argument set

    """
    parser.add_argument("-d", "--dryrun", dest='dryrun', action='store_true', default=False, required=False)
    parser.add_argument("-D", "--debug", dest='debug', action='store_true', default=False, required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', default=False, required=False)
    parser.add_argument("-s", "--set-version", dest='set', default=None, nargs='?', type=str, required=False)
    parser.add_argument("-u", "--update", dest='update', action='store_true', default=False, required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    return parser.parse_known_args()


def package_name(artifact):
    with open(artifact) as f1:
        f2 = f1.readlines()
    for line in f2:
        if line.startswith('PACKAGE'):
            return line.split(':')[1].strip()
    return None


def package_version():
    """
    Prints package version and requisite PACKAGE info
    """
    print(about_object)
    sys.exit(exit_codes['EX_OK']['Code'])


def pypi_registry(package_name):
    """
        Validate package build version vs. pypi version if exists

    Returns:
        Full version signature if package   ||   N/A
        exists in pypi registry             ||

    """
    installed_cmd = 'pip3 show {} 2>/dev/null'.format(package_name)
    search_cmd = 'pip3 search {} 2>/dev/null'.format(package_name)

    try:

        r = subprocess.getoutput(search_cmd)
        return r.split('-')[0].split('(')[1].split(')')[0].strip()

    except Exception:
        return 'N/A'


def installed_version(package_name):
    """
        Validate package installed version if exists

    Returns:
        Full version signature if package   ||   N/A
        installed in local environment      ||

    """
    installed_cmd = 'pip3 show {} 2>/dev/null'.format(package_name)

    try:
        r = subprocess.getoutput(installed_cmd)
        parsed = r.split('\n')
        raw = [x for x in parsed if x.startswith('Version')][0]
        return raw.split(':')[1].strip()

    except Exception:
        return 'N/A'


def update_signature(version, path):
    """Updates version number module with new"""
    try:
        with open(path, 'w') as f1:
            f1.write("__version__ = '{}'\n".format(version))
            return True
    except OSError:
        stdout_message('Version module unwriteable. Failed to update version')
    return False


def update_dryrun(package_name, module, force, debug=False):
    """
    Summary.
        Increments pypi registry project version by
        1 minor increment

    Args:
        :force_version (Nonetype): Version signature (x.y.z)
          if version number is hardset instead of incremental

    Returns:
        Success | Failure, TYPE: bool

    """
    module_path = os.path.join(_root(), package_name, str(module))

    # current version
    current = current_version(module_path)
    stdout_message('Current project version found: {}'.format(current))

    pypi = pypi_registry(package_name)
    stdout_message('Current pypi registry version found: {}'.format(pypi))

    _version = greater_version(current, pypi)

    if valid_version(_version):
        # hard set existing version to force_version value
        version_new = increment_version(_version)

    else:
        stdout_message('You must enter a valid version (x.y.z)', prefix='WARN')
        sys.exit(1)

    stdout_message('Incremental project version: {}'.format(version_new if force is None else force))
    return True


def update_version(force_version, package_name, module, debug=False):
    """
    Summary.
        Increments project version by 1 minor increment
        or hard sets to version signature specified

    Args:
        :force_version (Nonetype): Version signature (x.y.z)
            if version number is hardset insetead of increment

    Returns:
        Success | Failure, TYPE: bool
    """
    module_path = os.path.join(_root(), package_name, str(module))

    # current version
    current = current_version(module_path)
    stdout_message('Current project version found: {}'.format(current))

    if force_version is None:
        # increment existing version label
        inc_version = increment_version(current)
        pypi_version = pypi_registry(package_name)
        version_new = greater_version(inc_version, pypi_version)

    elif identical_version(force_version, current):
        tab = '\t'.expandtabs(4)
        msg = 'Force version ({}) is same as current version signature. \n \
        {}Skipping version update. End version_update.'.format((force_version), tab)
        stdout_message(msg)
        return True

    elif valid_version(force_version):
        # hard set existing version to force_version value
        most_recent = greater_version(force_version, pypi_registry(package_name))
        version_new = greater_version(most_recent, increment_version(current))

    else:
        stdout_message('You must enter a valid version (x.y.z)', prefix='WARN')
        sys.exit(1)

    stdout_message('Incremental project version: {}'.format(version_new))
    return update_signature(version_new, module_path)


def valid_version(parameter, min=0, max=100):
    """
    Summary.

        User input validation.  Validates version string made up of integers.
        Example:  '1.6.2'.  Each integer in the version sequence must be in
        a range of > 0 and < 100. Maximum version string digits is 3
        (Example: 0.2.3 )

    Args:
        :parameter (str): Version string from user input
        :min (int): Minimum allowable integer value a single digit in version
            string provided as a parameter
        :max (int): Maximum allowable integer value a single digit in a version
            string provided as a parameter

    Returns:
        True if parameter valid or None, False if invalid, TYPE: bool

    """
    if isinstance(parameter, int):
        return False

    elif isinstance(parameter, float):
        parameter = str(parameter)

    component_list = parameter.split('.')
    length = len(component_list)

    try:
        if length <= 3:
            for component in component_list:
                if isinstance(int(component), int) and int(component) in range(min, max + 1):
                    continue
                else:
                    return False
    except ValueError:
        fx = inspect.stack()[0][3]
        invalid_msg = 'One or more version numerical components are not integers'
        logger.exception('{}: {}'.format(fx, invalid_msg))
        return False
    return True


def main():
    """
        Main execution caller

    Return:
        Success || Failure, TYPE: bool
    """
    # prerequisities
    PACKAGE = package_name(os.path.join(_root(), 'DESCRIPTION.rst'))
    module = locate_version_module(PACKAGE)
    parser = argparse.ArgumentParser(add_help=False)

    try:

        args, unknown = options(parser)

    except Exception as e:
        stdout_message(str(e), 'ERROR')
        return exit_codes['E_BADARG']['Code']

    if (args.help or len(sys.argv) == 1) and not args.version:
        help_menu()
        return 0

    elif args.version:
        package_version()
        return 1

    elif args.dryrun and args.update:
        stdout_message('Option --dryrun and --update cannot be used together.', prefix='FAIL')
        return 1

    elif args.set and not (args.update or args.dryrun):
        stdout_message('--set-version must be used with --update or --dryrun.', prefix='FAIL')
        return 1

    elif args.dryrun:
        # use version contained in pypi registry
        update_dryrun(PACKAGE, module, args.set, args.debug)
        return 0

    elif args.update:
        update_version(args.set, PACKAGE, module, args.debug)
        return 0


if __name__ == '__main__':
    sys.exit(main())
