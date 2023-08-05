"""
Wind's Seed uses a bespoke simple archive format for bundling all its text and
graphics into a single file called WSDATA.FCP. One of its entries, STORY.DAT, is
especially relevant to us, as it contains all the dialogue we want to translate.
These functions unpack and repack that file.
"""

def pack_fcp(fcp: dict) -> bytes:
    b = bytearray(b"FCP 0100")
    p = 0x1208
    for name, contents in fcp.items():
        b += name.rstrip(b"@")
        b += bytes([p >> 16 & 255, p >> 24 & 255, p & 255, p >> 8 & 255])
        b += bytes([len(contents) & 255, len(contents) >> 8 & 255])
        p += len(contents)
    b = b.ljust(0x1208, b"\0")
    for contents in fcp.values():
        b += contents
    return b


def unpack_fcp(fcp_file: bytes) -> dict:
    file_list = 0x8
    i = file_list
    fcp = {}
    while fcp_file[i]:
        name = bytes(fcp_file[i : i + 12])
        address = (
            fcp_file[i + 13] << 24
            | fcp_file[i + 12] << 16
            | fcp_file[i + 15] << 8
            | fcp_file[i + 14]
        )
        size = (fcp_file[i + 17] << 8) + fcp_file[i + 16]
        contents = fcp_file[address : address + size]
        while name in fcp:
            # For some bizarre reason there are two files with the same name in
            # the archive! We'll just add a distinguishing character to the name
            # and strip it when we repack, so that one doesn't override the
            # other in the `fcp` Python dict.
            name += b"@"
        fcp[name] = contents
        i += 18
    return fcp
