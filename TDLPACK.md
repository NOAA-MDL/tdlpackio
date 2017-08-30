# TDLPACK

## TDLPACK File Types

Before we describe the TDLPACK data format, one first needs to know the different types of files in which a TDLPACK record can be reside in.  There a two file types: Fortran unformatted (variable record length); Fortran direct-access (fixed record length).  In MOS2K world, these are known as sequential and random access files, respectively.

### Sequential Files

This is a Fortran unformatted, variable record length file.  The TDLPACK record is contained within a Fortran record.  The TDLPACK record preceeded by 8-bytes that contains the record length in bytes of the TDLPACK record.  A TDLPACK sequental file can also contain 2 other type of records: station call letter record; trailer record.  Station call letters in MOS2K of of type CHARACTER*8.

Station call letter record is of the following format in bytes:
* 1 - 8: Size of the station call letters in bytes (number of stations * 8)
* 9 - _n_: Station Call Letters

Trailer record is of the following format in bytes:
* 1 - 8: Record length
* 9 - _n_:  Trailer record consisting of date/time information

### Random Access Files

This is a Fortran direct access, fixed record length file.  One can think of these files like a book in that there is a table of contents (i.e. key records) that point to where specific TDLPACK records (i.e. data records) exist within the file.  Also, there exists a Master Key Record at the beginning of the file.  In a Random Access File, a TDLPACK record is considered a logical record because it can span multiple (Fortran) physical records.  A TDLPACK random access file can also contain a station call letter record and is the same format as discussed above, however, accessing this record is different.

## TDLPACK Data Format

The following will attempt to briefly explain the TDLPACK format.  Please read the official documentation [here](https://www.weather.gov/media/mdl/TDL_OfficeNote00-1.pdf).  TDLPACK is a big-endian binary data format and is GRIB-like in that it contains an initial 4-character string to identify the data format "TDLP"; indentification sections (Indicator, Product, and Grid); Data section; and an End Section that contains "7777".  A more detailed description of TDLPACK sections can be found in the chapter 5 of the official documentation.  TDLPACK contains the following sections:

* Section 0 - Indictator Section
* Section 1 - Product Definition Section
* Section 2 - Grid Definition Section (**NOTE**: Not present when data are vector)
* Section 3 - Bitmap Section (defined, but never supported in code)
* Section 4 - Data Section
* Section 5 - End Section

A TDLPACK record can contain 2 types of data: vector data (i.e. most likely data at "stations"); gridded data (i.e. data at regularly spaced projected gridpoints).  TDLPACK only supports the following map projections:

* Lambert Conformal Conic
* Polar Stereograhic
* Mercator

There is no support for geographic grids (i.e. latitude-longitude grids).
