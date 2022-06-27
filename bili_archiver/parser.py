from typing import Generator, List
from datetime import datetime
from bili_archiver.api import BiliAPI
from bili_archiver.api.biliapi import BiliApiException
from dataclasses import dataclass
import json
from bili_archiver.logger import logger
from bili_archiver import recorder


@dataclass
class Page:
    cid: int
    pid: int
    title: str
    duration: int
    video_url: str
    audio_url: str


@dataclass
class Video:
    aid: int
    bvid: str
    title: str
    up_id: int
    up_name: str
    created_at: datetime
    pages: List[Page]


def parse(api: BiliAPI) -> Generator[Video, None, None]:
    records = recorder.get_to_download()

    for record in records:
        aid = record.video_id
        logger.info(f'parsing av{aid}')

        if record.info_raw != '':
            info = json.loads(record.info_raw)
            logger.info(f"get av{aid} info from db")
        else:
            try:
                info = api.get_video_info(aid=aid)
                logger.info(f"get av{aid} info from api")
            except BiliApiException as e:
                if e.code == -404 or e.code == 62002:
                    logger.warning(f"av{aid} disappeared")
                    recorder.download_history_set(aid, disappeared=True)
                    continue
                else:
                    logger.warning(f'parse av{aid} failed: {e}')
                    raise e

        logger.info(f"av{aid} title {info['title']}")

        if record.download_raw != '':
            play_urls = json.loads(record.download_raw)
            logger.info(f"get av{aid} play_urls from db")
        else:
            play_urls = []
            for page in info['pages']:
                logger.info(f"parsing page av{aid} p{page['page']} cid{page['cid']}({page['part']})")
                url = api.get_video_page_download_url(aid, page['cid'])
                play_urls.append(url)
            logger.info(f"get av{aid} play_urls from api")

        video = Video(
            aid=aid,
            bvid=info['bvid'],
            title=info['title'],
            up_id=info['owner']['mid'],
            up_name=info['owner']['name'],
            created_at=datetime.fromtimestamp(info['ctime']),
            pages=[
                Page(
                    cid=page['cid'],
                    pid=page['page'],
                    title=page['part'],
                    duration=page['duration'],
                    video_url=sorted(
                        download['dash']['video'],
                        key=lambda x: x['bandwidth'],
                        reverse=True
                    )[0]['base_url'],
                    audio_url=sorted(
                        download['dash']['audio'],
                        key=lambda x: x['bandwidth'],
                        reverse=True
                    )[0]['base_url']
                )
                for page, download in zip(info['pages'], play_urls)
            ]
        )
        recorder.download_history_set(aid, info_raw=json.dumps(info), download_raw=json.dumps(play_urls))
        yield video
