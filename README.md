# RPi_AIY
Files for use with Google AIY on Raspberry Pi

This is for the customization and adding extra commands to the Raspberry Pi Voice Google AIY install.

The current action.py includes the extra commands to

Added ability to play youtube audio - developed by Mike Redrobe
https://www.raspberrypi.org/forums/viewtopic.php?f=114&t=182665

Added ability to play streaming radio stations
Example :
radio BBC Radio 1

Added ability to play podcasts
Example:
podcast Good Job Brain

The radio and podcast commands use VLC so you have to install this on your Raspberry Pi first.

sudo apt update
sudo apt upgrade
sudo apt install vlc

Radio Stations supported are:
Absolute Radio
Absolute 80s
Absolute 90s
Absolute 00s
Eagle Radio
BBC Radio 1
BBC Radio 2
BBC Radio 3
BBC Radio 4
Capital FM

Podcasts Supported are:
Good Job Brain
No Such Thing As a Fish
Freakonomics

