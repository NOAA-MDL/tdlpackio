"""
Grid definitions of common grids in the MOS-2000/TDLPACK system.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import ClassVar, Literal

import numpy as np

from . import _tdlpackio

__all__ = ["TdlpackGridDef", "GRIDS", "get_grid", "has_grid"]


@dataclass(frozen=True, slots=True)
class TdlpackGridDef:
    """Definition of a TDLPACK grid.

    Stored longitude convention is MOS-2000:
    west longitude is positive.
    """

    mapProjection: int
    nx: int
    ny: int
    latitudeLowerLeft: float
    longitudeLowerLeft: float
    standardLatitude: float
    orientationLongitude: float
    gridLength: float

    # Array mapping
    IS2_INDEX: ClassVar[dict[str, int]] = {
        "mapProjection": 1,
        "nx": 2,
        "ny": 3,
        "latitudeLowerLeft": 4,
        "longitudeLowerLeft": 5,
        "orientationLongitude": 6,
        "gridLength": 7,
        "standardLatitude": 8,
    }

    # Attribute scale factors used to convert to whole integers.
    SCALE_FACTOR: ClassVar[dict[str, int]] = {
        "mapProjection": 1,
        "nx": 1,
        "ny": 1,
        "latitudeLowerLeft": 10_000,
        "longitudeLowerLeft": 10_000,
        "orientationLongitude": 10_000,
        "gridLength": 1000,
        "standardLatitude": 10_000,
    }

    def scaled_value(self, name: str) -> int:
        """Return one grid attribute scaled to an integer."""
        value = getattr(self, name)
        scale = self.SCALE_FACTOR[name]
        return int(round(value * scale))

    def to_is2(self) -> list[int]:
        """Return the grid definition as a scaled integer array."""
        is2 = np.zeros((_tdlpackio.ND7), dtype=np.int32)

        for name, index in self.IS2_INDEX.items():
            is2[index] = self.scaled_value(name)

        return is2

    def to_int_dict(self) -> dict[str, int]:
        """Return scaled integer values keyed by attribute name."""
        return {name: self.scaled_value(name) for name in self.IS2_INDEX}


_GRIDS: dict[str, TdlpackGridDef] = {
    "nbmak": TdlpackGridDef(
        mapProjection=5,
        nx=1649,
        ny=1105,
        latitudeLowerLeft=40.5301,
        longitudeLowerLeft=178.5713,
        standardLatitude=60.0,
        orientationLongitude=150.0,
        gridLength=2976.560059,
    ),
    "nbmco": TdlpackGridDef(
        mapProjection=3,
        nx=2345,
        ny=1597,
        latitudeLowerLeft=19.2290,
        longitudeLowerLeft=126.2766,
        standardLatitude=25.0,
        orientationLongitude=95.0,
        gridLength=2539.702881,
    ),
    "nbmgu": TdlpackGridDef(
        mapProjection=7,
        nx=193,
        ny=193,
        latitudeLowerLeft=12.3499,
        longitudeLowerLeft=216.3130,
        standardLatitude=20.0,
        orientationLongitude=360.0,
        gridLength=2500.0,
    ),
    "nbmhi": TdlpackGridDef(
        mapProjection=7,
        nx=625,
        ny=561,
        latitudeLowerLeft=14.3515,
        longitudeLowerLeft=164.9695,
        standardLatitude=20.0,
        orientationLongitude=160.0,
        gridLength=2500.0,
    ),
    "nbmoc": TdlpackGridDef(
        mapProjection=7,
        nx=2517,
        ny=1817,
        latitudeLowerLeft=-30.4192,
        longitudeLowerLeft=230.0942,
        standardLatitude=20.0,
        orientationLongitude=360.0,
        gridLength=10000.0,
    ),
    "nbmpr": TdlpackGridDef(
        mapProjection=7,
        nx=353,
        ny=257,
        latitudeLowerLeft=16.8280,
        longitudeLowerLeft=68.1954,
        standardLatitude=20.0,
        orientationLongitude=65.0,
        gridLength=1250.0,
    ),
    "nbmswp": TdlpackGridDef(
        mapProjection=7,
        nx=3683,
        ny=1903,
        latitudeLowerLeft=-26.0,
        longitudeLowerLeft=230.0,
        standardLatitude=-5.0,
        orientationLongitude=360.0,
        gridLength=2500.0,
    ),
    "gfs23": TdlpackGridDef(
        mapProjection=5,
        nx=593,
        ny=337,
        latitudeLowerLeft=2.8320,
        longitudeLowerLeft=150.0003,
        standardLatitude=60.0,
        orientationLongitude=105.0,
        gridLength=23812.5,
    ),
    "gfs47": TdlpackGridDef(
        mapProjection=5,
        nx=297,
        ny=169,
        latitudeLowerLeft=2.8320,
        longitudeLowerLeft=150.0003,
        standardLatitude=60.0,
        orientationLongitude=105.0,
        gridLength=47625.0,
    ),
    "gfs95": TdlpackGridDef(
        mapProjection=5,
        nx=149,
        ny=85,
        latitudeLowerLeft=2.8320,
        longitudeLowerLeft=150.0003,
        standardLatitude=60.0,
        orientationLongitude=105.0,
        gridLength=95250.0,
    ),
    "nam151": TdlpackGridDef(
        mapProjection=5,
        nx=425,
        ny=281,
        latitudeLowerLeft=0.7279,
        longitudeLowerLeft=150.3583,
        standardLatitude=60.0,
        orientationLongitude=110.0,
        gridLength=33812.0,
    ),
    "nam221": TdlpackGridDef(
        mapProjection=3,
        nx=349,
        ny=198,
        latitudeLowerLeft=9.5803,
        longitudeLowerLeft=150.7806,
        standardLatitude=50.0,
        orientationLongitude=107.0,
        gridLength=32463.410156,
    ),
}

GRIDS: Mapping[str, TdlpackGridDef] = MappingProxyType(_GRIDS)


def _mos2k_to_standard(lon: float) -> float:
    """
    Convert MOS-2000 longitude (west-positive) to standard
    east-positive longitude in [-180, 180].
    """
    # Flip sign: west-positive -> east-positive
    lon = -lon

    # Normalize robustly to [-180, 180)
    lon = ((lon + 180.0) % 360.0) - 180.0

    return lon


def _mos2k_to_0_360(lon: float) -> float:
    """
    Convert MOS-2000 longitude (west-positive) to east-positive [0, 360).
    """
    return _mos2k_to_standard(lon) % 360.0


def get_grid(
    name: str,
    *,
    lon_format: Literal["mos2k", "standard", "0_360"] = "mos2k",
) -> TdlpackGridDef:
    """
    Return a grid definition by name.

    Notes
    -----
    Internally, all grid definitions are stored using the MOS-2000
    longitude convention (west longitude is positive).

    Parameters
    ----------
    name : str
        Grid name.
    lon_format : {"mos2k", "standard", "0_360"}, optional
        Longitude convention to return:

        - "mos2k": West longitude positive (native storage format)
        - "standard": East-positive, range [-180, 180]
        - "0_360": East-positive, range [0, 360)

    Returns
    -------
    TdlpackGridDef
        Grid definition using the requested longitude convention.
    """
    try:
        grid = GRIDS[name.lower()]
    except KeyError as exc:
        raise KeyError(f"Unknown grid: {name!r}") from exc

    # Native format (no copy needed)
    if lon_format == "mos2k":
        return grid

    if lon_format == "standard":
        return replace(
            grid,
            longitudeLowerLeft=_mos2k_to_standard(grid.longitudeLowerLeft),
            orientationLongitude=_mos2k_to_standard(grid.orientationLongitude),
        )

    if lon_format == "0_360":
        return replace(
            grid,
            longitudeLowerLeft=_mos2k_to_0_360(grid.longitudeLowerLeft),
            orientationLongitude=_mos2k_to_0_360(grid.orientationLongitude),
        )

    raise ValueError(f"Invalid lon_format: {lon_format!r}. Expected one of {{'mos2k', 'standard', '0_360'}}.")


def has_grid(name: str) -> bool:
    """Return True if a grid name is known."""
    return name.lower() in GRIDS
