from versionpro._version import __version__ as version


__author__ = 'Blake Huber'
__version__ = version
__email__ = "blakeca00@gmail.com"

PACKAGE = 'versionpro'

try:
    from versionpro.colors import Colors
    from versionpro.colormap import ColorMap
except Exception:
    pass
