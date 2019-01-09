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
            tdlpack_fortran_args = ["-O3",
                                    "-g",
                                    "-fbacktrace",
                                    "-fd-lines-as-comments",
                                    "-ffixed-form",
                                    "-fautomatic",
                                    "-finit-integer=0",
                                    "-finit-real=zero",
                                    "-finit-logical=false"]
        elif "--fcompiler=intelem" in sys.argv:
            tdlpack_fortran_args = ["-O3",
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
    else:
        tdlpack_fortran_args = []

    # Define Extension object. For Fortran 77 source files, use "extra_f77_compile_args".
    # For Fortran 90+ source files, use "extra_f90_compile_args".
    fortran_sources = glob.glob("tdlpack/*.f")
    ext = Extension(name  = '_tdlpack',
                    sources = ["tdlpack/_tdlpack.pyf"]+glob.glob("tdlpack/*.f"),
                    extra_f77_compile_args = tdlpack_fortran_args
                    )

    # Run setup
    setup(name = 'pytdlpack',
          author            = "Eric Engle",
          author_email      = "eric.engle@mac.com",
          url               = "https://github.com/eengl/pytdlpack",
          download_url      = "https://github.com/eengl/pytdlpack/releases",
          version           = "0.1",
          description       = "Python interface for reading and writing TDLPACK data",
          ext_modules       = [ext],
          py_modules        = ['pytdlpack'],
          )