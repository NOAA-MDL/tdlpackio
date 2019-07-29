import builtins
import logging
import numpy as np
import pytdlpack
import struct
import sys  
import warnings

import pdb

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
        self._fh = builtins.open(filename,mode=mode,buffering=ONE_MB)
        self._hasindex = False
        self._index = {}
        self.records = 0
        self.recordnumber = 0
        # Perform indexing on read
        if 'r' in mode:
            self._get_index()

    def __enter__(self):
        """
        """
        return self

    def __exit__(self,atype,value,traceback):
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
        if self.recordnumber < self.records:
            return self.read(1)[0]
        else:
            raise StopIteration

    def _get_index(self):
        """
        Perform fast indexing of records.
        """
        self._index['offset'] = []
        self._index['size'] = []
        self._index['type'] = []
        self._index['date'] = []
        self._index['lead'] = []
        self._index['id1'] = []
        self._index['id2'] = []
        self._index['id3'] = []
        self._index['id4'] = []
        self._index['linked_station_id_record'] = []
        _last_station_id_record = 0
        while True:
            try:
                pos = self._fh.tell()
                fortran_header = struct.unpack('>i',self._fh.read(4))[0]
                if fortran_header >= 44:
                    bytes_to_read = 44
                else:
                    bytes_to_read = fortran_header
                temp = np.frombuffer(self._fh.read(bytes_to_read),dtype='>i4')
                _header = struct.unpack('>4s',temp[2])[0].decode()
                if _header == 'PLDT':
                    # This is a TDLPACK data record
                    self._index['size'].append(temp[1])
                    self._index['type'].append('data')
                    self._index['date'].append(temp[6])
                    self._index['lead'].append(int(temp[9]-((temp[9]/1000)*1000)))
                    self._index['id1'].append(temp[7])
                    self._index['id2'].append(temp[8])
                    self._index['id3'].append(temp[9])
                    self._index['id4'].append(temp[10])
                    self._index['linked_station_id_record'].append(_last_station_id_record)
                else:
                    if temp[1] == 24 and temp[6] == 9999:
                        self._index['size'].append(temp[1])
                        self._index['type'].append('trailer')
                        self._index['date'].append(None)
                        self._index['lead'].append(None)
                        self._index['id1'].append(None)
                        self._index['id2'].append(None)
                        self._index['id3'].append(None)
                        self._index['id4'].append(None)
                        self._index['linked_station_id_record'].append(_last_station_id_record)
                    else:
                        # This is a station ID record
                        self._index['size'].append(temp[1])
                        self._index['type'].append('station')
                        self._index['date'].append(None)
                        self._index['lead'].append(None)
                        self._index['id1'].append(400001000)
                        self._index['id2'].append(0)  
                        self._index['id3'].append(0)
                        self._index['id4'].append(0)
                        self._index['linked_station_id_record'].append(_last_station_id_record)

                # At this point we have successfully identified a TDLPACK record from
                # the file. Increment self.records and position the file pointer to
                # now read the Fortran trailer.
                self.records += 1 # Includes trailer records
                self._fh.seek(fortran_header-bytes_to_read,1)
                fortran_trailer = struct.unpack('>i',self._fh.read(4))[0]

                # Check Fortran header and trailer for the record.
                if fortran_header != fortran_trailer:
                    raise IOError('Bad Fortran record.')

                # NOTE: The 'offset' key contains the byte position in the file of where
                # data record begins. A value of 12 is added to consider a 4-byte Fortran
                # header, 4-byte "trash", and 4-byte ioctet value (already) stored on index.
                self._index['offset'].append(pos+12) # 4-byte header + 4-byte trash + 4-byte ioctet

                # Hold the record number of the last station ID record
                if self._index['type'][-1] == 'station':
                    _last_station_id_record = self.records # This should be OK.

            except(struct.error):
                self._fh.seek(0)
                break

        self._hasindex = True

    def close(self):
        """
        Close the file handle
        """
        self._fh.close()

    def read(self,num=None,unpack=True):
        """
        Read num records from the current position.
        """
        #pdb.set_trace()
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
            kwargs['ioctet'] = self._index['size'][nn]
            kwargs['ipack'] = np.frombuffer(self._fh.read(self._index['size'][nn]),dtype='>i4')
            if self._index['type'][nn] == 'data':
                kwargs['reference_date'] = self._index['date'][nn]
                rec = pytdlpack.TdlpackRecord(**kwargs)
                if unpack: rec.unpack()
                recs.append(rec)
            elif self._index['type'][nn] == 'station':
                kwargs['ipack'] = kwargs['ipack'].byteswap()
                rec = pytdlpack.TdlpackStationRecord(**kwargs)
                if unpack: rec.unpack()
                recs.append(rec)
            elif self._index['type'][nn] == 'trailer':
                recs.append(pytdlpack.TdlpackTrailerRecord(**kwargs))
            self.recordnumber = n
        return recs
    
    def record(self,rec,unpack=True):
        """
        Read the N-th record.
        """
        #pdb.set_trace()
        if rec is None:
            return None
        if rec <= 0:
            warnings.warn("Record numbers begin at 1.") 
            return None
        elif rec > self.records:
            warnings.warn("Not that many records in the file.")
            return None
        else:
            self.seek(rec) # Use the actual record number here.
            return self.read(1,unpack=unpack)[0]

    def seek(self,offset):
        """
        Set the position within the file in units of data records.
        """
        if self._hasindex:
            if offset == 0:
                self._fh.seek(self._index['offset'][offset])
                self.recordnumber = offset
            elif offset > 0:
                self._fh.seek(self._index['offset'][offset-1])
                self.recordnumber = offset-1
    
    def tell(self):
        """
        Return the position in units of records.
        """
        return self.recordnumber