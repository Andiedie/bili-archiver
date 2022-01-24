import requests
from datetime import datetime
import os


class BiliBiliApiException(Exception):
    @staticmethod
    def check(con, msg):
        if con:
            raise BiliBiliApiException(msg)


class BiliAPI:
    @staticmethod
    def from_env():
        BiliBiliApiException.check('SESSDATA' not in os.environ, 'environment variable SESSDATA needed')
        return BiliAPI(os.environ.get('SESSDATA'))

    def __init__(self, sessdata: str):
        self.session = requests.Session()
        self.session.cookies.set('SESSDATA', sessdata, domain='api.bilibili.com')

        # 验证登录
        user_info = self.get_user_info()
        BiliBiliApiException.check(not user_info['isLogin'], 'not login')

        # 记录当前用户 ID
        self.mid = user_info['mid']

    def get_user_info(self):
        return self.session.get('https://api.bilibili.com/x/web-interface/nav').json()['data']

    def get_history(self, after: datetime):
        after_ts = int(after.timestamp())
        cursor = {
            'max': 0,
            'view_at': 0,
            # 视频
            'business': 'archive',
            # page_size
            'ps': 30
        }
        result = []
        while True:
            resp = self.session.get('https://api.bilibili.com/x/web-interface/history/cursor',
                                    params=cursor)
            body = resp.json()
            cursor = body['data']['cursor']
            # 翻到底了
            if len(body['data']['list']) == 0:
                break

            result += [video for video in body['data']['list'] if video['view_at'] >= after_ts]

            if any(video['view_at'] < after_ts for video in body['data']['list']):
                break
        return result

    def get_favorite_folders(self, user_id: int):
        resp = self.session.get('https://api.bilibili.com/x/v3/fav/folder/created/list-all',
                                params={'up_mid': user_id})
        body = resp.json()

        if body.get('data') and body['data'].get('list'):
            return body['data']['list']

        return []

    def get_self_favorite_folders(self):
        return self.get_favorite_folders(self.mid)

    def get_videos_of_favorite_folder(self, fav_id: int, after: datetime):
        result = []
        pn = 0
        after_ts = int(after.timestamp())

        while True:
            pn += 1
            resp = self.session.get('https://api.bilibili.com/x/v3/fav/resource/list',
                                    params={
                                        'media_id': fav_id,
                                        'pn': pn,
                                        'ps': 20
                                    })
            body = resp.json()

            # 没视频了，直接退出
            if body['data']['medias'] is None or len(body['data']['medias']) == 0:
                break

            result += [video for video in body['data']['medias'] if video['fav_time'] >= after_ts]

            if any(video['fav_time'] < after_ts for video in body['data']['medias']):
                break
        return result

    def get_videos_of_user(self, user_id: int, after: datetime):
        result = []
        pn = 0
        after_ts = int(after.timestamp())

        while True:
            pn += 1
            resp = self.session.get('https://api.bilibili.com/x/space/arc/search',
                                    params={
                                        'mid': user_id,
                                        'pn': pn,
                                        'ps': 50
                                    })
            body = resp.json()

            # 没视频了，直接退出
            if len(body['data']['list']['vlist']) == 0:
                break

            result += [video for video in body['data']['list']['vlist'] if video['created'] >= after_ts]

        return result

    def get_video_info(self, aid: int = None, bvid: str = None):
        BiliBiliApiException.check(aid is None and bvid is None, 'aid or bvid needed')

        if aid is not None:
            payload = {'aid': aid}
        else:
            payload = {'bvid': bvid}

        resp = self.session.get('https://api.bilibili.com/x/web-interface/view', params=payload)
        body = resp.json()
        return body['data']

    def get_video_pages(self, aid):
        resp = self.session.get('https://api.bilibili.com/x/player/pagelist',
                                params={
                                    'aid': aid
                                })
        body = resp.json()
        return body['data']

    def get_video_page_download_url(self, aid: int, cid: int):
        resp = self.session.get('https://api.bilibili.com/x/player/playurl',
                                params={
                                    'avid': aid,
                                    'cid': cid,
                                    'otype': '',
                                    'fourk': 1,
                                    'fnver': 0,
                                    'fnval': 2000
                                })
        body = resp.json()
        return body['data']
