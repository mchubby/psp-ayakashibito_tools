#!/usr/bin/env python
import os, errno
import sys
from sys import stderr
from struct import unpack
import glob
import re
from mzx.decomp_mzx0 import mzx0_decompress

for filepath in glob.iglob('*.[Mm][Zz][Xx]'):
    basestem = os.path.splitext(os.path.basename(filepath))[0]
    outpath = basestem + '.out'
    with open(filepath, 'rb') as data:
        offset = 7 if(data.read(2) == b'LV') else 0
        data.seek(offset)
        sig, size = unpack('<LL', data.read(0x8))
        status, decbuf = mzx0_decompress(data, os.path.getsize(filepath) - 8 - offset, size)
        if status != "OK": print("[{0}] {1}".format(filepath, status), file=stderr)
        with open(outpath, 'wb') as dbg:
            dbg.write(decbuf)

