ws = [
    (0x03A9, "ＧＡＭＥ　ＯＶＥＲ", "    GAME OVER     "),  # ff
    (0x13C4, "が組み込まれていません", " not installed"),  # 0d
    (0x13F5, "のバージョンが違います", " version is wrong"),  # 0d
    (0x1428, " を組み込んで実行して下さい", " needs install and run"),  # 0d
    (0x1446, "メモリが不足しています。", "Not enough memory."),  # 0d
    (0x1460, "メインメモリ空き容量をメインプログラム実行時に", "Please ensure at least "),  # 0d
    (0x14A9, "以上確保して下さい。", "is available"),  # 0d
    (0x14C0, "メモリブロックの変更が出来ませんでした！！", "Memory block change failed!"),  # 24
    (0x14EB, "メモリの確保が出来ませんでした！！！", "Memory allocation failed!"),  # 24
    (0x1510, "ファイル", "File "),  # 5b
    (0x1526, "が読み込めません！！", " could not be read!"),  # 24
    (0x153F, "ＦＣＰファイルテーブルが読み込めません！！", "FCP file could not be read!"),  # 24
    (0x156A, "ＦＣＰファイル内に", "FCP file lacks "),  # 5b
    (0x158A, "が存在しません！！", "!!"),  # 24
    (0x159D, "致命的エラーが発生しました", "A fatal error has occurred"),  # 24
    # (0x19F6, "\x0A\x01", "\x0A\x00"),
    (0x19F8, "ミーナ", "Mina  "),  # 01
    # (0x1A03, "\x0A\x01", "\x0A\x00"),
    (0x1A05, "オットー", "Otto    "),  # ff
    (0x1A18, "   !／   !", "   1/    1"),
    (0x1A2D, "    !", "    1"),
    (0x1A3D, "   !／   !", "   1/    1"),
    (0x5755, "ＹＯＵ　ＷＯＮ！！", "     YOU WON!!    "),  # ff
    (0x576D, "ＥＸＰ：　    ", "    Exp:      "),  # 21
    (0x5782, "ＥＸＰ：　－－－－－", "    Exp:  ----------"),  # ff
    (0x579C, "　　　：　    ", "      :       "),  # 21
    (0x57B1, "　　ミーナ　レベルアップ！　　", "    Mina leveled up!"),  # ff
    (0x57D5, "　　オットー　レベルアップ！　", "    Otto leveled up!"),  # ff
    (0x57F9, "レベル：   ", "Level:"),  # 21
    (0x5808, "体力　：   ", "HP:"),  # 21
    (0x5814, "（＋   ", " (+    "),  # 21
    (0x5821, "攻撃力：   ", "Attack:"),  # 21
    (0x582D, "（＋   ", " (+    "),  # 21
    (0x583A, "防御力：   ", "Defense:"),  # 21
    (0x5846, "（＋   ", " (+    "),  # 21
    (0x5853, "素早さ：   ", "Speed:"),  # 21
    (0x585F, "（＋   ", " (+    "),  # 21
    (0x5BE5, "イシオニ", "Golem"),  # ff
    (0x5BF3, "かたいイシオニ", "Hard Golem"),  # ff
    (0x5C07, "すごいイシオニ", "Great Golem"),  # ff
    (0x5C1B, "コトダマ", "Kotodama"),  # ff
    (0x5C29, "カナキリゴエ", "Siren"),  # ff
    (0x5C3B, "イワトカゲ", "Rocklizard"),  # ff
    (0x5C4B, "ミドリイワトカゲ", "Green Rocklizard"),  # ff
    (0x5C61, "レーザー砲", "Cannon"),  # ff
    (0x5C71, "下級兵士", "Private"),  # ff
    (0x5C7F, "中級兵士", "Sergeant"),  # ff
    (0x5C8D, "上級兵士", "Major"),  # ff
    (0x5C9B, "ギャリオット", "Garriott"),  # ff
    (0x5CAD, "トライアンフ", "Triumph"),  # ff
    (0x5CBF, "ウォ－レン", "Warren"),  # ff
    (0x5CCF, "トライアンフ", "Triumph"),  # ff
    (0x5CE1, "イシオニ", "Golem"),  # ff
    (0x5CEF, "かたいイシオニ", "Hard Golem"),  # ff
    (0x5D03, "すごいイシオニ", "Great Golem"),  # ff
    (0x5D17, "コトダマ", "Kotodama"),  # ff
    (0x5D25, "カナキリゴエ", "Siren"),  # ff
    (0x5D37, "ミッキ－", "Mickey"),  # ff
    (0x5D45, "下級兵士", "Private"),  # ff
    (0x5D53, "中級兵士", "Sergeant"),  # ff
    (0x5D61, "上級兵士", "Major"),  # ff
    (0x5DFE, "　最初から　", "  Start     "),  # ff
    (0x5E0E, "　途中から　", "  Continue  "),  # ff
    (0x5E9A, "どうぐ　", "Items"),  # ff
    (0x5EA6, "つよさ　", "Status"),  # ff
    (0x5EB2, "システム", "System"),  # ff
    (0x5F38, "データセーブ", "Save"),  # ff
    (0x5F48, "データロード", "Load"),  # ff
    (0x5F58, "ゲームそくど", "Game Speed"),  # ff
    (0x5F68, "サウンド　　", "Sound"),  # ff
    (0x6200, "　　　　　　　　お祈り草の実　　", "                Praygrass"),  # ff
    (0x6222, "紫ミカンの実　　", "Purple Tangerine"),  # ff
    (0x6234, "ドリドリの葉　　", "Dori Leaf       "),  # ff
    (0x6246, "ザウワークラウト", "Sauerkraut      "),  # ff
    (0x6258, "四つ葉のドリドリ", "Four-Leaf Dori  "),  # ff
    (0x626A, "メディヴァイン　", "Medivine        "),  # ff
    (0x627C, "超肉体玉　　　　", "Super Orb       "),  # ff # wtf is this?
    (0x629B, "　" * 8, " " * 16),  # ff
    (0x62C9, "　" * 8, " " * 16),  # ff
    (0x62B9, "　▲　", "  ^^  "),  # 03
    (0x62E7, "　▼　", "  vv  "),  # 03
    (0x62F5, "どちらが？", "Who?"),  # ff
    (0x6303, "どちらに？", "To whom?"),  # ff
    (0x6354, "　ミーナ　", " Mina"),  # ff
    (0x6368, "オットー", "Otto"),  # 03
    (0x6466, "どちらの？", "Whose?"),  # ff
    (0x6474, "　ミーナ　", " Mina"),  # ff
    (0x6488, "オットー", "Otto"),  # 03
    (0x657C, "ミーナ", "Mina"),  # ff
    (0x6586, "オットー", "Otto"),  # ff
    (0x6594, "レベル     ", "Level      "),  # 21
    (0x65A3, "攻撃力     ", "Attack     "),  # 21
    (0x65B2, "防御力     ", "Defense    "),  # 21
    (0x65C1, "素早さ     ", "Speed      "),  # 21
    (0x65D0, "体力　     ", "HP         "),  # 21
    (0x65DC, "／    ", "/     "),  # 21
    (0x65E9, "経験値     ", "EXP        "),  # 21
    (0x65F5, "／    ", "/     "),  # 21
    (0x6602, "経験値　－－－－－／－－－－－", "  Exp.  ----------/ ----------"),  # ff
    (0x6769, "　　データ　セーブ　　", "    Save game         "),  # ff
    (0x6783, "セーブしますか？", "Really save?"),  # ff
    (0x686C, "　　データ　ロード　　", "    Load game         "),  # ff
    (0x6886, "ロードしますか？", "Really load?"),  # ff
    (0x689A, "データがありません", "No game saved."),  # ff
    (0x68EC, "　", "  "),  # 03
    (0x68F0, "　　Ｙｅｓ　　", "      Yes     "),  # 03
    (0x6900, "　", "  "),  # ff
    (0x6906, "　　　Ｎｏ　　　", "       No       "),  # ff
    (0x6958, "　　Ｙｅｓ　　", "      Yes     "),  # ff
    (0x6970, "　　Ｎｏ　　", "     No     "),  # 03
    (0x69EC, "ゲームそくど", "Game Speed  "),  # ff
    (0x6A02, "　はやい　", "  Fast    "),  # 03
    (0x6A1A, "　ふつう　", "  Normal  "),  # 03
    (0x6A8B, "サウンド", "Sound   "),  # ff
    (0x6A97, "　きく　", "  On    "),  # ff
    (0x6AA3, "きかない", "  Off   "),  # ff
    (0x6B55, "ザウワークラウト", "Sauerkraut      "),  # ff
    (0x6B69, "メディヴァイン　", "Medivine        "),  # ff
    (0x6B7D, "紫ミカンの実　　", "Purple Tangerine"),  # ff
    (0x6B91, "何も買わない　　", "Never mind      "),  # ff
    (0x6C7A, "個体攻撃", "FightOne"),  # ff
    (0x6C88, "全体攻撃", "FightAll"),  # ff
    (0x6C96, "コール１", "Call (1)"),  # ff
    (0x6CA4, "防御　　", "Defend  "),  # ff
    (0x6CB2, "道具　　", "Item    "),  # ff
    (0x6CC0, "逃げる　", "Run     "),  # ff
    (0x6CCE, "コール１", "Call (1)"),  # ff
    (0x6CDC, "コール２", "Call (2)"),  # ff
    (0x6CEA, "コール３", "Call (3)"),  # ff
    (0x6CF8, "必殺技　", "SuperAtk"),  # ff
    (0x6DCD, "攻撃　　", "Fight   "),  # ff
    (0x6DDB, "回復　　", "Heal    "),  # ff
    (0x6DE9, "コール１", "Call (1)"),  # ff
    (0x6DF7, "防御　　", "Defend  "),  # ff
    (0x6E05, "道具　　", "Item    "),  # ff
    (0x6E13, "逃げる　", "Run     "),  # ff
    (0x6E21, "コール１", "Call (1)"),  # ff
    (0x6E2F, "コール２", "Call (2)"),  # ff
    (0x6E3D, "コール３", "Call (3)"),  # ff
    (0x6E4B, "必殺技　", "SuperAtk"),  # ff
    (0xB992, '\x03\x02ｦﾐ･** "**&ﾞ!"ﾞ!" !"ﾟ!"', "\x03\x03Lv.99 1995-01-01 01:01"),  # ff
    (0xB9AB, "からっぽだよ～ん！　　", "Nothin' here yet!     "),  # ff
]
