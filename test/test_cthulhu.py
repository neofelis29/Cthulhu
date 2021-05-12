import time
import unittest
import pandas as pd
import os
from pip._vendor import requests
from dotenv import load_dotenv, find_dotenv
from src.cthulhu import Cthulhu

load_dotenv()

KRAKEN_API_PRIVATE_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", default="")

if __name__ == '__main__':
    unittest.main()


class TestVastAPI(unittest.TestCase):
    def setUp(self):
        self.cthulhu = Cthulhu()

    def test_system_status(self):
        self.assertTrue(self.cthulhu.is_online())

    def test_asset_is_df(self):
        self.assertIs(type(self.cthulhu.assets), pd.DataFrame)

    def test_get_asset(self):
        asset = self.cthulhu.get_asset("ETH")
        print(asset.altname)

    def test_get_pair_asset(self):
        asset = self.cthulhu.get_asset("BTC")
        asset_2 = self.cthulhu.get_asset("EUR")
        pair_asset = self.cthulhu.get_pair_asset(asset, asset_2)
        print(pair_asset.get_information())

    def test_get_balance(self):
        print(self.cthulhu.get_balance())