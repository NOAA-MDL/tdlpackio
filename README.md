# pytdlpack

## Introduction

NOAA/NWS Meteorological Development Lab (MDL) produces model output statistics (MOS) for a variety of NOAA/NCEP Numerical Weather Prediction (NWP) models.  MOS is produced via MDL's in-house MOS-2000 (MOS2K) Fortran-based software system.  The MOS2K software system uses a GRIB-like binary data format called TDLPACK.  `pytdlpack` is a Python interface to reading and writing TDLPACK files.

## Motivation

Python has a rich ecosystem of community supported scientific and numerical computing libraries and has become a viable environment to perform production quality work on large datasets.

## TDLPACK Format

The following will attempt to briefly explain the TDLPACK format.  Please read the official documentation [here](https://www.weather.gov/media/mdl/TDL_OfficeNote00-1.pdf).

Before we describe the TDLPACK data format, one first needs to know that a TDLPACK record can be reside in two types of files: Fortran unformatted (variable record length); Fortran direct-access (fixed record length).  In MOS2K world, these are known as sequential and random-access files, respectively.

TDLPACK is GRIB-like in that it contains an initial 4-character string to identify the data format "TDLP"; indentification sections (Indicator, Product, and Grid); Data section; and an End Section that contains "7777".  A more detailed description of TDLPACK sections can be found in the chapter 5 of the official documentation.

* Section 0 - Inidictator Section
* Section 1 - Product Definition Section
* Section 2 - Grid Definition Section
* Section 3 - Bitmap Section (technically available, but never supported)
* Section 4 - Data Section
* Section 5 - End Section

A TDLPACK record can contain 2 types of data: vector data (i.e. most likely data at "stations"); 2-D projected gridded data (i.e. data at regularly spaced gridpoints).  TDLPACK only supports the following map projections: Northern Hemispheric Lambert Conformal Conic, Northern Polar Stereograhic, and Mercator. A bit in 


