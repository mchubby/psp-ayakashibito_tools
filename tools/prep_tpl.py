#!/usr/bin/env python

"""prep_tpl version 1.0, Copyright (C) 2014 Nanashi3.

prep_tpl comes with ABSOLUTELY NO WARRANTY.

Usage:
prep_tpl.py ../allpac-unpacked
"""

import os, errno
import sys
from sys import stderr
from struct import unpack
import glob
import re
from mzx.decomp_mzx0 import mzx0_decompress

class CustomException(Exception):
    pass

LINE_WIDTH = 88

def write_line(strline):
    print(strline * LINE_WIDTH, file=stderr)

def makedir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(dirname):
            pass
        else: raise

makedir("10rawscript")
makedir("20decodedscript")

def process_directory(sourcedirpath):
    successful = failed = 0
    for filepath in glob.iglob(os.path.join(sourcedirpath, '*.[Mm][Zz][Xx]')):
        s = process_path(filepath)
        if s != "OK":
            failed += 1
        else:
            successful += 1
    return [successful, failed]

def process_path(sourcepath):
    sourcepath = os.path.normpath(sourcepath)
    basestem = os.path.splitext(os.path.basename(sourcepath))[0]
    outtxtpath = basestem + '.ini'
    outtplpath = basestem + '.tpl.txt'
    #print("[{0}]".format(sourcepath), file=stderr)
    with open(sourcepath, 'rb') as data:
        sig, size = unpack('<LL', data.read(0x8))
        status, decbuf = mzx0_decompress(data, os.path.getsize(sourcepath) - 8, size, xorff=True)
        if status != "OK": print("[{0}] {1}".format(sourcepath, status), file=stderr)
        fn = os.path.join("10rawscript", outtxtpath)
        with open(fn, 'wb') as dbg:
            dbg.write(decbuf)
        
        outcoll = []
        counter = 0
        for instr in decbuf.split(b';'):
            counter += 1
            instrtext = instr.decode('cp932')
            if re.search(r'_LVSV|_STTI|_MSAD|_ZM|SEL[R]', instrtext) is not None:
                outcoll.append("<{0:04d}>".format(counter) + instrtext.replace("^", "_r").replace("@n", "_n").replace(",", ";/")); # replace order significant
            elif len(re.sub('[ -~]', '', instrtext)) > 0:
                outcoll.append(u"!" + instrtext)  # flag missing matches containing non-ASCII characters
            else:
                outcoll.append(u"~" + instrtext + u"~")  # non-localizable

        if len(outcoll) > 0:
            fnprep = os.path.join("20decodedscript", outtplpath)
            with open(fnprep, 'wt', encoding="utf-8") as outfile:
                outfile.write(u"\n".join(outcoll))

    return status

"""
debugging:
    try:
        suite
    except Exception as exc:
        print("ERR: [{0}] - {1}".format(type(exc).__name__, str(exc)), file=stderr)
        sys.exit(1)
"""

############
# __main__ #
############

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('Usage: {} dir_with_mzx_files'.format(sys.argv[0]), file=stderr)
        sys.exit(20)
    successful = failed = 0

    if str.upper(os.path.splitext(sys.argv[1])[1]) == '.MZX':
        s = process_path(sys.argv[1])
        if s != "OK":
            successful = 0
            failed = 1
        else:
            successful = 1
            failed = 0
    else:
        successful, failed = process_directory(sys.argv[1])
    print("{0} scripts, {1} SUCCESS, {2} FAILURE".format(successful+failed, successful, failed), file=stderr)

    sys.exit(0)

