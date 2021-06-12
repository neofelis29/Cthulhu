import unittest
import pandas as pd
import os
from dotenv import load_dotenv

from src.User import User
from src.cthulhu import Cthulhu
import warnings

from src.utils import logger_init

warnings.simplefilter("ignore", ResourceWarning)
load_dotenv()

KRAKEN_API_PRIVATE_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", default="")

if __name__ == '__main__':
    unittest.main()


class TestVastAPI(unittest.TestCase):
    def setUp(self):
        logger_init()
        self.cthulhu = Cthulhu()
        self.user = User(self.cthulhu)

    def test_prediction(self):
        pred = self.user.get_prediction("Energy Web Token", "Euro")
        self.assertIsNotNone(pred)

    def test_get_slope_prediction_trend(self):
        pred = self.user.get_prediction("Energy Web Token", "Euro")
        self.user._get_slope_prediction_trend(pred)
