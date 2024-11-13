from spotipy import SpotifyOAuth
from spotipy import SpotifyException, SpotifyOauthError
from concurrent.futures import ThreadPoolExecutor
from spotipy import Spotify
from yt_dlp import YoutubeDL
from re import search
import time
import os
import sys

CONFIG = {
    # general:
    "path": "/mnt/data/music/.new/", # folder where your songs will belong
    "queue": "queue.txt", # you can use queue to download more than 1 song

    # spotify:
    "spotify": False, # enable to download spotify playlists/songs
    "id": "",
    "secret": "",

    # file:
    "format": "bestaudio/best", # overall quality of the song
    "codec": "mp3", # we support: mp3, mkv/mka, ogg/opus/flac, m4a/mp4/m4v/mov
    "thumbnail": True, # download song with thumbnail
    "file_name": "%(title)s", # song naming convention
    "bitrate": 320, # sound quality of the song

    # networking:
    "proxy": False, # you can use your own proxies
    "proxies": {''}, # here you can put your proxies

    # performance:
    "pools": True, # concurrent parallel downloads (ThreadPoolExecutor)
    "threads": 4, # maximum amount of threads used by ThreadPoolExecutor
    "downloader": 'aria2c', # change this only if you know what you're doing
    "downloader_args": ['-x', '16', '-k', '1M'], # -x = connections, -k = chunks in MB
    "http_chunk_size": 1024, # fragmentation of song into chunks (Kb)
    "caching": True # speed up of repetitive and avoiding retries
}

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
            with open(CONFIG.get("queue"), 'r') as f:
                self.urls = [line.strip() for line in f.readlines()]
            
            print(
                f"{len(self.urls)} item is available in queue." if len(self.urls) > 1 
                else f"{len(self.urls)} items are available in queue.")

            if (len(self.urls) <= 0):
                try:
                    self.urls = [input("Insert song or playlist URL: ")]
                except KeyboardInterrupt:
                    print(" (interrupted)")

        except FileNotFoundError:
            print('Queue file was not found, creating a new file.')

            with open(CONFIG.get("queue"), 'w') as f:
                f.write("")
            
            self.__init__(CONFIG.get("path"))

    def get_spotipy(self):
        if CONFIG.get("spotify"):
            try:
                client_id = CONFIG.get("id")
                client_secret = CONFIG.get("secret")
                redirect_uri = 'http://localhost:8888/callback'
                scope = 'playlist-read-private'

                return Spotify(
                    auth_manager=SpotifyOAuth(
                    client_id=client_id, 
                    client_secret=client_secret,
                    redirect_uri=redirect_uri, 
                    scope=scope))

                print(f"Spotify authentication was successful for {client_id}")
            except SpotifyOauthError as e:
                print(f"Spotify authentication has failed: {e}")
                exit()
        return None

    def get_playlist_name(self, url: str):
        if self.is_spotify(url) and CONFIG.get("spotify"):
            playlist_id = self.get_playlist_id(url)
            if playlist_id and self.spotify:
                try:
                    return self.spotify.playlist(playlist_id).get('name', 'Unknown Playlist')
                except SpotifyException as e:
                    print(f"Failed to fetch playlist information from Spotify: {e}")
                    return 'Unknown Playlist'
            else:
                print("Failed to extract playlist ID from Spotify URL.")
                return 'Unknown Playlist'
        else: # case for youtube
            options = {'quiet': True, 'extract_flat': True}
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
        with ThreadPoolExecutor(max_workers=int(CONFIG.get("threads"))) as executor:
            executor.map(method)

    def download(self) -> None:
        for url in self.urls:
            playlist_name: str = self.get_playlist_name(url)
            playlist = os.path.join(self.path, playlist_name)
            os.makedirs(playlist, exist_ok=True)

            proxies = CONFIG.get("proxies")
            proxy = None

            def get_random_proxy():
                from random import choice
                return choice(proxies) if proxies else None

            options = {
                'format': CONFIG.get("format"),
                'outtmpl': os.path.join(playlist, f"{CONFIG.get("file_name")}.%(ext)s"),
                'postprocessors': 
                    [{'key': 'FFmpegExtractAudio',
                    'preferredcodec': CONFIG.get("codec"),
                    'preferredquality': str(CONFIG.get("bitrate"))},
                    {'key': 'FFmpegMetadata'}],
                'embedthumbnail': True,
                'socket_timeout': 40,
                'caching': CONFIG.get("caching"),
                'http_chunk_size': int(CONFIG.get("http_chunk_size")) * int(CONFIG.get('http_chunk_size')),
                'external_downloader': CONFIG.get('downloader'),
                'external_downloader_args': CONFIG.get('downloader_args'),
            }

            def youtube():
                nonlocal proxy
                if CONFIG.get('proxy') and proxies:
                    options['proxy'] = proxy

                os.system('cls||clear')
                print(f"Starting to download: {url}")

                time_start = time.perf_counter()

                # Downloading a song from youtube
                with YoutubeDL(options) as yt:
                    yt.download([url])

                time_elapsed = (time.perf_counter() - time_start)

                os.system('cls||clear')
                print(f"Finished downloading in {round(time_elapsed, 2)}s")
                
            def spotify():
                nonlocal proxy

                playlist_id = self.get_playlist_id(url)
                if not playlist_id:
                    print("Invalid Spotify playlist ID!")
                    return
                
                playlist_tracks = self.spotify.playlist_tracks(playlist_id)
                for item in playlist_tracks['items']:
                    # Gather information to feed algorithm with
                    track = item['track']
                    track_name = track['name']
                    artist_name = ', '.join([artist['name'] for artist in track['artists']])
                    query = f"{track_name} {artist_name}"

                    if proxy and CONFIG.get('proxy'):
                        options['proxy'] = proxy

                    os.system('cls||clear')
                    print(f"Searching YouTube for {track_name} by {artist_name}...")
                    
                    time_start = time.perf_counter()

                    # Use song search algorithm
                    with YoutubeDL(options) as yt:
                        try:
                            yt.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                        except Exception as e:
                            print(f"Could not download {track_name}: {e}")
                    time_elapsed = (time.perf_counter() - time_start)
                    
                    os.system('cls||clear')
                    print(f"Finished downloading in {round(time_elapsed, 2)}s")

            if CONFIG.get('proxy'):
                proxy = get_random_proxy()
                print(f"You are currently using proxy: {proxy}")

            if CONFIG.get('pools'):
                self.bulk_download(spotify() if CONFIG.get("spotify") and self.is_spotify(url) else youtube())
            else:
                if CONFIG.get("spotify") and self.is_spotify(url): 
                    spotify() 
                else: 
                    youtube()

if __name__ == "__main__":
    AudioPipe(CONFIG.get("path")).download()