class Patch:
    def __init__(self, array, addr):
        self.array = array
        self.label = self.addr = addr

    def raw(self, bs: bytes):
        self.array[self.addr : self.addr + len(bs)] = bs
        self.addr += len(bs)

    def call(self, target):
        rel = (target - (self.addr + 3)) & 0xFFFF
        self.raw(bytes([0xE8, rel & 0xFF, rel >> 8]))

    mov_cl = lambda self, imm: self.raw(bytes([0xB1, imm]))
    mov_di = lambda self, imm: self.raw(bytes([0xBF, imm & 0xFF, imm >> 8]))
    mov_dl_cl = lambda self: self.raw(b"\x88\xca")
    mov_cl_dl = lambda self: self.raw(b"\x88\xd1")
    push_ax = lambda self: self.raw(b"\x50")
    pop_ax = lambda self: self.raw(b"\x58")
    ret = lambda self: self.raw(b"\xc3")
    lodsw_si = lambda self: self.raw(b"\xad")
    mov_bx_ax = lambda self: self.raw(b"\x8b\xd8")
    shl_bl_1 = lambda self: self.raw(b"\xd0\xe3")
