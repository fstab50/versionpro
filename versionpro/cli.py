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
from versionpro.dryrun import setup_table
from versionpro.core import locate_fileobjects
from versionpro.about import about_object
from versionpro.help import help_menu
from versionpro import __version__, PACKAGE

c = Colors()


# global logger
module = os.path.basename(__file__)
logd.local_config = script_config
logger = logd.getLogger(__version__)

# python modules containing version labels
module_names = ['_version.py', 'version.py']

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


def _debug_display(*args):
    """Output variables and their values for debugging purposes"""
    for arg in args:
        stdout_message(f'{getattr(arg, Name)}: {arg}')
    return True


def varname(var):
    _local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in _local_vars if var_val is var]


def _root():
    """Returns root directory of git project repository"""
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def current_version(module_path):
    """Return the current application version label"""
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


def locate_version_module(directory):
    """
    Returns path to python project module containing __version__
    """
    files = list(filter(lambda x: x.endswith('.py'), os.listdir(directory)))
    return [f for f in files if 'version' in f][0]


def global_version_module(root):
    """
        A global search of all objects in the git repository
        to locate the python module containing version label

    Args:
        :root (str):  git repository root location

    Returns:
        single path to version module (str) ||  'unknown'
    """
    def disclaimer():
        stdout_message('Cursor must be located in the root of a git project')
        sys.exit(exit_codes['EX_OK']['Code'])

    temp = []
    try:
        for path in locate_fileobjects(root):
            if os.path.split(path)[1] in module_names:
                temp.append(path)
        path = temp[0]
        return os.path.split(path)[0].split('/')[-1], os.path.split(path)[1]
    except Exception:
        return disclaimer()


def identical_version(new, existing):
    """
    Validates if current version signature is same as version
    provided by build scripts
    """
    if new == existing:
        return True
    return False


def increment_version(current):
    """Increments minor revision number by one"""
    major = '.'.join(current.split('.')[:2])
    minor = int(current.split('.')[-1]) + 1
    return '.'.join([major, str(minor)])


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options

    Returns:
        TYPE: argparse object, parser argument set

    """
    parser.add_argument("-d", "--dryrun", dest='dryrun', action='store_true', default=False, required=False)
    parser.add_argument("-D", "--debug", dest='debug', action='store_true', default=False, required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', default=False, required=False)
    parser.add_argument("-s", "--force-set", dest='set', default=None, nargs='?', type=str, required=False)
    parser.add_argument("-p", "--pypi", dest='pypi', action='store_true', default=False, required=False)
    parser.add_argument("-u", "--update", dest='update', action='store_true', default=False, required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', default=False, required=False)
    return parser.parse_known_args()


def package_name(artifact):
    """
    Retrieves python package (app) name if denoted with 'PACKAGE' in a project file
    """
    try:
        with open(artifact) as f1:
            f2 = f1.readlines()
        for line in f2:
            if line.startswith('PACKAGE'):
                return line.split(':')[1].strip()
    except Exception:
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
    search_cmd = 'pip3 show {} | grep Version: 2>/dev/null'.format(package_name)

    try:

        r = subprocess.getoutput(search_cmd)
        if 'Version:' in r:
            return r.split(':')[1].strip()
        else:
            # package not found in pypi database
            return ''

    except Exception:
        return None


def pypi_version(package_name, module, debug=False):
    """Update version lablel by incrementing pypi registry version"""
    def native_version(pkg, version_module):
        new_version = increment_version(installed_version(pkg))
        return update_signature(new_version, version_module)

    try:
        module_path = os.path.join(_root(), package_name, module)
        pypi = pypi_registry(package_name)
        stdout_message('pypi.python.org registry version:  {}'.format(pypi), prefix='OK')
        new = increment_version(pypi)
        stdout_message('Incremented version to be applied:  {}'.format(new))
    except Exception:
        stdout_message('Problem retrieving version label from public pypi.python.org', prefix='WARN')
        return native_version(package_name, module_path)
    return update_signature(new, module_path) #if new else native_version(package_name, module_path)


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
        return None


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

    # pypi.python.org registry version, if exits
    pypi = pypi_registry(package_name) or 'N/A'

    # increment (next) version
    _version = greater_version(current, pypi)

    if valid_version(_version):
        # hard set existing version to force_version value
        version_new = force or increment_version(_version)
    else:
        stdout_message('You must enter a valid version (x.y.z)', prefix='WARN')
        sys.exit(1)
    return setup_table(current, pypi, version_new)


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
    def operational_parameters():
        """Extract parameters required for version configuration operations"""
        try:
            package = package_name(os.path.join(_root(), 'DESCRIPTION.rst'))
            version_module = locate_version_module(package)
        except Exception:
            return global_version_module(_root())
        return package, version_module

    parser = argparse.ArgumentParser(add_help=False)

    try:

        args, unknown = options(parser)

    except Exception as e:
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['E_BADARG']['Code'])

    if args.debug:
        stdout_message('PACKAGE: {}'.format(PACKAGE), prefix='DBUG')
        stdout_message('module: {}'.format(module), prefix='DBUG')
        stdout_message('module_path: {}'.format(os.path.join(PACKAGE, module)), prefix='DBUG')

    if args.help or (len(sys.argv) == 1):
        help_menu()
        return 0

    elif args.version:
        package_version()
        return 1

    elif args.dryrun and args.update:
        stdout_message('Option --dryrun and --update cannot be used together.', prefix='FAIL')
        return 1

    elif args.set and not (args.update or args.dryrun):
        stdout_message('--force-set must be used with --update or --dryrun.', prefix='FAIL')
        return 1

    elif args.dryrun:
        PACKAGE, module = operational_parameters()
        update_dryrun(PACKAGE, module, args.set, args.debug)
        return 0

    elif args.pypi:
        # use version contained in pypi registry
        PACKAGE, module = operational_parameters()
        pypi_version(PACKAGE, module, args.debug)
        return 0

    elif args.update:
        PACKAGE, module = operational_parameters()
        update_version(args.set, PACKAGE, module, args.debug)
        return 0


if __name__ == '__main__':
    sys.exit(main())
