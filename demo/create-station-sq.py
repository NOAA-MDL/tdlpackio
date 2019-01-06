#!/usr/bin/env python

# ---------------------------------------------------------------------------------------- 
# Import modules
# ---------------------------------------------------------------------------------------- 
import pytdlpack
import numpy as np

# ---------------------------------------------------------------------------------------- 
# Open new TDLPACK file. Here we use pytdlpack.open() which is a function that returns
# an instance (i.e. an object) of class pytdlpack.TdlpackFile.
# ---------------------------------------------------------------------------------------- 
f = pytdlpack.open("station.sq",mode="w")
print "TDLPACK FILE INFO"
print f

# ---------------------------------------------------------------------------------------- 
# Define a station list and create an instance of TdlpackStationRecord
# ---------------------------------------------------------------------------------------- 
ccall = ('KBWI','KPHL','KIAD','KLNS','KACY') # Parentheses indictates a tuple (can also be a list).
stationrec = pytdlpack.TdlpackStationRecord(ccall=ccall) # All that is needed a station call letter list/tuple.
stationrec.pack() # pack() is a method (i.e. a function that acts on a class instance).
f.write(stationrec) # write() is a method of class TdlpackFile.

# ---------------------------------------------------------------------------------------- 
# Define TDLPACK Identification Sections
#
# NOTE: The pytdlpack module contains constansts to use!  -- Like ND7
# ---------------------------------------------------------------------------------------- 
is1 = np.zeros((pytdlpack.ND7),dtype=np.int32)
is1[0] = 0 
is1[1] = 0
is1[2] = 2018
is1[3] = 1
is1[4] = 2
is1[5] = 12
is1[6] = 0
is1[7] = 2018010212
is1[8] = 702000000
is1[9] = 0
is1[10] = 0
is1[11] = 0
is1[12] = 0
is1[13] = 0
is1[14] = 0
is1[15] = 0
is1[16] = 0
is1[17] = 0
is1[18] = 0
is1[19] = 0
is1[20] = 0
is1[21] = 32
plain = "OBS TEMPERATURE"
is2 = np.zeros((pytdlpack.ND7),dtype=np.int32) # Leave is2 empty since we are not packing a gridded record.
is4 = np.zeros((pytdlpack.ND7),dtype=np.int32)
is4[0] = 0
is4[1] = 0
is4[2] = stationrec.number_of_stations
is4[3] = np.int32(9999)
is4[4] = np.int32(0)

# ---------------------------------------------------------------------------------------- 
# Create some fake temperture-like data and create an instance of TdlpackRecord where all
# is* arrays are passed in, along with plain and data.
#
# NOTE: is0 is not passed as this section is created by the system.
# ---------------------------------------------------------------------------------------- 
data = np.array([65.4,59.2,68.0,66.1,9999.0],dtype=np.float32)
temprec = pytdlpack.TdlpackRecord(is1=is1,is2=is2,is4=is4,plain=plain,data=data)
temprec.pack() # The temperature data has now been packed.
f.write(temprec) # The packed temperature record has been written to file.

# ---------------------------------------------------------------------------------------- 
# Close the TDLPACK file.
# ---------------------------------------------------------------------------------------- 
f.close()

# ----------------------------------------------------------------------------------------
# Re-open file.
# ----------------------------------------------------------------------------------------
del f
f = pytdlpack.open("station.sq",mode="r")
recs = f.read(all=True)
print recs
f.close()
