from collections.abc import Iterable
from dataclasses import dataclass, field
import datetime
import numpy as np

from . import utils

DATE_FORMAT = "%Y%m%d%H"

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
    """Descriptor class for handling station lists"""

    def __get__(self, obj, objtype=None):
        if obj._stations is None:
            if obj._source is not None:
                from ._tdlpackio import _open_file_store

                obj._stations = [
                    s.decode("ascii").strip()
                    for s in _open_file_store[obj._source].read(obj._recnum).tolist()
                ]
                if len(obj._stations) != obj._nsta_expected:
                    raise ValueError(
                        f"Error reading stations, expected {obj._nsta_expected}, but got {len(obj._stations)}"
                    )
        return obj._stations

    def __set__(self, obj, value):
        if (
            isinstance(value, str)
            or isinstance(value, bytes)
            or not isinstance(value, Iterable)
        ):
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
    """TDLPACK version number.  Should always be 0."""

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
    """Seciton flags."""

    def __get__(self, obj, objtype=None):
        return obj._section_flags

    def __set__(self, obj, value):
        # Individual flags values are set by interacting with the TdlpackFlags object
        pass


class Year:
    """Year of Reference Date"""

    def __get__(self, obj, objtype=None):
        return int(obj.is1[2])

    def __set__(self, obj, value):
        obj.is1[2] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])


class Month:
    """Month of Reference Date"""

    def __get__(self, obj, objtype=None):
        return int(obj.is1[3])

    def __set__(self, obj, value):
        obj.is1[3] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])


class Day:
    """Day of Reference Date"""

    def __get__(self, obj, objtype=None):
        return int(obj.is1[4])

    def __set__(self, obj, value):
        obj.is1[4] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])


class Hour:
    """Hour of Reference Date"""

    def __get__(self, obj, objtype=None):
        return int(obj.is1[5])

    def __set__(self, obj, value):
        obj.is1[5] = value
        obj.refDate = datetime.datetime(*obj.is1[2:7])


class Minute:
    """Minute of Reference Date"""

    def __get__(self, obj, objtype=None):
        return int(obj.is1[6])

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
            value = datetime.timedelta(seconds=int(value / np.timedelta64(1, "s")))
        h, m = utils.validate_hours_minutes(value)
        obj.leadTimeHours = h
        obj.id.tau = obj.is1[12]
        obj.leadTimeMinutes = m


class LeadTimeHours:
    """Forecast lead time in hours"""

    def __get__(self, obj, objtype=None):
        return int(obj.is1[12])

    def __set__(self, obj, value):
        value = int(value)
        if value < 0 or value > 999:
            raise ValueError("leadTimeHours must be in the range 0–999 hours")
        obj.is1[12] = value
        obj.id.tau = value


class LeadTimeMinutes:
    """Minutes component of lead time."""

    def __get__(self, obj, objtype=None):
        return int(obj.is1[13])

    def __set__(self, obj, value):
        value = int(value)
        if value < 0 or value >= 60:
            raise ValueError("leadTimeMinutes must be in the range 0–59 minutes")
        obj.is1[13] = value


class ModelID:
    """Model ID. This is the same as the "dd" of the TDPACK ID"""

    def __get__(self, obj, objtype=None):
        return obj.is1[14]

    def __set__(self, obj, value):
        obj.is1[14] = value
        obj.id.dd = value


class ModelSequenceID:
    """Model sequence ID."""

    def __get__(self, obj, objtype=None):
        return obj.is1[15]

    def __set__(self, obj, value):
        obj.is1[15] = value


class DecScaleFactor:
    """Decimal Scale Factor for packing"""

    def __get__(self, obj, objtype=None):
        return obj.is1[16]

    def __set__(self, obj, value):
        obj.is1[16] = value


class BinScaleFactor:
    """Binary Scale Factor for packing"""

    def __get__(self, obj, objtype=None):
        return obj.is1[17]

    def __set__(self, obj, value):
        obj.is1[17] = value


class VariableName:
    """This is the TDLPACK "Plain Language" description of the variable"""

    def __get__(self, obj, objtype=None):
        return "".join([chr(i) for i in obj.is1[22:]])

    def __set__(self, obj, value):
        obj.is1[21] = 32
        value = value[:32].ljust(32)
        for n, s in enumerate(value[: obj.is1[21]]):
            obj.is1[22 + n] = np.int32(ord(s))


# --------------------------------------------------------------------------------------
# Section 2
# --------------------------------------------------------------------------------------
class MapProjection:
    """Map Projection"""

    def __get__(self, obj, objtype=None):
        return obj.is2[1]

    def __set__(self, obj, value):
        valid_mapproj = {3, 5, 7}
        if int(value) not in valid_mapproj:
            raise ValueError(f"mapProjection can only be {valid_mapproj}")
        obj.is2[1] = int(value)


class Nx:
    """Nx"""

    def __get__(self, obj, objtype=None):
        return obj.is2[2]

    def __set__(self, obj, value):
        if int(value) <= 0:
            raise ValueError(f"nx cannot be negative")
        obj.is2[2] = int(value)


class Ny:
    """Ny"""

    def __get__(self, obj, objtype=None):
        return obj.is2[3]

    def __set__(self, obj, value):
        if int(value) <= 0:
            raise ValueError(f"ny cannot be negative")
        obj.is2[3] = int(value)


class LatitudeLowerLeft:
    """Latitude of the lower left gridpoint"""

    def __get__(self, obj, objtype=None):
        return obj.is2[4] * 1e-4

    def __set__(self, obj, value):
        obj.is2[4] = value * 1e4
        obj._update_sha1_latlon()


class LongitudeLowerLeft:
    """longitude of the lower left gridpoint"""

    def __get__(self, obj, objtype=None):
        return obj.is2[5] * 1e-4

    def __set__(self, obj, value):
        obj.is2[5] = value * 1e4
        obj._update_sha1_latlon()


class OrientationLongitude:
    """Orientation Longitude"""

    def __get__(self, obj, objtype=None):
        return obj.is2[6] * 1e-4

    def __set__(self, obj, value):
        obj.is2[6] = value * 1e4
        obj._update_sha1_latlon()


class GridLength:
    """Grid length (i.e. mesh length)"""

    def __get__(self, obj, objtype=None):
        # Return in units of meters
        return obj.is2[7] * 1e-3

    def __set__(self, obj, value):
        # Set in units of mm
        obj.is2[7] = value * 1e3
        obj._update_sha1_latlon()


class StandardLatitude:
    """Standard Latitude"""

    def __get__(self, obj, objtype=None):
        return obj.is2[8] * 1e-4

    def __set__(self, obj, value):
        obj.is2[8] = value * 1e4
        obj._update_sha1_latlon()


class ProjParameters:
    """PROJ Parameters to define the reference system"""

    def __get__(self, obj, objtype=None):
        projparams = {}
        # Assume Earth to be spherical with radius 6371229.0 m.
        projparams["a"] = 6371229.0
        projparams["b"] = 6371229.0
        if obj.mapProjection == 3:
            # Lambert-Conformal
            projparams["proj"] = "lcc"
            projparams["lat_1"] = float(obj.standardLatitude)
            projparams["lat_2"] = float(obj.standardLatitude)
            projparams["lat_0"] = float(obj.standardLatitude)
            projparams["lon_0"] = float(obj.orientationLongitude)
        elif obj.mapProjection == 5:
            # Polar Stereographic
            projparams["proj"] = "stere"
            projparams["lat_ts"] = float(obj.standardLatitude)
            projparams["lat_0"] = 90.0  # North Pole
            projparams["lon_0"] = float(obj.orientationLongitude)
        elif obj.mapProjection == 7:
            # Mercator
            projparams["proj"] = "merc"
            projparams["lat_ts"] = float(obj.standardLatitude)
            projparams["lon_0"] = 0.0  # CHANGE THIS
        return projparams

    def __set__(self, obj, value):
        raise AttributeError(f"projParams is read-only")


@dataclass(init=False)
class GridDefinitionSection:
    """
    TDLPACK Grid Definition Section

    These metadata attributes map to specific items in the TdlpackRecord ojbect,
    is2 array attribute.
    """

    mapProjection: int = field(init=False, repr=False, default=MapProjection())
    nx: int = field(init=False, repr=False, default=Nx())
    ny: int = field(init=False, repr=False, default=Ny())
    latitudeLowerLeft: float = field(
        init=False, repr=False, default=LatitudeLowerLeft()
    )
    longitudeLowerLeft: float = field(
        init=False, repr=False, default=LongitudeLowerLeft()
    )
    orientationLongitude: float = field(
        init=False, repr=False, default=OrientationLongitude()
    )
    gridLength: float = field(init=False, repr=False, default=GridLength())
    standardLatitude: float = field(init=False, repr=False, default=StandardLatitude())
    projParams: float = field(init=False, repr=False, default=ProjParameters())

    @classmethod
    def _attrs(cls):
        return list(cls.__dataclass_fields__.keys())


# --------------------------------------------------------------------------------------
# Section 4
# --------------------------------------------------------------------------------------
class PackingFlags:
    """Packing flags"""

    def __get__(self, obj, objtype=None):
        return obj._packing_flags

    def __set__(self, obj, value):
        # Individual flags values are set by interacting with the TdlpackFlags object
        pass


class NumberOfPackedValues:
    """
    Number of packed values. This value is the number of stations when the
    record is vector or nx*ny when gridded.
    """

    def __get__(self, obj, objtype=None):
        return obj.is4[2]

    def __set__(self, obj, value):
        pass


class PrimaryMissingValue:
    """Primary missing value. Generally 9999"""

    def __get__(self, obj, objtype=None):
        return obj.is4[3]

    def __set__(self, obj, value):
        if value == obj.secondarMissingValue:
            raise ValueError(
                f"primary missing value cannot equal secondary missing value"
            )
        obj.is4[3] = int(value)
        obj.packingFlags["hasPrimaryMissingValue"] = 1


class SecondaryMissingValue:
    """Primary missing value. Generally 9997"""

    def __get__(self, obj, objtype=None):
        return obj.is4[4]

    def __set__(self, obj, value):
        if value == obj.primaryMissingValue:
            raise ValueError(
                f"secondary missing value cannot equal primary missing value"
            )
        obj.is4[4] = int(value)
        obj.packingFlags["hasSecondaryMissingValue"] = 1


class OverallMinValue:
    """Overall minimum value of data [READ-ONLY]"""

    def __get__(self, obj, objtype=None):
        return obj.is4[5]

    def __set__(self, obj, value):
        raise AttributeError(f"overallMinValue is read-only")


class NumberOfGroups:
    """Number of packing groups [READ-ONLY]"""

    def __get__(self, obj, objtype=None):
        return obj.is4[6]

    def __set__(self, obj, value):
        raise AttributeError(f"numberOfGroups is read-only")
