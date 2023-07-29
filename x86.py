reg8 = "al cl dl bl ah ch dh bh".split()
reg16 = "ax cx dx bx sp bp si di".split()


class Patch:
    def __init__(self, array, addr, nop_until=None):
        self.array = array
        self.start = self.end = addr
        if nop_until is not None:
            self.array[addr:nop_until] = b"\x90" * (nop_until - addr)

    def raw(self, bs: bytes):
        self.array[self.end : self.end + len(bs)] = bs
        self.end += len(bs)

    def code(self):
        return self.array[self.start : self.end]

    def call(self, target):
        rel = (target - (self.end + 3)) & 0xFFFF
        self.raw(bytes([0xE8, rel & 0xFF, rel >> 8]))

    def mov(self, tgt, src):
        if tgt in reg8 and src in reg8:
            self.raw(bytes([0x88, 0xC0 + 8 * reg8.index(src) + reg8.index(tgt)]))
        elif tgt in reg16 and src in reg16:
            self.raw(bytes([0x89, 0xC0 + 8 * reg16.index(src) + reg16.index(tgt)]))
        elif tgt in reg8 and isinstance(src, int):
            self.raw(bytes([0xB0 + reg8.index(tgt), src & 0xFF]))
        elif tgt in reg16 and isinstance(src, int):
            self.raw(bytes([0xB8 + reg16.index(tgt), src & 0xFF, src >> 8]))

    push_ax = lambda self: self.raw(b"\x50")
    pop_ax = lambda self: self.raw(b"\x58")
    ret = lambda self: self.raw(b"\xc3")
    lodsw_si = lambda self: self.raw(b"\xad")
    shl_bl_1 = lambda self: self.raw(b"\xd0\xe3")
