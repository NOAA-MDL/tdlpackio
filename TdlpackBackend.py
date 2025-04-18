#!/usr/bin/env python3
# TdlpackBackend is a backend entrypoint for decoding sequential tdlpack files with the engine 'tdlpack'
# TdlpackBackend is pre-release and the API is subject to change without backward compatability
from pathlib import Path
import shutil
import datetime
import numbers
from dataclasses import dataclass, field, astuple
import typing
from copy import copy
from abc import ABC, abstractmethod
from itertools import product
import logging
import numpy as np
import pandas as pd
import xarray as xr
from xarray.backends.common import (
    BACKEND_ENTRYPOINTS,
    AbstractDataStore,
    BackendArray,
    BackendEntrypoint,
)
from xarray.core import indexing
from xarray.backends.locks import SerializableLock
import pytdlpack
import TdlpackIO

logger = logging.getLogger(__name__)

LOCK = SerializableLock()

class TdlpackBackendEntrypoint(BackendEntrypoint):
    ''' xarray backend engine entrypoint for opening and  decoding sequential tdlpack files.

    .. warning::
            This backend is pre-release and its signature may change without backward comaptability.

    Parameters
    __________

    filename: str, Path, file-like
        sequential tdlpack file to be opened
    name_scheme: list of strings with tdlpack metadata, optional
        dictates name of variables and shape of arrays;
        tdlpack metadata expressed in the name will not be dimension of array
        * name_scheme is not recomended for use, the default ['ccc','fff'] is adequate
    filters: dict, optional when tdlpack file is not sparse
        applies whitelist filters to select data of interest; often useful for reducing data
        down to a non-sparse selection
        The tdlpack is considered not sparse when variables built have the same shape.
    '''
    def open_dataset(
        self,
        filename,
        *,
        drop_variables = None,
        name_scheme: list = ['ccc','fff'],
        filters: typing.Mapping[str, any] = None,
    ):

        # read and parse metadata from tdlpack file
        f = TdlpackIO.open(filename)
        file_index = pd.DataFrame(f._index)

        file_index = parse_tdlpackio_index_to_components(file_index)

        # divide up records by variable based on name scheme and filters
        filters = copy(filters)
        frames, cube, extra_geo, one_sta_list, is2 = make_variables(file_index, name_scheme, filters, f)
        # return empty dataset if no data
        if frames is None:
            return xr.Dataset()

        # create dataframe and add datarrays without any coords
        ds = xr.Dataset()
        for var_df in frames:
            da = build_da_without_coords(var_df, cube, f, one_sta_list)
            da.encoding['tdlp_is2'] = is2
#            da.encoding['tdlp_datset_name_scheme'] = name_scheme
            ds[da.name] = da

        # assign coords from the cube; the cube prevents datarrays with different shapes
        ds = ds.assign_coords(cube.coords())
        # assign extra geo coords
        ds = ds.assign_coords(extra_geo)

        return ds


class TdlpackBackendArray(BackendArray):

    def __init__(self, array, lock):
        self.array = array
        self.shape = array.shape
        self.dtype = np.dtype(array.dtype)
        self.lock = lock


    def __getitem__(self, key: xr.core.indexing.ExplicitIndexer) -> np.typing.ArrayLike:
        return xr.core.indexing.explicit_indexing_adapter(
            key,
            self.shape,
            indexing.IndexingSupport.BASIC,
            self._raw_getitem,
        )

    def _raw_getitem(self, key: tuple):
        # thread safe method implementing access to data on disk
        with self.lock:
            return self.array[key]


def exclusive_slice_to_inclusive(item):
    # return the None slice
    if item.start is None and item.stop is None and item.step is None:
        return item
    if not isinstance(item, slice):
        raise ValueError(f'item must be a slice; it was of type {type(item)}')
    # if step is None, it's one
    step = 1 if item.step is None else item.step
    if item.stop < item.start or step < 1:
        raise ValueError(f'slice {item} not accounted for')
    # handle case where slice has one item
    if abs(item.stop - item.start) == step:
        return [item.start]
    # other cases require reducing the stop by the step
    s = slice(item.start, item.stop - step, step)
    return s

class Validator:
    def __set_name__(self, owner, name):
        self.private_name = f'_{name}'
        self.name = name

    def __get__(self, obj, objtype=None):
        try:
            value = getattr(obj, self.private_name)
        except AttributeError:
            value = None
        return value

class PdIndex(Validator):

    def __set__(self, obj, value):
        try:
            value = pd.Index(value)
        except TypeError:
            value = pd.Index([value])
        setattr(obj, self.private_name, value)

def array_safe_eq(a, b) -> bool:
    """Check if a and b are equal, even if they are numpy arrays"""
    if a is b:
        return True
    if hasattr(a, 'equals'):
        return a.equals(b)
    if hasattr(a, 'all') and hasattr(b, 'all'):
        return a.shape == b.shape and (a == b).all()
    if hasattr(a, 'all') or hasattr(b, 'all'):
        return False
    try:
        return a == b
    except TypeError:
        return NotImplementedError

def dc_eq(dc1, dc2) -> bool:
    """checks if two dataclasses which hold numpy arrays are equal"""
    if dc1 is dc2:
        return True
    if dc1.__class__ is not dc2.__class__:
        return NotImplementedError
    t1 = astuple(dc1)
    t2 = astuple(dc2)
    return all(array_safe_eq(a1, a2) for a1, a2 in zip(t1, t2))


@dataclass(init=False)
class TdlpCube:
    date: pd.DatetimeIndex = PdIndex()
    lead: pd.TimedeltaIndex = PdIndex()
    ccc: pd.Index = PdIndex()
    fff: pd.Index = PdIndex()
    b: pd.Index = PdIndex()
    dd: pd.Index = PdIndex()
    v: pd.Index = PdIndex()
    llll: pd.Index = PdIndex()
    uuuu: pd.Index = PdIndex()
    t: pd.Index = PdIndex()
    o: pd.Index = PdIndex()
    thresh: pd.Index = PdIndex()
    i: pd.Index = PdIndex()
    s: pd.Index = PdIndex()
    g: pd.Index = PdIndex()
    y: pd.Index = PdIndex()
    x: pd.Index = PdIndex()
    station: pd.Index = PdIndex()

    def __setitem__(self, key, value):
        #super().__setitem__(key, value)
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __eq__(self, other):
        return dc_eq(self, other)

    def coords(self) -> typing.Dict[str, xr.Variable]:
        keys = list(TdlpCube.__dataclass_fields__.keys())
        keys.remove('x')
        keys.remove('y')
        coords = {k: xr.Variable(dims=k, data=self[k], attrs=dict(tdlp_name=k)) for k in keys if self[k] is not None}
        return coords

@dataclass
class OnDiskArray:
    file_name: str
    index: pd.DataFrame = field(repr=False)
    cube: TdlpCube = field(repr=False)
    one_station_list_and_ordered: bool = field(repr=False)
    shape: typing.Tuple[int, ...] = field(init=False)
    ndim: int = field(init=False)
    geo_ndim: int = field(init=False)
    dtype = 'float32'

    def __post_init__(self):
        if not self.cube.station is None:
            geo_shape = (len(self.cube.station),) # for stations, the record may not actually be this shape, but is converted to this shape
        else:
            geo_shape = self.index.iloc[0].record_shape  # multiple grids not allowed so can just use first

        self.geo_shape = geo_shape
        self.geo_ndim = len(geo_shape)

        if self.index.index.nlevels == 1:
            self.shape = (len(self.index),) + geo_shape
        else:
            self.shape = tuple([len(i) for i in self.index.index.levels]) + geo_shape
        self.ndim = len(self.shape)


    def __getitem__(self, item) -> np.array:
        # dimensions not in index are internal to tdlpack records; 2 dims for grids; 1 dim for stations
        f = TdlpackIO.open(self.file_name)

        index_slicer = item[:-self.geo_ndim]
        index_slicer = tuple([[i] if isinstance(i, int) else i for i in index_slicer]) # maintain all multindex levels
        # pandas loc slicing is inclusive, therefore convert slices into explicit lists
        index_slicer_inclusive = tuple([ exclusive_slice_to_inclusive(i) if isinstance(i, slice) else i for i in index_slicer])

        # get records selected by item in new index dataframe
        index = self.index.loc[index_slicer_inclusive, :]
        index = index.set_index(index.index)

        # reset miloc to new relative locations in sub array
        index['miloc'] = list(zip(*[index.index.unique(level=dim).get_indexer(index.index.get_level_values(dim)) for dim in index.index.names]))
        array_field_shape = index.index.levshape + self.geo_shape

        array_field = np.full(array_field_shape, fill_value=np.nan, dtype="float32")

        for key, row in index.iterrows():
            record = f[row['record']]
            logger.debug(f'unpacking and loading data, {record.reference_date}, {record.id}')
            record.unpack(data=True)
            if not self.cube.x is None: # grid
                values = record.data.transpose()
            else: # stations
                if self.one_station_list_and_ordered:
                    logger.debug(f'taking fast path for retrieving station record')
                    values = record.data
                else:
                    rec_stations = f[row['linked_station_id_record']].stations
                    rec_series = pd.Series(record.data, name='data', index=pd.Series(rec_stations, name='station'))
                    arr_series = pd.Series(np.nan, name='data', index=self.cube.station)
                    arr_series.update(rec_series)
                    values = arr_series.values


            array_field[row.miloc] = values

        # handle geo dim slicing
        array_field = array_field[(Ellipsis,) + item[-self.geo_ndim :]]

        # squeeze array dimensions expressed as integer
        for i, it in reversed(list(enumerate(item[: -self.geo_ndim]))):
            if isinstance(it, int):
                array_field = array_field[(slice(None, None, None),) * i + (0,)]
        f.close()
        array_field[array_field==9999.0] = np.nan
        return array_field


def dims_to_shape(d) -> tuple:
    if 'nx' in d:
        t = (d['ny'],d['nx'])
    else:
        t = (d['nsta'],)
    return t

def parse_tdlpackio_index_to_components(df, decode_time=True, decode_thresh=True, decode_lead=True, ttt='hours'):
    df = df[df.type != 'trailer']
    record = df.index + 1
    df = df.assign(record=record)

    ccc = (df.id1 // 1_000_000).astype('int32')
    fff = (df.id1 % 1_000_000 // 1000).astype('int32')
    cccfff = (df.id1 // 1000).astype('int32')
    b = (df.id1 % 1000 // 100).astype('int32')
    dd = (df.id1 % 100).astype('int32')

    v = (df.id2 // 100_000_000).astype('int32')
    llll = (df.id2 % 100_000_000 // 10_000).astype('int32')
    uuuu = (df.id2 % 10_000).astype('int32')

    t = (df.id3 // 100_000_000).astype('int32')
    # rr is modifier on date
    o = (df.id3 % 1_000_000 // 100_000).astype('int32')
    # hh should always be zero (not read)
    # ttt is lead
    #df['ttt'] = df.id3 % 1_000

    w = (df.id4 // 1_000_000_000).astype('int32')
    thresh_sign = w.apply(lambda x: -1 if x == 1 else 1)
    xxxx = (df.id4 % 1_000_000_000 // 100_000).astype('int32')
    yy = (df.id4 % 100_000 // 1000).astype('int32')
    yy[yy>=50] = (yy - 50) * -1
    thresh = (xxxx/10000 * 10.0**yy * thresh_sign).astype('float')

    i = (df.id4 % 1000 // 100).astype('int32')
    s = (df.id4 % 100 // 10).astype('int32')
    g = (df.id4 % 10).astype('int32')

    rr = (df.id3 % 100_000_000 // 1_000_000).astype('int')
    date = pd.to_datetime(df.date, format='%Y%m%d%H', errors='coerce')
    lead = pd.to_timedelta(df.lead, unit='hours')

    # parse dims to shape tuple
    # order as yx
    df = df[df.type == 'data']
    record_shape = df.dims.apply(dims_to_shape)

    df = df.assign(ccc=ccc, fff=fff, cccfff=cccfff, b=b, dd=dd,
            v=v, llll=llll, uuuu=uuuu,
            t=t, o=o,
            thresh=thresh,
            i=i, s=s, g=g,
            date=date, lead=lead,
            record_shape=record_shape)

    df = df.drop(['id1', 'id2', 'id3', 'id4', 'dims'], axis = 1)

    # remove any records with 1-9 stations as they are causing problems at the moment
  # df = df[df.record_shape != (1,)]
  # df = df[df.record_shape != (2,)]
  # df = df[df.record_shape != (3,)]
  # df = df[df.record_shape != (4,)]
  # df = df[df.record_shape != (5,)]
  # df = df[df.record_shape != (6,)]
  # df = df[df.record_shape != (7,)]
  # df = df[df.record_shape != (8,)]
  # df = df[df.record_shape != (9,)]

    return df


meta_formats = {
        'cccfff' : '{:06d}',
        'cccfffbdd' : '{:09d}',
        'ccc' : '{:03d}',
        'fff' : '{:03d}',
        'b' : '{:01d}',
        'dd' : '{:02d}',
        'v' : '{:01d}',
        'llll' : '{:04d}',
        'uuuu' : '{:04d}',
        't' : '{:01d}',
        'o' : '{:01d}',
        'thresh' : '{d}',
        }

def build_da_without_coords(index, cube, file, one_sorted_station_list:bool) -> xr.DataArray:
    dim_names = [k for k in cube.__dataclass_fields__.keys() if cube[k] is not None]
    constant_meta_names = [k for k in cube.__dataclass_fields__.keys() if cube[k] is None]
    dims = {k: len(cube[k]) for k in dim_names}

    data = OnDiskArray(file.name, index, cube, one_sorted_station_list)
    lock = LOCK
    data = TdlpackBackendArray(data, lock)
    data = indexing.LazilyIndexedArray(data)
    da = xr.DataArray(data, dims=dim_names)

    if 'station' in da.dims:
        da.encoding['preffered_chunks'] = {'station':-1}
    else:
        da.encoding['preffered_chunks'] = {'y':-1, 'x':-1}

    da.name = index.name.iloc[0]
    for meta_name in constant_meta_names:
        if meta_name in index.columns:
            da.attrs[meta_name] = index[meta_name].iloc[0]
            da.encoding[f'tdlp_{meta_name}'] = da.attrs[meta_name]

    return da

zfil = {
        'cccfff' : 6,
        'ccc' : 3,
        'fff' : 3,
        'b' : 1,
        'dd' : 2,
        'v' : 1,
        'llll' : 4,
        'uuuu' : 4,
        't' : 1,
        'o' : 1,
        'thresh' : 7,
        }
def _asarray_tuplesafe(values):
    """
    Convert values into a numpy array of at most 1-dimension, while preserving
    tuples.

    Adapted from pandas.core.common._asarray_tuplesafe
    grabbed from xarray because prefixed with _
    """
    if isinstance(values, tuple):
        result = utils.to_0d_object_array(values)
    else:
        result = np.asarray(values)
        if result.ndim == 2:
            result = np.empty(len(values), dtype=object)
            result[:] = values

    return result

def make_variables(index, name_scheme, filters, f):
    ''' from index as dataframe, separate by variable
        create an individual dataframe index and cube for each variable'''

    # let nam determine the variables
    #index['name'] = index[name_scheme].apply(lambda row: '_'.join(row.values.astype(str), axis=1)
    index.loc[:,'name'] = index[name_scheme].astype(str).apply(lambda col: col.str.zfill(zfil[col.name])).apply(lambda row: '_'.join(row), axis=1)

    # adopt parts of xarray's sel logic  so that filters behave similarly
    # allowed to filter to nothing to make empty dataset
    if filters:
        for k, v in filters.items():
            if isinstance(v, slice):
                index = index.set_index(k)
                index = index.loc[v]
                index = index.reset_index()
            else:
                label = (
                    v
                    if getattr(v, "ndim", 1) > 1  # vectorized-indexing
                    else _asarray_tuplesafe(v)
                    )
                if label.ndim == 0:
                    label_value = label[()] if label.dtype.kind in "mM" else label.item() # see https://github.com/pydata/xarray/pull/4292 for details
                    try:
                        indexer = pd.Index(index[k]).get_loc(label_value)
                        if isinstance(indexer, int):
                            index = index.iloc[[indexer]]
                        else:
                            index = index.iloc[indexer]
                    except KeyError:
                        index = index.iloc[[]]
                else:
                    indexer = pd.Index(index[k]).get_indexer_for(np.ravel(v))
                    index = index.iloc[indexer[indexer >= 0]]
    #      if isinstance(v, list):
    #          v = [int(k) if isinstance(v, str) else k for k in v]
    #      elif isinstance(v, str):
    #          v = [int(v)]
    #      elif isinstance(v, int):
    #          v = [v]
    #      filters[k] = index[k].isin(v)
    #   index = index[pd.DataFrame(filters).all(axis=1)]

    # set the index to the names components
    index = index.set_index(name_scheme).sort_index()
    # return nothing if no data
    if index.empty:
        return None,None,None,None,None


    ordered_meta = TdlpCube.__dataclass_fields__.keys()
    cube = None
    ordered_frames = list()
    for key in index.index.unique():
        frame = index.loc[[key]]
        frame = frame.reset_index()
        # frame is a dataframe with all records for one variable
        c = TdlpCube()
        for colname in frame.columns:
            if len(frame[colname].unique()) > 1:
                c[colname] = frame[colname].sort_values().unique()

        if c.date is None:
            # case where only one date; use date as unit dimesnion
            c['date'] = [frame.date.iloc[0]]
            #setattr(cube, 'date', [frame.date.iloc[0]])

        if c.lead is None:
            # case where only one lead; use lead as unit dimesnion
            c['lead'] = [frame.lead.iloc[0]]


        dims = [k for k in ordered_meta if c[k] is not None]

        for dim in dims:
            if frame[dim].value_counts().nunique() > 1:
                raise ValueError(f'un-even numer of records associated with dimension: {dim}\n unique values for {dim}: {frame[dim].unique()} ')

        frame = frame.sort_values(dims)
        frame = frame.set_index(dims)

        if cube:
            if cube != c:
                raise ValueError(f'{cube},\n {c};\n cubes are not the same; filter to a single cube')
        else:
            cube = c

        # miloc is multi-index integer location
        miloc = list(zip(*[frame.index.unique(level=dim).get_indexer(frame.index.get_level_values(dim)) for dim in dims]))
        frame = frame.assign(miloc=miloc)
        dim_ix = tuple([n+'_ix' for n in dims])
        frame = frame.set_index(pd.MultiIndex.from_tuples(frame.miloc, names=dim_ix))

        ordered_frames.append(frame)

    # no variables
    if cube is None:
        cube = TdlpCube()

    # check geography of data and assign to cube
    one_station_list = True
    record_shapes = index.record_shape.unique()
    if len(record_shapes) > 1:
        # records on file have multiple shapes
        if len(record_shapes[0]) == 1:
            # station records; check if the multiple station id records are identical
            station_id_records = index.linked_station_id_record.unique()
            if 0 in station_id_records:
                raise ValueError('tdlp file has a mix of station and gridded records; cannot read')
            if len(station_id_records) > 1:
                station = pd.Series(f[int(station_id_records[0])].stations, name='station')
                for station_record in station_id_records[1:]:
                    sta = pd.Series(f[int(station_record)].stations, name='station')
                    if not station.equals(sta):
                        # station lists on file are not all the same
                        logger.warning(f'station lists on file are not identical; loading of data will be less efficient')
                        one_station_list = False
                        station = pd.merge(station, sta, how='outer').station
            if station.is_monotonic_increasing:
                cube.station = station
                if one_station_list:
                    one_station_list_and_ordered = True
                else:
                    one_station_list_and_ordered = False
            else:
                logger.warning(f'station list(s) are not ordered; loading of data will be less efficient')
                one_station_list_and_ordered = False
                cube.station = station.sort_values()
        else:
            raise ValueError('multiple grids not accommodated')
    elif len(record_shapes) == 1:  # data records exist and have same shape
        if len(record_shapes[0]) == 1:
            rec = f[int(index.linked_station_id_record.iloc[0])]
            station_series = pd.Series(rec.stations, name='station')
            if station_series.is_monotonic_increasing:
                cube.station = station_series
                one_station_list_and_ordered = True
            else:
                logger.warning(f'station list(s) are not ordered; loading of data will be less efficient')
                cube.station = station_series.sort_values()
                one_station_list_and_ordered = False
        else:
            cube.y = range(index.record_shape.iloc[0][0])
            cube.x = range(index.record_shape.iloc[0][1])

    extra_geo = None
    rec = f[int(ordered_frames[0].record.iloc[0])]
    is2 = rec.is2
    if cube.x is not None:
        # we want the lat lons; make them via accessing a record; we are asuming all records are the same grid because they have the same shape;
        # may want a unique grid identifier from tdlpackio to avoid assuming this
        latitude, longitude = rec.latlons()
        latitude = xr.DataArray(latitude.transpose(), dims=['y','x'])
        latitude.attrs['standard_name'] = 'latitude'
        longitude = xr.DataArray(longitude.transpose() * -1, dims=['y','x'])
        longitude.attrs['standard_name'] = 'longitude'
        extra_geo = dict(latitude=latitude, longitude=longitude)
        one_station_list_and_ordered = None
    return ordered_frames, cube, extra_geo, one_station_list_and_ordered, is2


class Validator(ABC):
    def __set_name__(self, owner, name):
        self.private_name = f'_{name}'

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def get_name(self):
        ''' can be used by subclass with super().get_name() to discover
            the private name without _ ; helpfull for raising informative errors'''
        return self.private_name.strip('_')

    def __set__(self, obj, value):
        v = self.validate(value)
        if v is not None:
            value = v
        setattr(obj, self.private_name, value)
        if not hasattr(obj, '_validated'):
            obj._validated = []
        if self.private_name not in obj._validated:
            obj._validated.append(self.private_name)

    @abstractmethod
    def validate(self, value):
        ''' validate method can accept (null return), augment (return augmented)
        or raise an error'''
        pass

class Int(Validator):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def validate(self, value):
        if isinstance(value, (int, np.integer)):
            if self.min is not None:
                if self.min > value:
                    raise ValueError(f'Expected "{name}" value {value!r} to be >= {self.min}')
            if self.max is not None:
                if self.max < value:
                    raise ValueError(f'Expected "{name}" value {value!r} to be <= {self.max}')

            return value
        else:
            if self.min is not None:
                if self.min > value.min():
                    raise ValueError(f'Expected "{name}" min value {value!r} to be >= {self.min}')
            if self.max is not None:
                if self.max < value.max():
                    raise ValueError(f'Expected "{name}" max value {value!r} to be <= {self.max}')
            return pd.Index(value)

class Numeric(Validator):
    def __init__(self):
        pass

    def validate(self, value):
        if isinstance(value, numbers.Number):
            return value
        return pd.Index(value)  # no validation atm

class TimeDelta(Validator):
    def __init__(self):
        pass

    def validate(self, value):
        if isinstance(value, (datetime.timedelta, np.timedelta64)):
            return value
        return pd.TimedeltaIndex(value)

class DateTime(Validator):
    def __init__(self):
        pass

    def validate(self, value):
        if isinstance(value, (datetime.datetime, np.datetime64)):
            return value
        return pd.DatetimeIndex(value)


@dataclass(init=False)
class RequiredTdlpMeta():
    #Tdlpack metadata required as coord or in encoding
    date: datetime.datetime = DateTime()

    ccc: int = Int(min=0, max=999)
    fff: int = Int(min=0, max=999)
    b: int = Int(min=0, max=9)
    dd: int = Int(min=0, max=99)

    v: int = Int(min=0, max=9)
    llll: int = Int(min=0, max=9999)
    uuuu: int = Int(min=0, max=9999)

    t: int = Int(min=0, max=9)
#    rr: int = Int(min=0, max=99)
    o: int = Int(min=0, max=9)
#    hh: int = Int(min=0, max=99)
    lead: datetime.timedelta = TimeDelta()

    thresh: int = Numeric()
    i: int = Int(min=0, max=9)
    s: int = Int(min=0, max=9)
    g: int = Int(min=0, max=9)

    def __setitem__(self, key, value):
        #super().__setitem__(key, value)
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def to_id(self):
        for meta in self.__dataclass_fields__.keys():
            if isinstance(self[meta], pd.Index):
                raise ValueError(f'{meta} is an index, but must be singular to convert to an id')
        id1 = self.ccc * 1_000_000
        id1 += self.fff * 1000
        id1 += self.b * 100
        id1 += self.dd

        id2 = self.v * 100_000_000
        id2 += self.llll * 10_000
        id2 += self.uuuu

        id3 = self.t * 100_000_000
        id3 += self.o * 100_000
        id3 += int(pd.Timedelta(self.lead).total_seconds() / 3600)

        return[id1, id2, id3, 0]


@xr.register_dataset_accessor("tdlp")
class TdlpDataset:

    def __init__(self, xarray_obj):
        self._obj = xarray_obj


    def _iscoord(self, tdlp_meta):
        for coord_name in self._obj.coords:
            coord = self._obj[coord_name]
            if 'tdlp_name' in coord.attrs:
                if coord.attrs['tdlp_name'] == tdlp_meta:
                    return True
        return False

    def to_tdlpack(self, file, mode='w-', compute: bool = True, var_constants=None, min_unique=1000):
        '''
        mode : {"w", "w-"}, optional, default: "w-"
        Persistence mode: "w" means create (overwrite if exists);
        "w-" means create (fail if exists);
        '''

        have_chunks = any(v.chunks for v in self._obj.variables.values())
        # ensuring has x/y or station dims and that any chunks do not span those dims
        if 'station' in self._obj.dims:
            station = True
            if have_chunks:
                self._obj = self._obj.chunk({'station':-1})
        elif 'x' in self._obj.dims and 'y' in self._obj.dims:
            station = False
            if have_chunks:
                self._obj = self._obj.chunk({'x':-1, 'y':-1})
        else:
            raise ValueError("data does not have 'x' and 'y' or 'station' dims for writing to tdlp grid or station formats")

        # rename coordinates to tdlp_name attribute value
        for coord in self._obj.coords:
            if 'tdlp_name' in self._obj[coord].attrs:
                if self._obj[coord].attrs['tdlp_name'] not in self._obj.coords:
                    self._obj = self._obj.rename({coord : self._obj[coord].attrs['tdlp_name']})

        # make date and lead into dimensions if they are not
        if 'lead' not in self._obj.dims:
            self._obj = self._obj.expand_dims("lead")
        if 'date' not in self._obj.dims:
            self._obj = self._obj.expand_dims("date")

        possible_multi_var_keys=['ccc','fff','b','dd','v','llll','uuuu','t','o','i','s','g']
        multi_var_keys = [k for k in possible_multi_var_keys if not self._iscoord(k)]
        meta_dicts= list()
        for var in self._obj.data_vars:
            da = self._obj[var]
            meta_dicts.append({key: da.encoding[f'tdlp_{key}'] for key in multi_var_keys })
        df = pd.DataFrame(meta_dicts).nunique()
        meta_varying_by_var = df.index[df>1]



        meta = RequiredTdlpMeta()
        keys = list(meta.__dataclass_fields__.keys())
        coord_meta = list()
        const_meta = list()
        tdlpid = TdlpId()
        for key in keys:
            if f'tdlp_{key}' in da.encoding:
                meta[key] = da.encoding[f'tdlp_{key}']
                tdlpid[key] = meta[key]
                const_meta.append(key)
                continue
            found=False
            for coord_name in self._obj.coords:
                coord = self._obj[coord_name]
                if 'tdlp_name' in coord.attrs:
                    if coord.attrs['tdlp_name'] == key:
                        found=True
                        coord_meta.append(key)
                        meta[key] = coord
                        break
            if not found:
                raise ValueError(f'to_tdlpack requres metadata for {key} be in encoding or coordinate')


        filepath = Path(file)
        if mode == 'w-':
            if filepath.exists():
                raise ValueError(f"{file} already exists and will not be overwritten; mode: 'w' can overwrite existing files")
        elif mode == 'w':
            if filepath.is_dir():
                raise ValueError(f"cannot clobber directory {file}")

        open(filepath, 'w').close()
        store = filepath.parent / f'.{filepath.name}'
        if store.is_dir():
            logger.warning(f'removing existing hidden directory {store}')
            shutil.rmtree(store)
        store.mkdir(parents=True)

        prodicized = product(*[meta[k] for k in coord_meta])
        f = pytdlpack.open(store / filepath.name, mode='w', format='sequential')
        if station:
            template_rec = pytdlpack.TdlpackRecord(date=0, id=[0,0,0,0], data=np.array([0]))
            stations = pytdlpack.TdlpackStationRecord(list(self._obj.station.data))
            stations.pack()
            f.write(stations)
        else:
            # the grid doesn't matter ( can tweak/clean later)
            template_rec = pytdlpack.TdlpackRecord(date=0, id=[0,0,0,0], grid=pytdlpack.grids['nbmak'], data=np.array([0]))
            template_rec.is2 = da.encoding['tdlp_is2'] # this loads the grid metadata
        template_rec.primary_missing_value = 9999.0


        for t in prodicized:
            for var in self._obj.data_vars:
                # select slice of array for tdlpack record
                loc = {k:v for (k,v) in zip(coord_meta,t)}
                da = self._obj[var].loc[loc].squeeze()

                # put extra metadata that varies by variable in loc for updating tdlpid
                for m in meta_varying_by_var:
                    loc[m] = da.encoding[f'tdlp_{m}']
                tdlpid.update(**loc)

                # shape data array appropriately for station or grid formatted tdlpack record
                if station:
                    data = da.data
                else:
                    data = da.data.transpose()

                # build out a tdlpack DataRecord with appropriate metadata
                idlist = [tdlpid.word1, tdlpid.word2, tdlpid.word3, tdlpid.word4]
                if var_constants is None:
                    # look for plain text from encoding key "tdlp_plain"
                    if "tdlp_plain" in da.encoding:
                        plain = da.encoding["tdlp_plain"]
                        if len(plain) > pytdlpack.NCHAR_PLAIN:
                            raise ValueError(f"plain text '{plain}' exceeds {pytdlpack.NCHAR_PLAIN} characters")
                    else:
                        plain = 'NO PLAIN TEXT'
                    # let dec_scale allow for min_unique values in the space between the max and min
                    datamax = np.nanmax(data)
                    datamin = np.nanmin(data)
                    if datamax == datamin or np.isnan(datamax):
                        dec_scale = 9  # data is a constant or all missing and will compress well
                    else:
                        log10range = np.log10(np.nanmax(data)-np.nanmin(data))
                        range_place = np.floor(log10range)
                        dec_scale = int(np.ceil(np.log10(min_unique)) - range_place)
                else:
                    # TODO decide on whether to implement getting plain text or dec_scale from MOS2K constants file
                    # or remove this capability
                    raise NotImplementedError("var_constants is not implemented")
                    plain = var_constants.loc[tdlpid.cccfff]['plain']
                    dec_scale = var_constants.loc[tdlpid.cccfff]['iscale']

                date = da.date.data.squeeze()[()]
                rec = make_record(template_rec, idlist, data, plain, date)
                rec.pack(dec_scale=dec_scale)
                logger.debug(f'writing {date}, {idlist} with dec_scale: {dec_scale}')
                f.write(rec)

        f.close()
        shutil.move(store / filepath.name, file)
        shutil.rmtree(store)

@xr.register_dataarray_accessor("tdlp")
class TdlpDataarray:

    def __init__(self, xarray_obj):
        self._obj = xarray_obj

    def to_tdlpack(self, file, mode='w-', compute: bool = True, **kwargs):
        '''
        mode : {"w", "w-"}, optional, default: "w-"
        Persistence mode: "w" means create (overwrite if exists);
        "w-" means create (fail if exists);
        '''
        ds = self._obj.to_dataset()
        ds.tdlp.to_tdlpack(file, mode=mode, compute=compute, **kwargs)

def make_record(template, rec_id, data, plain, date):
    rec = copy(template)
    rec.data = data

    rec.id = rec_id
    rec.is1[8:12] = rec.id
    rec.is1[12] = rec.is1[10] % 1000
    rec.reference_date = pd.to_datetime(date)
    rec.is1[2] = int(rec.reference_date.strftime('%Y'))
    rec.is1[3] = int(rec.reference_date.strftime('%m'))
    rec.is1[4] = int(rec.reference_date.strftime('%d'))
    rec.is1[5] = int(rec.reference_date.strftime('%H'))
    rec.is1[7] = int(rec.reference_date.strftime('%Y%m%d%H'))

    rec.is4[2] = len(data)
    rec.number_of_values = rec.is4[2]

    rec.plain = plain
#    rec.lead_time = 24

    return rec

@dataclass
class TdlpId:
    word1: int = 0
    word2: int = 0
    word3: int = 0
    word4: int = 0

    # word1
    @property
    def ccc(self):
        return  self.word1 // 1_000_000
    @ccc.setter
    def ccc(self, value):
        self.word1 = self.word1 - self.ccc * 1_000_000 + value * 1_000_000

    @property
    def fff(self):
        return  self.word1 % 1_000_000 // 1000
    @fff.setter
    def fff(self, value):
        self.word1 = self.word1 - self.fff * 1000 + value * 1000

    @property
    def b(self):
        return  self.word1 % 1000 // 100
    @b.setter
    def b(self, value):
        self.word1 = self.word1 - self.b * 100 + value * 100

    @property
    def dd(self):
        return  self.word1 % 100
    @dd.setter
    def dd(self, value):
        self.word1 = self.word1 - self.dd + value

    # word2
    @property
    def v(self):
        return  self.word2 // 100_000_000
    @v.setter
    def v(self, value):
        self.word2 = self.word2 - self.v * 100_000_000 + value * 100_000_000

    @property
    def llll(self):
        return  self.word2 % 100_000_000 // 10_000
    @llll.setter
    def llll(self, value):
        self.word2 = self.word2 - self.llll * 10_000 + value * 10_000

    @property
    def uuuu(self):
        return  self.word2 % 10_000
    @uuuu.setter
    def uuuu(self, value):
        self.word2 = self.word2 - self.uuuu + value

    # word3
    @property
    def rr(self):
        return self.word3 % 100_000_000 // 1_000_000
    @rr.setter
    def rr(self, value):
        self.word3 = self.word3 - self.rr * 1_000_000 + value * 1_000_000

    @property
    def ttt(self):
        return self.word3 % 1_000
    @ttt.setter
    def ttt(self, value):
        self.word3 = self.word3 - self.ttt + value

    @property
    def lead(self):
        return datetime.timedelta(hours=self.ttt)
    @lead.setter
    def lead(self, value):
        self.ttt = int(pd.Timedelta(value).total_seconds() / 3600)

    # word4
    @property
    def w(self):
        return  self.word4 // 1_000_000_000
    @property
    def xxxx(self):
        return  self.word4 % 1_000_000_000 // 100_000
    @property
    def yy(self):
        return self.word4 % 100_000 // 1_000
    @property
    def wxxxxyy(self):
        return self.word4 // 1_000
    @wxxxxyy.setter
    def wxxxxyy(self, value):
        self.word4 = self.word4 - self.wxxxxyy * 1_000 + value * 1_000

    @property
    def isg(self):
        return self.word4 % 1000
    @isg.setter
    def isg(self, value):
        self.word4 = self.word4 - self.isg + value

    @property
    def i(self):
         return self.word4 % 1000 // 100
    @i.setter
    def i(self, value):
        self.word4 = self.word4 - self.i * 100 + value * 100

    @property
    def s(self):
        return self.word4 % 100 // 10
    @s.setter
    def s(self, value):
        self.word4 = self.word4 - self.s * 10 + value * 10

    @property
    def g(self):
        return self.word4 % 10
    @g.setter
    def g(self, value):
        self.word4 = self.word4 - self.g + value

    @property
    def thresh(self):
        return f'{self.w}.{self.xxxx:04}E{self.yy:02}'
    @thresh.setter
    def thresh(self, value):
        if value == 0:
            self.wxxxxyy = 0
            return
        n = np.log10(np.abs(value)).astype('int')
        n = n+1 if n > 0 else n
        xxxx = (np.abs(value) / 10.0**n * 10000).round(decimals=0).astype('int')
        wxxxx = xxxx+50000 if value < 0 else xxxx
        wxxxxyy = wxxxx * 100 + abs(n) if n >= 0 else wxxxx * 100 + abs(n) + 50
        self.wxxxxyy = wxxxxyy


    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def update(self, **kwargs):
        for k,v in kwargs.items():
            self[k] = v
