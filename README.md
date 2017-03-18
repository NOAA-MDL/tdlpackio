# pytdlpack

## Introduction

NOAA/NWS Meteorological Development Lab (MDL) produces model output statistics (MOS) for a variety of NOAA/NCEP Numerical Weather Prediction (NWP) models.  MOS is produced via MDL's in-house MOS-2000 (MOS2K) Fortran-based software system.  The MOS2K software system uses a GRIB-like binary data format called TDLPACK.  `pytdlpack` is a Python interface to reading and writing TDLPACK files.

## Motivation

With its rich ecosystem of community supported scientific and numerical computing libraries, Python has become a viable environment to perform production quality work on large datasets.

## TDLPACK Format

The following will attempt to briefly explain the TDLPACK format.  Please read the official documentation [here](https://www.weather.gov/media/mdl/TDL_OfficeNote00-1.pdf).

Before we describe the TDLPACK data format, one first needs to know that a TDLPACK record can be reside in two types of files: Fortran unformatted (variable record length); Fortran direct-access (fixed record length).  In MOS2K world, these are known as sequential and random-access files, respectively.
