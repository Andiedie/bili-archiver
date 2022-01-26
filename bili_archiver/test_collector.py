from unittest import TestCase
from bili_archiver import collector


class Test(TestCase):
    def test_collect(self):
        collector.collect(from_history=True, from_self_favorite_folders=True)
