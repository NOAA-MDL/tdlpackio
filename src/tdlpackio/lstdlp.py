import argparse
import numpy as np
import signal
import sys
import tdlpackio

DESCRIPTION = """
lstdlp - a command-line utility to inventory MDL's MOS-2000 TDLPACK files based
the tdlpackio Python package.
"""

QUIET_HELP = """
Quiet mode.  Suppress all inventory output.  Only errors are printed to
standard output.
"""

REC_HELP = """
Inventory TDLPACK records with record number REC.  REC can be a comma-delimited
list of numbers and/or ranges (e.g. 1,2,5,6,10-20)
"""

TDLP_HELP = """
Output TDLPACK records to new sequential file FILE.
"""

VERBOSE_HELP = """
Verbose inventory.  Data are unpacked and statistics (max, min, mean values); 
counts of missing values are provided.
"""

def process_user_rec(rec):
    """
    Process record numbers and ranges from the user via -rec argument.
    """
    recs = list()
    for r in rec.split(','):
        if '-' in r:
            start, stop = r.split('-')
            recs += list(range(int(start),int(stop)+1,1))
        else:
            recs.append(int(r))
    return recs


def signal_handler(sig, frame):
    """
    """
    exit(0)


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


def _lstdlp_main():
    """
    """
    # Define and parse args
    parser = argparse.ArgumentParser(prog='lstdlp',
                                     description=DESCRIPTION)
    parser.add_argument('file')
    parser.add_argument('-q', dest='quiet', action='store_true', help=QUIET_HELP)
    parser.add_argument('-rec', dest='rec', type=process_user_rec, help=REC_HELP)
    parser.add_argument('-tdlp', dest='tdlp', action='store', help=TDLP_HELP)
    parser.add_argument('-v', dest='verbose', action='store_true', help=VERBOSE_HELP)
    args = parser.parse_args()

    # Capture signals
    signal.signal(signal.SIGINT,signal_handler)

    # Open input file and create iterable collection of records based on user
    # supplied args
    f = tdlpackio.open(args.file)
    fiter = f
    if args.rec is not None:
        fiter = [f[r] for r in args.rec]

    # Check if writing to new file.
    if args.tdlp is not None: fout = tdlpackio.open(args.tdlp,mode='w',format='sequential')

    # Iterate over records
    for rec in fiter:

        # Default inventory print
        if not args.quiet:
            recstr = list(rec.__str__().split(':'))
            print(':'.join([s.rstrip() for s in recstr]),flush=True)

        #
        if not hasattr(rec,'_data'):
            continue

        # Verbose mode
        if args.verbose and not args.quiet:
            print(verbose(rec),flush=True)
            rec.flush_data()

        # Output records to new file
        if args.tdlp is not None:
            rec.pack()
            fout.write(rec)

    # Close input file
    f.close()
    # Close output file
    if args.tdlp is not None: fout.close()
