from spotipy import SpotifyOAuth

import yt_dlp
import spotipy
import os
import yaml
import re

class AudioPipe:
    def __init__(self, path: str) -> None:
        self.path = path
        self.urls = []
        self.check_queue()
        self.get_spotipy()
    
    def check_queue(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        try:
            with open(load_config('queue')) as f:
                self.urls = [line.strip() for line in f.readlines()]
            
            print(
                f"{len(self.urls)} item is available in queue." if len(self.urls) == 1 
                else f"{len(self.urls)} items are available in queue.")

            if (len(self.urls) <= 0):
                self.urls = [input("Insert song url: ")]

        except FileNotFoundError:
            print('ERROR: Queue was not found, creating a new file instead.')

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

                self.spotify = spotipy.Spotify(
                    auth_manager=SpotifyOAuth(
                    client_id=client_id, client_secret=client_secret,
                    redirect_uri=redirect_uri, scope=scope))
            except spotipy.oauth2.SpotifyOauthError:
                print("ERROR: id or/and secret is/are missing. Configure it in the config file")
                exit()

    def get_playlist_name(self, url: str):
        if self.is_spotify(url) and load_config('spotify'):
            playlist_id = self.get_spotify_id(url)
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
        else: # case for youtube
            options = {
                'quiet': not load_config("verbose"),
                'extract_flat': True
            }
            with yt_dlp.YoutubeDL(options) as yt:
                info_dict = yt.extract_info(url, download=False)
                playlist_title = info_dict.get('title', 'Unknown Playlist')
                return playlist_title

    def is_spotify(self, url: str):
        pattern = r'https?://(?:open|play)\.spotify\.com/(?:(?:user/[^/]+|artist|album|track|playlist)/[a-zA-Z0-9]+)'
        return bool(re.search(pattern, url))
    
    def is_youtube(self, url: str):
        pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        return bool(re.search(pattern, url))

    def get_spotify_id(self, url: str):
        pattern = r'https?://open\.spotify\.com/(album|track|playlist)/([a-zA-Z0-9]+)'
        match = re.search(pattern, url)
        if match:
            return match.group(2)
        return None

    def download(self) -> None:
        for url in self.urls:
            # Check for valid url
            # Create a directory for playlist
            playlist = os.path.join(self.path, self.get_playlist_name(url))
            os.makedirs(playlist, exist_ok=True)

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

            def youtube():
                if self.is_youtube(url):
                    os.system('cls||clear')

                    # Downloading a song from youtube
                    with yt_dlp.YoutubeDL(options) as yt:
                        yt.download([url])

                    os.system('cls||clear')
                else:
                    os.system('cls||clear')

                    with yt_dlp.YoutubeDL(options) as yt:
                        result = yt.extract_info(query, download=False)
                        if 'entries' in result:
                            video = result['entries'][0]
                        else:
                            video = result
                return f"https://www.youtube.com/watch?v={video['id']}"

                os.system('cls||clear')
                
            def spotify():
                if self.is_spotify(url):
                    id = self.get_spotify_id(url)
                    try:
                        playlist_data = self.spotify.playlist_tracks(playlist_id)
                        for item in playlist_data.get('items', []):
                            # Gather information to feed algorithm with
                            track_info = item.get('track', {})
                            artists = [artist.get('name') for artist in track_info.get('artists', [])]

                            track_name = track_info.get('name')
                            artist = ", ".join(artists)
                        
                            query = f"{track_name} {artist}"

                            os.system('cls||clear')
                            print(f"Downloading {track_name} by {artist}...")

                            # Use song search algorithm
                            with yt_dlp.YoutubeDL(options) as yt:
                                try:
                                    info = yt.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                                    print(f"Downloaded: {info['title']}")
                                except Exception as e:
                                    print(f"ERROR: Could not download {track_name}: {e}")
                    
                        os.system('cls||clear')
                    except Exception as e:
                        print(f"ERROR: Failed to fetch {id} from spotify: {e}")

            if self.is_spotify(url) and load_config("spotify"):
                spotify()
            elif self.is_youtube(url):
                youtube()

# Handling user's config
def load_config(key: str):

    # Incase of a missing config file
    default_config = {
        'path': './downloads',
        'queue': 'queue.txt',
        'format': 'mp3',
        'thumbnail': True,
        'file_name': '%(title)s',
        'quality': 192,
        'verbose': True,
        'spotify': False,
        'id': '',
        'secret': ''
    }
    config = {}

    if os.path.exists('config.yaml'): # Config file check
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f) # Reading config
        except Exception as e:
            print(f"ERROR: could not read config file: {e}")
            print("Loading default settings.")
            config = default_config
    else:
        print("ERROR: config file was not found")
        print("Creating a new")
        with open('config.yaml', 'w') as f:
            yaml.dump(default_config, f)
        config = default_config
    
    return config.get(key, default_config.get(key))


def main():
    main = AudioPipe(load_config('path'))
    main.download()

if __name__ == "__main__":
    main()