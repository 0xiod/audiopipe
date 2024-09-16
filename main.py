from spotipy import SpotifyOAuth
from spotipy import SpotifyException, SpotifyOauthError
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
from spotipy import Spotify
from yt_dlp import YoutubeDL
from re import search

import time
import logging
import os

init(autoreset=True)

class Logger(logging.Formatter):
    CODES = {
        logging.DEBUG: Fore.CYAN + "[DEBUG] " + Style.RESET_ALL + "%(message)s",
        logging.INFO: Fore.GREEN + "[INFO] " + Style.RESET_ALL + "%(message)s",
        logging.WARNING: Fore.YELLOW + "[WARNING] " + Style.RESET_ALL + "%(message)s",
        logging.ERROR: Fore.RED + "[ERROR] " + Style.RESET_ALL + "%(message)s",
        logging.CRITICAL: Fore.RED + Style.BRIGHT + "[CRITICAL] " + Style.RESET_ALL + "%(message)s"
    }

    def format(self, record):
        log_fmt = self.CODES.get(record.levelno, self.CODES[logging.INFO])
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(Logger())

logger.addHandler(console_handler)

class AudioPipe:
    def __init__(self, path: str) -> None:
        self.path = path
        self.urls = []
        self.check_queue()
        self.spotify = self.get_spotipy()
    
    def check_queue(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
 
        try:
            with open(load_config('queue'), 'r') as f:
                self.urls = [line.strip() for line in f.readlines()]
            
            logger.info(
                f"{len(self.urls)} item is available in queue." if len(self.urls) > 1 
                else f"{len(self.urls)} items are available in queue.")

            if (len(self.urls) <= 0):
                try:
                    self.urls = [input("Insert song or playlist URL: ")]
                except KeyboardInterrupt:
                    print(" (interrupted)")

        except FileNotFoundError:
            logger.error('Queue file was not found, creating a new file.')

            with open(load_config('queue'), 'w') as f:
                f.write("Maybe don't delete the essential files next time ;)")
            
            os.system("cls||clear")
            self.__init__(load_config('path'))

    def get_spotipy(self):
        if load_config('spotify'):
            try:
                client_id = load_config('id')
                client_secret = load_config('secret')
                redirect_uri = 'http://localhost:8888/callback'
                scope = 'playlist-read-private'

                return Spotify(
                    auth_manager=SpotifyOAuth(
                    client_id=client_id, 
                    client_secret=client_secret,
                    redirect_uri=redirect_uri, 
                    scope=scope))

                logger.info(f"Spotify authentication was successful for {client_id}")
            except SpotifyOauthError as e:
                logger.error(f"Spotify authentication has failed: {e}")
                exit()
        return None

    def get_playlist_name(self, url: str):
        if self.is_spotify(url) and load_config('spotify'):
            playlist_id = self.get_playlist_id(url)
            if playlist_id and self.spotify:
                try:
                    return self.spotify.playlist(playlist_id).get('name', 'Unknown Playlist')
                except SpotifyException as e:
                    logger.error(f"Failed to fetch playlist information from Spotify: {e}")
                    return 'Unknown Playlist'
            else:
                logger.error("Failed to extract playlist ID from Spotify URL.")
                return 'Unknown Playlist'
        else: # case for youtube
            options = {'quiet': not load_config("verbose"), 'extract_flat': True}
            with YoutubeDL(options) as yt:
                info_dict = yt.extract_info(url, download=False)
                return info_dict.get('title', 'Unknown Playlist')

    def is_spotify(self, url: str):
        pattern = r'https?://(?:open|play)\.spotify\.com/(?:(?:user/[^/]+|artist|album|track|playlist)/[a-zA-Z0-9]+)'
        return bool(search(pattern, url))

    def get_playlist_id(self, url: str):
        pattern = r'https?://open\.spotify\.com/(album|track|playlist)/([a-zA-Z0-9]+)'
        match = search(pattern, url)
        return match.group(2) if match else None

    def bulk_download(self, method):
        with ThreadPoolExecutor(max_workers=int(load_config("threads"))) as executor:
            executor.map(method)

    def download(self) -> None:
        for url in self.urls:
            playlist_name: str = self.get_playlist_name(url)
            playlist = os.path.join(self.path, playlist_name)
            os.makedirs(playlist, exist_ok=True)

            proxies = load_config('proxies')
            proxy = None

            def get_random_proxy():
                from random import choice
                return choice(proxies) if proxies else None

            options = {
                'format': load_config('format'),
                'outtmpl': os.path.join(playlist, f"{load_config('file_name')}.%(ext)s"),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': load_config('codec'),
                    'preferredquality': str(load_config('bitrate')),
                },
                {
                    'key': 'FFmpegMetadata'
                }],
                'embedthumbnail': load_config('thumbnail'),
                'socket_timeout': 40,
                'caching': load_config('caching'),
                'http_chunk_size': int(load_config('http_chunk_size')) * int(load_config('http_chunk_size')),
                'external_downloader': load_config('downloader'),
                'external_downloader_args': load_config('downloader_args'),
                'log_level': 'WARNING',
                'logger': logger,
                'logtostderr': False
            }

            def youtube():
                nonlocal proxy
                if load_config('proxy') and proxies:
                    options['proxy'] = proxy

                os.system('cls||clear')
                logger.info(f"Starting to download: {url}")

                time_start = time.perf_counter()

                # Downloading a song from youtube
                with YoutubeDL(options) as yt:
                    yt.download([url])

                time_elapsed = (time.perf_counter() - time_start)

                os.system('cls||clear')
                logger.info("Finished downloading in %.1fs", time_elapsed)
                
            def spotify():
                nonlocal proxy

                playlist_id = self.get_playlist_id(url)
                if not playlist_id:
                    logger.error("Invalid Spotify playlist ID!")
                    return
                
                playlist_tracks = self.spotify.playlist_tracks(playlist_id)
                for item in playlist_tracks['items']:
                    # Gather information to feed algorithm with
                    track = item['track']
                    track_name = track['name']
                    artist_name = ', '.join([artist['name'] for artist in track['artists']])
                    query = f"{track_name} {artist_name}"

                    if proxy and load_config('proxy'):
                        options['proxy'] = proxy

                    os.system('cls||clear')
                    logger.info(f"Searching YouTube for {track_name} by {artist_name}...")
                    
                    time_start = time.perf_counter()

                    # Use song search algorithm
                    with YoutubeDL(options) as yt:
                        try:
                            yt.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                        except Exception as e:
                            logger.error(f"Could not download {track_name}: {e}")
                    time_elapsed = (time.perf_counter() - time_start)
                    
                    os.system('cls||clear')
                    logger.info("Finished downloading in %.1fs", time_elapsed)

            if load_config('proxy'):
                proxy = get_random_proxy()
                logger.info(f"You are currently using proxy: {proxy}")

            if load_config('pools'):
                self.bulk_download(spotify() if load_config("spotify") and self.is_spotify(url) else youtube())
            else:
                if load_config("spotify") and self.is_spotify(url): 
                    spotify() 
                else: 
                    youtube()

# Handling user's config
def load_config(key: str):
    import yaml

    # Incase of a missing config file
    default_config = {
        # general
        'path': './downloads',
        'queue': 'queue.txt',
        # spotify
        'spotify': False,
        'id': '',
        'secret': '',
        # file
        'format': 'bestaudio/best',
        'codec': 'mp3',
        'thumbnail': True,
        'file_name': '%(title)s',
        'bitrate': 256,
        # networking
        'proxy': False,
        'proxies': [],
        # performance
        'pools': True,
        'threads': 4,
        'downloader': 'aria2c',
        'downloader_args': ['-x', '16', '-k', '1M'],
        'http_chunk_size:': 1024,
        'caching': True
    }
    config = {}

    if os.path.exists('config.yaml'): # Config file check
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f) # Reading config
        except Exception as e:
            logger.error(f"Could not read the config file: {e}")
            config = default_config
            logger.info("Default config has been loaded!")
    else:
        logger.error("Config file not found!")
        logger.info("Creating new config file with a default config.")
        with open('config.yaml', 'w') as f:
            yaml.dump(default_config, f)
        config = default_config
        logger.info("Default config has been loaded!")

    return config.get(key, default_config.get(key))

def main():
    main = AudioPipe(load_config('path'))
    main.download()

if __name__ == "__main__":
    main()