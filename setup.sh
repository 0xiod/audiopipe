#!/bin/sh

# Ask for user confirmation
printf 'Are you sure to compile the project to a binary (Yes/No)? '
old_stty_cfg=$(stty -g)
stty raw -echo
answer=$(head -c 1)
stty $old_stty_cfg

if [ "$answer" != "${answer#[Yy]}" ]; then
  echo "Yes"

  # Trap Ctrl+C
  trap ctrl_c INT

  ctrl_c() {
    printf "Cleaning up..."
    rm -rf build/ main.dist/
    rm -rf dist/ main.build/
    rm -rf onefile/ main.onefile-build/
    printf " done!\n"
    exit 1
  }

  # Clean up directories and files
  printf "Cleaning up..."
  rm -rf build/ main.dist/
  rm -rf dist/ main.build/
  rm -rf onefile/ main.onefile-build/
  rm -f main.bin audiopipe.bin
  printf " done!\n"

  # Remove lazy extractors
  printf "Removing lazy extractors..."
  rm -rf .venv/lib64/python3*/site-packages/yt_dlp/extractor/lazy_extractors.py
  rm -rf .venv/lib/python3*/site-packages/yt_dlp/extractor/lazy_extractors.py
  printf " done!\n"

  # Activating virtual environment
  printf "Activating virtual environment..."
  source .venv/bin/activate
  printf " done!\n"
  
  # Install dependencies
  echo "Installing dependencies..."
  pip install --upgrade pip
  pip install nuitka
  pip install -r requirements.txt

  # Compile the project using Nuitka
  echo "Compilation will begin..."
  nuitka --standalone --product-version=1.0 --product-name=AudioPipe --static-libpython=yes --onefile main.py

  # Move compiled files to their respective directories
  printf "Moving files..."
  mv -f main.dist/ dist/
  mv -f main.build/ build/
  mv -f main.onefile-build/ onefile/
  mv -f main.bin audiopipe.bin
  printf "done!\n"
else
  echo "No"
fi

