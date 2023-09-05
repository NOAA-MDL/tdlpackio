"""
Introduction
============

tdlpackio is a Python package for reading and writing TDLPACK files by providing an interface
to the MOS-2000 (MOS2K) software system that is written in Fortran.  Contained in tdlpackio is
tdlpacklib which contains the necessary MOS2K subroutines to read and write TDLPACK sequential
or random-access files and to properly decode from the TDLPACK format and to encode data into
the TDLPACK format.

TDLPACK is a GRIB-like binary data format that is exclusive to MOS2K Fortran-based sofftware
system.  This software system was developed at the Meteorological Development Laboratory (MDL)
within NOAA/NWS and its primary purpose is to perform statistical post-processing of meteorological data.
TDLPACK format is based on the World Meteorological Organizations (WMO) GRIdded Binary (GRIB)
code, but has been tailored to MDL needs for data -- mainly the ability to store 1D (vector),
datasets such as station observations, along with 2D grids.

The TDLPACK data format are contained in two types of Fortran-based files; sequential or random-access.
Sequential files are variable length, record-based, and unformatted. Random-access files are fixed-length
and direct-access.  tdlpackio accommodates reading and writing of both types of TDLPACK files.

TDLPACK files can contain two other types of records: a station call letter record and trailer record.
A station call letter record can exist in both types of TDLPACK files and contains a stream of
alphanumeric characters (`CHARACTER(LEN=8)`).  A trailer record exists to signal the MOS2K system that
another station call letter record is about to be read or we have reached the end of the file (EOF).
A trailer record is not written to a random-access file.

For more information on the MOS-2000 software system and TDLPACK foremat, user is
referred to the official [MOS-2000 documentation](https://www.weather.gov/media/mdl/TDL_OfficeNote00-1.pdf).

In order for tdlpackio to read/write TDLPACK files, we need to compile the necessary MOS2K
Fortran source code into a shared object library.  This is handled by the setup process as the
Fortran source is compiled with f2py (included with Numpy).  The following are some important
items to note regarding MOS2K source files included:

- Several Fortran 90+ source files have been created to better interface to MOS2K Fortran 77 code.
- The only modification made to MOS2K source files is changing the filename variable, `CFILX` from
`CHARACTER*60` to `CHARACTER*1024` in the appropropriate subroutines where random-access file IO
occurs.

Download
========

- Latest code from [github repository](https://github.com/eengl/tdlpackio).
- Latest [releases](https://github.com/eengl/tdlpackio/releases) on GitHub.
- [PyPI](https://pypi.org/project/tdlpackio)

Requires
========

- Python 3.8+
- [numpy array module](http://numpy.scipy.org), version 1.22 or later.
- [setuptools](https://pypi.python.org/pypi/setuptools), version 34.0 or later.
- Fortran compiler: GNU (gfortran) and Intel (ifort) have been tested.

Install
=======

```shell
pip install tdlpackio
```

**Build and Install from Source**

```shell
pip install .
```

To build with Intel compilers, perform the following:

```shell
pip install . --config-settings="--build-option=build --fcompiler=intelem"
```

Tutorial
========

1. [Creating/Opening/Closing a TDLPACK file.](#section1)
2. [Reading a TDLPACK file.](#section2)
3. [TdlpackRecord Object.](#section3)
4. [Creating a TdlpackRecord Object.](#section4)
5. [Creating a TDLPACK Station Record.](#section5)
6. [Creating a TDLPACK Record.](#section6)
7. [Packing/Unpacking a TDLPACK Record.](#section7)

## <div id='section1'>1) Creating/Opening/Closing a TDLPACK file.

To create a TDLPACK file from Python, you call the `tdlpackio.open` function and provide the
file name, and if writing, `mode='w' or 'a'`.  For `mode='a'`, this will append to an existing
file.  When creating a new file, the default file format is `'sequential'`, but the user can
also specify the format with `format='sequential' or 'random-access'`.  If the new file is
random-access, then the user can also specify `ra_template='small' or 'large'`.  The default
is 'small' and 'large' is recommended for a high-resolution grids (i.e. ~ > 2M total points).

Example: Create a new sequential file:

```python
>>> import tdlpackio
>>> f = tdlpackio.open('test.sq',mode='w')
```

Example: Create a new random-access file:

```python
>>> import tdlpackio
>>> f = tdlpackio.open('test.sq',mode='w',format='random-access',ra_template='small')
```

To open an existing TDLPACK file, provide the filename since the default mode is read.
Throughout this tutorial, we will use the file, "gfspkd47.2017020100.sq".

```python
import tdlpackio
>>> f = tdlpackio.open("./sampledata/gfspkd47.2017020100.sq")
>>> type(f)
<class 'tdlpackio._tdlpackio.open'>
>>> f
mode = rb
name = /home/ericengle/Projects/GitHub/tdlpackio/sampledata/gfspkd47.2017020100.sq
records = 100
filetype = sequential
size = 3363792
>>> f.close()
```

## <div id='section2'>2) Reading a TDLPACK file.

When tdlpackio opens a TDLPACK files, the entire contents of the file are indexed.
It is important to note that reading TDLPACK files is done natively in Python, including
reading random-access files.  This allows tdlpackio to control how much data is read
from disk for the purposes of indexing TDLPACK metadata.  Since records in the file have
already been inventoried, records can we read in a random access-like manner.

You can access records bye using index notation on the file object.

```python
>>> rec = f[0]
>>> print(rec)
0:d=2017020100:001000008 000001000 000000000 0000000000:  0-HR FCST:1000 MB HGT GFS
>>> recs = f[:10]
>>> for rec in recs: print(rec)
...
0:d=2017020100:001000008 000001000 000000000 0000000000:  0-HR FCST:1000 MB HGT GFS
1:d=2017020100:001000008 000000975 000000000 0000000000:  0-HR FCST: 975 MB HGT GFS
2:d=2017020100:001000008 000000950 000000000 0000000000:  0-HR FCST: 950 MB HGT GFS
3:d=2017020100:001000008 000000925 000000000 0000000000:  0-HR FCST: 925 MB HGT GFS
4:d=2017020100:001000008 000000900 000000000 0000000000:  0-HR FCST: 900 MB HGT GFS
5:d=2017020100:001000008 000000850 000000000 0000000000:  0-HR FCST: 850 MB HGT GFS
6:d=2017020100:001000008 000000800 000000000 0000000000:  0-HR FCST: 800 MB HGT GFS
7:d=2017020100:001000008 000000750 000000000 0000000000:  0-HR FCST: 750 MB HGT GFS
8:d=2017020100:001000008 000000700 000000000 0000000000:  0-HR FCST: 700 MB HGT GFS
9:d=2017020100:001000008 000000600 000000000 0000000000:  0-HR FCST: 600 MB HGT GFS
```

## <div id='section3'>3) TdlpackRecord Object.

All TDLPACK records are represented in tdlpackio as class TdlpackRecord.  This class
accommdates both gridded and vector (i.e. station) records.  The TdlpackRecord class
only stores the TDLPACK metadata sections which are integer based and a few other
pieces of of data.  The TDLPACK metadata attributes are descriptor classes that
contain custom __get__() and __set__() methods for each metadata attribute that map
to a certain integer value in the TDLPACK sections.  The packed data are not read from
disk until data are requested by referencing the `data` attribute.  This is commonly
referred to as "lazy reading".

```python
>>> rec = f[0]
>>> rec.is0
array([1347175508,      21661,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0,          0,
                0,          0,          0,          0], dtype=int32)
>>> rec.is1
array([        71,          1,       2017,          2,          1,
                0,          0, 2017020100,    1000008,       1000,
                0,          0,          0,          0,          8,
                1,          0,          0,          0,          0,
                0,         32,         49,         48,         48,
               48,         32,         77,         66,         32,
               72,         71,         84,         32,         71,
               70,         83,         32,         32,         32,
               32,         32,         32,         32,         32,
               32,         32,         32,         32,         32,
               32,         32,         32,         32], dtype=int32)
>>> rec.is2
array([      28,        5,      297,      169,    28320,  1500000,
        1050000, 47625000,   600000,        0,        0,        0,
              0,        0,        0,        0,        0,        0,
              0,        0,        0,        0,        0,        0,
              0,        0,        0,        0,        0,        0,
              0,        0,        0,        0,        0,        0,
              0,        0,        0,        0,        0,        0,
              0,        0,        0,        0,        0,        0,
              0,        0,        0,        0,        0,        0],
      dtype=int32)
>>> rec.is4
array([21550,    12, 50193,     0,     0,     0,     0,     0,     0,
           0,     0,     0,     0,     0,     0,     0,     0,     0,
           0,     0,     0,     0,     0,     0,     0,     0,     0,
           0,     0,     0,     0,     0,     0,     0,     0,     0,
           0,     0,     0,     0,     0,     0,     0,     0,     0,
           0,     0,     0,     0,     0,     0,     0,     0,     0],
      dtype=int32)
>>> rec
Section 0: edition = 0
Section 1: sectionFlags = 00000001
Section 1: year = 2017
Section 1: month = 2
Section 1: day = 1
Section 1: hour = 0
Section 1: minute = 0
Section 1: refDate = 2017-02-01 00:00:00
Section 1: id1 = 1000008
Section 1: id2 = 1000
Section 1: id3 = 0
Section 1: id4 = 0
Section 1: id = [1000008    1000       0       0]
Section 1: leadTime = 0:00:00
Section 1: leadTimeMinutes = 0
Section 1: decScaleFactor = 0
Section 1: binScaleFactor = 0
Section 1: name = 1000 MB HGT GFS
Section 1: type = grid
Section 1: validDate = 2017-02-01 00:00:00
Section 2: mapProjection = 5
Section 2: nx = 297
Section 2: ny = 169
Section 2: latitudeLowerLeft = 2.8320000000000003
Section 2: longitudeLowerLeft = 150.0
Section 2: orientationLongitude = 105.0
Section 2: gridLength = 47625.0
Section 2: standardLatitude = 60.0
Section 4: packingFlags = 00001100
Section 4: numberOfPackedValues = 50193
Section 4: primaryMissingValue = 0
Section 4: secondaryMissingValue = 0
Section 4: overallMinValue = 0
Section 4: numberOfGroups = 0
```

Unpacking the data:

```python
>>> rec.data
array([[ 88.,  88.,  88., ..., 107., 101.,  97.],
       [ 87.,  88.,  88., ..., 118., 114., 104.],
       [ 87.,  87.,  87., ..., 120., 120., 116.],
       ...,
       [136., 135., 135., ..., 170., 174., 177.],
       [136., 136., 135., ..., 170., 173., 176.],
       [136., 136., 135., ..., 169., 172., 175.]], dtype=float32)
```

Use the `latlons()` method to get latitude and longitude values for gridded records.

```python
>>> rec.latlons()
(array([[ 2.8320062,  3.002308 ,  3.1725748, ...,  9.856886 ,  9.695385 ,
         9.53346  ],
       [ 3.0023057,  3.1735988,  3.3448648, ..., 10.0720415,  9.909414 ,
         9.746364 ],
       [ 3.172573 ,  3.344863 ,  3.5171287, ..., 10.287412 , 10.12365  ,
         9.959467 ],
       ...,
       [22.115602 , 22.432093 , 22.749762 , ..., 36.43131  , 36.066128 ,
        35.70211  ],
       [22.118425 , 22.43495  , 22.752638 , ..., 36.43567  , 36.07043  ,
        35.706383 ],
       [22.119368 , 22.435898 , 22.7536   , ..., 36.437122 , 36.07187  ,
        35.7078   ]], dtype=float32), array([[-150.00027 , -149.82924 , -149.6572  , ...,  -68.13083 ,
         -67.91318 ,  -67.69678 ],
       [-150.1713  , -150.00027 , -149.82822 , ...,  -67.96649 ,
         -67.748505,  -67.53174 ],
       [-150.34335 , -150.17233 , -150.00027 , ...,  -67.8009  ,
         -67.58258 ,  -67.36548 ],
       ...,
       [-194.31772 , -194.31343 , -194.30917 , ...,  -15.910004,
         -15.902863,  -15.895691],
       [-194.65808 , -194.6575  , -194.65466 , ...,  -15.455414,
         -15.451965,  -15.447632],
       [-195.00015 , -195.00015 , -195.00015 , ...,  -15.      ,
         -15.      ,  -15.      ]], dtype=float32))
```

## <div id='section4'>4) Creating a TDLPACK Station Record.

The constructor for `pytdlpack.TdlpackStationRecord` provides two methods of
instantiation via the traditional **kwargs (see `pytdlpack.TdlpackStationRecord.__init__`)
or simply providing `ccall = ...` ***(recommended)***.  The value passed to the `ccall=` argument can
be a single call letter string, list, tuple, or comma-delimited string of station call letter records.

```python
>>> import pytdlpack
>>> stations = pytdlpack.TdlpackStationRecord(['KBWI','KDCA','KIAD'])
>>> stations
ccall = ['KBWI', 'KDCA', 'KIAD']
id = [400001000         0         0         0]
ioctet = 0
ipack = []
number_of_stations = 3
```

## <div id='section5'>5) Creating a TDLPACK Record.

The recommended method for creating a `pytdlpack.TdlpackRecord` is to pass the TDLPACK
indentification arrays, plain language string, and data to the approproiate keyword.  Please
see `pytdlpack.TdlpackRecord.__init__` for more info.

```python
>>> import numpy as np
>>> record = pytdlpack.TdlpackRecord(date=2019070100,id=[4210008, 0, 24, 0],lead=24,
plain="GFS WIND SPEED",grid=grid_def,data=<np.float32 array>)
```

The user is encouraged to read the official MOS-2000 documentation (specifically Chapter 5)
on construction of these arrays and proper encoding.

## <div id='section6'>6) Packing/Unpacking a TDLPACK Record.

Once any of the three classes of TDLPACK records have been instantiated, you can pack the
record using the class method `pack`.  Using the example from [Section 5](#section5), `record`
is now an instance of `pytdlpack.TdlpackRecord`.  You can pack this record with the following:

```python
>>> record.pack()
```

To unpack a packed TDLPACK record, perform:

```python
>>> record.unpack()
```

The `pytdlpack.TdlpackRecord.unpack` class method for TDLPACK data records, contains optional
arguments `data=` (to control the unpacking of data) and `missing_value=` (to set a different
missing value other than what is contained in the record).  For TDLPACK data records,
`pytdlpack.TdlpackRecord.unpack` automatically unpacks the TDLPACK meta-data.

```python
>>> record.unpack(data=True,missing_value=-9999.0)
```

"""
"""
TdlpackIO is a pure Python implementation for performing IO with TDLPACK sequential files
(i.e. Fortran unformatted files).  Instead of using Fortran for perform IO, we are using
Python builtins.open() in binary mode.  This allows us to perform stream-based IO for TDLPACK
files.  When a file is opened for reading, its contents (TDLPACK records) are automatically
indexed and stored in a dictionary.  The dictionary stores the byte offset the data record;
the size of the data record; date and lead time; and MOS-2000 ID.

This indexing allow the user to access a TDLPACK sequential file in a random-access nature.
For example if a users wants to read the 500th record in the file, the first 499 records in
their entirety do not need to be read.
"""

from dataclasses import dataclass, field
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

FORTRAN_STDOUT_LUN = 12

TDLP_HEADER = 1413762128 # "TDLP" converted to int

L3264B = int(tdlpacklib.tdlpacklib_mod.l3264b)
L3264W = int(tdlpacklib.tdlpacklib_mod.l3264w)
NBYPWD = int(tdlpacklib.tdlpacklib_mod.nbypwd)

MINPK = 21
NCHAR = 8
ND5 = 5242880 # Accommodates a 20MB record
ND7 = 54
ONE_MB = 1048576
PMISS = 9999.
SMISS = 9997.

_latlon_store = dict()
_open_file_store = dict()
_record_class_store = dict()

tdlpacklib.openlog(FORTRAN_STDOUT_LUN,path=os.devnull)

class open:
    """
    Open class for tdlpackio.
    """
    def __init__(self, path, mode='r', format=None, ra_template=None):
        """
        Class Constructor

        Parameters
        ----------

        **`path : str`**

        File name.

        **`mode : str, optional, default = 'r'`**

        File handle mode.  The default is open for reading ('r').

        **`format : str, optional, default = 'sequential'`**

        File type when creating a new file.  Valid values are
        'sequential` (DEFAULT) or 'random-access'.
        """
        if mode == 'r' or mode == 'w': mode = mode+'b'
        if mode == 'a': mode = 'wb'
        self._byteorder = 0
        self._hasindex = False
        self._index = {}
        self.mode = mode
        self.name = os.path.abspath(path)
        self.records = 0

        # Perform indexing on read
        if 'r' in self.mode:
            self._filehandle = builtins.open(path,mode=mode,buffering=ONE_MB)
            self.filetype = self._get_tdlpack_file_type()
            self._build_index()
        elif 'w' in self.mode:
            self.bytes_written = 0
            self.records_written = 0
            self.filetype = format if format is not None else 'sequential'
            if self.filetype == 'random-access':
                ifiletype = 1
                ra_template = 'small' if ra_template is None else ra_template
                self._lun,self._byteorder,ifiletype,ier = \
                tdlpacklib.openfile(FORTRAN_STDOUT_LUN,self.name,self.mode,self._byteorder,ifiletype,ra_template=ra_template)
            elif self.filetype == 'sequential':
                self._filehandle = builtins.open(path,mode=mode,buffering=ONE_MB)
                ifiletype = 2
                self._lun,self._byteorder,ifiletype,ier = \
                tdlpacklib.openfile(FORTRAN_STDOUT_LUN,self.name,self.mode,self._byteorder,ifiletype)

        # Get file size
        try:
            self.size = os.path.getsize(self.name)
        except(FileNotFoundError):
            self.size = 0
        # Add self to file data store
        _open_file_store[self.name] = self

    def __enter__(self):
        """
        """
        return self

    def __exit__(self, atype ,value, traceback):
        """
        """
        self.close()

    def __iter__(self):
        """
        """
        yield from self._index['record']

    def __repr__(self):
        """
        """
        strings = []
        keys = self.__dict__.keys()
        for k in keys:
            if not k.startswith('_'):
                strings.append('%s = %s\n'%(k,self.__dict__[k]))
        return ''.join(strings)

    def __getitem__(self,key):
        """
        """
        if isinstance(key,slice):
            return self._index['record'][key]
        elif isinstance(key,int):
            return self._index['record'][key]
        else:
            raise KeyError('Key must be an integer record number or a slice')

    def _get_tdlpack_file_type(self):
        """
        Determine the type of TDLPACK file.
        """
        self._filehandle.seek(0)
        a = struct.unpack('>i',self._filehandle.read(4))[0]
        b = struct.unpack('>i',self._filehandle.read(4))[0]
        self._filehandle.seek(0)
        return 'random-access' if [a,b] == [0,4] else 'sequential'

    def _build_index(self):
        """
        Record Indexer
        """
        # Initialize index dictionary
        self._index['offset'] = []
        self._index['size'] = []
        self._index['type'] = []
        self._index['record'] = []

        if self.filetype == 'sequential': self._sequential_file_indexer()
        if self.filetype == 'random-access': self._randomaccess_file_indexer()
        self._hasindex = True

    def _randomaccess_file_indexer(self):
        """
        Indexer for random-access TDLPACK files.
        """
        # Read master key
        version, nids, nwords, nkyrec, maxent, lastky = struct.unpack('>iiiiii',self._filehandle.read(24))
        nbytes = nwords*NBYPWD
        self.master_key = dict(version=version,nids=nids,nwords=nwords,
                               nkyrec=nkyrec,maxent=maxent,lastky=lastky)
        # Set file position to first key record
        self._filehandle.seek(nbytes)

        last_station = -1

        # Iterate over all key records
        while True:

            # Read key record "header" data
            nkeys, nprec_this_key, prec_next_key = struct.unpack('>iii',self._filehandle.read(12))

            ids = list()
            nsize = list()
            prec_begin = list()

            # Read key record information
            for i in range(nkeys):
                id1,id2,id3,id4,nd,bprec = struct.unpack('>iiiiii',self._filehandle.read(24))
                ids.append([id1,id2,id3,id4])
                nsize.append(nd)
                prec_begin.append(bprec)

            # Using key record info, move around file to inventory TDLPACK data
            for (m,n,b) in zip(ids,nsize,prec_begin):

                # Disect prec_begin
                prec1 = int(b/1000.0)
                nprec = int(b-(prec1*1000.0))

                # Offset to the data record
                offset = (prec1-1)*nbytes
                self._filehandle.seek(offset)
                self._index['offset'].append(offset)
                self._index['size'].append(n*NBYPWD)

                # Determine record type.  Since the 4-word ID is stored in the
                # key record, we can use it to determine station call letter
                # record or TDLPACK data record.
                if m[0] == 400001000:
                    # Station ID record...not in TDLPACK format
                    rec = TdlpackStationRecord()
                    last_station = self.records
                    rec._recnum = self.records
                    rec._source = self.name
                    rec.numberOfStations = int(n/2)
                    self._index['record'].append(rec)
                    self._index['type'].append('station')
                else:
                    # TDLPACK data record
                    ipack = np.frombuffer(self._filehandle.read(132),dtype='>i4')
                    is0, is1, is2, is4, ier = tdlpacklib.unpack_meta_wrapper(ipack,ND7)
                    if np.all(is2==0): is2 = None
                    rec = TdlpackRecord(is0,is1,is2,is4)
                    rec._recnum = self.records
                    rec._linked_station_record = last_station
                    rec._source = self.name
                    shape = (rec.ny,rec.nx) if rec.type == 'grid' else (rec.numberOfPackedValues,)
                    ndim = len(shape)
                    dtype = 'float32'
                    rec._data = TdlpackRecordOnDiskArray(shape,ndim,dtype,self.filetype,
                                                         self._filehandle,rec,
                                                         self._index['offset'][-1],
                                                         self._index['size'][-1])
                    self._index['record'].append(rec)
                    self._index['type'].append('data')
                self.records += 1

            # Hold the record number of the last station ID record
            if self._index['type'][-1] == 'station':
                _last_station_id_record = self.records # This should be OK.

            # Break loop here, at last key record
            if prec_next_key == 99999999: break
            offset = (prec_next_key-1)*nbytes
            self._filehandle.seek(offset)

    def _sequential_file_indexer(self):
        """
        Indexer for sequential TDLPACK files.
        """
        last_station = -1
        # Iterate
        while True:
            try:
                # First read 4-byte Fortran record header
                pos = self._filehandle.tell()
                fortran_header = struct.unpack('>i',self._filehandle.read(4))[0]
                if fortran_header >= 132:
                    bytes_to_read = 132
                else:
                    bytes_to_read = fortran_header

                pos = self._filehandle.tell()
                ioctet = np.frombuffer(self._filehandle.read(8),dtype='>i8')[0]
                ipack = np.frombuffer(self._filehandle.read(bytes_to_read-8),dtype='>i4')
                _header = struct.unpack('>4s',ipack[0])[0].decode()

                # Check to first 4 bytes of the data record to determine the data
                # record type.
                if _header == 'PLDT':
                    # TDLPACK data record
                    is0, is1, is2, is4, ier = tdlpacklib.unpack_meta_wrapper(ipack,ND7)
                    self._index['offset'].append(pos)
                    self._index['size'].append(fortran_header) # Size given by Fortran header
                    if np.all(is2==0): is2 = None
                    rec = TdlpackRecord(is0,is1,is2,is4)
                    rec._recnum = self.records
                    rec._linked_station_record = last_station
                    rec._source = self.name
                    shape = (rec.ny,rec.nx) if rec.type == 'grid' else (rec.numberOfPackedValues,)
                    ndim = len(shape)
                    dtype = 'float32'
                    rec._data = TdlpackRecordOnDiskArray(shape,ndim,dtype,self.filetype,
                                                         self._filehandle,rec,
                                                         self._index['offset'][-1],
                                                         self._index['size'][-1])
                    self._index['record'].append(rec)
                    self._index['type'].append('data')
                else:
                    if ioctet == 24 and ipack[4] == 9999:
                        # Trailer record
                        rec = TdlpackTrailerRecord()
                        rec._recnum = self.records
                        rec._source = self.name
                        self._index['offset'].append(pos)
                        self._index['size'].append(fortran_header)
                        self._index['type'].append('trailer')
                        self._index['record'].append(rec)
                    else:
                        # Station ID record
                        rec = TdlpackStationRecord()
                        last_station = self.records
                        rec._recnum = self.records
                        rec._source = self.name
                        rec.numberOfStations = int(ioctet/8)
                        self._index['offset'].append(pos)
                        self._index['size'].append(fortran_header)
                        self._index['type'].append('station')
                        self._index['record'].append(rec)

                # At this point we have successfully identified a TDLPACK record from
                # the file. Increment self.records and position the file pointer to
                # now read the Fortran trailer.
                self.records += 1 # Includes trailer records
                self._filehandle.seek(fortran_header-bytes_to_read,1)
                fortran_trailer = struct.unpack('>i',self._filehandle.read(4))[0]

                # Check Fortran header and trailer for the record.
                if fortran_header != fortran_trailer:
                    raise IOError('Bad Fortran record.')

                # Hold the record number of the last station ID record
                if self._index['type'][-1] == 'station':
                    _last_station_id_record = self.records # This should be OK.

            except(struct.error):
                self._filehandle.seek(0)
                break

    def read(self, n):
        """
        """
        if 'w' in self.mode: pass # Remove this at some point....
        # Position file pointer to the beginning of the TDLPACK record.
        self._filehandle.seek(self._index['offset'][n])
        if self.filetype == 'sequential':
            size = np.frombuffer(self._filehandle.read(8),dtype='>i8')[0]
        elif self.filetype == 'random-access':
            size = self._index['size'][n]

        if self._index['type'][n] in ['data','trailer']:
            return np.frombuffer(self._filehandle.read(size),dtype='>i4')
        elif self._index['type'][n] == 'station':
            return np.frombuffer(self._filehandle.read(size),dtype='S8')

    def write(self, record):
        """
        """
        if isinstance(record,list):
            for rec in record:
                self.write(rec)
            return

        if self.filetype == 'random-access':
            if not hasattr(record,'_ipack'): record.pack()
            nreplace, ncheck = 0, 0
            if isinstance(record,TdlpackStationRecord):
                ipack = np.ndarray((record.numberOfStations*2),dtype='S4')
                for n,s in enumerate(record.stations):
                    s = s.ljust(8)
                    ipack[n*2] = s[:4]
                    ipack[(n*2)+1] = s[-4:]
                print(ipack)
                ier = tdlpacklib.writera_char(FORTRAN_STDOUT_LUN,self._lun,self.name,record.id,ipack,nreplace,ncheck)
            elif issubclass(record.__class__,_TdlpackRecord):
                ier = tdlpacklib.writefile(FORTRAN_STDOUT_LUN,self.name,self._lun,1,record._ipack,nreplace=nreplace,ncheck=ncheck)
        elif self.filetype == 'sequential':
            if isinstance(record,TdlpackStationRecord):
                if self.records > 0:
                    ier = tdlpacklib.trail(FORTRAN_STDOUT_LUN,self._lun,L3264B,L3264W,self.bytes_written,self.records_written)
                ipack = [s.ljust(NCHAR) for s in record.stations]
                ntotby, ntotrc = 0, 0
                ntotby, ntotrc, ier = tdlpacklib.writesq_station_record(FORTRAN_STDOUT_LUN,self._lun,ipack,ntotby,ntotrc)
            elif issubclass(record.__class__,_TdlpackRecord):
                if not hasattr(record,'_ipack'): record.pack()
                ier = tdlpacklib.writefile(FORTRAN_STDOUT_LUN,self.name,self._lun,2,record._ipack)
            self._type_lastrecord_written = record.type
        self.records += 1

    def close(self):
        """
        Close the file handle
        """
        if 'w' in self.mode:
            if self.filetype == 'sequential' and self._type_lastrecord_written == 'vector':
                ier = tdlpacklib.trail(FORTRAN_STDOUT_LUN,self._lun,L3264B,L3264W,self.bytes_written,self.records_written)
            elif self.filetype == 'random-access':
                ier = tdlpacklib.clfilm(FORTRAN_STDOUT_LUN,self._lun)
        if hasattr(self,'_filehandle'): self._filehandle.close()
        del _open_file_store[self.name]

    def select(self,**kwargs):
        """
        Select TDLPACK records by `TdlpackRecord` attributes.
        """
        # TODO: Added ability to process multiple values for each keyword (attribute)
        idxs = []
        nkeys = len(kwargs.keys())
        for k,v in kwargs.items():
            for m in self._index['record']:
                if hasattr(m,k) and getattr(m,k) == v: idxs.append(m._recnum)
        idxs = np.array(idxs,dtype='>i4')
        return [self._index['record'][i] for i in [ii[0] for ii in collections.Counter(idxs).most_common() if ii[1] == nkeys]]


class TdlpackRecord:
    """
    Creation class for TDLPACK Record.
    """
    def __new__(self, is0: np.array = np.zeros((ND7),dtype=np.int32),
                      is1: np.array = np.zeros((ND7),dtype=np.int32),
                      is2: np.array = None, #np.zeros((ND7),dtype=np.int32),
                      is4: np.array = np.zeros((ND7),dtype=np.int32),
                      *args, **kwargs):

        bases = list()
        if is2 is None:
            rectype = 'vector'
        else:
            bases.append(templates.GridDefinitionSection)
            rectype = 'grid'

        try:
            Record = _record_class_store['rectype']
        except(KeyError):
            @dataclass(init=False, repr=False)
            class Record(_TdlpackRecord, *bases):
                pass
            _record_class_store['rectype'] = Record

        # For new record, set section flags
        if np.all(is1==0):
            is1[1] = 1 if rectype == 'grid' else 0

        # For new record, make sure valid date is present
        if np.all(is1[2:8]==0):
            d = datetime.datetime.utcfromtimestamp(0)
            is1[2:7] = d.timetuple()[:5]
            is1[7] = np.int32(d.strftime(templates.DATE_FORMAT))

        return Record(is0, is1, is2, is4, *args)


@dataclass
class _TdlpackRecord:
    """
    TDLPACK Record base class
    """
    # TDLPACK Sections
    is0: np.array = field(init=True,repr=False)
    is1: np.array = field(init=True,repr=False)
    is2: np.array = field(init=True,repr=False)
    is4: np.array = field(init=True,repr=False)

    # Section 0 looked up attributes
    edition: int = field(init=False,repr=False,default=templates.Edition())

    # Section 1 looked up attributes
    sectionFlags: int = field(init=False,repr=False,default=templates.SectionFlags())
    year: int = field(init=False,repr=False,default=templates.Year())
    month: int = field(init=False,repr=False,default=templates.Month())
    day: int = field(init=False,repr=False,default=templates.Day())
    hour: int = field(init=False,repr=False,default=templates.Hour())
    minute: int = field(init=False,repr=False,default=templates.Minute())
    refDate: int = field(init=False,repr=False,default=templates.RefDate())
    id1: int = field(init=False,repr=False,default=templates.VariableID1())
    id2: int = field(init=False,repr=False,default=templates.VariableID2())
    id3: int = field(init=False,repr=False,default=templates.VariableID3())
    id4: int = field(init=False,repr=False,default=templates.VariableID4())
    id: int = field(init=False,repr=False,default=templates.VariableID())
    leadTime: int = field(init=False,repr=False,default=templates.LeadTime())
    leadTimeMinutes: int = field(init=False,repr=False,default=templates.LeadTimeMinutes())
    modelID: int = field(init=False,repr=False,default=templates.ModelID())
    modelSequenceID: int = field(init=False,repr=False,default=templates.ModelSequenceID())
    decScaleFactor: int = field(init=False,repr=False,default=templates.DecScaleFactor())
    binScaleFactor: int = field(init=False,repr=False,default=templates.BinScaleFactor())
    name: str = field(init=False,repr=False,default=templates.VariableName())
    validDate: int = field(init=False,repr=False,default=templates.ValidDate())

    # Section 4 looked up attributes
    packingFlags: int = field(init=False,repr=False,default=templates.PackingFlags())
    numberOfPackedValues: int = field(init=False,repr=False,default=templates.NumberOfPackedValues())
    primaryMissingValue: int = field(init=False,repr=False,default=templates.PrimaryMissingValue())
    secondaryMissingValue: int = field(init=False,repr=False,default=templates.SecondaryMissingValue())
    overallMinValue: int = field(init=False,repr=False,default=templates.OverallMinValue())
    numberOfGroups: int = field(init=False,repr=False,default=templates.NumberOfGroups())

    def __post_init__(self):
        """
        """
        self._data_modified = False
        self._recnum = -1
        self._linked_station_record = -1
        if self.is2 is None:
            self.type = 'vector'
        else:
            self.type = 'grid'
            self._sha1_is2 = hashlib.sha1(self.is2).hexdigest()

    def __repr__(self):
        """
        """
        info = ''
        for sect in [0,1,2,4]:
            for k,v in self.attrs_by_section(sect,values=True).items():
                info += f'Section {sect}: {k} = {v}\n'
        return info

    def __str__(self):
        """
        """
        ids = ' '.join([str(i).zfill(z) for (i,z) in zip(self.id,[9,9,9,10])])
        try:
            date = self.refDate.strftime(templates.DATE_FORMAT)
        except(ValueError):
            date = '0'.zfill(10)
        lead = int(self.leadTime.total_seconds()/3600.)
        name = self.name.rstrip()
        return (f'{self._recnum}:d={date}:{ids}:'
                f'{lead:3d}-HR FCST:{name}')

    def attrs_by_section(self, sect, values=False):
        """
        Provide a tuple of attribute names for the given TDLPACK section.

        Parameters
        ----------

        **`sect : int`**

        The TDLPACK section number.

        **`values : bool, optional`**

        Optional (default is `False`) arugment to return attributes values.

        Returns
        -------

        A List attribute names or Dict if `values = True`.
        """
        if sect in {0,1,4}:
            attrs = templates._section_attrs[sect]
        elif sect == 2 and self.type == 'grid':
            def _find_class_index(n):
                _key = {2:'Grid'}
                for i,c in enumerate(self.__class__.__mro__):
                    if _key[n] in c.__name__:
                        return i
                else:
                    return []
            if sys.version_info.minor <= 8:
                attrs = templates._section_attrs[sect]+\
                        [a for a in dir(self.__class__.__mro__[_find_class_index(sect)]) if not a.startswith('_')]
            else:
                attrs = templates._section_attrs[sect]+\
                        self.__class__.__mro__[_find_class_index(sect)]._attrs
        else:
            attrs = []
        if values:
            return {k:getattr(self,k) for k in attrs}
        else:
            return attrs

    def latlons(self):
        """
        Returns a tuple of latitudes and lontiude numpy.float32 arrays
        for the TDLPACK record. If the record is station, then return
        is None.

        Returns
        -------

        **`lats, lons : tuple of arrays`**

        Tuple of numpy.float32 arrays of grid latitudes and longitudes.
        If `self.grid = 'station'`, then None are returned.
        """
        if self.type == 'vector':
            return (None, None)
        if self._sha1_is2 in _latlon_store.keys():
            return _latlon_store[self._sha1_is2]
        lats, lons, ier = tdlpacklib.gridij_to_latlon(FORTRAN_STDOUT_LUN,self.nx,self.ny,
                          self.mapProjection,self.gridLength,self.orientationLongitude,
                          self.standardLatitude,self.latitudeLowerLeft,
                          self.longitudeLowerLeft)
        _latlon_store[self._sha1_is2] = (lats.T, -1.0*lons.T)
        return _latlon_store[self._sha1_is2]

    def pack(self):
        """
        """
        # Make sure TDLPACK sections are well-formed.
        if self.is0[0] == 0: self.is0[0] = TDLP_HEADER

        if isinstance(self._data,TdlpackRecordOnDiskArray):
            # No data read yet, so get packed message from file
            self._ipack = _open_file_store[self._source].read(self._recnum)
        elif isinstance(self._data,np.ndarray):
            # Data has been read or set, so check that, or just read the packed message.
            if self._data_modified:
                if self.type == 'grid':
                    self._ipack, ioctet, ier = tdlpacklib.pack2d_wrapper(self.is0,self.is1,
                                               self.is2,self.is4,
                                               self.data.T,ND5)
                elif self.type == 'vector':
                    self._ipack, ioctet, ier = tdlpacklib.pack1d_wrapper(self.is0,self.is1,
                                               self.is2,self.is4,
                                               self.data,ND5)
                self._ipack = self._ipack[:int(ioctet/NBYPWD)]
            else:
                self._ipack = _open_file_store[self._source].read(self._recnum)

    def unpack(self):
        """
        """
        pass

    @property
    def stations(self) -> list:
        """
        """
        return None if self.type == 'grid' else \
        _open_file_store[self._source][self._linked_station_record].stations

    @property
    def data(self) -> np.array:
        """
        Accessing the data attribute loads data into memmory
        """
        if hasattr(self,'_data'):
            self._data = np.asarray(self._data)
            return self._data
        raise ValueError

    @data.setter
    def data(self, data):
        if not isinstance(data, np.ndarray):
            raise ValueError('TdlpackRecord data only supports numpy arrays')
        if self.type == 'grid' and len(data.shape) != 2:
            raise ValueError('data must be 2D array for TDLPACK gridded record')
        elif self.type == 'vector' and len(data.shape) != 1:
            raise ValueError('data must be 1D array for TDLPACK station record')
        self._data = data
        self._data_modified = True

    def __getitem__(self, item):
        """
        """
        if self.type == 'grid':
            if not isinstance(item,tuple):
                item = tuple(item)
        elif self.type == 'vector':
            if isinstance(item,str):
                item = tuple([_open_file_store[self._source][self._linked_station_id_record].stations.index(item)])

        try:
            return self.data[item]
        except(AttributeError):
            return None

    def __setitem__(self, item):
        """
        """
        raise NotImplementedError('assignment of data not supported via setitem')


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
        return np.asarray(_data(self.filehandle, self.filetype, self.rec, self.offset, self.size),dtype=dtype)


def _data(filehandle: open, filetype: str, rec: TdlpackRecord, offset: int, size: int)-> np.array:
    """
    Returns an unpacked data grid.

    Returns
    -------

    **`numpy.ndarray`**

    A numpy.ndarray with shape (ny,nx). By default the array dtype is np.float32.
    """

    # Position file pointer to the beginning of the TDLPACK record.
    filehandle.seek(offset)
    if filetype == 'sequential':
        ioctet = np.frombuffer(filehandle.read(8),dtype='>i8')[0]
    elif filetype == 'random-access':
        ioctet = size
    _ipack = np.frombuffer(filehandle.read(ioctet),dtype='>i4')

    # Unpack data
    ipack = np.zeros((rec.numberOfPackedValues),dtype='>i4')
    ipack[0:_ipack.shape[0]] = np.copy(_ipack[:])
    del _ipack
    is0,is1,is2,is4,xdata,ier = tdlpacklib.unpack_data_wrapper(ipack,ND7)

    return xdata.reshape((rec.ny,rec.nx)) if rec.type == 'grid' else xdata


@dataclass
class TdlpackStationRecord:
    stations: list = field(init=False,repr=False,default=templates.Stations())
    numberOfStations: int = field(init=False,repr=False,default=templates.NumberOfStations())
    type: str = field(init=False,repr=False,default='station')

    _stations: list = None
    _numberOfStations: int = 0

    def __post_init__(self):
        self.id = [400001000, 0, 0, 0]

    def __str__(self):
        return (f'{self._recnum}:d=0000000000:'
                f'STATION CALL LETTER RECORD:{self.numberOfStations}')

    def pack(self):
        """
        """
        pass

    def unpack(self):
        """
        """
        pass


@dataclass
class TdlpackTrailerRecord:
    type: str = field(init=False,repr=False,default='trailer')

    def __str__(self):
        return (f'{self._recnum}:d=0000000000:TRAILER RECORD')

    def pack(self):
        self._ipack = np.array([0, 0, 0, 0, 9999, 0],dtype=np.int32)

    def unpack(self,record):
        pass
