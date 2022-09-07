import shutil
import time
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
from typing import List
from bili_archiver.parser import Video

ua = UserAgent().chrome
slugify = partial(slugify.slugify, allow_unicode=True)
tempdir = Path(tempfile.gettempdir()).joinpath('bili_archiver')


class DownloadException(Exception):
    pass


class MergeException(Exception):
    pass


def download_video(api: BiliAPI, video: Video, output: Path):
    should_cleanup = True
    temp_parent = tempdir.joinpath(f"{video.up_id}_{slugify(video.up_name)}_{video.aid}_{slugify(video.title)}")
    temp_parent.mkdir(exist_ok=True, parents=True)
    parent = output.joinpath(f"{video.up_id}_{slugify(video.up_name)}/{video.aid}_{slugify(video.title)}")
    parent.mkdir(exist_ok=True, parents=True)
    try:
        referer = f'https://www.bilibili.com/video/{video.bvid}'
        for page in video.pages:
            temp_out_path = temp_parent.joinpath(f'{page.pid}_{slugify(page.title)}.mp4')

            page = parser.parse_cid(api, page)
            if page is None:
                return
            if page.video_url != '' and page.audio_url != '':
                out_path = parent.joinpath(f'{page.pid}_{slugify(page.title)}.mp4')
                if out_path.exists():
                    logger.info(f'aid {page.aid} cid {page.cid} page {page.pid} downloaded, skip')
                    continue
                logger.info(f'downloading aid {page.aid} cid {page.cid} with dash mode')
                temp_video_path = temp_parent.joinpath(f'{page.pid}_{slugify(page.title)}.biliarchiver.mp4')
                temp_audio_path = temp_parent.joinpath(f'{page.pid}_{slugify(page.title)}.biliarchiver.m4a')

                logger.info(f'downloading aid {page.aid} cid {page.cid} video')
                aria2c(page.video_url, referer, temp_video_path)
                logger.info(f'downloading aid {page.aid} cid {page.cid} audio')
                aria2c(page.audio_url, referer, temp_audio_path)
                logger.info(f'merging aid {page.aid} cid {page.cid} audio & video')
                merge(temp_video_path, temp_audio_path, temp_out_path)
                temp_video_path.unlink()
                temp_audio_path.unlink()
            else:
                out_path = parent.joinpath(f'{page.pid}_{slugify(page.title)}.flv')
                if out_path.exists():
                    logger.info(f'aid {page.aid} cid {page.cid} page {page.pid} downloaded, skip')
                    continue
                logger.info(f'downloading aid {page.aid} cid {page.cid} with segment mode')
                file_list = []
                for seg_idx in range(len(page.video_urls)):
                    if seg_idx > 0:
                        # 下载太频繁会报 Connection aborted.
                        time.sleep(3)
                        page = parser.parse_cid(api, page)
                        if page is None:
                            return
                    temp_video_path = temp_parent.joinpath(
                        f'{page.pid}_{slugify(page.title)}_{seg_idx}.biliarchiver.flv'
                    )
                    logger.info(f'downloading aid {page.aid} cid {page.cid} seg {seg_idx + 1}/{len(page.video_urls)}')
                    aria2c(page.video_urls[seg_idx], referer, temp_video_path)
                    file_list.append(temp_video_path)
                logger.info(f'merging aid {page.aid} cid {page.cid} {len(page.video_urls)} segments')
                merge_segment(file_list, temp_out_path)

            logger.info(f'moving {temp_out_path} to {out_path}')
            shutil.move(temp_out_path, out_path)

        recorder.download_history_set(video.aid, downloaded=True)

    except Exception as e:
        logger.error(f'download failed, av: {video.aid} bv: {video.bvid}, title: {video.title}, reason: {e}')
        traceback.print_exc()
        raise e
    except KeyboardInterrupt as e:
        logger.error(f'interrupt by user')
        should_cleanup = False
        raise e
    finally:
        if should_cleanup:
            logger.info(f'removing {temp_parent}')
            shutil.rmtree(temp_parent)


def download(api: BiliAPI, output: Path):
    records = recorder.get_to_download()
    for record in records:
        aid = record.video_id
        video = parser.parse_video(api, aid)
        if video is None:
            continue
        download_video(api, video, output)
        time.sleep(5)


def merge(video_path: Path, audio_path: Path, out_path: Path):
    p = subprocess.Popen([
        'ffmpeg', '-hide_banner', '-y',
        '-i', video_path, '-i', audio_path, '-c', 'copy', out_path
    ], stderr=subprocess.PIPE)
    _, stderr = p.communicate()
    if p.returncode != 0:
        raise MergeException(stderr.decode('utf-8', 'replace'))


def merge_segment(file_list: List[Path], out_path: Path):
    file_list_txt = out_path.with_suffix('.txt')
    with file_list_txt.open('w') as f:
        for one in file_list:
            f.write(f"file '{str(one)}'\n")
    p = subprocess.Popen([
        'ffmpeg', '-hide_banner', '-y',
        '-f', 'concat', '-safe', '0', '-i', file_list_txt,
        '-c', 'copy',
        out_path
    ], stderr=subprocess.PIPE)
    _, stderr = p.communicate()
    if p.returncode != 0:
        raise MergeException(stderr.decode('utf-8', 'replace'))


def aria2c(url: str, referer: str, out: Path):
    p = subprocess.Popen([
        'aria2c',
        '-x', '4', '-s', '16', '-k', '1M',
        '--check-certificate=false',
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
