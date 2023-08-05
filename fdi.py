"""
This file contains code to unpack all the files from the Wind's Seed .FDI floppy
disk image, and to repack it and fix the FAT table (because one of the files
will have grown).
"""

import math
import os

FAT_START = 0x2400


def pack_fat_table(entries: list[int]) -> bytes:
    # Wind's Seed, like most PC98 floppies, uses FAT12. We pack a list of 12-bit
    # numbers into the right format where each entry is spread over 1½ bytes.
    b = bytearray(math.ceil(len(entries) / 2) * 3)
    for i, x in enumerate(entries):
        if i % 2 == 0:
            b[i // 2 * 3] |= x & 0xFF
            b[i // 2 * 3 + 1] |= x >> 8
        else:
            b[i // 2 * 3 + 1] |= (x & 0xF) << 4
            b[i // 2 * 3 + 2] |= x >> 4
    return bytes(b)


def pack_fdi(fs: dict[bytes, any], rom: bytes) -> bytes:
    b = bytearray(rom[:FAT_START])
    sector = 2
    queue = []

    fat = [0xFFE, 0xFFF]

    for i, (name, contents) in enumerate(fs.items()):
        base, ext = name.encode().split(b".")
        meta = rom[0x240B + 32 * i : 0x241A + 32 * i]
        if i >= 12:
            # Hack for save files
            meta = b" \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xef\xba\xfcV"
        se = sector.to_bytes(2, byteorder="little")
        le = len(contents).to_bytes(4, byteorder="little")
        b += base.ljust(8) + ext.ljust(3) + meta + se + le
        queue.append((sector, contents))
        old = sector
        sector += math.ceil(len(contents) / 1024)
        fat += [*range(old + 1, sector), 0xFFF]

    ft = pack_fat_table(fat).ljust(0x800, b"\0")
    b[0x1400:0x1C00] = ft
    b[0x1C00:0x2400] = ft

    for sector, contents in queue:
        # Copy padding from ROM
        b += rom[len(b) : (sector + 4) * 1024 + FAT_START]
        b += contents
    return b + rom[len(b) : len(rom)]


def unpack_fdi(rom: bytes) -> dict[bytes, any]:
    fs = {}
    for i in range(99):
        header = rom[FAT_START + 32 * i : FAT_START + 32 * i + 32]
        if header[0] == 0:
            break
        name = bytes(header[:8]).decode().strip()
        ext = bytes(header[8:11]).decode().strip()
        if ext:
            name += "." + ext
        sector = int.from_bytes(header[26:28], byteorder="little")
        length = int.from_bytes(header[28:32], byteorder="little")
        start = (sector + 0x4) * 1024 + FAT_START
        end = start + length
        data = rom[start:end]
        fs[name] = data
        # print(name, hex(start), hex(end))
        # print(hex(FAT_START + 32 * i), header)
        if not os.path.isdir("dump"):
            os.mkdir("dump")
        path = os.path.join("dump", name)
        if not os.path.isfile(path):
            print("Dumping", path)
            with open("dump\\" + name, "wb") as of:
                of.write(data)
    return fs
