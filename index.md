# Wind's Seed

Wind's Seed is a short JRPG for the PC-9801, released in 1995 by Compile. I translated it into English.

![Screenshot of the game](https://github.com/lynn/winds-seed/assets/16232127/ada7591f-4772-46ae-9d57-5679994a94af)

## Installing Wind's Seed to a floppy disk image

1. First, obtain `Disc Station Vol. 07 (Disk 1).hdm` by Compile.

2. Create a new floppy disk image and call it `ws.hdm`. If you're using Neko Project, you can use "New disk" in the "Emulate" menu:

   ![Creating a new floppy disk image in Neko Project](https://github.com/lynn/winds-seed/assets/16232127/3295155b-07f8-4f5d-93f4-164770f37297)

3. Load `Disc Station Vol. 07 (Disk 1).hdm` in FDD1 and the blank `ws.hdm` in FDD2, and then reboot.

4. Press Enter, then down to highlight the Wind's Seed installer:

   ![Selecting the Wind's Seed installer](https://github.com/lynn/winds-seed/assets/16232127/79065cbe-a9d5-4ea6-818f-eaff38b4eeb5)

5. Press Enter to launch it. Move the cursor down to `インストールの実行` and press Enter twice to install.

6. Now your `ws.hdm` file contains Wind's Seed in Japanese! (If you eject FDD1 and reboot, you should be able to play it.)

## Patching the game

Download the patch [here](./winds-seed-english.xdelta) and apply it using [xdelta](http://xdelta.org/).

To apply it, I suggest you use [xdelta UI](https://www.romhacking.net/utilities/598/), but if you prefer using the command line, try:

    xdelta -d -s ws.hdm winds-seed-english.xdelta ws-en.hdm

Now you can load `ws-en.hdm` to play the game in English. Have fun!

## Manual

I also translated the game's [manual](./manual) (it was published as part of a magazine).