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
        rm -rf build/ main.dist/
        rm -rf dist/ main.build/
        rm -rf onefile/ main.onefile-build/
    }

    rm -rf build/ main.dist/
    rm -rf dist/ main.build/
    rm -rf onefile/ main.onefile-build/
    rm -f main.bin
    rm -rf .venv/lib64/python3.12/site-packages/yt_dlp/extractor/lazy_extractors.py
    rm -rf .venv/lib/python3.12/site-packages/yt_dlp/extractor/lazy_extractors.py

    source .venv/bin/activate
    pip install nuitka
    pip install -r requirements.txt

    nuitka --standalone --product-version=1.0 --product-name=AudioPipe --static-libpython=yes --onefile main.py
    
    mv main.dist/ dist/
    mv main.build/ build/
    mv main.onefile-build/ onefile/
    mv main.bin audiopipe.bin
else
    echo No
fi
