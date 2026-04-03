import hashlib
import pytest
import tdlpackio


def test_new_station_object():
    # Empty
    rec = tdlpackio.TdlpackStationRecord()
    assert rec.stations is None
    assert rec.numberOfStations == 0

    # Non-empty
    test_stations = ["KACY", "KBWI", "KDCA", "KIAD", "KPHL"]
    rec = tdlpackio.TdlpackStationRecord(test_stations)
    assert rec.stations == test_stations
    assert rec.numberOfStations == len(test_stations)

    # FUTURE...
    #rec = tdlpackio.TdlpackStationRecord(["kacy", " kbwi "])
    #assert rec.stations == ["KACY", "KBWI"]


def test_stations_from_file(request):
    data = request.config.rootdir / "tests" / "data"

    f = tdlpackio.open(data / "hre201701.sq")
    try:
        rec = f[0]

        assert rec._source is not None
        assert rec.numberOfStations == 2892

        digest = hashlib.sha1("".join(rec.stations).encode("ascii")).hexdigest()
        assert digest == "7ad0c02a504ad2dc5d13aa88a185429db8acd3a1"

        with pytest.raises(AttributeError, match=r"cannot be modified"):
            rec.stations = []
    finally:
        if hasattr(f, "close"):
            f.close()


@pytest.mark.parametrize("bad_value", ["KBWI", b"KBWI", 5, object()])
def test_invalid_station_inputs(bad_value):
    rec = tdlpackio.TdlpackStationRecord()
    with pytest.raises(TypeError, match=r"stations"):
        rec.stations = bad_value
