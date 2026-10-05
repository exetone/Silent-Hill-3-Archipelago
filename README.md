# Silent Hill 3 AP
Full Archipelago integration for the PC version of Silent Hill 3.

Silent Hill 3 is a 2003 survival horror video game published by Konami for the PlayStation 2 and PC. This AP randomizes the Items, Supplies, Weapons, Maps, Extra New Game Weapons, and newly added Fast Travel Points.

A Fast Travel system has been implemented, letting you teleport to any save point in the game you have previously reached. Optional settings in the YAML let these Fast Travel points be placed anywhere in the multiworld. The custom menu also includes an item tracker, check tracker, and Archipelago activity - the latter 2 able to be displayed in the corner during gameplay.

Due to the modular way the items are placed only Normal Action Difficulty and Normal Riddle Difficulty are allowed for the AP, extra difficulty can be added with modular traps replacing filler items and other YAML options.

The Goal is to either kill God or kill all 5 bosses depending on your YAML settings. Key Items like keys and puzzle items make up the Progression Items, while weapons act as Useful Items, and health items/Ammo make up the game's Filler.

# Setup Guide
You need a PC version of Silent Hill 3 (version 1.0.0.1.). It is *abandonware* but I have to tell you to legally procure your own copy. It's best if your legally obtained copy of the game is labelled *Full-Rip Pre-installed game with NoCD included English version 2.6 GB*.

Next you'll need Steam006's PC Fix to make the game work on modern hardware. Password is pcgw. Just unzip the downloaded folder and place the loose contents in your Silent Hill 3 folder.  
https://community.pcgamingwiki.com/files/file/1331-silent-hill-3-pc-fix-by-steam006/

If you're using an Xbox controller, you'll need to download XInputPlus for the triggers to work. Download it anywhere on your PC > open XInputPlus.exe > point Target Program at sh3.exe > click the DirectInput tab and then Enable DirectInput Output > change LT/RT to Button 11/12 > Apply. After that you can delete the XInputPlus folder if you want. The website is in Japanese, don't worry about it.  
https://0dd14lab.net/xinputplus/

Download sh3.apworld from the github link and double click it to install it or move it to Archipelago\custom_worlds. Close Archipelago if you had it open, then open the Silent Hill Client. This'll patch the game with everything needed. Archipelago Port, Slot, Password etc are all inputted in the Silent Hill Client in the Archipelago Launcher. And that's it! An optional Poptracker pack is also available for this game on the github page.  
https://github.com/exetone/Silent-Hill-3-Archipelago/releases

You can use the generated SH3AP_Mode_Toggle.bat to revert the game back to the vanilla un-archipelago version (with the Steam006 and XInputPlus fixes still applied). Savefiles made pre-modding the game will be reimplemented. Using the Toggle again will re-mod the game and bring your AP savefiles back. SH3AP_Uninstall.bat similarly uninstalls all the Archipelago related files.  

# 
AI Disclaimer
AI was used throughout the coding and bug testing process for this project. If someone better at coding than me wants to attempt this project without AI then I'll support you with my full chest but at the moment with just me this wouldn't exist without AI assistance.
