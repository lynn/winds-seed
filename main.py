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

import hashlib
import os
import struct
import sys

from fcp import pack_fcp, unpack_fcp
from hdm import pack_hdm, unpack_hdm
from x86 import Patch
import story
import strings
from util import edit, translate, find_strings

if __name__ == "__main__":
    rom_name = "ws.hdm"
    if "--dump-save" in sys.argv:
        rom_name = "patched.hdm"
    with open(rom_name, "rb") as f:
        rom = bytearray(f.read())

    fs = unpack_hdm(rom)

    if "--dump-save" in sys.argv:
        exit()

    ws = fs["WS.COM"]
    ws_patched = bytearray(ws)

    table = ws[0xCC40:0xCD80].decode("cp932")

    fcp = unpack_fcp(fs["WSDATA.FCP"])
    assert fs["WSDATA.FCP"] == pack_fcp(fcp)
    assert rom == pack_hdm(fs, rom)

    if not os.path.isdir("fcpdump"):
        os.mkdir("fcpdump")

    for k, v in fcp.items():
        path = os.path.join("fcpdump", k.decode("ascii").replace(" ", ""))
        if not os.path.isfile(path):
            print("Dumping", path)
            with open(path, "wb") as of:
                of.write(v)

    original_story = fcp[b"STORY   .DAT"]
    if "--dump-story" in sys.argv:
        print("Dumping story...")
        story.dump(original_story, table)

    print("Original story length:", len(original_story))
    tl = story.parse()
    print("Translation length:", len(tl))
    fcp[b"STORY   .DAT"] = tl

    if "--find-strings" in sys.argv:
        find_strings(ws)

    drbios = fs["DRBIOS.COM"]
    bios_patched = bytearray(drbios)

    # halfwidth text
    # 0:  30 e4                   xor    ah,ah
    # 2:  2c 40                   sub    al,0x40
    # 4:  d0 f8                   sar    al,1
    # 6:  04 40                   add    al,0x40
    # 8:  86 e0                   xchg   al,ah
    # a:  66 89 c2                mov    dx,ax
    # d:  e6 a5                   out    0xa5,al
    hw = "30e4 2c40 d0f8 0440 86e0 6689c2 e6a5 90909090909090"
    edit(bios_patched, 0x9C7, bytes.fromhex(hw))

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

    # Swap halves of hankaku bitmap from Kanji ROM (rol ax,8)
    # Only invert the hankaku part (not al instead of not ax)
    # Clear the ah part?
    edit(bios_patched, 0xA2D, bytes.fromhex("c1c008 f6c280 7402 f6d0 b4 00 90"))

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
    edit(bios_patched, 0xB7E, b"\x90" * 4)
    edit(bios_patched, 0xB82, b"\x90" * 4)
    edit(bios_patched, 0xB8E, b"\x90" * 4)
    edit(bios_patched, 0xB92, b"\x90" * 4)
    edit(bios_patched, 0xBA0, b"\x90" * 5)
    edit(bios_patched, 0xBA5, b"\x90" * 5)
    edit(bios_patched, 0xBB4, b"\x90" * 5)
    edit(bios_patched, 0xBB9, b"\x90" * 5)

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
    blank = 0xB64A
    double_menu_x = Patch(ws_patched, blank)
    double_menu_x.lodsw_si()
    double_menu_x.mov("bx", "ax")
    double_menu_x.shl_bl_1()
    double_menu_x.ret()
    blank = double_menu_x.end
    Patch(ws_patched, 0x7302).call(double_menu_x.start)

    # Copy more story (0x2900 words instead of 0x2000, i.e. 0x5200 bytes not 0x4000)
    edit(ws_patched, 0x304, b"\xb9\x00\x29")

    # CS:b7af holds the DS value for story.
    # CS:b7ad holds the DS value for what comes after.
    # (remember 2e 8e 1e af b7 is the MOV DS instruction for reading story)
    # This ADD instruction adjusts the gap between them. We change it from 0x400 to 0x600.
    # This really wins us 0x2000 bytes, not 0x200, because segment pointers express 16-byte increments.
    edit(ws_patched, 0x18C, b"\x05\x00\x06")

    # Invert kanji pictures
    # edit(bios_patched, 0xa36, b"\x75")

    # Disable kana compression... But it's easier to undo it in DRBIOS.COM.
    # edit(ws_patched, 0x2284, b"\x90\x90")
    # edit(ws_patched, 0x2293, b"\xb6\x00\x90")

    for addr, ja, en in strings.ws:
        try:
            en.encode("ascii")
        except UnicodeEncodeError as e:
            print("Non-ASCII in English string:", en)
            raise e
        translate(ws_patched, addr, ja, en)

    # Get rid of those @ signs?
    ws_patched = ws_patched.replace(
        bytes.fromhex("0302 8140"), bytes.fromhex("0302 2020")
    )
    ws_patched = ws_patched.replace(
        bytes.fromhex("0300 8140"), bytes.fromhex("0300 2020")
    )

    fs["DRBIOS.COM"] = bios_patched
    fs["WS.COM"] = ws_patched
    fs["WSDATA.FCP"] = pack_fcp(fcp)

    if "WSSAVE00" in sys.argv[-1]:
        with open(sys.argv[-1], "rb") as f:
            sav = bytearray(f.read())

        # lvl, hp, maxhp, atk, def, spd
        stats = struct.pack("<BHHHHH", 99, 999, 999, 999, 999, 999)

        # Mina stats
        sav[0x6A : 0x6A + 11] = stats
        # Money
        sav[0x9A:0x9C] = (9999).to_bytes(2, "little")
        # Otto stats
        sav[0xF0 : 0xF0 + 11] = stats

        fs["WSSAVE00.DAT"] = sav

    patched = pack_hdm(fs, rom)

    with open("patched.hdm", "wb") as of:
        print("Writing patched.hdm: sha1 =", hashlib.sha1(patched).hexdigest())
        of.write(patched)
