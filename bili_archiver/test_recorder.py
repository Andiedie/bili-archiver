from unittest import TestCase
from bili_archiver import recorder
from datetime import datetime, timedelta


class Test(TestCase):
    def test_last_collect_time(self):
        recorder._del_last_collect_time('1')
        assert recorder.get_last_collect_time('1') == datetime.fromtimestamp(946656000)
        t = datetime.now()
        recorder.set_last_collect_time('1', t)
        assert recorder.get_last_collect_time('1') == t
        t += timedelta(microseconds=1)
        recorder.set_last_collect_time('1', t)
        assert recorder.get_last_collect_time('1') == t
        recorder._del_last_collect_time('1')

    def test_download(self):
        recorder._del_downloaded(1)
        assert recorder.is_collected(1) is False
        assert recorder.is_downloaded(1) is False
        assert recorder.is_disappeared(1) is False
        recorder.download_history_set(1)
        assert recorder.is_collected(1) is True
        assert recorder.is_downloaded(1) is False
        assert recorder.is_disappeared(1) is False
        recorder.download_history_set(1, downloaded=True)
        assert recorder.is_collected(1) is True
        assert recorder.is_downloaded(1) is True
        assert recorder.is_disappeared(1) is False
        recorder.download_history_set(1, downloaded=False, disappeared=True)
        assert recorder.is_collected(1) is True
        assert recorder.is_downloaded(1) is False
        assert recorder.is_disappeared(1) is True
        recorder._del_downloaded(1)

    def test(self):
        print(recorder.get_to_download())
