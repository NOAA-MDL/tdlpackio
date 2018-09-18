__version__ = '0.1.0'

import copy
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

r"""TDLPACK-related Constants
======================== =============== ==============================================
Name                     Value           Description
------------------------ --------------- ----------------------------------------------
_default_l3264b          32              Integer word size in bits
_default_minpk           14              Minimum group size when packing
_default_nd5             5242880         Size of IPACK array in 4-byte units (20MB)
_default_nd7             54              Size of TDLPACK Indentification Section Arrays
"""
_default_l3264b = 32 
_default_minpk = 14
_default_nd5 = 5242880
_default_nd7 = 54
_ier = 0
_lx = 0
_misspx = 0
_misssx = 0
_nplain = 32
_iwork = np.zeros((_default_nd5),dtype=np.int32,order='F')
_is0 = np.zeros((_default_nd7),dtype=np.int32,order='F')
_is1 = np.zeros((_default_nd7),dtype=np.int32,order='F')
_is2 = np.zeros((_default_nd7),dtype=np.int32,order='F')
_is4 = np.zeros((_default_nd7),dtype=np.int32,order='F')

global _l3264b
global _minpk
global _nd5
global _nd7
_l3264b = _default_l3264b
_minpk = _default_minpk
_nd5 = _default_nd5
_nd7 = _default_nd7

# ---------------------------------------------------------------------------------------- 
# Class: TdlpackFile
# ---------------------------------------------------------------------------------------- 
class TdlpackFile(object):
    """
    Definition of TdlpackFile which defines a file object for TDLPACK files. Methods 
    defined for this class are read, write, and close. Each method is a "wrapper" function
    to a Fortran subroutine.
    """
    def __init__(self, **kwargs):
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

    def close(self):
        """
        Close a TDLPACK Sequential File. This method calls a Fortran subroutine
        _tdlpack.closefile() to close the lun and set to -1.
        """
        ret = _tdlpack.closefile(self.lun)
        self.lun = -1
        self.current_record = 0
        self.IOStatus = 'closed'

    def read(self):
        """
        Read a record from a TDLPACK file. This method will call Fortran subroutine
        _tdlpack.readfile and has the capability to instantiate and return an instance
        of three types of objects.

        Returns
        -------
        out : {TdlpackRecord, TdlpackTrailer, or TdlpackStations}
        """
        # Initialize kwargs
        kwargs = {}

        # Read record from file
        ipack, ioctet, ier = _tdlpack.readfile(self.lun,_nd5,_l3264b)

        # Error return of -1 signal EOF, so close the file.
        if ier == -1: self.close()

        # Update number of records read.
        self.current_record += 1

        # Set ipack and ioctet
        kwargs['ioctet'] = np.copy(ioctet)
        kwargs['ipack'] = np.copy(ipack)

        # Handle IPACK array accordingly.
        if ipack[0] > 0:
            header = struct.unpack('>4s',ipack[0].byteswap())[0]
            if header == 'TDLP':
                # TDLPACK Record
                kwargs['reference_date'] = np.copy(ipack[4])
                kwargs['id'] = np.copy(ipack[5:9])
                return TdlpackRecord(**kwargs)
            else:
                # Station Call Letter Record
                return TdlpackStations(**kwargs)
        elif ioctet == 24 and ipack[4] == 9999:
            # Trailer Record
            return TdlpackTrailer(**kwargs)

    def write(self, record):
        """
        Write a TDLPACK record to file.

        This method will call Fortran subroutine _tdlpack.writefile to write a packed
        record to file.

        Parameters
        ----------
        record : {TdlpackStations, TdlpackRecord, or TdlpackTrailer}
        """
        ier = 0
        ntotby = np.int32(0)
        ntotrc = np.int32(0)
        if record is None:
            pass
        elif type(record) is TdlpackStations:
            # Pack stations, then write to output file
            record.pack()
            ier = _tdlpack.writefile(self.lun,_l3264b,record.ioctet,record.ipack)
            if ier != 0: raise IOError("Error writing Station Call Letter record to TDLPACK file.")
        elif type(record) is TdlpackRecord:
            # Write to output file
            nwords = record.ioctet*8/_l3264b
            _tdlpack.writep(6,self.lun,record.ipack[0:nwords],ntotby,ntotrc,_l3264b,ier)
            if ier != 0: raise IOError("Error writing TDLPACK record to TDLPACK file")
        elif type(record) is TdlpackTrailer:
            # Write trailer record
            _tdlpack.trail(6,self.lun,_l3264b,np.int32(64/_l3264b),ntotby,ntotrc,ier)
            if ier != 0: raise IOError("Error writing Trailer record to TDLPACK file")
        else:
            # Raise error
            raise TypeError("Record is not Tdlpack-based.")
 
# ---------------------------------------------------------------------------------------- 
# Class TdlpackRecord
# ---------------------------------------------------------------------------------------- 
class TdlpackRecord(object):
    """
    Definition of TdlpackRecord which defines a data object for TDLPACK data. Methods
    defined for this class are unpack and pack. Each method is a "wrapper" function to a
    Fortran subroutine.

    Attributes
    ----------
    datatype : str
        TDLPACK data type ('grid' or 'vector').
    is0 : numpy.ndarray
        TDLPACK Section 0 (Indicator Section).
    is1 : numpy.ndarray
        TDLPACK Section 1 (Product Definition Section).
    is2 : numpy.ndarray
        TDLPACK Section 2 (Grid Definition Section). [If datatype='grid']
    is4 : numpy.ndarray
        TDLPACK Section 4 (Data Section).
    llLat : np.float32
        Lower-left latitude.
    llLon : np.float32
        Lower-left longitude.
    mapProj : str
        Map projection (using basemap projection strings).
    meshLength : np.float32
        Gridpoint spacing in meters.
    nx : int
        Number of gridpoints in the x-direction.
    ny : int
        Number of gridpoints in the y-direction.
    orientLon : np.float32
        Orientation longitude.
    plain : str
        Plain Language description of data.
    stdLat: np.float32
        Standard latitude.
    """
    def __init__(self, **kwargs):
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

    # Class Method: pack handles packing a TDLPACK record
    def pack(self):
        """
        Pack contents of object TdlpackRecord using _tdlpack.pack1d() for vector data
        (i.e. stations) or _tdlpack.pack2d() for gridded data.
        """
        # Initialize
        ier = 0
        ioctet = 0
        xmissp = np.float32(self.primaryMissingValue)
        xmisss = np.float32(self.secondaryMissingValue)
        ipack = np.zeros((_nd5),dtype=np.int32,order='F')
        
        # "Pack" Plain Langauge into self.is1[ ].
        self.is1[21] = _nplain
        for n,s in enumerate(self.plain):
            self.is1[22+n] = ord(s)

        # Pack data using TDLPACK pack1d or pack2d accordingly.
        self.is4[:] = np.int32(0)
        if self.datatype == "vector":
            ic = np.zeros((self.nsta),dtype=np.int32)
            ioctet,ier = _tdlpack.pack1d(6,self.data,ic,self.is0,self.is1,self.is2,self.is4,xmissp,xmisss,ipack,_minpk,_lx,_l3264b)
        elif self.datatype == "grid":
            ia = np.zeros((self.nx,self.ny),dtype=np.int32,order='F')
            ic = np.zeros((self.nx*self.ny),dtype=np.int32,order='F') 
            ioctet,ier = _tdlpack.pack2d(6,self.data,ia,ic,self.is0,self.is1,self.is2,self.is4,xmissp,xmisss,ipack,_minpk,_lx,_l3264b)

        # Here we want to put copies of ipack and ioctet into the TDLPACK object.
        self.ipack = np.copy(ipack)
        self.ioctet = ioctet

        # Since we have packed data, delete data from object
        if self.data is not None: del self.data

    # Class Method: unpack handles unpacking a TDLPACK record
    def unpack(self, unpack_data = True):
        """
        Unpack a packed TDLPACK Record using _tdlpack.unpack()

        Parameters
        ----------
        unpack_data : bool, optional
            Determine whether to unpack data or just TDLPACK sections (Default True). 
        """
        # Unpack TDLPACK record.
        igive = 2
        if unpack_data is False: igive = 1
        _data,ier = _tdlpack.unpack(6,self.ipack,_iwork,_is0,_is1,_is2,_is4,_misspx,_misssx,igive,_l3264b) 

        # Set object is0 and other class vars.
        self.is0 = np.copy(_is0) 
        self.TdlpackSize = np.copy(_is0[1])
        self.TdlpackVersion = np.copy(_is0[2])
        
        # Set object is1 and other class vars.
        self.is1 = np.copy(_is1)
        self.year = np.copy(_is1[2])
        self.month = np.copy(_is1[3])
        self.day = np.copy(_is1[4])
        self.hour = np.copy(_is1[5])
        self.leadTime = np.copy(_is1[12])
        self.modelNumber = np.copy(_is1[14])
        self.modelSequenceNumber = np.copy(_is1[15])
        self.decimalScaleFactor = np.copy(_is1[16])
        self.binaryScaleFactor = np.copy(_is1[17])
        self.lengthPlainLanguage = np.copy(_is1[21])

        # Set Plain language
        self.plain = ''
        for n in np.nditer(self.is1[22:(22+self.is1[21])]):
            self.plain += chr(n)
        
        # Set is2 object vars according to datatype.
        self.is2 = np.copy(_is2) 
        if self.is1[1] == 0:
            self.datatype = 'vector'
            self.is2[:] = 0
        elif self.is1[1] == 1:
            self.datatype = 'grid'
            if self.is2[1] == 3:
               self.basemapProj = 'lcc'
               self.mapProjNumber = 3
            if self.is2[1] == 5:
               self.basemapProj='npstere'
               self.mapProjNumber = 5
            if self.is2[1] == 7:
               self.basemapProj='merc'
               self.mapProjNumber = 7
            self.nx = self.is2[2]
            self.ny = self.is2[3]
            self.lowerLeftLatitude = self.is2[4]/10000.
            self.lowerLeftLongitude = self.is2[5]/10000.
            self.orientationLongitude = self.is2[6]/10000.
            self.meshLength = self.is2[7]/1000000.
            self.standardLatitude = self.is2[8]/10000.

        # Set is4 object var and other relating to packing
        self.is4 = np.copy(_is4) 
        if self.is4[1]&8 == 0:
            self.packingMethod = 'simplePacking'
        elif self.is4[1]&8 == 8:
            if self.is4[1]&4 == 0:
                self.packingMethod = 'complexPacking'
            elif self.is4[1]&4 == 4:
                self.packingMethod = 'complexPackingWithSecondOrderSpatialDifferencing'
        if self.is4[1]&2 == 0:
            self.isPrimaryMissingValuePresent = False
        elif self.is4[1]&2 == 2:
            self.isPrimaryMissingValuePresent = True
        if self.is4[1]&1 == 0:
            self.isSecondaryMissingValuePresent = False
        elif self.is4[1]&1 == 1:
            self.isSecondaryMissingValuePresent = True
        self.numberOfValuesPacked = np.int32(self.is4[2])
        if self.datatype == 'vector': self.nsta = np.int32(self.is4[2])
        self.primaryMissingValue = np.float32(self.is4[3])
        self.secondaryMissingValue = np.float32(self.is4[4])

        # Trim/reshape data values array -- 1D for vector; 2D for grid.
        if igive == 2:
           self.overallMinimumValue = np.float32(self.is4[5])
           self.numberOfGroupsPacked = np.int32(self.is4[6])
           if self.datatype == 'vector':
               self.data = np.copy(_data[0:self.is4[2]])
           elif self.datatype == 'grid':
               self.data = _tdlpack.xfer1d2d(self.nx,self.ny,_data[0:self.is4[2]])

# ---------------------------------------------------------------------------------------- 
# Class TdlpackStations
# ---------------------------------------------------------------------------------------- 
class TdlpackStations(object):
    """
    Definition of TdlpackStations which defines a TDLPACK Station Call Letter record.
    The first 4 bytes of this record contain the number of stations in bytes 
    (number of stations * 8 bytes) then a stream of bytes representing the Station Call
    Letters.  The width of each station call letter is 8 characters (bytes).
    """
    def __init__(self, **kwargs):
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
        Pack a Station Call Letter Record. Following procedures in the mos2k software
        system, the station call letter records are "packed" into an integer array
        with word size of _l3264b bits.
        """
        # Station Call Letter Record
        self.ioctet = self.nsta*8
        self.ipack = np.ndarray((self.ioctet/(_l3264b/8)),dtype=np.int32,order='F')

        # Unpack Station Call Letters
        for n,c in enumerate(self.ccall):
            sta = c.ljust(8,' ')
            self.ipack[n*2] = np.copy(np.fromstring(sta[0:4],dtype=np.int32).byteswap())
            self.ipack[(n*2)+1] = np.copy(np.fromstring(sta[4:8],dtype=np.int32).byteswap())

    def unpack(self):
        """
        Unpack a Station Call Letter Record. The integer array, ipack, returned from
        pytdlpack.TdlpackFile.read() function is "unpacked" into strings with a width
        of 8 characters into a tuple.
        """
        # Station Call Letter Record
        self.nsta = self.ioctet/8
        self.ccall = []

        # Unpack Station Call Letters
        for n in range(0,(self.ioctet/4),2):
           self.ccall.append(struct.unpack('>8s',self.ipack[n:n+2].byteswap())[0].strip(' '))
        self.ccall = tuple(self.ccall)
        
# ---------------------------------------------------------------------------------------- 
# Class TdlpackTrailer
# ---------------------------------------------------------------------------------------- 
class TdlpackTrailer(object):
    """
    Definition of TdlpackTrailer which defines a TDLPACK trailer record.  This record is
    used only in TDLPACK sequential files and either is the last record in a vector
    dataset or when there are multiple Station Call Letter records, will preceed the
    station call letter record.
    """
    def __init__(self, **kwargs):
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

# ---------------------------------------------------------------------------------------- 
# Function open: Call _tdlpack.openfile (Fortran)
# ---------------------------------------------------------------------------------------- 
def open(filename, mode="r"):
    """
    Open a TDLPACK Sequential File.

    Parameters
    ----------
    filename : str
        TDLPACK Filename
    mode : { 'r' or 'w'}, optional
        File IO mode (default 'r'). 
            - 'r' : Read only access
            - 'w' : Read and write access

    Returns
    -------
    TdlpackFile : TdlpackFile
        Instance of class TdlpackFile
    """
    kwargs = {}
    filename = os.path.abspath(filename)
    _lun, byteorder, filetype = _tdlpack.openfile(filename, mode)
    kwargs['mode'] = mode
    kwargs['lun'] = _lun
    kwargs['name'] = filename
    kwargs['current_record'] = 0
    if mode == "r": kwargs['IOStatus'] = 'opened, read-only'
    if mode == "w": kwargs['IOStatus'] = 'opened, new file for write'
    if byteorder == -1: kwargs['byteorder'] = 'little'
    if byteorder == 1: kwargs['byteorder'] = 'big'
    if filetype == 1: kwargs['filetype'] = 'random-access'
    if filetype == 2: kwargs['filetype'] = 'sequential'
    
    return TdlpackFile(**kwargs)

# ---------------------------------------------------------------------------------------- 
# Function set_packingoptions: Set some parameters that would affect packing.
# ---------------------------------------------------------------------------------------- 
def set_packingoptions(minpk=None):
    """
    Set printing options.
    These options determine the way data are packed into TDLPACK format.

    Parameters
    ----------
    minpk : int, optional
        Minimum number of values in a group (default 14). Methods for changing this value
        should be the following formula: (minpk/2) + minpk.
    """
    global _minpk
    if minpk is not None:
        _minpk = minpk

# ---------------------------------------------------------------------------------------- 
# End of pytdlpack.py
# ---------------------------------------------------------------------------------------- 
