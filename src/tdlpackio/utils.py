"""Utilities for handling TDLPACK-related objects"""

def parse_id(mosid: list) -> dict:
    """
    Parse a 4-Word TDLPACK variable ID into its 15 components and the threshold
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

    idprs = {}
    idprs['ccc'] = int(id1[0:3].lstrip('0') or 0)
    idprs['fff'] = int(id1[3:6].lstrip('0') or 0)
    idprs['b'] = int(id1[6])
    idprs['dd'] = int(id1[7:9].lstrip('0') or 0)
    idprs['v'] = int(id2[0])
    idprs['llll'] = int(id2[1:5].lstrip('0') or 0)
    idprs['uuuu'] = int(id2[5:9].lstrip('0') or 0)
    idprs['t'] = int(id3[0])
    idprs['rr'] = int(id3[1:3].lstrip('0') or 0)
    idprs['o'] = int(id3[3])
    idprs['hh'] = int(id3[4:6].lstrip('0') or 0)
    idprs['tau'] = int(id3[6:9].lstrip('0') or 0)
    idprs['i'] = int(id4[7])
    idprs['s'] = int(id4[8])
    idprs['g'] = int(id4[9])

    sign = 1 if int(id4[0]) == 0 else -1
    fraction = int(id4[1:5].lstrip('0') or 0)

    exp = int(id4[5:7].lstrip('0') or 0)
    exp = int(-1*(exp-50)) if exp >= 50 else exp
    exp = 1 if fraction == 0 else exp

    idprs['thresh'] = sign*(float(fraction)*10**exp)

    return idprs

def unparse_id(parsedid: dict) -> list:
    """
    Unparse the TDLPACK variable components into the 4-word TDLPACK
    variable ID.

    Parameters
    ----------
    parsedid : dict
        The parsed ID dictionary.

    Returns
    -------
    list
        The 4-word TDLPACK variable ID.
    """
    id1 = str(parsedid['ccc']).zfill(3)+str(parsedid['fff']).zfill(3)+\
          str(parsedid['b'])+str(parsedid['dd']).zfill(2)
    id2 = str(parsedid['v'])+str(parsedid['llll']).zfill(4)+\
          str(parsedid['uuuu']).zfill(4)
    id3 = str(parsedid['t'])+str(parsedid['rr']).zfill(2)+\
          str(parsedid['o'])+str(parsedid['hh']).zfill(2)+\
          str(parsedid['tau']).zfill(3)
    id4 = encode_threshold_for_id(parsedid['thresh'])+\
          str(parsedid['i'])+\
          str(parsedid['s'])+\
          str(parsedid['g'])

    return [int(id1.lstrip('0') or 0), int(id2.lstrip('0') or 0),
            int(id3.lstrip('0') or 0), int(id4.lstrip('0') or 0)]

def encode_threshold_for_id(thresh: float):
    """
    Encode a threshold floating-point value for a TDLPACK ID.

    Parameters
    ----------
    thresh : float
        Threshold value.

    Returns
    -------
        A numeric string of the encoded threshold value.
    """
    exp = 0
    sign = 1 if thresh >= 0 else -1
    thresh = abs(thresh)
    ival, ifrac = str(thresh).split('.')
    ival = '' if ival == '0' else ival
    ifrac = '' if ifrac == '0' else ifrac
    nval, nfrac = len(ival), len(ifrac)
    if nval == 0 and nfrac > 0:
        exp = 4
        ithresh = ifrac.ljust(4,'0')[:4]
    elif nval > 0 and nfrac == 0:
        exp = 4 - nval if nval <= 4 else 0
        ithresh = ival.ljust(4,'0')[:4]
    else:
        ndigits = nval+nfrac
        if ndigits < 4:
            exp = ndigits
        elif ndigits >= 4:
            exp = 4-nval
            exp = 0 if nval >= 4 else exp
        ithresh = (ival+ifrac).ljust(4,'0')[:4]
    exp = -exp
    w = '0' if sign == 1 else '1'
    yy = str(50+abs(exp)) if exp < 0 else str(abs(exp)).zfill(2)
    return w+ithresh+yy
