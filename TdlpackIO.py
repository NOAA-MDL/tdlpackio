import builtins
import numpy as np
import pytdlpack
import struct
import sys

ONE_MB = 1024 ** 3

class open(object):
    def __init__(self,filename,mode='r'):
        """
        Class Constructor

        Parameters
        ----------

        **`filename : str`**

        File name.

        **`mode : str, optional, default = 'r'`**

        File handle mode.  The default is open for reading ('r').
        """
        if mode == 'r' or mode == 'w':
            mode = mode+'b'
        elif mode == 'a':
            mode = 'wb'
        self._file = builtins.open(filename,mode=mode,buffering=ONE_MB)
        self._hasindex = False
        self._index = []
        self.records = 0
        self.recordnumber = 0
        # Perform indexing on read
        if 'r' in mode:
            self._get_index()

    def __iter__(self):
        """
        """
        return self

    def __enter__(self):
        """
        """
        return self

    def __exit__(self,atype,value,traceback):
        """
        """
        self.close()

    def __next__(self):
        """
        """
        if self.recordnumber < len(self._index):
            return self.read(1)[0]
        else:
            raise StopIteration

    def _get_index(self):
        """
        Perform fast indexing of records.
        """
        while True:
            try:
                recdict = {}
                pos = self._file.tell()
                fortran_header = struct.unpack('>i',self._file.read(4))[0]
                if fortran_header >= 44:
                    bytes_to_read = 44
                else:
                    bytes_to_read = fortran_header
                temp = np.frombuffer(self._file.read(bytes_to_read),dtype='>i4')
                _header = struct.unpack('>4s',temp[2])[0].decode()
                if _header == 'PLDT':
                    # This is a TDLPACK data record
                    recdict['size'] = temp[1]
                    recdict['recType'] = 'data'
                    recdict['refDate'] = temp[6]
                    recdict['leadTime'] = int(temp[9]-((temp[9]/1000)*1000))
                    recdict['id1'] = temp[7]
                    recdict['id2'] = temp[8]
                    recdict['id3'] = temp[9]
                    recdict['id4'] = temp[10]
                else:
                    if temp[1] == 24 and temp[6] == 9999:
                        recdict['recType'] = 'trailer'
                        recdict['size'] = temp[1]
                    else:
                        # This is a station ID record
                        recdict['size'] = temp[1]
                        recdict['recType'] = 'station'
                        recdict['id1'] = 400001000
                        recdict['id2'] = 0  
                        recdict['id3'] = 0
                        recdict['id4'] = 0

                # At this point we have successfully identified a TDLPACK record from
                # the file. Increment self.records and position the file pointer to
                # now read the Fortran trailer.
                self.records += 1 # Includes trailer records
                self._file.seek(fortran_header-bytes_to_read,1)
                fortran_trailer = struct.unpack('>i',self._file.read(4))[0]

                # Check Fortran header and trailer for the record.
                if fortran_header != fortran_trailer:
                    raise IOError('Bad Fortran record.')

                # NOTE: The 'offset' key contains the byte position in the file of where
                # data record begins. A value of 12 is added to consider a 4-byte Fortran
                # header, 4-byte "trash", and 4-byte ioctet value (already) stored on index.
                recdict['offset'] = pos+12 # 4-byte header + 4-byte trash + 4-byte ioctet
                self._index.append(recdict)

            except(struct.error):
                self._file.seek(0)
                break

        self._hasindex = True

    def close(self):
        """
        Close the file handle
        """
        self._file.close()

    def read(self,num=None):
        """
        Read num records from the current position.
        """
        recs = []
        if num == 0:
            return recs
        elif num == 1:
            reclist = [self.recordnumber+1]
        elif num > 1:
            reclist = list(range(self.recordnumber+1,self.recordnumber+1+num))
        for n in reclist:
            nn = n-1 # Use this for the self._index referencing
            kwargs = {}
            self.seek(n)
            kwargs['ioctet'] = self._index[nn]['size']
            kwargs['ipack'] = np.frombuffer(self._file.read(self._index[nn]['size']),dtype='>i4')
            if self._index[nn]['recType'] == 'data':
                kwargs['reference_date'] = self._index[nn]['refDate']
                rec = pytdlpack.TdlpackRecord(**kwargs)
                rec.unpack()
                recs.append(rec)
            elif self._index[nn]['recType'] == 'station':
                kwargs['ipack'] = kwargs['ipack'].byteswap()
                rec = pytdlpack.TdlpackStationRecord(**kwargs)
                rec.unpack()
                recs.append(rec)
            elif self._index[nn]['recType'] == 'trailer':
                recs.append(pytdlpack.TdlpackTrailerRecord(**kwargs))
        return recs
    
    def record(self,rec):
        """
        Read the rec-th record.
        """
        if rec <= 0:
            return None
        else:
            self.seek(rec)
            return self.read(1)[0]

    def seek(self,offset):
        """
        Set the position within the file in units of data records.
        """
        if self._hasindex:
            if offset == 0:
                self._file.seek(self._index[offset]['offset'])
                self.recordnumber = offset
            elif offset > 0:
                self._file.seek(self._index[offset-1]['offset'])
                self.recordnumber = offset
    
    def tell(self):
        """
        Return the position in units of records.
        """
        return self.recordnumber