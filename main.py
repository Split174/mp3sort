import os
import eyed3
from typing import List, Tuple, Optional, NamedTuple, Dict
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--src-dir', help='целевая директория, по умолчанию директория в которой запущен скрипт')
parser.add_argument('-d', '--dist-dir', help='целевая директория, по умолчанию директория в которой запущен скрипт')
args = parser.parse_args()

class ID3Tags(NamedTuple):
    """
    'C-like' struct for id3 tags
    """
    artist: str
    album: str
    title: str

def get_mp3_in_dir(path: str) -> List[str]:
    """
    Receiving mp3 files in a directory
    """
    res: List[str] = []
    for f in os.listdir(path):
        file_ext: str = os.path.splitext(f)[1]
        if os.path.isfile(os.path.join(path, f)) and file_ext == '.mp3':
            res.append(os.path.join(path, f))
    return res

def get_id3tags(path_mp3: str) -> ID3Tags:
    """
    Gets id3 tags from mp3 file
    """
    audio = eyed3.load(path_mp3)
    return ID3Tags(audio.tag.artist, audio.tag.album, audio.tag.title)


def create_music_path(music: str, dist_path: str) -> str:
    """
    Creates a new path for mp3 based on id3 tags and target directory
    Params
    ------------------
    music : str
        Path to mp3
    dist_path : str
        Target path
    Returns
    ------------------
    str
        New path to mp3
    """
    newpath: str
    tags: ID3Tags = get_id3tags(music)
    filename: str = tags.title if tags.title != None else os.path.splitext(os.path.basename(music))[0]
    if tags.album == None or tags.artist == None:
        newpath = music
    else:
        newpath = os.path.join(dist_path, tags.artist, tags.album, f'{filename} - {tags.artist} - {tags.album}.mp3')
    return newpath

def valid_dir(path: str, access_mode: int = os.W_OK) -> str:
    """
    Check catalogs for validity
    Params
    ------------------
    path: str
        Path to dir
    access_mode: int
        Mode from os lib
    Returns
    ------------------
    str
        Error message
    """
    err_msg: str = ""
    if not os.path.exists(path):
        err_msg += f'Каталог {path} не существует\n'
    if err_msg != "" and not os.path.isdir(path):
        err_msg += f'{path} не является каталогом\n'
    if err_msg != "" and access_mode == os.R_OK and not os.access(path, access_mode):
        err_msg += f'{path} нет доступа на чтение\n'
    if err_msg != "" and access_mode == os.W_OK and not os.access(path, access_mode):
        err_msg += f'{path} нет доступа на запись\n'
    return err_msg 

def main():
    """
    The basic process of sorting mp3 files
    """
    src_dir: str = args.src_dir if args.src_dir != None else os.getcwd()
    dist_dir: str = args.dist_dir if args.dist_dir != None else os.getcwd()
    src_valid: str = valid_dir(src_dir, os.R_OK)
    dist_valid: str = valid_dir(dist_dir, os.W_OK)
    if src_valid != "" or dist_valid != "":
        print(src_valid)
        print(dist_valid)
        return
    musics: List[str] = get_mp3_in_dir(src_dir)
    for m in musics:
        try:
            new_path: str = create_music_path(m, dist_dir)
            if m == new_path:
                continue
            if os.path.exists(new_path):
                os.remove(new_path)
            os.renames(m, new_path)
            print(f'\033[31m{m} -> \033[37m{new_path}')
        except IOError as e: 
            print(e)

main()