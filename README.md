
# AudioPipe
Command-line audio downloader based on yt-dlp, that does a good job on downloading your favourite songs or playlists. It is made in mind of compatibility and intergration between YouTube and Spotify

## Installation

**1. Installing dependencies**

To use AudioPipe you have to install python dependencies used by AudioPipe.

The command will be diffrent depending on your operating system. Here I've prepared some examples of installing those dependencies on diffrent operating systems.

Windows:
```bash
python3 -m pip install -r requirements.txt
```

Linux/MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Run**

Please execute this command in the project's directory. 

```bash
python main.py
```

## Configuration

This will cover getting the spotify intergration working with your account

1. Go to this website: [Spotify developer dashboard](https://developer.spotify.com/dashboard).

2. You have to be already logged in or you just have to log in into your spotify account.

3. Click create app (just to clear things out, you have to be in the dashboard).

![1](https://i.ibb.co/qx11C9B/1.png)

4. After creating new app click on it and go into it's settings.

![2](https://i.ibb.co/7n2VcS3/2.png)

5. Copy the Client ID and the Client secret of your newly created app.

![3](https://i.ibb.co/VjVgFSj/image.png)

6. Replace these two variables in the CONFIG, and you're now good to go!
