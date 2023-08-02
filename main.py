# breakpoints
# - 18ae:236d (putchar)
# - 18ae:239a (putchar's INT 4f)
# - 18ae:7390 (puts_menu)
#   - 18ae:73a7 (puts_menu loop)
# - 13d0:0103 (entrypoint of int 4f)
# - 13d0:0ac0 (entrypoint of getkanji)
#
# getkanji:
#   DX is shift-jis code (gets converted to JIS)
#   CX is 0f for normal text, 4f for big text... 80 for inverted
#   BX is position?
#     mina start 1407 1408 1409...
#     otto start 141b 141c 141d...
#


# save games:
#
# rom[0xc5000:0xc5400] = 0x400 bytes (what format?)
# rom[0x2580:0x25a0] = b'WSSAVE00DAT \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xef\xba\xfcV\x07\x03\x00\x04\x00\x00'

from dataclasses import dataclass
from typing import Dict, List
import os.path
import re
import sys

from x86 import Patch
import story
import strings
from util import edit, translate, find_strings


@dataclass
class Entry:
    index: int
    name: str
    start: int
    end: int
    data: bytes


if __name__ == "__main__":
    rom_name = "Winds_Seed.FDI"
    # rom_name = "patched.fdi"
    with open(rom_name, "rb") as f:
        rom = bytearray(f.read())

    fs = {}
    START = 0x2400
    for i in range(99):
        header = rom[START + 32 * i : START + 32 * i + 32]
        if header[0] == 0:
            break
        name = bytes(header[:8]).decode().strip()
        ext = bytes(header[8:11]).decode().strip()
        if ext:
            name += "." + ext
        sector = int.from_bytes(header[26:28], byteorder="little")
        length = int.from_bytes(header[28:32], byteorder="little")
        start = (sector + 0x4) * 1024 + START
        end = start + length
        data = rom[start:end]
        fs[name] = Entry(i, name, start, end, data)
        # print(name, hex(start), hex(end))
        # print(hex(START + 32 * i), header)
        if not os.path.isdir("dump"):
            os.mkdir("dump")
        path = os.path.join("dump", name)
        if not os.path.isfile(path):
            print("Dumping", path)
            with open("dump\\" + name, "wb") as of:
                of.write(data)

    ws = fs["WS.COM"]
    ws_patched = bytearray(ws.data)

    table = ws.data[0xCC40:0xCD80].decode("cp932")

    tl = story.parse()

    fcp_file = bytearray(fs["WSDATA.FCP"].data)
    file_list = 0x8
    i = file_list
    while fcp_file[i]:
        name = bytes(fcp_file[i : i + 8].strip() + fcp_file[i + 8 : i + 12])
        address = (
            fcp_file[i + 13] << 24
            | fcp_file[i + 12] << 16
            | fcp_file[i + 15] << 8
            | fcp_file[i + 14]
        )
        size = (fcp_file[i + 17] << 8) + fcp_file[i + 16]
        contents = fcp_file[address : address + size]
        if name == b"STORY.DAT":
            story_contents = contents
            print("Original story length:", len(contents))
            print("Translation length:", len(tl))
            if len(tl) > len(contents):
                print("That's too big!! Trimming it")
                tl = tl[: len(contents)]
            edit(fcp_file, address, tl)
            # edit(fcp_file, address + 0x288, b"\x0d\x0b\x00\x0a\x02\x07\x0a")
            # with open(name.decode(), "wb") as of:
            #    of.write(contents)
        i += 18

    if "--dump-story" in sys.argv:
        print("Dumping story...")
        story.dump(story_contents, table)

    if "--find-strings" in sys.argv:
        find_strings(ws.data)

    patched = rom[:]

    drbios = fs["DRBIOS.COM"]
    bios_patched = bytearray(drbios.data)

    # Make jump over picture copy unconditional
    # edit(bios_patched, 0x9f7, b"\xeb")

    # Disable bold text
    # edit(bios_patched, 0xA2F, b"\x90\x90")

    # halfwidth text
    # 0:  30 e4                   xor    ah,ah
    # 2:  2c 40                   sub    al,0x40
    # 4:  d0 f8                   sar    al,1
    # 6:  04 40                   add    al,0x40
    # 8:  86 e0                   xchg   al,ah
    # a:  66 89 c2                mov    dx,ax
    # d:  e6 a5                   out    0xa5,al
    edit(
        bios_patched,
        0x9C7,
        b"\x30\xE4\x2C\x40\xD0\xF8\x04\x40\x86\xE0\x66\x89\xC2\xE6\xA5\x90\x90\x90\x90\x90\x90\x90",
    )

    # halfwidth digits: add 0x30, not 0x21 (which was ０ in the table)
    edit(ws_patched, 0x7488, b"\x04\x30")  # ADD AL, last digit
    edit(ws_patched, 0x749E, b"\x80\xc1\x30")  # ADD CL, other digits
    edit(ws_patched, 0x74BD, b"\x3c\x30")  # CMP, to clear leading zeros
    edit(ws_patched, 0x6B2B, b"\x3c\x30")  # CMP, to clear leading zeros
    edit(ws_patched, 0x19C0, b"\x3c\x30")  # CMP, to clear leading zeros

    # HP and money x positions
    edit(ws_patched, 0x1A11, bytes([0x0A * 2]))
    edit(ws_patched, 0x1A26, bytes([0x0D * 2 + 4]))
    edit(ws_patched, 0x1A36, bytes([0x1E * 2]))

    blank = 0xB64A

    # Scroll "kanji" picture 8px to the left (rol ax,8)
    edit(bios_patched, 0xA2D, b"\xc1\xc0\x08\x90\x90\x90")

    # and these guys draw the bg?
    # edit(bios_patched, 0xa6e, b"\x90\x90\x90")
    # edit(bios_patched, 0xa76, b"\x90\x90\x90")
    # edit(bios_patched, 0xa7e, b"\x90\x90\x90")
    # edit(bios_patched, 0xa86, b"\x90\x90\x90")

    # so these guys draw the text...
    # edit(bios_patched, 0xa95, b"\x90\x90\x90")
    # edit(bios_patched, 0xa9d, b"\x90\x90\x90")
    # edit(bios_patched, 0xaa5, b"\x90\x90\x90")
    # edit(bios_patched, 0xaad, b"\x90\x90\x90")

    # edit(bios_patched, 0xb18, b"\xb9\x08\x00") #no this is the height ugh

    # Don't draw the right half of the 16x16 bg
    edit(bios_patched, 0xB62, b"\x90" * 4)
    edit(bios_patched, 0xB6A, b"\x90" * 4)

    # nop out the x*=2 instruction, wrap lines at x=80
    edit(bios_patched, 0xA44, b"\x50")
    edit(bios_patched, 0xAC9, b"\x50")
    edit(bios_patched, 0xA56, b"\x90\x90")

    # Fix up text box start positions:
    edit(ws_patched, 0x389, b"\xbb\x14\x08")  # maybe?
    edit(ws_patched, 0x1874, b"\xbb\x0e\x14")
    edit(ws_patched, 0x2315, b"\xbb\x0e\x14")
    edit(ws_patched, 0x2334, b"\xbb\x36\x14")
    edit(ws_patched, 0x2531, b"\xbb\x0e\x14")
    edit(ws_patched, 0x25B4, b"\xbb\x36\x14")

    # Replacing "lodsw si; mov bx,ax" in menu code with call to patch that doubles x
    double_menu_x = Patch(ws_patched, blank)
    double_menu_x.lodsw_si()
    double_menu_x.mov("bx", "ax")
    double_menu_x.shl_bl_1()
    double_menu_x.ret()
    blank = double_menu_x.end
    Patch(ws_patched, 0x7302).call(double_menu_x.start)

    # Invert kanji pictures
    # edit(bios_patched, 0xa36, b"\x75")

    # Disable kana compression... But it's easier to undo it in DRBIOS.COM.
    # edit(ws_patched, 0x2284, b"\x90\x90")
    # edit(ws_patched, 0x2293, b"\xb6\x00\x90")

    if True:
        for addr, ja, en in strings.ws:
            try:
                en.encode("ascii")
            except UnicodeEncodeError as e:
                print("Non-ASCII in English string:", en)
                raise e
            translate(ws_patched, addr, ja, en)

    patched[drbios.start : drbios.end] = bios_patched
    patched[ws.start : ws.end] = ws_patched
    fcp = fs["WSDATA.FCP"]
    patched[fcp.start : fcp.end] = fcp_file

    patched[
        0x2580:0x25A0
    ] = b"WSSAVE00DAT \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xef\xba\xfcV\x07\x03\x00\x04\x00\x00"
    patched[0xC5000:0xC5400] = open("dump/WSSAVE00_start.DAT", "rb").read()

    with open("patched.fdi", "wb") as of:
        print("Writing patched.fdi")
        of.write(patched)
