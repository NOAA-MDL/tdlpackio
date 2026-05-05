import pytest
from datetime import timedelta
import numpy as np
import pandas as pd
import xarray as xr


def test_station_open(request):
    sampledata = request.config.rootdir / "tests" / "data"
    ds = xr.open_dataset(sampledata / "stations.sq", engine="tdlpackio")
    assert ds.dims == {"refDate": 123, "leadTime": 1, "station": 3279}


def test_grid_open(request):
    sampledata = request.config.rootdir / "tests" / "data"
    ds = xr.open_dataset(sampledata / "gfspkd47.2017020100.sq", engine="tdlpackio", filters=dict(cccfff=1000))
    assert ds.dims == {"refDate": 1, "leadTime": 1, "uuuu": 12, "y": 169, "x": 297}
    assert "001_000" in ds.data_vars


def test_station_open_with_sort(request):
    sampledata = request.config.rootdir / "tests" / "data"
    ds = xr.open_dataset(sampledata / "test1.sq", engine="tdlpackio")
    assert ds.station.to_series().is_monotonic_increasing
    expected_arr = np.array([[[17.0, -53.0, 92.0, 72.0, -33.0]], [[-91.0, 3.0, -79.0, 95.0, -64.0]]], dtype="float32")
    np.testing.assert_array_equal(expected_arr, ds["001_002"].data)


def test_catted_equall_multi(request):
    sampledata = request.config.rootdir / "tests" / "data"
    ds_multi = xr.open_mfdataset([sampledata / "test1.sq", sampledata / "test2.sq"], engine="tdlpackio")
    ds_catted = xr.open_dataset(sampledata / "test1_2.sq", engine="tdlpackio")


def test_filters(request):
    sampledata = request.config.rootdir / "tests" / "data"
    dsf = xr.open_dataset(sampledata / "stations.sq", engine="tdlpackio", filters=dict(refDate="2021-09-07"))
    ds = xr.open_dataset(sampledata / "stations.sq", engine="tdlpackio").sel(refDate="2021-09-07")
    xr.testing.assert_equal(dsf, ds)
    dsf = xr.open_dataset(sampledata / "stations.sq", engine="tdlpackio", filters=dict(refDate=["2021-09-07 06", "2021-09-09 06"]))
    ds = xr.open_dataset(sampledata / "stations.sq", engine="tdlpackio").sel(refDate=["2021-09-07 06", "2021-09-09 06"])
    xr.testing.assert_equal(dsf, ds)
    dsf = xr.open_dataset(sampledata / "stations.sq", engine="tdlpackio", filters=dict(refDate=slice("2021-09-07", "2021-09-09")))
    ds = xr.open_dataset(sampledata / "stations.sq", engine="tdlpackio").sel(refDate=slice("2021-09-07", "2021-09-09"))
    xr.testing.assert_equal(dsf, ds)


def test_grid_same_as_tdlpackio(request):
    sampledata = request.config.rootdir / "tests" / "data"
    ds = xr.open_dataset(sampledata / "gfspkd47.2017020100.sq", engine="tdlpackio", filters=dict(cccfff=1000))
    da = ds["001_000"].sel(uuuu=1000).squeeze()

    import tdlpackio

    with tdlpackio.open(sampledata / "gfspkd47.2017020100.sq") as f:
        rec = f[0]
        np.testing.assert_array_equal(da.data, rec.data)
