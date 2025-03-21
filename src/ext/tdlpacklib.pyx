# cython: language_level=3, boundscheck=False
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
"""
Cython code to provide python interfaces to functions in the libtdlpack library.

IMPORTANT: Make changes to this file, not the C code that Cython generates.
"""

#cimport cython
#from cpython.buffer cimport Py_buffer, PyObject_GetBuffer, PyBuffer_Release, PyBUF_SIMPLE, PyBUF_WRITABLE
#from libc.stdlib cimport free
#from libc.string cimport memcpy
from libc.stdint cimport int32_t

import numpy as np
cimport numpy as cnp
cnp.import_array()

# ----------------------------------------------------------------------------------------
# Some helper definitions from the Python API
# ----------------------------------------------------------------------------------------
cdef extern from "Python.h":
    char * PyUnicode_AsUTF8(object string)
    #object PyBytes_FromString(char *s)
    #object PyBytes_FromStringAndSize(char *s, size_t size)

# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
cdef extern from "tdlpack.h":
    cdef int32_t TDLP_L3264B
    cdef int32_t TDLP_L3264W
    cdef int32_t TDLP_NBYPWD
    cdef int32_t ND5
    cdef int32_t ND7

    void tdlp_close_tdlpack_file(int32_t *, int32_t *, int32_t *)
    void tdlp_gridij_to_latlon(int32_t *, int32_t *, int32_t *, float *, float *, float *,
                               float *, float *, float *, float *, int32_t *)
    void tdlp_open_log_file(int32_t *, char *)
    void tdlp_open_tdlpack_file(char *, char *, int32_t *, int32_t *, int32_t *, char *)
    void tdlp_pack_1d_wrapper(int32_t *, int32_t *, int32_t *, int32_t *, int32_t *,
                              float *, int32_t *, int32_t *, int32_t *, int32_t *)
    void tdlp_pack_2d_wrapper(int32_t *, int32_t *, int32_t *, int32_t *, int32_t *,
                              int32_t *, float *, int32_t *, int32_t *, int32_t *, int32_t *)
    void tdlp_unpack_meta(int32_t *, int32_t *, int32_t *, int32_t *, int32_t *,
                          int32_t *, int32_t *)
    void tdlp_unpack_data(int32_t *, int32_t *, int32_t *, int32_t *, int32_t *,
                          int32_t *, float *, int32_t *)
    void tdlp_write_station_record(char *, int32_t *, int32_t *, int32_t *, int32_t *,
                                   int32_t *, int32_t *, int32_t *, int32_t *,
                                   int32_t *, int32_t *)
    void tdlp_write_tdlpack_record(char *, int32_t *, int32_t *, int32_t *, int32_t *,
                                   int32_t *, int32_t *, int32_t *, int32_t *, int32_t *)
    void tdlp_write_trailer_record(int32_t *, int32_t *, int32_t *, int32_t *, int32_t *)

# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
class _TdlpackConstants:
    @property
    def L3264B(self):
        return TDLP_L3264B

    @property
    def L3264W(self):
        return TDLP_L3264W

    @property
    def NBYPWD(self):
        return TDLP_NBYPWD

constants = _TdlpackConstants()

# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
def close_tdlpack_file(int lun,
                       int ftype):
    """
    """
    cdef int32_t iret

    iret = 0

    tdlp_close_tdlpack_file(
        <int32_t *>&lun,
        <int32_t *>&ftype,
        &iret,
    )

    return iret


def open_log_file(int log_unit,
                  log_path=None):
    """
    """
    cdef char *c_log_path = NULL
    cdef int32_t iret

    iret = 0
    if log_path is not None:
        c_log_path = <char *>PyUnicode_AsUTF8(log_path)

    tdlp_open_log_file(
        <int32_t *>&log_unit,
        c_log_path,
    )


def open_tdlpack_file(path,
                      mode,
                      int ftype,
                      ra_template=None):
    """ 
    """ 
    cdef char *c_path = NULL
    cdef char *c_mode = NULL
    cdef char *c_ra_template = NULL
    cdef int32_t lun
    cdef int32_t iret

    print(path, mode, ftype)

    c_path = <char *>PyUnicode_AsUTF8(path)
    c_mode = <char *>PyUnicode_AsUTF8(mode)

    lun = 0 
    iret = 0
    if ra_template is not None:
        c_ra_template = <char *>PyUnicode_AsUTF8(ra_template)

    tdlp_open_tdlpack_file(
        c_path,
        c_mode,
        &lun,
        <int32_t *>&ftype,
        &iret,
        c_ra_template,
    )

    return iret, lun


def unpack_meta(cnp.ndarray[cnp.int32_t, ndim=1] ipack):
    """
    """
    cdef int32_t nd5 = len(ipack)
    cdef int32_t[:] ipack_view = ipack
    cdef int32_t[:] is0 = np.empty(ND7, dtype=np.int32)
    cdef int32_t[:] is1 = np.empty(ND7, dtype=np.int32)
    cdef int32_t[:] is2 = np.empty(ND7, dtype=np.int32)
    cdef int32_t[:] is4 = np.empty(ND7, dtype=np.int32)
    cdef int32_t iret = 0

    tdlp_unpack_meta(&nd5,
        <int32_t *>&ipack_view[0],
        &is0[0],
        &is1[0],
        &is2[0],
        &is4[0],
        &iret,
    )

    return iret, np.asarray(is0), np.asarray(is1), np.asarray(is2), np.asarray(is4)


def unpack_data(cnp.ndarray[cnp.int32_t, ndim=1] ipack):
    """
    """
    cdef int32_t[:] ipack_view = ipack
    cdef int32_t[:] is0 = np.empty(ND7, dtype=np.int32)
    cdef int32_t[:] is1 = np.empty(ND7, dtype=np.int32)
    cdef int32_t[:] is2 = np.empty(ND7, dtype=np.int32)
    cdef int32_t[:] is4 = np.empty(ND7, dtype=np.int32)
    cdef int32_t iret = 0

    cdef float[:] data = np.empty(ND5, dtype=np.float32)

    tdlp_unpack_data(&ND5,
        <int32_t *>&ipack_view[0],
        &is0[0],
        &is1[0],
        &is2[0],
        &is4[0],
        &data[0],
        &iret,
    )

    return iret, np.asarray(is0), np.asarray(is1), np.asarray(is2), np.asarray(is4), np.asarray(data[:is4[2]])


def pack_1d(cnp.ndarray[cnp.int32_t, ndim=1] is0,
            cnp.ndarray[cnp.int32_t, ndim=1] is1,
            cnp.ndarray[cnp.int32_t, ndim=1] is2,
            cnp.ndarray[cnp.int32_t, ndim=1] is4,
            cnp.ndarray[cnp.float, ndim=1] data):
    """
    """
    cdef int32_t[:] is0_view = is0
    cdef int32_t[:] is1_view = is1
    cdef int32_t[:] is2_view = is2
    cdef int32_t[:] is4_view = is4
    cdef float[:] data_view = data

    cdef int32_t nd
    cdef int32_t ioctet
    cdef int32_t iret

    nd = len(data)
    ioctet = 0
    iret = 0

    cdef int32_t[:] ipack = np.empty(ND5, dtype=np.int32)

    tdlp_pack_1d_wrapper(
        <int32_t *>&is0_view[0],
        <int32_t *>&is1_view[0],
        <int32_t *>&is2_view[0],
        <int32_t *>&is4_view[0],
        &nd,
        <float *>&data_view[0],
        &ND5,
        &ipack[0],
        &ioctet,
        &iret
    )

    return iret, ioctet, np.asarray(ipack[:ioctet/TDLP_NBYPWD])


def pack_2d(cnp.ndarray[cnp.int32_t, ndim=1] is0,
            cnp.ndarray[cnp.int32_t, ndim=1] is1,
            cnp.ndarray[cnp.int32_t, ndim=1] is2,
            cnp.ndarray[cnp.int32_t, ndim=1] is4,
            cnp.ndarray[cnp.float, ndim=2] data):
    """
    """
    cdef int32_t[:] is0_view = is0
    cdef int32_t[:] is1_view = is1
    cdef int32_t[:] is2_view = is2
    cdef int32_t[:] is4_view = is4
    cdef float[:, ::1] data_view = data

    cdef int32_t nx
    cdef int32_t ny
    cdef int32_t ioctet
    cdef int32_t iret

    nx = data.shape[0]
    ny = data.shape[0]
    ioctet = 0
    iret = 0

    cdef int32_t[:] ipack = np.empty(ND5, dtype=np.int32)

    tdlp_pack_2d_wrapper(
        <int32_t *>&is0_view[0],
        <int32_t *>&is1_view[0],
        <int32_t *>&is2_view[0],
        <int32_t *>&is4_view[0],
        &nx,
        &ny,
        &data_view[0, 0],
        &ND5,
        &ipack[0],
        &ioctet,
        &iret
    )

    return iret, ioctet, np.asarray(ipack[:ioctet/TDLP_NBYPWD])


def write_station_record(path,
                         int lun,
                         int ftype,
                         list[str] stations,
                         int ntotby,
                         int ntotrc,
                         nreplace=None,
                         ncheck=None):
    """
    """
    cdef char *c_path = NULL
    cdef int32_t c_nreplace
    cdef int32_t c_ncheck
    cdef int32_t *c_nreplace_ptr = NULL
    cdef int32_t *c_ncheck_ptr = NULL
    cdef int32_t c_ntotby
    cdef int32_t c_ntotrc
    cdef int32_t iret
    cdef int i

    if nreplace is not None:
        c_nreplace = nreplace
        c_nreplace_ptr = &c_nreplace
    if ncheck is not None:
        c_ncheck = ncheck
        c_ncheck_ptr = &c_ncheck

    cdef int nsta = len(stations)
    cdef int32_t nd5 = nsta * 2
    cdef int32_t[:] ipack = np.empty(nd5, dtype=np.int32)
    for i in range(nsta):
        sbytes = stations[i].encode('utf-8')    
        ipack[i * 2] = int.from_bytes(sbytes[:4], 'little', signed=False)
        ipack[i * 2 + 1] = int.from_bytes(sbytes[4:], 'little', signed=False)

    c_ntotby = ntotby
    c_ntotrc = ntotrc
    iret = 0
    c_path = <char *>PyUnicode_AsUTF8(path)

    tdlp_write_station_record(
        c_path,
        <int32_t *>&lun,
        <int32_t *>&ftype,
        <int32_t *>&nsta,
        &nd5,
        <int32_t *>&ipack[0],
        &c_ntotby,
        &c_ntotrc,
        &iret,
        c_nreplace_ptr,
        c_ncheck_ptr,
    )

    del ipack
    return iret, c_ntotby, c_ntotrc


def write_tdlpack_record(path,
                         int lun,
                         int ftype,
                         cnp.ndarray[cnp.int32_t, ndim=1] ipack,
                         int ntotby,
                         int ntotrc,
                         nreplace=None,
                         ncheck=None):
    """
    """
    cdef char *c_path = NULL
    cdef int32_t c_nreplace
    cdef int32_t c_ncheck
    cdef int32_t *c_nreplace_ptr = NULL
    cdef int32_t *c_ncheck_ptr = NULL
    cdef int32_t c_ntotby
    cdef int32_t c_ntotrc
    cdef int32_t iret
    cdef int32_t nd5

    if nreplace is not None:
        c_nreplace = nreplace
        c_nreplace_ptr = &c_nreplace
    if ncheck is not None:
        c_ncheck = ncheck
        c_ncheck_ptr = &c_ncheck

    c_ntotby = ntotby
    c_ntotrc = ntotrc
    nd5 = len(ipack)
    iret = 0
    c_path = <char *>PyUnicode_AsUTF8(path)
                         
    tdlp_write_tdlpack_record(
        c_path,
        <int32_t *>&lun,
        <int32_t *>&ftype,
        &nd5,
        <int32_t *>&ipack[0],
        &c_ntotby,
        &c_ntotrc,
        &iret,
        c_nreplace_ptr,
        c_ncheck_ptr,
    )

    return iret, c_ntotby, c_ntotrc


def write_trailer_record(int lun,
                         int ftype,
                         int ntotby,
                         int ntotrc):
    """
    """
    cdef int32_t c_ntotby
    cdef int32_t c_ntotrc
    cdef int32_t iret

    c_ntotby = ntotby
    c_ntotrc = ntotrc
    iret = 0
    
    tdlp_write_trailer_record(
        <int32_t *>&lun,
        <int32_t *>&ftype,
        &c_ntotby,
        &c_ntotrc,
        &iret
    )

    return iret, c_ntotby, c_ntotrc

# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
def gridij_to_latlon(int nx,
                     int ny,
                     int mproj,
                     float xmeshl,
                     float orient,
                     float xlat,
                     float xlatll,
                     float xlonll):
    """
    """
    cdef int32_t iret

    cdef float[:, ::1] lats = np.empty((nx, ny), dtype=np.float32) 
    cdef float[:, ::1] lons = np.empty((nx, ny), dtype=np.float32) 

    iret = 0

    tdlp_gridij_to_latlon(
        <int32_t *>&nx,
        <int32_t *>&ny,
        <int32_t *>&mproj,
        <float *>&xmeshl,
        <float *>&orient,
        <float *>&xlat,
        <float *>&xlatll,
        <float *>&xlonll,
        <float *>&lats[0, 0],
        <float *>&lons[0, 0],
        &iret,
    )

    return iret, np.asarray(lats), np.asarray(lons)
