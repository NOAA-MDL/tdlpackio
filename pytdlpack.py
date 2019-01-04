__version__ = '0.5.0'

from copy import deepcopy
from itertools import count

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

_DEFAULT_L3264B = np.int32(32)
_DEFAULT_ND5 = np.int32(5242880)
_DEFAULT_ND7 = np.int32(54)

DEFAULT_MISSING_VALUE = np.float32(9999.0)
FORTRAN_STDOUT_LUN = np.int32(6)
L3264B = _DEFAULT_L3264B
NCHAR = np.int32(8)
NCHAR_PLAIN = np.int32(32)
ND5 = _DEFAULT_ND5
ND5_META = np.int32(32)
ND7 = _DEFAULT_ND7
NBYPWD = np.int32(L3264B/8)

_ccall = []
_ier = np.int32(0)
_misspx = np.int32(0)
_misssx = np.int32(0)
_is0 = np.zeros((ND7),dtype=np.int32)
_is1 = np.zeros((ND7),dtype=np.int32)
_is2 = np.zeros((ND7),dtype=np.int32)
_is4 = np.zeros((ND7),dtype=np.int32)
_iwork_meta = np.zeros((ND5_META),dtype=np.int32)
_data_meta = np.zeros((ND5_META),dtype=np.int32)

class TdlpackFile(object):
    """
    TDLPACK File with associated information.

    Attributes
    ----------
    byte_order : str
        Byte order of TDLPACK file using definitions as defined by Python built-in struct module.
    data_type : {'grid', 'station'}
        Type of data contained in the file.
    eof : bool
        True if we have reached end of file.
    format : {'random-access', 'sequential'}
        File format of TDLPACK file.
    fortran_lun : np.int32
        Fortran unit number for file access. If the file is not open, then this value is -1. 
    mode : str
        Access mode (see pytdlpack.open() docstring).
    name : str
        File name.
    position : int
        The current record being read from file. If the file type is 'random-access', then this
        value is -1.
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

    def close(self):
        """
        Close a TDLPACK file.
        """
        _ier = np.int32(0)
        _ier = _tdlpack.closefile(self.fortran_lun)
        if _ier == 0:
            self.eof = False
            self.fortran_lun = -1
            self.position = 0
            type(self).counter -= 1
    
    def read(self,all=False,unpack=True):
        """
        Read a record from a TDLPACK file.

        Parameters
        ----------
        all : bool, optional
            Read all records from file. The default is False.
        unpack : bool, optional
            Unpack TDLPACK identification sections.  Note that data are not unpacked.  The default is True.
        
        Returns
        -------
        TdlpackStationRecord, TdlpackRecord, or TdlpackTrailerRecord
        """
        if all: records = []
        while True:
            _ipack = np.array((),dtype=np.int32)
            _ioctet = np.int32(0)
            _ier = np.int32(0)
            _ipack,_ioctet,_ier = _tdlpack.readfile(self.fortran_lun,ND5,L3264B)
            if _ier == -1:
                self.eof = True
                break
            elif _ier == 0:
                kwargs = {}
                kwargs['ipack'] = deepcopy(_ipack)
                kwargs['ioctet'] = deepcopy(_ioctet)
                if _ipack[0] > 0:
                    if struct.unpack('>4s',_ipack[0].byteswap())[0] == "TDLP":
                        kwargs['id'] = deepcopy(_ipack[5:9])
                        kwargs['reference_date'] = deepcopy(_ipack[4])
                        record = TdlpackRecord(**kwargs)
                        if unpack:
                            record.unpack()
                            if record.is1[1] == 0:
                                if self.position == 0: self.data_type = 'station'
                            elif record.is1[1] == 1:
                                if self.position == 0: self.data_type = 'grid'
                    else:
                        if self.position == 0: self.data_type = 'station'
                        kwargs['number_of_stations'] = deepcopy(_ioctet/NCHAR)
                        record = TdlpackStationRecord(**kwargs)
                        record.unpack()
                elif _ioctet == 24 and _ipack[4] == 9999:
                    return TdlpackTrailerRecord(**kwargs)

                self.position += 1
                if all:
                    records.append(record)
                else:
                    break

        if not self.eof:
            if all:
                return records
            else:
                return record
    
    def write(self,record):
        """
        Write a packed TDLPACK record to file.
        """
        _ier = np.int32(0)
        _ntotby = np.int32(0)
        _ntotrc = np.int32(0)

        if type(record) is TdlpackStationRecord:
            if self.position == 0: self.data_type = 'station'
            _ier = _tdlpack.writefile(self.fortran_lun,L3264B,record.ioctet,record.ipack)
        elif type(record) is TdlpackRecord:
            if self.position == 0: self.data_type = 'grid'
            _nwords = np.int32((record.ioctet*8)/L3264B)
            _tdlpack.writep(FORTRAN_STDOUT_LUN,self.fortran_lun,record.ipack[0:_nwords],_ntotby,_ntotrc,L3264B,_ier)
        elif type(record) is TdlpackTrailerRecord:
            _tdlpack.trail(FORTRAN_STDOUT_LUN,self.fortran_lun,L3264B,np.int32(64/L3264B),_ntotby,_ntotrc,_ier)
        if _ier == 0:
            self.position += 1

class TdlpackRecord(object):
    """
    Defines a TDLPACK data record object.

    Attributes
    ----------
    data : array_like
        Data values.
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
    number_of_values : int
        Number of data values.
    nx : int
        Number of points in the x-direction (West-East).
    ny : int
        Number of points in the y-direction (West-East).
    plain : str
        Plain language description of TDLPACK record.
    primary_missing_value : float
        Primary missing value.
    reference_date : int
        Reference date from the TDLPACK data record in YYYYMMDDHH format.
    secondary_missing_value : float
        Secondary missing value.
    type : {'grid', 'station'}
        Identifies the type of data. 
    """
    counter = 0
    def __init__(self,is1=None,is2=None,is4=None,plain=None,data=None,**kwargs):
        """
        Constructor

        Parameters
        ----------
        is1 : array_like
            TDLPACK Identification Section 1 (Product Definition Section).
        is2 : array_like
            TDLPACK Identification Section 2 (Grid Definition Section).
        is4 : array_like
            TDLPACK Identification Section 4 (Data Section).
        plain : str
            Plain language descriptor.
        data : array_like
            Data values.
        **kwargs : dict
            Dictionary of class attributes (keys) and class attributes (values).
        """
        type(self).counter += 1
        self._metadata_unpacked = False
        self._data_unpacked = False
        self.data = np.array((),dtype=np.float32)
        self.id = np.array((),dtype=np.int32)
        self.ioctet = np.int32(0)
        self.ipack = np.array((),dtype=np.int32)
        self.is0 = np.array((),dtype=np.int32)
        self.is1 = np.array((),dtype=np.int32)
        self.is2 = np.array((),dtype=np.int32)
        self.is4 = np.array((),dtype=np.int32)
        self.lead_time = np.int32(0)
        self.number_of_values = np.int32(0)
        self.nx = None
        self.ny = None
        self.plain = ''
        self.primary_missing_value = np.float32(0)
        self.reference_date = np.int32(0)
        self.secondary_missing_value = np.float32(0)
        self.type = ''
        if is1 is not None:
            self.is0 = np.zeros((ND7),dtype=np.int32)
            self.is1 = np.int32(is1)
            self.id = np.int32(self.is1[8:12])
            self.lead_time = self.is1[10]-((self.is1[10]/1000)*1000)
            self.reference_date = np.int32(self.is1[7])
            if self.is1[1] == 0:
                self.type = 'station'
            elif self.is1[1] == 1:
                self.type = 'grid'
        if is2 is not None:
            self.is2 = np.int32(is2)
            self.nx = self.is2[2]
            self.ny = self.is2[3]
        if is4 is not None:
            self.is4 = np.int32(is4)
            self.number_of_values = np.int32(self.is4[2])
            self.primary_missing_value = np.float32(self.is4[3])
            self.secondary_missing_value = np.float32(self.is4[4])
        if plain is not None:
            self.plain = plain[0:len(plain)]+" "*(NCHAR_PLAIN-len(plain))
            for n,s in enumerate(self.plain):
                self.is1[22+n] = ord(s)
        if data is not None:
            self.data = np.float32(data)
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
        Pack a TDLPACK record.
        """
        _ier = np.int32(0)
        _minpk = np.int32(14)
        _lx = np.int32(0)
        self.ipack = np.zeros((ND5),dtype=np.int32)
        if self.type == 'grid':
            _a = np.zeros((self.nx,self.ny),dtype=np.float32,order="F")
            _ia = np.zeros((self.nx,self.ny),dtype=np.int32,order="F")
            _ic = np.zeros((self.nx*self.ny),dtype=np.int32)
            self.ioctet,_ier = _tdlpack.pack2d(FORTRAN_STDOUT_LUN,self.data,_ia,_ic,self.is0,
                               self.is1,self.is2,self.is4,self.primary_missing_value,
                               self.secondary_missing_value,self.ipack,_minpk,_lx,L3264B)
        elif self.type == 'station':
            _ic = np.zeros((self.number_of_values),dtype=np.int32)
            self.ioctet,_ier = _tdlpack.pack1d(FORTRAN_STDOUT_LUN,self.data,_ic,self.is0,
                               self.is1,self.is2,self.is4,self.primary_missing_value,
                               self.secondary_missing_value,self.ipack,_minpk,
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
        _data_meta,_ier = _tdlpack.unpack(FORTRAN_STDOUT_LUN,self.ipack[0:ND5_META],
                                          _iwork_meta,_is0,_is1,_is2,_is4,_misspx,
                                          _misssx,np.int32(1),L3264B)
        if _ier == 0:
            self._metadata_unpacked = True
            self.is0 = deepcopy(_is0)
            self.is1 = deepcopy(_is1)
            self.is2 = deepcopy(_is2)
            self.is4 = deepcopy(_is4)

            if not self.plain:
                for n in np.nditer(self.is1[22:(22+self.is1[21])]):
                    self.plain += chr(n)

            self.lead_time = self.is1[10]-((self.is1[10]/1000)*1000)
            self.number_of_values = self.is4[2]
            self.primary_missing_value = deepcopy(np.float32(_misspx))
            self.secondary_missing_value = deepcopy(np.float32(_misssx))
            if self.is1[1] == 0:
                self.type = 'station'
            elif self.is1[1] == 1:
                self.type = 'grid'
                self.nx = self.is2[2]
                self.ny = self.is2[3]
        
        if data:
            self._data_unpacked = True
            _nd5_local = max(self.is4[2],(self.ioctet/NBYPWD))
            _iwork = np.zeros((_nd5_local),dtype=np.int32)
            _data = np.zeros((_nd5_local),dtype=np.float32)
            _data,_ier = _tdlpack.unpack(FORTRAN_STDOUT_LUN,self.ipack[0:_nd5_local],_iwork,self.is0,self.is1,self.is2,
                                         self.is4,_misspx,_misssx,np.int32(2),L3264B)
            if _ier == 0:
                _data = deepcopy(_data[0:self.number_of_values+1])
            else:
                _data = np.zeros((self.number_of_values),dtype=np.float32)+DEFAULT_MISSING_VALUE
            self.data = deepcopy(_data[0:self.number_of_values])
            if missing_value is not None:
                self.data = np.where(self.data==self.primary_missing_value,np.float32(missing_value),self.data)
                self.primary_missing_value = np.float32(missing_value)
    
class TdlpackStationRecord(object):
    """
    Defines a TDLPACK Station Call Letter Record.

    Attributes
    ----------
    ccall : tuple
        A tuple of station call letter records.
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
        self.ioctet = self.number_of_stations*NCHAR
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
    
def open(name,mode='r'):
    """
    Open a TDLPACK File.

    Parameters
    ----------
    name : str
        TDLPACK File name.
    mode : {'r', 'w', 'a', 'x'}
        Access mode. 'r' means read only; 'w' means write (existing file is overwritten);
        'a' means to append to the existing file; 'x' means to write to a new file (if
        the file exists, an error is raised).
    
    Returns
    -------
    TdlpackFile
        Instance of class TdlpackFile.
    """
    _byteorder = np.int32(0)
    _filetype = np.int32(0)
    _lun = np.int32(0)
    _ier = np.int32(0)
    _lun,_byteorder,_filetype,_ier = _tdlpack.openfile(os.path.abspath(name),mode)

    kwargs = {}
    if _byteorder == -1:
        kwargs['byte_order'] = '<'
    elif _byteorder == 1:
        kwargs['byte_order'] = '>'
    if _filetype == 1:
        kwargs['format'] = 'random-access'
    elif _filetype == 2:
        kwargs['format'] = 'sequential'
    kwargs['fortran_lun'] = deepcopy(_lun)
    kwargs['mode'] = mode
    kwargs['name'] = os.path.abspath(name)
    kwargs['position'] = np.int32(0)

    return TdlpackFile(**kwargs)