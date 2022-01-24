from typing import List
from datetime import datetime
from bili_archiver.api import BiliAPI
from dataclasses import dataclass
import json


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
    info_raw: str
    pages_play_url_raw: str


def parse(aids: List[int], api: BiliAPI = BiliAPI.from_env()) -> List[Video]:
    result = []
    for aid in aids:
        info = api.get_video_info(aid=aid)
        play_urls = [
            api.get_video_page_download_url(aid, page['cid'])
            for page in info['pages']
        ]
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
            ],
            info_raw=json.dumps(info),
            pages_play_url_raw=json.dumps(play_urls)
        )
        result.append(video)
    return result
