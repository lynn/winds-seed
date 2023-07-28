import re

cc = {
    0x03: "<Something>",
    0x07: "<Idk ",
    # Newline
    0x04: "<NL>",
    # Prompt for next message
    0x05: "<Next>\n",
    # Set text color
    0x08: "<Color ",
    # End text routine
    0xFF: "<End>\n\n",
    # Size
    0x0a: "<Size ",
    # Set left speaker sprite
    0x0B: "<LS ",
    # Set right speaker sprite
    0x0C: "<RS ",
    # Use left box
    0x0D: "<LB>",
    # Use right box
    0x0E: "<RB>",
}

cc_inv = { v.strip("\n <>"): k for k, v in cc.items() }

speaker = {
    0x00: "Mina",
    0x01: "Otto",
    0x02: "Gray",
    0x03: "TownMan",
    0x04: "TownLady",
    0x05: "TownKid",
    0x07: "MinaInn",
    0x09: "Innkeeper",
    0x0a: "InnGuest",
    0x0b: "CurryEater",
    0x0c: "WindsSeed",
    0x0e: "GodAngry",
    0x0f: "Mickey",
    0x10: "Donald",
    0x11: "KronkCharge",
    0x12: "God",
    0x14: "MinaShop",
    0x15: "OttoShop",
    0x16: "Shopkeeper",
    0x17: "Kronk",
    0x18: "Blank",
    0x19: "MinaG", # Used when meeting Garriott
    0x1a: "OttoG", # Used when meeting Garriott
    0x1b: "Garriott",
    0x1d: "Warren",
}

speaker_inv = {v: k for k, v in speaker.items()}

def dump(story, table):
    output = []
    for i in range(0, 0x200, 2):
        ptr = story[i] + (story[i+1] << 8)
        if not ptr:
            continue
        output.append("<!-- event 0x%04x at 0x%04x -->\n" % (i, ptr))
        while True:
            byte = story[ptr]
            if byte == 0x20:
                # Half-width space
                char = " "
                ptr += 1
            elif byte < 0x20 or byte >= 0xF0:
                # Control code
                try:
                    char = cc[byte]
                except KeyError:
                    print("Unknown control code: %02x" % byte)
                    char = "<%02x>" % byte
                ptr += 1
                if char == "<LS " or char == "<RS ":
                    char += speaker.get(story[ptr], "%02x" % story[ptr]) + ">"
                    if story[ptr] not in speaker:
                        print("Unknown speaker: %02x" % story[ptr])
                    ptr += 1
                elif char.endswith(" "):
                    char += "%02x" % story[ptr] + ">"
                    ptr += 1
            elif 0x21 <= byte <= 0x7F:
                char = table[byte - 0x21]
                ptr += 1
            elif 0xA1 <= byte <= 0xDF:
                char = table[byte - 0x20 - 0x21]
                ptr += 1
            else:
                try:
                    char = story[ptr : ptr + 2].decode("cp932")
                except UnicodeDecodeError as e:
                    print("???", hex(ptr))
                    raise e
                ptr += 2
            output.append(char)
            if byte == 0xFF:
                break

    with open("story.txt", "w") as of:
        of.write("".join(output))


def parse():
    with open("story-eng.txt") as f:
        translation = f.read()
    event_id = None
    buffer = bytearray(0x201)
    # Null event idk
    buffer[0x200] = 0xFF
    for line in translation.split("\n"):
        if line.startswith("<!--"):
            event_id = int(line.split()[2], 16)
            ptr = len(buffer)
            buffer[event_id] = ptr & 0xFF
            buffer[event_id + 1] = ptr >> 8
        else:
            for m in re.finditer(r"<(\w+)>|<(\w+) ([^>]+)>|(.)", line):
                cmd, cmd1, arg, ch = m.groups()
                if cmd:
                    buffer.append(cc_inv[cmd])
                elif cmd1:
                    buffer.append(cc_inv[cmd1])
                    i = speaker_inv.get(arg)
                    if i is None: i = int(arg, 16)
                    buffer.append(i)
                elif ch:
                    buffer.extend(ch.encode("ascii", errors="replace"))
    return buffer
