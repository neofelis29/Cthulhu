import json
from typing import List
from src.cthulhu import Cthulhu
import pandas as pd


class User:
    def __init__(self, cthulhu: Cthulhu):
        self.cthulhu = cthulhu
        self.balance = cthulhu.get_balance()
        self.open_orders = cthulhu.get_open_orders()["result"]
        self.closed_orders = cthulhu.get_closed_orders()

    def get_open_orders(self):
        return pd.DataFrame(self.open_orders["open"]).transpose().reset_index().rename(columns={"index": "id"})

    def get_information_orders(self, ids_list: List[str]) -> json:
        return pd.DataFrame(self.cthulhu.get_information_orders(ids_list)["result"]).transpose().reset_index().rename(columns={"index": "id"})
    
    def get_prediction(self, asset_name_1: str, asset_name_2: str) -> pd.DataFrame:
        asset = self.cthulhu.get_asset(asset_name_1)
        asset_2 = self.cthulhu.get_asset(asset_name_2)
        pair_asset = self.cthulhu.get_pair_asset(asset, asset_2)
        success, result = pair_asset.predict_crypto_currency(forecasting_time=7 * 24)
        if success:
            return result.iloc[:7*24]
        else:
            return None
    

