"""
Introduction
============

tdlpackio is a Python package for reading and writing TDLPACK-formatted data contained in Fortran-based
unformatted ("sequential") and direct-access ("random-access") files. tdlpackio provides a Cython extension
module, tdlpacklib, for interfacing to the [libtdlpack](https://github.com/NOAA-MDL/libtdlpack) Fortran library,
a subset of subroutines from the MOS-2000 (MOS2K) software system.

The TDLPACK data format is a GRIB-like binary data format that is exclusive to MOS2K Fortran-based sofftware
system.  This software system was developed at the NOAA/NWS/Meteorological Development Laboratory (MDL)
and its primary purpose is to perform statistical post-processing of meteorological data.
TDLPACK format is based on the World Meteorological Organizations (WMO) GRIdded Binary (GRIB), version 1,
but with modifications to support the needs of MDL's statistical post-processing needs -- mainly the ability
to store 1D (vector), datasets such as station observations, along with 2D gridded data.

The TDLPACK data format are contained in two types of Fortran-based files; sequential or random-access.
Sequential files are variable length, record-based, and unformatted. Random-access files are fixed-length
and direct-access. tdlpackio accommodates reading and writing of both types of TDLPACK files.

TDLPACK files can contain two other types of records: a station call letter record and trailer record.
A station call letter record can exist in both types of TDLPACK files and contains a stream of
alphanumeric characters (`CHARACTER(LEN=8)`).  A trailer record exists to signal that either another station
call letter record is about to be read or we have reached the end of the file (EOF).
A trailer record is not written to a random-access file.

For more information on the MOS-2000 software system and TDLPACK format, user is
referred to the official [MOS-2000 documentation](https://www.weather.gov/media/mdl/TDL_OfficeNote00-1.pdf).

Verison 2.0 Refactor
====================

tdlpackio v2.0 is a major factor of pytdlpack v1.x. The API, code design, and structure borrow heavily
from [grib2io](https://github.com/NOAA-MDL/grib2io) v2. As stated, TDLPACK data can live in a sequential
or random-access file, can contain vector or gridded data. tdlpackio v2 aims to provide data to the user
in a consistent manner. When opening a TDLPACK file, records are lazily-indexed so that data are only read
and unpacked only when necessary. tdlpackio performs the TDLPACK file reading natively in Python. The
open class contains methods for reading and indexing. However, packing and unpacking TDLPACK data as well
as writing to files are performed by the subroutines in libtdlpack.

Tutorials
=========
The following Jupyter Notebooks are available as tutorials:

* [General Usage](https://github.com/NOAA-MDL/tdlpackio/blob/master/demos/tdlpackio-v2.ipynb)
"""

from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from typing import ClassVar, Iterable, Literal, Optional
import builtins
import collections
import datetime
import hashlib
import numpy as np
import os
import struct
import sys

from . import tdlpacklib
from . import templates
from . import utils

FORTRAN_STDOUT_LUN = 12

TDLP_HEADER = 1413762128  # "TDLP" converted to int

L3264B = tdlpacklib.constants.L3264B
L3264W = tdlpacklib.constants.L3264W
NBYPWD = tdlpacklib.constants.NBYPWD

MINPK = 21
NCHAR = 8
ND5 = 5242880  # Accommodates a 20MB record
ND7 = 54
PMISS = 9999.0
SMISS = 9997.0

_latlon_store = dict()
_open_file_store = dict()
_record_class_store = dict()

tdlpacklib.open_log_file(FORTRAN_STDOUT_LUN, log_path=os.devnull)


class open:
    """
    Open class for tdlpackio.

    Parameters
    ----------
    path : str
        File name.

    mode : {'r', 'w'}, default 'r'
        File handle mode.

    format : {'sequential', 'random-access'}, optional
        File type when creating a new file.

    ra_template : {'small', 'large'}, optional
        Template used when creating random-access files.
    """

    _filetype_map = {
        "random-access": 1,
        "sequential": 2,
    }

    def __init__(self, path, mode="r", format=None, ra_template=None):
        if mode not in {"r", "w", "a"}:
            raise ValueError(f"Invalid mode: {mode}")
        if mode in {"r", "w"}:
            mode = mode + "b"
        elif mode == "a":
            mode = "wb"
        self.path = path
        self.mode = mode
        self.format = format
        self.ra_template = ra_template
        self._hasindex = False
        self._index = {}
        self._lun = -1
        self.mode = mode
        self.name = os.path.abspath(path)
        self.records = 0

        # Perform indexing on read
        if "r" in self.mode:
            self._filehandle = builtins.open(path, mode=mode)
            self.filetype = self._get_tdlpack_file_type()
            self._build_index()

        elif "w" in self.mode:
            self.bytes_written = 0
            self.records_written = 0
            self.filetype = format if format is not None else "sequential"
            if self.filetype == "random-access":
                ra_template = "small" if ra_template is None else ra_template
                iret, self._lun = tdlpacklib.open_tdlpack_file(self.name, self.mode, self._ifiletype, ra_template=ra_template)
            elif self.filetype == "sequential":
                self._filehandle = builtins.open(path, mode=mode)
                iret, self._lun = tdlpacklib.open_tdlpack_file(self.name, self.mode, self._ifiletype, ra_template=ra_template)

        # Add self to file data store
        _open_file_store[self.name] = self

    @property
    def _ifiletype(self):
        """Return numeric filetype"""
        return self._filetype_map[self.filetype]

    @property
    def size(self):
        """Return the file size."""
        return os.path.getsize(self.name)

    def __enter__(self):
        """"""
        return self

    def __exit__(self, atype, value, traceback):
        """"""
        self.close()

    def __iter__(self):
        """"""
        yield from self._index["record"]

    def __repr__(self):
        """"""
        strings = []
        keys = list(self.__dict__.keys())
        for k in keys:
            if not k.startswith("_"):
                strings.append(f"{k} = {self.__dict__[k]}\n")
        # Attach size property.
        strings.append(f"size = {self.size}\n")
        return "".join(strings)

    def __getitem__(self, key):
        """"""
        if isinstance(key, slice):
            return self._index["record"][key]
        elif isinstance(key, int):
            return self._index["record"][key]
        else:
            raise KeyError("Key must be an integer record number or a slice")

    def _get_tdlpack_file_type(self):
        """Determine the type of TDLPACK file"""
        self._filehandle.seek(0)
        a = struct.unpack(">i", self._filehandle.read(4))[0]
        b = struct.unpack(">i", self._filehandle.read(4))[0]
        self._filehandle.seek(0)
        return "random-access" if [a, b] == [0, 4] else "sequential"

    def _build_index(self):
        """Record Indexer"""
        # Initialize index dictionary
        self._index["offset"] = []
        self._index["size"] = []
        self._index["type"] = []
        self._index["record"] = []

        if self.filetype == "random-access":
            self._randomaccess_file_indexer()
        elif self.filetype == "sequential":
            self._sequential_file_indexer()
        self._hasindex = True

    def _randomaccess_file_indexer(self):
        """Indexer for random-access TDLPACK files"""
        # Read master key
        version, nids, nwords, nkyrec, maxent, lastky = struct.unpack(">iiiiii", self._filehandle.read(24))
        nbytes = nwords * NBYPWD
        last_key_check = [99999999] if lastky > 9999 else [9999, 99999999]
        self.master_key = dict(
            version=version,
            nids=nids,
            nwords=nwords,
            nkyrec=nkyrec,
            maxent=maxent,
            lastky=lastky,
        )
        self.key_records = []
        # Set file position to first key record
        self._filehandle.seek(nbytes)

        last_station_id_rec = -1
        last_station_lat_rec = -1
        last_station_lon_rec = -1

        # Iterate over all key records
        while True:
            # Read key record "header" data
            nkeys, prec_this_key, prec_next_key = struct.unpack(">iii", self._filehandle.read(12))
            self.key_records.append(
                dict(
                    nkeys=nkeys,
                    prec_this_key=prec_this_key,
                    prec_next_key=prec_next_key,
                )
            )

            ids = list()
            nsize = list()
            prec_begin = list()

            # Read key record information
            for i in range(nkeys):
                id1, id2, id3, id4, nd, bprec = struct.unpack(">iiiiii", self._filehandle.read(24))
                ids.append([id1, id2, id3, id4])
                nsize.append(nd)
                prec_begin.append(bprec)

            # Using key record info, move around file to inventory TDLPACK data
            for m, n, b in zip(ids, nsize, prec_begin):
                # Disect prec_begin
                prec1 = int(b / 1000.0)

                # Offset to the data record
                offset = (prec1 - 1) * nbytes
                self._filehandle.seek(offset)
                self._index["offset"].append(offset)
                self._index["size"].append(n * NBYPWD)

                # Determine record type.  Since the 4-word ID is stored in the
                # key record, we can use it to determine station call letter
                # record or TDLPACK data record.
                if m[0] == 400001000:
                    # Station ID record...not in TDLPACK format
                    rec = TdlpackStationRecord()
                    last_station_id_rec = self.records
                    rec._recnum = self.records
                    rec._source = self.name
                    rec._nsta_expected = int(n / 2)
                    self._index["record"].append(rec)
                    self._index["type"].append("station")
                else:
                    if m[0] == 400006000:
                        last_station_lat_rec = self.records
                    elif m[0] == 400007000:
                        last_station_lon_rec = self.records
                    # TDLPACK data record
                    ipack = np.frombuffer(self._filehandle.read(132), dtype=">i4").astype(np.int32)
                    iret, is0, is1, is2, is4 = tdlpacklib.unpack_meta(ipack)
                    if np.all(is2 == 0):
                        is2 = None
                    rec = TdlpackRecord(is0, is1, is2, is4)
                    rec._recnum = self.records
                    rec._linked_station_id_record = last_station_id_rec
                    rec._linked_station_lat_record = last_station_lat_rec
                    rec._linked_station_lon_record = last_station_lon_rec
                    rec._source = self.name
                    shape = (rec.ny, rec.nx) if rec.type == "grid" else (rec.numberOfPackedValues,)
                    ndim = len(shape)
                    dtype = "float32"
                    rec._data = TdlpackRecordOnDiskArray(
                        shape,
                        ndim,
                        dtype,
                        self.filetype,
                        self._filehandle,
                        rec,
                        self._index["offset"][-1],
                        self._index["size"][-1],
                    )
                    self._index["record"].append(rec)
                    self._index["type"].append("data")
                self.records += 1

            # Hold the record number of the last station ID record
            if self._index["type"][-1] == "station":
                _last_station_id_record = self.records  # This should be OK.

            # Break loop here, at last key record
            if prec_next_key in last_key_check:
                break
            offset = (prec_next_key - 1) * nbytes
            self._filehandle.seek(offset)

        # Make key_records immutable
        self.key_records = tuple(self.key_records)

    def _sequential_file_indexer(self):
        """Indexer for sequential TDLPACK files"""
        last_station_id_rec = -1
        last_station_lat_rec = -1
        last_station_lon_rec = -1

        # Iterate
        while True:
            try:
                # First read 4-byte Fortran record header
                pos = self._filehandle.tell()
                fortran_header = struct.unpack(">i", self._filehandle.read(4))[0]
                if fortran_header >= 132:
                    bytes_to_read = 132
                else:
                    bytes_to_read = fortran_header

                pos = self._filehandle.tell()
                ioctet = np.frombuffer(self._filehandle.read(8), dtype=">i8").astype(np.int64)[0]
                ipack = np.frombuffer(self._filehandle.read(bytes_to_read - 8), dtype=">i4").astype(np.int32)
                _header = struct.unpack(">4s", ipack[0])[0].decode()

                # Check to first 4 bytes of the data record to determine the data
                # record type.
                if _header == "PLDT":
                    if ipack[5] == 400006000:
                        last_station_lat_rec = self.records
                    elif ipack[5] == 400007000:
                        last_station_lon_rec = self.records
                    # TDLPACK data record
                    iret, is0, is1, is2, is4 = tdlpacklib.unpack_meta(ipack)
                    self._index["offset"].append(pos)
                    self._index["size"].append(fortran_header)  # Size given by Fortran header
                    if np.all(is2 == 0):
                        is2 = None
                    rec = TdlpackRecord(is0, is1, is2, is4)
                    rec._recnum = self.records
                    rec._linked_station_id_record = last_station_id_rec
                    rec._linked_station_lat_record = last_station_lat_rec
                    rec._linked_station_lon_record = last_station_lon_rec
                    rec._source = self.name
                    shape = (rec.ny, rec.nx) if rec.type == "grid" else (rec.numberOfPackedValues,)
                    ndim = len(shape)
                    dtype = "float32"
                    rec._data = TdlpackRecordOnDiskArray(
                        shape,
                        ndim,
                        dtype,
                        self.filetype,
                        self._filehandle,
                        rec,
                        self._index["offset"][-1],
                        self._index["size"][-1],
                    )
                    self._index["record"].append(rec)
                    self._index["type"].append("data")
                else:
                    if ioctet == 24 and ipack[4] == 9999:
                        # Trailer record
                        rec = TdlpackTrailerRecord()
                        rec._recnum = self.records
                        rec._source = self.name
                        self._index["offset"].append(pos)
                        self._index["size"].append(fortran_header)
                        self._index["type"].append("trailer")
                        self._index["record"].append(rec)
                    else:
                        # Station ID record
                        rec = TdlpackStationRecord()
                        last_station_id_rec = self.records
                        rec._recnum = self.records
                        rec._source = self.name
                        rec._nsta_expected = int(ioctet / 8)
                        self._index["offset"].append(pos)
                        self._index["size"].append(fortran_header)
                        self._index["type"].append("station")
                        self._index["record"].append(rec)

                # At this point we have successfully identified a TDLPACK record from
                # the file. Increment self.records and position the file pointer to
                # now read the Fortran trailer.
                self.records += 1  # Includes trailer records
                self._filehandle.seek(fortran_header - bytes_to_read, 1)
                fortran_trailer = struct.unpack(">i", self._filehandle.read(4))[0]

                # Check Fortran header and trailer for the record.
                if fortran_header != fortran_trailer:
                    raise IOError("Bad Fortran record.")

                # Hold the record number of the last station ID record
                if self._index["type"][-1] == "station":
                    _last_station_id_record = self.records  # This should be OK.

            except struct.error:
                self._filehandle.seek(0)
                break

    def read(self, n):
        """
        Read record from file.

        Parameters
        ----------
        n : int
            Record number.

        Returns
        -------
        numpy.ndarray
            Record data as a NumPy array. The returned dtype depends on the
            record type:

            - ``data`` or ``trailer`` : ``int32`` array.
            - ``station`` : fixed-width byte string array (``S8``).

        Notes
        -----
        The file pointer is positioned using the internal index before reading.
        Record size is determined from the file header (sequential) or index
        (random-access).
        """
        if "w" in self.mode:
            pass  # Remove this at some point....
        # Position file pointer to the beginning of the TDLPACK record.
        self._filehandle.seek(self._index["offset"][n])
        if self.filetype == "sequential":
            size = np.frombuffer(self._filehandle.read(8), dtype=">i8").astype(np.int64)[0]
        elif self.filetype == "random-access":
            size = self._index["size"][n]

        if self._index["type"][n] in {"data", "trailer"}:
            return np.frombuffer(self._filehandle.read(size), dtype=">i4").astype(np.int32)
        elif self._index["type"][n] == "station":
            return np.frombuffer(self._filehandle.read(size), dtype="S8")

    def write(self, record):
        """
        Write record(s) to file.

        Parameters
        ----------
        record : TdlpackStationRecord, _TdlpackRecord, TdlpackTrailerRecord, or list
            Record or list of records to write.

            - ``TdlpackStationRecord`` : Station record. Station identifiers
              are padded to ``NCHAR``.
            - ``_TdlpackRecord`` : Packed data record.
            - ``TdlpackTrailerRecord`` : Trailer record.
            - ``list`` : List of supported record types.

        Returns
        -------
        None

        Notes
        -----
        Updates ``bytes_written``, ``records_written``, ``records``, and
        ``_type_lastrecord_written``.
        """
        if isinstance(record, list):
            for rec in record:
                self.write(rec)
            return

        nreplace, ncheck = 0, 0

        if isinstance(record, TdlpackStationRecord):
            # Adjust string length of each station to NCHAR.
            stns = [s.ljust(NCHAR) for s in record.stations]
            iret, self.bytes_written, self.records_written = tdlpacklib.write_station_record(
                self.name,
                self._lun,
                self._ifiletype,
                stns,
                self.bytes_written,
                self.records_written,
                nreplace,
                ncheck,
            )

        elif issubclass(record.__class__, _TdlpackRecord):
            iret, self.bytes_written, self.records_written = tdlpacklib.write_tdlpack_record(
                self.name,
                self._lun,
                self._ifiletype,
                record._ipack,
                self.bytes_written,
                self.records_written,
                nreplace,
                ncheck,
            )

        elif isinstance(record, TdlpackTrailerRecord):
            iret, self.bytes_written, self.records_written = tdlpacklib.write_trailer_record(
                self._lun, self._ifiletype, self.bytes_written, self.records_written
            )

        self._type_lastrecord_written = record.type
        self.records += 1

    def close(self):
        """
        Close the file.

        Returns
        -------
        None

        Notes
        -----
        For write mode, a trailer record may be written for sequential files
        if the last record type requires it. The underlying TDLpack file handle
        is then closed. The file is removed from the internal open file store.
        """
        if "r" in self.mode:
            self._filehandle.close()
        if "w" in self.mode:
            if self.filetype == "sequential":
                if self._type_lastrecord_written == "vector":
                    iret = tdlpacklib.write_trailer_record(
                        self._lun,
                        self._ifiletype,
                        self.bytes_written,
                        self.records_written,
                    )
            iret = tdlpacklib.close_tdlpack_file(self._lun, self._ifiletype)
            if iret != 0:
                raise ValueError("return from tdlpacklib.close_tdlpack_file is non-zero")
        if self.name in _open_file_store.keys():
            del _open_file_store[self.name]

    def select(self, **kwargs):
        """
        Select records by attribute.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments specifying ``TdlpackRecord`` attributes and
            values to match.

        Returns
        -------
        list
            List of records matching all provided attribute/value pairs.

        Notes
        -----
        Selection is performed against records in the internal index. Records
        must match all specified attributes to be included in the result.
        """
        _id_keys = [
            "word1",
            "word2",
            "word3",
            "word4",
            "ccc",
            "fff",
            "b",
            "dd",
            "v",
            "llll",
            "uuuu",
            "t",
            "rr",
            "o",
            "hh",
            "tau",
            "thresh",
            "i",
            "s",
            "g",
        ]

        # TODO: Add ability to process multiple values for each keyword (attribute)
        idxs = []
        nkeys = len(kwargs.keys())
        for k, v in kwargs.items():
            if k in _id_keys:
                for rec in self._index["record"]:
                    # if hasattr(rec, k) and getattr(rec, k) == v:
                    if getattr(rec.id, k) == v:
                        idxs.append(rec._recnum)
            else:
                for rec in self._index["record"]:
                    if hasattr(rec, k) and getattr(rec, k) == v:
                        idxs.append(rec._recnum)
        idxs = np.array(idxs, dtype=">i4")
        return [self._index["record"][i] for i in [ii[0] for ii in collections.Counter(idxs).most_common() if ii[1] == nkeys]]


class TdlpackRecord:
    """
    Creation class for TDLPACK record objects.

    This class dynamically constructs and returns an instance of a
    ``_TdlpackRecord`` subclass based on the provided section arrays and
    optional keyword arguments. Record classes are cached by type to avoid
    repeated class construction.

    Parameters
    ----------
    is0 : numpy.ndarray, optional
        Section 0 array. Default is zero-initialized ``int32`` array of size ``ND7``.
    is1 : numpy.ndarray, optional
        Section 1 array. Default is zero-initialized ``int32`` array of size ``ND7``.
    is2 : numpy.ndarray, optional
        Section 2 array. Default is zero-initialized ``int32`` array of size ``ND7``.
    is4 : numpy.ndarray, optional
        Section 4 array. Default is zero-initialized ``int32`` array of size ``ND7``.
    *args : tuple
        Additional positional arguments passed to the constructed record class.
    **kwargs : dict
        Optional keyword arguments. The following key is recognized:

        - ``type`` : str, optional
          Record type. Default is ``"vector"``. If ``is2`` contains any
          non-zero values, the type is automatically set to ``"grid"``.

    Returns
    -------
    _TdlpackRecord
        Instance of a dynamically generated subclass of ``_TdlpackRecord``.

    Notes
    -----
    - Record subclasses are created dynamically and cached in
      ``_record_class_store`` using the record type as the key.
    - For ``"grid"`` records, ``templates.GridDefinitionSection`` is added
      as a base class and ``is1[1]`` is set to indicate the presence of a
      grid definition section.
    """

    def __new__(
        self,
        is0: np.array = np.zeros((ND7), dtype=np.int32),
        is1: np.array = np.zeros((ND7), dtype=np.int32),
        is2: np.array = np.zeros((ND7), dtype=np.int32),
        is4: np.array = np.zeros((ND7), dtype=np.int32),
        *args,
        **kwargs,
    ):

        rectype = "vector"
        if "type" in kwargs.keys():
            rectype = kwargs["type"]
            if rectype not in {"grid", "vector"}:
                raise ValueError('Invalid "type" argument. Expected "grid" or "vector".')

        if bool(np.any(is2)):
            rectype = "grid"

        bases = list()
        if rectype == "grid":
            bases.append(templates.GridDefinitionSection)
            is1[1] = 1  # Flag in is1 to state that a grid definition section exists

        try:
            Record = _record_class_store[rectype]
        except KeyError:

            @dataclass(init=False, repr=False)
            class Record(_TdlpackRecord, *bases):
                pass

            _record_class_store[rectype] = Record

        return Record(is0, is1, is2, is4, *args)


@dataclass
class _TdlpackRecord:
    """TDLPACK Record base class"""

    # TDLPACK Sections
    is0: np.array = field(init=True, repr=False)
    is1: np.array = field(init=True, repr=False)
    is2: np.array = field(init=True, repr=False)
    is4: np.array = field(init=True, repr=False)

    # Section 0 looked up attributes
    edition: int = field(init=False, repr=False, default=templates.Edition())

    # Section 1 looked up attributes
    sectionFlags: int = field(init=False, repr=False, default=templates.SectionFlags())
    year: int = field(init=False, repr=False, default=templates.Year())
    month: int = field(init=False, repr=False, default=templates.Month())
    day: int = field(init=False, repr=False, default=templates.Day())
    hour: int = field(init=False, repr=False, default=templates.Hour())
    minute: int = field(init=False, repr=False, default=templates.Minute())
    refDate: int = field(init=False, repr=False, default=templates.RefDate())
    id: int = field(init=False, repr=False, default=templates.Id())
    leadTime: int = field(init=False, repr=False, default=templates.LeadTime())
    leadTimeHours: int = field(init=False, repr=False, default=templates.LeadTimeHours())
    leadTimeMinutes: int = field(init=False, repr=False, default=templates.LeadTimeMinutes())
    modelID: int = field(init=False, repr=False, default=templates.ModelID())
    modelSequenceID: int = field(init=False, repr=False, default=templates.ModelSequenceID())
    decScaleFactor: int = field(init=False, repr=False, default=templates.DecScaleFactor())
    binScaleFactor: int = field(init=False, repr=False, default=templates.BinScaleFactor())
    name: str = field(init=False, repr=False, default=templates.VariableName())

    # Section 4 looked up attributes
    packingFlags: int = field(init=False, repr=False, default=templates.PackingFlags())
    numberOfPackedValues: int = field(init=False, repr=False, default=templates.NumberOfPackedValues())
    primaryMissingValue: int = field(init=False, repr=False, default=templates.PrimaryMissingValue())
    secondaryMissingValue: int = field(init=False, repr=False, default=templates.SecondaryMissingValue())
    overallMinValue: int = field(init=False, repr=False, default=templates.OverallMinValue())
    numberOfGroups: int = field(init=False, repr=False, default=templates.NumberOfGroups())

    def __post_init__(self):
        """"""
        self._data_modified = False
        self._linked_station_id_record = -1
        self._linked_station_lat_record = -1
        self._linked_station_lon_record = -1
        self._recnum = -1
        self._source = None
        self._type = "data"
        self._sha1_latlon = None
        self._update_sha1_latlon()
        self.duration = datetime.timedelta(hours=0)
        self._id = TdlpackID(
            self.is1[8:12].tolist(),
            self,
        )
        self._section_flags = TdlpackFlags(
            "section",
            self,
        )
        self._packing_flags = TdlpackFlags(
            "packing",
            self,
        )
        # For new record, make sure the reference date is present
        if np.all(self.is1[2:8] == 0):
            d = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
            self.is1[2:7] = d.timetuple()[:5]
            self.is1[7] = np.int32(d.strftime(templates.DATE_FORMAT))

    def __repr__(self):
        """"""
        info = ""
        for sect in [0, 1, 2, 4]:
            for k, v in self.attrs_by_section(sect, values=True).items():
                info += f"Section {sect}: {k} = {v}\n"
        return info

    def __str__(self):
        """"""
        ids = self.id.to_string()
        try:
            date = self.refDate.strftime(templates.DATE_FORMAT)
        except ValueError:
            date = "0".zfill(10)
        lead = int(self.leadTime.total_seconds() / 3600.0)
        name = self.name.rstrip()
        return f"{self._recnum}:d={date}:{ids}:{lead:3d}-HR FCST:{name}"

    def _update_sha1_latlon(self):
        try:
            newsha1 = hashlib.sha1(self.is2).hexdigest()
            if newsha1 != self._sha1_latlon:
                self._sha1_latlon = newsha1
        except TypeError:
            pass

    @property
    def parseid(self):
        """Return parsed ID"""
        return utils.parse_id(self.id)

    @property
    def validDate(self):
        """Provide the valid date"""
        return self.refDate + self.leadTime

    def attrs_by_section(self, sect, values=False):
        """
        Provide a tuple of attribute names for the given TDLPACK section.

        Parameters
        ----------
        sect : int
            The TDLPACK section number.

        values : bool, optional
            Optional (default is `False`) arugment to return attributes values.

        Returns
        -------
        list of attribute names or dict if `values = True` where the
        attribute names are keys and values are the attribute values.
        """
        if sect in {0, 1, 4}:
            attrs = templates._section_attrs[sect]
        elif sect == 2 and self.type == "grid":

            def _find_class_index(n):
                _key = {2: "Grid"}
                for i, c in enumerate(self.__class__.__mro__):
                    if _key[n] in c.__name__:
                        return i
                else:
                    return []

            attrs = templates._section_attrs[sect] + self.__class__.__mro__[_find_class_index(sect)]._attrs()
        else:
            attrs = []
        if values:
            return {k: getattr(self, k) for k in attrs}
        else:
            return attrs

    def latlons(self):
        """
        Return a tuple of latitude and longitude arrays.

        This method supports grid and vector (i.e. station) TDLPACK
        records. Some vector TDLPACK files might not contain latitude
        or longitude records. In this scenario, None is returned.

        Returns
        -------
        lats, lons : tuple of arrays
            Tuple of numpy.float32 arrays of latitudes and longitudes.
        """
        pass
        if self._sha1_latlon in _latlon_store.keys():
            return _latlon_store[self._sha1_latlon]

        if self.type == "vector":
            if self._sha1_latlon is None:
                self._sha1_latlon = hashlib.sha1("".join([s for s in self.stations]).encode("ASCII")).hexdigest()
                if {
                    self._linked_station_lat_record,
                    self._linked_station_lon_record,
                } == {-1, -1}:
                    _latlon_store[self._sha1_latlon] = (None, None)
                else:
                    lats = _open_file_store[self._source][self._linked_station_lat_record].data
                    lons = _open_file_store[self._source][self._linked_station_lon_record].data
                    _latlon_store[self._sha1_latlon] = (lats, -1.0 * lons)
            return _latlon_store[self._sha1_latlon]
        elif self.type == "grid":
            iret, lats, lons = tdlpacklib.gridij_to_latlon(
                self.nx,
                self.ny,
                self.mapProjection,
                self.gridLength,
                self.orientationLongitude,
                self.standardLatitude,
                self.latitudeLowerLeft,
                self.longitudeLowerLeft,
            )
            _latlon_store[self._sha1_latlon] = (lats.T, -1.0 * lons.T)
            return _latlon_store[self._sha1_latlon]

    def pack(self):
        """Pack TDLPACK section information and data values"""
        # Make sure TDLPACK sections are well-formed.
        if self.is0[0] == 0:
            self.is0[0] = TDLP_HEADER

        if isinstance(self._data, TdlpackRecordOnDiskArray):
            # No data read yet, so get packed message from file
            self._ipack = _open_file_store[self._source].read(self._recnum)
        elif isinstance(self._data, np.ndarray):
            # Data has been read or set, so check that, or just read the packed message.
            if self._data_modified:
                if self.type == "grid":
                    iret, ioctet, self._ipack = tdlpacklib.pack_2d(
                        self.is0,
                        self.is1,
                        self.is2,
                        self.is4,
                        np.asfortranarray(self.data.T, dtype=np.float32),
                    )
                elif self.type == "vector":
                    iret, ioctet, self._ipack = tdlpacklib.pack_1d(
                        self.is0,
                        self.is1,
                        self.is2,
                        self.is4,
                        np.asfortranarray(self.data, dtype=np.float32),
                    )
            else:
                self._ipack = _open_file_store[self._source].read(self._recnum)

    @property
    def stations(self) -> list:
        """If vector, return stations"""
        return None if self.type == "grid" else _open_file_store[self._source][self._linked_station_id_record].stations

    @property
    def data(self) -> np.array:
        """Accessing the data attribute loads data into memory"""
        if hasattr(self, "_data"):
            if isinstance(self._data, TdlpackRecordOnDiskArray):
                self._ondiskarray = self._data
                self._data = np.asarray(self._data)
            return self._data
        raise ValueError

    @data.setter
    def data(self, data):
        if not isinstance(data, np.ndarray):
            raise ValueError("TdlpackRecord data only supports numpy arrays")
        if self.type == "grid" and len(data.shape) != 2:
            raise ValueError("Data must be 2D array for TDLPACK gridded record")
        elif self.type == "vector" and len(data.shape) != 1:
            raise ValueError("Data must be 1D array for TDLPACK station record")
        self._data = data
        self._data_modified = True

    def flush_data(self):
        """Flush the unpacked data values from the TdlpackRecord object"""
        del self._data
        self._data = self._ondiskarray

    def __getitem__(self, item):
        """"""
        if self.type == "grid":
            if not isinstance(item, tuple):
                item = tuple(item)
        elif self.type == "vector":
            if isinstance(item, str):
                item = tuple([_open_file_store[self._source][self._linked_station_id_record].stations.index(item)])

        try:
            return self.data[item]
        except AttributeError:
            return None

    def __setitem__(self, item):
        """"""
        raise NotImplementedError("Assignment of data not supported via setitem")

    @property
    def lats(self):
        """Return latitudes."""
        return self.latlons()[0]

    @property
    def lons(self):
        """Return longitudes."""
        return self.latlons()[1]

    @property
    def max(self):
        "Return data minimum"
        return np.nanmax(self.data)

    @property
    def min(self):
        "Return data minimum"
        return np.nanmin(self.data)

    @property
    def mean(self):
        """Return mean value of data."""
        return np.nanmean(self.data)

    @property
    def median(self):
        """Return median value of data."""
        return np.nanmedian(self.data)

    @property
    def shape(self):
        """Return shape of data."""
        if self.type == "grid":
            return tuple([int(self.ny), int(self.nx)])
        elif self.type == "vector":
            return tuple([int(self.numberOfPackedValues)])

    @property
    def type(self):
        """Return TDLPACK type."""
        return "grid" if hasattr(self, "nx") else "vector"


@dataclass
class TdlpackRecordOnDiskArray:
    shape: str
    ndim: str
    dtype: str
    filetype: str
    filehandle: open
    rec: TdlpackRecord
    offset: int
    size: int

    def __array__(self, dtype=None):
        return np.asarray(
            _data(self.filehandle, self.filetype, self.rec, self.offset, self.size),
            dtype=dtype,
        )


def _data(filehandle: open, filetype: str, rec: TdlpackRecord, offset: int, size: int) -> np.array:
    """
    Returns an unpacked data grid.

    Returns
    -------
    numpy.ndarray with shape (ny,nx). By default the array dtype is np.float32.
    """

    # Position file pointer to the beginning of the TDLPACK record.
    filehandle.seek(offset)
    if filetype == "sequential":
        ioctet = np.frombuffer(filehandle.read(8), dtype=">i8").astype(np.int64)[0]
    elif filetype == "random-access":
        ioctet = size
    ipack = np.frombuffer(filehandle.read(ioctet), dtype=">i4").astype(np.int32)
    iret, ios0, is1, is2, is2, xdata = tdlpacklib.unpack_data(ipack)
    del ipack

    return xdata.reshape((rec.ny, rec.nx)) if rec.type == "grid" else xdata


@dataclass
class TdlpackStationRecord:
    """
    TDLPACK Station Record class
    """

    stations_in: InitVar[Optional[Iterable[str]]] = None

    type: str = field(init=False, repr=False, default="station")
    stations: ClassVar[templates.Stations] = templates.Stations()

    # Private class variable holding the list
    _stations: Optional[list[str]] = field(init=False, repr=False, default=None)

    def __post_init__(self, stations_in):
        self._nsta_expected = 0
        self._recnum = -1
        self._source = None
        self._stations = None
        self._type = "station"
        self.id = TdlpackID([400001000, 0, 0, 0], self)

        if stations_in is not None:
            self.stations = stations_in

    def __str__(self):
        return f"{self._recnum}:d=0000000000:STATION CALL LETTER RECORD:{self.numberOfStations}"

    @property
    def numberOfStations(self):
        if self._source is not None and (isinstance(self._stations, list) or self._stations is None):
            return self._nsta_expected
        return 0 if self.stations is None else len(self.stations)

    @property
    def data(self):
        pass

    def pack(self):
        pass


@dataclass
class TdlpackTrailerRecord:
    """
    TDLPACK Trailer Record class
    """

    type: str = field(init=False, repr=False, default="trailer")

    def __post_init__(self):
        """"""
        self._recnum = -1
        self._type = "trailer"
        self.id = TdlpackID([0, 0, 0, 0], self)

    def __str__(self):
        """"""
        return f"{self._recnum}:d=0000000000:TRAILER RECORD"

    @property
    def data(self):
        """"""
        pass

    def pack(self):
        """"""
        pass


class TdlpackID:
    """
    TDLPACK variable ID class
    """

    __slots__ = ("_id", "_rec")

    def __init__(self, id, linked_rec=None):
        """
        Initialize TDLPACK variable ID

        Parameters
        ----------
        id : list of ints
            The 4-word TDLPACK variable ID
        linked_rec : TdlpackRecord, optional
            TDLPACK record object. This optional argument provides a mechanism
            for updating the TDLPACK variable ID in the TdlpackRecord is1 array.
        """
        self._id = utils.parse_id(id)
        self._rec = linked_rec

    def __eq__(self, value):
        if isinstance(value, list) or isinstance(value, tuple):
            return self.word1 == value[0] and self.word2 == value[1] and self.word3 == value[2] and self.word4 == value[3]
        else:
            return False

    def __format__(self, spec: str) -> str:
        if not spec:
            spec = "basic"
        return self.format(spec)

    def __repr__(self):
        return repr(utils.unparse_id(self._id))

    @classmethod
    def from_string(cls, idstr):
        """
        Create a TdlpackID object from a TDLPACK ID string.

        Parameters
        ----------
        idstr : str
            String containing the TDLPACK ID with leading zeros and delimited
            by a non-numeric character.

        Returns
        -------
            An instance of TdlpackID.
        """
        delim = idstr[9]
        if {idstr[19], idstr[29]} != {delim, delim}:
            raise ValueError(f"Invalid TDLPACK ID string format")
        return cls([int(i.lstrip("0")) if len(i.lstrip("0")) > 0 else 0 for i in idstr.split(delim)])

    def format(self, style: str = "basic") -> str:
        """
        Format the TDLPACK ID identifier as a string.

        This method returns a string representation of the identifier in one
        of several supported formats commonly used in MOS-2000 workflows.

        Parameters
        ----------
        style : {'basic', 'b', 'mos', 'm', 'parsed', 'p'}, optional
            Output format style (case-insensitive):

            - ``"basic"`` or ``"b"``
                Four-word identifier. Each word is printed as a zero-padded
                integer field.

            - ``"mos"`` or ``"m"``
                MOS-style identifier consisting of the first three words
                followed by the ISG components and the threshold value
                formatted in scientific notation (``.0000e±00``).

            - ``"parsed"`` or ``"p"``
                Identifier parsed into its individual components as defined
                by the internal ID mapping. All components are printed as
                zero-padded integers except the threshold value, which is
                printed as a floating-point value with ``F13.6`` formatting.

        Returns
        -------
        str
            String representation of the identifier in the requested format.

        Notes
        -----
        The MOS-style threshold representation removes the leading zero
        from scientific notation (e.g., ``0.0000e+00`` → ``.0000e+00``)
        to match legacy MOS-2000 formatting conventions.

        Examples
        --------
        Using the ``format`` method:

        >>> rec.format("basic")
        '001000008 000000500 000000000 0000000000'

        >>> rec.format("mos")
        '001000008 000000500 000000000 000 .0000e+00'

        >>> rec.format("parsed")
        '001 000 0 08 0 0000 0500 0 00 0 00 000 0 0 0      0.000000'

        Using Python's format protocol (``__format__``):

        >>> f"{rec.id:basic}"
        '001000008 000000500 000000000 0000000000'

        >>> f"{rec.id:mos}"
        '001000008 000000500 000000000 000 .0000e+00'

        >>> f"{rec.id:parsed}"
        '001 000 0 08 0 0000 0500 0 00 0 00 000 0 0 0      0.000000'
        """
        style = style.lower()

        if style in {"basic", "b"}:
            return f"{str(self.word1).zfill(9)} {str(self.word2).zfill(9)} {str(self.word3).zfill(9)} {str(self.word4).zfill(10)}"
        elif style in {"mos", "m"}:
            thresh = f"{self.thresh:.4e}"
            if thresh.startswith("0"):
                thresh = thresh[1:]
            elif thresh.startswith("-0"):
                thresh = "-" + thresh[2:]
            return f"{str(self.word1).zfill(9)} {str(self.word2).zfill(9)} {str(self.word3).zfill(9)} {self.i}{self.s}{self.g} {thresh}"
        elif style in {"parsed", "p"}:
            parsed = ""
            for k, v in self._id.items():
                if "thresh" not in k:
                    parsed += f"{str(v).zfill(len(k))} "
                else:
                    parsed += f"{v:13.6f}"
            return parsed

        raise ValueError(f"Unknown TdlpackID format style: {style!r}")

    def to_dict(self):
        """
        Return TDLPACK variable ID as dict.

        Returns
        -------
            String of the 4-word TDLPACK variable ID.
        """
        return self._id

    def to_string(self, delim=" "):
        """
        Return TDLPACK variable ID as string.

        Parameters
        ----------
        delim : str, optional
            Delimiter character between each TDLPACK variable ID word.

        Returns
        -------
            String of the 4-word TDLPACK variable ID.
        """
        strlen = (9, 9, 9, 10)
        return delim.join([str(i).zfill(word) for word, i in zip(strlen, utils.unparse_id(self._id))])

    @property
    def word1(self):
        """
        First ID word.

        Returns
        -------
        int
            First parsed ID word.
        """
        return utils.unparse_id(self._id)[0]

    @word1.setter
    def word1(self, value):
        """
        Set first ID word.

        Parameters
        ----------
        value : int
            New value.

        Notes
        -----
        Updates internal ID and ``is1[8]`` if record is attached.
        """
        newid = utils.unparse_id(self._id)
        newid[0] = value
        self._id = utils.parse_id(newid)
        if self._rec is not None:
            self._rec.is1[8] = newid[0]

    @property
    def word2(self):
        """
        Second ID word.

        Returns
        -------
        int
            Second parsed ID word.
        """
        return utils.unparse_id(self._id)[1]

    @word2.setter
    def word2(self, value):
        """
        Set second ID word.

        Parameters
        ----------
        value : int
            New value.

        Notes
        -----
        Updates internal ID and ``is1[9]`` if record is attached.
        """
        newid = utils.unparse_id(self._id)
        newid[1] = value
        self._id = utils.parse_id(newid)
        if self._rec is not None:
            self._rec.is1[9] = newid[1]

    @property
    def word3(self):
        """
        Third ID word.

        Returns
        -------
        int
            Third parsed ID word.
        """
        return utils.unparse_id(self._id)[2]

    @word3.setter
    def word3(self, value):
        """
        Set third ID word.

        Parameters
        ----------
        value : int
            New value.

        Notes
        -----
        Updates internal ID and ``is1[10]`` if record is attached.
        """
        newid = utils.unparse_id(self._id)
        newid[2] = value
        self._id = utils.parse_id(newid)
        if self._rec is not None:
            self._rec.is1[10] = newid[2]

    @property
    def word4(self):
        """
        Fourth ID word.

        Returns
        -------
        int
            Fourth parsed ID word.
        """
        return utils.unparse_id(self._id)[3]

    @word4.setter
    def word4(self, value):
        """
        Set fourth ID word.

        Parameters
        ----------
        value : int
            New value.

        Notes
        -----
        Updates internal ID and ``is1[11]`` if record is attached.
        """
        newid = utils.unparse_id(self._id)
        newid[3] = value
        self._id = utils.parse_id(newid)
        if self._rec is not None:
            self._rec.is1[11] = newid[3]

    @property
    def ccc(self):
        """
        CCC identifier component.

        Returns
        -------
        int
        """
        return self._id["ccc"]

    @ccc.setter
    def ccc(self, value):
        """
        Set CCC identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[8]`` if record is attached.
        """
        self._id["ccc"] = value
        if self._rec is not None:
            self._rec.is1[8] = utils.unparse_id(self._id)[0]

    @property
    def fff(self):
        """
        FFF identifier component.

        Returns
        -------
        int
        """
        return self._id["fff"]

    @fff.setter
    def fff(self, value):
        """
        Set FFF identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[8]`` if record is attached.
        """
        self._id["fff"] = value
        if self._rec is not None:
            self._rec.is1[8] = utils.unparse_id(self._id)[0]

    @property
    def cccfff(self):
        """
        Combined CCCFFF identifier.

        Returns
        -------
        int
            Integer representation of ``word1 / 1000``.
        """
        return int(self.word1 / 1000)

    @property
    def b(self):
        """
        B identifier component.

        Returns
        -------
        int
        """
        return self._id["b"]

    @b.setter
    def b(self, value):
        """
        Set B identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[8]`` if record is attached.
        """
        self._id["b"] = value
        if self._rec is not None:
            self._rec.is1[8] = utils.unparse_id(self._id)[0]

    @property
    def dd(self):
        """
        DD identifier component.

        Returns
        -------
        int
        """
        return self._id["dd"]

    @dd.setter
    def dd(self, value):
        """
        Set DD identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[8]`` and ``is1[14]`` if record is attached.
        """
        self._id["dd"] = value
        if self._rec is not None:
            self._rec.is1[8] = utils.unparse_id(self._id)[0]
            self._rec.is1[14] = value

    @property
    def v(self):
        """
        V identifier component.

        Returns
        -------
        int
        """
        return self._id["v"]

    @v.setter
    def v(self, value):
        """
        Set V identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[9]`` if record is attached.
        """
        self._id["v"] = value
        if self._rec is not None:
            self._rec.is1[9] = utils.unparse_id(self._id)[1]

    @property
    def llll(self):
        """
        LLLL identifier component.

        Returns
        -------
        int
        """
        return self._id["llll"]

    @llll.setter
    def llll(self, value):
        """
        Set LLLL identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[9]`` if record is attached.
        """
        self._id["llll"] = value
        if self._rec is not None:
            self._rec.is1[9] = utils.unparse_id(self._id)[1]

    @property
    def uuuu(self):
        """
        UUUU identifier component.

        Returns
        -------
        int
        """
        return self._id["uuuu"]

    @uuuu.setter
    def uuuu(self, value):
        """
        Set UUUU identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[9]`` if record is attached.
        """
        self._id["uuuu"] = value
        if self._rec is not None:
            self._rec.is1[9] = utils.unparse_id(self._id)[1]

    @property
    def t(self):
        """
        T identifier component.

        Returns
        -------
        int
        """
        return self._id["t"]

    @t.setter
    def t(self, value):
        """
        Set T identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[10]`` if record is attached.
        """
        self._id["t"] = value
        if self._rec is not None:
            self._rec.is1[10] = utils.unparse_id(self._id)[2]

    @property
    def rr(self):
        """
        RR identifier component.

        Returns
        -------
        int
        """
        return self._id["rr"]

    @rr.setter
    def rr(self, value):
        """
        Set RR identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[10]`` if record is attached.
        """
        self._id["rr"] = value
        if self._rec is not None:
            self._rec.is1[10] = utils.unparse_id(self._id)[2]

    @property
    def o(self):
        """
        O identifier component.

        Returns
        -------
        int
        """
        return self._id["o"]

    @o.setter
    def o(self, value):
        """
        Set O identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[10]`` if record is attached.
        """
        self._id["o"] = value
        if self._rec is not None:
            self._rec.is1[10] = utils.unparse_id(self._id)[2]

    @property
    def hh(self):
        """
        HH identifier component.

        Returns
        -------
        int
        """
        return self._id["hh"]

    @hh.setter
    def hh(self, value):
        """
        Set HH identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[10]`` if record is attached.
        """
        self._id["hh"] = value
        if self._rec is not None:
            self._rec.is1[10] = utils.unparse_id(self._id)[2]

    @property
    def tau(self):
        """
        Forecast hour (tau).

        Returns
        -------
        int
        """
        return self._id["tau"]

    @tau.setter
    def tau(self, value):
        """
        Set forecast hour (tau).

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[10]`` and ``is1[12]`` if record is attached.
        """
        self._id["tau"] = value
        if self._rec is not None:
            self._rec.is1[10] = utils.unparse_id(self._id)[2]
            self._rec.is1[12] = value

    @property
    def thresh(self):
        """
        Threshold identifier component.

        Returns
        -------
        int
        """
        return self._id["thresh"]

    @thresh.setter
    def thresh(self, value):
        """
        Set threshold identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[11]`` if record is attached.
        """
        self._id["thresh"] = value
        if self._rec is not None:
            self._rec.is1[11] = utils.unparse_id(self._id)[3]

    @property
    def i(self):
        """
        I identifier component.

        Returns
        -------
        int
        """
        return self._id["i"]

    @i.setter
    def i(self, value):
        """
        Set I identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[11]`` if record is attached.
        """
        self._id["i"] = value
        if self._rec is not None:
            self._rec.is1[11] = utils.unparse_id(self._id)[3]

    @property
    def s(self):
        """
        S identifier component.

        Returns
        -------
        int
        """
        return self._id["s"]

    @s.setter
    def s(self, value):
        """
        Set S identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[11]`` if record is attached.
        """
        self._id["s"] = value
        if self._rec is not None:
            self._rec.is1[11] = utils.unparse_id(self._id)[3]

    @property
    def g(self):
        """
        G identifier component.

        Returns
        -------
        int
        """
        return self._id["g"]

    @g.setter
    def g(self, value):
        """
        Set G identifier component.

        Parameters
        ----------
        value : int

        Notes
        -----
        Updates ``is1[11]`` if record is attached.
        """
        self._id["g"] = value
        if self._rec is not None:
            self._rec.is1[11] = utils.unparse_id(self._id)[3]


class TdlpackFlags:
    """
    TDLPACK Flags class

    This class can be used to handle bit flags for the section flags in is1[1] or
    the packing flags is4[1].
    """

    __slots__ = (
        "_arr_item",
        "_arr_item_idx",
        "_flags",
        "_rec",
        "_type",
    )

    _immutable_flags = (
        "hasBitMapSection",
        "isVectorData",
        "packing",
        "packingOptions",
    )

    _idx = 1

    _section_flags_mapping = {
        "hasBitMapSection": 6,
        "hasGridDefinitionSection": 7,
    }

    _packing_flags_mapping = {
        "isVectorData": 3,  # 0 = False (i.e. gridpoint); 1 = True
        "packing": 4,  # 0 = Simple Packing; 1 = Complex packing
        "packingOptions": 5,  # 0 = Original scaled data; 1 = 2nd order spatial differences
        "hasPrimaryMissingValue": 6,  # 0 = No primary missing value; primary missing value may be present
        "hasSecondaryMissingValue": 7,  # 0 = No primary missing value; primary missing value may be present
    }

    def __init__(
        self,
        flag_type: Literal["section", "packing"],
        linked_rec: "TdlpackRecord",
    ):
        """
        Initialize a TdlpackFlags instance.

        Parameters
        ----------
        flag_type : {"section", "packing"}
            Specifies which set of flags this instance manages. Determines
            both the internal flag mapping and the underlying array in
            ``linked_rec`` that will be accessed and modified.
        linked_rec : TdlpackRecord
            The parent record containing the underlying data arrays. Flag
            updates performed through this instance are applied directly to
            the corresponding ``is1`` or ``is4`` array of this object.

        Notes
        -----
        - ``flag_type="section"`` maps to ``linked_rec.is1``.
        - ``flag_type="packing"`` maps to ``linked_rec.is4``.
        """
        self._rec = linked_rec
        self._type = flag_type
        if flag_type == "section":
            self._flags = self._section_flags_mapping
            self._arr_item = self._rec.is1
        elif flag_type == "packing":
            self._flags = self._packing_flags_mapping
            self._arr_item = self._rec.is4

    def __repr__(self):
        return self.to_dict().__repr__()

    def __getitem__(self, key):
        arr_item = [int(i) for i in f"{self._arr_item[self._idx]:08b}"]
        return arr_item[self._flags[key]]

    def __setitem__(self, key, value):
        if value not in {0, 1}:
            raise ValueError(f"flag values can only be 0 or 1")
        if key in self._immutable_flags:
            raise TypeError(f"flag '{key}' is immutable and cannot be modified")
        s = self.to_list()
        s[self._flags[key]] = value
        self._arr_item[self._idx] = int("".join([str(i) for i in s]), 2)

    def to_dict(self):
        """Return flags as a dictionary"""
        return {key: self[key] for key in self._flags.keys()}

    def to_list(self):
        """Return flags as a list"""
        return [int(i) for i in self.to_string()]

    def to_string(self):
        """Return flags as a string"""
        return f"{self._arr_item[self._idx]:08b}"
