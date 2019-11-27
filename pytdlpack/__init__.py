# init for pytdlpack package
from ._pytdlpack import *
from ._pytdlpack import __doc__,__pdoc__

from ._grid_definitions import grids

from .version import version as __version__

__all__ = ['__version__','TdlpackFile','TdlpackRecord','TdlpackStationRecord','TdlpackTrailerRecord',
           'open','create_grid_definition','grids']
