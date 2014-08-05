import os, sys
from struct import unpack, pack
from subprocess import call
import glob
import zlib
 

# http://blog.flip-edesign.com/?p=23
class Byte(object):
    def __init__(self, number):
        self.number = number

    @property
    def high(self):
        return self.number >> 4

    @property
    def low(self):
        return self.number & 0x0F


def write_pngsig(f):
    f.write(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A')

def write_pngchunk_withcrc(f, type, data):
    f.write(pack(">I",len(data)))
    f.write(type)
    f.write(data)
    f.write(pack(">I",zlib.crc32(type+data, 0)& 0xffffffff))


"""
   color = 1 (palette used), 2 (color used), and 4 (alpha channel used). Valid values are 0, 2, 3, 4, and 6. 
 
   Color    Allowed    Interpretation
   Type    Bit Depths
   
   0       1,2,4,8,16  Each pixel is a grayscale sample.
   
   2       8,16        Each pixel is an R,G,B triple.
   
   3       1,2,4,8     Each pixel is a palette index;
                       a PLTE chunk must appear.
   
   4       8,16        Each pixel is a grayscale sample,
                       followed by an alpha sample.
   
   6       8,16        Each pixel is an R,G,B triple,
                       followed by an alpha sample.
"""
def write_ihdr(f, width, height, depth, color):
    chunk = pack(">IIBB",width,height,depth,color) + b'\0\0\0'
    write_pngchunk_withcrc(f, b"IHDR", chunk)

def write_plte(f, palettebin):
    write_pngchunk_withcrc(f, b"PLTE", palettebin)

def write_trns(f, transparencydata):
    write_pngchunk_withcrc(f, b"tRNS", transparencydata)

def write_idat(f, pixels):
    write_pngchunk_withcrc(f, b"IDAT", zlib.compress(pixels))

def write_iend(f):
    write_pngchunk_withcrc(f, b"IEND", b"")

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]

###############################################
# struct TGAHeader
# {
#   uint8   idLength,           // Length of optional identification sequence.
#           paletteType,        // Is a palette present? (1=yes)
#           imageType;          // Image data type (0=none, 1=indexed, 2=rgb,
#                               // 3=grey, +8=rle packed).
#   uint16  firstPaletteEntry,  // First palette index, if present.
#           numPaletteEntries;  // Number of palette entries, if present.
#   uint8   paletteBits;        // Number of bits per palette entry.
#   uint16  x,                  // Horiz. pixel coord. of lower left of image.
#           y,                  // Vert. pixel coord. of lower left of image.
#           width,              // Image width in pixels.
#           height;             // Image height in pixels.
#   uint8   depth,              // Image color depth (bits per pixel).
#           descriptor;         // Image attribute flags.
# };

if __name__ == '__main__':
    outfilepattern = "tile{}.tga"
    # indexed 8bpp RGBa with 256-entry RGBa palette (0x400 bytes)
    #bm_bpp = 8
    #bm_pal = 0x400

    desc = open(glob.glob("*000.bin")[0], 'rb')
    width, height, tile_width, tile_height, tile_x_count, tile_y_count, bmp_type, unk = unpack('<HHHHHHHH', desc.read(0x10))
    paletteblob = b''
    palettepng = b''
    transpng = b''
    imagedata = b''
    bitmapbpp    =    4 if unk == 0x10 else 8
    palettecount = 0x10 if unk == 0x10 else 0x100
    
    
    for i in range(palettecount):
        r = desc.read(1)
        g = desc.read(1)
        b = desc.read(1)
        a = desc.read(1)
        paletteblob += (b + g + r + a)
        palettepng += (r + g + b)
        transpng += a
    for i in range(palettecount, 0x100):
        paletteblob += b'\x00\x00\x00\xFF'
        palettepng += b'\x00\x00\x00'
        transpng += b'\xFF'

    for infilepath in glob.iglob("*.out"):
        print(infilepath)
        outfilepath = outfilepattern.format(infilepath)
        with open(outfilepath, 'wb') as outfile:
            outfile.write(b"\x00\x01\x01\x00\x00" + pack("<H", 0x100) + b"\x20\x00\x00\x00\x00" + pack('<HHBB', tile_width, tile_height, 8, 0x20|8))
            outfile.write( paletteblob )
            data = open(infilepath,'rb').read()
            if len(data) < tile_width * tile_height * bitmapbpp // 8:
                print("Not enough data: {} {}".format(len(data), tile_width * tile_height * bitmapbpp // 8))
            if bitmapbpp == 8:
                outfile.write( data )
            elif bitmapbpp == 4:
                for octet in data:
                    thebyte = Byte(octet)
                    imagedata += pack('BB', thebyte.high, thebyte.low)
                data = imagedata
                outfile.write( data )

        # uses from just above loop: data
        with open("ztile{}.png".format(infilepath), 'wb') as pngout:
            write_pngsig(pngout)
            write_ihdr(pngout, tile_width, tile_height, 8, 3)  # 8bpp (PLTE)
            write_plte(pngout, palettepng)
            write_trns(pngout, transpng)

            # split into rows and add png filtering info (mandatory even with no filter)
            rowdata = b''
            for i, rowrawpixels in enumerate(chunks(data, tile_width)):
                rowdata += b'\x00' + rowrawpixels
            
            write_idat(pngout, rowdata)
            write_iend(pngout)

        #call(["cmd", "/c", "start", outfilepath])