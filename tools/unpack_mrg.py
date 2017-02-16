#!/usr/bin/env python
#
# MRG Extractor
# comes with ABSOLUTELY NO WARRANTY.
#
# Copyright (C) 2016 Quibi
# Copyright (C) 2016 Hintay <hintay@me.com>
#
# Portions Copyright (C) 2016 Quibi
#
# MRG files extraction utility
# For more information, see Specifications/mzp_format.md

import os
import sys
import struct


INPUT_FILE_NAME = 'allscr.mrg'
MODE = 'fate'


class ArchiveEntry:
	def __init__(self, sector_offset, offset, sector_size_upper_boundary, size, number_of_entries):
		self.sector_offset = sector_offset
		self.offset = offset
		self.sector_size_upper_boundary = sector_size_upper_boundary
		self.size = size
		self.real_size = (sector_size_upper_boundary - 1) // 0x20 * 0x10000 + size
		data_start_offset = 6 + 2 + number_of_entries * 8
		self.real_offset = data_start_offset + self.sector_offset * 0x800 + self.offset

input_file = open(INPUT_FILE_NAME, 'rb')
header = input_file.read(6)
print('header: {0}'.format(header.decode('ASCII')))

number_of_entries, = struct.unpack('<H', input_file.read(2))

print('found {0} entries'.format(number_of_entries))
entries_descriptors = []
for i in range(number_of_entries):
	sector_offset, offset, sector_size_upper_boundary, size  = struct.unpack('<HHHH', input_file.read(8))
	entries_descriptors.append(ArchiveEntry(sector_offset=sector_offset, offset=offset, sector_size_upper_boundary=sector_size_upper_boundary, size=size, number_of_entries=number_of_entries))

file_names = ['allscr.nam', 'unknownX.mrg', 'unknownX2.mrg']
for i in range(number_of_entries):
	file_name = ''
	if i * 32 < entries_descriptors[0].real_size:
		# Fix code for RN
		if(MODE == 'fate'):
			if 101 <= i and i<= 202:
				file_name = 'セイバールート十'
			elif i == 240:
				file_name = 'ラストエピソ'
			elif 338 <= i and i<= 483:
				file_name = '桜ルート十'
			elif 604 <= i and i<= 705:
				file_name = '凛ルート十'

		file_name_bytes, = struct.unpack('<32s', input_file.read(32))
		file_name_bytes = file_name_bytes.replace(b'\x01', b'')
		file_name = file_name + file_name_bytes[0:file_name_bytes.index(b'\x00')].decode('932', 'ignore')
	if not file_name: file_name = 'unknown' + str(i)
	file_names.append(file_name + '.mzx')

output_dir = os.path.splitext(INPUT_FILE_NAME)[0] + '-unpacked'
if not os.path.isdir(output_dir):
	os.mkdir(output_dir)

for index, entry in enumerate(entries_descriptors):
	input_file.seek(entry.real_offset)
	data = input_file.read(entry.real_size)
	output_file_name = os.path.join(output_dir, file_names[index])
	print(output_file_name, file=sys.stderr)
	output_file = open(output_file_name, 'wb')
	output_file.write(data)
	output_file.close()

input_file.close()
