from unittest import TestCase
from bili_archiver.api.biliapi import BiliAPI, BiliApiException
import os
from datetime import datetime


class TestAPI(TestCase):
    def setUp(self) -> None:
        self.ins = BiliAPI.from_env()

    def test_ins(self):
        with self.assertRaises(BiliApiException):
            BiliAPI('123', '123')

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

    def test_get_videos_of_user(self):
        print(
            [
                one['title']
                for one in self.ins.get_videos_of_user(7349, today())
            ]
        )

    def test_def_get_video_info(self):
        print(self.ins.get_video_info(bvid='BV1qM4y1w716'))

    def test_get_video_pages(self):
        print(self.ins.get_video_pages(934637444))

    def test_get_video_page_download_url(self):
        print(self.ins.get_video_page_download_url(210904288, 493070282))


def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
