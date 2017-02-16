#!/usr/bin/env python
#
# MZP Extractor version 1.0
# comes with ABSOLUTELY NO WARRANTY.
#
# Copyright (C) 2016 Hintay <hintay@me.com>
# Portions Copyright (C) 2016 Quibi
#
# MZP image files extraction utility
# For more information, see Specifications/mzp_format.md

from _extract_mzp_tiles import *
import struct
import os
import argparse

class ArchiveEntry:
	def __init__(self, sector_offset, offset, sector_size_upper_boundary, size, number_of_entries):
		self.sector_offset = sector_offset
		self.offset = offset
		self.sector_size_upper_boundary = sector_size_upper_boundary
		self.size = size
		self.real_size = (sector_size_upper_boundary - 1) // 0x20 * 0x10000 + size
		data_start_offset = 6 + 2 + number_of_entries * 8
		self.real_offset = data_start_offset + self.sector_offset * 0x800 + self.offset

#############################################################################
def parse_args():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-b', '--bin',
		action='store_true', dest='bin',
		help='just extract MZP to bin and not output PNGs')
	parser.add_argument('-n', '--notmzx',
		action='store_true', dest='notmzx',
		help='do not extract MZX that extracted from MZP')
	parser.add_argument('-i', '--ignore_extracted',
		action='store_true', dest='ignore_extracted',
		help='do not extract MZP that already extracted')
	parser.add_argument('input', metavar='input.mzp', help='input .mzp file')

	return parser, parser.parse_args()

#############################################################################
# extract verb #
################
def extract_check(args):
	if not os.path.exists(args.input):
		parser.print_usage()
		print('Error: the following file or folder does not exist: ' + args.input)
		sys.exit(20)

	if os.path.isfile(args.input):
		extract_verb(args)
	else: # ÎÄ¼þ¼Ð
		for root, dirs, files in os.walk(args.input):
			for file in files:
				if file.endswith('MZP'):
					extract_verb(args, root, file)

def extract_verb(args, root = '.', file = None):
	input_file_name = os.path.join(root, file) if(file != None) else args.input
	input_base_name = os.path.splitext(input_file_name)[0]

	if(args.ignore_extracted and os.path.exists(input_base_name+'.png')): return

	with open(input_file_name, 'rb') as input_file:
		header = input_file.read(6)
		if(header != b'mrgd00'): return

		print('\nExtracting from ' + input_file_name, file=sys.stderr)
		print('header: {0}'.format(header.decode('ASCII')))

		number_of_entries, = struct.unpack('<H', input_file.read(2))
		print('found {0} entries'.format(number_of_entries))
		if(not number_of_entries): return

		entries_descriptors = []
		for i in range(number_of_entries):
			sector_offset, offset, sector_size_upper_boundary, size  = struct.unpack('<HHHH', input_file.read(8))
			entries_descriptors.append(ArchiveEntry(sector_offset, offset, sector_size_upper_boundary, size, number_of_entries))

		if(args.bin): extract_bin(input_base_name, input_file, entries_descriptors, args.notmzx)
		else: MzpFile(input_base_name, input_file, entries_descriptors)

def extract_bin(input_base_name, input_file, entries_descriptors, notmzx):
	output_dir = input_base_name + '-unpacked'

	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)

	for index, entry in enumerate(entries_descriptors):
		input_file.seek(entry.real_offset)
		data = input_file.read(entry.real_size)

		# Desc
		if index == 0:
			desc_file_name = os.path.join(output_dir, '0desc.bin')
			write_file(data, desc_file_name)
			continue

		file_name = 'tile' + str(index)
		if notmzx:
			mzx_file_name = os.path.join(output_dir, file_name + '.mzx')
			write_file(data, mzx_file_name)
		else:
			extract_file_name = os.path.join(output_dir, file_name + '.ucp')
			input_file.seek(entry.real_offset)
			sig, size = unpack('<LL', input_file.read(0x8))
			status, extract_data = mzx0_decompress(input_file, entry.real_size-8, size)
			write_file(extract_data, extract_file_name)

def write_file(data, output_file_name):
	output_file = open(output_file_name, 'wb')
	output_file.write(data)
	output_file.close()

############
# __main__ #
############

if __name__ == '__main__':
	parser, args = parse_args()
	if (args.input != None): extract_check(args)
	else:
		parser.print_usage()
		sys.exit(20)
	sys.exit(0)