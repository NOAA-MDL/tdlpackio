import argparse
import numpy as np
import sys
import tdlpackio

DESCRIPTION = """
itdlp - a command line utility to inventory MDL's MOS-2000 TDLPACK files.
"""

V_HELP = """
Verbose inventory.  Data are unpacked.  Print statistics (max, min, mean values) and
information and counts of missing values.
"""


def verbose(rec):
    """
    """
    npmiss = np.count_nonzero(rec.data==rec.primaryMissingValue)
    nsmiss = np.count_nonzero(rec.data==rec.secondaryMissingValue)

    data = rec.data
    data[data==rec.primaryMissingValue] = np.nan
    data[data==rec.secondaryMissingValue] = np.nan

    dmin = np.nanmin(data)
    dmax = np.nanmax(data)
    dmean = np.mean(data)

    output = []
    output.append((f'    MAX = {dmax:0.3f}'
                   f':MIN = {dmin:0.3f}'
                   f':MEAN = {dmean:0.3f}\n'))
    output.append((f'    PMISS = {rec.primaryMissingValue:0.0f}'
                   f':SMISS = {rec.secondaryMissingValue:0.0f}\n'))
    output.append((f'    NDATA = {rec.numberOfPackedValues:0.0f}'
                   f':NPMISS = {npmiss:01d}'
                   f':NSMISS = {nsmiss:01d}'))
    return ''.join([s for s in output])


def _itdlp_main():
    """
    """
    parser = argparse.ArgumentParser(prog='itdlp',
                                     description=DESCRIPTION)
    parser.add_argument('file')
    parser.add_argument('-v', dest='verbose', action='store_true', help=V_HELP)
    args = parser.parse_args()

    f = tdlpackio.open(args.file)
    for rec in f:

        recstr = list(rec.__str__().split(':'))
        print(':'.join([s for s in recstr]),flush=True)

        if not hasattr(rec,'type'): continue

        if args.verbose: print(verbose(rec),flush=True)

    f.close()
