from collections.abc import Iterable
from dataclasses import dataclass, field
import datetime
import numpy as np

from . import utils

DATE_FORMAT = '%Y%m%d%H'

_section_attrs = {
    0: [
        "edition",
    ],
    1: [
        "sectionFlags",
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "refDate",
        "id",
        "leadTime",
        "leadTimeHours",
        "leadTimeMinutes",
        "modelID",
        "modelSequenceID",
        "decScaleFactor",
        "binScaleFactor",
        "name",
        "validDate",
        "duration",
    ],
    2: [],
    4: [
        "packingFlags",
        "numberOfPackedValues",
        "primaryMissingValue",
        "secondaryMissingValue",
        "overallMinValue",
        "numberOfGroups",
    ],
}

# --------------------------------------------------------------------------------------
# Descriptor classes for dealing with stations
# --------------------------------------------------------------------------------------
class Stations:
    def __get__(self, obj, objtype=None):
        if obj._stations is None:
            if obj._source is not None:
                from ._tdlpackio import _open_file_store
                obj._stations = [s.decode('ascii').strip() for s in _open_file_store[obj._source].read(obj._recnum).tolist()]
                if len(obj._stations) != obj._nsta_expected:
                    raise ValueError(f"Error reading stations, expected {obj._nsta_expected}, but got {len(obj._stations)}")
        return obj._stations
    def __set__(self, obj, value):
        if isinstance(value, str) or isinstance(value, bytes) or not isinstance(value, Iterable):
            raise TypeError("stations must be an iterable of station IDs")
        # Restrict modification if record came from a source
        if obj._source is not None:
            raise AttributeError(
                "stations cannot be modified on records read from file"
            )
        obj._stations = list(value)

# --------------------------------------------------------------------------------------
# Section 0
# --------------------------------------------------------------------------------------
class Edition:
    """
    """
    def __get__(self, obj, objtype=None):
        return obj.is0[2]
    def __set__(self, obj, value):
        if int(value) != 0:
            raise ValueError(f"TDLPACK Edition (version) number must be zero")
        obj.is0[2] = int(value)

# --------------------------------------------------------------------------------------
# Section 1
# --------------------------------------------------------------------------------------
class SectionFlags:
    def __get__(self, obj, objtype=None):
        return f'{obj.is1[1]:08b}'
    def __set__(self, obj, value):
        obj.is1[1] = value

class Year:
    def __get__(self, obj, objtype=None):
        return obj.is1[2]
    def __set__(self, obj, value):
        obj.is1[2] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])

class Month:
    def __get__(self, obj, objtype=None):
        return obj.is1[3]
    def __set__(self, obj, value):
        obj.is1[3] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])

class Day:
    def __get__(self, obj, objtype=None):
        return obj.is1[4]
    def __set__(self, obj, value):
        obj.is1[4] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])

class Hour:
    def __get__(self, obj, objtype=None):
        return obj.is1[5]
    def __set__(self, obj, value):
        obj.is1[5] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])

class Minute:
    def __get__(self, obj, objtype=None):
        return obj.is1[6]
    def __set__(self, obj, value):
        obj.is1[6] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])

class RefDate:
    """Reference Date. NOTE: This is a `datetime.datetime` object."""
    def __get__(self, obj, objtype=None):
        return datetime.datetime(*obj.is1[2:7])
    def __set__(self, obj, value):
        if isinstance(value, np.datetime64):
            timestamp = (value - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(
                1, "s"
            )
            value = datetime.datetime.utcfromtimestamp(timestamp)
        if isinstance(value, datetime.datetime):
            obj.is1[2] = value.year
            obj.is1[3] = value.month
            obj.is1[4] = value.day
            obj.is1[5] = value.hour
            obj.is1[6] = value.minute
            obj.is1[7] = int(value.strftime(DATE_FORMAT))
        else:
            msg = "Reference date must be a datetime.datetime or np.datetime64 object."
            raise TypeError(msg)

class Id:
    """Tdlpack Record variable ID."""
    def __get__(self, obj, objtype=None):
        return obj._id
    def __set__(self, obj, value):
        if isinstance(value, list):
            obj._id.word1 = value[0]
            obj._id.word2 = value[1]
            obj._id.word3 = value[2]
            obj._id.word4 = value[3]
            # Update lead time item in is1 array.
            obj.is1[12] = obj._id.tau

class LeadTime:
    """Forecast Lead Time. NOTE: This is a `datetime.timedelta` object."""
    def __get__(self, obj, objtype=None):
        return datetime.timedelta(
            hours=int(obj.is1[12]),
            minutes=int(obj.is1[13]),
        )
    def __set__(self, obj, value):
        if isinstance(value, np.timedelta64):
            # Allows setting from xarray
            value = datetime.timedelta(
                seconds=int(value/np.timedelta64(1, 's')))
        h, m = utils.validate_hours_minutes(value)
        obj.leadTimeHours = h
        obj.id.tau = obj.is1[12]
        obj.leadTimeMinutes = m

class LeadTimeHours:
    def __get__(self, obj, objtype=None):
        return obj.is1[12]
    def __set__(self, obj, value):
        if value < 0 or value > 999:
            raise ValueError("leadTimeHours must be in the range 0–999 hours")
        obj.is1[12] = int(value)
        obj.id.tau = obj.is1[12]

class LeadTimeMinutes:
    def __get__(self, obj, objtype=None):
        return obj.is1[13]
    def __set__(self, obj, value):
        if value < 0 or value >= 60:
            raise ValueError("leadTimeMinutes must be in the range 0–59 minutes")
        obj.is1[13] = int(value)

class ModelID:
    def __get__(self, obj, objtype=None):
        return obj.is1[14]
    def __set__(self, obj, value):
        obj.is1[14] = value
        obj.id.dd = value

class ModelSequenceID:
    def __get__(self, obj, objtype=None):
        return obj.is1[15]
    def __set__(self, obj, value):
        obj.is1[15] = value

class DecScaleFactor:
    def __get__(self, obj, objtype=None):
        return obj.is1[16]
    def __set__(self, obj, value):
        obj.is1[16] = value

class BinScaleFactor:
    def __get__(self, obj, objtype=None):
        return obj.is1[17]
    def __set__(self, obj, value):
        obj.is1[17] = value

class VariableName:
    """
    This is the TDLPACK "Plain Language" description of the variable
    """
    def __get__(self, obj, objtype=None):
        return "".join([chr(i) for i in obj.is1[22:]])
    def __set__(self, obj, value):
        obj.is1[21] = 32
        if len(value) == 0:
            value = 32*" "
        for n,s in enumerate(value[:obj.is1[21]]):
            obj.is1[22+n] = np.int32(ord(s))

class ValidDate:
    def __get__(self, obj, objtype=None):
        return obj.refDate + obj.leadTime
    def __set__(self, obj, value):
        raise AttributeError(f"validDate is read-only")

# --------------------------------------------------------------------------------------
# Section 2
# --------------------------------------------------------------------------------------
class MapProjection:
    def __get__(self, obj, objtype=None):
        return obj.is2[1]
    def __set__(self, obj, value):
        valid_mapproj = {3, 5, 7}
        if int(value) not in valid_mapproj:
            raise ValueError(f"mapProjection can only be {valid_mapproj}")
        obj.is2[1] = int(value)

class Nx:
    def __get__(self, obj, objtype=None):
        return obj.is2[2]
    def __set__(self, obj, value):
        if int(value) <= 0:
            raise ValueError(f"nx cannot be negative")
        obj.is2[2] = int(value)

class Ny:
    def __get__(self, obj, objtype=None):
        return obj.is2[3]
    def __set__(self, obj, value):
        if int(value) <= 0:
            raise ValueError(f"ny cannot be negative")
        obj.is2[3] = int(value)

class LatitudeLowerLeft:
    def __get__(self, obj, objtype=None):
        return obj.is2[4]*1e-4
    def __set__(self, obj, value):
        obj.is2[4] = value*1e+4
        obj._update_sha1_latlon()

class LongitudeLowerLeft:
    def __get__(self, obj, objtype=None):
        return obj.is2[5]*1e-4
    def __set__(self, obj, value):
        obj.is2[5] = value*1e+4
        obj._update_sha1_latlon()

class OrientationLongitude:
    def __get__(self, obj, objtype=None):
        return obj.is2[6]*1e-4
    def __set__(self, obj, value):
        obj.is2[6] = value*1e+4
        obj._update_sha1_latlon()

class GridLength:
    def __get__(self, obj, objtype=None):
        # Return in units of meters
        return obj.is2[7]*1e-3
    def __set__(self, obj, value):
        # Set in units of mm
        obj.is2[7] = value*1e+3
        obj._update_sha1_latlon()

class StandardLatitude:
    def __get__(self, obj, objtype=None):
        return obj.is2[8]*1e-4
    def __set__(self, obj, value):
        obj.is2[8] = value*1e+4
        obj._update_sha1_latlon()

@dataclass(init=False)
class GridDefinitionSection():
    mapProjection: int = field(init=False, repr=False, default=MapProjection())
    nx: int = field(init=False, repr=False, default=Nx())
    ny: int = field(init=False, repr=False, default=Ny())
    latitudeLowerLeft: float = field(init=False, repr=False, default=LatitudeLowerLeft())
    longitudeLowerLeft: float = field(init=False, repr=False, default=LongitudeLowerLeft())
    orientationLongitude: float = field(init=False, repr=False, default=OrientationLongitude())
    gridLength: float = field(init=False, repr=False, default=GridLength())
    standardLatitude: float = field(init=False, repr=False, default=StandardLatitude())
    @classmethod
    @property
    def _attrs(cls):
        return list(cls.__dataclass_fields__.keys())

# --------------------------------------------------------------------------------------
# Section 4
# --------------------------------------------------------------------------------------
class PackingFlags:
    def __get__(self, obj, objtype=None):
        return f'{obj.is4[1]:08b}'
    def __set__(self, obj, value):
        pass

class NumberOfPackedValues:
    def __get__(self, obj, objtype=None):
        return obj.is4[2]
    def __set__(self, obj, value):
        pass

class PrimaryMissingValue:
    def __get__(self, obj, objtype=None):
        return obj.is4[3]
    def __set__(self, obj, value):
        obj.is4[3] = value

class SecondaryMissingValue:
    def __get__(self, obj, objtype=None):
        return obj.is4[4]
    def __set__(self, obj, value):
        obj.is4[4] = value

class OverallMinValue:
    def __get__(self, obj, objtype=None):
        return obj.is4[5]
    def __set__(self, obj, value):
        raise AttributeError(f"overallMinValue is read-only")

class NumberOfGroups:
    def __get__(self, obj, objtype=None):
        return obj.is4[6]
    def __set__(self, obj, value):
        raise AttributeError(f"numberOfGroups is read-only")
