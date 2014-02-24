 The .mzp format
=================
> Revision 2, maintainer: Waku_Waku

> Reverse-engineered by Waku_Waku

All fields are little-endian unless specified otherwise.


 Introduction
==============

The .mzp archive format is mostly used in consumer titles in Playstation 2-era and early PSP lifetime, in a limited production subset from Interchannel and Piacci, such as "Kyuuketsu Kitan Moon Ties", "Like Life Every Hour" or even PS3 title "Suzukaze no Melt Days in the Sanctuary".


It is not to be confused with the top-level MRG/HED/NAM structure, or with F&C's MRG format.

 I) .mzp structure (header: 0x6 bytes)
=======================================
	4 bytes - 'mrgd00' signature (0x6D 0x72 0x67 0x64 0x30 0x30)
	2 bytes - number of archive entry descriptors
    { n times (0x8 bytes): Archive Entry Descriptor }
    { Data }


 I.1)  Archive Entry Descriptor
--------------------------------

	2 bytes - offset, sector count (0x800 bytes)
	2 bytes - offset, within sector
	2 bytes - size upper boundary, sector count (0x800 bytes)
	2 bytes - size in data section (Raw)

Real offset = data start offset + .ofsSect * 0x800 + .ofsByte

.sizeSect * 0x800 <= .sizeRaw
