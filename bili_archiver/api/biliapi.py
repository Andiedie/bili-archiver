import requests
from datetime import datetime
import browsercookie


class BiliApiException(Exception):
    def __init__(self, msg: str, code: int):
        self.code = code
        super().__init__(msg)

    @staticmethod
    def check(con: bool, msg: str, code: int = 0):
        if con:
            raise BiliApiException(msg, code)


class BiliAPI:
    # @staticmethod
    # def from_env():
    #     BiliApiException.check('SESSDATA' not in os.environ, 'environment variable SESSDATA needed')
    #     BiliApiException.check('BILIJCT' not in os.environ, 'environment variable BILIJCT needed')
    #     session = requests.Session()
    #     session.cookies.set('SESSDATA', os.environ.get('SESSDATA'))
    #     session.cookies.set('bili_jct', os.environ.get('BILIJCT'))
    #     return BiliAPI(session)

    @staticmethod
    def from_chrome():
        cj = browsercookie.chrome()
        session = requests.Session()
        session.cookies = cj
        return BiliAPI(session)

    def __init__(self, session: requests.Session):
        self.session = session
        # 验证登录
        user_info = self.get_user_info()
        BiliApiException.check(not user_info['isLogin'], 'not login')

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
            BiliApiException.check(body['code'] != 0, body['message'], body['code'])
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
        BiliApiException.check(body['code'] != 0, body['message'], body['code'])
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
            BiliApiException.check(body['code'] != 0, body['message'], body['code'])
            # 没视频了，直接退出
            if body['data']['medias'] is None or len(body['data']['medias']) == 0:
                break

            result += [video for video in body['data']['medias'] if video['fav_time'] >= after_ts]

            if any(video['fav_time'] < after_ts for video in body['data']['medias']):
                break
        return result

    def get_follow_groups(self):
        resp = self.session.get('https://api.bilibili.com/x/relation/tags')
        body = resp.json()
        BiliApiException.check(body['code'] != 0, body['message'], body['code'])
        return body.get('data', [])

    def get_users_in_group(self, group_id: int):
        result = []
        pn = 0

        while True:
            pn += 1
            resp = self.session.get('https://api.bilibili.com/x/relation/tag',
                                    params={
                                        'tagid': group_id,
                                        'pn': pn,
                                        'ps': 20
                                    })
            body = resp.json()
            BiliApiException.check(body['code'] != 0, body['message'], body['code'])
            if 'data' not in body or len(body['data']) == 0:
                break
            result += body.get('data', [])

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
            BiliApiException.check(body['code'] != 0, body['message'], body['code'])
            # 没视频了，直接退出
            if len(body['data']['list']['vlist']) == 0:
                break

            result += [video for video in body['data']['list']['vlist'] if video['created'] >= after_ts]
            if any(video['created'] < after_ts for video in body['data']['list']['vlist']):
                break

        return result

    def get_video_info(self, aid: int = None, bvid: str = None):
        BiliApiException.check(aid is None and bvid is None, 'aid or bvid needed')

        if aid is not None:
            payload = {'aid': aid}
        else:
            payload = {'bvid': bvid}

        resp = self.session.get('https://api.bilibili.com/x/web-interface/view', params=payload)
        body = resp.json()
        BiliApiException.check(body['code'] != 0, body['message'], body['code'])
        return body.get('data')

    def get_video_pages(self, aid):
        resp = self.session.get('https://api.bilibili.com/x/player/pagelist',
                                params={
                                    'aid': aid
                                })
        body = resp.json()
        BiliApiException.check(body['code'] != 0, body['message'], body['code'])
        return body['data']

    def get_video_page_download_url(self, aid: int, cid: int):
        resp = self.session.get('https://api.bilibili.com/x/player/playurl',
                                params={
                                    'avid': aid,
                                    'cid': cid,
                                    'otype': 'json',
                                    'qn': 120,
                                    'fourk': 1,
                                    'fnver': 0,
                                    'fnval': 2000
                                })
        body = resp.json()
        BiliApiException.check(body['code'] != 0, body['message'], body['code'])

        resp = self.session.get('https://api.bilibili.com/x/player/playurl',
                                params={
                                    'avid': aid,
                                    'cid': cid,
                                    'otype': 'json',
                                    'qn': max(body['data']['accept_quality']),
                                    'fourk': 1,
                                    'fnver': 0,
                                    'fnval': 2000
                                })
        body = resp.json()

        BiliApiException.check(body['code'] != 0, body['message'], body['code'])
        return body['data']
