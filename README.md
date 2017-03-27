# pytdlpack

## Introduction

NOAA/NWS Meteorological Development Lab ([MDL](https://www.weather.gov/mdl/)) produces model output statistics (MOS) for a variety of NOAA/NCEP Numerical Weather Prediction (NWP) models.  MOS is produced via MDL's in-house MOS-2000 (MOS2K) Fortran-based software system.  MOS2K uses a GRIB-like binary data format called TDLPACK.  `pytdlpack` is a Python interface to reading and writing TDLPACK files.

For a brief introduction to TDLPACK file and data formats, click [here](https://www.github.com/eengl/pytdlpack/TDLPACK.md).

## Motivation

Python has a rich ecosystem of community supported scientific and numerical computing libraries and has become a viable environment to perform production quality work on large datasets.

