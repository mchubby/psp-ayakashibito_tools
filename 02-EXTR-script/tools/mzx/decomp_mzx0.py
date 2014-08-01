#!/usr/bin/env python

from struct import unpack

def mzx0_decompress(f, inlen, exlen, xorff=False):
    """Decompress a block of data.
    """
    dout = bytearray(b'\0' * (exlen+50)) # slightly overprovision for writes past end of buffer
    ringbuf = [b'\0'] * 128
    ring_wpos = 0
    clear_count = 0
    offset = 0
    max = f.tell() + inlen
    last1 = last2 = 0
    status = "UNK"
    try:
        while offset < exlen:
            if f.tell() >= max:
                break
            if clear_count <= 0:
                clear_count = 0x1000
                last1 = last2 = 0
            flags = ord(f.read(1))
            #print("+ %X %X %X" % (flags, f.tell(), offset))
            
            clear_count -= 1 if (flags & 0x03) == 2 else flags // 4 + 1

            if flags & 0x03 == 0:
                for i in range(flags // 4 + 1):
                    dout[offset  ] = last1
                    dout[offset+1] = last2
                    offset += 2

            elif flags & 0x03 == 1:
                k = ord(f.read(1))
                k = 2 * (k+1)
                for i in range(flags // 4 + 1):
                    # read two previous bytes in sliding
                    dout[offset] = dout[offset - k]
                    offset += 1
                    dout[offset] = dout[offset - k]
                    offset += 1

                last1 = dout[offset-2]
                last2 = dout[offset-1]

            elif flags & 0x03 == 2:
                dout[offset  ] = last1 = ringbuf[2 * (flags // 4)]
                dout[offset+1] = last2 = ringbuf[2 * (flags // 4) + 1]
                offset += 2

            else:
                for i in range(flags // 4 + 1):
                    if f.tell() >= max:
                        break
                    last1 = ringbuf[ring_wpos] = dout[offset] = ord(f.read(1))
                    ring_wpos += 1
                    offset += 1
                    last2 = ringbuf[ring_wpos] = dout[offset] = ord(f.read(1))
                    ring_wpos += 1
                    offset += 1
                    ring_wpos &= 0x7F

            if offset >= exlen:
                break
        status = "OK"
    except IndexError:
        status = "ERR"
        pass

    key = 0xFF
    return [status, bytearray(x ^ key for x in dout[0:exlen])] if xorff else [status, dout[0:exlen]]
