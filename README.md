# Wind's Seed

Wind's Seed is a short JRPG for the PC-9801, released in 1995 by Compile.

This repository contains a Python scripts that translate the game to English.

[46OkuMen's exploration of this game](https://github.com/46OkuMen/windseed) helped me get started. Thank you!

## Usage

Copy `Winds_Seed.FDI` to this directory, then:

```sh
python3 main.py                 # Writes an English translation to `patched.fdi`.
python3 main.py --dump-save     # Dumps save files from `patched.fdi`, then quits.
                                # (I'm reinserting save files while playtesting.)

python3 main.py --dump-story    # Dumps the story file to `story.txt` in a human-friendly format.
python3 main.py --find-strings  # Use crappy heuristics to look for Japanese strings on the disk.
```
