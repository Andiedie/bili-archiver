import re
from bili_archiver.parser import Video
from typing import Generator
from fake_useragent import UserAgent
from pathlib import Path
import subprocess
import os
from bili_archiver import recorder

ua = UserAgent().chrome


class DownloadException(Exception):
    pass


class MergeException(Exception):
    pass


def download(videos: Generator[Video, None, None]):
    for video in videos:
        parent = Path(os.getcwd()).joinpath(f"{slug(video.up_name)}/{video.aid}_{slug(video.title)}")
        referer = f'https://www.bilibili.com/video/{video.bvid}'
        for page in video.pages:
            video_path = parent.joinpath(f'{page.pid}_{slug(page.title)}.bili_archiver.mp4')
            audio_path = parent.joinpath(f'{page.pid}_{slug(page.title)}.bili_archiver.m4a')
            out_path = parent.joinpath(f'{page.pid}_{slug(page.title)}.mp4')
            aria2c(page.video_url, referer, video_path)
            aria2c(page.audio_url, referer, audio_path)
            merge(video_path, audio_path, out_path)
            video_path.unlink()
            audio_path.unlink()
        recorder.download_history_set(video.aid, downloaded=True)


def merge(video_path: Path, audio_path: Path, out_path: Path):
    p = subprocess.Popen([
        'ffmpeg', '-y',
        '-i', video_path, '-i', audio_path, '-c', 'copy', out_path
    ], stderr=subprocess.PIPE)
    _, stderr = p.communicate()
    if p.returncode != 0:
        raise MergeException(stderr.decode('utf-8', 'replace'))


def aria2c(url: str, referer: str, out: Path):
    print(out.parent)
    print(out.name)
    p = subprocess.Popen([
        'aria2c',
        '-x', '16', '-s', '16', '-k', '1M',
        f'--user-agent="{ua}"',
        f'--referer={referer}',
        f'--dir={out.parent}',
        f'--out={out.name}',
        url
    ], stderr=subprocess.PIPE)
    _, stderr = p.communicate()
    if p.returncode != 0:
        raise DownloadException(stderr.decode('utf-8', 'replace'))


def slug(v):
    return re.sub(r'[/\\:*?"<>|]', '', v)
