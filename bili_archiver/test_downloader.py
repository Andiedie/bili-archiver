from unittest import TestCase
from bili_archiver import parser, downloader


class Test(TestCase):
    def test_download(self):
        videos = parser.parse([934637444])
        downloader.download(videos)

