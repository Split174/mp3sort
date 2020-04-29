import os
import eyed3
from typing import List, Tuple, Optional, NamedTuple, Dict
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--src-dir', help='целевая директория, по умолчанию директория в которой запущен скрипт')
parser.add_argument('-d', '--dist-dir', help='целевая директория, по умолчанию директория в которой запущен скрипт')
args = parser.parse_args()


class ID3Tags(NamedTuple):
    artist: str
    album: str
    title: str

def get_file_in_dir(path : str, exts : List[str]) -> List[str]:
    res : List[str] = []
    for f in os.listdir(path):
        file_ext : str = os.path.splitext(f)[1]
        if os.path.isfile(os.path.join(path, f)) and file_ext in exts:
            res.append(f) # TODO лучше fullpath 
    return res

def get_id3tags(path : str) -> ID3Tags:
    audio = eyed3.load(path)
    return ID3Tags(audio.tag.artist, audio.tag.album, audio.tag.title)


def create_music_path(music : str, dist_path : str) -> str:
    newpath :str
    tags : ID3Tags = get_id3tags(music)
    filename : str = tags.title if tags.title != None else os.path.splitext(music)[0]
    if tags.album == None or tags.artist == None:
        newpath = os.path.join(os.getcwd(), f'{filename}.mp3')
    else:
        newpath = os.path.join(dist_path, tags.artist, tags.album, f'{filename} - {tags.artist} - {tags.album}.mp3')
    return newpath

def is_valid_dir(path : str):
    is_valid = True
    if os.path.exists(path):
        print(f'Каталог {path} не существует')
        is_valid = False
    if (os.path.isdir(path)):
        print(f'{path} не является каталогом')
        is_valid = False
    if os.access(path, os.R_OK): # TODO допроверять
        print(f'{path} нет доступа на чтение')
        is_valid = False
    return is_valid 

def renames_file(files : Dict[str, str]):
    for old, new in files.items():
        print(f'\033[31m{old} -> \033[37m{new}')
        os.renames(old, new)

def main():
    src_dir : str = args.src_dir if args.src_dir != None else os.getcwd()
    dist_dir : str = args.dist_dir if args.dist_dir != None else os.getcwd()
    if not is_valid_dir(src_dir) or not is_valid_dir(dist_dir):
        return
    os.chdir(src_dir) # TODO прочекать есть ли вообще смысл
    musics : List[str] = get_file_in_dir(os.getcwd(), ['.mp3'])
    musics_old_new : Dict[str, str] = dict()
    for m in musics:
        try:
            m_full_path = os.path.join(os.getcwd(), m)
            musics_old_new[m_full_path] = create_music_path(m, dist_dir)
        except IOError as e: 
            print(e)
    renames_file(musics_old_new)

main()