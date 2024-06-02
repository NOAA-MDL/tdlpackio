import pytest
import datetime
import hashlib
import tdlpackio

def test_tdlpack_gridded_record_attrs(request):
    data = request.config.rootdir / 'sampledata'
    f = tdlpackio.open(data / 'gfspkd47.2017020100.sq' )
    rec = f[5]
    assert rec.edition == 0
    assert rec.sectionFlags == '00000001'
    assert rec.year == 2017
    assert rec.month == 2
    assert rec.day == 1
    assert rec.hour == 0
    assert rec.minute == 0
    assert rec.refDate == datetime.datetime(2017, 2, 1, 0)
    assert rec.id == [1000008, 850, 0, 0]
    assert rec.id.to_string() == '001000008 000000850 000000000 0000000000'
    assert rec.leadTime == datetime.timedelta(hours=0)
    assert rec.leadTimeMinutes == 0
    assert rec.modelID == 8
    assert rec.modelSequenceID == 1
    assert rec.decScaleFactor == 0
    assert rec.binScaleFactor == 0
    assert rec.name.strip() ==  '850 MB HGT GFS'
    assert rec.validDate == datetime.datetime(2017, 2, 1, 0)
    assert rec.duration == datetime.timedelta(hours=0)
    assert rec.mapProjection == 5
    assert rec.nx == 297
    assert rec.ny == 169
    assert rec.latitudeLowerLeft == 2.8320000000000003
    assert rec.longitudeLowerLeft == 150.0
    assert rec.orientationLongitude == 105.0
    assert rec.gridLength == 47625.0
    assert rec.standardLatitude == 60.0
    assert rec.packingFlags == '00001100'
    assert rec.numberOfPackedValues == 50193
    assert rec.primaryMissingValue == 0
    assert rec.secondaryMissingValue == 0
    assert rec.overallMinValue == 0
    assert rec.numberOfGroups == 0
    # Check data
    assert hashlib.sha1(rec.data).hexdigest() == '124d6c2666dfa8ffd024042ef3f246fcc2771672'
    f.close()

def test_tdlpack_station_record_attrs(request):
    data = request.config.rootdir / 'sampledata'
    f = tdlpackio.open(data / 'hre201701.sq' )
    rec = f[5]
    assert rec.edition == 0
    assert rec.sectionFlags == '00000000'
    assert rec.year == 2017
    assert rec.month == 1
    assert rec.day == 1
    assert rec.hour == 0
    assert rec.minute == 0
    assert rec.refDate == datetime.datetime(2017, 1, 1, 0)
    assert rec.id == [702000000, 0, 0, 0]
    assert rec.id.to_string() == '702000000 000000000 000000000 0000000000'
    assert rec.leadTime == datetime.timedelta(hours=0)
    assert rec.leadTimeMinutes == 0
    assert rec.modelID == 0
    assert rec.modelSequenceID == 0
    assert rec.decScaleFactor == 0
    assert rec.binScaleFactor == 0
    assert rec.name.strip('\x00').strip() ==  'OBS TEMPERATURE'
    assert rec.validDate == datetime.datetime(2017, 1, 1, 0)
    assert rec.duration == datetime.timedelta(hours=0)
    assert rec.packingFlags == '00011010'
    assert rec.numberOfPackedValues == 2892
    assert rec.primaryMissingValue == 9999
    assert rec.secondaryMissingValue == 0
    assert rec.overallMinValue == 0
    assert rec.numberOfGroups == 0
    # Check station list
    station_hash = hashlib.sha1(''.join([s for s in rec.stations]).encode('ASCII')).hexdigest()
    assert station_hash == '7ad0c02a504ad2dc5d13aa88a185429db8acd3a1'
    # Check data
    assert hashlib.sha1(rec.data).hexdigest() == 'ce08ac287b1fb6eddb9409feeeb3e5d860894b95'
    f.close()
    
