import pytest
import datetime
import hashlib
import numpy as np

import tdlpackio

def test_create_new_gridded_record():
    rec = tdlpackio.TdlpackRecord(type="grid")
    rec.refDate = datetime.datetime(2026, 2, 1, 12)
    rec.id = [4210008,10,24,0]
    rec.mapProjection = 3
    rec.nx = 2345
    rec.ny = 1597
    rec.latitudeLowerLeft = 19.2290
    rec.longitudeLowerLeft = 233.7234
    rec.orientationLongitude = 265.
    rec.standardLatitude = 25.
    rec.gridLength = 2.539703
    rec.data = np.random.rand(rec.nx*rec.ny).reshape(rec.shape)*75.0

    is0_hash_expected = "5b9e36ec3fb5698a93d45103ee2f541249c68be4"
    is1_hash_expected = "4a6e0e7ff594d3b2e28d9ea986cf28057db24255"
    is2_hash_expected = "57e02f2ffdb8d98ae12238766946edcf8e42c903"
    is4_hash_expected = "5b9e36ec3fb5698a93d45103ee2f541249c68be4"

    assert hashlib.sha1(rec.is0).hexdigest() == is0_hash_expected
    assert hashlib.sha1(rec.is1).hexdigest() == is1_hash_expected
    assert hashlib.sha1(rec.is2).hexdigest() == is2_hash_expected
    assert hashlib.sha1(rec.is4).hexdigest() == is4_hash_expected
