from platformdirs import PlatformDirs
import sys
import os

"""
Welcome to the source code of AudioPipe!
This is the place you've been prooly looking for
if you've ever wanted a Spotify and YouTube audio downloader
that's fast, lightweight, minimal, functional,
portable, hackable, etc.

I've created this program as I didn't like other audio downloaders
out there and wanted one that's more snappy and small.
I have come to a conclusion that's it's best to do it by myself.
As because of my close friends who found it really useful to use,
I got even more motivated to work towards it.

This project is licensed under the GNU General Public License v3.0 or later.
"""

class Logger:
    def debug(self, msg):
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

class AudioPipe:
    def __init__(self):
        # The names of the updates belong to the species of fish.
        self.codename = "Goldfish"
        self.version = 1.0

        # Give platformdirs program name and author. 
        self.dirs = PlatformDirs("audiopipe", "iodomi")
        
        if not os.path.exists(self.dirs.user_config_path):
            os.makedirs(self.dirs.user_config_path)
        
        # Store path to config as a variable for convinience.
        self.config_path = os.path.join(self.dirs.user_config_path, "config.json")

        # A queue file that is used to read urls by program
        # and write them by user.
        self.queue_path = os.path.join(self.dirs.user_config_path, "queue.txt")

        # You generally shouldn't modify this variable.
        self.DEFAULT_CONFIG = \
        {
            # BASIC:
            "path": "downloads/", # Folder where your songs will belong.
            "queue": False, # Do you wish to use queue?
            "debug": False, # Do you wish to print unusual amount of logs?
            "verbose": False, # Would you like yt-dlp to print more logs?
            "search": False, # Would you like to search YouTube instead of passing url.
            "silent": False, # Would you like to silent (almost) all yt-dlp messsages?

            # SPOTIFY:
            "spotify": False, # Check to download music from spotify.
            "auth": False, # Do you wish to authenticate spotify session?
            "id": None, # Here you can pass your spotify app's ID,
            "secret": None, # and its secret.
            "token": None, # You can pass your app token.
            "headless": False, # Would you like to authenticate spotify without using a browser?

            # AUDIO FILE:
            "format": "bestaudio/best", # Genrally speaking the quality of songs.
            "codec": "mp3", # Supported formats: mp3, mkv/mka, ogg/opus/flac, m4a/mp4/m4v/mov
            "thumbnail": False, # Do you wish to download songs with covers?
            "bitrate": 320, # Sound quality of a song, metered in Kbit/s.

            # NETWORKING:
            "proxies": [''], # Put the proxies you want here...

            # PERFORMANCE:
            "multithreading": False, # Concurrent parallel downloads (it mostly means better performance).
            "threads": 1, # The maximum amount of threads used.
            "caching": False, # Speeds up the repetitive processes and avoids retries.

            # ADVANCED:   
            "downloader": 'aria2c', # Download utility that's beign used.
            "downloaderargs": ['-x', '16', '-k', '1M'], # -x = connections, -k = chunks in MB
            "chunksize": 1024 # Fragmentation of a song into chunks (metered in Kb)
        }

        # I think it's easier to check for config using a variable.
        self.using_config = False

        # Check if there are any arguments provided.
        if sys.argv[1:] != []:
            self.parse_commands()
        else:
            self.command = None

        # Check custom config is passed as a cli argument and it's type is not none.
        if hasattr(self.command, "config") and type(self.command.config) != None:
            self.config = self.load_config(self.command.config)
            if self.get_value("debug"):
                print(f"set config={self.command.config}")
            self.using_config = True
        # Else if config file exists on the system. 
        elif os.path.exists(self.config_path):
            self.config = self.load_config(self.config_path)
            self.using_config = True
        else:
            self.config = self.DEFAULT_CONFIG
            if self.get_value("debug"):
                print("set config=defualt")

        # Urls that later can be provided by a user.
        self.urls = []

        if not os.path.exists(self.dirs.user_data_dir):
            os.makedirs(self.dirs.user_data_dir)

        # Set path to where downloaded files will be.
        self.path = os.path.join(self.dirs.user_data_dir, self.get_value("path"))

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        if self.get_value("spotify"):
            from spotify import Spotify
            # Load and authenticate Spotify module.
            Spotify.init(
                client_id=self.get_value("id"),
                client_secret=self.get_value("secret"),
                headless=self.get_value("headless"),
                user_auth=self.get_value("auth"),
                auth_token=self.get_value("token")
            )

        # Get the proxy list.
        self.proxy_list = self.get_value("proxies")

        # Is YouTube searching on?
        self.search = self.get_value("search")

        # Ask for url input or check queue file for it.
        if not self.get_value("queue"):
            self.urls = self.get_user_input()
        elif self.is_queue_empty(self.queue_path):
            # Inform the user that queue file is empty.
            print("You're using queue but it's seems empty...")
            sys.exit()
        else:
            self.urls = self.check_queue(self.queue_path)
        
        if self.get_value("caching"):
            # Make directory where cache file will be saved.
            if not os.path.exists(self.dirs.user_cache_dir):
                os.makedirs(self.dirs.user_cache_dir)

    def get_value(self, key: str):
        """
        Retrieves a value from the current config or
        a custom config provided by a command or a command.
        """

        # In the first place we check if command has attribute and it's valid.
        if hasattr(self.command, key) and getattr(self.command, key) != None:
            return getattr(self.command, key)
        # Check if user is using config file.
        if self.using_config:
            return self.config.get(key)
        # Try to get attribute from self (f.e. self.search)
        elif hasattr(self, key):
            return getattr(self, key)
        # If everything above fails load from default config.
        else:
            return self.DEFAULT_CONFIG.get(key)

    def load_config(self, config_file):
        """ Loading pre-existing config from config json file. """
        import json

        try:
            # Read a config file and save to f.
            with open(config_file, 'r') as f:
                return json.load(f)

        except FileNotFoundError:
            print(f"Could not find {config_file}, to fix please rerun with -g flag...")
            return None

        # except json.JSONDecodeError as err:
        #     raise err
        
        except Exception as err:
            raise err

    def write_config(self, json_str, config_path):
        """ Write config from json_str to a file. """
        with open(config_path, "w") as f:
            f.write(json_str)
        if self.get_value("debug"):
            print("[info] Config has been written to a file!")

    def gen_config(self, config_template, *ask):
        """
        Generates config file, does so by dumping values from
        config template and putting them inside of a .json file.
        """

        import json
        print("Generating config... ", end='')

        def serialize_sets(obj):
            # Check if object is instance of a set.
            if isinstance(obj, set):
                return list(obj)
            return obj

        # Dump config_template to a string.
        json_str = json.dumps(config_template, default=serialize_sets, indent=4)
        print(f"generated!\n", end='')
    
        if ask and ask != None:
            try:
                response = input("Would you like save config to file? [Yes/No] ").lower()
            except KeyboardInterrupt:
                print(" (interrupted)")
                sys.exit()

            if response == "" or response == "y" or response == "yes":
                try:
                    # Write json_str to a config file.
                    self.write_config(json_str, self.config_path)
                except FileNotFoundError as err:
                    print(f"Config file not found...")
                    if self.get_value("debug"):
                        print(f"[err] {err}")
                    return None
            else:
                # Print json_str instead of saving.
                json_str = json.dumps(config_template, default=serialize_sets)
                print(json_str)
        else:
            # Write without asking for permission to do so.
            self.write_config(json_str, self.config_path)

    def get_user_input(self):
        """ Get url input from user and return it. """

        try:
            if self.search:
                url = input("Enter the name of a song or playlist: ")
            else:
                url = input("Enter the url to a song or playlist: ")
            return [url]

        except KeyboardInterrupt:
            print(" (interrupted)")
            sys.exit()

        except Exception as err:
            raise err

    def is_queue_empty(self, queue_file):
        """
        A simple function to check if queue file
        that returns True if queue is empty.
        """

        try:
            with open(queue_file, 'r') as f:
                line = [line.strip() for line in f.readlines()]

            if len(line) > 0:
                return False
            else:
                return True
        except FileNotFoundError as err:
            self.make_missing_queue(queue_file, err)

    def make_missing_queue(self, queue_file, err):
        if self.get_value("debug"):
            print(f"[err] {err}")
        print('Queue file is missing... ', end="")

        # Write a new queue file.
        with open(queue_file, 'w') as f:
            f.write("")

        print("created new one!")
        sys.exit()

    def check_queue(self, queue_file):
        """
        Check the queue file for any urls. If queue file
        is not found create a new queue file.
        """

        try:
            # Read the queue file.
            with open(queue_file, 'r') as f:
                line = [line.strip() for line in f.readlines()]

            if len(line) > 1:
                print(f"{len(line)} item is available in queue.")
            else:
                print(f"{len(line)} items are available in queue.")
            return line
        except FileNotFoundError as err:
            self.make_missing_queue(queue_file, err)

    def make_playlist(self, url: str):
        """ Create a directory for playlist and return playlist."""
        from spotify import Spotify
        from youtube import YouTube

        # Set a playlist name.
        if self.get_value("spotify") and Spotify.is_spotify(url):
            playlist_name = Spotify.get_playlist_name(url)
        else:
            try:
                playlist_name = YouTube.get_playlist_name(
                    YouTube.extract_info(url, self.search))
            except AttributeError:
                playlist_name = YouTube.get_playlist_name(
                    YouTube.extract_info(url, False))

        # Get os path to playlist.
        playlist = os.path.join(self.path, playlist_name)

        # Make a new directory.
        os.makedirs(playlist, exist_ok=True)

        if self.get_value("debug"):
            print("[info] Created playlist directory!")

        return playlist

    def get_random_proxy(self, proxy_list):
        """ Get a random proxy from the proxy list """
        from random import choice
        
        proxy = choice(proxy_list)
        print(f"You are currently using proxy: {proxy}")
        return proxy

    async def download(self, urls: str):
        """
        Download content from service like YouTube/Spotify 
        by using their own functions.
        """
        from concurrent.futures import ThreadPoolExecutor
        from youtube import YouTube
        from spotify import Spotify

        for url in urls:
            if YouTube.is_playlist(url):
                playlist = self.make_playlist(url)
            else:
                playlist = self.path

        # Options for yt_dlp to run with.
        options = {
            'format': str(self.get_value("format")),
            'postprocessorsoptions': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': str(self.get_value("codec")),
                    'preferredquality': str(self.get_value("bitrate"))
                }
            ],
            'embedthumbnail': self.get_value("thumbnail"),
            'socket_timeout': 40,
            'outtmpl': os.path.join(playlist, "%(title)s.%(ext)s"),
            'http_chunk_size': self.get_value("chunksize") * self.get_value("chunksize"),
            'external_downloader': self.get_value('downloader'),
            'external_downloader_args': self.get_value('downloaderargs'),
            'quiet': not self.get_value("verbose"),
            'debug': not self.get_value("debug"),
        }

        # Initialize silent logger if silent mode is on.
        if self.get_value("silent"):
            options['logger'] = Logger()

        # Provide cache directory if caching is on.
        if self.get_value("caching"):
            options['cache_dir'] = os.path.join(self.dirs.user_cache_dir, '.cache')
        else:
            options['cache_dir'] = None

        
        if self.proxy_list:
            proxy = self.get_random_proxy(self.proxy_list)
        else:
            proxy = None

        # Check if the multithreading mode is enabled.
        if self.get_value("multithreading"):
            # Run python a pool with threads predefined.
            with ThreadPoolExecutor(max_workers=int(self.get_value("threads"))) as executor:
                if self.get_value("spotify") and Spotify.is_spotify(urls):
                    executor.map(Spotify.download(urls, options, proxy))
                else:
                    executor.map(YouTube.download(urls, options, proxy, self.search))

        elif self.get_value("spotify"):
            if Spotify.is_spotify(urls):
                Spotify.download(urls, options, proxy)

        else:
            YouTube.download(urls, options, proxy, self.search)

    def parse_commands(self):
        """ Handle all of the commands that program has to offer. """
        from argparse import ArgumentParser

        # Initialize argument parser.
        parser = ArgumentParser(prog="AudioPipe", description="AudioPipe: command-line interface for downloading music")
        
        # Initialize command groups.
        basic = parser.add_argument_group('basic')
        spotify = parser.add_argument_group('spotify')
        file = parser.add_argument_group('audio file')
        networking = parser.add_argument_group('networking')
        performance = parser.add_argument_group('performance')

        parser.add_argument(
            "-V", "--version",
            action="version",
            version=f"%(prog)s {self.version} ({self.codename})",
            help="output version information and exit"
        )

        basic.add_argument(
            "-d", "--debug",
            action="store_true",
            help="print an exhaustive amount of logs like debug messages"
        )
        basic.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="make yt-dlp print more messages"
        )
        basic.add_argument(
            "-s", "--search",
            action="store_true",
            help="if you wish to search thru YouTube"
        )
        basic.add_argument(
            "-p", "--path",
            type=str,
            help="specify a directory where files will be downloaded"
        )
        basic.add_argument(
            "-c", "--config",
            type=str,
            help="specify the config file to be loaded"
        )
        basic.add_argument(
            "-g", "--genconfig",
            action="store_true",
            help="generate config file using default template"
        )
        basic.add_argument(
            "-q", "--queue",
            action="store_true",
            help="use user's queue file instead of program's"
        )
        basic.add_argument(
            "--silent",
            action="store_true",
            help="make yt-dlp not print any messages except errors"
        )
        
        spotify.add_argument(
            "-S", "--spotify",
            action="store_true",
            help="if you wish to use spotify"
        )
        spotify.add_argument(
            "-a", "--auth",
            action="store_true",
            help="if you wish to use spotify authentication"
        )
        spotify.add_argument(
            "-i", "--id",
            type=str,
            help="pass spotify app's client id"
        )
        spotify.add_argument(
            "--secret",
            type=str,
            help="pass spotify app's client secret"
        )
        spotify.add_argument(
            "--token",
            type=str,
            help="pass spotify app's auth token"
        )
        spotify.add_argument(
            "-H", "--headless",
            action="store_true",
            help="do not open browser while authenticating spotify"
        )

        file.add_argument(
            "-t", "--thumbnail",
            action="store_true",
            help="if you wish to use album covers"
        )
        file.add_argument(
            "-b", "--bitrate",
            type=int,
            help="specify a bitrate of a sound file"
        )
        file.add_argument(
            "-C", "--codec",
            type=str,
            help="specify a audio format of a sound file"
        )

        networking.add_argument(
            "-P", "--proxies",
            type=list,
            help="specify a list of proxies to load"
        )
        performance.add_argument(
            "-m", "--multithreading",
            action="store_true",
            help="if you wish to boost your download speeds"
        )
        performance.add_argument(
            "-T", "--threads",
            type=int,
            help="count of cpu threads used by parallel download"
        )
        performance.add_argument(
            "--caching",
            action="store_true",
            help="store cache to speed up the repetitive processes"
        )

        # Initialize the command variable
        self.command, unknown = parser.parse_known_args()

        if self.command.genconfig:
            self.gen_config(self.DEFAULT_CONFIG, True)
            sys.exit()

        if unknown:
            # Throw an exception while user supplies unknown arguments. 
            parser.error("invalid arguments: {}".format(" ".join(unknown)))

if __name__ == "__main__":
    try:
        from asyncio import run
        ap = AudioPipe()
        run(ap.download(ap.urls))
    except ModuleNotFoundError as err:
        print(f"{err}, missing dependencies...")