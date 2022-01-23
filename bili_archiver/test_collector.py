from unittest import TestCase
from bili_archiver import collector


class Test(TestCase):
    def test_collect(self):
        print(collector.collect(from_history=False, from_self_favorite_folders=True))
