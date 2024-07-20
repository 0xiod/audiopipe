from colorama import init as colorama_init
from spotipy.oauth2 import SpotifyOAuth
from colorama import Style
from colorama import Fore
from time import sleep
import datetime
import spotipy
import asyncio
import aiohttp
import yt_dlp
import toml
import os
import re

colorama_init()

ERROR = f'{Fore.RED}ERROR:{Style.RESET_ALL}'

class AudioPipe:
    def __init__(self, path) -> None:
        self.path = path
        self.urls = []

        # Will print any ascii art
        self.get_ascii()

        # Preparation for the program to run
        self.check_queue()

        # Connect with spotify api
        self.get_spotipy()

    
    # Check if path exists and read queue file in search of items
    def check_queue(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        try:
            with open(load_config('queue')) as f:
                self.urls = [line.strip() for line in f.readlines()]
            
            print(
                f"{len(self.urls)} item is available in queue." if len(self.urls) == 1 
                else f"{len(self.urls)} items are available in queue.")
        except FileNotFoundError:
            print(ERROR, 'Queue was not found, creating a new file instead.')

            with open(load_config('queue'), 'w') as f:
                f.write("Maybe don't delete the essential files next time ;)")
            
            sleep(1)
            os.system("cls||clear")
            self.__init__(load_config('path'))


    # Print your desired ascii art
    def get_ascii(self):
        if load_config("ascii_art"):
            with open("ascii.art", "r") as f:
                print(Fore.CYAN + f.read() + Style.RESET_ALL)
            

    # Initialize spotipy
    def get_spotipy(self):
        if load_config('spotify'):
            try:
                client_id = load_config('spotify_client_id')
                client_secret = load_config('spotify_client_secret')
                redirect_uri = 'http://localhost:8888/callback'
                scope = 'playlist-read-private'

                self.spotify = spotipy.Spotify(
                    auth_manager=SpotifyOAuth(
                    client_id=client_id, client_secret=client_secret,
                    redirect_uri=redirect_uri, scope=scope))
            except spotipy.oauth2.SpotifyOauthError:
                print(ERROR, "spotify_client_id or/and spotify_client_secret is/are missing. Configure it in config.toml")
                exit()


    # Fetching name of the playlist
    def get_playlist_name(self, url):
        if self.is_spotify(url):
            playlist_id = self.get_playlist_id(url)
            if playlist_id:
                try:
                    playlist_data = self.spotify.playlist(playlist_id)
                    playlist_name = playlist_data.get('name', 'Unknown Playlist')
                    return playlist_name
                except spotipy.SpotifyException as e:
                    print(ERROR, f"Failed to fetch playlist information from Spotify: {e}")
                    return 'Unknown Playlist'
            else:
                print(ERROR, "Failed to extract playlist ID from Spotify URL.")
                return 'Unknown Playlist'
        else:
            options = {
                'quiet': not load_config("verbose"),
                'extract_flat': True
            }
            with yt_dlp.YoutubeDL(options) as yt:
                info_dict = yt.extract_info(url, download=False)
                playlist_title = info_dict.get('title', 'Unknown Playlist')
                return playlist_title


    # Simple checks for spotify and youtube
    def is_spotify(self, url):
        pattern = r'https?://(?:open|play)\.spotify\.com/(?:(?:user/[^/]+|artist|album|track|playlist)/[a-zA-Z0-9]+)'
        return bool(re.match(pattern, url))
    
    def is_youtube(self, url):
        pattern = r'https?://(?:www\.)?(?:youtube\.com/\?v=|youtu\.be/)[a-zA-Z0-9_-]+'
        return bool(re.match(pattern, url))
    

    # Fetching spotify's album, playlist or track
    def get_playlist_id(self, url: str):
        pattern = r'https?://open.spotify.com/(?:playlist|album|track)/([a-zA-Z0-9]+)'
        match = re.match(pattern, url)
        if match:
            return match.group(1)
        return None

    # The main method for download process
    async def download(self) -> None:
        tasks = []

        async with aiohttp.ClientSession():            
            for url in self.urls:
                if self.is_youtube(url) or self.is_spotify(url): # Check for valid url
                    
                    # Create a playlist directory
                    playlist_path = os.path.join(self.path, self.get_playlist_name(url))
                    os.makedirs(playlist_path, exist_ok=True)

                    if not load_config('spotify'): # YouTube
                        tasks.append(self.youtube_dl(url, playlist_path))
                    else: # Spotify
                        playlist_id = self.get_playlist_id(url)
                        if playlist_id:
                            tasks.append(self.spotify_dl(playlist_id, playlist_path))
                else:
                    print(ERROR, "Invalid URL:", url)
        await asyncio.gather(*tasks)


    # Responsible for downloading spotify playlists
    async def spotify_dl(self, playlist_id, playlist) -> None:
        try:
            playlist_data = self.spotify.playlist_tracks(playlist_id)
            for item in playlist_data.get('items', []):

                # Gather of informations to feed algorithm with
                track_info = item.get('track', {})
                artists = [artist.get('name') for artist in track_info.get('artists', [])]

                track_name = track_info.get('name')
                artist = ", ".join(artists)
                
                query = f"{track_name} {artist}"

                start_time = asyncio.get_event_loop().time()

                os.system('cls||clear')
                print(f"Downloading {track_name} by {artist}...")

                # yt-dlp options for a song download
                options = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(playlist, f"{load_config('file_name')}.%(ext)s"),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': load_config('format'),
                        'preferredquality': str(load_config('quality')),
                    }],
                    'embedthumbnail': load_config('thumbnail'),
                    'quiet': not load_config('verbose'),
                    'progress_hooks': [lambda d: print(d['status'])] if load_config('verbose') else []
                }

                # Use of song search algorithm
                with yt_dlp.YoutubeDL(options) as yt:
                    try:
                        info = yt.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                        print(f"Downloaded: {info['title']}")
                    except Exception as e:
                        print(ERROR, f"Could not download {track_name}: {e}")
                        
                end_time = asyncio.get_event_loop().time()
                os.system('cls||clear')
                
                elapsed_time = datetime.timedelta(seconds=(end_time - start_time))

                print(f'Finished in {str(elapsed_time)}')
        except spotipy.SpotifyException as e:
            print(f"Failed to fetch tracks from Spotify playlist {playlist_id}: {e}")


    # Basic method of downloading youtube playlists
    async def youtube_dl(self, url, playlist) -> None:
        start_time = asyncio.get_event_loop().time()
        os.system('cls||clear')

        # yt-dlp options for a song download
        options = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(playlist, f"{load_config('file_name')}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': load_config('format'),
                'preferredquality': str(load_config('quality')),
            }],
            'embedthumbnail': load_config('thumbnail'),
            'quiet': not load_config('verbose'),
            'progress_hooks': [lambda d: print(d['status'])] if load_config('verbose') else []
        }

        # Downloading
        with yt_dlp.YoutubeDL(options) as yt:
            yt.download([url])
                
        end_time = asyncio.get_event_loop().time()
        os.system('cls||clear')

        elapsed_time = datetime.timedelta(seconds=(end_time - start_time))

        print(f'Finished in {str(elapsed_time)}')


# Handling user's config
def load_config(key: str):

    # Incase of missing config file
    default_config = {
        'path': './downloads',
        'ascii_art': False,
        'queue': 'queue.txt',
        'format': 'mp3',
        'thumbnail': True,
        'file_name': '%(title)s',
        'quality': 192,
        'verbose': True,
        'spotify': False,
        'spotify_client_id': '',
        'spotify_client_secret': ''
    }
    config = {}

    if os.path.exists('config.toml'): # Config file check
        try:
            with open('config.toml', 'r') as f:
                config = toml.load(f) # Reading config
        except Exception as e:
            print(f"Error reading config.toml: {e}")
            print("Loading default settings.")
            config = default_config
    else:
        print("config.toml not found, creating a new one with default config.")
        with open('config.toml', 'w') as f:
            toml.dump(default_config, f)
        config = default_config
    
    return config.get(key, default_config.get(key))


async def main():
    main = AudioPipe(load_config('path'))
    await main.download()

if __name__ == "__main__":
    asyncio.run(main())
