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

    def get_open_orders(self) -> pd.Dataframe:
        """
        Get open order information
        :return: Information of open order
        """
        return pd.DataFrame(self.open_orders["open"]).transpose().reset_index().rename(columns={"index": "id"})

    def get_information_orders(self, ids_list: List[str]) -> json:
        """
        Get open order information of specific order
        :param ids_list: List of ids
        :return: Information of open order
        """
        return pd.DataFrame(self.cthulhu.get_information_orders(ids_list)["result"]).transpose().reset_index().rename(columns={"index": "id"})
    
    def _get_prediction(self, asset_name_1: str, asset_name_2: str) -> pd.DataFrame:
        """
        Compute prediction currency of the asset given
        :param asset_name_1: Asset name
        :param asset_name_2: Asset name
        :return: The dataframe of currency prediction
        """
        asset = self.cthulhu.get_asset(asset_name_1)
        asset_2 = self.cthulhu.get_asset(asset_name_2)
        pair_asset = self.cthulhu.get_pair_asset(asset, asset_2)
        success, result = pair_asset.predict_crypto_currency(forecasting_time=7 * 24)
        if success:
            return result.iloc[:7*24]
        else:
            return None
    

