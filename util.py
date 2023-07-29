import re

def edit(byte_array: bytearray, index: int, contents: bytes):
    byte_array[index : index + len(contents)] = contents


def translate(byte_array: bytearray, index: int, source: str, target: str):
    bs = source.encode("cp932")
    bt = target.encode("cp932")
    assert byte_array[index : index + len(bs)] == bs
    assert len(bt) <= len(bs)
    byte_array[index : index + len(bs)] = bt.ljust(len(bs))


def find_strings(ws_data):
    for m in re.finditer(b"(([\x81-\x9f][\x40-\xfc]|\x20){2,})", ws_data):
        try:
            s = m.group(1)
            i = m.start(0)
            d = s.decode("cp932")
            if (
                d.strip()
                and "己" not in d
                and not (0x7000 < i < 0xD000 or 0x2000 < i < 0x5000)
            ):
                rd = repr(d).replace("\\u3000", "\u3000")
                print(
                    "translate(ws_data, 0x%04x, %s, %s) # %02x"
                    % (i, rd, rd, ws_data[i + len(s)])
                )
        except UnicodeDecodeError:
            pass
