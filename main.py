# breakpoints
# - 18ae:236d (putchar)
# - 18ae:239a (putchar's INT 4f)
# - 18ae:7690 (putchar_menu)
# - 13d0:0103 (entrypoint of int 4f)
# - 13d0:0ac0 (entrypoint of getkanji)
# -
#
# getkanji:
#   DX is shift-jis code (gets converted to JIS)
#   CX is 0f for normal text, 4f for big text... 80 for inverted
#   BX is position?
#     mina start 1407 1408 1409...
#     otto start 141b 141c 141d...
#
# putchar:

from dataclasses import dataclass
from typing import Dict, List
import os.path
import re

from x86 import Patch
import story


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
        # print(name, data.count("道具".encode("cp932")))
        print(name, data.count(bytes.fromhex("2e 8a 37 2e 8a")))
        if not os.path.isdir("dump"):
            os.mkdir("dump")
        path = os.path.join("dump", name)
        if not os.path.isfile(path):
            print("Dumping", path)
            with open("dump\\" + name, "wb") as of:
                of.write(data)

    table = fs["WS.COM"].data[0xCC40:0xCD80].decode("cp932")

    tl = story.parse()

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
        if name == b"STORY.DAT":
            story_contents = contents
            print(len(contents))
            print(len(tl))
            edit(fcp_file, address, tl)
            # edit(fcp_file, address + 0x288, b"\x0d\x0b\x00\x0a\x02\x07\x0a")
            # with open(name.decode(), "wb") as of:
            #    of.write(contents)
        i += 18

    # story.dump(story_contents, table)

    ws = fs["WS.COM"]
    ws_data = bytearray(ws.data)
    if False:
        find_strings(ws_data)

    patched = rom[:]

    drbios = fs["DRBIOS.COM"]
    bios_data = bytearray(drbios.data)

    if False:

        # nop out the cursor shl instruction
        edit(bios_data, 0xA56, b"\x90\x90")
        # make the text wrap at the end of the screen, not halfway through
        edit(bios_data, 0xA4D, b"\x90")

        # left window cursor
        edit(ws_data, 0x2532, b"\x0e")
        # right window cursor
        edit(ws_data, 0x25B5, b"\x30")

    # Make jump over picture copy unconditional
    # edit(bios_data, 0x9f7, b"\xeb")

    # Disable bold text
    edit(bios_data, 0xA2F, b"\x90\x90")

    # halfwidth text
    # 0:  30 e4                   xor    ah,ah
    # 2:  2c 40                   sub    al,0x40
    # 4:  d0 f8                   sar    al,1
    # 6:  04 40                   add    al,0x40
    # 8:  86 e0                   xchg   al,ah
    # a:  66 89 c2                mov    dx,ax
    # d:  e6 a5                   out    0xa5,al
    edit(
        bios_data,
        0x9C7,
        b"\x30\xE4\x2C\x40\xD0\xF8\x04\x40\x86\xE0\x66\x89\xC2\xE6\xA5\x90\x90\x90\x90\x90\x90\x90",
    )

    # nop out the x*=2 instruction, wrap lines at x=80
    edit(bios_data, 0xA44, bytes([80]))
    edit(bios_data, 0xAC9, bytes([80]))
    edit(bios_data, 0xA56, b"\x90\x90")

    # Fix up text box start positions:
    edit(ws_data, 0x389, b"\xbb\x14\x08") # maybe?
    edit(ws_data, 0x1874, b"\xbb\x0e\x14")
    edit(ws_data, 0x2315, b"\xbb\x0e\x14")
    edit(ws_data, 0x2334, b"\xbb\x36\x14")
    edit(ws_data, 0x2531, b"\xbb\x0e\x14")
    edit(ws_data, 0x25b4, b"\xbb\x36\x14")


    blank = 0xb64a
    double_menu_x = Patch(ws_data, blank)
    double_menu_x.lodsw_si()
    double_menu_x.mov_bx_ax()
    double_menu_x.shl_bl_1()
    double_menu_x.ret()
    blank = double_menu_x.addr
    # Replacing "lodsw si; mov bx,ax" with call to patch that doubles x
    Patch(ws_data, 0x7302).call(double_menu_x.label)

    # Invert kanji pictures
    # edit(bios_data, 0xa36, b"\x75")

    # Disable kana compression... But it's easier to do it in DRBIOS.COM.
    # edit(ws_data, 0x2284, b"\x90\x90")
    # edit(ws_data, 0x2293, b"\xb6\x00\x90")

    if True:
        translate(ws_data, 0x03A9, "ＧＡＭＥ　ＯＶＥＲ", "ＧＡＭＥ　ＯＶＥＲ")  # ff
        translate(ws_data, 0x13C4, "が組み込まれていません", " not installed")  # 0d
        translate(ws_data, 0x13F5, "のバージョンが違います", " version is wrong")  # 0d
        translate(ws_data, 0x1428, " を組み込んで実行して下さい", " needs install and run")  # 0d
        translate(ws_data, 0x1446, "メモリが不足しています。", "Not enough memory.")  # 0d
        translate(
            ws_data, 0x1460, "メインメモリ空き容量をメインプログラム実行時に", "Please ensure at least "
        )  # 0d
        translate(ws_data, 0x14A9, "以上確保して下さい。", "is available")  # 0d
        translate(
            ws_data, 0x14C0, "メモリブロックの変更が出来ませんでした！！", "Memory block change failed!"
        )  # 24
        translate(
            ws_data, 0x14EB, "メモリの確保が出来ませんでした！！！", "Memory allocation failed!"
        )  # 24
        translate(ws_data, 0x1510, "ファイル", "File ")  # 5b
        translate(ws_data, 0x1526, "が読み込めません！！", " could not be read!")  # 24
        translate(
            ws_data, 0x153F, "ＦＣＰファイルテーブルが読み込めません！！", "FCP file could not be read!"
        )  # 24
        translate(ws_data, 0x156A, "ＦＣＰファイル内に", "FCP file lacks ")  # 5b
        translate(ws_data, 0x158A, "が存在しません！！", "!!")  # 24
        translate(ws_data, 0x159D, "致命的エラーが発生しました", "A fatal error has occurred")  # 24
        translate(ws_data, 0x19F8, "ミーナ", "Mina  ")  # 01
        translate(ws_data, 0x1A05, "オットー", "Otto    ")  # ff
        translate(ws_data, 0x5755, "ＹＯＵ　ＷＯＮ！！", "ＹＯＵ　ＷＯＮ！！")  # ff
        translate(ws_data, 0x576D, "ＥＸＰ：　    ", "ＥＸＰ：　    ")  # 21
        translate(ws_data, 0x5782, "ＥＸＰ：　－－－－－", "ＥＸＰ：　－－－－－")  # ff
        translate(ws_data, 0x579C, "　　　：　    ", "　　　：　    ")  # 21
        translate(ws_data, 0x57B1, "　　ミーナ　レベルアップ！　　", "    Mina leveled up!")  # ff
        translate(ws_data, 0x57D5, "　　オットー　レベルアップ！　", "    Otto leveled up!")  # ff
        translate(ws_data, 0x57F9, "レベル：   ", "Level:")  # 21
        translate(ws_data, 0x5808, "体力　：   ", "HP:")  # 21
        translate(ws_data, 0x5814, "（＋   ", "（＋   ")  # 21
        translate(ws_data, 0x5821, "攻撃力：   ", "Attack:")  # 21
        translate(ws_data, 0x582D, "（＋   ", "（＋   ")  # 21
        translate(ws_data, 0x583A, "防御力：   ", "Defense:")  # 21
        translate(ws_data, 0x5846, "（＋   ", "（＋   ")  # 21
        translate(ws_data, 0x5853, "素早さ：   ", "Speed:")  # 21
        translate(ws_data, 0x585F, "（＋   ", "（＋   ")  # 21
        translate(ws_data, 0x5BE5, "イシオニ", "Golem")  # ff
        translate(ws_data, 0x5BF3, "かたいイシオニ", "Hard Golem")  # ff
        translate(ws_data, 0x5C07, "すごいイシオニ", "Great Golem")  # ff
        translate(ws_data, 0x5C1B, "コトダマ", "Kotodama")  # ff
        translate(ws_data, 0x5C29, "カナキリゴエ", "Siren")  # ff
        translate(ws_data, 0x5C3B, "イワトカゲ", "RockLizard")  # ff
        translate(ws_data, 0x5C4B, "ミドリイワトカゲ", "Green RockLizard")  # ff
        translate(ws_data, 0x5C61, "レーザー砲", "Cannon")  # ff
        translate(ws_data, 0x5C71, "下級兵士", "Private")  # ff
        translate(ws_data, 0x5C7F, "中級兵士", "Sergeant")  # ff
        translate(ws_data, 0x5C8D, "上級兵士", "Major")  # ff
        translate(ws_data, 0x5C9B, "ギャリオット", "Garriott")  # ff
        translate(ws_data, 0x5CAD, "トライアンフ", "Triumph")  # ff
        translate(ws_data, 0x5CBF, "ウォ－レン", "Warren")  # ff
        translate(ws_data, 0x5CCF, "トライアンフ", "Triumph")  # ff
        translate(ws_data, 0x5CE1, "イシオニ", "Golem")  # ff
        translate(ws_data, 0x5CEF, "かたいイシオニ", "Hard Golem")  # ff
        translate(ws_data, 0x5D03, "すごいイシオニ", "Great Golem")  # ff
        translate(ws_data, 0x5D17, "コトダマ", "Kotodama")  # ff
        translate(ws_data, 0x5D25, "カナキリゴエ", "Siren")  # ff
        translate(ws_data, 0x5D37, "ミッキ－", "Mickey")  # ff
        translate(ws_data, 0x5D45, "下級兵士", "Private")  # ff
        translate(ws_data, 0x5D53, "中級兵士", "Sergeant")  # ff
        translate(ws_data, 0x5D61, "上級兵士", "Major")  # ff
        translate(ws_data, 0x5DFE, "　最初から　", "　Start")  # ff
        translate(ws_data, 0x5E0E, "　途中から　", "　Continue")  # ff
        translate(ws_data, 0x5E9A, "どうぐ　", "Items")  # ff
        translate(ws_data, 0x5EA6, "つよさ　", "Status")  # ff
        translate(ws_data, 0x5EB2, "システム", "Systemム")  # ff
        translate(ws_data, 0x5F38, "データセーブ", "Save")  # ff
        translate(ws_data, 0x5F48, "データロード", "Load")  # ff
        translate(ws_data, 0x5F58, "ゲームそくど", "Game Speed")  # ff
        translate(ws_data, 0x5F68, "サウンド　　", "Sound")  # ff
        translate(ws_data, 0x6200, "　　　　　　　　お祈り草の実　　", "　　　　　　　　Praygrass")  # ff
        translate(ws_data, 0x6222, "紫ミカンの実　　", "Purple Tangerine")  # ff
        translate(ws_data, 0x6234, "ドリドリの葉　　", "Dori Leaf       ")  # ff
        translate(ws_data, 0x6246, "ザウワークラウト", "Sauerkraut      ")  # ff
        translate(ws_data, 0x6258, "四つ葉のドリドリ", "Four-Leaf Dori  ")  # ff
        translate(ws_data, 0x626A, "メディヴァイン　", "Medivine        ")  # ff
        translate(ws_data, 0x627C, "超肉体玉　　　　", "Super Orb       ")  # ff # wtf is this?
        translate(ws_data, 0x62B9, "　▲　", "　▲　")  # 03
        translate(ws_data, 0x62E7, "　▼　", "　▼　")  # 03
        translate(ws_data, 0x62F5, "どちらが？", "Who?")  # ff
        translate(ws_data, 0x6303, "どちらに？", "To whom?")  # ff
        translate(ws_data, 0x6354, "　ミーナ　", "Mina")  # ff
        translate(ws_data, 0x6368, "オットー", "Otto")  # 03
        translate(ws_data, 0x6466, "どちらの？", "Whose?")  # ff
        translate(ws_data, 0x6474, "　ミーナ　", "Mina")  # ff
        translate(ws_data, 0x6488, "オットー", "Otto")  # 03
        translate(ws_data, 0x657C, "ミーナ", "Mina")  # ff
        translate(ws_data, 0x6586, "オットー", "Otto")  # ff
        translate(ws_data, 0x6594, "レベル     ", "Level      ")  # 21
        translate(ws_data, 0x65A3, "攻撃力     ", "Attack     ")  # 21
        translate(ws_data, 0x65B2, "防御力     ", "Defense    ")  # 21
        translate(ws_data, 0x65C1, "素早さ     ", "Speed      ")  # 21
        translate(ws_data, 0x65D0, "体力　     ", "HP         ")  # 21
        translate(ws_data, 0x65DC, "／    ", "／    ")  # 21
        translate(ws_data, 0x65E9, "経験値     ", "  Exp.     ")  # 21
        translate(ws_data, 0x65F5, "／    ", "／    ")  # 21
        translate(ws_data, 0x6602, "経験値　－－－－－／－－－－－", "  Exp.　－－－－－／－－－－－")  # ff
        translate(ws_data, 0x6769, "　　データ　セーブ　　", "　　Save game     　　")  # ff
        translate(ws_data, 0x6783, "セーブしますか？", "Really save?")  # ff
        translate(ws_data, 0x686C, "　　データ　ロード　　", "　　Load game     　　")  # ff
        translate(ws_data, 0x6886, "ロードしますか？", "Really load?")  # ff
        translate(ws_data, 0x689A, "データがありません", "No game saved.")  # ff
        translate(ws_data, 0x68F0, "　　Ｙｅｓ　　", "　　Ｙｅｓ　　")  # 03
        translate(ws_data, 0x6906, "　　　Ｎｏ　　　", "　　　Ｎｏ　　　")  # ff
        translate(ws_data, 0x6958, "　　Ｙｅｓ　　", "　　Ｙｅｓ　　")  # ff
        translate(ws_data, 0x6970, "　　Ｎｏ　　", "　　Ｎｏ　　")  # 03
        translate(ws_data, 0x69EC, "ゲームそくど", "Game Speed  ")  # ff
        translate(ws_data, 0x6A02, "　はやい　", "　Fast  　")  # 03
        translate(ws_data, 0x6A1A, "　ふつう　", "　Normal　")  # 03
        translate(ws_data, 0x6A8B, "サウンド", "Sound   ")  # ff
        translate(ws_data, 0x6A97, "　きく　", "　On  　")  # ff
        translate(ws_data, 0x6AA3, "きかない", "　Off 　")  # ff
        translate(ws_data, 0x6B55, "ザウワークラウト", "Sauerkraut      ")  # ff
        translate(ws_data, 0x6B69, "メディヴァイン　", "Medivine        ")  # ff
        translate(ws_data, 0x6B7D, "紫ミカンの実　　", "Purple Tangerine")  # ff
        translate(ws_data, 0x6B91, "何も買わない　　", "Never mind      ")  # ff

        translate(ws_data, 0x6C7A, "個体攻撃", "FightOne")  # ff
        translate(ws_data, 0x6C88, "全体攻撃", "FightAll")  # ff
        translate(ws_data, 0x6C96, "コール１", "Call (1)")  # ff
        translate(ws_data, 0x6CA4, "防御　　", "Defend  ")  # ff
        translate(ws_data, 0x6CB2, "道具　　", "Item    ")  # ff
        translate(ws_data, 0x6CC0, "逃げる　", "Run     ")  # ff
        translate(ws_data, 0x6CCE, "コール１", "Call (1)")  # ff
        translate(ws_data, 0x6CDC, "コール２", "Call (2)")  # ff
        translate(ws_data, 0x6CEA, "コール３", "Call (3)")  # ff
        translate(ws_data, 0x6CF8, "必殺技　", "SuperAtk")  # ff
        translate(ws_data, 0x6DCD, "攻撃　　", "Fight   ")  # ff
        translate(ws_data, 0x6DDB, "回復　　", "Heal    ")  # ff
        translate(ws_data, 0x6DE9, "コール１", "Call (1)")  # ff
        translate(ws_data, 0x6DF7, "防御　　", "Defend  ")  # ff
        translate(ws_data, 0x6E05, "道具　　", "Item    ")  # ff
        translate(ws_data, 0x6E13, "逃げる　", "Run     ")  # ff
        translate(ws_data, 0x6E21, "コール１", "Call (1)")  # ff
        translate(ws_data, 0x6E2F, "コール２", "Call (2)")  # ff
        translate(ws_data, 0x6E3D, "コール３", "Call (3)")  # ff
        translate(ws_data, 0x6E4B, "必殺技　", "SuperAtk")  # ff

    patched[drbios.start : drbios.end] = bios_data
    patched[ws.start : ws.end] = ws_data
    fcp = fs["WSDATA.FCP"]
    patched[fcp.start : fcp.end] = fcp_file

    with open("patched.fdi", "wb") as of:
        print("Writing patched.fdi")
        of.write(patched)
