cmake_minimum_required(VERSION 3.18)
project(tdlpackio LANGUAGES C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# -----------------------------------------------------------------------------
# function: tdlpackio_env_bool
# -----------------------------------------------------------------------------

function(tdlpackio_env_bool ENV_NAME DEFAULT_VALUE OUT_VAR)
    if(DEFINED ENV{${ENV_NAME}})
        string(TOUPPER "$ENV{${ENV_NAME}}" _env_val)
        if(_env_val STREQUAL "1" OR _env_val STREQUAL "ON" OR
           _env_val STREQUAL "TRUE" OR _env_val STREQUAL "YES")
            set(_out ON)
        elseif(_env_val STREQUAL "0" OR _env_val STREQUAL "OFF" OR
               _env_val STREQUAL "FALSE" OR _env_val STREQUAL "NO")
            set(_out OFF)
        else()
            message(
                FATAL_ERROR
                "Environment variable ${ENV_NAME} must be a boolean "
                "(True/False, On/Off, 1/0)"
            )
        endif()
    else()
        set(_out ${DEFAULT_VALUE})
    endif()

    set(${OUT_VAR} ${_out} PARENT_SCOPE)
endfunction()

# -----------------------------------------------------------------------------
# function: tdlpackio_python_bool
# -----------------------------------------------------------------------------

function(tdlpackio_python_bool VALUE OUT_VAR)
    if(${VALUE})
        set(${OUT_VAR} "True" PARENT_SCOPE)
    else()
        set(${OUT_VAR} "False" PARENT_SCOPE)
    endif()
endfunction()

# -----------------------------------------------------------------------------
# function: tdlpackio_find_library
# -----------------------------------------------------------------------------

function(tdlpackio_find_library OUT_VAR)
    set(options REQUIRED STATIC)
    set(oneValueArgs)
    set(multiValueArgs NAMES HINTS)

    cmake_parse_arguments(
        PARSE_ARGV 1 ARG
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
    )

    if(ARG_STATIC)
        set(_saved_suffixes "${CMAKE_FIND_LIBRARY_SUFFIXES}")
        set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
    endif()

    set(_find_var "_TDLPACKIO_${OUT_VAR}")

    # Ensure find_library() performs a new search rather than using a stale
    # internal cache entry.
    unset(${_find_var})
    unset(${_find_var} CACHE)

    if(ARG_REQUIRED)
        find_library(
            ${_find_var}
            NAMES ${ARG_NAMES}
            HINTS ${ARG_HINTS}
            PATH_SUFFIXES lib lib64
            REQUIRED
        )
    else()
        find_library(
            ${_find_var}
            NAMES ${ARG_NAMES}
            HINTS ${ARG_HINTS}
            PATH_SUFFIXES lib lib64
        )
    endif()

    if(ARG_STATIC)
        set(CMAKE_FIND_LIBRARY_SUFFIXES "${_saved_suffixes}")
    endif()

    set(${OUT_VAR} "${${_find_var}}" PARENT_SCOPE)
endfunction()

# -----------------------------------------------------------------------------
# function: tdlpackio_add_cython_module
# -----------------------------------------------------------------------------

function(tdlpackio_add_cython_module TARGET_NAME PYX_FILE)
    set(_generated_c "${CMAKE_CURRENT_BINARY_DIR}/${TARGET_NAME}.c")

    add_custom_command(
        OUTPUT "${_generated_c}"
        COMMAND
            "${Python_EXECUTABLE}" -m cython -3 --fast-fail
            -o "${_generated_c}" "${PYX_FILE}"
        DEPENDS "${PYX_FILE}"
        VERBATIM
    )

    Python_add_library(${TARGET_NAME} MODULE WITH_SOABI "${_generated_c}")
    set_target_properties(
        ${TARGET_NAME}
        PROPERTIES
            PREFIX ""
            OUTPUT_NAME "${TARGET_NAME}"
    )

    target_include_directories(${TARGET_NAME} PRIVATE ${Python_INCLUDE_DIRS})
    target_compile_definitions(
        ${TARGET_NAME}
        PRIVATE NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
    )

    install(TARGETS ${TARGET_NAME} LIBRARY DESTINATION tdlpackio)
endfunction()

execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import numpy; print(numpy.get_include())"
    OUTPUT_VARIABLE NUMPY_INCLUDE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE NUMPY_INCLUDE_RESULT
)
if(NOT NUMPY_INCLUDE_RESULT EQUAL 0 OR NOT NUMPY_INCLUDE_DIR)
    message(FATAL_ERROR "Unable to determine NumPy include directory")
endif()

# -----------------------------------------------------------------------------
# Read version from VERSION file
# -----------------------------------------------------------------------------

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" TDLPACKIO_VERSION)
string(STRIP "${TDLPACKIO_VERSION}" TDLPACKIO_VERSION)

# -----------------------------------------------------------------------------
# Build options (defaults can be overridden with env vars or cmake.define)
# -----------------------------------------------------------------------------

tdlpackio_env_bool("TDLPACK_STATIC" OFF TDLPACKIO_TDLPACK_STATIC)

# A static Fortran archive does not carry its runtime dependencies. Enable the
# Fortran language so the extension can be linked with the Fortran driver.
if(TDLPACKIO_TDLPACK_STATIC)
    enable_language(Fortran)
endif()

set(_tdlpack_hints)
set(_tdlpack_include_hints)
set(_conda_prefix_hints)

# -----------------------------------------------------------------------------
# Check for conda environment
# -----------------------------------------------------------------------------

if(DEFINED ENV{CONDA_PREFIX})
    list(APPEND _conda_prefix_hints "$ENV{CONDA_PREFIX}")
endif()
if(DEFINED ENV{CONDA_ROOT})
    list(APPEND _conda_prefix_hints "$ENV{CONDA_ROOT}")
endif()
if(DEFINED ENV{MAMBA_ROOT_PREFIX})
    list(APPEND _conda_prefix_hints "$ENV{MAMBA_ROOT_PREFIX}")
endif()

# -----------------------------------------------------------------------------
# Generate path hints for libtdlpack
# -----------------------------------------------------------------------------

if(DEFINED ENV{TDLPACK_DIR})
    list(APPEND
        _tdlpack_include_hints
        "$ENV{TDLPACK_DIR}"
        "$ENV{TDLPACK_DIR}/include"
    )
    list(APPEND
        _tdlpack_hints
        "$ENV{TDLPACK_DIR}"
        "$ENV{TDLPACK_DIR}/lib"
        "$ENV{TDLPACK_DIR}/lib64"
    )
else()
    # Env var TDLPACK_DIR not defined, now check for specific
    # TDLPACK_INCDIR and TDLPACK_LIBDIR.
    if(DEFINED ENV{TDLPACK_INCDIR})
        list(APPEND _tdlpack_include_hints "$ENV{TDLPACK_INCDIR}")
    endif()
    if(DEFINED ENV{TDLPACK_LIBDIR})
        list(APPEND _tdlpack_hints "$ENV{TDLPACK_LIBDIR}")
    endif()
endif()

foreach(_prefix IN LISTS _conda_prefix_hints)
    list(APPEND _tdlpack_include_hints "${_prefix}" "${_prefix}/include")
    list(APPEND _tdlpack_hints "${_prefix}/lib" "${_prefix}/lib64")
endforeach()

list(APPEND _tdlpack_include_hints /usr /usr/local /opt/homebrew /opt/local /opt)
list(APPEND _tdlpack_hints /usr /usr/local /opt/homebrew /opt/local /opt)

find_path(
    TDLPACK_INCLUDE_DIR
    tdlpack.h
    HINTS ${_tdlpack_include_hints}
    PATH_SUFFIXES include
    REQUIRED
)

if(TDLPACKIO_TDLPACK_STATIC)
    tdlpackio_find_library(
        TDLPACK_LIBRARY
        REQUIRED STATIC
        NAMES tdlpack
        HINTS ${_tdlpack_hints}
    )
else()
    tdlpackio_find_library(
        TDLPACK_LIBRARY
        REQUIRED
        NAMES tdlpack
        HINTS ${_tdlpack_hints}
    )
endif()

get_filename_component(TDLPACK_LIBRARY_DIR "${TDLPACK_LIBRARY}" DIRECTORY)
message(STATUS "Resolved TDLPACK include dir: ${TDLPACK_INCLUDE_DIR}")
message(STATUS "Resolved TDLPACK library: ${TDLPACK_LIBRARY}")
set(TDLPACKIO_TDLPACK_LIBRARY ${TDLPACK_LIBRARY})

# -----------------------------------------------------------------------------
# tdlpacklib extension module
# -----------------------------------------------------------------------------

tdlpackio_add_cython_module(
    tdlpacklib
    "${CMAKE_CURRENT_SOURCE_DIR}/src/ext/tdlpacklib.pyx"
)

target_include_directories(
    tdlpacklib
    PRIVATE "${TDLPACK_INCLUDE_DIR}" "${NUMPY_INCLUDE_DIR}"
)

target_link_libraries(tdlpacklib PRIVATE "${TDLPACK_LIBRARY}")

if(TDLPACKIO_TDLPACK_STATIC)
    # libtdlpack.a contains Fortran objects, but CMake cannot infer that from a
    # library filename. Use the Fortran compiler driver for the final extension
    # link so the required Fortran runtime libraries are included.
    set_property(TARGET tdlpacklib PROPERTY LINKER_LANGUAGE Fortran)
else()
    set_property(
        TARGET tdlpacklib
        PROPERTY INSTALL_RPATH "${TDLPACK_LIBRARY_DIR}"
    )
endif()

# -----------------------------------------------------------------------------
# Generate runtime build configuration module
# -----------------------------------------------------------------------------

set(TDLPACKIO_EXTRA_OBJECTS "[]")
tdlpackio_python_bool(
    TDLPACKIO_TDLPACK_STATIC
    TDLPACKIO_TDLPACK_STATIC_PY
)
tdlpackio_python_bool(
    TDLPACKIO_HAS_INTERPOLATION
    TDLPACKIO_HAS_INTERPOLATION_PY
)
tdlpackio_python_bool(
    TDLPACKIO_IP_STATIC
    TDLPACKIO_IP_STATIC_PY
)
tdlpackio_python_bool(
    TDLPACKIO_HAS_OPENMP
    TDLPACKIO_HAS_OPENMP_PY
)

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/tdlpackio_config.py.in"
    "${CMAKE_CURRENT_BINARY_DIR}/__config__.py"
    @ONLY
)
install(
    FILES "${CMAKE_CURRENT_BINARY_DIR}/__config__.py"
    DESTINATION tdlpackio
)

message(STATUS "tdlpackio version: ${TDLPACKIO_VERSION}")
message(STATUS "libtdlpack static: ${TDLPACKIO_TDLPACK_STATIC}")
message(STATUS "OpenMP support: ${TDLPACKIO_HAS_OPENMP}")
