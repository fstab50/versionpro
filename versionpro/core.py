"""
Summary.

    Core Logic Module -- Common Functionality

"""
import os
import sys
import re
import inspect
import logging
from shutil import which
from versionpro.colors import Colors
from versionpro import __version__

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)

try:
    from libtools.oscodes_unix import exit_codes
    os_type = 'Linux'
    user_home = os.getenv('HOME')
    splitchar = '/'                             # character for splitting paths (linux)
    acct = Colors.ORANGE
    text = Colors.BRIGHT_PURPLE
    TITLE = Colors.WHITE + Colors.BOLD
except Exception:
    from libtools.oscodes_win import exit_codes    # non-specific os-safe codes
    os_type = 'Windows'
    user_home = os.getenv('username')
    splitchar = '\\'                            # character for splitting paths (windows)
    acct = Colors.CYAN
    text = Colors.LT2GRAY
    TITLE = Colors.WHITE + Colors.BOLD


def is_binary_external(filepath):
    try:
        f = open(filepath, 'rb').read(1024)
        textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
        fx = lambda bytes: bool(bytes.translate(None, textchars))
    except Exception:
        return True
    return fx(f)


def remove_illegal(d, illegal_dirs=['venv', 'pycache', '_venv', '_env']):
    """
        Removes excluded file types

    Args:
        :d (list): list of filesystem paths ending with a file object
        :illegal (list):  list of file type extensions for to be excluded

    Returns:
        legal filesystem paths (str)
    """
    def parse_list(path):
        """Reads in list from file object"""
        with open(path) as f1:
            return [x.strip() for x in f1.readlines()]

    def is_binary(filepath):
        try:
            f = open(filepath, 'rb').read(1024)
            textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            fx = lambda bytes: bool(bytes.translate(None, textchars))
            return fx(f)
        except Exception:
            return True

    bad = []

    # filter for illegal or binary file object
    for fpath in d:

        fobject = os.path.split(fpath)[1]

        # filter for illegal dirs first, then files, then binary
        if list(filter(lambda x: x in fpath, illegal_dirs)):
            bad.append(fpath)

        if is_binary(fpath):
            bad.append(fpath)

    return sorted(list(set(d) - set(bad)))


def locate_fileobjects(origin, abspath=True):
    """
    Summary.

        - Walks local fs directories identifying all git repositories

    Args:
        - origin (str): filesystem directory location
        - abspath (bool): return absolute paths relative to current cursor position

    Returns:
        - paths, TYPE: list
        - Format:

         .. code-block:: json

                [
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/utils_email.py',
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/slack_delivery.py',
                    '/cloud-custodian/tools/c7n_mailer/c7n_mailer/datadog_delivery.py',
                    '/cloud-custodian/tools/c7n_sentry/setup.py',
                    '/cloud-custodian/tools/c7n_sentry/test_sentry.py',
                    '/cloud-custodian/tools/c7n_kube/setup.py',
                    '...
                ]

    """
    def relpath_normalize(path):
        """
        Prepends correct relative filesystem syntax if analyzed pwd
        """
        if pattern_hidden.match(path) or pattern_asci.match(path):
            return './' + path
        elif path.startswith('..'):
            return path

    pattern_hidden = re.compile('^.[a-z]+')                    # hidden file (.xyz)
    pattern_asci = re.compile('^[a-z]+', re.IGNORECASE)        # standalone, regular file
    fobjects = []

    if os.path.isfile(origin):
        return [origin]

    for root, dirs, files in os.walk(origin):
        for file in [f for f in files if '.git' not in root]:
            try:

                if abspath:
                    # absolute paths (default)
                    _path = os.path.abspath(os.path.join(root, file))
                else:
                    # relative paths (optional)
                    _path = os.path.relpath(os.path.join(root, file))
                    _path = relpath_normalize(_path)

                fobjects.append(_path)

            except OSError:
                logger.exception(
                    '%s: Read error while examining local filesystem path (%s)' %
                    (inspect.stack()[0][3], _path)
                )
                continue
    return remove_illegal(fobjects)
