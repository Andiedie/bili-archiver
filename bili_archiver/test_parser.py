from unittest import TestCase
from bili_archiver import parser


class Test(TestCase):
    def test_parse(self):
        print(parser.parse([934637444, 678437796]))
