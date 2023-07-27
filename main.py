from dataclasses import dataclass
from typing import Dict, List
import os.path

import story


def edit(byte_array: bytearray, index: int, contents: bytes):
    byte_array[index : index + len(contents)] = contents


@dataclass
class Entry:
    index: int
    name: str
    start: int
    end: int
    data: bytes


@dataclass
class Context:
    fs: Dict[str, Entry]
    font_widths: List[int]


if __name__ == "__main__":
    rom_name = "Winds_Seed.FDI"
    with open(rom_name, "rb") as f:
        rom = bytearray(f.read())

    fs = {}
    START = 0x2400
    for i in range(12):
        header = rom[START + 32 * i : START + 32 * i + 32]
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
        if not os.path.isdir("dump"):
            os.mkdir("dump")
        path = os.path.join("dump", name)
        if not os.path.isfile(path):
            print("Dumping", path)
            with open("dump\\" + name, "wb") as of:
                of.write(data)

    table = fs["WS.COM"].data[0xCC40:0xCD80].decode("cp932")

    fcp_file = bytearray(fs["WSDATA.FCP"].data)
    file_list = 0x8
    i = file_list
    while fcp_file[i]:
        name = fcp_file[i : i + 8].strip() + fcp_file[i + 8 : i + 12]
        address = (
            (fcp_file[i + 13] << 24)
            + (fcp_file[i + 12] << 16)
            + (fcp_file[i + 15] << 8)
            + fcp_file[i + 14]
        )
        size = (fcp_file[i + 17] << 8) + fcp_file[i + 16]
        contents = fcp_file[address : address + size]
        # print(name, contents.count(b"\x0d\x0b"))
        if name == b"STORY.DAT":
            story_contents = contents
            edit(fcp_file, address + 0x288, b"\x0d\x0b\x00\x0a\x02\x07\x0a")
            # with open(name.decode(), "wb") as of:
            #    of.write(contents)
        i += 18

    story.dump(story_contents, table)

    patched = rom[:]

    drbios = fs["DRBIOS.COM"]
    bios_data = bytearray(drbios.data)

    if False:
        # halfwidth text
        edit(
            bios_data,
            0x9C7,
            b"\x30\xE4\x2C\x40\xD0\xF8\x04\x40\x86\xE0\x66\x89\xC2\x90\x90\x90\x90\x90\x90\x90\x90\x90",
        )
        # nop out the cursor shl instruction
        edit(bios_data, 0xA56, b"\x90\x90")
        # make the text wrap at the end of the screen, not halfway through
        edit(bios_data, 0xA4D, b"\x90")
        patched[drbios.start : drbios.end] = bios_data

        ws = fs["WS.COM"]
        ws_data = bytearray(ws.data)
        # left window cursor
        edit(ws_data, 0x2532, b"\x0e")
        # right window cursor
        edit(ws_data, 0x25B5, b"\x30")
        patched[ws.start : ws.end] = ws_data

    wsdata = fs["WSDATA.FCP"]
    patched[wsdata.start : wsdata.end] = fcp_file

    with open("patched.fdi", "wb") as of:
        print("Writing patched.fdi")
        of.write(patched)
