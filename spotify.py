from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy import SpotifyOauthError
from spotipy import Spotify, SpotifyException

class Spotify:
    # Some parts of code belong to spotDL project
    # and their owners respecively.
    # https://github.com/spotDL/spotify-downloader

    def init(client_id: str, client_secret: str, headless: bool, user_auth, auth_token):
        """ Make a request to Spotify using the user's credentials. """

        print(f"Initializing spotify...")

        credential_manager = None

        try:
            # Use SpotifyOAuth as auth manager
            if user_auth:
                credential_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="http://127.0.0.1:9900/",
                scope="user-library-read,user-follow-read,playlist-read-private",
                open_browser=not headless,
            )

            # Use SpotifyClientCredentials as auth manager
            else:
                credential_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
            )
            
            if auth_token is not None:
                credential_manager = None

            # Create instance
            instance = super().__call__(
                auth=auth_token,
                auth_manager=credential_manager,
                status_forcelist=(429, 500, 502, 503, 504, 404),
            )

            print(f"Spotify has been successfully authenticated!")
            return instance

        except SpotifyOauthError as err:
            raise err

    def get_playlist_id(urls: str):
        """ Returns id of a spotify playlist provided via url. """
        from re import search

        # Pattern of an url regular expression. 
        pattern = r'https?://open\.spotify\.com/(album|track|playlist)/([a-zA-Z0-9]+)'
        # Match url with the patter above.
        for url in urls:
            match = search(pattern, url)

        return match.group(2) if match else None

    def is_spotify(urls: str):
        """ Return true if provided url is a spotify url. """
        from re import search

        pattern = r'https?://(?:open|play)\.spotify\.com/(?:(?:user/[^/]+|artist|album|track|playlist)/[a-zA-Z0-9]+)'
        
        for url in urls:
            return bool(search(pattern, url))

    def get_playlist_name(playlist_id:str):
        """ Extract playlist name from Spotify. """

        if playlist_id:
            try:
                # Extract the playlist title from spotify
                return Spotify.playlist(playlist_id).get('name', 'Unknown playlist')
            except SpotifyException as err:
                raise err
                return 'Unknown playlist'
        else:
            print("Failed to extract playlist ID from Spotify URL.")
            return 'Unknown playlist'

    def download(urls: str, options: list, *proxies: list):
        """ Download Spotify content from YouTube. """
        from yt_dlp import YoutubeDL
        from time import perf_counter
        from os import system

        for url in urls:
            playlist_id = Spotify.get_playlist_id(url)

        if not playlist_id:
            print("Invalid Spotify playlist ID!")
            return

        # Make a list containing all of the tracks.                
        playlist_tracks = Spotify.playlist_tracks(playlist_id)
        for item in playlist_tracks['items']:
            # Gather information to feed the algorithm with.
            track = item['track']
            track_name = track['name']
            artist_name = ', '.join([artist['name'] for artist in track['artists']])
            query = f"{track_name} {artist_name}"

            # Again same as in YouTube().download 
            # it'll check if there are proxies.
            if proxies != None:
                options['proxy'] = proxies

            system('cls||clear')
            print(f"Searching YouTube for {track_name} by {artist_name}...")
                    
            # Initialize 1st a performance counter.
            time_start = perf_counter()

            # Query using YouTube search algorithm and download the song.
            with YoutubeDL(options) as yt:
                yt.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                
            # Calculate time that has passed since the 'time_start' initialization.
            time_elapsed = (perf_counter() - time_start)
            
            # Clear the output and print elapsed time.
            print(f"Finished downloading in {round(time_elapsed, 2)}s")
