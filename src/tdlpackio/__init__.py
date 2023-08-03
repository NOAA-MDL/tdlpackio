# init for tdlpackio package
from ._tdlpackio import *
from ._tdlpackio import __doc__

#from ._grid_definitions import grids

from .version import version as __version__

__all__ = ['__version__','open','TdlpackRecord','TdlpackStationRecord','TdlpackTrailerRecord',]
