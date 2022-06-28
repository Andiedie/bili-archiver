import shutil
import traceback
from bili_archiver.api import BiliAPI
from fake_useragent import UserAgent
from pathlib import Path
import subprocess
from bili_archiver import recorder
from bili_archiver import parser
# noinspection PyPackageRequirements
import slugify
from functools import partial
from bili_archiver.logger import logger
import tempfile

ua = UserAgent().chrome
slugify = partial(slugify.slugify, allow_unicode=True)
tempdir = Path(tempfile.gettempdir()).joinpath('bili_archiver')


class DownloadException(Exception):
    pass


class MergeException(Exception):
    pass


def download(api: BiliAPI, output: Path):
    records = recorder.get_to_download()
    for record in records:
        should_cleanup = True
        aid = record.video_id
        video = parser.parse_video(api, aid)
        if video is None:
            continue
        temp_parent = tempdir.joinpath(f"{video.up_id}_{slugify(video.up_name)}_{video.aid}_{slugify(video.title)}")
        temp_parent.mkdir(exist_ok=True, parents=True)
        parent = output.joinpath(f"{video.up_id}_{slugify(video.up_name)}/{video.aid}_{slugify(video.title)}")
        parent.mkdir(exist_ok=True, parents=True)
        try:
            referer = f'https://www.bilibili.com/video/{video.bvid}'
            for page in video.pages:
                out_path = parent.joinpath(f'{page.pid}_{slugify(page.title)}.mp4')
                if out_path.exists():
                    continue

                page = parser.parse_cid(api, page)
                temp_out_path = temp_parent.joinpath(f'{page.pid}_{slugify(page.title)}.mp4')
                temp_video_path = temp_parent.joinpath(f'{page.pid}_{slugify(page.title)}.bili_archiver.mp4')
                temp_audio_path = temp_parent.joinpath(f'{page.pid}_{slugify(page.title)}.bili_archiver.m4a')

                logger.info(f'downloading {temp_video_path}')
                aria2c(page.video_url, referer, temp_video_path)
                logger.info(f'downloading {temp_audio_path}')
                aria2c(page.audio_url, referer, temp_audio_path)
                logger.info(f'merging {temp_video_path} & {temp_audio_path} to {temp_out_path}')
                merge(temp_video_path, temp_audio_path, temp_out_path)

                logger.info(f'moving {temp_out_path} to {out_path}')
                shutil.move(temp_out_path, out_path)

            recorder.download_history_set(video.aid, downloaded=True)

        except Exception as e:
            logger.error(f'download failed, av: {video.aid} bv: {video.bvid}, title: {video.title}, reason: {e}')
            traceback.print_exc()
        except KeyboardInterrupt as e:
            logger.error(f'interrupt by user')
            should_cleanup = False
            raise e
        finally:
            if should_cleanup:
                logger.info(f'removing {temp_parent}')
                shutil.rmtree(temp_parent)


def merge(video_path: Path, audio_path: Path, out_path: Path):
    p = subprocess.Popen([
        'ffmpeg', '-y',
        '-i', video_path, '-i', audio_path, '-c', 'copy', out_path
    ], stderr=subprocess.PIPE)
    _, stderr = p.communicate()
    if p.returncode != 0:
        raise MergeException(stderr.decode('utf-8', 'replace'))


def aria2c(url: str, referer: str, out: Path):
    p = subprocess.Popen([
        'aria2c',
        '-x', '16', '-s', '16', '-k', '1M',
        '--file-allocation=none',
        '--auto-file-renaming=false',
        '--allow-overwrite=true',
        f'--user-agent="{ua}"',
        f'--referer={referer}',
        f'--dir={out.parent}',
        f'--out={out.name}',
        url
    ], stderr=subprocess.PIPE)
    _, stderr = p.communicate()
    if p.returncode != 0:
        raise DownloadException(stderr.decode('utf-8', 'replace'))
