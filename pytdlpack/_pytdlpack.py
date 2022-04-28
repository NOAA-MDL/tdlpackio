"""
Introduction
============

pytdlpack is a Python interface to reading/writing TDLPACK files via official
MOS-2000 (MOS2K) Fortran-based source files.  The necessary MOS2K source files are included
in this package and are available as module, tdlpack.

TDLPACK is a GRIB-like binary data format that is exclusive to MOS2K Fortran-based 
sofftware system.  This software system was developed at the Meteorological Development 
Laboratory (MDL) within NOAA/NWS and its primary purpose is to perform statistical 
post-processing of meteorological data.

TDLPACK-formatted data are contained in two type of Fortran-based files;
sequential or random-access.  Sequential files are variable length, record-based, and unformatted.
Random-access files are fixed-length and direct-access.  pytdlpack accommodates reading
and writing of both types of TDLPACK files.

TDLPACK format is based on the World Meteorological Organizations (WMO) GRIdded Binary (GRIB)
code, but has been tailored to MDL needs for data -- mainly the ability to store 1D (vector),
datasets such as station observations, along with 2D grids.

There also exists two other types of records in a TDLPACK file: station call letter record
and trailer record.  A station call letter record can exist in both types of TDLPACK files
and contains a stream of alphanumeric characters (`CHARACTER(LEN=8)`).  A trailer record exists
to signal the MOS2K system that another station call letter record is about to be read or we
have reached the end of the file (EOF).  A trailer record is not written to a random-access
file.

For more information on the MOS-2000 software system and TDLPACK foremat, user is
referred to the official [MOS-2000 documentation](https://www.weather.gov/media/mdl/TDL_OfficeNote00-1.pdf).

In order for pytdlpack to read/write TDLPACK files, we need to compile the necessary MOS2K
Fortran source code into a shared object library.  This is handled by the setup process as the
Fortran source is compiled with f2py (included with Numpy).  The following are some important
items to note regarding MOS2K source files included:

- Several Fortran 90+ source files have been created to better interface to MOS2K Fortran 77 code.
- The only modification made to MOS2K source files is changing the filename variable, `CFILX` from
`CHARACTER*60` to `CHARACTER*1024` in the appropropriate subroutines where random-access file IO
occurs.

Download
========

- Latest code from [github repository](https://github.com/eengl/pytdlpack).
- Latest [releases](https://github.com/eengl/pytdlpack/releases) on GitHub.
- [PyPI](https://pypi.org/project/pytdlpack)

Requires
========

- Python 3.6+
- [numpy array module](http://numpy.scipy.org), version 1.12 or later.
- [setuptools](https://pypi.python.org/pypi/setuptools), version 18.0 or later.
- GNU or Intel Fortran compiler (if installing from source).

Install
=======

```shell
pip3 install pytdlpack
```

**Build and Install from Source**

```shell
python3 setup.py build_ext --fcompiler=[gnu95|intelem] build
python3 setup.py install [--user | --prefix=PREFIX]
```

Tutorial
========

1. [Creating/Opening/Closing a TDLPACK file.](#section1)
2. [Reading a TDLPACK file.](#section2)
3. [Writing a TDLPACK file.](#section3)
4. [Creating a TDLPACK Station Record.](#section4)
5. [Creating a TDLPACK Record.](#section5)
6. [Packing/Unpacking a TDLPACK Record.](#section6)

## <div id='section1'>1) Creating/Opening/Closing a TDLPACK file.

To create a TDLPACK file from Python, you call the `pytdlpack.open` function and provide the
file name and `mode='w' or 'a'`.  For `mode='a'`, this will append to an existing file.  When 
creating a new file, the default file format is `'sequential'`, but the user can also specify 
the format with `format='sequential' or 'random-access'`.  If the new file is random-access, 
then the user can also specify `ra_template='small' or 'large'`.  The default is 'small' and
'large' is recommended for a high-resolution grids (i.e. ~ > 2M total points).

Example: Create a new sequential file:

```python
>>> import pytdlpack
>>> f = pytdlpack.open('test.sq',mode='w')
```

Example: Create a new random-access file:

```python
>>> import pytdlpack
>>> f = pytdlpack.open('test.sq',mode='w',format='random-access',ra_template='small')
```

To open an existing TDLPACK file, simply provide the filename since the default mode is read.

```python
import pytdlpack
>>> f = pytdlpack.open('test.sq')
>>> type(f)
<class 'pytdlpack._pytdlpack.TdlpackFile'>
>>> f
byte_order = >
data_type =
eof = False
format = sequential
fortran_lun = 65535
mode = r
name = test.sq
position = 0
ra_master_key = None
size = 998672
```

To close a TDLPACK file is straightforward.

```python
>>> f.close()
```

## <div id='section2'>2) Reading a TDLPACK file.

When a TDLPACK file is opened, an instance of class `pytdlpack.TdlpackFile` is created.  
To read a record the file, use the class method `pytdlpack.TdlpackFile.read`.  By default 
only 1 record is returned and the TDLPACK indentification sections are unpacked.

Example: Reading a gridded TDLPACK record.

```python
>>> x = f.read()
>>> x
grid_length = 2539.703
id = [223254166         0         6         0]
ioctet = 998656
ipack = [1347175508  255654144 1191249890 ...          0          0          0]
is0 = [1347175508     998649          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0]
is1 = [        71          1       2018         12          4          0
          0 2018120400  223254166          0          6          0
          6          0         66          0          1          0
          0          0          0         32          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0
          0          0          0          0          0          0]
is2 = [     28       3    2345    1597  192290 2337234  950000 2539703  250000
       0       0       0       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0]
is4 = [ 998538      12 3744965       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0
       0       0       0       0       0       0       0       0       0]
lead_time = 6
lower_left_latitude = 19.229
lower_left_longitude = 233.7234
map_proj = 3
number_of_values = 3744965
nx = 2345
ny = 1597
origin_longitude = 95.0
plain =
primary_missing_value = 0.0
reference_date = 2018120400
secondary_missing_value = 0.0
standard_latitude = 25.0
type = grid
```

You can also have `pytdlpack.TdlpackFile.read` read the entire file with optional keyword
`all = True`.  Reading all records at once is not recommened if the file is large in size.

```python
>>> x = f.read(all=True)
```

Here, x will become a list of instances of either `pytdlpack.TdlpackStationRecord`, 
`pytdlpack.TdlpackRecord`, or `pytdlpack.TdlpackTrailerRecord`.

If the file being read a TDLPACK random-access (`format='random-access'`), then you can also provide the `id=` 
argument to search for a specific record.

```python
>>> import pytdlpack
>>> f = pytdlpack.open('test.ra')
>>> x = f.read(id=[400001000,0,0,0])
>>> type(x)
<class 'pytdlpack._pytdlpack.TdlpackStationRecord'>
```

## <div id='section3'>3) Writing a TDLPACK file.

Writing to a TDLPACK file is as easy as reading.  The following uses variable x, from 
above, is an instance of `pytdlpack.TdlpackStationRecord` that has been packed.

Example: Write to a new TDLPACK sequential file.

```python
>>> import pytdlpack
>>> f.open("new.sq",mode="w",format="sequential")
>>> f.write(x)
>>> f.close()
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

from copy import deepcopy
from itertools import count
import pdb
import os
import struct
import sys

_IS_PYTHON3 = sys.version_info.major >= 3

if _IS_PYTHON3:
    import builtins
else:
    import __builtin__ as builtins

try:
    import numpy as np
except ImportError:
    raise ImportError("NumPy required")
try:
    import tdlpack
except ImportError:
    raise ImportError("tdlpack not found.")

__pdoc__ = {}

_DEFAULT_L3264B = np.int32(32)
_DEFAULT_MINPK = np.int32(14)
_DEFAULT_ND5 = np.int32(5242880)
_DEFAULT_ND7 = np.int32(54)

DEFAULT_MISSING_VALUE = np.float32(9999.0)
FORTRAN_STDOUT_LUN = np.int32(12)
L3264B = _DEFAULT_L3264B
L3264W = np.int32(64/L3264B)
MINPK = _DEFAULT_MINPK
NCHAR = np.int32(8)
NCHAR_PLAIN = np.int32(32)
ND5 = _DEFAULT_ND5
ND5_META_MIN = np.int32(24)
ND5_META_MAX = np.int32(32)
ND7 = _DEFAULT_ND7
NBYPWD = np.int32(L3264B/8)

_starecdict = {} # Dictionary to store station lists.  Key is the Fortran LUN where list came from.
_ccall = []
_ier = np.int32(0)
_lx = np.int32(0)
_misspx = np.int32(0)
_misssx = np.int32(0)
_is0 = np.zeros((ND7),dtype=np.int32)
_is1 = np.zeros((ND7),dtype=np.int32)
_is2 = np.zeros((ND7),dtype=np.int32)
_is4 = np.zeros((ND7),dtype=np.int32)

_ier = tdlpack.openlog(FORTRAN_STDOUT_LUN,file=os.devnull)
if _ier != 0:
    raise IOError("Cannot write to log file")

class TdlpackFile(object):
    """
    TDLPACK File with associated information.

    Attributes
    ----------

    **`byte_order : str`**

    Byte order of TDLPACK file using definitions as defined by Python built-in struct module.

    **`data_type : {'grid', 'station'}`**

    Type of data contained in the file.

    **`eof : bool`**

    True if we have reached end of file.

    **`format : {'random-access', 'sequential'}`**

    File format of TDLPACK file.

    **`fortran_lun : np.int32`**

    Fortran unit number for file access. If the file is not open, then this value is -1. 

    **`mode : str`**

    Access mode (see pytdlpack.open() docstring).

    **`name : str`**

    File name.

    **`position : int`**

    The current record being read from file. If the file type is 'random-access', then this
    value is -1.

    **`size : int`**

    File size in units of bytes.
    """
    counter = 0
    def __init__(self,**kwargs):
        """Contructor"""
        type(self).counter += 1
        self.byte_order = ''
        self.data_type = ''
        self.eof = False
        self.format = ''
        self.fortran_lun = np.int32(-1)
        self.mode = ''
        self.name = ''
        self.position = np.int32(0)
        self.ra_master_key = None
        for k, v in kwargs.items():
            setattr(self,k,v)

    def __repr__(self):
        strings = []
        keys = self.__dict__.keys()
        for k in keys:
            if not k.startswith('_'):
                strings.append('%s = %s\n'%(k,self.__dict__[k]))
        return ''.join(strings)

    def __enter__(self):
        """no additional setup as opening with context manager is not required"""
        return self

    def __exit__(self,type,value,traceback):
        """
        """
        self.close()

    def __iter__(self):
        """
        """
        return self

    def __next__(self):
        """
        """
        if not self.eof:
            rec = self.read()
            if self.eof and isinstance(rec,type(None)):
                raise StopIteration
            else:
                return rec
        else:
            raise StopIteration

    def _determine_record_type(self,ipack,ioctet):
        kwargs = {}
        if ipack[0] == 0 and ipack[4] == 9999 and ioctet == 24:
            kwargs['ipack'] = deepcopy(ipack)
            kwargs['ioctet'] = deepcopy(ioctet)
            kwargs['id'] = np.int32([0,0,0,0])
            return TdlpackTrailerRecord(**kwargs)
        if ipack[0] > 0:
            kwargs['ipack'] = deepcopy(ipack)
            kwargs['ioctet'] = deepcopy(ioctet)
            header = struct.unpack('>4s',ipack[0].byteswap())[0]
            if _IS_PYTHON3:
                header = header.decode()
            if header in ["PLDT","TDLP"] :
                if not self.data_type: self.data_type = 'grid'
                kwargs['id'] = deepcopy(ipack[5:9])
                kwargs['reference_date'] = deepcopy(ipack[4])
                kwargs['lead_time'] = np.int32(str(ipack[7])[-3:])
                kwargs['_filelun'] = self.fortran_lun
                kwargs['_starecindex'] = len(_starecdict[self.fortran_lun])-1 if len(_starecdict[self.fortran_lun]) > 0 else 0
                return TdlpackRecord(**kwargs)
            else:
                if not self.data_type: self.data_type = 'station'
                kwargs['id'] = np.int32([400001000,0,0,0])
                kwargs['number_of_stations'] = np.int32(deepcopy(ioctet/NCHAR))
                return TdlpackStationRecord(**kwargs)
        else:
            #raise
            pass #for now

    def backspace(self):
        """
        Position file backwards by one record.
        """
        if self.fortran_lun == -1:
            raise IOError("File is not opened.")

        if self.format == 'sequential':
            _ier = np.int32(0)
            _ier = tdlpack.backspacefile(self.fortran_lun)
            if _ier == 0:
                self.position -= 1
            else:
                raise IOError("Could not backspace file. ier = "+str(_ier))

    def close(self):
        """
        Close a TDLPACK file.
        """
        _ier = np.int32(0)
        if self.format == 'random-access':
            _ier = tdlpack.clfilm(FORTRAN_STDOUT_LUN,self.fortran_lun)
        elif self.format == 'sequential':
            _ier = tdlpack.closefile(FORTRAN_STDOUT_LUN,self.fortran_lun,np.int32(2))
        if _ier == 0:
            try:
                del _starecdict[self.fortran_lun]
            except(KeyError):
                pass
            self.eof = False
            self.fortran_lun = -1
            self.position = 0
            type(self).counter -= 1
        else:
            raise IOError("Trouble closing file. ier = "+str(_ier))

    def read(self,all=False,unpack=True,id=[9999,0,0,0]):
        """
        Read a record from a TDLPACK file.

        Parameters
        ----------

        **`all : bool, optional`**

        Read all records from file. The default is False.

        **`unpack : bool, optional`**

        Unpack TDLPACK identification sections.  Note that data are not unpacked.  The default is True.
            
        **`id : array_like or list, optional`**

        Provide an ID to search for. This can be either a Numpy.int32 array with shape (4,) or list 
        with length 4.  The default is [9999,0,0,0] which will signal the random access IO reader
        to sequentially read the file.
        
        Returns
        -------

        **`record [records] : instance [list]`**

        An instance of list of instances contaning `pytdlpack.TdlpackStationRecord`, 
        `pytdlpack.TdlpackRecord`, or `pytdlpack.TdlpackTrailerRecord`
        """
        if self.fortran_lun == -1:
            raise IOError("File is not opened.")

        record = None
        records = []
        while True:
            _ipack = np.array((),dtype=np.int32)
            _ioctet = np.int32(0)
            _ier = np.int32(0)
            if self.format == 'random-access':
                id = np.int32(id)
                _nvalue = np.int32(0)
                _ipack,_nvalue,_ier = tdlpack.rdtdlm(FORTRAN_STDOUT_LUN,self.fortran_lun,self.name,id,ND5,L3264B)
                if _ier == 0:
                    _ioctet = _nvalue*NBYPWD
                    record = self._determine_record_type(_ipack,_ioctet)
                elif _ier == 153:
                    self.eof = True
                    break
                else:
                    #raise
                    pass # for now
            elif self.format == 'sequential':
                _ioctet,_ipack,_ier = tdlpack.readfile(FORTRAN_STDOUT_LUN,self.name,self.fortran_lun,ND5,L3264B,np.int32(2))
                if _ier == 0:
                    record = self._determine_record_type(_ipack,_ioctet)
                    self.position += 1
                elif _ier == -1:
                    self.eof = True
                    break

            if unpack: record.unpack()

            if type(record) is TdlpackStationRecord:
                _starecdict[self.fortran_lun].append(record.stations)

            if all:
                records.append(record)
            else:
                break

        if len(records) > 0:
            return records
        else:
            return record
    
    def rewind(self):
        """
        Position file to the beginning.
        """
        if self.fortran_lun == -1:
            raise IOError("File is not opened.")

        if self.format == 'sequential':
            _ier = np.int32(0)
            _ier = tdlpack.rewindfile(self.fortran_lun)
            if _ier == 0:
                self.position = 0
                self.eof = False
            else:
                raise IOError("Could not rewind file. ier = "+str(_ier))

    def write(self,record):
        """
        Write a packed TDLPACK record to file.

        Parameters
        ----------

        **`record : instance`**

        An instance of either `pytdlpack.TdlpackStationRecord`, `pytdlpack.TdlpackRecord`, 
        or `pytdlpack.TdlpackTrailerRecord`.  `record` should contain a packed data.
        """
        #pdb.set_trace()
        if self.fortran_lun == -1:
            raise IOError("File is not opened.")
        if self.mode == "r":
            raise IOError("File is read-only.")

        _ier = np.int32(0)
        _ntotby = np.int32(0)
        _ntotrc = np.int32(0)
        _nreplace = np.int32(0)
        _ncheck = np.int32(0)

        if type(record) is TdlpackStationRecord:
            if self.position == 0: self.data_type = 'station'
            _nwords = record.number_of_stations*2
            if self.format == 'random-access':
                _ier = tdlpack.wrtdlm(FORTRAN_STDOUT_LUN,self.fortran_lun,self.name,
                                       record.id,record.ipack[0:_nwords],_nreplace,
                                       _ncheck,L3264B)
            elif self.format == 'sequential':
                _ntotby,_ntotrc,_ier = tdlpack.writep(FORTRAN_STDOUT_LUN,self.fortran_lun,
                                       record.ipack[0:_nwords],_ntotby,_ntotrc,L3264B)
        elif type(record) is TdlpackRecord:
            if self.position == 0: self.data_type = 'grid'
            _nwords = np.int32(record.ioctet/NBYPWD)
            if self.format == 'random-access':
                record.ipack[0] = record.ipack[0].byteswap()
                _ier = tdlpack.wrtdlm(FORTRAN_STDOUT_LUN,self.fortran_lun,self.name,
                                       record.id,record.ipack[0:_nwords],_nreplace,
                                       _ncheck,L3264B)
            elif self.format == 'sequential':
                _ntotby,_ntotrc,_ier = tdlpack.writep(FORTRAN_STDOUT_LUN,self.fortran_lun,
                                       record.ipack[0:_nwords],_ntotby,_ntotrc,L3264B)
        elif type(record) is TdlpackTrailerRecord:
            _ier = tdlpack.trail(FORTRAN_STDOUT_LUN,self.fortran_lun,L3264B,L3264W,_ntotby,
                           _ntotrc)
        if _ier == 0:
            self.position += 1
            self.size = os.path.getsize(self.name)

class TdlpackRecord(object):
    """
    Defines a TDLPACK data record object.  Once data are unpacked (TdlpackRecord.unpack(data=True)),
    values are accessible using "fancy indexing".

    For gridded records, use grid index values and/or ranges (e.g. rec[0,0]).
    
    For station records, use the station ID string: (e.g. rec['KPHL']).

    Attributes
    ----------

    **`data : array_like`**

    Data values.

    **`grid_length : float`**

    Distance between grid points in units of meters.

    **`id : array_like`**

    ID of the TDLPACK data record. This is a NumPy 1D array of dtype=np.int32.

    **`ioctet : int`**

    Size of the packed TDLPACK data record in bytes.

    **`ipack : array_like`**

    Packed TDLPACK data record. This is a NumPy 1D array of dtype=np.int32.

    **`is0 : array_like`**

    TDLPACK Section 0 (Indicator Section).

    **`is1 : array_like`**

    TDLPACK Section 1 (Product Definition Section).

    **`is2 : array_like`**

    TDLPACK Section 2 (Grid Definition Section)

    **`is4 : array_like`**

    TDLPACK Section 4 (Data Section).

    **`lead_time : int`**

    Forecast lead time in units of hours.

    **`lower_left_latitude : float`**

    Latitude of lower left grid point

    **`lower_left_longitude : float`**

    Longitude of lower left grid point

    **`number_of_values : int`**

    Number of data values.

    **`nx : int`**

    Number of points in the x-direction (West-East).

    **`ny : int`**

    Number of points in the y-direction (West-East).

    **`origin_longitude : float`**

    Originating longitude of projected grid.

    **`plain : str`**

    Plain language description of TDLPACK record.

    **`primary_missing_value : float`**

    Primary missing value.

    **`reference_date : int`**

    Reference date from the TDLPACK data record in YYYYMMDDHH format.

    **`secondary_missing_value : float`**

    Secondary missing value.

    **`standard_latitude : float`**

    Latitude at which the grid length applies.

    **`type : {'grid', 'station'}`**

    Identifies the type of data.  This implies that data are 1D for type = 'station'
    and data are 2D for type = 'grid'.

    """
    counter = 0
    def __init__(self,date=None,id=None,lead=None,plain=None,grid=None,data=None,
                 missing_value=None,**kwargs):
        """
        Constructor

        Parameters
        ----------

        **`date : int, optional`**

        Forecast initialization or observation date in YYYYMMDDHH format.

        **`id : list or 1-D array, optional`**

        List or 1-D array of length 4 containing the 4-word (integer) MOS-2000 ID of the data
        to be put into TdlpackRecord

        **`lead : int, optional`**

        Lead time (i.e. forecast projection) in hours of the data.  NOTE: This can be omitted

        **`plain : str, optional`**

        Plain language descriptor.  This is limited to 32 characters, though here 
        the input can be longer (will be cut off when packing).

        **`grid : dict , optional`**

        A dictionary containing grid definition attributes.  See
        Dictionary of grid specs (created from create_grid_def_dict)

        **`data : array_like, optional`**

        Data values.

        **`missing_value : float or list of floats, optional`**

        Provide either a primary missing value or primary and secondary as list.

        **`**kwargs : dict, optional`**

        Dictionary of class attributes (keys) and class attributes (values).
        """
        type(self).counter += 1
        self._metadata_unpacked = False
        self._data_unpacked = False
        self.plain = ''
        if len(kwargs) == 0:
            # Means we are creating TdlpackRecord instance from the other function
            # input, NOT the kwargs Dict.
            self.id = id
            self.reference_date = date
            self.type = 'station'
            self.is0 = np.zeros(ND7,dtype=np.int32)
            self.is1 = np.zeros(ND7,dtype=np.int32)
            self.is2 = np.zeros(ND7,dtype=np.int32)
            self.is4 = np.zeros(ND7,dtype=np.int32)

            self.is1[2] = np.int32(date/1000000)
            self.is1[3] = np.int32((date/10000)-(self.is1[2]*100))
            self.is1[4] = np.int32((date/100)-(self.is1[2]*10000)-(self.is1[3]*100))
            self.is1[5] = np.int32(date-((date/100)*100))
            self.is1[6] = np.int32(0)
            self.is1[7] = np.int32(date)
            self.is1[8] = np.int32(id[0])
            self.is1[9] = np.int32(id[1])
            self.is1[10] = np.int32(id[2])
            self.is1[11] = np.int32(id[3])
            if lead is None:
                self.is1[12] = np.int32(self.is1[10]-((self.is1[10]/1000)*1000))
            else:
                self.is1[12] = np.int32(lead)
            self.is1[13] = np.int32(0)
            self.is1[14] = np.int32(self.is1[8]-((self.is1[8]/100)*100))
            self.is1[15] = np.int32(0)
            self.is1[16] = np.int32(0)
            self.is1[17] = np.int32(0)
            self.is1[18] = np.int32(0)
            self.is1[19] = np.int32(0)
            self.is1[20] = np.int32(0)
            self.is1[21] = NCHAR_PLAIN
            if plain is None:
                self.plain = ' '*NCHAR_PLAIN
            else:
                self.plain = plain
                for n,p in enumerate(plain):
                    self.is1[22+n] = np.int32(ord(p))

            if grid is not None and type(grid) is dict or data.shape == 2:
                # Gridded Data
                self.type = 'grid'
                self.is1[1] = np.int32(1) # Set IS1[1] = 1
                self.is2[1] = np.int32(grid['proj'])
                self.is2[2] = np.int32(grid['nx'])
                self.is2[3] = np.int32(grid['ny'])
                self.is2[4] = np.int32(grid['latll']*10000)
                self.is2[5] = np.int32(grid['lonll']*10000)
                self.is2[6] = np.int32(grid['orientlon']*10000)
                self.is2[7] = np.int32(grid['meshlength']*1000) # Value in dict is in units of meters.
                self.is2[8] = np.int32(grid['stdlat']*10000)
                self.nx = np.int32(grid['nx'])
                self.ny = np.int32(grid['ny'])
            if len(data) > 0:
                self.data = np.array(data,dtype=np.float32)
                self.number_of_values = len(data)
                self._data_unpacked = True
            else:
                raise ValueError

            if missing_value is None:
                self.primary_missing_value = np.int32(0)
                self.secondary_missing_value = np.int32(0)
            else:
                if type(missing_value) is list:
                    if len(missing_value) == 1:
                        self.primary_missing_value = np.int32(missing_value[0])
                    elif len(missing_value) == 2:
                        self.primary_missing_value = np.int32(missing_value[0])
                        self.secondary_missing_value = np.int32(missing_value[1])
                else:
                    self.primary_missing_value = np.int32(missing_value)
                    self.secondary_missing_value = np.int32(0)

        else:
            # Instantiate via **kwargs
            for k,v in kwargs.items():
                setattr(self,k,v)

    def __getitem__(self,indices):
        """
        """
        if self.type == 'grid':
            if not isinstance(indices,tuple):
                indices = tuple(indices)
        elif self.type == 'station':
            if isinstance(indices,str):
                indices = tuple([_starecdict[self._filelun][self._starecindex].index(indices)])

        try:
            return self.data[indices]
        except(AttributeError):
            return None

    def __setitem__(self,indices,values):
        """
        """
        if self.type == 'grid':
            if not isinstance(indices,tuple):
                indices = tuple(indices)
        elif self.type == 'station':
            if isinstance(indices,str):
                indices = tuple([_starecdict[self._filelun][self._starecindex].index(indices)])

        self.data[indices] = values

    def __repr__(self):
        strings = []
        keys = self.__dict__.keys()
        for k in keys:
            if not k.startswith('_'):
                strings.append('%s = %s\n'%(k,self.__dict__[k]))
        return ''.join(strings)
    
    def pack(self,dec_scale=None,bin_scale=None):
        """
        Pack a TDLPACK record.

        Parameters
        ----------

        **`dec_scale : int, optional, default = 1`**

        Decimal Scale Factor used to when packing TdlpackRecord data [DEFAULT is 1].

        **`bin_scale : int, optional, default = 0`**

        Binary Scale Factor used to when packing TdlpackRecord data [DEFAULT is 0]. NOTE:
        binary scale factor is currently NOT SUPPORTED in MOS-2000 software. It is added
        here for completeness.
        """

        # Make sure data are unpacked
        if not self._data_unpacked:
            self.unpack(data=True)

        _ier = np.int32(0)
        self.ipack = np.zeros((ND5),dtype=np.int32)

        if dec_scale is not None:
            self.is1[16] = np.int32(dec_scale)

        if bin_scale is not None:
            self.is1[17] = np.int32(bin_scale)

        # Pack plain langauge into IS1 array.
        self.plain = self.plain.ljust(NCHAR_PLAIN)
        for n,p in enumerate(self.plain):
            self.is1[22+n] = np.int32(ord(p))

        # Handle potential NaN values
        if self.primary_missing_value == 0:
            self.primary_missing_value == DEFAULT_MISSING_VALUE
        self.data = np.where(np.isnan(self.data),np.float32(self.primary_missing_value),
                             self.data)

        if self.type == 'grid':
            _a = np.zeros((self.nx,self.ny),dtype=np.float32,order='F')
            _ia = np.zeros((self.nx,self.ny),dtype=np.int32,order='F')
            _ic = np.zeros((self.nx*self.ny),dtype=np.int32)
            self.ioctet,_ier = tdlpack.pack2d(FORTRAN_STDOUT_LUN,self.data,_ia,_ic,self.is0,
                               self.is1,self.is2,self.is4,self.primary_missing_value,
                               self.secondary_missing_value,self.ipack,MINPK,_lx,L3264B)
        elif self.type == 'station':
            _ic = np.zeros((self.number_of_values),dtype=np.int32)
            self.ioctet,_ier = tdlpack.pack1d(FORTRAN_STDOUT_LUN,self.data,_ic,self.is0,
                               self.is1,self.is2,self.is4,self.primary_missing_value,
                               self.secondary_missing_value,self.ipack,MINPK,
                               _lx,L3264B)
    
    def unpack(self,data=False,missing_value=None):
        """
        Unpacks the TDLPACK identification sections and data (optional).

        Parameters
        ----------

        **`data : bool, optional`**

        If True, unpack data values. The default is False.

        **`missing_value : float, optional`**
        
        Set a missing value. If a missing value exists for the TDLPACK data record,
        it will be replaced with this value.
        """
        _ier = np.int32(0)
        if not self._metadata_unpacked:
            if self.ipack.shape[0] < ND5_META_MAX:
                _nd5_local = self.ipack.shape[0]
            else:
                _nd5_local = ND5_META_MAX
            _data_meta = np.zeros((_nd5_local),dtype=np.int32)
            _iwork_meta = np.zeros((_nd5_local),dtype=np.int32)
            _data_meta,_ier = tdlpack.unpack(FORTRAN_STDOUT_LUN,self.ipack[0:_nd5_local],
                              _iwork_meta,_is0,_is1,_is2,_is4,_misspx,
                              _misssx,np.int32(1),L3264B)
            if _ier == 0:
                self._metadata_unpacked = True
                self.is0 = deepcopy(_is0)
                self.is1 = deepcopy(_is1)
                self.is2 = deepcopy(_is2)
                self.is4 = deepcopy(_is4)
                self.id = self.is1[8:12]

        # Set attributes from is1[].
        self.lead_time = np.int32(str(self.is1[10])[-3:])
        if not self.plain:
            if self.is1[21] > 0:
                for n in np.nditer(self.is1[22:(22+self.is1[21])]):
                    self.plain += chr(n)
            else:
                self.plain = ' '*NCHAR_PLAIN

        # Set attributes from is2[].
        if self.is1[1] == 0:
            self.type = 'station'
            self.map_proj = None
            self.nx = None
            self.ny = None
            self.lower_left_latitude = None
            self.lower_left_longitude = None
            self.origin_longitude = None
            self.grid_length = None
            self.standard_latitude = None
            if np.sum(self.is2) > 0: self.is2 = np.zeros((ND7),dtype=np.int32)
        elif self.is1[1] == 1:
            self.type = 'grid'
            self.map_proj = self.is2[1]
            self.nx = self.is2[2]
            self.ny = self.is2[3]
            self.lower_left_latitude = self.is2[4]/10000.
            self.lower_left_longitude = self.is2[5]/10000.
            self.origin_longitude = self.is2[6]/10000.
            self.grid_length = self.is2[7]/1000.
            self.standard_latitude = self.is2[8]/10000.
            self.grid_def = create_grid_definition(proj=self.map_proj,nx=self.nx,ny=self.ny,
                            latll=self.lower_left_latitude,lonll=self.lower_left_longitude,
                            orientlon=self.origin_longitude,stdlat=self.standard_latitude,
                            meshlength=self.grid_length)
            self.proj_string = _create_proj_string(self.grid_def)
       
        # Set attributes from is4[].
        self.number_of_values = self.is4[2]
        self.primary_missing_value = deepcopy(np.float32(self.is4[3]))
        self.secondary_missing_value = deepcopy(np.float32(self.is4[4]))

        if data:
            self._data_unpacked = True
            _nd5_local = max(self.is4[2],int(self.ioctet/NBYPWD))
            _iwork = np.zeros((_nd5_local),dtype=np.int32)
            _data = np.zeros((_nd5_local),dtype=np.float32)
            # Check to make sure the size of self.ipack is long enough. If not, then
            # we will "append" to self.ipack.
            if self.ipack.shape[0] < _nd5_local:
                pad = np.zeros((_nd5_local-self.ipack.shape[0]),dtype=np.int32)
                self.ipack = np.append(self.ipack,pad)
            _data,_ier = tdlpack.unpack(FORTRAN_STDOUT_LUN,self.ipack[0:_nd5_local],
                                         _iwork,self.is0,self.is1,self.is2,self.is4,
                                         _misspx,_misssx,np.int32(2),L3264B)
            if _ier == 0:
                _data = deepcopy(_data[0:self.number_of_values+1])
            else:
                _data = np.zeros((self.number_of_values),dtype=np.float32)+DEFAULT_MISSING_VALUE
            self.data = deepcopy(_data[0:self.number_of_values])
            if missing_value is not None:
                self.data = np.where(self.data==self.primary_missing_value,np.float32(missing_value),self.data)
                self.primary_missing_value = np.float32(missing_value)
            if self.type == 'grid':
                self.data = np.reshape(self.data[0:self.number_of_values],(self.nx,self.ny),order='F')
    
    def latlons(self):
        """
        Returns a tuple of latitudes and lontiude numpy.float32 arrays for the TDLPACK record.
        If the record is station, then return is None.

        Returns
        -------

        **`lats,lons : array_like`**
        
        Numpy.float32 arrays of grid latitudes and longitudes.  If `self.grid = 'station'`, then None are returned.
        """
        lats = None
        lons = None
        if self.type == 'grid':
            _ier = np.int32(0)
            lats = np.zeros((self.nx,self.ny),dtype=np.float32,order='F')
            lons = np.zeros((self.nx,self.ny),dtype=np.float32,order='F')
            lats,lons,_ier = tdlpack.gridij_to_latlon(FORTRAN_STDOUT_LUN,self.nx,self.ny,
                             self.map_proj,self.grid_length,self.origin_longitude,
                             self.standard_latitude,self.lower_left_latitude,
                             self.lower_left_longitude)
        return (lats,lons)

class TdlpackStationRecord(object):
    """
    Defines a TDLPACK Station Call Letter Record.

    Attributes
    ----------

    **`station : list`**

    A list of station call letters.

    **`id : array_like`**

    ID of station call letters. Note: This id is only used for random-access IO.

    **`ioctet : int`**

    Size of packed station call letter record in bytes.

    **`ipack : array_like`**

    Array containing the packed station call letter record.

    **`number_of_stations: int`**

    Size of station call letter record.
    """
    counter = 0
    def __init__(self,stations=None,**kwargs):
        """
        `pytdlpack.TdlpackStationRecord` Constructor

        Parameters
        ----------

        **`stations : str or list or tuple`**

        String of a single station or a list or tuple of stations.
        """
        type(self).counter += 1

        if stations is not None:
            if type(stations) is str:
                self.stations = [stations]
            elif type(stations) is list:
                self.stations = stations
            elif type(stations) is tuple:
                self.stations = list(stations)
            else:
                pass # TODO: raise error... TypeError
            self.number_of_stations = np.int32(len(stations))
            self.id = np.int32([400001000,0,0,0])
            self.ioctet = np.int32(0)
            self.ipack = np.array((),dtype=np.int32)
        else:
            for k,v in kwargs.items():
                setattr(self,k,v)

        #self.number_of_stations = np.int32(len(stations))
        #self.id = np.int32([400001000,0,0,0])
        #self.ioctet = np.int32(0)
        #self.ipack = np.array((),dtype=np.int32)

    def __repr__(self):
        strings = []
        keys = self.__dict__.keys()
        for k in keys:
            if not k.startswith('_'):
                strings.append('%s = %s\n'%(k,self.__dict__[k]))
        return ''.join(strings)
    
    def pack(self):
        """
        Pack a Station Call Letter Record.
        """
        #pdb.set_trace()
        self.ioctet = np.int32(self.number_of_stations*NCHAR)
        self.ipack = np.ndarray(int(self.ioctet/(L3264B/NCHAR)),dtype=np.int32)
        for n,s in enumerate(self.stations):
            sta = s.ljust(int(NCHAR),' ')
            self.ipack[n*2] = np.copy(np.fromstring(sta[0:int(NCHAR/2)],dtype=np.int32).byteswap())
            self.ipack[(n*2)+1] = np.copy(np.fromstring(sta[int(NCHAR/2):int(NCHAR)],dtype=np.int32).byteswap())

    def unpack(self):
        """
        Unpack a Station Call Letter Record.
        """
        _stations = []
        _unpack_string_fmt = '>'+str(NCHAR)+'s'
        nrange = range(0,int(self.ioctet/(NCHAR/2)),2)
        if _IS_PYTHON3:
            nrange = list(range(0,int(self.ioctet/(NCHAR/2)),2))
        for n in nrange:
            tmp = struct.unpack(_unpack_string_fmt,self.ipack[n:n+2].byteswap())[0]
            if _IS_PYTHON3:
                tmp = tmp.decode()
            _stations.append(tmp.strip(' '))
        self.stations = list(deepcopy(_stations))

class TdlpackTrailerRecord(object):
    """
    Defines a TDLPACK Trailer Record.
    """
    counter = 0
    def __init__(self, **kwargs):
        """
        `pytdlpack.TdlpackTrailerRecord` Constructor
        """
        type(self).counter += 0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        strings = []
        keys = self.__dict__.keys()
        for k in keys:
            if not k.startswith('_'):
                strings.append('%s = %s\n'%(k,self.__dict__[k]))
        return ''.join(strings)

    def pack(self):
        pass

    def unpack(self):
        pass
    
def open(name, mode='r', format=None, ra_template=None):
    """
    Opens a TDLPACK File for reading/writing.

    Parameters
    ----------
    **`name : str`**

    TDLPACK file name.  This string is expanded into an absolute path via os.path.abspath().

    **`mode : {'r', 'w', 'a', 'x'}, optional`**

    Access mode. `'r'` means read only; `'w'` means write (existing file is overwritten);
    `'a'` means to append to the existing file; `'x'` means to write to a new file (if
    the file exists, an error is raised).

    **`format : {'sequential', 'random-access'}, optional`**

    Type of TDLPACK File when creating a new file.  This parameter is ignored if the
    file access mode is `'r'` or `'a'`.

    **`ra_template : {'small', 'large'}, optional`**

    Template used to create new random-access file. The default is 'small'.  This parameter
    is ignored if the file access mode is `'r'` or `'a'` or if the file format is `'sequential'`.
    
    Returns
    -------
    **`pytdlpack.TdlpackFile`**

    Instance of class TdlpackFile.
    """
    _byteorder = np.int32(0)
    _filetype = np.int32(0)
    _lun = np.int32(0)
    _ier = np.int32(0)
    name = os.path.abspath(name)

    if format is None: format = 'sequential'
    if mode == 'w' or mode == 'x':

        if format == 'random-access':
            if not ra_template: ra_template = 'small'
            if ra_template == 'small':
                _maxent = np.int32(300)
                _nbytes = np.int32(2000)
            elif ra_template == 'large':
                _maxent = np.int32(840)
                _nbytes = np.int32(20000)
            _filetype = np.int32(1)
            _lun,_byteorder,_filetype,_ier = tdlpack.openfile(FORTRAN_STDOUT_LUN,name,mode,L3264B,_byteorder,_filetype,
                                             ra_maxent=_maxent,ra_nbytes=_nbytes)
        elif format == 'sequential':
            _filetype = np.int32(2)
            _lun,_byteorder,_filetype,_ier = tdlpack.openfile(FORTRAN_STDOUT_LUN,name,mode,L3264B,_byteorder,_filetype)

    elif mode == 'r' or mode == 'a':
        if os.path.isfile(name):
            _lun,_byteorder,_filetype,_ier = tdlpack.openfile(FORTRAN_STDOUT_LUN,name,mode,L3264B,_byteorder,_filetype)
        else:
            raise IOError("File not found.")

    if _ier == 0:
        kwargs = {}
        if _byteorder == -1:
            kwargs['byte_order'] = '<'
        elif _byteorder == 1:
            kwargs['byte_order'] = '>'
        if _filetype == 1:
            kwargs['format'] = 'random-access'
            kwargs['ra_master_key'] = _read_ra_master_key(name)
        elif _filetype == 2:
            kwargs['format'] = 'sequential'
        kwargs['fortran_lun'] = deepcopy(_lun)
        kwargs['mode'] = mode
        kwargs['name'] = name
        kwargs['position'] = np.int32(0)
        if mode == 'r' or mode == 'a': kwargs['size'] = os.path.getsize(name)
    else:
        raise IOError("Could not open TDLPACK file"+name+". Error return from tdlpack.openfile = "+str(_ier))

    _starecdict[_lun] = []

    return TdlpackFile(**kwargs)

def create_grid_definition(name=None,proj=None,nx=None,ny=None,latll=None,lonll=None,
                           orientlon=None,stdlat=None,meshlength=None):
    """
    Create a dictionary of grid specs.  The user has the option to 
    populate the dictionary via the args or create an empty dict. 

    Parameters
    ----------

    **`name : str, optional`**

    String that identifies a predefined grid.

    **`proj : int, optional`**

    Map projection of the grid (3 = Lambert Conformal; 5 = Polar Stereographic; 
    7 = Mercator). NOTE: This parameter is optional if data are station-based.

    **`nx : int, optional`**

    Number of points in X-direction (East-West). NOTE: This parameter is optional if
    data are station-based. 

    **`ny : int, optional`**

    Number of points in Y-direction (North-South). NOTE: This parameter is optional if
    data are station-based.

    **`latll : float, optional`**

    Latitude in decimal degrees of lower-left grid point.  NOTE: This parameter is optional if
    data are station-based.

    **`lonll : float, optional`**

    Longitude in decimal degrees of lower-left grid point.  NOTE: This parameter is optional if
    data are station-based. 

    **`orientlon : float, optional`**

    Longitude in decimal degrees of the central meridian.  NOTE: This parameter is optional if
    data are station-based.

    **`stdlat : float, optional`**

    Latitude in decimal degrees of the standard latitude.  NOTE: This parameter is optional if
    data are station-based.

    **`meshlength : float, optional`**

    Distance in meters between grid points.  NOTE: This parameter is optional if
    data are station-based.

    Returns
    -------

    **`griddict : dict`**

    Dictionary whose keys are the named parameters of this function.
    """
    griddict = {}
    if name is not None:
        from ._grid_definitions import grids
        griddict = grids[name]
    else:
        griddict['proj'] = proj
        griddict['nx'] = nx
        griddict['ny'] = ny
        griddict['latll'] = latll
        griddict['lonll'] = lonll
        griddict['orientlon'] = orientlon
        griddict['stdlat'] = stdlat
        griddict['meshlength'] = meshlength
    return griddict

def _create_proj_string(griddict):
    """
    Returns a string that defines a pyproj.Proj map projection.  If pyproj is not availale,
    then None is returned.

    Parameters
    ----------

    **`griddict : dict`**

    Dictionary of TDLPACK grid definition parameters

    Returns
    -------

    **`str`**    

    String containing the pyproj.Proj definition generating by pyproj.Proj.definition_string().
    """
    try:
        import pyproj
        if griddict['proj'] == 3:
            p = pyproj.Proj(proj='lcc',
                            lat_1=griddict['stdlat'],
                            lat_2=griddict['stdlat'],
                            lon_0=(360.-griddict['orientlon']))
            x,y = p(360.0-griddict['lonll'],griddict['latll'])
            try: 
                projstring = p.definition_string().replace('x_0=0','x_0='+str(x)).replace('y_0=0','y_0='+str(y))
            except(AttributeError):
                projstring = None
        elif griddict['proj'] == 5:
            p = pyproj.Proj(proj='stere',
                            lat_0=90.0,
                            lat_ts=griddict['stdlat'],
                            lon_0=(360.-griddict['orientlon']))
            x,y = p(360.0-griddict['lonll'],griddict['latll'])
            try: 
                projstring = p.definition_string().replace('x_0=0','x_0='+str(x)).replace('y_0=0','y_0='+str(y))
            except(AttributeError):
                projstring = None
        elif griddict['proj'] == 7:
            p = pyproj.Proj(proj='merc',
                            lat_ts=griddict['stdlat'],
                            lon_0=(360.-griddict['orientlon']))
            x,y = p(360.0-griddict['lonll'],griddict['latll'])
            try: 
                projstring = p.definition_string().replace('x_0=0','x_0='+str(x)).replace('y_0=0','y_0='+str(y))
            except(AttributeError):
                projstring = None
        else:
            projstring = None
    except(ImportError):
        projstring = None
    return projstring

def _read_ra_master_key(file):
    """
    Reads the master key record of TDLPACK Random-Access files.

    Parameters
    ----------

    **`file : str`**

    Distance in meters between grid points.  NOTE: This parameter is optional if
    data are station-based.

    Returns
    -------

    **`array`**    
    """
    f = builtins.open(file,'rb')
    raw = f.read(24)
    f.close()
    return np.fromstring(raw,dtype='>i4')
