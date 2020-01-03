"""
Build Script local logging and configuration variables

    - Python3 only
    - Requirement to set artifact which contains PACKAGE name
    - log_mode sets type of logging (i.e. 'STREAM' or 'FILE')

"""
import os
import sys
import subprocess
from versionpro.help import help_menu


artifact = 'DESCRIPTION.rst'
enable_logging = True
log_filename = ''
log_path = ''
log_mode = 'STREAM'


def _root():
    """Returns root directory of git project repository"""
    cmd = 'git rev-parse --show-toplevel 2>/dev/null'
    return subprocess.getoutput(cmd).strip()


def package_name(artifact):
    try:
        with open(artifact) as f1:
            f2 = f1.readlines()
        for line in f2:
            if line.startswith('PACKAGE'):
                return line.split(':')[1].strip()
    except Exception:
        stdout_message('Cursor must be located in the root of a git project')
        sys.exit(0)
    return None


script_config = {
    "PROJECT": {
        "PACKAGE": 'versionpro',
    },
    "LOGGING": {
        "ENABLE_LOGGING": enable_logging,
        "LOG_FILENAME": log_filename,
        "LOG_PATH": log_path,
        "LOG_MODE": log_mode,
        "SYSLOG_FILE": False
    }
}
