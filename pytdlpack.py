#!/usr/bin/env python

# ---------------------------------------------------------------------------------------- 
# Modules
# ---------------------------------------------------------------------------------------- 
import numpy as np
import os
import struct
import sys
import _tdlpack

# ---------------------------------------------------------------------------------------- 
# TDLPACK related parameters
# ---------------------------------------------------------------------------------------- 
_l3264b = 32   # Bit size of integer "words"
_nd5 = 5242880 # Max size of IPACK, 20MB record in 4-byte units
_nd7 = 54      # Size of IS() array

# ---------------------------------------------------------------------------------------- 
# Scalars and Arrays for TDLPACK unpacking/packing
# ---------------------------------------------------------------------------------------- 
_ier = 0
_lx = 0
_minpk = 14
_misspx = 0
_misssx = 0
_nplain = 32
_iwork = np.zeros((_nd5),dtype=np.int32,order='F')
_is0 = np.zeros((_nd7),dtype=np.int32,order='F')
_is1 = np.zeros((_nd7),dtype=np.int32,order='F')
_is2 = np.zeros((_nd7),dtype=np.int32,order='F')
_is4 = np.zeros((_nd7),dtype=np.int32,order='F')
_data = np.zeros((_nd5),dtype=np.float32,order='F')

# ---------------------------------------------------------------------------------------- 
# Function: unpackStations
# ---------------------------------------------------------------------------------------- 
def unpackStations(ipack, ioctet):
    """ Returns a TDLPACK station call letter record from integer-based IPACK
        array.  Note that the integer word size is 4-bytes, so an 8-character CALL letter
        will be split into 2 IPACK words. Whitespace is removed from from each station
        call letter.

        Definition:
        unpackStations(ipack, ioctet) -> nsta, ccall

        Arguments:
        ipack -- IPACK array.
        ioctet -- Size of IPACK array in bytes.

        Returns:
        nsta -- number of stations in record.
        ccall -- list of stations.
    """
    # Station Call Letter Record
    nsta = ioctet/8
    ccall = []

    # Unpack Station Call Letters
    for n in range(0,(ioctet/4),2):
       ccall.append(struct.unpack('>8s',ipack[n:n+2].byteswap())[0].strip(' '))
    ccall = tuple(ccall) 

    return nsta, ccall

# ----------------------------------------------------------------------------------------
# Function: packStations
# ----------------------------------------------------------------------------------------
def packStations(ccall, nsta):
    """ Returns a packed station call letter record from a list of station call letter
        records.  Whitespace is added to each station call letter such that the length
        is 8-characters.

        Definition:
        packStations(ccall, nsta) -> ioctet, ipack

        Arguments:
        ccall -- list of stations.
        nsta -- number of stations in record.

        Returns:
        ioctet -- Size of IPACK array in bytes. NOTE: This is a long (i.e. 64-bits).
        ipack -- IPACK array.
    """
    # Station Call Letter Record
    ioctet = nsta*8
    ipack = np.ndarray((ioctet/4),dtype=np.int32,order="F")

    # Unpack Station Call Letters
    for n,c in enumerate(ccall):
        i1 = n*2
        i2 = i1+1
        sta = c.ljust(8,' ')
        ipack[i1] = np.copy(np.fromstring(sta[0:4],dtype=np.int32).byteswap())
        ipack[i2] = np.copy(np.fromstring(sta[4:8],dtype=np.int32).byteswap())

    return long(ioctet), ipack

# ---------------------------------------------------------------------------------------- 
# Class: TdlpackFile
# ---------------------------------------------------------------------------------------- 
class TdlpackFile(object):
    """ Class of TdlpackFile

        This class defines a file object for TDLPACK files.  Methods defined for this
        class are read, write, and close.  Each method is a "wrapper" function to a
        Fortran subroutine.

        Attributes:
            byteorder (str): Byte order (endianness) of the TDLPACK file.
            current_record (int): The current record read in the file.
            filetype (str): Type of TDLPACK file ('random-access' or 'sequential').
            lun (int): Fortran logical unit number.
            mode (str): File IO mode ('a', 'r', or 'w').
            name (str): File name (absolute file path).
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
        """ Close a TDLPACK Sequential File.

            This method calls a Fortran subroutine _tdlpack.closefile() to close
            the lun and set to -1.
        """
        ret = _tdlpack.closefile(self.lun)
        self.lun = -1
        self.current_record = 0
        self.IOStatus = 'closed'

    def read(self):
       """ Read a record from a TDLPACK file.

           This method will call Fortran subroutine _tdlpack.readfile and has the 
           capability to instantiate and return 3 types of objects depending on 
           what is read:

               TdlpackRecord
               TdlpackTrailer
               TdlpackStations
       """

       # Initialize kwargs
       kwargs = {}

       # Read record from file
       ipack, ioctet, ier = _tdlpack.readfile(self.lun,_nd5)

       # Error return of -1 signal EOF, so close the file.
       if ier == -1: self.close()

       # Update number of records read.
       self.current_record += 1

       # Handle IPACK array accordingly.
       if ipack[0] > 0:
           header = struct.unpack('>4s',ipack[0].byteswap())[0]
           if header == 'TDLP':
               # TDLPACK Record
               kwargs['ipack'] = np.copy(ipack)
               kwargs['reference_date'] = np.copy(ipack[4])
               kwargs['id'] = np.copy(ipack[5:9])
               kwargs['ioctet'] = ioctet
               return TdlpackRecord(**kwargs)
           else:
               nsta, ccall = unpackStations(ipack,ioctet)
               kwargs['nsta'] = nsta
               kwargs['ccall'] = ccall
               return TdlpackStations(**kwargs)
       elif ioctet == 24 and ipack[4] == 9999:
           kwargs['ioctet'] = ioctet
           kwargs['ipack'] = np.copy(ipack)
           return TdlpackTrailer(**kwargs)

    def write(self, record):
        """ Write a TDLPACK record to file.

            This method will call Fortran subroutine _tdlpack.writefile to write a packed
            record to file.

            Arguments:
            record -- packed record of type TdlpackStations, TdlpackRecord, or
                      TdlpackTrailer
        """
        if record is None:
            pass
        elif type(record) is TdlpackStations:
            # Pack stations, then write to output
            ioctet, ipack = packStations(record.ccall,record.nsta)
            ier = _tdlpack.writefile(self.lun,ioctet,ipack)
            if ier != 0: raise IOError("Error writing to TDLPACK file.")
        elif type(record) is TdlpackRecord or type(record) is TdlpackTrailer:
            # Write to output
            ier = 0
            ier = _tdlpack.writefile(self.lun,record.ioctet,record.ipack)
            if ier != 0: raise IOError("Error writing to TDLPACK file")
        else:
            # Raise error
            raise TypeError("Record is not Tdlpack-based.")
 
# ---------------------------------------------------------------------------------------- 
# Class TdlpackRecord
# ---------------------------------------------------------------------------------------- 
class TdlpackRecord(object):
    """ Class of TdlpackRecord

        This class defines a data object for TDLPACK data.  Methods defined for this
        class are unpack and pack.  Each method is a "wrapper" function to a
        Fortran subroutine.

        Attributes:
            datatype (str): TDLPACK data type ('grid' or 'vector').
            is0 (numpy.ndarray): TDLPACK Section 0 (Indicator Section).
            is1 (numpy.ndarray): TDLPACK Section 1 (Product Definition Section).
            is2 (numpy.ndarray): TDLPACK Section 2 (Grid Definition Section). [If datatype='grid']
            is4 (numpy.ndarray): TDLPACK Section 4 (Data Section).
            llLat (float): Lower-left latitude.
            llLon (float): Lower-left longitude.
            mapProj (str): Map projection (using basemap projection strings).
            meshLength (float): Gridpoint spacing in meters.
            nx (int): Number of gridpoints in the x-direction.
            ny (int): Number of gridpoints in the y-direction.
            orientLon (float): Orientation longitude.
            plain (string): Plain Language description of data.
            stdLat (float): Standard latitude.
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
        """ Pack TDLPACK Record using _tdlpack.pack1d() and _tdlpack.pack2d() """

        # Initialize
        ier = 0
        ioctet = 0
        xmissp = self.primaryMissingValue
        xmisss = self.secondaryMissingValue
        ipack = np.zeros((_nd5),dtype=np.int32,order='F')
        
        # "Pack" Plain Langauge into self.is1[ ].
        self.is1[21] = _nplain
        for n,s in enumerate(self.plain):
            self.is1[22+n] = ord(s)

        # Pack data using TDLPACK pack1d or pack2d accordingly.
        if self.datatype == "vector":
            ic = np.zeros((self.nsta),dtype=np.int32)
            _tdlpack.pack1d(6,self.data,ic,self.is0,self.is1,self.is2,self.is4,xmissp,xmisss,ipack,_minpk,_lx,ioctet,\
                            _l3264b,ier)
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
        """ Unpack TDLPACK Record using _tdlpack.unpack() """

        igive = 2
        if unpack_data is False: igive = 1

        _tdlpack.unpack(6,self.ipack,_iwork,_data,_is0,_is1,_is2,_is4,_misspx,_misssx,igive,_l3264b,_ier) 

        self.is0 = np.copy(_is0) 
        self.is1 = np.copy(_is1) 
        self.is2 = np.copy(_is2) 
        self.is4 = np.copy(_is4) 

        if self.is1[1] == 0:
            self.datatype = 'vector'
        elif self.is1[1] == 1:
            self.datatype = 'grid'
            if self.is2[1] == 3: self.mapProj='lcc'
            if self.is2[1] == 5: self.mapProj='npstere'
            if self.is2[1] == 7: self.mapProj='merc'
            self.nx = self.is2[2]
            self.ny = self.is2[3]
            self.llLat = self.is2[4]/10000.
            self.llLon = self.is2[5]/10000.
            self.orientLon = self.is2[6]/10000.
            self.meshLength = self.is2[7]/1000000.
            self.stdLat = self.is2[8]/10000.

        # Plain language
        self.plain = ''
        for n in np.nditer(self.is1[22:(22+self.is1[21])]):
            self.plain += chr(n)

        # Trim/reshape data values array -- 1D for vector; 2D for grid.
        if igive == 2:
           if self.is1[1] == 0:
               self.data = np.copy(_data[0:self.is4[2]])
           elif self.is1[1] == 1:
               self.data = np.copy(np.reshape(_data[0:self.is4[2]],(self.nx,self.ny,),order='F'))

        # Define the missing values
        self.primaryMissingValue = float(self.is4[3])
        self.secondaryMissingValue = float(self.is4[4])

        # Return values
        #return data

    values = property(unpack)

# ---------------------------------------------------------------------------------------- 
# Class TdlpackStations
# ---------------------------------------------------------------------------------------- 
class TdlpackStations(object):

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
        
# ---------------------------------------------------------------------------------------- 
# Class TdlpackTrailer
# ---------------------------------------------------------------------------------------- 
class TdlpackTrailer(object):

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

# ---------------------------------------------------------------------------------------- 
# Function open: Call _tdlpack.openfile (Fortran)
# ---------------------------------------------------------------------------------------- 
def open(filename, mode="r"):
    """ Opens a TDLPACK Sequential File """
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
# End of pytdlpack.py
# ---------------------------------------------------------------------------------------- 
