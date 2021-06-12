import json
from typing import List, Tuple
from src.cthulhu import Cthulhu
import pandas as pd
from scipy import stats
import datetime as dt


class User:
    def __init__(self, cthulhu: Cthulhu):
        self.cthulhu = cthulhu
        self.balance = cthulhu.get_balance()
        self.open_orders = cthulhu.get_open_orders()["result"]
        self.closed_orders = cthulhu.get_closed_orders()

    def get_open_orders(self) -> pd.DataFrame:
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
    
    def get_prediction(self, asset_name_1: str, asset_name_2: str) -> pd.DataFrame:
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

    def _get_slope_prediction_trend(self, prediction_trend: pd.DataFrame) -> float:
        """
        Compute slop of crypto currency prediction
        :return: The slope of prediction computed
        """
        prediction_trend['date_ordinal'] = pd.to_datetime(prediction_trend['ds']).map(dt.datetime.toordinal)
        slope, intercept, r_value, p_value, std_err = stats.linregress(prediction_trend['date_ordinal'], prediction_trend['trend'])
        return slope


    def _get_min_max(self, prediction_trend: pd.DataFrame) -> Tuple[float, float]:
        """
        Get the min max of prediction
        :param prediction_trend: Dataframe of prediction trend
        :return: Return mni and max value of prediction
        """
        return prediction_trend["trend"].min(), prediction_trend["trend"].max()
