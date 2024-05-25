from colorama import init as colorama_init
from colorama import Style
from colorama import Fore
from time import sleep
import subprocess as sub
import toml
import os

colorama_init()

class Main:
    def __init__(self, path) -> None:
        self.path = path

        if not os.path.exists(self.path):
            os.mkdir(self.path)
            print("Created a music folder.")

        print(Fore.RED +'''              ┏┓   ┓•  ┏┳┓  ┓   
              ┣┫┓┏┏┫┓┏┓ ┃ ┓┏┣┓┏┓
              ┛┗┗┻┗┻┗┗┛ ┻ ┗┻┗┛┗ ''' + Style.RESET_ALL)

    def download(self) -> None:
        ran = False
        
        while True:
            if not ran:
                playlist = input('Set your playlist name: ')

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

                sleep(2)
                os.system('cls' if os.name == 'nt' else 'clear')

def load_config(*args):
    default_config = {'path': './downloads'}
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
    main = Main(load_config('path'))
    main.download()
