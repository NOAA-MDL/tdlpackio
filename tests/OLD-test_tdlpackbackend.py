import pytest
from datetime import timedelta
import numpy as np
import pandas as pd
import xarray as xr


def test_station_open(request):
    sampledata = request.config.rootdir / 'sampledata'
    ds = xr.open_dataset(sampledata / 'stations.sq', engine='tdlpack')
    assert ds.dims == {'date': 123, 'lead': 1, 'station': 3279}

def test_grid_open(request):
    sampledata = request.config.rootdir / 'sampledata'
    ds = xr.open_dataset(sampledata / 'gfspkd47.2017020100.sq', engine='tdlpack', filters=dict(cccfff=1000))
    assert ds.dims == {'date': 1, 'lead': 1, 'uuuu': 12, 'y': 169, 'x': 297}
    assert '001_000' in ds.data_vars

def test_station_open_with_sort(request):
    sampledata = request.config.rootdir / 'sampledata'
    ds = xr.open_dataset(sampledata / 'test1.sq', engine='tdlpack')
    assert ds.station.to_series().is_monotonic
    expected_arr = np.array([[[ 17., -53.,  92.,  72., -33.]],
                             [[-91.,   3., -79.,  95., -64.]]], dtype='float32')
    np.testing.assert_array_equal(expected_arr, ds['001_002'].data)

def test_catted_equall_multi(request):
    sampledata = request.config.rootdir / 'sampledata'
    ds_multi = xr.open_mfdataset([sampledata / 'test1.sq', sampledata / 'test2.sq'], engine='tdlpack')
    ds_catted = xr.open_dataset(sampledata / 'test1_2.sq', engine='tdlpack')

def test_filters(request):
    sampledata = request.config.rootdir / 'sampledata'
    dsf = xr.open_dataset(sampledata / 'stations.sq', engine='tdlpack', filters=dict(date='2021-09-07'))
    ds = xr.open_dataset(sampledata / 'stations.sq', engine='tdlpack').sel(date='2021-09-07')
    xr.testing.assert_equal(dsf, ds)
    dsf = xr.open_dataset(sampledata / 'stations.sq', engine='tdlpack', filters=dict(date=['2021-09-07 06', '2021-09-09 06']))
    ds = xr.open_dataset(sampledata / 'stations.sq', engine='tdlpack').sel(date=['2021-09-07 06', '2021-09-09 06'])
    xr.testing.assert_equal(dsf, ds)
    dsf = xr.open_dataset(sampledata / 'stations.sq', engine='tdlpack', filters=dict(date=slice('2021-09-07', '2021-09-09')))
    ds = xr.open_dataset(sampledata / 'stations.sq', engine='tdlpack').sel(date=slice('2021-09-07', '2021-09-09'))
    xr.testing.assert_equal(dsf, ds)

def test_grid_same_as_pytdlpack(request):
    sampledata = request.config.rootdir / 'sampledata'
    ds = xr.open_dataset(sampledata / 'gfspkd47.2017020100.sq', engine='tdlpack', filters=dict(cccfff=1000))
    da = ds['001_000'].sel(uuuu=1000).squeeze()

    import pytdlpack
    with pytdlpack.open(sampledata / 'gfspkd47.2017020100.sq') as f:
        rec = f.read()
    rec.unpack(data=True)

    np.testing.assert_array_equal(da.data, rec.data.transpose())
