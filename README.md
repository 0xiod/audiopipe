# AudioPipe
A python command-line interface audio downloader utilizing `yt-dlp`. It is fast, lightweight, minimal,
functional and easy to use. It was created with portability, compability and intergration between services like **YouTube** and **Spotify** in mind.

## Installation process

<!-- ### Automatic (recommended) -->

<!-- #### Install using pip
Make sure you've installed `pip` on your system. 

**Linux/macOS**
```bash
python -m ensurepip --upgrade
```

**Windows**
```bash
py -m ensurepip --upgrade
```

After making sure you can just install it by pasting this command to your terminal:

```bash
pip install audiopipe
``` -->

<!-- #### Install and execute binary
Simply download and run binary file (note if you use windows you might rename the binary to .exe):

File|Description|Operating System
:---|:---|:---
[audiopipe.bin](https://gitlab.com/iodomi/AudioPipe/releases/latest/download/audiopipe.bin)|Platform independent binary.|**Any**
-->

### Manual

#### TL;DR (Linux)

Install deps:
```bash
apt-get install ffmpeg git
```
Install AudioPipe:
```bash
git clone https://codeberg.org/iodomi/audiopipe.git
```
Install pip deps:
```bash
cd audiopipe/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Run:
```bash
python3 src/main.py
```

#### Full guide

**1. Cloning the repository**

To do the following you need to have installed `git` on your system:

**Debian/Ubuntu**
```bash
apt-get install git
```
**Other Linux distros** 

https://git-scm.com/downloads/linux


**macOS**
```bash
brew install git
```

**Windows**

https://git-scm.com/downloads/win

and execute this command:
```bash
git clone https://codeberg.org/iodomi/audiopipe.git
```

**2. Installing dependencies**

To use AudioPipe you will have to install a few python dependencies and FFmpeg in order for it to work.

The commands will be diffrent depending on operating system you're using. Here I've prepared some examples of installing those dependencies on diffrent operating systems (If your OS is not there just Google it by yourself):

**Linux/macOS:**
```bash
cd audiopipe/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python3 -m pip install -r requirements.txt
```

**FFmpeg Installation:**

You will also need FFmpeg on your system and it doesn't matter if you use Windows, Linux or macOS
just go here: https://ffmpeg.org/download.html and follow along. Otherwise yt-dlp will complain:
```python
ERROR: Postprocessing: ffprobe and ffmpeg not found. Please install or provide the path using --ffmpeg-location
```
while trying to download stuff. You can also install it using package manager of course:
```bash
apt-get install ffmpeg
```

**3. Run**

If you've successfully followed along with the previous steps you can now change directory to the AudioPipe project folder and execute the file named main.py using your system's python:

```bash
python3 src/main.py
```

Alternatively you may like to run AudioPipe with a python package and dependency manager like [`Poetry`](https://python-poetry.org/). **It is worth noting that you should skip the step 2 (not the FFmpeg part tho), while using a manager.** It's because most managers install dependencies automatically. Here's an example of running this program with help of [`uv`](https://docs.astral.sh/uv/) package manager:

```bash
uv run src/main.py
```

Of course to make it work you have to be in the project directory as well as before.

## Configuration

This will cover getting the Spotify intergration working alongside with your Spotify account.

1. First visit this website: https://developer.spotify.com/dashboard

2. You have to be already logged in or you just have to log in into your spotify account.

3. Click on create app button (just to clear things out, you'll have to go to the dashboard).

![1](https://i.ibb.co/qx11C9B/1.png)

4. After creating new app click on it and go into it's settings.

![2](https://i.ibb.co/7n2VcS3/2.png)

5. Copy the Client ID and the Client secret of your newly created app.

6. Now you can put those into config.json or just pass them as an argument and downloading enjoy your playlists!

## Backstory
I've created this program as I didn't like other audio downloaders
out there and wanted one that's more snappy and small.
I have come to a conclusion that it's best to do it by myself.
And because of my close friends who found it really useful,
I got even more motivated to work on it.

## TO:DO
- Add on PyPI (in progress)
- Build binary

## Licensing
This project is licensed under the GNU General Public License v3.0 or later.
