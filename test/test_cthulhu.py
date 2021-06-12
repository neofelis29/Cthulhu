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
        asset = self.cthulhu.get_asset("Bitcoin")
        asset_2 = self.cthulhu.get_asset("Euro")
        pair_asset = self.cthulhu.get_pair_asset(asset, asset_2)
        self.assertIsNotNone(pair_asset)

    def test_get_balance(self):
        print(self.cthulhu.get_balance())

    @ignore_warnings
    def test_ohclc(self):
        asset = self.cthulhu.get_asset("Dogecoin")
        asset_2 = self.cthulhu.get_asset("Euro")
        pair_asset = self.cthulhu.get_pair_asset(asset, asset_2)
        pair_asset.graph_timestamp()

    @ignore_warnings
    def test_get_trend(self):
        asset = self.cthulhu.get_asset("Bitcoin")
        asset.graph_timestamp_trend()

    def test_predict_crypto_currency(self):
        asset = self.cthulhu.get_asset("Energy Web Token")
        asset_2 = self.cthulhu.get_asset("Euro")
        pair_asset = self.cthulhu.get_pair_asset(asset, asset_2)
        success, result = pair_asset.predict_crypto_currency(optional_input_data_list=["close"], graph=True,
                                                             forecasting_time=7 * 24)
        self.assertTrue(success)

    def test_predict_crypto_currency_optimized(self):
        asset = self.cthulhu.get_asset("Energy Web Token")
        asset_2 = self.cthulhu.get_asset("Euro")
        pair_asset = self.cthulhu.get_pair_asset(asset, asset_2)
        pair_asset.predict_crypto_currency_optimized(graph=True)

    def test_client_get_open_orders(self):
        client = User(self.cthulhu)
        self.assertIsNotNone(client.open_orders)

    def test_client_get_closed_orders(self):
        client = User(self.cthulhu)
        self.assertIsNotNone(client.closed_orders)
