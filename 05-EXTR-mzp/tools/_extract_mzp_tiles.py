import os, sys
from struct import unpack, pack
from subprocess import call
import glob

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
    paletteblob = b'';
    bitmapbpp    =    4 if unk == 0x10 else 8
    palettecount = 0x10 if unk == 0x10 else 0x100
    print(palettecount)
    
    for i in range(palettecount):
        r = desc.read(1)
        g = desc.read(1)
        b = desc.read(1)
        paletteblob += (b + g + r + desc.read(1))

    for infilepath in glob.iglob("*.out"):
        print(infilepath)
        outfilepath = outfilepattern.format(infilepath)
        with open(outfilepath, 'wb') as outfile:
            outfile.write(b"\x00\x01\x01\x00\x00" + pack("<H", palettecount) + b"\x20\x00\x00\x00\x00" + pack('<HHBB', tile_width, tile_height, 8, 0x20|bitmapbpp))
            outfile.write( paletteblob )
            data = open(infilepath,'rb').read()
            if len(data) < tile_width * tile_height * bitmapbpp // 8:
                print("Not enough data: {} {}".format(len(data), tile_width * tile_height * bitmapbpp // 8))
            outfile.write( data )
        #call(["cmd", "/c", "start", outfilepath])