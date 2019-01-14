"""
Version 0.9.0
-------------
- - -

Introduction
============

pytdlpack is a Python interface to reading/writing TDLPACK files.

TDLPACK is a GRIB-like binary data format that is exclusive to MOS-2000 (MOS2K)
Fortran-based sofftware system.  This software system was developed at the 
Meteorological Development Laboratory (MDL) within NOAA/NWS and its primary purpose is
to perform statistical post-processing of meteorological data.

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

Download
========

- Latest code from [github repository](https://github.com/eengl/pytdlpack).
- Latest [releases](https://pypi.python.org/pypi/pytdlpack) (source code and binary installers).

Requires
========

- Python 2.7 (Python 3 support coming soon!).
- [numpy array module](http://numpy.scipy.org), version 1.8.0 or later.
- [setuptools](https://pypi.python.org/pypi/setuptools), version 18.0 or later.
- Fortran compiler (if installing from source). ***Only GNU (gfortran) and Intel (ifort) are supported at this time.***

Install
=======

Tutorial
========

1. [Creating/Opening/Closing a TDLPACK file.](#section1)
2. [Reading a TDLPACK file.](#section2)
3. [Writing a TDLPACK file.](#section3)
4. [Creating a TDLPACK Station Record.](#section4)
5. [Creating a TDLPACK Record.](#section5)

## <div id='section1'>1) Creating/Opening/Closing a TDLPACK file.

To create a TDLPACK file from Python, you call the `pytdlpack.open` function and provide the
file name and `mode='w' or 'a'`.  For `mode='a'`, this will append to an existing file.  When 
creating a new file, the default file format is `'sequential'`, but the user can also specify 
the format with `format='sequential' or 'random-access'`.  If the new file is random-access, 
then the user can also specify `ra_template='small' or 'large'`.  The default is 'small'.

Example: Create a new sequential file:

    :::python
    >>> import pytdlpack
    >>> f = pytdlpack.open('test.sq',mode='w')

Example: Create a new random-access file:

    :::python
    >>> import pytdlpack
    >>> f = pytdlpack.open('test.sq',mode='w',format='random-access',ra_template='small')

To open an existing TDLPACK file, the user only need to provide the file name.

    :::python
    import pytdlpack
    >>> f = pytdlpack.open('test.sq')
    >>> type(f)
    <class 'pytdlpack._pytdlpack.TdlpackFile'>
    >>> print f
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

To close a TDLPACK file is straightforward.

    :::python
    >>> f.close()

## <div id='section2'>2) Reading a TDLPACK file.

Once a TDLPACK file has been opened, an instance of class `pytdlpack.TdlpackFile` has 
been created.  To read a record the file, use the class method `pytdlpack.TdlpackFile.read`.  
By default only 1 record is returned and the TDLPACK indentification sections are unpacked.

Example: Reading a gridded TDLPACK record.

    :::python
    >>> x = f.read()
    >>> print x
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

You can also configure the `pytdlpack.TdlpackFile.read` to read the entire file with

    :::python
    >>> x = f.read(all=True)

Here, x will become a list of instances of either `pytdlpack.TdlpackStationRecord`, 
`pytdlpack.TdlpackRecord`, or `pytdlpack.TdlpackTrailerRecord`.

If the file being read is `format='random-access'`, then you can also provide the `id=` 
argument to search for a specific record.

    :::python
    >>> import pytdlpack
    >>> f = pytdlpack.open('test.ra')
    >>> x = f.read(id=[400001000,0,0,0])
    >>> type(x)
    <class 'pytdlpack._pytdlpack.TdlpackStationRecord'

## <div id='section3'>3) Writing a TDLPACK file.

Writing to a TDLPACK file is as easy as reading.  The following that the variable, x, 
is an instance of `pytdlpack.TdlpackRecord` that has been packed.

Example: Write to a new TDLPACK sequential file.

    :::python
    >>> import pytdlpack
    >>> f.open("new.sq",mode="w",format="sequential")
    >>> f.write(x)
    >>> f.close()

## <div id='section4'>4) Creating a TDLPACK Station Record.

The constructor for `pytdlpack.TdlpackStationRecord` provides two methods of
instantiation via the traditional **kwargs (see `pytdlpack.TdlpackStationRecord.__init__`) 
or simply providing `ccall = ...` ***(recommended)***.  The value passed to the `ccall=` argument can
be a single call letter string, list, tuple, or comma-delimited string of station call letter records.

    :::python
    >>> import pytdlpack
    >>> stations = pytdlpack.TdlpackStationRecord(ccall=['KBWI','KDCA','KIAD'])
    >>> print stations
    ccall = ('KBWI', 'KDCA', 'KIAD')
    id = [400001000         0         0         0]
    ioctet = 0
    ipack = []
    number_of_stations = 3

## <div id='section5'>5) Creating a TDLPACK Record.

The recommended method for creating a `pytdlpack.TdlpackRecord` is to pass the TDLPACK 
indentification arrays, plain language string, and data to the approproiate keyword.

    :::python
    >>> import numpy as np
    >>> import pytdlpack
    >>> is1 = np.int32(...)
    >>> is2 = np.int32(...)
    >>> is4 = np.int32(...)
    >>> plain = "..."
    >>> data = np.float32(...)
    >>> record = pytdlpack.TdlpackRecord(is1=is1,is2=is2,is4=is4,plain=plain,data=data)

The user is encouraged to read the official MOS-2000 documentation on construction of 
these arrays and proper encoding.

"""
__version__ = '0.9.0'

from copy import deepcopy
from itertools import count

import __builtin__
import os
import struct
import sys

try:
    import numpy as np
except ImportError:
    raise ImportError("NumPy required")
try:
    import _tdlpack
except ImportError:
    raise ImportError("_tdlpack not found.")

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
ND5_META = np.int32(32)
ND7 = _DEFAULT_ND7
NBYPWD = np.int32(L3264B/8)

_ccall = []
_ier = np.int32(0)
_lx = np.int32(0)
_misspx = np.int32(0)
_misssx = np.int32(0)
_is0 = np.zeros((ND7),dtype=np.int32)
_is1 = np.zeros((ND7),dtype=np.int32)
_is2 = np.zeros((ND7),dtype=np.int32)
_is4 = np.zeros((ND7),dtype=np.int32)
_iwork_meta = np.zeros((ND5_META),dtype=np.int32)
_data_meta = np.zeros((ND5_META),dtype=np.int32)

_ier = _tdlpack.openlog(FORTRAN_STDOUT_LUN,os.devnull)
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
        keys.sort()
        for k in keys:
            if not k.startswith('_'):
                strings.append('%s = %s\n'%(k,self.__dict__[k]))
        return ''.join(strings)
    
    def _determine_record_type(self,ipack,ioctet):
        kwargs = {}
        if ipack[0] > 0:
            kwargs['ipack'] = deepcopy(ipack)
            kwargs['ioctet'] = deepcopy(ioctet)
            if ioctet == 24 and ipack[4] == 9999:
                kwargs ['id'] = np.int32([0,0,0,0])
                return TdlpackTrailerRecord(**kwargs)
            if struct.unpack('>4s',ipack[0].byteswap())[0] == "TDLP":
                if not self.data_type: self.data_type = 'grid'
                kwargs['id'] = deepcopy(ipack[5:9])
                kwargs['reference_date'] = deepcopy(ipack[4])
                return TdlpackRecord(**kwargs)
            else:
                if not self.data_type: self.data_type = 'station'
                kwargs['id'] = np.int32([400001000,0,0,0])
                kwargs['number_of_stations'] = deepcopy(ioctet/NCHAR)
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
            _ier = _tdlpack.backspacefile(self.fortran_lun)
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
            _ier = _tdlpack.clfilm(FORTRAN_STDOUT_LUN,self.fortran_lun)
        elif self.format == 'sequential':
            _ier = _tdlpack.closefile(FORTRAN_STDOUT_LUN,self.fortran_lun,np.int32(2))
        if _ier == 0:
            self.eof = False
            self.fortran_lun = -1
            self.position = 0
            type(self).counter -= 1
        else:
            raise IOError("Trouble closing file. ier = "+str(_ier))
    
    def read(self,all=False,unpack=True,id=None):
        """
        Read a record from a TDLPACK file.

        Parameters
        ----------
        all : bool, optional
            Read all records from file. The default is False.
        unpack : bool, optional
            Unpack TDLPACK identification sections.  Note that data are not unpacked.  The default is True.
        id : array_like or list, optional
            Provide an ID to search for. This can be either a Numpy.int32 array with shape (4,) or list 
            with length 4.
        
        Returns
        -------
        TdlpackStationRecord, TdlpackRecord, TdlpackTrailerRecord, or None
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
                if id is None:
                    id = np.int32([9999,0,0,0])
                else:
                    id = np.int32(id)
                _nvalue = np.int32(0)
                _ipack,_nvalue,_ier = _tdlpack.rdtdlm(FORTRAN_STDOUT_LUN,self.fortran_lun,self.name,id,ND5,L3264B)
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
                _ioctet,_ipack,_ier = _tdlpack.readfile(FORTRAN_STDOUT_LUN,self.name,self.fortran_lun,ND5,L3264B,np.int32(2))
                if _ier == 0:
                    record = self._determine_record_type(_ipack,_ioctet)
                elif _ier == -1:
                    self.eof = True
                    break
            if unpack: record.unpack()
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
            _ier = _tdlpack.rewindfile(self.fortran_lun)
            if _ier == 0:
                self.position = 0
            else:
                raise IOError("Could not rewind file. ier = "+str(_ier))

    def write(self,record):
        """
        Write a packed TDLPACK record to file.
        """
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
                _ier = _tdlpack.wrtdlm(FORTRAN_STDOUT_LUN,self.fortran_lun,self.name,
                                       record.id,record.ipack[0:_nwords],_nreplace,
                                       _ncheck,L3264B)
            elif self.format == 'sequential':
                _ntotby,_ntotrc,_ier = _tdlpack.writep(FORTRAN_STDOUT_LUN,self.fortran_lun,
                                       record.ipack[0:_nwords],_ntotby,_ntotrc,L3264B)
        elif type(record) is TdlpackRecord:
            if self.position == 0: self.data_type = 'grid'
            _nwords = np.int32(record.ioctet/NBYPWD)
            if self.format == 'random-access':
                record.ipack[0] = record.ipack[0].byteswap()
                _ier = _tdlpack.wrtdlm(FORTRAN_STDOUT_LUN,self.fortran_lun,self.name,
                                       record.id,record.ipack[0:_nwords],_nreplace,
                                       _ncheck,L3264B)
            elif self.format == 'sequential':
                _tdlpack.writep(FORTRAN_STDOUT_LUN,self.fortran_lun,record.ipack[0:_nwords],
                                _ntotby,_ntotrc,L3264B,_ier)
        elif type(record) is TdlpackTrailerRecord:
            _ier = _tdlpack.trail(FORTRAN_STDOUT_LUN,self.fortran_lun,L3264B,L3264W,_ntotby,
                           _ntotrc)
        if _ier == 0:
            self.position += 1
            self.size = os.path.getsize(self.name)

class TdlpackRecord(object):
    """
    Defines a TDLPACK data record object.

    Attributes
    ----------
    data : array_like
        Data values.
    grid_length : float
        Distance between grid points in units of meters.
    id : array_like
        ID of the TDLPACK data record. This is a NumPy 1D array of dtype=np.int32.
    ioctet : int
        Size of the packed TDLPACK data record in bytes.
    ipack : array_like
        Packed TDLPACK data record. This is a NumPy 1D array of dtype=np.int32.
    is0 : array_like
        TDLPACK Section 0 (Indicator Section).
    is1 : array_like
        TDLPACK Section 1 (Product Definition Section).
    is2 : array_like
        TDLPACK Section 2 (Grid Definition Section)
    is4 : array_like
        TDLPACK Section 4 (Data Section).
    lead_time : int
        Forecast lead time in units of hours.
    lower_left_latitude : float
        Latitude of lower left grid point
    lower_left_longitude : float
        Longitude of lower left grid point
    number_of_values : int
        Number of data values.
    nx : int
        Number of points in the x-direction (West-East).
    ny : int
        Number of points in the y-direction (West-East).
    origin_longitude : float
        Originating longitude of projected grid.
    plain : str
        Plain language description of TDLPACK record.
    primary_missing_value : float
        Primary missing value.
    reference_date : int
        Reference date from the TDLPACK data record in YYYYMMDDHH format.
    secondary_missing_value : float
        Secondary missing value.
    standard_latitude : float
        Latitude at which the grid length applies.
    type : {'grid', 'station'}
        Identifies the type of data. 
    """
    counter = 0
    def __init__(self,is1=None,is2=None,is4=None,plain=None,data=None,**kwargs):
        """
        Constructor

        Parameters
        ----------
        is1 : array_like, optional
            TDLPACK Identification Section 1 (Product Definition Section).
        is2 : array_like, optional
            TDLPACK Identification Section 2 (Grid Definition Section).
        is4 : array_like, optional
            TDLPACK Identification Section 4 (Data Section).
        plain : str, optional
            Plain language descriptor.
        data : array_like, optional
            Data values.
        **kwargs : dict, optional
            Dictionary of class attributes (keys) and class attributes (values).
        """
        type(self).counter += 1
        self._metadata_unpacked = False
        self._data_unpacked = False
        self.nx = None
        self.ny = None
        self.plain = ''
        if np.any(is1) and np.any(is4) and plain and np.any(data) and len(kwargs) == 0:
            kwargs = {}
            kwargs['is0'] = np.zeros((ND7),dtype=np.int32)
            kwargs['is1'] = is1.astype(np.int32)
            kwargs['is2'] = is2.astype(np.int32)
            kwargs['is4'] = is4.astype(np.int32)
            kwargs['id'] = np.int32(is1[8:12])
            kwargs['plain'] = plain
            kwargs['data'] = data.astype(np.float32)
            kwargs['_metadata_unpacked'] = True
            kwargs['_data_unpacked'] = True
        for k,v in kwargs.items():
            setattr(self,k,v)
        if self._metadata_unpacked: self.unpack()

    def __repr__(self):
        strings = []
        keys = self.__dict__.keys()
        keys.sort()
        for k in keys:
            if not k.startswith('_'):
                strings.append('%s = %s\n'%(k,self.__dict__[k]))
        return ''.join(strings)
    
    def pack(self):
        """
        Pack a TDLPACK record.
        """
        _ier = np.int32(0)
        self.ipack = np.zeros((ND5),dtype=np.int32)
        if self.type == 'grid':
            _a = np.zeros((self.nx,self.ny),dtype=np.float32,order='F')
            _ia = np.zeros((self.nx,self.ny),dtype=np.int32,order='F')
            _ic = np.zeros((self.nx*self.ny),dtype=np.int32)
            self.ioctet,_ier = _tdlpack.pack2d(FORTRAN_STDOUT_LUN,self.data,_ia,_ic,self.is0,
                               self.is1,self.is2,self.is4,self.primary_missing_value,
                               self.secondary_missing_value,self.ipack,MINPK,_lx,L3264B)
        elif self.type == 'station':
            _ic = np.zeros((self.number_of_values),dtype=np.int32)
            self.ioctet,_ier = _tdlpack.pack1d(FORTRAN_STDOUT_LUN,self.data,_ic,self.is0,
                               self.is1,self.is2,self.is4,self.primary_missing_value,
                               self.secondary_missing_value,self.ipack,MINPK,
                               _lx,L3264B)
    
    def unpack(self,data=False,missing_value=None):
        """
        Unpacks the TDLPACK identification sections and data (optional).

        Parameters
        ----------
        data : bool, optional
            If True, unpack data values. The default is False.
        missing_value : float, optional
            Set a missing value. If a missing value exists for the TDLPACK data record,
            it will be replaced with this value.
        """
        _ier = np.int32(0)
        if not self._metadata_unpacked:
            _data_meta,_ier = _tdlpack.unpack(FORTRAN_STDOUT_LUN,self.ipack[0:ND5_META],
                              _iwork_meta,_is0,_is1,_is2,_is4,_misspx,
                              _misssx,np.int32(1),L3264B)
            if _ier == 0:
                self._metadata_unpacked = True
                self.is0 = deepcopy(_is0)
                self.is1 = deepcopy(_is1)
                self.is2 = deepcopy(_is2)
                self.is4 = deepcopy(_is4)

        # Set attributes from is1[].
        self.lead_time = self.is1[10]-((self.is1[10]/1000)*1000)
        if not self.plain:
            for n in np.nditer(self.is1[22:(22+self.is1[21])]):
                self.plain += chr(n)

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
       
        # Set attributes from is4[].
        self.number_of_values = self.is4[2]
        self.primary_missing_value = deepcopy(np.float32(self.is4[3]))
        self.secondary_missing_value = deepcopy(np.float32(self.is4[4]))

        if data:
            self._data_unpacked = True
            _nd5_local = max(self.is4[2],(self.ioctet/NBYPWD))
            _iwork = np.zeros((_nd5_local),dtype=np.int32)
            _data = np.zeros((_nd5_local),dtype=np.float32)
            _data,_ier = _tdlpack.unpack(FORTRAN_STDOUT_LUN,self.ipack[0:_nd5_local],
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
            if self.type == "grid":
                self.data = np.reshape(self.data[0:self.number_of_values],(self.nx,self.ny),order='F')
    
    def grid(self):
        """
        Returns latitudes and lontiude numpy.float32 arrays for the TDLPACK record. 
        If the record is station, then return is None.

        Returns
        -------
        lats,lons : array_like if TdlpackRecord is type = "grid", otherwise None are returned.
        """
        lats = None
        lons = None
        if self.type == 'grid':
            _ier = np.int32(0)
            lats = np.zeros((self.nx,self.ny),dtype=np.float32,order='F')
            lons = np.zeros((self.nx,self.ny),dtype=np.float32,order='F')
            lats,lons,_ier = _tdlpack.gridij_to_latlon(FORTRAN_STDOUT_LUN,self.nx,self.ny,
                             self.map_proj,self.grid_length,self.origin_longitude,
                             self.standard_latitude,self.lower_left_latitude,
                             self.lower_left_longitude)
        return lats,lons

class TdlpackStationRecord(object):
    """
    Defines a TDLPACK Station Call Letter Record.

    Attributes
    ----------
    ccall : tuple
        A tuple of station call letters.
    id : array_like
        ID of station call letters. Note: This id is only used for random-access IO.
    ioctet : int
        Size of station call letter record in bytes.
    ipack : array_like
        Packed station call letter record.
    number_of_stations: int
        Size of station call letter record.
    """
    counter = 0
    def __init__(self,ccall=None,**kwargs):
        """
        Constructor

        Parameters
        ----------
        ccall : list, optional
            A list of station call letter records.
        **kwargs : dict
            Dictionary of class attributes (keys) and class attributes (values).
        """
        type(self).counter += 1
        if ccall is None:
            self.ccall = None
            self.number_of_stations = np.int32(0)
        else:
            self.ccall = tuple(ccall)
            self.number_of_stations = len(self.ccall)
        self.id = np.int32([400001000,0,0,0])
        self.ioctet = np.int32(0)
        self.ipack = np.array((),dtype=np.int32)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        strings = []
        keys = self.__dict__.keys()
        keys.sort()
        for k in keys:
            if not k.startswith('_'):
                strings.append('%s = %s\n'%(k,self.__dict__[k]))
        return ''.join(strings)
    
    def pack(self):
        """
        Pack a Station Call Letter Record.
        """
        self.ioctet = np.int32(self.number_of_stations*NCHAR)
        self.ipack = np.ndarray((self.ioctet/(L3264B/NCHAR)),dtype=np.int32)
        for n,c in enumerate(self.ccall):
            sta = c.ljust(NCHAR,' ')
            self.ipack[n*2] = np.copy(np.fromstring(sta[0:(NCHAR/2)],dtype=np.int32).byteswap())
            self.ipack[(n*2)+1] = np.copy(np.fromstring(sta[(NCHAR/2):NCHAR],dtype=np.int32).byteswap())

    def unpack(self):
        """
        Unpack a Station Call Letter Record.
        """
        _ccall = []
        _unpack_string_fmt = '>'+str(NCHAR)+'s'
        for n in range(0,(self.ioctet/(NCHAR/2)),2):
           _ccall.append(struct.unpack(_unpack_string_fmt,self.ipack[n:n+2].byteswap())[0].strip(' '))
        self.ccall = tuple(deepcopy(_ccall))

class TdlpackTrailerRecord(object):
    """
    Defines a TDLPACK Trailer Record.
    """
    counter = 0
    def __init__(self, **kwargs):
        type(self).counter += 0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        strings = []
        keys = self.__dict__.keys()
        keys.sort()
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

    How to initialize a new random-access file. The default is 'small'.  This parameter
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

    if not format: format == 'sequential'

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
            _lun,_byteorder,_filetype,_ier = _tdlpack.openfile(FORTRAN_STDOUT_LUN,name,mode,L3264B,_byteorder,_filetype,
                                             ra_maxent=_maxent,ra_nbytes=_nbytes)
        elif format == 'sequential':
            _filetype = np.int32(2)
            _lun,_byteorder,_filetype,_ier = _tdlpack.openfile(FORTRAN_STDOUT_LUN,name,mode,L3264B,_byteorder,_filetype)

    elif mode == 'r' or mode == 'a':
        _lun,_byteorder,_filetype,_ier = _tdlpack.openfile(FORTRAN_STDOUT_LUN,name,mode,L3264B,_byteorder,_filetype)

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
        kwargs['size'] = os.path.getsize(name)
    else:
        raise IOError("Could not open TDLPACK file"+name+". Error return from _tdlpack.openfile = "+str(_ier))

    return TdlpackFile(**kwargs)

def _read_ra_master_key(file):
    f = __builtin__.open(file,'rb')
    raw = f.read(24)
    f.close()
    return np.fromstring(raw,dtype='>i4')