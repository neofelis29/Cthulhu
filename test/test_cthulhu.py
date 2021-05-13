import time
import unittest
import pandas as pd
import os
from pip._vendor import requests
from dotenv import load_dotenv, find_dotenv
from src.cthulhu import Cthulhu
from src.utils import graph_timestamp
import warnings
warnings.simplefilter("ignore", ResourceWarning)
load_dotenv()

KRAKEN_API_PRIVATE_KEY = os.getenv("KRAKEN_API_PRIVATE_KEY", default="")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", default="")

if __name__ == '__main__':
    unittest.main()


class TestVastAPI(unittest.TestCase):
    def setUp(self):
        self.cthulhu = Cthulhu()

    def ignore_warnings(test_func):
        def do_test(self, *args, **kwargs):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                test_func(self, *args, **kwargs)

        return do_test

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
        print(pair_asset.get_ticker_information())

    def test_get_balance(self):
        print(self.cthulhu.get_balance())

    def test_ohclc(self):
        asset = self.cthulhu.get_asset("BTC")
        asset_2 = self.cthulhu.get_asset("EUR")
        pair_asset = self.cthulhu.get_pair_asset(asset, asset_2)
        data = pair_asset.get_data(60)
        self.assertIsNotNone(data)
        graph_timestamp(data[["high", "low"]], asset.name+"/"+asset_2.name)

    @ignore_warnings
    def test_trend(self):
        asset = self.cthulhu.get_asset("BTC")
        print(asset.get_data())