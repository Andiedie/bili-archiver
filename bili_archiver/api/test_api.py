import json
from unittest import TestCase
from bili_archiver.api.biliapi import BiliAPI
from datetime import datetime


class TestAPI(TestCase):
    def setUp(self) -> None:
        self.ins = BiliAPI.from_chrome()

    def test_get_history(self):
        print(
            [
                one['title']
                for one in self.ins.get_history(today())
            ]
        )

    def test_get_favorite_folders(self):
        print(self.ins.get_favorite_folders(946974))

    def test_get_self_favorite_folders(self):
        print(self.ins.get_self_favorite_folders())

    def test_get_video_of_favorite_folder(self):
        print(
            [
                one['title']
                for one in self.ins.get_videos_of_favorite_folder(
                    self.ins.get_self_favorite_folders()[0]['id'], today()
                )
            ]
        )

    def test_get_follow_groups(self):
        print(
            self.ins.get_follow_groups()
        )

    def test_get_users_in_group(self):
        print(
            self.ins.get_users_in_group(436424)
        )

    def test_get_videos_of_user(self):
        print(
            [
                one['title']
                for one in self.ins.get_videos_of_user(7349, today())
            ]
        )

    def test_def_get_video_info(self):
        print(json.dumps(self.ins.get_video_info(aid=8320117)))

    def test_get_video_pages(self):
        print(self.ins.get_video_pages(8320117))

    def test_get_video_page_download_url(self):
        print(json.dumps(self.ins.get_video_page_download_url(8320117, 181853543)))


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
