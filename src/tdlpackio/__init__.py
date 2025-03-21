# init for tdlpackio package
from ._tdlpackio import *
from ._tdlpackio import __doc__

from .version import version as __version__

__all__ = ['__version__', 'open', 'TdlpackRecord', 'TdlpackStationRecord',
           'TdlpackTrailerRecord', 'TdlpackID']

try:
    from . import __config__
    __version__ = __config__.tdlpackio_version
    has_openmp_support = __config__.has_openmp_support
    tdlpack_static = __config__.tdlpack_static
    extra_objects = __config__.extra_objects
except(ImportError):
    pass

__tdlpacklib_version__ = '1.0.0' # For now...

def show_config():
    """Print tdlpackio build configuration information."""
    print(f'tdlpackio version {__version__} Configuration:')
    print(f'')
    print(f'libtdlpack library version: {__tdlpacklib_version__}')
    print(f'\tStatic library: {tdlpack_static}')
    print(f'\tOpenMP support: {has_openmp_support}')
    print(f'')
    print(f'Static libs:')
    for lib in extra_objects:
        print(f'\t{lib}')
