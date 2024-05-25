from colorama import init as colorama_init
from colorama import Style
from colorama import Fore
from time import sleep, time
import subprocess as sub
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

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        if load_config('auto_dl'):
            print('Auto download was choosen (this can be changed in "config.toml" file)')
        else:
            print('Manual download was choosen (this can be changed in "config.toml" file)')

        if load_config('ascii'):
            print(ASCII_ART)

    def main(self, dl, auto_dl) -> None:
        if load_config('auto_dl'):
            auto_dl()
        if not load_config('auto_dl'):
            dl()

    def auto_download(self) -> None:
        ran = False

        while True:
            if not ran:
                playlist = input('Name your playlist: ')

            playlist_path = os.path.join(self.path, playlist)

            if not os.path.exists(playlist_path):
                os.mkdir(playlist_path)
                ran = True

            start_time = time()

            try:
                with open(load_config('queue')) as f:
                    for line in f.readlines():
                        link = line.strip()
                        
                        os.system('cls' if os.name == 'nt' else 'clear')

                        if link:
                            sub.run([
                                'yt-dlp', '-P', playlist_path, 
                                '-x', '--audio-format', 'mp3', 
                                '--embed-thumbnail', line])
            except FileNotFoundError:
                print(f"Queue file is missing!")
                with open(load_config('queue'), 'w') as f:
                    f.write("Maybe don't delete the needed files next time ;)")

            end_time = time()

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'Finished in {(end_time - start_time):.2f}')
            break

    def download(self) -> None:
        ran = False

        while True:
            if not ran:
                playlist = input('Name your playlist: ')

            playlist_path = os.path.join(self.path, playlist)

            if not os.path.exists(playlist_path):
                os.mkdir(playlist_path)
                print("Created a playlist folder.")
                ran = True

            os.system('cls' if os.name == 'nt' else 'clear')

            link = input('Enter your youtube link ("q" to quit): ')

            if link.lower() == 'q':
                break
            else:
                sub.run([
                    'yt-dlp', '-P', playlist_path, 
                    '-x', '--audio-format', 'mp3', 
                    '--embed-thumbnail', link])

                sleep(1)
                os.system('cls' if os.name == 'nt' else 'clear')

def load_config(*args):
    default_config = {
        'path': './downloads',
        'ascii': True,
        'auto_dl': True,
        'queue': 'queue.txt'}
    config = {}

    if not os.path.exists('config.toml'):
        with open('config.toml', 'w') as f:
            toml.dump(default_config, f)
        config = default_config
    else:
        with open('config.toml', 'r') as f:
            config = toml.load(f)
    
    return config.get(*args, default_config.get(*args))

if __name__ == "__main__":
    ap = AudioPipe(load_config('path'))
    ap.main(dl=ap.download, auto_dl=ap.auto_download)
