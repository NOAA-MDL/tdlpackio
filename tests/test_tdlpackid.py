import hashlib
import pytest
import tdlpackio

TEST_ID = [222330068, 0, 120, 123450000]


def test_tdlpackid():

    a = tdlpackio.TdlpackID(TEST_ID)

    assert f"{a:basic}" == "222330068 000000000 000000120 0123400000"
    assert f"{a:mos}" == "222330068 000000000 000000120 000 1.2340e+03"
    assert f"{a:parsed}" == "222 330 0 68 0 0000 0000 0 00 0 00 120 0 0 0   1234.000000"
