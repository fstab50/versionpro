"""

versionpro :  Copyright 2018-2019, Blake Huber

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

see: https://www.gnu.org/licenses/#GPL

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
contained in the program LICENSE file.

"""

import os
import sys
import platform
import subprocess
from shutil import which
from shutil import copy2 as copyfile
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import getpass
from codecs import open
import versionpro


requires = [
    'libtools>=0.3.2',
    'veryprettytable>=0.8.1'
]


_project = 'versionpro'
_root = os.path.abspath(os.path.dirname(__file__))
_comp_fname = 'versionpro-completion.bash'


def _root_user():
    """
    Checks localhost root or sudo access.  Returns bool
    """
    if os.geteuid() == 0:
        return True
    elif subprocess.getoutput('echo $EUID') == '0':
        return True
    return False


def _user():
    """Returns username of caller"""
    return getpass.getuser()


def _set_pythonpath():
    """
    Temporarily reset PYTHONPATH to prevent home dir = python module home
    """
    os.environ['PYTHONPATH'] = '/'


def create_artifact(object_path, type):
    """Creates post install filesystem artifacts"""
    if type == 'file':
        with open(object_path, 'w') as f1:
            f1.write(sourcefile_content())
    elif type == 'dir':
        os.makedirs(object_path)


def module_dir():
    """Filsystem location of Python3 modules"""
    bin_path = which('python3.6') or which('python3.7')
    bin = bin_path.split('/')[-1]
    if 'local' in bin:
        return '/usr/local/lib/' + bin + '/site-packages'
    return '/usr/lib/' + bin + '/site-packages'


def os_parityPath(path):
    """
    Converts unix paths to correct windows equivalents.
    Unix native paths remain unchanged (no effect)
    """
    path = os.path.normpath(os.path.expanduser(path))
    if path.startswith('\\'):
        return 'C:' + path
    return path


class PostInstall(install):
    """
    Summary.

        Postinstall script to place bash completion artifacts
        on local filesystem

    """
    def valid_os_shell(self):
        """
        Summary.

            Validates install environment for Linux and Bash shell

        Returns:
            Success | Failure, TYPE bool

        """
        if platform.system() == 'Windows':
            return False
        elif which('bash'):
            return True
        elif 'bash' in subprocess.getoutput('echo $SHELL'):
            return True
        return False

    def run(self):
        """
        Summary.

            Executes post installation configuration only if correct
            environment detected

        """
        if self.valid_os_shell():

            completion_file = os.path.join(user_home(), '.bash_completion')
            completion_dir = os.path.join(user_home(), '.bash_completion.d')

            if not os.path.exists(os_parityPath(completion_file)):
                create_artifact(os_parityPath(completion_file), 'file')
            if not os.path.exists(os_parityPath(completion_dir)):
                create_artifact(os_parityPath(completion_dir), 'dir')

            ## ensure installation of home directory artifacts (data_files) ##

            # bash_completion; (overwrite if exists)
            copyfile(
                os_parityPath(os.path.join('bash', _comp_fname)),
                os_parityPath(os.path.join(completion_dir, _comp_fname))
            )
        install.run(self)


class PostInstallRoot(install):
    """
    Summary.

        Postinstall script to place bash completion artifacts
        on local filesystem

    """
    def valid_os_shell(self):
        """
        Summary.

            Validates install environment for Linux and Bash shell

        Returns:
            Success | Failure, TYPE bool

        """
        if platform.system() == 'Windows':
            return False
        elif which('bash'):
            return True
        elif 'bash' in subprocess.getoutput('echo $SHELL'):
            return True
        return False

    def run(self):
        """
        Summary.

            Executes post installation configuration only if correct
            environment detected

        """
        # bash shell + root user
        if self.valid_os_shell():
            completion_dir = '/etc/bash_completion.d'

            ## ensure installation of home directory artifacts (data_files) ##

            # bash_completion; (overwrite if exists)
            copyfile(
                os_parityPath(os.path.join('bash', _comp_fname)),
                os_parityPath(os.path.join(completion_dir, _comp_fname))
            )
        install.run(self)


def preclean(dst):
    if os.path.exists(dst):
        os.remove(dst)
    return True


def read(fname):
    basedir = os.path.dirname(sys.argv[0])
    return open(os.path.join(basedir, fname)).read()


def sourcefile_content():
    sourcefile = """
    for bcfile in ~/.bash_completion.d/* ; do
        [ -f "$bcfile" ] && . $bcfile
    done\n
    """
    return sourcefile


def user_home():
    """Returns os specific home dir for current user"""
    try:
        if platform.system() == 'Linux' or platform.system() == 'Darwin':
            # Linux or BSD Unix (Mac)
            return os.path.expanduser('~') or os.environ.get('HOME')

        elif platform.system() == 'Windows':
            username = os.getenv('username')
            return 'C:\\Users\\' + username

        elif platform.system() == 'Java':
            print('Unable to determine home dir, unsupported os type')
            sys.exit(1)
    except OSError as e:
        raise e


# branch install based on user priviledge level

if _root_user():

    setup(
        name=_project,
        version=versionpro.__version__,
        description='Version Managmement Utility for Python3 Projects',
        long_description=read('DESCRIPTION.rst'),
        url='https://github.com/fstab50/versionpro',
        author=versionpro.__author__,
        author_email=versionpro.__email__,
        license='GPL-3.0',
        classifiers=[
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
        ],
        keywords='CI/CD continuous integration continuous deployment version management',
        packages=find_packages(exclude=['assets', 'docs', 'reports', 'scripts', 'tests']),
        install_requires=requires,
        python_requires='>=3.6, <4',
        cmdclass={
            'install': PostInstallRoot
        },
        data_files=[
            (
                os.path.join('/etc/bash_completion.d'),
                [os.path.join('bash', _comp_fname)]
            )
        ],
        entry_points={
            'console_scripts': [
                'versionpro=versionpro.cli:main'
            ]
        },
        zip_safe=False
    )

else:

    # non-priviledged user

    setup(
        name=_project,
        version=versionpro.__version__,
        description='Version Managmement Utility for Python3 Projects',
        long_description=read('DESCRIPTION.rst'),
        url='https://github.com/fstab50/versionpro',
        author=versionpro.__author__,
        author_email=versionpro.__email__,
        license='GPL-3.0',
        classifiers=[
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
        ],
        keywords='CI/CD continuous integration continuous deployment version management',
        packages=find_packages(exclude=['assets', 'docs', 'reports', 'scripts', 'tests']),
        install_requires=requires,
        python_requires='>=3.6, <4',
        cmdclass={
            'install': PostInstall
        },
        data_files=[
            (
                os.path.join(user_home(), '.bash_completion.d'),
                [os.path.join('bash', _comp_fname)]
            ),
        ],
        entry_points={
            'console_scripts': [
                'versionpro=versionpro.cli:main'
            ]
        },
        zip_safe=False
    )
