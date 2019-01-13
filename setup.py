# ---------------------------------------------------------------------------------------- 
# Import modules
# ---------------------------------------------------------------------------------------- 
from numpy.distutils.core import setup, Extension
import glob
import os
import sys

# ---------------------------------------------------------------------------------------- 
# Build pytdlpack
# ---------------------------------------------------------------------------------------- 
if __name__ == "__main__":

    # Define Fortran compiler flags for GNU and Intel Fortran
    if "build" in sys.argv:
        if "--fcompiler=gnu95" in sys.argv:
            f77_flags = ["-O3",
                         "-g",
                         "-fbacktrace",
                         "-fd-lines-as-comments",
                         "-ffixed-form",
                         "-fautomatic",
                         "-finit-integer=0",
                         "-finit-real=zero",
                         "-finit-logical=false"]
            f90_flags = ["-O3",
                         "-g",
                         "-fbacktrace",
                         "-fautomatic",
                         "-finit-integer=0",
                         "-finit-real=zero",
                         "-finit-logical=false"]
        elif "--fcompiler=intelem" in sys.argv:
            f77_flags = ["-O3",
                         "-g",
                         "-traceback",
                         "-nofree",
                         "-integer-size 32",
                         "-real-size 32",
                         "-auto",
                         "-fpscomp logicals",
                         "-fp-model strict",
                         "-assume byterecl",
                         "-xHost",
                         "-align array64byte",
                         "-fast-transcendentals",
                         "-assume buffered_io"]
            f90_flags = ["-O3",
                         "-g",
                         "-traceback",
                         "-integer-size 32",
                         "-real-size 32",
                         "-auto",
                         "-fpscomp logicals",
                         "-fp-model strict",
                         "-assume byterecl",
                         "-xHost",
                         "-align array64byte",
                         "-fast-transcendentals",
                         "-assume buffered_io"]
    else:
        f77_flags = []
        f90_flags = []

    # Define Extension object. For Fortran 77 source files, use "extra_f77_compile_args".
    # For Fortran 90+ source files, use "extra_f90_compile_args".
    f77_sources = glob.glob("tdlpack/*.f")
    f90_sources = glob.glob("tdlpack/*.f90")
    all_sources = ["tdlpack/_tdlpack.pyf"]+f77_sources+f90_sources
    ext = Extension(name  = '_tdlpack',
                    sources = all_sources,
                    extra_f77_compile_args = f77_flags,
                    extra_f90_compile_args = f90_flags
                    )

    # Run setup
    setup(name = 'pytdlpack',
          author           = "Eric Engle",
          author_email     = "eric.engle@mac.com",
          url              = "https://github.com/eengl/pytdlpack",
          download_url     = "https://github.com/eengl/pytdlpack/releases",
          version          = "0.9.0",
          description      = "Python interface for reading and writing TDLPACK data",
          license          = 'GPL-3.0',
          install_requires = ['numpy'],
          ext_modules      = [ext],
          packages         = ['pytdlpack'],
          )