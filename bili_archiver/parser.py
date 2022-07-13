from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass
from bili_archiver.api import BiliAPI
from bili_archiver.api.biliapi import BiliApiException
from bili_archiver.logger import logger
from bili_archiver import recorder


@dataclass
class PageBase:
    aid: int
    bvid: str
    cid: int
    pid: int
    title: str
    duration: int


@dataclass
class Page(PageBase):
    video_url: str
    audio_url: str
    video_urls: List[str]


@dataclass
class Video:
    aid: int
    bvid: str
    title: str
    up_id: int
    up_name: str
    created_at: datetime
    pages: List[PageBase]


def parse_cid(api: BiliAPI, page: PageBase) -> Optional[Page]:
    logger.info(f'parsing page, av: {page.aid} page: {page.pid} cid: {page.cid}')

    try:
        download = api.get_video_page_download_url(page.aid, page.cid)
    except BiliApiException as e:
        if e.code == -404 or e.code == 62002:
            logger.warning(f"av{page.aid} disappeared")
            recorder.download_history_set(page.aid, disappeared=True)
            return None
        else:
            logger.warning(f'parse av{page.aid} failed: {e}')
            raise e

    if 'dash' in download:
        video_url = sorted(
            download['dash']['video'],
            key=lambda x: x['id'],
            reverse=True
        )[0]['base_url']
        if download['dash'].get('dolby'):
            audio_url = sorted(
                download['dash']['dolby']['audio'],
                key=lambda x: x['bandwidth'],
                reverse=True
            )[0]['base_url']
        else:
            audio_url = sorted(
                download['dash']['audio'],
                key=lambda x: x['bandwidth'],
                reverse=True
            )[0]['base_url']
        return Page(
            aid=page.aid,
            bvid=page.bvid,
            cid=page.cid,
            pid=page.pid,
            title=page.title,
            duration=page.duration,
            video_url=video_url,
            audio_url=audio_url,
            video_urls=[]
        )
    else:
        return Page(
            aid=page.aid,
            bvid=page.bvid,
            cid=page.cid,
            pid=page.pid,
            title=page.title,
            duration=page.duration,
            video_url='',
            audio_url='',
            video_urls=[
                one['url']
                for one in download['durl']
            ]
        )


def parse_video(api: BiliAPI, aid: int) -> Optional[Video]:
    logger.info(f'parsing av{aid}')

    try:
        info = api.get_video_info(aid=aid)
        logger.info(f"get av{aid} info from api")
    except BiliApiException as e:
        if e.code == -404 or e.code == 62002:
            logger.warning(f"av{aid} disappeared")
            recorder.download_history_set(aid, disappeared=True)
            return None
        else:
            logger.warning(f'parse av{aid} failed: {e}')
            raise e

    logger.info(f"av{aid} title {info['title']}")

    video = Video(
        aid=aid,
        bvid=info['bvid'],
        title=info['title'],
        up_id=info['owner']['mid'],
        up_name=info['owner']['name'],
        created_at=datetime.fromtimestamp(info['ctime']),
        pages=[
            PageBase(
                aid=aid,
                bvid=info['bvid'],
                cid=page['cid'],
                pid=page['page'],
                title=page['part'],
                duration=page['duration']
            )
            for page in info['pages']
        ]
    )
    return video
