#!/bin/sh

# Not working properly, yet...

printf 'Are you sure to compile the project to a binary (Yes/No)? '
old_stty_cfg=$(stty -g)
stty raw -echo ; answer=$(head -c 1) ; stty $old_stty_cfg
if [ "$answer" != "${answer#[Yy]}" ]; then
    echo Yes
    trap ctrl_c INT

    ctrl_c () {
        echo "Cleaning up..."
        rm -rf build/ audiopipe.dist/
        rm -rf dist/ audiopipe.build/
        rm -rf onefile/ audiopipe.onefile-build/
    }

    rm -rf build/ audiopipe.dist/
    rm -rf dist/ audiopipe.build/
    rm -rf onefile/ audiopipe.onefile-build/
    rm -f audiopipe.bin
    rm -f .venv/lib/yt_dlp/extractor/lazy_extractors.py
    rm -f .venv/lib64/yt_dlp/extractor/lazy_extractors.py

    source .venv/bin/activate
    pip install nuitka

    nuitka --standalone --product-version=1.0 --product-name=AudioPipe --static-libpython=yes --onefile audiopipe.py
    
    mv audiopipe.dist/ dist/
    mv audiopipe.build/ build/
    mv audiopipe.onefile-build/ onefile/   
else
    echo No
fi