from colorama import init as colorama_init
from colorama import Style
from colorama import Fore
import yt_dlp
import asyncio
import aiohttp
import toml
import os

colorama_init()

ASCII_ART = Fore.CYAN + """
                         d8b   d8,                    d8,                 
                         88P  `8P                    `8P                  
                        d88                                               
 d888b8b  ?88   d8P d888888    88b d8888b ?88,.d88b,  88b?88,.d88b, d8888b
d8P' ?88  d88   88 d8P' ?88    88Pd8P' ?88`?88'  ?88  88P`?88'  ?88d8b_,dP
88b  ,88b ?8(  d88 88b  ,88b  d88 88b  d88  88b  d8P d88   88b  d8P88b    
`?88P'`88b`?88P'?8b`?88P'`88bd88' `?8888P'  888888P'd88'   888888P'`?888P'
                                            88P'           88P'           
                                           d88            d88             
                                           ?8P            ?8P             
""" + Style.RESET_ALL

class AudioPipe:
    def __init__(self, path) -> None:
        self.path = path
        self.links = []

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        if load_config('ascii'):
            print(ASCII_ART)

        try:
            with open(load_config('queue')) as f:
                self.links = [line.strip() for line in f.readlines()]
            
            print(
                f"{len(self.links)} item is available in queue." if len(self.links) == 1 
                else f"{len(self.links)} items are available in queue.")
        except FileNotFoundError:
            with open(load_config('queue'), 'w') as f:
                f.write("Maybe don't delete the essential files next time ;)")

    def get_playlist_name(self, link):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            playlist_title = info_dict.get('title', 'Unknown Playlist')
            return playlist_title

    async def download(self) -> None:
        tasks = []
        async with aiohttp.ClientSession():
            for link in self.links:
                playlist_path = os.path.join(self.path, self.get_playlist_name(link))
                os.makedirs(playlist_path, exist_ok=True)
                tasks.append(self.download_song(link, playlist_path))
            await asyncio.gather(*tasks)

    async def download_song(self, link, playlist) -> None:
        start_time = asyncio.get_event_loop().time()
        os.system('cls||clear')

        command = [
            'yt-dlp', '-P', playlist, '-o', {f'{load_config('file_name')}.%(ext)s'},
            '-x', '--audio-format', load_config('format'), 
            '--embed-thumbnail' if load_config('thumbnail') 
            else '--no-embed-thumbnail', link]
        
        process = await asyncio.create_subprocess_exec(*command)
        await process.communicate()
                
        end_time = asyncio.get_event_loop().time()
        os.system('cls||clear')

        print(f'Finished in {(end_time - start_time):.2f}s')

def load_config(key):
    default_config = {
        'path': './downloads',
        'ascii_art': False,
        'queue': 'queue.txt',
        'format': 'mp3',
        'thumbnail': True,
        'file_name': '%(title)s'
    }
    config = {}

    if os.path.exists('config.toml'):
        try:
            with open('config.toml', 'r') as f:
                config = toml.load(f)
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
