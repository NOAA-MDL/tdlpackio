# pytdlpack

## Introduction

NOAA/NWS Meteorological Development Lab (MDL) produces model output statistics (MOS) for a variety of NOAA/NCEP Numerical Weather Prediction (NWP) models.  MOS is produced via MDL's in-house MOS-2000 (MOS2K) Fortran-based software system.  The MOS2K software system uses a GRIB-like binary data format called TDLPACK.  `pytdlpack` is a Python interface to reading and writing TDLPACK files.

## Motivation

Python has a rich ecosystem of community supported scientific and numerical computing libraries and has become a viable environment to perform production quality work on large datasets.

## TDLPACK Files

Before we describe the TDLPACK data format, one first needs to know that a TDLPACK record can be reside in two types of files: Fortran unformatted (variable record length); Fortran direct-access (fixed record length).  In MOS2K world, these are known as sequential and random access files, respectively.

### Sequential Files

This is a Fortran unformatted, variable record length file.  The TDLPACK record is contained within a Fortran record.  The TDLPACK record preceeded by 8-bytes that contains the record length in bytes of the TDLPACK record.  A TDLPACK sequental file can also contain 2 other type of records: station call letter record; trailer record.  Station call letters in MOS2K of of type CHARACTER*8.

Station call letter record is of the following format in bytes:
* 1 - 4: Size of the station call letters in bytes (number of stations * 8)
* 5 - _n_: station call letters

Trailer record is of the following format:
* PUT FORMAT HERE

### Random Access Files

This is a Fortran direct access, fixed record length file.  One can think of these files like a book in that there is a table of contents that point to where specific TDLPACK records exist within the file.  Here, a TDLPACK record is considered a logical record because it can span multiple (Fortran) physical records.  A TDLPACK random access file can also contain a station call letter record and is the same format as discussed above, however, accessing this record is different.

## TDLPACK Format

The following will attempt to briefly explain the TDLPACK format.  Please read the official documentation [here](https://www.weather.gov/media/mdl/TDL_OfficeNote00-1.pdf).  TDLPACK is GRIB-like in that it contains an initial 4-character string to identify the data format "TDLP"; indentification sections (Indicator, Product, and Grid); Data section; and an End Section that contains "7777".  A more detailed description of TDLPACK sections can be found in the chapter 5 of the official documentation.

* Section 0 - Inidictator Section
* Section 1 - Product Definition Section
* Section 2 - Grid Definition Section
* Section 3 - Bitmap Section (technically available, but never supported)
* Section 4 - Data Section
* Section 5 - End Section

A TDLPACK record can contain 2 types of data: vector data (i.e. most likely data at "stations"); 2-D projected gridded data (i.e. data at regularly spaced gridpoints).  TDLPACK only supports the following map projections: Northern Hemispheric Lambert Conformal Conic, Northern Polar Stereograhic, and Mercator.


