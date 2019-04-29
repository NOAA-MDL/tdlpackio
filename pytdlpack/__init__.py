# init for pytdlpack package
from ._pytdlpack import *

from ._pytdlpack import __doc__,__pdoc__

__all__ = ['TdlpackFile','TdlpackRecord','TdlpackStationRecord','TdlpackTrailerRecord',
           'open','create_grid_def_dict','_read_ra_master_key']