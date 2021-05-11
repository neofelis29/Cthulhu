import time
import unittest

from src.cthulhu import Cthulhu

if __name__ == '__main__':
    unittest.main()


class TestVastAPI(unittest.TestCase):
    def setUp(self):
        pass
    def test_get_time(self):
        cthulhu =  Cthulhu()
        cthulhu.get_public_time()