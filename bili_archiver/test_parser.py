from unittest import TestCase
from bili_archiver.api import BiliAPI
from pathlib import Path
from bili_archiver import parser
from bili_archiver.parser import PageBase


class Test(TestCase):
    def test_parse_cid(self):
        api = BiliAPI.from_file(Path('/Users/andie/Downloads/bilibili.com_cookies.txt'))
        res = parser.parse_cid(api, PageBase(
            aid=500820921,
            bvid='',
            cid=272641411,
            pid=1,
            title='',
            duration=0
        ))
        print(res)
