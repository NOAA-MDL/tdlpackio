import pytest
import datetime
import hashlib
import numpy as np

import tdlpackio


def test_create_new_gridded_record():
    rec = tdlpackio.TdlpackRecord(grid="nbmco")
    rec.refDate = datetime.datetime(2026, 2, 1, 12)
    rec.id = [4210008, 10, 24, 0]
    rec.data = np.random.rand(rec.nx * rec.ny).reshape(rec.shape) * 75.0

    is0_hash_expected = "5b9e36ec3fb5698a93d45103ee2f541249c68be4"
    is1_hash_expected = "4a6e0e7ff594d3b2e28d9ea986cf28057db24255"
    is2_hash_expected = "8698f5c0dd78aaf54830cdfe58d5e90ee838c001"
    is4_hash_expected = "5b9e36ec3fb5698a93d45103ee2f541249c68be4"

    assert hashlib.sha1(rec.is0).hexdigest() == is0_hash_expected
    assert hashlib.sha1(rec.is1).hexdigest() == is1_hash_expected
    assert hashlib.sha1(rec.is2).hexdigest() == is2_hash_expected
    assert hashlib.sha1(rec.is4).hexdigest() == is4_hash_expected
