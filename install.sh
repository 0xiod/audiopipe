#!/bin/bash

# script for those who use arch btw
yes | sudo pacman -S python-toml python-colorama python-yt_dlp python-aiohttp
git clone https://aur.archlinux.org/python-spotipy.git
cd python-spotipy
makepkg -si
cd ..
python main.py