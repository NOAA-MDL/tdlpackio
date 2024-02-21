from distutils.cmd import Command
from numpy.distutils.core import setup, Extension
import glob
import numpy
import os
import sys

VERSION = '2.0.0'

# ----------------------------------------------------------------------------------------
# Define Fortran compiler options for supported compilers
# ----------------------------------------------------------------------------------------
gnu_f77_flags = ["-O3",
                 "-g",
                 "-fbacktrace",
                 "-fd-lines-as-comments",
                 "-ffixed-form",
                 "-fautomatic",
                 "-finit-integer=0",
                 "-finit-real=zero",
                 "-finit-logical=false"]
gnu_f90_flags = ["-O3",
                 "-g",
                 "-fbacktrace",
                 "-fautomatic",
                 "-finit-integer=0",
                 "-finit-real=zero",
                 "-finit-logical=false"]
intel_f77_flags = ["-O3",
                   "-g",
                   "-traceback",
                   "-nofree",
                   "-integer-size","32",
                   "-real-size","32",
                   "-auto",
                   "-fpscomp","logicals",
                   "-fp-model=strict",
                   "-assume","byterecl",
                   "-xHost",
                   "-align","array64byte",
                   "-assume","buffered_io"]
intel_f90_flags = ["-O3",
                   "-g",
                   "-traceback",
                   "-integer-size","32",
                   "-real-size","32",
                   "-auto",
                   "-fpscomp","logicals",
                   "-fp-model=strict",
                   "-assume","byterecl",
                   "-xHost",
                   "-align","array64byte",
                   "-assume","buffered_io"]

# ----------------------------------------------------------------------------------------
# Write version info
# ----------------------------------------------------------------------------------------
def write_version_file(filename='src/tdlpackio/version.py'):
    cnt = """
# THIS FILE IS GENERATED FROM PYTDLPACK SETUP.PY
version = '%(version)s'
"""
    a = open(filename,'w')
    try:
        a.write(cnt % {'version': VERSION})
    finally:
        a.close()

# ----------------------------------------------------------------------------------------
# Define Fortran compiler flags for GNU and Intel Fortran
# ----------------------------------------------------------------------------------------
f77_flags = gnu_f77_flags
f90_flags = gnu_f90_flags
try:
    if 'gfortran' in os.environ['FC']:
        f77_flags = gnu_f77_flags
        f90_flags = gnu_f90_flags
    elif 'ifort' in os.environ['FC']:
        f77_flags = intel_f77_flags
        f90_flags = intel_f90_flags
except(KeyError):
    pass # Default to GNU Fortran
if "build" in sys.argv:
    if "--fcompiler=gnu95" in sys.argv:
        f77_flags = gnu_f77_flags
        f90_flags = gnu_f90_flags
    elif "--fcompiler=intelem" in sys.argv:
        f77_flags = intel_f77_flags
        f90_flags = intel_f90_flags

# ----------------------------------------------------------------------------------------
# Define Extension object. For Fortran 77 source files, use "extra_f77_compile_args".
# For Fortran 90+ source files, use "extra_f90_compile_args".
# ----------------------------------------------------------------------------------------
f77_sources = glob.glob("src/ext/tdlpacklib/*.f")
f90_sources = glob.glob("src/ext/tdlpacklib/*.f90")
all_sources = ["src/ext/tdlpacklib/tdlpacklib.pyf"]+f77_sources+f90_sources
ext = Extension(name  = 'tdlpackio.tdlpacklib',
                sources = all_sources,
                include_dirs = [numpy.get_include()],
                extra_f77_compile_args = f77_flags,
                extra_f90_compile_args = f90_flags
                )

# ----------------------------------------------------------------------------------------
# Define testing class
# ----------------------------------------------------------------------------------------
class TestCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys, subprocess
        for f in os.listdir('./test/'):
            raise SystemExit(subprocess.call([sys.executable,'./test/'+f]))

# ----------------------------------------------------------------------------------------
# Rewrite the version file everytime
# ----------------------------------------------------------------------------------------
write_version_file()

# ----------------------------------------------------------------------------------------
# Import README.md as PyPi long_description
# ----------------------------------------------------------------------------------------
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# ----------------------------------------------------------------------------------------
# Run setup
# ----------------------------------------------------------------------------------------
setup(name             = 'tdlpackio',
      version          = VERSION,
      ext_modules      = [ext],
      long_description  = long_description,
      long_description_content_type = 'text/markdown'
)
