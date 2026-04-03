from ctypes.util import find_library as ctypes_find_library
from pathlib import Path
from setuptools import setup, Extension
import numpy
import os
import platform
import subprocess
import sys
import sysconfig
import warnings

# This maps package names to library names used in the library filename.
pkgname_to_libname = {
    'tdlpack': ['tdlpack'],
}


def check_lib_static(name):
    """Check whether or not to build with a static library."""
    bval = False
    env_var_name = name.upper()+'_STATIC'
    if os.environ.get(env_var_name):
        val = os.environ.get(env_var_name)
        if val not in {'True','False'}:
            raise ValueError('Environment variable {env_var_name} must be \'True\' or \'False\'')
        bval = True if val == 'True' else False
    return bval


def get_tdlpackio_version():
    """Get the tdlpackion version string."""
    with open("VERSION","rt") as f:
        ver = f.readline().strip()
    return ver


def get_package_info(name, static=False, required=True, include_file=None):
    """Get package information."""
    # First try to get package information from env vars
    pkg_dir = os.environ.get(name.upper()+'_DIR')
    pkg_incdir = os.environ.get(name.upper()+'_INCDIR')
    pkg_libdir = os.environ.get(name.upper()+'_LIBDIR')

    # Return if include and lib dir env vars were set.
    if name in {'tdlpack'}:
        if pkg_incdir is not None and pkg_libdir is not None:
            libname = pkgname_to_libname[name][0]
            return libname, pkg_incdir, pkg_libdir

    if pkg_dir is not None:
        if name in {'tdlpack'}:
            libname = pkgname_to_libname[name][0]
            libpath = find_library(libname, dirs=[pkg_dir], static=static, required=required)
            pkg_libdir = os.path.dirname(libpath)
            incfile = find_include_file(include_file, root=pkg_dir)
            pkg_incdir = os.path.dirname(incfile)
    else:
        # No env vars set, now find everything.
        libnames = pkgname_to_libname[name] if name in pkgname_to_libname.keys() else [name]
        for l in libnames:
            libpath = find_library(l, static=static, required=required)
            if libpath is not None: break
        libname = l
        if libpath is None:
            pkg_libdir = None
            pkg_incdir = None
        else:
            pkg_libdir = os.path.dirname(libpath)
            pkg_incdir = os.path.join(os.path.dirname(pkg_libdir),'include')
            if include_file is not None:
                incfile = find_include_file(include_file, root=os.path.dirname(pkg_libdir))
                if incfile is not None:
                    pkg_incdir = os.path.dirname(incfile)

    return libname, pkg_incdir, pkg_libdir


def find_include_file(file, root=None):
    """Find absolute path to include file."""
    incfile = None
    if root is None:
        return None
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name == file:
                incfile = os.path.join(path, name)
                break
    return incfile


def find_library(name, dirs=None, static=False, required=True):
    """Find absolute path to library file."""
    _libext_by_platform = {"linux": ".so", "darwin": ".dylib"}
    out = []

    # According to the ctypes documentation Mac and Windows ctypes_find_library
    # returns the full path.
    #
    # IMPORTANT: The following does not work at this time (Jan. 2024) for macOS on
    # Apple Silicon.
    if (os.name, sys.platform) != ("posix", "linux"):
        if (sys.platform, platform.machine()) == ("darwin", "arm64"):
            pass
        else:
            out.append(ctypes_find_library(name))

    # For Linux and macOS (Apple Silicon), we have to search ourselves.
    libext = _libext_by_platform[sys.platform]
    if static: libext = '.a'
    if dirs is None:
        if os.environ.get("CONDA_PREFIX"):
            dirs = [os.environ["CONDA_PREFIX"]]
        else:
            dirs = ["/usr", "/usr/local", "/opt/local", "/opt/homebrew", "/opt", "/sw"]
    if os.environ.get("LD_LIBRARY_PATH"):
        dirs = dirs + os.environ.get("LD_LIBRARY_PATH").split(":")

    out = []
    for d in dirs:
        libs = Path(d).rglob(f"lib{name}{libext}")
        out.extend(libs)
    if not out:
        if required:
            raise ValueError(f"""

The library "lib{name}{libext}" could not be found in any of the following
directories:
{dirs}

""")
        else:
            return None
    return out[0].absolute().resolve().as_posix()


def run_ar_command(filename):
    """Run the ar command"""
    cmd = subprocess.run(['ar','-t',filename],
                         stdout=subprocess.PIPE)
    cmdout = cmd.stdout.decode('utf-8')
    return cmdout


def run_nm_command(filename):
    """Run the nm command"""
    cmd = subprocess.run(['nm',filename],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    cmdout = cmd.stdout.decode('utf-8')
    return cmdout


def run_ldd_command(filename):
    """Run the ldd command"""
    cmd = subprocess.run(['ldd',filename],
                         stdout=subprocess.PIPE)
    cmdout = cmd.stdout.decode('utf-8')
    return cmdout


def run_otool_command(filename):
    """Run the otool command"""
    cmd = subprocess.run(['otool','-L',filename],
                         stdout=subprocess.PIPE)
    cmdout = cmd.stdout.decode('utf-8')
    return cmdout


def check_ip_for_openmp(ip_lib, static=False):
    """Check for OpenMP in NCEPLIBS-ip"""
    check = False
    is_apple_clang = False
    info = ''
    libname = ''
    ftnname = None

    # Special check for macOS, based on C compiler to be
    # used here.
    if sys.platform == 'darwin':
        try:
            is_apple_clang = 'clang' in os.environ['CC']
        except(KeyError):
            is_apple_clang = 'clang' in sysconfig.get_config_vars().get('CC')
        
    if static:
        if sys.platform in {'darwin','linux'}:
            info = run_nm_command(ip_lib)
            if 'GOMP' in info:
                check = True
                libname = 'gomp'
                ftnname = 'gfortran'
            elif 'kmpc' in info:
                check = True
                libname = 'iomp5'
                ftnname = 'ifcore'
    else:
        if sys.platform == 'darwin':
            info = run_otool_command(ip_lib)
        elif sys.platform == 'linux':
            info = run_ldd_command(ip_lib)
        if 'gomp' in info:
            check = True
            libname = 'gomp'
            ftnname = 'gfortran'
        elif 'iomp5' in info:
            check = True
            libname = 'iomp5'
            ftnname = 'ifcore'
        elif 'omp' in info:
            check = True
            libname = 'omp'
            ftnname = 'gfortran'

    # Final adjustment is macOS and clang.
    if sys.platform == 'darwin' and is_apple_clang:
        check = True
        libname = 'omp'

    return check, libname, ftnname

# ----------------------------------------------------------------------------------------
# Main part of setup.py
# ----------------------------------------------------------------------------------------
VERSION = get_tdlpackio_version()

#build_with_ip = True
build_with_openmp = False

extmod_config = {}
extension_modules = []
all_extra_objects = []

# ----------------------------------------------------------------------------------------
# Build Cython sources
# ----------------------------------------------------------------------------------------
from Cython.Distutils import build_ext
cmdclass = {'build_ext': build_ext}
tdlpacklib_pyx  = 'src/ext/tdlpacklib.pyx'
#openmp_pyx = 'src/ext/openmp_handler.pyx'

# ----------------------------------------------------------------------------------------
# Get libtdlpack information (THIS IS REQUIRED)
# ----------------------------------------------------------------------------------------
tdlpack_static = check_lib_static('tdlpack')
pkginfo = get_package_info('tdlpack', static=tdlpack_static, required=True, include_file="tdlpack.h")
if None in pkginfo:
    raise ValueError(f"libtdlpack library not found. tdlpackio will not build.")

extmod_config['tdlpacklib'] = dict(libraries=[pkginfo[0]],
                               incdirs=[pkginfo[1]],
                               libdirs=[pkginfo[2]],
                               extra_objects=[])

if tdlpack_static:
    staticlib = find_library('tdlpack', dirs=extmod_config['tdlpacklib']['libdirs'], static=True)
    extmod_config['tdlpacklib']['extra_objects'].append(staticlib)
    symbols = run_ar_command(staticlib)

    # Clear out libraries and libdirs when using static libs
    extmod_config['tdlpacklib']['libraries'] = []
    extmod_config['tdlpacklib']['libdirs'] = []

extmod_config['tdlpacklib']['incdirs'].append(numpy.get_include())

# ----------------------------------------------------------------------------------------
# Summary 
# ----------------------------------------------------------------------------------------
print(f'Build with libtdlpack static library: {tdlpack_static}')
print(f'Needs OpenMP: {build_with_openmp}')
for n, c in extmod_config.items():
    print(f'Extension module name: {n}')
    for k, v in c.items():
        if k == 'extra_objects':
            all_extra_objects.extend(v)
        print(f'\t{k}: {v}')

# ----------------------------------------------------------------------------------------
# Define extensions
# ----------------------------------------------------------------------------------------
tdlpacklibext = Extension('tdlpackio.tdlpacklib',
                      [tdlpacklib_pyx],
                      include_dirs = extmod_config['tdlpacklib']['incdirs'],
                      library_dirs = extmod_config['tdlpacklib']['libdirs'],
                      libraries = extmod_config['tdlpacklib']['libraries'],
                      runtime_library_dirs = extmod_config['tdlpacklib']['libdirs'],
                      extra_objects = extmod_config['tdlpacklib']['extra_objects'])
extension_modules.append(tdlpacklibext)

# ----------------------------------------------------------------------------------------
# Create __config__.py
# ----------------------------------------------------------------------------------------
cnt = \
"""# This file is generated by tdlpackio's setup.py
# It contains configuration information when building this package.
tdlpackio_version = '%(tdlpackio_version)s'
tdlpack_static = %(tdlpack_static)s
has_openmp_support = %(has_openmp_support)s
extra_objects = %(extra_objects)s
"""
a = open('src/tdlpackio/__config__.py','w')
cfgdict = {}
cfgdict['tdlpackio_version'] = VERSION
cfgdict['tdlpack_static'] = tdlpack_static
cfgdict['has_openmp_support'] = build_with_openmp
cfgdict['extra_objects'] = all_extra_objects
try:
    a.write(cnt % cfgdict)
finally:
    a.close()

# ----------------------------------------------------------------------------------------
# Import README.md as PyPi long_description
# ----------------------------------------------------------------------------------------
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# ----------------------------------------------------------------------------------------
# Run setup.py.  See pyproject.toml for package metadata.
# ----------------------------------------------------------------------------------------
setup(ext_modules = extension_modules,
      cmdclass = cmdclass,
      long_description = long_description,
      long_description_content_type = 'text/markdown')
