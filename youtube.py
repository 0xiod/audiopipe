from yt_dlp import YoutubeDL

class YouTube:
    def extract_info(url: str, search: bool = False):
        """ Extract info from YouTube and return it. """
        options = {'quiet': True, 'extract_flat': True}
        try:
            with YoutubeDL(options) as yt:
                if search:
                    return yt.extract_info(f"ytsearch:{url}", download=False)
                else:
                    return yt.extract_info(url, download=False)
        except Exception as err:
            raise err

    def is_playlist(info):
        if 'entries' in info and info['entries']:
            return True
        else:
            return False

    def get_playlist_name(info):
        """ Extract playlist name from YouTube. """
        if isinstance(info, dict):
            return info.get('title', 'Unknown playlist')
        else:
            return "Unknown playlist"

    def download(urls: str, options: list, proxies: list, search: bool = False):
        """ Download content from YouTube. """
        from time import perf_counter
        from os import system

        # Check for proxies if there are any.
        if proxies != None:
            options['proxy'] = proxies

        system('cls||clear')

        # Initialize 1st a performance counter.
        time_start = perf_counter()

        # Downloading a song from YouTube.
        for url in urls:
            with YoutubeDL(options) as yt:
                if search:
                    yt.extract_info(f"ytsearch:{url}", download=True)['entries'][0]
                else:
                    yt.download(url)

        # Calculate time that has passed since the 'time_start' initialization.
        time_elapsed = (perf_counter() - time_start)

        # Clear out the output and print elapsed time.
        print(f"Finished downloading in {round(time_elapsed, 2)}s")
