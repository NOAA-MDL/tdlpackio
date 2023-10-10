"""Utilities for handling MOS2K-related objects"""

def parse_id(mosid: list) -> dict:
    """
    Parse a 4-Word MOS-2000 ID into its 15 components and the threshold
    value.

    Parameters
    ----------
    mosid : list
        The 4-word, integer MOS-2000 ID.

    Returns
    -------
    idprs : dict
        Dictionary where the keys are the names of the components
        and values are the integer parsed id component along with
        the floating-point threshold.
    """
    id1 = str(mosid[0]).zfill(9)
    id2 = str(mosid[1]).zfill(9)
    id3 = str(mosid[2]).zfill(9)
    id4 = str(mosid[3]).zfill(10)

    idprs = dict()
    idprs['ccc'] = int(id1[0:3].lstrip('0') or 0)
    idprs['fff'] = int(id1[3:6].lstrip('0') or 0)
    idprs['b'] = int(id1[6])
    idprs['dd'] = int(id1[7:9].lstrip('0') or 0)
    idprs['v'] = int(id2[0])
    idprs['llll'] = int(id2[1:4].lstrip('0') or 0)
    idprs['uuuu'] = int(id2[5:9].lstrip('0') or 0)
    idprs['t'] = int(id3[0])
    idprs['rr'] = int(id3[1:3].lstrip('0') or 0)
    idprs['o'] = int(id3[3])
    idprs['hh'] = int(id3[4:6].lstrip('0') or 0)
    idprs['ttt'] = int(id3[6:9].lstrip('0') or 0)
    idprs['i'] = int(id4[7])
    idprs['s'] = int(id4[8])
    idprs['g'] = int(id4[9])

    sign = int(id4[0])
    if sign == 0:
        sign = 1
    elif sign == 1:
        sign = -1

    exp = int(id4[5:7].lstrip('0') or 0)
    exp = -1*(50-exp) if exp >= 50 else exp

    fraction = int(id4[1:5].lstrip('0') or 0)
    exp = 1 if fraction == 0 else exp

    idprs['thresh'] = (sign*float(fraction))**exp

    return idprs
